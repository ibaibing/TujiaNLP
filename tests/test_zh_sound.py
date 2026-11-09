"""Tests for tujia_nlp.zh_sound."""

from tujia_nlp import zh_sound as zs


def test_pinyin_digit_tone():
    assert zs.pinyin_to_ipa("ni3") == ("ni", 21)
    assert zs.pinyin_to_ipa("ma1") == ("ma", 55)


def test_pinyin_tone_mark():
    # ǎ carries tone 3
    assert zs.pinyin_to_ipa("nǎ") == ("na", 21)


def test_pinyin_initial_and_final():
    assert zs.pinyin_to_ipa("zhong1") == ("tʂuŋ", 55)
    assert zs.pinyin_to_ipa("hao3") == ("xau", 21)


def test_pinyin_whole_syllable():
    # zi matches final "i" before the whole-syllable branch, so it stays tsi.
    assert zs.pinyin_to_ipa("zi1") == ("tsi", 55)


def test_pinyin_empty():
    assert zs.pinyin_to_ipa("") == ("", None)


def test_text_to_syllables_pinyin():
    out = zs.text_to_syllables("ni hao")
    assert out == [
        {"ipa": "ni", "tone": None, "text": "ni"},
        {"ipa": "xau", "tone": None, "text": "hao"},
    ]


def test_text_to_syllables_empty():
    assert zs.text_to_syllables("") == []


def test_sound_class():
    assert zs.sound_class("p") == "stop"
    assert zs.sound_class("a") == "vowel"
    assert zs.sound_class("zzz") == "zzz"


def test_class_edit_identical():
    assert zs.class_edit("pa", "pa") == 0.0


def test_class_edit_same_class_is_free():
    # p and t are both stops, so swapping them costs nothing.
    assert zs.class_edit("pa", "ta") == 0.0


def test_class_edit_substitution_costs_less_than_insertion():
    # nasal vs stop costs 0.6; "pata" adds two phones, so insertion costs 2.0
    assert zs.class_edit("ma", "pa") == 0.6
    assert zs.class_edit("pa", "pata") == 2.0


def test_class_edit_empty():
    assert zs.class_edit("", "pa") == 2.0
    assert zs.class_edit("pa", "") == 2.0
