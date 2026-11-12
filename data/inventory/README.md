# Syllable inventory 0.6.3

1,347 syllables attested in Tujia source material, normalised to the
northern system (Yedshu 1984). This is an inventory, not a dictionary: it lists
which syllables exist, one per row, with no gloss, example or page image.

| column | meaning |
| --- | --- |
| `syllable` | onset plus rhyme in IPA, tones excluded (tone is not part of the key) |
| `onset` | initial as written after normalisation; empty for vowel-initial syllables |
| `rhyme` | the rest of the syllable |
| `status` | `legal` = two or more independent sources; `attested` = one source |
| `n_books` | support count, bucketed as `1` / `2` / `3+` |

Totals: 632 legal, 715 attested.

Source identities and per-source attribution are **not** published. They are
held in a private registry and can be produced for a rights holder on request.
That is also why `n_books` is bucketed rather than exact: a precise count next
to a rare syllable would narrow down which source it came from.

`folds` in [manifest.json](manifest.json) records the rhyme normalisation
(`ian` → `iã`, `ɤi` → `ei`, `iøŋ` → `iũ`) so a consumer can apply the same
mapping instead of guessing.

## Consuming it

```python
from tujia_nlp import inventory
inventory.load("inventory/syllables-0.6.3.tsv")
```

`tujia-nlp` ships its own pinned snapshot of this table; this directory is the
versioned, checksummed copy.

## Licence

The compilation is released under CC0-1.0. The source works keep their own
terms; nothing from them is reproduced here.
