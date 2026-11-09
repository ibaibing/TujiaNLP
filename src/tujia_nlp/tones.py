"""Tone notation conversion for Tujia.

The same four tones are written three ways in the literature and in our tools:

    Chao five-level digits   "55"  "35"  "21"  "53"
    Superscript digits       "55"  "35"  "21"  "53"   (rendered as superscripts)
    Ye tone letters          "x"   "f"   "r"   "v"

This module converts between them. It is deliberately independent of any
dialect: the four tones and their letters are shared by north and south.
"""

from __future__ import annotations

CHAO_TONES = ("55", "35", "21", "53")

CHAO_TO_LETTER = dict(zip(CHAO_TONES, "xfrv"))
LETTER_TO_CHAO = {v: k for k, v in CHAO_TO_LETTER.items()}

_DIGIT_TO_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_SUP_TO_DIGIT = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
_SUP_DIGITS = frozenset("⁰¹²³⁴⁵⁶⁷⁸⁹")


def to_superscript(tone: str) -> str:
    """``"35"`` -> ``"³⁵"``."""
    _check(tone)
    return tone.translate(_DIGIT_TO_SUP)


def from_superscript(text: str) -> str:
    """``"³⁵"`` -> ``"35"``."""
    tone = text.translate(_SUP_TO_DIGIT)
    _check(tone)
    return tone


def to_letter(tone: str) -> str:
    """``"35"`` -> ``"f"``."""
    _check(tone)
    return CHAO_TO_LETTER[tone]


def from_letter(letter: str) -> str:
    """``"f"`` -> ``"35"``."""
    try:
        return LETTER_TO_CHAO[letter]
    except KeyError:
        raise ValueError(
            f"unknown tone letter {letter!r}; expected one of {''.join(LETTER_TO_CHAO)}"
        ) from None


def normalize(tone: str) -> str:
    """Accept ``"35"``, ``"³⁵"`` or ``"f"`` and return ``"35"``."""
    if tone in CHAO_TO_LETTER:
        return tone
    if tone in LETTER_TO_CHAO:
        return LETTER_TO_CHAO[tone]
    if all(ch in _SUP_DIGITS for ch in tone):
        return from_superscript(tone)
    raise ValueError(
        f"cannot read tone {tone!r}; expected one of {CHAO_TONES}, "
        f"their superscript forms, or {'/'.join(LETTER_TO_CHAO)}"
    )


def _check(tone: str) -> None:
    if tone not in CHAO_TO_LETTER:
        raise ValueError(
            f"unknown tone {tone!r}; expected one of {', '.join(CHAO_TONES)}"
        )
