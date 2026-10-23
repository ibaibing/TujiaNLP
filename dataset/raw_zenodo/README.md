# 第三方语料：来源与使用边界

本目录**不再随仓库分发**任何第三方语料。数据由使用者运行 `fetch_zenodo.py`
从 Zenodo 获取，或自行从记录页下载。

## 来源

| 版本 | Zenodo 记录 | DOI |
|---|---|---|
| V2（当前） | 4447924 | https://doi.org/10.5281/zenodo.4447924 |
| V1（旧版） | 4446698 | https://doi.org/10.5281/zenodo.4446698 |

V2 在 V1 基础上增加了 `Tujia Greetings.txt`，其余文件基本一致。

## 版权与许可

- Zenodo 记录由 Zhou & Hill (2021) 上传，许可字段标注为
  `Other (Public Domain)`。该标注**不是标准许可**（不是 CC0，也不是 CC BY）。
- 其中 `Brassett (2006) to Ye orthography.csv` 是 Brassett 土家语词表的
  数字化衍生。原始词表文件标注 `(C) 2004 Philip & Cecilia Brassett`，
  与上述公有领域声明冲突。
- 本仓库不因收录或提供下载脚本而授予任何许可；版权归原权利人。
- 如权利人提出异议，将立即移除相关脚本与说明。

## 使用

```bash
python3 dataset/raw_zenodo/fetch_zenodo.py
```

脚本会把文件写入 `dataset/raw_zenodo/v2_4447924/`，并按 Zenodo 公布的
MD5 校验。若网络被 Zenodo 拦截（返回 403），请用浏览器打开记录页手动下载。

## 引用

```bibtex
@misc{zhou_hill_2021_tujia,
  author    = {Zhou, Chu and Hill, Nathan W.},
  title     = {Tujia language dataset},
  year      = {2021},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.4447924}
}
```

词表本身请同时引用：

> Brassett, Cecilia, Philip Brassett & Meiyan Lu. 2006. *The Tujia Language*.
> (Languages of the World/Materials 455.) München: LINCOM.
