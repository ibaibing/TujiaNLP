# Lexicon data

**Tujia Lexicon Commons** — public, redistributable Tujia lexicon data.

TujiaNLP carries this data layer alongside the orthography code. It does not
contain a decoding engine: the recogniser lives in `tujia-asr`, and the
translation rules live in `tujia-trans`.

## Principles

- The Tujia language belongs to the people who speak it. A word, its meaning and
  its pronunciation are shared facts, not the property of a dictionary.
- What is published here is only what may be redistributed: self-authored data,
  openly licensed data, community contributions and authorised packs.
- Every entry carries its source and licence. Provenance is never stripped.
- One pack equals one source. Packs are merged at query time, never on disk, so
  attribution and withdrawal stay possible.
- **One canonical output.** A lexicon is published once, as `tujia.pack/v1`
  (directory or `.tjpack`). Derived formats — TTS pronunciation tables, ASR word
  lists, translation caches — are produced by each consumer, never here. Adding a
  field for one downstream tool is the wrong fix; that tool converts.

```
TujiaNLP        orthography, tone notation, phone normalisation, entry/manifest schemas
TujiaNLP data   syllable inventory, public packs, schema and release artifacts
tujia-asr       speech recognition; reads a lexicon through --dict
tujia-trans     translation engine and app; reads packs directly
```

## What is published here

Only material that may be redistributed:

- packs built for this data layer (currently `tujia-open-core`, CC-BY-4.0);
- community-contributed packs whose licence allows redistribution;
- packs whose rights holder has given written permission.

Published source dictionaries are **not** included, even in part. The full
merged lexicon used for local research stays in the private data repository and
is never copied here.

## Packs

```
data/packs/
  tujia-open-core/
    manifest.json
    lexicon.jsonl
    NOTICE.md
    README.md
```

A **pack equals one source**. Packs are never merged on disk; an application
loads several packs and merges them at query time. This keeps attribution,
licensing and withdrawal per source.

This data layer publishes **packs only**, never a ready-made application index.
An application that loads several packs maintains its own `index.json` in tier
order (`tier 0` is the primary pack, higher tiers are fallbacks). The format is
described by `data/schema/packindex.schema.json`:

```json
{
  "schema": "tujia.packindex/v1",
  "packs": [
    {
      "file": "tujia-open-core.tjpack",
      "pack_id": "tujia-open-core",
      "edition": "0.1.0",
      "tier": 0,
      "license": "CC-BY-4.0",
      "entries": 1620,
      "sha256": "…"
    }
  ]
}
```

## Syllable inventory

```
inventory/
  syllables-0.6.3.tsv
  manifest.json
  README.md
```

`inventory/` is not a pack and not a dictionary. It is the closed list of
syllables attested in Tujia source material — one row per syllable, no gloss,
no example, no page image — normalised to the northern system. Consumers use it
to answer "is this a legal syllable" when validating recogniser output, TTS
input or model output.

| column | meaning |
| --- | --- |
| `syllable` | onset plus rhyme, tones excluded |
| `onset` / `rhyme` | the two halves, so a consumer can recombine them |
| `status` | `legal` (two or more independent sources) / `attested` (one) |
| `n_books` | support count bucketed as `1` / `2` / `3+` |

Unlike a pack, the inventory is compiled from many sources, and those sources
are **not named**. There is no per-source column and the support count is
bucketed, so no reader can tell which work attests a given syllable. Source
identities are held in a private registry; a rights holder can ask and get the
attribution. That is also how withdrawal works: drop the source in the private
registry, rebuild the inventory, bump the edition.

`manifest.json` carries the SHA-256, the column list, the status meanings and
the `folds` table (how non-northern rhymes were mapped: `ian` → `iã`, `ɤi` →
`ei`, `iøŋ` → `iũ`). Its contract is
[schema/syllabary.schema.json](schema/syllabary.schema.json); `validate.py`
enforces the parts a schema cannot express (row invariants, counts, and the ban
on source-naming keys).

`tujia-nlp` ships a pinned snapshot of this table; this directory is the
versioned, checksummed copy. Load it with:

```python
from tujia_nlp import inventory
inv = inventory.load("inventory/syllables-0.6.3.tsv")
```

## Entry format

One JSON object per line, UTF-8, in `lexicon.jsonl`. Entries satisfy the
published [TujiaNLP entry schema](https://github.com/ibaibing/TujiaNLP/blob/main/schema/entry.schema.json):
`w`, `p`, `g`, `pos`, `pg` are always present; `sense`, `src`, `src_head`,
`variety` add provenance and meaning.

```json
{"w":"ȵi³⁵","p":"n i","g":"你","pos":"代","pg":"tujia-open-core#1","sense":1,"src":"tujia-open-core","src_head":"ȵi³⁵","variety":"北部土家语（龙山）"}
```

| Field | Required | Meaning |
| --- | --- | --- |
| `w` | yes | Tujia word form in toned IPA, superscript tone digits |
| `p` | yes | detoned phone sequence, space separated (`tujia_nlp.phone_seq` compatible) |
| `g` | yes | one Chinese sense; do not pack several senses into one line |
| `pos` | yes | part of speech, one character; empty string when unannotated |
| `pg` | yes | source locator; `page_0018` or `pack_id#row` |
| `sense` | no | sense number for the same form, starting at 1 |
| `variety` | no | dialect point, e.g. `北部土家语（龙山）`, `南部土家语（泸溪）` |
| `src` | no | pack id that contributed the entry |
| `src_head` | no | headword as printed in the source, kept for checking |
| `ye` | no | Ye spelling, when the source provides it |
| `kind` | no | `word` (default) / `example` / `partial` |
| `flags` | no | free-form markers |

Entries sharing a form but carrying different senses are separate lines with
different `sense` values. Entries from different sources stay separate as well;
merging is a query-time view, not a write-time operation.

`src` and `src_head` are provenance metadata, not copied content. They are what
makes attribution, correction and withdrawal possible later.

## Build and release

```bash
# build the open-core pack from the Zhou (2020) CLDF dataset
python3 tools/lexicon/build_open_core.py

# check required fields, pg pattern, entry count and sha256
python3 tools/lexicon/validate.py data/packs/tujia-open-core

# check the inventory: columns, row invariants, counts, sha256, no source names
python3 tools/lexicon/validate.py data/inventory

# produce dist/<pack_id>-<edition>.tjpack (manual; apps usually read the directory)
python3 tools/lexicon/package.py data/packs/tujia-open-core
```

A `.tjpack` is a zip containing `manifest.json`, `lexicon.jsonl`, `NOTICE.md`,
`README.md` and any optional `rules/`, `tm.jsonl`, `orthography.yaml` declared
in the manifest. It is a transport container for consumers that need one file;
this repository does not publish it.

## Versioning

- `MAJOR` — field meaning or orthography changes
- `MINOR` — entries added, glosses corrected
- `PATCH` — metadata or NOTICE changes

Every release is immutable and carries the SHA-256 of `lexicon.jsonl`.
Consumers cache a downloaded pack locally and verify the checksum; nothing is
updated silently.

## Licence

- `tujia-open-core`: CC-BY-4.0 (Zhou 2020).
- Contributed packs: the licence declared in their own `manifest.json` and
  `NOTICE.md`; a pack without an explicit redistributable licence is not merged.
- Code and scripts in this repository: MIT.

## Consuming a pack

```bash
# ASR: syllable output by default; pass a lexicon for word output
tujia-asr audio.wav --dict packs/tujia-open-core/lexicon.jsonl

# translation app / CLI: read the pack directory, or a .tjpack you built yourself
```

The open-core pack is a **core vocabulary**, not a comprehensive decoding
lexicon. For arbitrary speech, syllable output is the honest floor; word
decoding works best with a user-supplied, comprehensive lexicon.
