"""Tujia orthography utilities: tone notation, IPA <-> Ye, phone normalisation.

    from tujia_nlp import to_ye, to_ipa, format_syllable

    to_ye("la35")                  # "laf"
    to_ipa("laf")                  # "la35"
    format_syllable("la35", "ipa") # "la³⁵"

Submodules:

    tones       tone notation: Chao digits, superscripts, Ye tone letters
    ye          IPA syllable <-> Ye spelling (legacy and 2021 spellings accepted)
    corpus      corpus romanisation (x- = ɕ-, hh- = ɣ-) to IPA
    syllable    toned IPA word splitting and tone statistics
    inventory   closed syllable inventory: is_legal / nearest / analyze
    phone_norm  phone-symbol normalisation across recognisers
    zh_sound    pinyin / hanzi to approximate phone sequences
    lexicon     open vocabulary packs shipped under data/packs/
"""

from . import corpus, inventory, lexicon
from .lexicon import pack_dir, pack_entries, pack_lexicon_path, pack_manifest
from .tones import (
    CHAO_TONES,
    CHAO_TO_LETTER,
    LETTER_TO_CHAO,
    from_letter,
    from_superscript,
    normalize,
    to_letter,
    to_superscript,
)
from .ye import (
    available_dialects,
    format_syllable,
    normalize_shape,
    split_tone,
    to_ipa,
    to_ye,
)

__version__ = "0.4.0"

__all__ = [
    "CHAO_TONES",
    "CHAO_TO_LETTER",
    "LETTER_TO_CHAO",
    "available_dialects",
    "corpus",
    "format_syllable",
    "from_letter",
    "from_superscript",
    "inventory",
    "lexicon",
    "normalize",
    "normalize_shape",
    "pack_dir",
    "pack_entries",
    "pack_lexicon_path",
    "pack_manifest",
    "split_tone",
    "to_ipa",
    "to_letter",
    "to_superscript",
    "to_ye",
    "__version__",
]
