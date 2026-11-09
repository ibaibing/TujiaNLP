"""Toned IPA syllable handling: symbol expansion, word splitting, tone statistics.

Dictionary entries store a word as toned IPA such as ``a⁵⁵ji²¹``. This module
turns that into syllable shapes with integer tones, and collects how often each
shape occurs with each tone across a word list.
"""

import re
import unicodedata
from collections import Counter, defaultdict

SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
TONE_CHARS = set(SUP)
TONE_MAP = {c: str(i) for i, c in enumerate(SUP)}
TONE_VALUES = (55, 35, 21, 53)

_PUNCT = re.compile(r"[*，,。．、…~`'\"\s\[\]（）()／/|.]+")

# Dictionary-orthography symbols -> the phone symbols used by the recognisers.
DICT_EXPAND = {
    "ʦ": "ts", "ʣ": "ts", "ʨ": "tɕ", "ʥ": "tɕ", "ʧ": "tʃ", "ʤ": "tʃ",
    "ɿ": "ɨ", "ʮ": "ɨ",
    "ɔ": "o", "ə": "ɤ", "ɪ": "i", "ɘ": "ɤ", "ɜ": "ɤ", "ʌ": "ɤ", "ʊ": "u",
    "ɵ": "o", "ɶ": "a",
    "ɲ": "n", "ɳ": "n", "ɴ": "ŋ", "ɱ": "m",
    "ç": "ɕ", "ʝ": "j", "ʐ": "z", "ʑ": "z", "ʒ": "z",
    "χ": "x", "h": "x", "ɦ": "x", "ɣ": "k",
    "β": "w", "ʋ": "w", "v": "w", "ɸ": "f", "θ": "s", "ð": "z",
    "ɹ": "l", "ɻ": "l", "ɽ": "l", "ɾ": "l", "r": "l", "ʀ": "l", "ʁ": "l",
    "ɬ": "l", "ɮ": "l", "ɭ": "l", "ʟ": "l",
    "ʈ": "t", "ɖ": "t", "ȶ": "t", "ɟ": "k", "ɢ": "k",
    "ʏ": "y", "ʎ": "l", "ɯ": "u",
}


def clean_ipa(s):
    """Drop punctuation and combining marks (except aspiration), keep base symbols."""
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(ch for ch in s if ch == "ʰ" or unicodedata.combining(ch) == 0)
    s = unicodedata.normalize("NFC", s)
    return _PUNCT.sub("", s)


def expand_symbols(shape):
    """Map dictionary-orthography symbols to recogniser symbols.

    This is a symbol-level rewrite (``ʦ`` -> ``ts``, ``ɿ`` -> ``ɨ``). It is not
    the same thing as :func:`tujia_nlp.normalize_shape`, which converts between
    the legacy and the 2021 IPA spellings (``aŋ`` -> ``ã``).
    """
    out = []
    for ch in clean_ipa(shape):
        out.append(DICT_EXPAND.get(ch, ch))
    return "".join(out)


def split_head(word):
    """Toned IPA word -> ``[(shape, tone or None), ...]``.

    ``"a⁵⁵ji²¹"`` -> ``[("a", 55), ("ji", 21)]``
    """
    out = []
    cur, tone = "", ""
    for ch in clean_ipa(word):
        if ch in TONE_CHARS:
            tone += TONE_MAP[ch]
        else:
            if tone and cur:
                out.append((expand_symbols(cur), int(tone)))
                cur, tone = "", ""
            cur += ch
    if cur:
        out.append((expand_symbols(cur), int(tone) if tone else None))
    return out


def phone_seq(shape):
    """Shape -> per-character phone sequence (matches the recogniser spike grain)."""
    return list(shape)


def tone_stats(words):
    """Collect tone usage over word forms.

    ``words`` is an iterable of toned IPA strings (or ``{"w": ...}`` entries).
    Returns ``{"shapes": {shape: {tone: count}}, "pairs": {(shape, tone): count}}``.
    """
    shapes = defaultdict(Counter)
    pairs = defaultdict(int)
    for w in words:
        form = w.get("w", "") if isinstance(w, dict) else w
        for shape, tone in split_head(form):
            if not shape or tone is None or tone not in TONE_VALUES:
                continue
            shapes[shape][tone] += 1
            pairs[(shape, tone)] += 1
    return {"shapes": dict(shapes), "pairs": dict(pairs)}
