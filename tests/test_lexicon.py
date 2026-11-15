import json

from tujia_nlp import lexicon
from tujia_nlp.lexicon import pack_entries, pack_lexicon_path, pack_manifest


def test_default_pack_is_packaged():
    manifest = pack_manifest()
    assert manifest["id"] == lexicon.DEFAULT_PACK
    assert manifest["license"] == "CC-BY-4.0"
    assert manifest["files"]["lexicon"] == "lexicon.jsonl"


def test_entries_and_variety_filter():
    rows = pack_entries()
    assert len(rows) == pack_manifest()["entries"]
    assert all(r["w"] for r in rows)

    north = pack_entries(variety="north")
    south = pack_entries(variety="south")
    assert north and south
    assert len(north) + len(south) == len(rows)
    assert all("北部" in r["variety"] for r in north)


def test_lexicon_path_is_readable_jsonl():
    with open(pack_lexicon_path(), encoding="utf-8") as f:
        first = json.loads(f.readline())
    assert "w" in first
