#!/usr/bin/env python3
"""Build the `tujia-open-core` pack from the Lexibank zhoubizic CLDF dataset.

Source: Zhou, Yulou (2020) Proto-Bizic (CC-BY-4.0).
The Proto-Bizic reconstructions are excluded; only the six modern varieties are
exported. Every entry satisfies the published TujiaNLP entry schema:
`w / p / g / pos / pg` are always present, `sense` and `src_head` are added.

Usage:
    python3 scripts/build_open_core.py
    python3 scripts/build_open_core.py --cldf /path/to/cldf --out packs/tujia-open-core
"""

import argparse
import csv
import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
# 数据源用环境变量指定，避免把本地语料仓的目录结构写进公开仓库
DEFAULT_CLDF = Path(os.environ.get(
    "TUJIA_ZHOU_CLDF",
    str(REPO.parent / "zhoubizic" / "cldf"),
))

PACK_ID = "tujia-open-core"
EDITION = "0.1.0"
TITLE = "土家语开放核心词表"
LICENSE = "CC-BY-4.0"
TONES = "⁰¹²³⁴⁵⁶⁷⁸⁹"

VARIETY = {
    "LongshanHusiL": "北部土家语（龙山 Laxidong）",
    "LongshanHusiT": "北部土家语（龙山 Tasha·他砂）",
    "XiaTujia": "北部土家语（仙仁）",
    "GuzhangHusi": "北部土家语（古丈 Xialongre）",
    "Cebu": "南部土家语（Cebu）",
    "CajiAdi": "南部土家语（下且己）",
}


def clean_form(text):
    """Collapse whitespace and drop a leading reconstruction asterisk."""
    text = re.sub(r"\s+", " ", (text or "").strip())
    return text.lstrip("*").strip()


def phone_string(form):
    """Toned IPA -> space separated detoned phone string (the `p` field)."""
    text = re.sub(r"\s+", "", form or "")
    text = text.replace("*", "").replace("?", "")
    phones = []
    for ch in text:
        if ch in TONES or ch.isdigit():
            continue
        # Keep letters, IPA modifier letters and combining marks; drop
        # punctuation such as "-" used for tone contours.
        if ch.isalpha() or unicodedata.category(ch) in ("Lm", "Mn", "Mc"):
            phones.append(ch)
    return " ".join(phones)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_cldf(cldf):
    with open(cldf / "parameters.csv", encoding="utf-8") as f:
        params = {r["ID"]: r for r in csv.DictReader(f)}
    with open(cldf / "forms.csv", encoding="utf-8") as f:
        forms = list(csv.DictReader(f))
    return params, forms


def build_entries(params, forms):
    entries, seen = [], set()
    dropped = []
    for row in forms:
        lang = row["Language_ID"]
        if lang == "ProtoBizic":
            continue
        form = clean_form(row.get("Form"))
        if not form:
            continue
        p = phone_string(form)
        if not p:
            dropped.append({"form": form, "reason": "no phones"})
            continue
        param = params.get(row["Parameter_ID"]) or {}
        gloss = (param.get("Chinese_Gloss") or param.get("Concepticon_Gloss") or param.get("Name") or "").strip()
        if not gloss:
            dropped.append({"form": form, "reason": "no gloss"})
            continue
        variety = VARIETY.get(lang, lang)
        key = (form, gloss, variety)
        if key in seen:
            dropped.append({"form": form, "reason": "duplicate"})
            continue
        seen.add(key)
        entries.append(
            {
                "w": form,
                "p": p,
                "g": gloss,
                "pos": "",
                "pg": "",  # filled below with a numeric locator
                "sense": 1,
                "src": PACK_ID,
                "src_head": form,
                "variety": variety,
            }
        )
    for i, entry in enumerate(entries, start=1):
        entry["pg"] = f"zhoubizic#{i}"
    return entries, dropped


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def notice_text(entries, concepts):
    return f"""# NOTICE

## Source

This pack is derived from:

- Zhou, Yulou (2020). *Proto-Bizic: A Study of Tujia Historical Phonology*.
  Bachelor thesis, Stanford University.
- The digitised data is also published at
  https://github.com/luggroo/bizic-dictionary; its maintainer granted
  permission to reuse it, asking only for attribution when published.

The Chinese concept glosses come from the same CLDF dataset
(`parameters.csv`, `Chinese_Gloss`), which links to Concepticon
(https://concepticon.clld.org/, CC-BY-4.0).

## What this pack contains

- {len(entries)} modern lexical forms from six Tujia varieties.
- {concepts} concepts.
- Fields: `w`, `p`, `g`, `pos`, `pg`, `sense`, `src`, `src_head`, `variety`.

## What was changed

- Proto-Bizic reconstructions were excluded.
- Orthography was kept as published in the CLDF `Form` column.
- `p` was derived by removing tone digits and whitespace from `w`.
- `pg` is a local row locator (`zhoubizic#N`), not a page number.
- Exact duplicates within a variety were removed.

## What is not included

- No content from any published Tujia dictionary or textbook.
- No audio, example sentences, translations or page images.
- This is an open core, not a complete dictionary.

## Licence

CC-BY-4.0. Attribution is required. See the citation above.
"""


def pack_readme(entries, concepts):
    return f"""# {TITLE}

Open, redistributable core vocabulary for Tujia, built from the CC-BY-4.0
Lexibank `zhoubizic` dataset (Zhou 2020).

| | |
| --- | --- |
| Entries | {entries} |
| Concepts | {concepts} |
| Varieties | 6 (northern and southern) |
| Licence | CC-BY-4.0 |
| Source | Zhou, Yulou (2020) |
| Data provider | https://github.com/luggroo/bizic-dictionary |

Fields follow the TujiaNLP entry schema: `w` (toned IPA), `p` (detoned phones),
`g` (Chinese gloss), `pos`, `pg`, plus `sense`, `src`, `src_head`, `variety`.

This is a core vocabulary, not a complete dictionary. Proto-Bizic
reconstructions and all copyrighted dictionary content are excluded.

```bash
tujia-asr audio.wav --dict packs/tujia-open-core/lexicon.jsonl
```
"""


def main():
    ap = argparse.ArgumentParser(description="Build the tujia-open-core pack")
    ap.add_argument("--cldf", type=Path, default=DEFAULT_CLDF)
    ap.add_argument("--out", type=Path, default=REPO / "data" / "packs" / PACK_ID)
    args = ap.parse_args()

    params, forms = read_cldf(args.cldf)
    entries, dropped = build_entries(params, forms)
    concepts = len({r["Parameter_ID"] for r in forms if r["Language_ID"] != "ProtoBizic"})

    args.out.mkdir(parents=True, exist_ok=True)
    lexicon = args.out / "lexicon.jsonl"
    write_jsonl(lexicon, entries)
    (args.out / "NOTICE.md").write_text(notice_text(entries, concepts), encoding="utf-8")
    (args.out / "README.md").write_text(pack_readme(len(entries), concepts), encoding="utf-8")

    digest = sha256_file(lexicon)
    manifest = {
        # tujia.pack/v1：Dart 引擎（tujia-trans）直接读取
        "schema": "tujia.pack/v1",
        "id": PACK_ID,
        "name": TITLE,
        "version": EDITION,
        # 发布索引字段：tools/lexicon 的 validate/package 读取
        "pack_id": PACK_ID,
        "title": TITLE,
        "edition": EDITION,
        "variety": "北部土家语 / 南部土家语",
        "orthography": "IPA, superscript tone digits",
        "entries": len(entries),
        "sha256": digest,
        "rights_holder": "Zhou, Yulou; Lexibank contributors",
        "license": LICENSE,
        "allowed_uses": ["research", "redistribution", "commercial-use", "modification"],
        "visibility": "public",
        "provenance": (
            "Zhou (2020) Proto-Bizic (CC-BY-4.0) "
            "-> IPA retained -> TujiaNLP entry schema -> TujiaNLP data pack"
        ),
        "source": {
            "name": "Zhou (2020)",
            "url": "https://github.com/luggroo/bizic-dictionary",
            "row_count": len(forms),
        },
        "notes": "Open core vocabulary, not a complete dictionary.",
        "files": {"lexicon": "lexicon.jsonl", "notice": "NOTICE.md"},
        "counts": {
            "lexicon": len(entries),   # tujia.pack/v1 的运行时计数
            "entries": len(entries),
            "concepts": concepts,
            "varieties": len(VARIETY),
        },
        "checksums": {"lexicon.jsonl": f"sha256:{digest}"},
        "generator": "scripts/build_open_core.py",
    }
    (args.out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"entries: {len(entries)}")
    print(f"concepts: {concepts}")
    print(f"dropped: {len(dropped)}")
    for d in dropped[:10]:
        print("  drop", d)
    print(f"sha256: {digest}")
    print(f"out: {args.out}")


if __name__ == "__main__":
    main()
