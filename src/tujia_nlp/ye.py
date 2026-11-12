"""IPA <-> Ye (Yedshu 1984) syllable conversion for Tujia.

Public entry points::

    to_ye("la35")              -> "laf"
    to_ye("la³⁵")              -> "laf"
    to_ipa("laf")              -> "la35"
    format_syllable("la35", "ye") -> "laf"

North (Longshan/Yongshun/Laifeng) is the only dialect shipped as of 0.1.0;
``dialect="south"`` raises until a south table is added.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from . import tones

_DATA_DIR = Path(__file__).parent / "data"
_SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_TONE_AT_END = re.compile(rf"^(.*?)([0-9]{{2}}|[{_SUP}]{{2}})$")
# Corpora also write the tone as a single category digit: la1 / la2 / la3 / la4.
_TONE_DIGIT_AT_END = re.compile(r"^(.*?)([1-4])$")
_TONE_DIGIT_TO_CHAO = {"1": "55", "2": "35", "3": "21", "4": "53"}

# Legacy spelling -> current IPA convention.
# Northern Tujia materials use two spellings for the same sounds: earlier sources
# write a -ŋ coda, ʐ and iu, while the current standard writes nasalised vowels,
# z and iou. Lookups and outputs use the current form; input accepts either.
# Order matters: longer sequences must be replaced first (ioŋ before oŋ).
_LEGACY_TO_NEW = (
    ("ioŋ", "iũ"),
    ("oŋ", "ũ"),
    ("uŋ", "ũ"),
    ("aŋ", "ã"),
    ("eŋ", "ẽ"),
    ("iŋ", "ĩ"),
    ("ʐ", "z"),
    ("ȵ", "ɲ"),
    ("iu", "iou"),
)
_NEW_TO_LEGACY = tuple((new, old) for old, new in reversed(_LEGACY_TO_NEW))

# The Ye scheme does not distinguish the pairs below, so lookups fall back to the
# common spelling. This only affects to_ye: these inputs produce Ye, but to_ipa
# cannot recover them, because the distinction is lost in the Ye layer.
#   ɿ / i   apical vowel in Chinese loans; Ye writes i (as in pinyin zi/ci/si)
#   ə / ɤ   both written e in Ye
_LOOKUP_ALIASES = (
    ("pʰɿ", "pʰi"),
    ("sɿ", "si"),
    ("tsʰɿ", "tsʰi"),
    ("pɿ", "pi"),
    ("ə", "ɤ"),
)

# A second romanisation appears in the text corpora: x- stands for ɕ- and hh-
# for ɣ-. The standard Ye table writes ɕ without an initial letter (ɕi -> "i")
# and ɣ as hx (ɣi -> "hxi"), so those spellings are not table keys. They are
# accepted on input only; to_ye still emits the standard spelling.
_CORPUS_SHAPE_ALIASES = {
    "xi": "ɕi",
    "xia": "ɕia",
    "xiao": "ɕiau",
    "xie": "ɕiɛ",
    "xiu": "ɕiu",
    "xian": "ɕiã",
    "xing": "ɕiŋ",
    "xiong": "ɕiøŋ",
    "hhi": "ɣi",
    "hhe": "ɣɤ",
}

# Single-digit tones used by the corpora (and by pinyin) mapped to Chao values.
_DIGIT_TONE = _TONE_DIGIT_TO_CHAO


def normalize_shape(shape: str) -> str:
    """Legacy syllable shape -> modern IPA. ``"kaŋ"`` -> ``"kã"``, ``"ʐu"`` -> ``"zu"``."""
    s = shape or ""
    for a, b in _LEGACY_TO_NEW:
        s = s.replace(a, b)
    return s


def _to_legacy(shape: str) -> str:
    """Modern -> legacy shape, used only as a lookup fallback."""
    s = shape or ""
    for a, b in _NEW_TO_LEGACY:
        s = s.replace(a, b)
    return s


def _lookup(table: dict, shape: str):
    entry = table.get(shape)
    return entry.get("ye") if entry else None



@lru_cache(maxsize=None)
def _load(dialect: str) -> dict:
    path = _DATA_DIR / f"{dialect}.json"
    if not path.exists():
        available = sorted(p.stem for p in _DATA_DIR.glob("*.json"))
        raise ValueError(
            f"no syllable table for dialect {dialect!r}; available: {available}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _reverse(dialect: str) -> dict[str, str]:
    """Ye spelling -> IPA shape. Ambiguous spellings prefer a zero initial."""
    table = _load(dialect)["syllables"]
    out: dict[str, str] = {}
    for shape, entry in table.items():
        ye = entry["ye"]
        current = out.get(ye)
        if current is None:
            out[ye] = shape
            continue
        # Two IPA shapes share one Ye spelling (e.g. iɛ / ɕiɛ -> "ie").
        # Prefer the form without an initial consonant, which is what a reader
        # of the Ye spelling would assume.
        if _has_initial(current) and not _has_initial(shape):
            out[ye] = shape
    return out


def _has_initial(shape: str) -> bool:
    return bool(shape) and shape[0] not in "aeiouɤɛœəɐɑɒæ"


def split_tone(label: str) -> tuple[str, str]:
    """``"la35"`` / ``"la³⁵"`` / ``"la2"`` -> ``("la", "35")``; no tone -> ``(label, "")``."""
    text = label.strip()
    match = _TONE_AT_END.match(text)
    if match:
        return match.group(1), tones.normalize(match.group(2))
    category = _TONE_DIGIT_AT_END.match(text)
    if category:
        return category.group(1), _TONE_DIGIT_TO_CHAO[category.group(2)]
    return text, ""


def to_ye(label: str, dialect: str = "north") -> str:
    """IPA label to Ye spelling. Falls back to superscript IPA when unmapped.

    Both spellings are accepted: ``"kaŋ35"`` and ``"kã35"`` hit the same Ye entry.
    The table is queried as stored; the other spelling is converted first.
    """
    shape, tone = split_tone(label)
    table = _load(dialect)["syllables"]
    ye = _lookup(table, shape)
    if ye is None:
        for alt in (normalize_shape(shape), _to_legacy(shape)):
            if alt != shape:
                ye = _lookup(table, alt)
                if ye is not None:
                    break
    if ye is None:
        for a, b in _LOOKUP_ALIASES:
            if a in shape:
                ye = _lookup(table, shape.replace(a, b))
                if ye is not None:
                    break
    if ye is None:
        return shape + tones.to_superscript(tone) if tone else shape
    if not tone:
        return ye
    return ye + tones.to_letter(tone)


def _split_ye(label: str) -> tuple[str, str]:
    """Ye token -> ``(spelling, Chao digits)``.

    Accepts the three tone notations used by the corpora: letter (``f``), single
    digit (``2``) and none. Two-digit or superscript Chao tones are handled by
    :func:`split_tone` on the IPA side only.
    """
    token = label.strip()
    if len(token) > 1:
        last = token[-1]
        if last in tones.LETTER_TO_CHAO:
            return token[:-1], tones.LETTER_TO_CHAO[last]
        if last in _DIGIT_TONE:
            return token[:-1], _DIGIT_TONE[last]
    return token, ""


def to_ipa(label: str, dialect: str = "north") -> str:
    """Ye spelling to IPA label with Chao digits. Returns ``"laf"`` -> ``"la35"``.

    Output is always the modern IPA convention (nasalised vowels, z, iou), even
    when the table entry was recorded in the legacy form (``aŋ`` / ``ʐ`` / ``iu``).
    Tone letters, single tone digits and plain spellings are all accepted, as are
    the corpus spellings ``x-`` (ɕ-) and ``hh-`` (ɣ-).
    """
    if not label.strip():
        return label
    table = _reverse(dialect)
    base, tone = _split_ye(label)
    shape = table.get(base) or _CORPUS_SHAPE_ALIASES.get(base)
    if shape is None:
        raise ValueError(f"cannot convert Ye syllable {label!r} for dialect {dialect!r}")
    return normalize_shape(shape) + tone


def format_syllable(label: str, fmt: str = "ascii", dialect: str = "north") -> str:
    """Render one IPA label in the requested notation.

    ``ascii`` -> ``la35``, ``ipa`` -> ``la³⁵``, ``ye`` -> ``laf``.
    """
    if fmt == "ascii":
        shape, tone = split_tone(label)
        return shape + tone
    if fmt == "ipa":
        shape, tone = split_tone(label)
        return shape + tones.to_superscript(tone) if tone else shape
    if fmt == "ye":
        return to_ye(label, dialect=dialect)
    raise ValueError(f"unknown format {fmt!r}; expected 'ascii', 'ipa' or 'ye'")


def available_dialects() -> list[str]:
    return sorted(p.stem for p in _DATA_DIR.glob("*.json"))
