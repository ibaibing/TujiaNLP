# TujiaNLP

Preserving the endangered **Northern Tujia** language with AI.

> Tujia is now spoken mainly by elderly native speakers. This open-source project aims to
> digitise the language record and build Tujia speech, translation and dialogue models.

[Chinese version](README.zh-CN.md)

## Goals

1. Collect field recordings and build a consistently annotated bilingual corpus.
2. Train Tujia ASR (speech recognition) and TTS (speech synthesis).
3. Build Tujia ↔ Chinese machine translation.
4. Assemble a Tujia dialogue pipeline, modular first, LLM fine-tuning later.
5. Ship lightweight learning tools for language revitalisation.

## Scope

**Northern Tujia only** (Longshan / Yongshun / Laifeng area, Miaotan standard).
Southern Tujia is deliberately excluded for now, to avoid mixing dialects in training.

## Orthography

The project follows the **Yedshu–Peng (1984) Tujia romanisation** ("Ye"). Other
transcriptions are not used as the working standard.

Two IPA spellings appear in source materials for the same sounds:

| Earlier spelling | Current standard |
| --- | --- |
| `aŋ eŋ iŋ oŋ`, `ʐ`, `iu` | `ã ẽ ĩ ũ`, `z`, `iou` |

The `tujia_nlp` package normalises between them: input accepts either spelling, output is
always the current convention.

## Ecosystem

| Repository | Role |
| --- | --- |
| **TujiaNLP** (this) | Corpus terms, collection standards, orthography, licensing |
| [tujia-asr](https://github.com/ibaibing/tujia-asr) | Acoustic model releases: syllable-level CTC |
| [tujia-tts](https://github.com/ibaibing/tujia-tts) | Speech synthesis releases |
| [tujia-llm](https://github.com/ibaibing/tujia-llm) | LoRA adapters and the evaluation protocol |

Where the work happens:

```
audio ──► tujia-asr        acoustic model, syllable-level output

text  ──► tujia_nlp        IPA ↔ Ye, tone notation ──► tts / llm data, annotations
```

Rules of thumb:

- **This repository** owns language resources and contracts: the syllable table, the
  orthography rules, the corpus terms, and the dictionary entry/manifest schemas.
- **tujia-asr / tujia-tts / tujia-llm** own model releases. Training code lives in private
  `*-lib` / `*-lab` repositories.

## Installation

```bash
pip install tujia-nlp
```

Requires Python 3.9+. No third-party dependencies.

## Usage

```python
from tujia_nlp import format_syllable, normalize_shape, to_ipa, to_ye

to_ye("la35")                    # "laf"
to_ye("kaŋ35")                   # "gangf"   legacy input accepted
to_ipa("gangf")                  # "kã35"    output in the current convention
format_syllable("la35", "ipa")   # "la³⁵"
normalize_shape("ʐuo")           # "zuo"
```

Notation rules:

- `to_ipa` always emits the current convention: nasalised vowels `ã ẽ ĩ ũ`, `z`, `iou`.
- `to_ye` accepts both: legacy `aŋ eŋ iŋ oŋ`, `ʐ`, `iu` are folded before lookup.
- A few contrasts are not distinguished by the Ye scheme (`ɿ` / `i`, `ə` / `ɤ`), so conversion
  is one-way: `to_ye` can produce Ye, `to_ipa` cannot recover them.

The syllable table covers 291 Northern Tujia syllables, 227 attested in corpus material and
64 derived by rule.

Beyond IPA ↔ Ye, four helpers are available as submodules:

```python
from tujia_nlp import corpus, phone_norm, syllable, zh_sound

syllable.split_head("a⁵⁵ji²¹")     # [("a", 55), ("ji", 21)]
syllable.tone_stats(["la³⁵"])      # tone usage per shape
phone_norm.canon("d")              # ["t"]  voiced stops fold onto voiceless
zh_sound.pinyin_to_ipa("ni3")      # ("ni", 21)
corpus.to_ipa("xi2")               # [{"ipa": "ɕi", ...}]  corpus romanisation
```

`corpus` covers the spelling used by the text corpora (`x-` = ɕ-, `hh-` = ɣ-, `an` = ã),
which differs from the standard Ye inventory in `north.json`.

`zh_sound.text_to_syllables` accepts hanzi only when the optional `pypinyin` package is
installed (`pip install "tujia-nlp[zh]"`); plain pinyin input needs nothing extra.

### Attested syllable inventory

`inventory` answers "does this syllable exist", which is what ASR post-processing, TTS
front-end checks and LLM output validation all need. It ships a pinned snapshot of the
frozen table (1,521 syllables attested across the source dictionaries; `legal` = two or
more sources, `attested` = one).

```python
from tujia_nlp import inventory

inventory.is_legal("liã")                        # True
inventory.nearest("tɕʰiøŋ")                      # "tɕʰiũ"  northern fold
inventory.analyze("tɕʰiøŋ²¹ma⁵⁵")                # per-syllable verdict, tones kept
inventory.normalize_text("tɕʰiøŋ²¹ ma⁵⁵")        # "tɕʰiũ²¹ ma⁵⁵"
```

This is a different table from `north.json`: `north.json` is the Ye scheme (25 initials,
40 finals, 291 syllables the orthography can spell); `syllabary.json` is what the
dictionaries actually attest. Point `TUJIA_SYLLABARY` at a frozen `syllables-*.tsv` to
swap versions without reinstalling.

## Data coverage

The published package contains only the syllable tables. Recordings, transcripts and
dictionary entries are not distributed. The attested inventory carries no source names
and no per-source attribution; only a support count bucket per syllable.

## Repository layout

```
src/tujia_nlp/     the package: tones.py, ye.py, syllable.py, inventory.py, phone_norm.py, zh_sound.py
schema/            dictionary entry and pack manifest contracts (JSON Schema)
tests/             unit tests (pytest)
docs/              annotation standards and resources
tools/             early conversion scripts, superseded by the package
```

## Zenodo datasets

Two public North Tujia text corpora are archived on Zenodo. This repository does not
redistribute them; obtain the files from the DOIs below.

1. **V1 (DOI: 10.5281/zenodo.4446698)** — incomplete, contains annotation errors, for
   provenance only, **not for training**.
2. **V2 (DOI: 10.5281/zenodo.4447924)** — the recommended source for translation, LLM, ASR
   and TTS work; includes the orthography mapping, vocabulary, textbook sentences, folk
   narratives and greetings.

The upstream record is marked `Other (Public Domain)`, which is not a standard licence. This
project does not redistribute the files. Standardised data derived by this project is
released under CC-BY 4.0, covering only the new conversion and annotation work.

### Citation

Zhou, Y., & Hill, N. W. (2021). *A collection of North Tujia (Bifzivsar) vocabulary and
textual passages for use in NLP* (Version 2) [Data set]. Zenodo.
https://doi.org/10.5281/zenodo.4447924

See `DATASET_LICENSE.md` for the full constraints.

## Contributing

- Tujia speakers: field recordings, semantic proofreading, pronunciation checks.
- NLP developers: model fine-tuning, code review, front-end tools.
- Linguists: vocabulary expansion and grammatical notes.

### Ethics

Every field recording requires prior **informed consent**. Speaker privacy must be protected
and recorded material must not be used commercially without permission.

## Lexicon data

The repository also carries the public data that other Tujia projects consume.
The Python package itself stays code-only; `data/` ships with the source tree.

```
data/
  inventory/              syllables-0.6.3.tsv + manifest.json (sha256, counts, folds)
  packs/tujia-open-core/  CC-BY-4.0 core vocabulary (1,620 entries, Zhou 2020)
  schema/                 syllabary + packindex contracts
tools/lexicon/
  validate.py             contract checks (columns, counts, sha, no source names)
  package.py              build .tjpack (manual; consumers usually read the directory)
  build_open_core.py      regenerate the open-core pack
```

- `inventory/` is the authoritative syllable table; `src/tujia_nlp/data/syllabary.json`
  is a pinned snapshot for offline use and must match it.
- `packs/tujia-open-core/` is a `tujia.pack/v1` directory; Dart consumers
  (`tujia-trans`) read it without conversion.
- Validate after any data change:

```bash
python3 tools/lexicon/validate.py data/inventory
```

### Attribution

`packs/tujia-open-core/` is derived from Zhou, Yulou (2020), *Proto-Bizic: A Study of
Tujia Historical Phonology* (Bachelor thesis, Stanford University), licensed
**CC-BY-4.0**. The digitised data is also published at
<https://github.com/luggroo/bizic-dictionary>; its maintainer granted permission to
reuse it, asking for attribution when published.

```
Zhou, Y. (2020). Proto-Bizic: A Study of Tujia Historical Phonology
[Bachelor thesis]. Stanford University.
```

## License

- Source code: **MIT** (see `LICENSE`).
- Third-party source corpora: not redistributed; rights remain with their authors.
- Data produced here, including `data/inventory/` and `data/packs/tujia-open-core/`:
  **CC-BY 4.0** with attribution.
- Field recordings: governed by each speaker's individual consent form.

## Roadmap

- [x] Repository bootstrapped
- [x] `tujia_nlp` orthography package (IPA ↔ Ye, tone notation)
- [x] Dictionary entry and pack manifest schemas
- [ ] Annotation standard finalised
- [ ] Base vocabulary assembled
- [ ] Field recording collection started
- [ ] Tujia ASR fine-tuning
- [ ] Tujia TTS training
- [ ] Tujia ↔ Chinese translation model
- [ ] Dialogue web demo
- [ ] LLM SFT (long-term)
