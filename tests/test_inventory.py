"""Tests for the closed syllable inventory."""

import json

import pytest

from tujia_nlp import inventory


@pytest.fixture(scope="module")
def inv():
    return inventory.load()


def test_snapshot_is_complete(inv):
    assert inv.version == "0.6.3"
    assert len(inv) == 1347
    statuses = {s.status for s in inv}
    assert statuses == {"legal", "attested"}


def test_legal_lookup(inv):
    assert inv.is_legal("liã")
    assert inv.is_legal("tɕʰiũ")
    assert not inv.is_legal("qwerty")
    assert "ma" in inv


def test_spelling_is_undone(inv):
    # aspiration written with h, digraph letters, alveolo-palatal nasal
    assert inv.canonical("khe") == "kʰɤ"
    assert inv.canonical("ʦa") == "tsa"
    assert inv.canonical("ȵi") == "ni"
    assert inv.canonical("e") == "ɤ"


def test_rhyme_folds(inv):
    assert inv.canonical("pian") == "piã"
    assert inv.canonical("tɤi") == "tei"
    assert inv.canonical("tɕʰiøŋ") == "tɕʰiũ"
    assert inv.canonical("ian") == "iã"


def test_nearest_snaps_notation_only(inv):
    assert inv.nearest("tɕʰiøŋ") == "tɕʰiũ"
    assert inv.nearest("pian") == "piã"
    assert inv.nearest("qwerty") is None


def test_nearest_can_be_restricted_to_legal(inv):
    attested = next(s for s in inv if s.status == "attested")
    assert inv.nearest(attested.shape, legal_only=True) != attested.shape


def test_analyze_keeps_tones(inv):
    out = inv.analyze("tɕʰiøŋ²¹ma⁵⁵")
    assert [(a.shape, a.tone) for a in out] == [("tɕʰiũ", "²¹"), ("ma", "⁵⁵")]
    assert all(a.ok for a in out)


def test_normalize_text(inv):
    assert inv.normalize_text("tɕʰiøŋ²¹ ma⁵⁵ kʰa²¹") == "tɕʰiũ²¹ ma⁵⁵ kʰa²¹"
    assert inv.normalize_text("ȵi³⁵ khe³") == "ni³⁵ kʰɤ³"


def test_analyze_marks_unknown(inv):
    out = inv.analyze("qwerty⁵⁵")
    assert out[0].status is None
    assert not out[0].ok
    assert out[0].replacement is None


def test_load_frozen_tsv(tmp_path):
    (tmp_path / "syllables-9.9.9.tsv").write_text(
        "syllable\tonset\trhyme\tstatus\tn_books\n"
        "la\tl\ta\tlegal\t3+\n"
        "mɤ\tm\tɤ\tattested\t1\n",
        encoding="utf-8",
    )
    (tmp_path / "manifest.json").write_text(
        json.dumps({"folds": {"ian": "iã"}}), encoding="utf-8"
    )
    inv = inventory.load(tmp_path / "syllables-9.9.9.tsv")
    assert inv.version == "9.9.9"
    assert len(inv) == 2
    assert inv.is_legal("la")
    assert inv.canonical("lian") == "liã"


def test_env_override(tmp_path, monkeypatch):
    (tmp_path / "syllables-1.0.0.tsv").write_text(
        "syllable\tonset\trhyme\tstatus\tn_books\nla\tl\ta\tlegal\t3+\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(inventory.ENV, str(tmp_path / "syllables-1.0.0.tsv"))
    assert len(inventory.load()) == 1
