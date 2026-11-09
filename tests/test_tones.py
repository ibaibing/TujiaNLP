"""Tests for tujia_nlp.tones."""

import pytest

from tujia_nlp import tones


def test_letter_roundtrip():
    for chao, letter in tones.CHAO_TO_LETTER.items():
        assert tones.to_letter(chao) == letter
        assert tones.from_letter(letter) == chao


def test_superscript_roundtrip():
    for chao in tones.CHAO_TONES:
        sup = tones.to_superscript(chao)
        assert len(sup) == 2
        assert tones.from_superscript(sup) == chao


def test_normalize_accepts_three_forms():
    assert tones.normalize("35") == "35"
    assert tones.normalize("³⁵") == "35"
    assert tones.normalize("f") == "35"


def test_unknown_tone_raises():
    with pytest.raises(ValueError):
        tones.to_letter("44")
    with pytest.raises(ValueError):
        tones.from_letter("z")
    with pytest.raises(ValueError):
        tones.normalize("abc")
