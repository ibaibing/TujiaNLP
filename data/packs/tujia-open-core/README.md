# Tujia open-core vocabulary / 土家语开放核心词表

Open, redistributable core vocabulary for Tujia, built from Zhou, Yulou (2020),
licensed CC-BY-4.0.

| | |
| --- | --- |
| Entries | 1620 |
| Concepts | 346 |
| Varieties | 6 (northern and southern) |
| Licence | CC-BY-4.0 |
| Source | Zhou, Yulou (2020) |
| Data provider | https://github.com/luggroo/bizic-dictionary |

Fields follow the TujiaNLP entry schema: `w` (toned IPA), `p` (detoned phones),
`g` (Chinese gloss), `pos`, `pg`, plus `sense`, `src`, `src_head`, `variety`.

This is a core vocabulary, not a complete dictionary. Proto-Bizic
reconstructions and all copyrighted dictionary content are excluded.

```bash
tujia-asr audio.wav --dict data/packs/tujia-open-core/lexicon.jsonl
```
