#!/usr/bin/env python3
"""从 Zenodo 下载土家语语料（记录 4447924）。

本仓库不再分发这些文件。运行本脚本后，数据会落在
dataset/raw_zenodo/v2_4447924/，并逐个校验 Zenodo 公布的 MD5。

用法:
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
        print(f"[skip] {name} 已存在")
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
            f"[error] 下载 {name} 失败：{exc}\n"
            f"        请用浏览器打开 https://zenodo.org/records/{record} 手动下载，"
            f"并放入 {OUT}/ 后重跑本脚本。"
        )
    got = hashlib.md5(data).hexdigest()
    if got != md5:
        sys.exit(f"[error] {name} 校验失败：{got} != {md5}")
    OUT.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    print(f"[ok] {name} ({size} bytes)")


def main():
    record, files = load_manifest()
    for name, info in files.items():
        fetch(record, name, info["md5"], info["size"])


if __name__ == "__main__":
    main()
