# Third-party corpus: source and scope

No third-party corpus is distributed with this repository. Run `fetch_zenodo.py` to
download it from Zenodo, or download it from the record page manually.

## Source

| Version | Zenodo record | DOI |
|---|---|---|
| V2 (current) | 4447924 | https://doi.org/10.5281/zenodo.4447924 |
| V1 (older) | 4446698 | https://doi.org/10.5281/zenodo.4446698 |

V2 adds `Tujia Greetings.txt` on top of V1; the remaining files are essentially the same.

## Usage

```bash
python3 dataset/raw_zenodo/fetch_zenodo.py
```

The script writes the files to `dataset/raw_zenodo/v2_4447924/` and verifies each one
against the MD5 published by the record. If the network is blocked (HTTP 403), open the
record page in a browser and download manually.

The third-party corpus is not distributed here, and providing a fetch script grants no
licence. Use of the files is governed by the terms of the original publisher.
