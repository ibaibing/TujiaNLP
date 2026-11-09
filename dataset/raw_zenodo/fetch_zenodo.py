#!/usr/bin/env python3
"""Download the North Tujia corpus from Zenodo (record 4447924).

The files are not distributed with this repository. Running this script places
them in dataset/raw_zenodo/v2_4447924/ and verifies each file against the MD5
published by Zenodo.

Usage:
    python3 dataset/raw_zenodo/fetch_zenodo.py
"""
import hashlib
import json
import pathlib
import sys
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "v2_4447924"


def load_manifest():
    with open(HERE / "checksums.json", encoding="utf-8") as f:
        meta = json.load(f)
    return meta["record"], meta["files"]


def fetch(record, name, md5, size):
    dst = OUT / name
    if dst.exists() and dst.stat().st_size == size:
        print(f"[skip] {name} already present")
        return
    url = (
        f"https://zenodo.org/api/records/{record}/files/"
        + urllib.parse.quote(name)
        + "/content"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TujiaNLP-fetch/1.0"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = resp.read()
    except Exception as exc:  # noqa: BLE001
        sys.exit(
            f"[error] failed to download {name}: {exc}\n"
            f"        Open https://zenodo.org/records/{record} in a browser, "
            f"download manually into {OUT}/, then rerun this script."
        )
    got = hashlib.md5(data).hexdigest()
    if got != md5:
        sys.exit(f"[error] checksum mismatch for {name}: {got} != {md5}")
    OUT.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    print(f"[ok] {name} ({size} bytes)")


def main():
    record, files = load_manifest()
    for name, info in files.items():
        fetch(record, name, info["md5"], info["size"])


if __name__ == "__main__":
    main()
