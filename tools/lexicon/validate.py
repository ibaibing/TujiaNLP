#!/usr/bin/env python3
"""Validate one pack directory or inventory directory against its contract.

Packs (`tujia.packentry/v1`) check:
  - manifest required fields and checksum
  - lexicon.jsonl parses, required entry fields exist
  - `pg` locator pattern
  - entry count matches manifest
  - every entry's `src` equals the pack id

Inventories (`tujia.syllabary/v1`) check:
  - manifest required fields, schema id and checksum
  - the TSV has exactly the sanctioned columns
  - every row: `syllable == onset + rhyme`, status in legal/attested,
    support bucket in 1/2/3+, no duplicates
  - counts match the file
  - no source-naming key anywhere (that is the whole point of the inventory)

Usage:
    python3 scripts/validate.py packs/tujia-open-core
    python3 scripts/validate.py inventory
"""

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ENTRY_REQUIRED = ("w", "p", "g", "pos", "pg")
MANIFEST_REQUIRED = (
    "pack_id", "title", "edition", "variety", "orthography", "entries",
    "sha256", "rights_holder", "license", "allowed_uses", "visibility", "provenance",
)
PG_RE = re.compile(r"^[A-Za-z0-9_.-]+(#[0-9]+)?$")

INVENTORY_SCHEMA = "tujia.syllabary/v1"
INVENTORY_REQUIRED = ("schema", "version", "file", "sha256", "columns", "counts")
INVENTORY_COLUMNS = ["syllable", "onset", "rhyme", "status", "n_books"]
INVENTORY_STATUSES = {"legal", "attested"}
INVENTORY_SUPPORT = {"1", "2", "3+"}
# The inventory exists because the sources may not be named. These keys would
# put them back, so their presence is an error rather than a warning.
PROVENANCE_KEYS = ("sources", "books", "attribution", "rights_holder", "source")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(pack_dir):
    pack_dir = Path(pack_dir).expanduser()
    errors = []
    manifest_path = pack_dir / "manifest.json"
    lexicon_path = pack_dir / "lexicon.jsonl"

    if not manifest_path.is_file():
        return [f"missing {manifest_path}"], {}
    if not lexicon_path.is_file():
        return [f"missing {lexicon_path}"], {}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in MANIFEST_REQUIRED:
        if key not in manifest:
            errors.append(f"manifest: missing `{key}`")

    pack_id = manifest.get("pack_id", "")
    lexicon_sha = sha256_file(lexicon_path)
    if manifest.get("sha256") and manifest["sha256"] != lexicon_sha:
        errors.append("manifest: sha256 does not match lexicon.jsonl")
    checksums = manifest.get("checksums") or {}
    declared = checksums.get("lexicon.jsonl")
    if declared and declared != f"sha256:{lexicon_sha}":
        errors.append("manifest: checksums.lexicon.jsonl does not match")

    entries = 0
    with open(lexicon_path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            entries += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"line {lineno}: invalid JSON ({e})")
                continue
            for key in ENTRY_REQUIRED:
                if key not in row:
                    errors.append(f"line {lineno}: missing `{key}`")
            pg = row.get("pg", "")
            if pg and not PG_RE.match(str(pg)):
                errors.append(f"line {lineno}: bad pg `{pg}`")
            if pack_id and row.get("src") and row["src"] != pack_id:
                errors.append(f"line {lineno}: src `{row['src']}` != pack_id `{pack_id}`")
            if not str(row.get("w", "")).strip():
                errors.append(f"line {lineno}: empty w")
            if not str(row.get("g", "")).strip():
                errors.append(f"line {lineno}: empty g")

    if manifest.get("entries") != entries:
        errors.append(f"manifest: entries={manifest.get('entries')} but file has {entries}")

    summary = {
        "pack_id": pack_id,
        "entries": entries,
        "sha256": lexicon_sha,
        "license": manifest.get("license", ""),
        "visibility": manifest.get("visibility", ""),
    }
    return errors, summary


def validate_inventory(inv_dir):
    """Check one `inventory/` directory against `tujia.syllabary/v1`."""
    inv_dir = Path(inv_dir).expanduser()
    errors = []
    manifest_path = inv_dir / "manifest.json"
    if not manifest_path.is_file():
        return [f"missing {manifest_path}"], {}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in INVENTORY_REQUIRED:
        if key not in manifest:
            errors.append(f"manifest: missing `{key}`")
    if manifest.get("schema") != INVENTORY_SCHEMA:
        errors.append(f"manifest: schema is `{manifest.get('schema')}`, expected `{INVENTORY_SCHEMA}`")
    for key in PROVENANCE_KEYS:
        if key in manifest:
            errors.append(f"manifest: `{key}` names sources; the inventory must not")
    if manifest.get("columns") != INVENTORY_COLUMNS:
        errors.append(f"manifest: columns must be {INVENTORY_COLUMNS}")

    tsv_path = inv_dir / str(manifest.get("file", ""))
    if not tsv_path.is_file():
        return errors + [f"missing {tsv_path}"], {}

    digest = sha256_file(tsv_path)
    if manifest.get("sha256") != digest:
        errors.append("manifest: sha256 does not match the table")

    counts = {"total": 0, "legal": 0, "attested": 0}
    seen = set()
    with open(tsv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if reader.fieldnames != INVENTORY_COLUMNS:
            errors.append(f"table: header is {reader.fieldnames}, expected {INVENTORY_COLUMNS}")
        for lineno, row in enumerate(reader, start=2):
            counts["total"] += 1
            syl = row.get("syllable") or ""
            if not syl:
                errors.append(f"line {lineno}: empty syllable")
                continue
            if syl in seen:
                errors.append(f"line {lineno}: duplicate `{syl}`")
            seen.add(syl)
            if syl != (row.get("onset") or "") + (row.get("rhyme") or ""):
                errors.append(f"line {lineno}: syllable != onset + rhyme for `{syl}`")
            st = row.get("status")
            if st in INVENTORY_STATUSES:
                counts[st] += 1
            else:
                errors.append(f"line {lineno}: bad status `{st}`")
            if row.get("n_books") not in INVENTORY_SUPPORT:
                errors.append(f"line {lineno}: n_books `{row.get('n_books')}` not in {sorted(INVENTORY_SUPPORT)}")

    for key in ("total", "legal", "attested"):
        declared = (manifest.get("counts") or {}).get(key)
        if declared != counts[key]:
            errors.append(f"manifest: counts.{key}={declared} but table has {counts[key]}")

    summary = {
        "version": manifest.get("version", ""),
        "total": counts["total"],
        "legal": counts["legal"],
        "attested": counts["attested"],
        "sha256": digest,
    }
    return errors, summary


def _is_inventory(path):
    manifest = Path(path) / "manifest.json"
    if not manifest.is_file():
        return False
    try:
        return json.loads(manifest.read_text(encoding="utf-8")).get("schema") == INVENTORY_SCHEMA
    except json.JSONDecodeError:
        return False


def main():
    ap = argparse.ArgumentParser(description="Validate a Tujia lexicon pack or inventory")
    ap.add_argument("path", type=Path)
    args = ap.parse_args()

    if _is_inventory(args.path):
        errors, summary = validate_inventory(args.path)
        if errors:
            print(f"FAIL {args.path}")
            for e in errors[:40]:
                print("  -", e)
            if len(errors) > 40:
                print(f"  ... {len(errors) - 40} more")
            return 1
        print(f"OK inventory {summary['version']}: {summary['total']} syllables "
              f"({summary['legal']} legal, {summary['attested']} attested)")
        print(f"sha256 {summary['sha256']}")
        return 0

    errors, summary = validate(args.path)
    if errors:
        print(f"FAIL {args.path}")
        for e in errors[:40]:
            print("  -", e)
        if len(errors) > 40:
            print(f"  ... {len(errors) - 40} more")
        return 1
    print(f"OK {summary['pack_id']}: {summary['entries']} entries, "
          f"{summary['license']}, {summary['visibility']}")
    print(f"sha256 {summary['sha256']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
