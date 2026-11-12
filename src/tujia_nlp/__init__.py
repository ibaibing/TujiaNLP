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
"""

from . import corpus, inventory
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

__version__ = "0.3.0"

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
    "normalize",
    "normalize_shape",
    "split_tone",
    "to_ipa",
    "to_letter",
    "to_superscript",
    "to_ye",
    "__version__",
]
