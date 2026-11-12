#!/usr/bin/env python3
"""Package one pack directory as a `.tjpack` and refresh `index.json`.

A `.tjpack` is a zip containing manifest.json, lexicon.jsonl, NOTICE.md,
README.md and any optional rules / tm / orthography files declared in the
manifest. The zip is deterministic enough for checksum-based distribution.

Usage:
    python3 scripts/package.py packs/tujia-open-core
    python3 scripts/package.py packs/tujia-open-core --tier 0
"""

import argparse
import json
import sys
import zipfile
from pathlib import Path

from validate import validate

REPO = Path(__file__).resolve().parents[2]


def optional_files(pack_dir, manifest):
    files = manifest.get("files") or {}
    out = []
    for key in ("rules",):
        for rel in files.get(key) or []:
            path = pack_dir / rel
            if path.is_file():
                out.append(rel)
    for key in ("tm", "orthography", "notice"):
        rel = files.get(key)
        if rel and (pack_dir / rel).is_file():
            out.append(rel)
    return out


def build_pack(pack_dir, dist_dir):
    manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
    pack_id, edition = manifest["pack_id"], manifest["edition"]
    target = dist_dir / f"{pack_id}-{edition}.tjpack"

    members = ["manifest.json", "lexicon.jsonl", "NOTICE.md", "README.md"]
    members += [rel for rel in optional_files(pack_dir, manifest) if rel not in members]
    missing = [m for m in members if not (pack_dir / m).is_file()]
    if missing:
        raise FileNotFoundError(f"pack {pack_id}: missing {missing}")

    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in members:
            zf.write(pack_dir / rel, arcname=rel)
    return target, manifest


def refresh_index(pack_dirs, dist_dir, tiers):
    old = {}
    index_path = REPO / "data" / "index.json"
    if index_path.is_file():
        try:
            data = json.loads(index_path.read_text(encoding="utf-8"))
            old = {p["pack_id"]: p for p in data.get("packs", [])}
        except Exception:
            old = {}

    packs = []
    for pack_dir in sorted(pack_dirs):
        manifest_path = pack_dir / "manifest.json"
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        pack_id = manifest["pack_id"]
        target = dist_dir / f"{pack_id}-{manifest['edition']}.tjpack"
        if not target.is_file():
            continue
        tier = tiers.get(pack_id, old.get(pack_id, {}).get("tier", 0))
        packs.append(
            {
                "file": target.name,
                "pack_id": pack_id,
                "title": manifest.get("title", ""),
                "edition": manifest["edition"],
                "tier": tier,
                "license": manifest.get("license", ""),
                "variety": manifest.get("variety", ""),
                "entries": manifest.get("entries", 0),
                "sha256": manifest.get("sha256", ""),
            }
        )
    packs.sort(key=lambda p: (p["tier"], p["pack_id"]))
    index_path.write_text(
        json.dumps({"schema": "tujia.packindex/v1", "packs": packs}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return index_path, packs


def main():
    ap = argparse.ArgumentParser(description="Package Tujia lexicon packs")
    ap.add_argument("pack", type=Path)
    ap.add_argument("--dist", type=Path, default=REPO / "dist")
    ap.add_argument("--tier", type=int, default=None)
    args = ap.parse_args()

    errors, _ = validate(args.pack)
    if errors:
        print(f"FAIL {args.pack}: fix validation errors first")
        for e in errors[:20]:
            print("  -", e)
        return 1

    target, manifest = build_pack(args.pack, args.dist)
    tiers = {manifest["pack_id"]: args.tier} if args.tier is not None else {}
    index_path, packs = refresh_index(
        [p for p in (REPO / "data" / "packs").iterdir() if p.is_dir()], args.dist, tiers
    )
    print(f"pack:  {target}  ({target.stat().st_size} bytes)")
    print(f"index: {index_path}  ({len(packs)} packs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
