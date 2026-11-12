# 变更日志

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循
[语义化版本](https://semver.org/lang/zh-CN/)。

## [0.3.0] - 未发布

### 新增

- **音节表模块 `tujia_nlp.inventory`**：封闭音节表（0.6.3，1,347 行）的读取、
  归一与查询；支持 `TUJIA_SYLLABARY` 覆盖内置快照。
- **语料音系模块 `tujia_nlp.corpus`**：Ye 声母/韵母表与声调标记的正反向映射，
  供 ASR/TTS/翻译前端共用。
- **数据层 `data/`**：
  - `data/inventory/`：`syllables-0.6.2.tsv`、`syllables-0.6.3.tsv`、`manifest.json`；
  - `data/packs/tujia-open-core/`：1,620 条可再分发的核心词形（346 概念），
    `tujia.pack/v1` 格式，CC-BY-4.0；
  - `data/schema/`：音节表与包索引契约；
  - `data/index.json`、`data/manifest.example.json`。
- **数据工具 `tools/lexicon/`**：`validate.py`（契约校验）、`package.py`（打
  `.tjpack` 与索引）、`build_open_core.py`（重建核心词表）。
- **文档**：`docs/lexicon.md`（数据层说明）、README 的 “Lexicon data” 与
  “开放核心词表” 章节、`Attribution` 署名段。

### 变更

- `__init__.py` 版本号升至 `0.3.0`，导出 `corpus` 与 `inventory`。
- `ye.py` 补全 IPA↔Ye 的边界处理与声调规则。
- `MANIFEST.in` 增加 `recursive-include data *`，sdist 携带数据层。
- `DATASET_LICENSE.md` 明确：原始语料不分发；`data/inventory/` 与
  `data/packs/tujia-open-core/` 按 CC-BY-4.0 分发并须署名。
- 中英 README 的许可段改为三分：代码 MIT / 原始语料不分发 / 本项目数据 CC-BY-4.0。

### 移除

- `dataset/raw_zenodo/`：原始语料副本、取数脚本与校验和。数据获取方式保留在
  README 的 Zenodo DOI 与引用格式中。

### 修复

- 音节表导出统一使用 LF 行尾。此前 csv 默认 `\r\n` 导致 `manifest.json` 的
  sha256 与实际文件长期不一致，`validate.py` 反复报错。
- 清理指向已删除仓库 `tujia-lexicon` 的死引用（含两个 schema 的 `$id`）。

### 验证

- `python3 tools/lexicon/validate.py data/inventory`：OK，1,347 音节，
  sha256 `d02e78ea…`。
- `pytest`：79 passed。
- 构建产物：`tujia_nlp-0.3.0-py3-none-any.whl`（36 KB）、
  `tujia_nlp-0.3.0.tar.gz`（96 KB）、`tujia-open-core-0.1.0.tjpack`（31 KB）、
  `tujia-inventory-0.6.3.tar.gz`（20 KB）。
- 脱敏：本地路径、私有库名、页码、未授权字样均为 0；sdist 45 个文件复扫无命中。

### 兼容性

- `tujia-asr` 的 `postprocess` 依赖 `tujia_nlp.inventory`（0.3.0 新增），
  其依赖下限应从 `tujia-nlp>=0.2.0` 调整为 `>=0.3.0`。

## [0.2.0] - 2026-11-09

### 新增

- `tujia_nlp` 正字法包：IPA↔Ye、声调记法、音素归一。
- 词典条目与包清单的 JSON Schema。
- Zenodo 数据集的引用与获取说明。

### 说明

- 本版不含音节表与数据包；数据层自 0.3.0 起随源码树分发。
