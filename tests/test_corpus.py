"""Corpus romanisation (x- = ɕ-, hh- = ɣ-) to IPA."""

from tujia_nlp import corpus


def test_parse_syllable():
    assert corpus.parse_syllable("laf") == ("l", "a", "f")
    assert corpus.parse_syllable("xi2") == ("x", "i", "f")
    assert corpus.parse_syllable("hhi") == ("hh", "i", "")
    assert corpus.parse_syllable("zzz") is None


def test_to_ipa_single():
    assert corpus.to_ipa("dax")[0]["ipa"] == "ta"
    assert corpus.to_ipa("xi2")[0]["ipa"] == "ɕi"
    assert corpus.to_ipa("hhif")[0]["ipa"] == "ɣi"


def test_to_ipa_splits_words_and_reports_failures():
    rows = corpus.to_ipa("tur bav bor")
    assert [r["text"] for r in rows] == ["tur", "bav", "bor"]
    assert all(r["ok"] for r in rows)

    bad = corpus.to_ipa("bitzivsar")     # not a legal syllable run
    assert len(bad) == 1 and bad[0]["ok"] is False


def test_nasal_finals_fold_to_one_series():
    assert corpus.to_ipa("lan")[0]["ipa"] == "lã"
    assert corpus.to_ipa("lang")[0]["ipa"] == "lã"
    assert corpus.to_ipa("lun")[0]["ipa"] == "lũ"
