"""Tests for tujia_nlp.phone_norm."""

from tujia_nlp import phone_norm as pn


def test_canon_keeps_aspiration():
    assert pn.canon("tʰ") == ["tʰ"]
    assert pn.canon("t") == ["t"]


def test_canon_merges_voicing():
    # Voiced stops collapse onto the voiceless class.
    assert pn.canon("d") == ["t"]
    assert pn.canon("g") == ["k"]


def test_canon_retroflex_merges():
    assert pn.canon("ʈʰ") == ["tʰ"]
    assert pn.canon("ʂ") == ["s"]
    assert pn.canon("ʐ") == ["s"]


def test_canon_strips_joiners_and_marks():
    assert pn.canon("t͡ɕ") == ["tɕ"]
    assert pn.canon("aː") == ["a"]


def test_canon_splits_concatenation():
    assert pn.canon("tɕʰi") == ["tɕʰ", "i"]
    assert pn.canon("ɑu") == ["a", "u"]


def test_canon_unknown():
    assert pn.canon("❓") == []
    assert pn.canon("") == []


def test_syllabify_basic():
    assert pn.syllabify(["p", "a", "n"]) == ["pan"]
    assert pn.syllabify(["p", "a", "n", "t", "i"]) == ["pan", "ti"]


def test_syllabify_nasal_coda():
    assert pn.syllabify(["ts", "a", "ŋ"]) == ["tsaŋ"]


def test_canon_seq():
    assert pn.canon_seq(["d", "a", "ɡ"]) == ["t", "a", "k"]


def test_strip_digits():
    assert pn.strip_digits(["a", "55", "b"]) == ["a", "b"]
