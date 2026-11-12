"""Corpus romanisation to IPA.

The text corpora use a second spelling convention alongside the standard Ye
table in :mod:`tujia_nlp.ye`: ``x-`` stands for ɕ-, ``hh-`` for ɣ-, a final
``base + n`` is a nasalised vowel, and ``-ng`` folds into the same nasal. The
standard table writes ɕ without an initial letter and ɣ as ``hx``, so the two
inventories do not overlap one-to-one.

This module keeps that convention in one place so that the pipelines do not
each carry their own copy. Conversions back to standard Ye still go through
:func:`tujia_nlp.to_ye`.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).parent / "data" / "corpus.json"

TONE_LETTERS = frozenset("xfrv")
DIGIT_TO_LETTER = {"1": "x", "2": "f", "3": "r", "4": "v"}
WORD_SEP = frozenset(" \t-~,;、|")
_MAX_SYLLABLE = 6


def _read() -> dict:
    return json.loads(_DATA.read_text(encoding="utf-8"))


_RAW = _read()
INITIAL_TO_IPA: dict[str, str] = _RAW["initials"]
FINAL_TO_IPA: dict[str, str] = _RAW["finals"]


@lru_cache(maxsize=None)
def _tables() -> tuple[dict[str, str], dict[str, str], tuple[str, ...], tuple[str, ...]]:
    return (
        INITIAL_TO_IPA,
        FINAL_TO_IPA,
        tuple(sorted(INITIAL_TO_IPA, key=len, reverse=True)),
        tuple(sorted(FINAL_TO_IPA, key=len, reverse=True)),
    )


def parse_syllable(text: str):
    """One corpus syllable -> ``(initial, final, tone)`` or ``None``.

    A syllable is an optional initial, a final, and an optional tone (letter
    ``x/f/r/v`` or digit ``1-4``, returned as a letter).
    """
    initials, finals, by_len_i, _ = _tables()
    if not text:
        return None
    tone, body = "", text
    if len(text) >= 2 and text[-1] in TONE_LETTERS:
        tone, body = text[-1], text[:-1]
    elif len(text) >= 2 and text[-1] in DIGIT_TO_LETTER:
        tone, body = DIGIT_TO_LETTER[text[-1]], text[:-1]
    for initial in ("",) + by_len_i:
        if initial and not body.startswith(initial):
            continue
        rest = body[len(initial):]
        if rest in finals:
            return initial, rest, tone
    return None


def _split_chunk(chunk: str) -> list[tuple[str, tuple[str, str, str] | None]]:
    """Split a run of letters into syllables (DP, fewest then longest)."""
    n = len(chunk)
    memo: dict[int, list | None] = {}

    def solve(i: int):
        if i == n:
            return []
        if i in memo:
            return memo[i]
        best = None
        for j in range(min(n, i + _MAX_SYLLABLE), i, -1):
            piece = chunk[i:j]
            parsed = parse_syllable(piece)
            if parsed is None:
                continue
            tail = solve(j)
            if tail is None:
                continue
            candidate = [(piece, parsed)] + tail
            if best is None or len(candidate) < len(best):
                best = candidate
        memo[i] = best
        return best

    got = solve(0)
    if got is None:
        return [(chunk, None)]
    return got


def to_ipa(text: str) -> list[dict]:
    """Corpus Ye text -> one record per syllable.

    Each record has ``text``, ``initial``, ``final``, ``tone``, ``ipa`` and
    ``ok``. A run that cannot be split yields a single ``ok: False`` record so
    callers can count and report coverage instead of losing the input.
    """
    out: list[dict] = []
    chunk = ""
    for ch in str(text) + " ":
        if ch in WORD_SEP:
            if chunk:
                out.extend(_records(chunk))
                chunk = ""
        else:
            chunk += ch
    if chunk:
        out.extend(_records(chunk))
    return out


def _records(chunk: str) -> list[dict]:
    initials, finals, _, _ = _tables()
    records = []
    for syllable, parsed in _split_chunk(chunk):
        if parsed is None:
            records.append({"text": syllable, "initial": "", "final": "",
                            "tone": "", "ipa": "", "ok": False})
            continue
        initial, final, tone = parsed
        records.append({
            "text": syllable,
            "initial": initial,
            "final": final,
            "tone": tone,
            "ipa": initials.get(initial, "") + finals.get(final, ""),
            "ok": True,
        })
    return records
