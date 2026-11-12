"""Closed syllable inventory: which syllables exist, and how to snap onto them.

The syllable table is a closed set. That is what makes it useful to models: a
recogniser, a synthesiser and a language model all produce *sequences*, and the
inventory is the one place that can say "this token is a Tujia syllable" or
"this token is off by one phone".

    from tujia_nlp import inventory

    inventory.is_legal("liã")          # True
    inventory.status("tɕʰiũ")          # "legal"
    inventory.nearest("tɕʰiøŋ")        # "tɕʰiũ"  (folded to the northern rhyme)
    inventory.normalize_text("tɕʰiøŋ²¹ ma⁵⁵")   # "tɕʰiũ²¹ ma⁵⁵"
    inventory.analyze("tɕʰiøŋ²¹ma⁵⁵")  # [Analysis(...), Analysis(...)]

Data comes from `data/syllabary.json`, a pinned snapshot. Point
`TUJIA_SYLLABARY` at a frozen `syllables-<version>.tsv` to use another table:

    export TUJIA_SYLLABARY=/path/to/syllables-0.6.3.tsv

Statuses:

    legal      two or more independent sources; the core set
    attested   one source; usable, but not the core

`nearest` and `normalize_text` only rewrite a token when the distance is within
`max_cost` (default 2). Anything further away is left alone and reported as
unknown by `analyze`, because guessing at that distance invents words.
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from pathlib import Path

_DATA = Path(__file__).parent / "data" / "syllabary.json"
ENV = "TUJIA_SYLLABARY"
SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_TONE_CHARS = set(SUP) | set("0123456789")
_SUPPORT_ORDER = {"3+": 0, "2": 1, "1": 2}
LEGAL = "legal"
ATTESTED = "attested"

# Spelling conventions that are not contrasts. `h` after an obstruent marks
# aspiration (`khe` = `kʰe`), and the digraph letters below are one phone
# written two ways. `h` itself, `ɣ`, `ʂ` and `ʐ` are deliberately absent: the
# inventory keeps those as separate symbols.
_ASPIRATION = [("tsh", "tsʰ"), ("tʂh", "tʂʰ"), ("tɕh", "tɕʰ"), ("tʃh", "tʃʰ"),
               ("ph", "pʰ"), ("th", "tʰ"), ("kh", "kʰ")]
_SYMBOL = {
    "ʦ": "ts", "ʣ": "dz", "ʨ": "tɕ", "ʥ": "dʑ", "ʧ": "tʃ", "ʤ": "dʒ",
    "ɿ": "ɨ", "ʅ": "ɨ", "ʮ": "ɨ", "ʯ": "ɨ",
    "ɔ": "o", "ə": "ɤ", "ɪ": "i", "ɘ": "ɤ", "ɜ": "ɤ", "ʌ": "ɤ", "ʊ": "u",
    "ɵ": "o", "ɶ": "a", "ɲ": "n", "ɳ": "n", "ɴ": "ŋ", "ɱ": "m", "ȵ": "n",
    "ç": "ɕ", "ʝ": "j", "ʒ": "z",
    "β": "w", "ʋ": "w", "v": "w", "ɸ": "f", "θ": "s", "ð": "z",
    "ɹ": "l", "ɻ": "l", "ɽ": "l", "ɾ": "l", "r": "l", "ʀ": "l", "ʁ": "l",
    "ɬ": "l", "ɮ": "l", "ɭ": "l", "ʟ": "l", "ʎ": "l",
    "ʈ": "t", "ɖ": "t", "ȶ": "t", "ɟ": "k", "ɢ": "k", "ʏ": "y", "ɯ": "u",
}


@dataclass(frozen=True)
class Syllable:
    """One row of the inventory."""

    shape: str
    onset: str
    rhyme: str
    status: str
    support: str

    @property
    def is_legal(self) -> bool:
        return self.status == LEGAL


@dataclass(frozen=True)
class Analysis:
    """One toned syllable of an input string, and what the inventory makes of it."""

    raw: str
    shape: str
    tone: str
    status: str | None
    replacement: str | None

    @property
    def ok(self) -> bool:
        """Known to the inventory (legal or attested), no rewriting needed."""
        return self.status is not None

    @property
    def fixed(self) -> str:
        """The syllable to emit: itself when known, else the nearest known one."""
        return self.replacement or self.shape


def _fix_spelling(shape: str) -> str:
    """Undo notation, not contrast: `khe` -> `kʰe`, `ʦa` -> `tsa`, `ȵi` -> `ni`."""
    s = shape
    for a, b in _ASPIRATION:
        if s.startswith(a):
            s = b + s[len(a):]
            break
    return "".join(_SYMBOL.get(ch, ch) for ch in s)


def _lev(a: str, b: str) -> int:
    """Plain Levenshtein distance over code points."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _split_syllables(text: str) -> list[tuple[str, str]]:
    """Split a toned string into ``(shape, tone)`` at each tone run."""
    out: list[tuple[str, str]] = []
    shape, tone = "", ""
    for ch in text or "":
        if ch.isspace() or ch in "-·":
            continue
        if ch in _TONE_CHARS:
            tone += ch
        else:
            if tone and shape:
                out.append((shape, tone))
                shape, tone = "", ""
            shape += ch
    if shape:
        out.append((shape, tone))
    return out


class Inventory:
    """A frozen syllable table with lookup and snapping."""

    def __init__(self, version: str, syllables: list[Syllable], folds: dict[str, str],
                 onset_folds: dict[str, str] | None = None):
        self.version = version
        self.syllables = {s.shape: s for s in syllables}
        self.onsets = sorted({s.onset for s in syllables if s.onset}, key=len, reverse=True)
        self.folds = dict(folds or {})
        self.onset_folds = dict(onset_folds or {})
        self._cache: dict[tuple[str, int, bool], str | None] = {}

    def __len__(self) -> int:
        return len(self.syllables)

    def __contains__(self, shape: object) -> bool:
        return isinstance(shape, str) and self.canonical(shape) in self.syllables

    def __iter__(self):
        return iter(self.syllables.values())

    def canonical(self, shape: str) -> str:
        """Spelling fix plus rhyme fold: the form this inventory is keyed on."""
        return self.fold(_fix_spelling(shape))

    def get(self, shape: str) -> Syllable | None:
        return self.syllables.get(self.canonical(shape))

    def is_legal(self, shape: str) -> bool:
        s = self.get(shape)
        return bool(s and s.status == LEGAL)

    def status(self, shape: str) -> str | None:
        s = self.get(shape)
        return s.status if s else None

    def support(self, shape: str) -> str | None:
        s = self.get(shape)
        return s.support if s else None

    def split(self, shape: str) -> tuple[str, str]:
        """Longest onset the inventory knows, plus the rest."""
        for onset in self.onsets:
            if shape.startswith(onset) and len(shape) > len(onset):
                return onset, shape[len(onset):]
        return "", shape

    def fold(self, shape: str) -> str:
        """Apply the inventory's folds: onset first, then rhyme.

        `ʐi` -> `zi`, `pian` -> `piã`, `ʔa` -> `a`. When the onset is not in
        the table at all (it was folded out during the build), the longest
        `onset_folds` key is matched at the front instead. Values come from
        the table's manifest, not from code.
        """
        s = shape[1:] if shape.startswith("ʔ") else shape
        onset, rhyme = self.split(s)
        if onset:
            onset = self.onset_folds.get(onset, onset)
        else:
            for key in sorted(self.onset_folds, key=len, reverse=True):
                if key and s.startswith(key):
                    onset, rhyme = self.onset_folds[key], s[len(key):]
                    break
        return onset + self.folds.get(rhyme, rhyme)

    def nearest(self, shape: str, max_cost: int = 2, legal_only: bool = False) -> str | None:
        """Closest syllable in the inventory, or ``None`` if too far away."""
        probe = self.canonical(shape)
        key = (probe, max_cost, legal_only)
        if key in self._cache:
            return self._cache[key]

        s = self.syllables.get(probe)
        if s and (not legal_only or s.status == LEGAL):
            self._cache[key] = probe
            return probe

        best: tuple[tuple, str] | None = None
        for cand in self.syllables.values():
            if legal_only and cand.status != LEGAL:
                continue
            d = _lev(probe, cand.shape)
            if d > max_cost:
                continue
            rank = (d, 0 if cand.status == LEGAL else 1,
                    _SUPPORT_ORDER.get(cand.support, 9), cand.shape)
            if best is None or rank < best[0]:
                best = (rank, cand.shape)

        out = best[1] if best else None
        self._cache[key] = out
        return out

    def analyze(self, text: str, max_cost: int = 2, legal_only: bool = False) -> list[Analysis]:
        """Per-syllable verdict for a toned string."""
        out = []
        for raw, tone in _split_syllables(text):
            shape = self.canonical(raw)
            s = self.syllables.get(shape)
            rep = None if s else self.nearest(shape, max_cost=max_cost, legal_only=legal_only)
            out.append(Analysis(raw=raw, shape=shape, tone=tone,
                                status=s.status if s else None, replacement=rep))
        return out

    def normalize_text(self, text: str, max_cost: int = 2, legal_only: bool = False) -> str:
        """Rewrite unknown syllables to their nearest known form, keeping tones.

        The result is space-separated. Syllables already in the inventory are
        passed through unchanged; those too far from anything are kept as-is so
        that a caller can see what was rejected (`analyze` reports them).
        """
        return " ".join(
            a.fixed + a.tone for a in self.analyze(text, max_cost=max_cost, legal_only=legal_only)
        )


def _from_json(path: Path) -> Inventory:
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = [Syllable(*r) for r in d["syllables"]]
    return Inventory(d.get("version", "unknown"), rows,
                     d.get("folds") or {}, d.get("onset_folds") or {})


def _from_tsv(path: Path) -> Inventory:
    """Read a frozen table (TujiaNLP `data/inventory/` layout)."""
    version = path.stem.replace("syllables-", "")
    folds: dict[str, str] = {}
    onset_folds: dict[str, str] = {}
    meta = path.parent / "manifest.json"
    if meta.exists():
        m = json.loads(meta.read_text(encoding="utf-8"))
        folds = m.get("folds") or {}
        onset_folds = m.get("onset_folds") or {}
    rows = []
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            rows.append(Syllable(r["syllable"], r["onset"], r["rhyme"], r["status"], r["n_books"]))
    return Inventory(version, rows, folds, onset_folds)


def load(path: str | os.PathLike | None = None) -> Inventory:
    """Load an inventory. Defaults to the pinned snapshot or `TUJIA_SYLLABARY`."""
    target = Path(path or os.environ.get(ENV) or _DATA)
    if not target.exists():
        raise FileNotFoundError(f"syllable inventory not found: {target}")
    return _from_tsv(target) if target.suffix == ".tsv" else _from_json(target)


_DEFAULT: Inventory | None = None


def default() -> Inventory:
    """The process-wide inventory, loaded once."""
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = load()
    return _DEFAULT


def is_legal(shape: str) -> bool:
    return default().is_legal(shape)


def status(shape: str) -> str | None:
    return default().status(shape)


def nearest(shape: str, max_cost: int = 2, legal_only: bool = False) -> str | None:
    return default().nearest(shape, max_cost=max_cost, legal_only=legal_only)


def analyze(text: str, max_cost: int = 2, legal_only: bool = False) -> list[Analysis]:
    return default().analyze(text, max_cost=max_cost, legal_only=legal_only)


def normalize_text(text: str, max_cost: int = 2, legal_only: bool = False) -> str:
    return default().normalize_text(text, max_cost=max_cost, legal_only=legal_only)
