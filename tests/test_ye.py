"""Tests for tujia_nlp.ye."""

import pytest

from tujia_nlp import format_syllable, to_ipa, to_ye


@pytest.mark.parametrize(
    "ipa, ye",
    [
        ("la35", "laf"),
        ("la³⁵", "laf"),
        ("keŋ55", "gengx"),
        ("liŋ21", "lingr"),
        ("kuo53", "guov"),
        ("ʐuo35", "ruof"),
        ("tsʰeŋ21", "cengr"),
        ("ɕiɛ55", "iex"),
        ("a55", "ax"),
    ],
)
def test_to_ye(ipa, ye):
    assert to_ye(ipa) == ye


def test_to_ye_without_tone():
    assert to_ye("la") == "la"


def test_to_ye_unknown_shape_falls_back_to_ipa():
    assert to_ye("xyz35") == "xyz³⁵"


@pytest.mark.parametrize("ye, ipa", [("laf", "la35"), ("gengx", "kẽ55"), ("guov", "kuo53")])
def test_to_ipa(ye, ipa):
    assert to_ipa(ye) == ipa


def test_to_ipa_without_tone():
    assert to_ipa("la") == "la"


def test_to_ipa_ambiguous_prefers_zero_initial():
    # iɛ and ɕiɛ both spell "ie"; the zero-initial reading wins.
    assert to_ipa("ie") == "iɛ"


def test_to_ipa_rejects_unknown():
    with pytest.raises(ValueError):
        to_ipa("zzz")


def test_format_syllable():
    assert format_syllable("la35", "ascii") == "la35"
    assert format_syllable("la35", "ipa") == "la³⁵"
    assert format_syllable("la35", "ye") == "laf"


def test_format_syllable_rejects_unknown_format():
    with pytest.raises(ValueError):
        format_syllable("la35", "utf8")


def test_roundtrip_over_table():
    from tujia_nlp.ye import _load, normalize_shape

    bad = []
    for shape in _load("north")["syllables"]:
        label = shape + "55"
        if to_ipa(to_ye(label)) != normalize_shape(shape) + "55":
            bad.append((label, to_ye(label), to_ipa(to_ye(label))))
    # Only ɕi / ɕiɛ omit the ɕ in Ye, so they can only come back as zero-initial.
    assert len(bad) <= 2, bad


def test_legacy_ipa_input_accepted():
    # Legacy spellings (aŋ / ʐ / iu) hit the same Ye as the 2021 convention.
    assert to_ye("kaŋ35") == "gangf"
    assert to_ye("ʐuo35") == "ruof"
    assert to_ye("liu55") == "liux"


def test_to_ipa_always_outputs_new_notation():
    from tujia_nlp import normalize_shape

    assert to_ipa("gangf") == "kã35"
    assert to_ipa("ruof") == "zuo35"
    assert to_ipa("liux") == "liou55"
    assert to_ipa("cengr") == "tsʰẽ21"
    # Legacy entries in the table are folded to the modern convention too.
    for shape in ("aŋ", "eŋ", "liŋ", "oŋ", "ʐu", "liu"):
        assert to_ipa(to_ye(shape + "35")) == normalize_shape(shape) + "35"


def test_normalize_shape():
    from tujia_nlp import normalize_shape

    assert normalize_shape("kaŋ") == "kã"
    assert normalize_shape("ʐuo") == "zuo"
    assert normalize_shape("tɕiu") == "tɕiou"
    assert normalize_shape("tɕʰiøŋ") == "tɕʰiøŋ"   # no rule for this shape, returned as-is


def test_south_not_available_yet():
    with pytest.raises(ValueError):
        to_ye("la35", dialect="south")


def test_to_ipa_digit_tone():
    assert to_ipa("la1") == "la55"
    assert to_ipa("la4") == "la53"
    assert to_ipa("guo2") == "kuo35"


def test_digit_tone_category():
    from tujia_nlp import format_syllable, split_tone

    assert split_tone("la2") == ("la", "35")
    assert to_ye("la2") == "laf"
    assert to_ye("la53") == "lav"          # two digits stay a Chao value
    assert format_syllable("la2", "ipa") == "la³⁵"


def test_to_ipa_corpus_spellings():
    # Text corpora write ɕ- as x- and ɣ- as hh-; the standard table does not.
    assert to_ipa("xi2") == "ɕi35"
    assert to_ipa("xie3") == "ɕiɛ21"
    assert to_ipa("xian2") == "ɕiã35"
    assert to_ipa("xiong1") == "ɕiøŋ55"
    assert to_ipa("hhi1") == "ɣi55"
    assert to_ipa("hhe2") == "ɣɤ35"


def test_unknown_ye_still_raises():
    with pytest.raises(ValueError):
        to_ipa("notasyllable2")
