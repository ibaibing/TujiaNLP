"""Open vocabulary packs shipped with the package.

The packs live under ``data/packs/<id>/`` and follow ``tujia.pack/v1``
(``manifest.json`` + ``lexicon.jsonl``). They are core vocabularies, not
complete dictionaries; every pack carries its own licence and attribution in
``NOTICE.md`` and must be redistributed with it.

    from tujia_nlp.lexicon import pack_entries

    rows = pack_entries("tujia-open-core", variety="north")

``variety`` filters on the ``variety`` field, which mixes Chinese
(``北部土家语（仙仁）``) and English (``northern``) labels. Entries without a
variety are kept, since user-supplied lexicons never carry one.
"""

import json
import os
from importlib import resources

DEFAULT_PACK = "tujia-open-core"

_VARIETY_WORDS = {
    "north": ("北部", "north"),
    "south": ("南部", "south"),
}


def pack_dir(name=DEFAULT_PACK):
    """Filesystem path to a pack directory inside the installed package."""
    return resources.files(__package__).joinpath("data", "packs", name)


def pack_manifest(name=DEFAULT_PACK):
    path = pack_dir(name).joinpath("manifest.json")
    return json.loads(path.read_text(encoding="utf-8"))


def pack_entries(name=DEFAULT_PACK, variety=None):
    """Load a pack's lexicon as a list of rows.

    ``variety`` may be ``"north"`` / ``"south"`` (matched against the
    ``variety`` field) or ``None`` for every row.
    """
    path = pack_dir(name).joinpath("lexicon.jsonl")
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not row.get("w"):
                continue
            if variety is not None:
                words = _VARIETY_WORDS.get(variety, (variety,))
                label = str(row.get("variety", ""))
                if label and not any(w in label.lower() if w.isascii() else w in label
                                     for w in words):
                    continue
            rows.append(row)
    return rows


def pack_lexicon_path(name=DEFAULT_PACK):
    """Path to ``lexicon.jsonl``, for tools that take a file path."""
    return os.fspath(pack_dir(name).joinpath("lexicon.jsonl"))
