"""Tests for tujia_nlp.syllable."""

from tujia_nlp import syllable as sy


def test_split_head_basic():
    assert sy.split_head("a⁵⁵ji²¹") == [("a", 55), ("ji", 21)]


def test_split_head_single():
    assert sy.split_head("la³⁵") == [("la", 35)]


def test_split_head_without_tone():
    assert sy.split_head("la") == [("la", None)]


def test_split_head_multi_char_tone():
    # ⁵⁵ is two superscript digits forming one tone.
    assert sy.split_head("tsʰeŋ²¹") == [("tsʰeŋ", 21)]


def test_expand_symbols():
    assert sy.expand_symbols("ʦɿ") == "tsɨ"
    assert sy.expand_symbols("ʨi") == "tɕi"


def test_clean_ipa_drops_punctuation():
    assert sy.clean_ipa("la，35") == "la35"


def test_phone_seq():
    assert sy.phone_seq("tsʰa") == ["t", "s", "ʰ", "a"]


def test_tone_stats():
    words = ["a⁵⁵ji²¹", "a⁵⁵pa²¹", "a³⁵"]
    stats = sy.tone_stats(words)
    assert stats["shapes"]["a"] == {55: 2, 35: 1}
    assert stats["pairs"][("ji", 21)] == 1


def test_tone_stats_accepts_entries():
    stats = sy.tone_stats([{"w": "la³⁵"}, {"w": "la⁵⁵"}])
    assert stats["shapes"]["la"] == {35: 1, 55: 1}


def test_tone_values_constant():
    assert sy.TONE_VALUES == (55, 35, 21, 53)
