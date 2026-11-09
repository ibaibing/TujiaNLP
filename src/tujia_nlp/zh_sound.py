"""Chinese text to approximate phone sequences: pinyin (with tone marks) and hanzi.

Used when a second channel returns Chinese rather than Tujia, so the text can be
compared against Tujia phone strings. Hanzi support requires the optional
``pypinyin`` package; pinyin input works with the standard library alone.
"""

import unicodedata

TONE_BY_MARK = {"\u0304": 55, "\u0301": 35, "\u030c": 21, "\u0300": 53}

_INITIALS = [
    ("zh", "tʂ"), ("ch", "tʂʰ"), ("sh", "ʂ"),
    ("b", "p"), ("p", "pʰ"), ("m", "m"), ("f", "f"),
    ("d", "t"), ("t", "tʰ"), ("n", "n"), ("l", "l"),
    ("g", "k"), ("k", "kʰ"), ("h", "x"),
    ("j", "tɕ"), ("q", "tɕʰ"), ("x", "ɕ"),
    ("r", "z"), ("z", "ts"), ("c", "tsʰ"), ("s", "s"),
]

_FINALS = [
    ("iang", "iaŋ"), ("iong", "yuŋ"), ("uang", "uaŋ"), ("ueng", "uɤŋ"),
    ("ian", "iɛn"), ("iao", "iau"), ("ing", "iŋ"), ("ang", "aŋ"),
    ("eng", "ɤŋ"), ("ong", "uŋ"), ("uan", "uan"), ("uai", "uai"),
    ("üan", "yɛn"), ("üe", "yɛ"),
    ("ai", "ai"), ("ei", "ei"), ("ao", "au"), ("ou", "ou"),
    ("an", "an"), ("en", "ɤn"), ("er", "ɤl"),
    ("ia", "ia"), ("ie", "iɛ"), ("iu", "iou"), ("in", "in"),
    ("ua", "ua"), ("uo", "uo"), ("ui", "uei"), ("un", "uən"),
    ("ü", "y"), ("v", "y"),
    ("a", "a"), ("o", "o"), ("e", "ɤ"), ("i", "i"), ("u", "u"),
]

_WHOLE_SYLLABLES = ("zhi", "chi", "shi", "ri", "zi", "ci", "si")

# Mandarin digit tones (1-4, neutral) mapped to Tujia Chao values.
_DIGIT_TONE = {1: 55, 2: 35, 3: 21, 4: 53, 5: 21}


def _strip_tone(s):
    decomposed = unicodedata.normalize("NFD", s)
    tone = None
    letters = []
    for ch in decomposed:
        if ch in TONE_BY_MARK:
            tone = TONE_BY_MARK[ch]
        elif unicodedata.combining(ch) == 0:
            letters.append(ch)
    return "".join(letters).lower(), tone


def pinyin_to_ipa(syl):
    """One pinyin syllable (tone mark or digit tone) -> (IPA string, tone or None)."""
    if not syl:
        return "", None
    tail = None
    if syl[-1].isdigit():
        tail = _DIGIT_TONE.get(int(syl[-1]))
        syl = syl[:-1]
    base, mark_tone = _strip_tone(syl)
    tone = tail or mark_tone
    if not base:
        return "", tone

    for ini, ipa in _INITIALS:
        if base.startswith(ini):
            rest = base[len(ini):]
            if rest:
                for fin, fipa in _FINALS:
                    if rest == fin:
                        return ipa + fipa, tone
            if rest in ("i", "u", "ü", "v") or not rest:
                # Whole-syllable readings: zhi/chi/shi/ri/zi/ci/si
                if base in _WHOLE_SYLLABLES:
                    return ipa + "ɨ", tone
                if ini in ("y", "w"):
                    continue
                return ipa, tone
    if base in _WHOLE_SYLLABLES:
        return "tʂ" + "ɨ", tone
    if base.startswith("y"):
        rest = base[1:]
        mp = {"i": "i", "in": "in", "ing": "iŋ", "a": "ia", "an": "iɛn",
              "ang": "iaŋ", "ao": "iau", "e": "iɛ", "ou": "iou", "u": "y", "ue": "yɛ",
              "uan": "yɛn", "un": "yn"}
        return mp.get(rest, "i" + rest), tone
    if base.startswith("w"):
        rest = base[1:]
        mp = {"u": "u", "a": "ua", "o": "uo", "ai": "uai", "ei": "uei",
              "an": "uan", "en": "uən", "ang": "uaŋ", "eng": "uɤŋ"}
        return mp.get(rest, "u" + rest), tone
    for fin, fipa in _FINALS:
        if base == fin:
            return fipa, tone
    return base, tone


def text_to_syllables(text):
    """Text -> [{ipa, tone, text}]; None when nothing can be parsed.

    Hanzi input needs the optional ``pypinyin`` package, imported lazily so that
    plain pinyin input keeps working with the standard library alone.
    """
    text = (text or "").strip()
    if not text:
        return []
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):
        try:
            from pypinyin import Style, pinyin
        except ImportError:
            return None
        rows = pinyin(text, style=Style.TONE3, errors="ignore")
        out = []
        for r in rows:
            if not r:
                continue
            syl = r[0]
            ipa, tone = pinyin_to_ipa(syl)
            if ipa:
                out.append({"ipa": ipa, "tone": tone, "text": syl})
        return out or None

    out = []
    for tok in text.replace("，", " ").replace("。", " ").split():
        ipa, tone = pinyin_to_ipa(tok)
        if ipa:
            out.append({"ipa": ipa, "tone": tone, "text": tok})
    return out or None


_CLASSES = {
    "p": "stop", "pʰ": "stop", "b": "stop", "t": "stop", "tʰ": "stop", "d": "stop",
    "k": "stop", "kʰ": "stop", "g": "stop", "ʔ": "stop",
    "ts": "affricate", "tsʰ": "affricate", "tɕ": "affricate", "tɕʰ": "affricate",
    "tʂ": "affricate", "tʂʰ": "affricate", "tʃ": "affricate", "dʑ": "affricate",
    "f": "fric", "s": "fric", "ʂ": "fric", "ʐ": "fric", "ɕ": "fric", "x": "fric",
    "z": "fric", "ʒ": "fric", "h": "fric",
    "m": "nasal", "n": "nasal", "ŋ": "nasal", "ɲ": "nasal",
    "l": "liquid", "r": "liquid",
    "j": "glide", "w": "glide", "y": "glide",
    "i": "vowel", "u": "vowel", "y": "vowel", "a": "vowel", "o": "vowel",
    "e": "vowel", "ɤ": "vowel", "ɛ": "vowel", "ɨ": "vowel", "ɑ": "vowel",
    "ai": "vowel", "au": "vowel", "ei": "vowel", "ou": "vowel",
}


def sound_class(phone):
    return _CLASSES.get(phone, phone)


def _tokens(phones):
    """Phone string or list -> sound-class sequence (longest match first)."""
    if isinstance(phones, (list, tuple)):
        return [sound_class(p) for p in phones]
    out = []
    i = 0
    keys = sorted((k for k in _CLASSES if len(k) > 1), key=len, reverse=True)
    while i < len(phones):
        for k in keys:
            if phones.startswith(k, i):
                out.append(_CLASSES[k])
                i += len(k)
                break
        else:
            out.append(_CLASSES.get(phones[i], phones[i]))
            i += 1
    return out


def class_edit(a, b):
    """Class-weighted Levenshtein; inputs may be phone strings or phone lists.

    Substituting one sound class for another costs 0.6 while insertion and
    deletion cost 1.0, so a near-miss is punished less than a missing phone.
    """
    ta, tb = _tokens(a), _tokens(b)
    la, lb = len(ta), len(tb)
    if la == 0:
        return float(lb)
    if lb == 0:
        return float(la)
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        for j in range(1, lb + 1):
            sub = 0.0 if ta[i - 1] == tb[j - 1] else 0.6
            cur[j] = min(prev[j] + 1.0, cur[j - 1] + 1.0, prev[j - 1] + sub)
        prev = cur
    return float(prev[lb])
