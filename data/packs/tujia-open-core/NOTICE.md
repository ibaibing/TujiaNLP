# NOTICE

## Source

This pack is derived from:

- Zhou, Yulou (2020). *Proto-Bizic: A Study of Tujia Historical Phonology*.
  Bachelor thesis, Stanford University. Licensed CC-BY-4.0.
- The digitised data is also published at
  https://github.com/luggroo/bizic-dictionary; its maintainer granted
  permission to reuse it, asking only for attribution when published
  (2026-11).

The Chinese concept glosses come from the same CLDF dataset
(`parameters.csv`, `Chinese_Gloss`), which links to Concepticon
(https://concepticon.clld.org/, CC-BY-4.0).

## What this pack contains

- 1620 modern lexical forms from six Tujia varieties.
- 346 concepts.
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
