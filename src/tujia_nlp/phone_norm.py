"""Phone-symbol normalisation across tools.

Different recognisers emit different IPA conventions for the same sound: ZIPA
uses coarticulated symbols, espeak writes ɒ / ʌ / ɻ̩, Allosaurus writes
t̪ʰ / d͡ʒ / ɻ̩. Comparing raw output would count notation differences as
recognition errors, so this module folds every symbol into a coarse local
class (place + manner + vowel height/backness) and then applies areal merges
(south-western Mandarin has no retroflexes, so tʂ / ʂ / ʐ collapse to ts / s / z).

This is equivalence-class merging only, never correction. If Allosaurus
transcribes the word for "earth" as t̪ʰ i ʂ o, the class sequence becomes
tʰ i s o and the error is preserved.
"""

import re
import unicodedata

# Combining marks (aspiration, dentalisation, centralisation, devoicing) are
# dropped; the base symbol carries the class.
_COMB = dict.fromkeys(range(0x300, 0x370))

CONSONANT = {
    # Stops: aspiration contrast is preserved
    "p": "p", "pʰ": "pʰ", "b": "p", "bʰ": "pʰ",
    "t": "t", "tʰ": "tʰ", "d": "t", "dʰ": "tʰ",
    "ʈ": "t", "ʈʰ": "tʰ", "ɖ": "t",
    "k": "k", "kʰ": "kʰ", "ɡ": "k", "g": "k", "gʰ": "kʰ",
    "q": "k", "qʰ": "kʰ", "ɢ": "k",
    "ʔ": "",
    # Affricates
    "ts": "ts", "tsʰ": "tsʰ", "dz": "ts",
    "tʂ": "ts", "tʂʰ": "tsʰ", "dʐ": "ts",   # retroflex merges into alveolar
    "tɕ": "tɕ", "tɕʰ": "tɕʰ", "dʑ": "tɕ", "dʒ": "tɕ", "tʃ": "ts", "tʃʰ": "tsʰ",
    "pf": "p", "pfʰ": "pʰ",
    # Fricatives
    "f": "f", "v": "f",
    "s": "s", "z": "s", "ʂ": "s", "ʐ": "s", "ʃ": "s", "ʒ": "s",
    "ɕ": "ɕ", "ʑ": "ɕ",
    "x": "x", "ɣ": "x", "h": "x", "ɦ": "x", "χ": "x", "ʁ": "x",
    "θ": "s", "ð": "s", "β": "f", "ɸ": "f",
    # Nasals
    "m": "m", "n": "n", "ɳ": "n", "ɲ": "n", "ŋ": "ŋ", "ɴ": "ŋ", "ɱ": "m",
    # Laterals and rhotics
    "l": "l", "ɭ": "l", "ɺ": "l", "r": "l", "ɾ": "l", "ɹ": "l", "ɻ": "l",
    # Approximants
    "j": "j", "w": "w", "ʋ": "w", "ɥ": "j", "ɰ": "w",
    # Others
    "c": "tɕ", "ɟ": "tɕ", "ʎ": "l",
}

VOWEL = {
    "i": "i", "ɪ": "i", "e": "i", "ɪ̞": "i",
    "y": "y", "ʏ": "y", "ø": "y", "œ": "y",
    "ɨ": "ɨ", "ɯ": "ɨ", "ɤ": "ɤ", "ʌ": "ɤ", "ə": "ɤ", "ɚ": "ɤ", "ɜ": "ɤ",
    "a": "a", "ɑ": "a", "ɒ": "a", "æ": "a", "ɐ": "a", "ɶ": "a",
    "ɛ": "e", "æ̞": "e",
    "o": "o", "ɔ": "o", "ʊ": "u", "u": "u",
}

# Nuclei used for rough syllable segmentation.
NUCLEI = set("i y ɨ ɯ ɤ ʌ ə a ɑ ɒ æ ɛ e o ɔ u ʊ ɐ".split())


def _strip(sym):
    """Drop combining marks and joiners; unify affricate and doubled spellings."""
    s = unicodedata.normalize("NFD", sym)
    s = s.translate(_COMB)
    s = unicodedata.normalize("NFC", s)
    s = s.replace("͡", "").replace("͜", "")
    s = s.replace(".", "").replace("ː", "").replace("ˑ", "")
    s = re.sub(r"[0-9]", "", s)
    # espeak writes aspiration as ASCII h (th/ph/kh/tsh/tɕh); fold back to ʰ
    for a, b in (("tɕh", "tɕʰ"), ("tʃh", "tʃʰ"), ("tʂh", "tʂʰ"),
                ("tsh", "tsʰ"), ("th", "tʰ"), ("ph", "pʰ"), ("kh", "kʰ")):
        s = s.replace(a, b)
    return s


_KNOWN = sorted(set(list(CONSONANT) + list(VOWEL)), key=len, reverse=True)


def _split_known(s):
    """Greedily split concatenated phones such as ɑu / ai / uei / onɡ."""
    out, i = [], 0
    while i < len(s):
        for k in _KNOWN:
            if s.startswith(k, i):
                out.append(k)
                i += len(k)
                break
        else:
            return None
    return out


def canon(sym):
    """One phone symbol -> list of local classes (may split); [] when unknown."""
    if not sym or sym in ("<pad>", "<s>", "</s>", "|", "‖"):
        return []
    s = _strip(sym)
    if not s:
        return []
    if s in CONSONANT:
        return [CONSONANT[s]]
    if s in VOWEL:
        return [VOWEL[s]]
    if len(s) > 1 and s[-1] in ("ʷ", "ʲ", "ˠ", "ˤ"):
        base = canon(s[:-1])
        if base:
            return base
    parts = _split_known(s)
    if parts:
        out = []
        for p in parts:
            out += canon(p)
        return out
    if len(s) == 1:
        low = s.lower()
        if low in CONSONANT:
            return [CONSONANT[low]]
        if low in VOWEL:
            return [VOWEL[low]]
    return []


def canon_seq(seq):
    out = []
    for s in seq:
        out += canon(s)
    return out


def syllabify(seq):
    """Rough syllable split: vowel nuclei anchor, preceding consonants attach, nasals close.

    Note this is a phone-string heuristic; it is unrelated to the dictionary
    constrained segmentation used by the decoding engine.
    """
    out, cur, seen_v = [], [], False
    for c in seq:
        if c in NUCLEI:
            if seen_v:
                out.append(cur)
                cur = [c]
            else:
                cur.append(c)
            seen_v = True
        elif c == "ŋ" and seen_v:
            cur.append(c)
            out.append(cur)
            cur, seen_v = [], False
        elif c in ("n",) and seen_v and len(cur) and cur[-1] in NUCLEI:
            cur.append(c)
            out.append(cur)
            cur, seen_v = [], False
        else:
            if seen_v:
                out.append(cur)
                cur, seen_v = [], False
            cur.append(c)
    if cur:
        out.append(cur)
    return ["".join(x) for x in out if x]


def strip_digits(tokens):
    return [t for t in tokens if not re.fullmatch(r"[0-9]+", t or "")]
