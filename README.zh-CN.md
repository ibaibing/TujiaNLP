# TujiaNLP
利用AI技术抢救、保护濒危**北部土家语（龙山苗儿滩标准音）**
> 土家语目前仅高龄土家族母语者掌握，面临语言消亡风险。本开源公益项目旨在数字化留存语言资料，构建土家语AI语音、翻译与对话模型。

[English](README.md)

## 🎯 项目目标
1. 田野采集土家语音频，建立规范双语标注数据集；
2. 训练土家语ASR（语音识别）、TTS（语音合成）；
3. 实现土家语 ↔ 汉语机器翻译；
4. 搭建土家语对话AI（模块化流水线先行，远期开展LLM微调）；
5. 产出轻量化学习工具，用于土家语传承科普。

> ⚠️ 范围限定：**北部土家语（龙山/永顺/来凤片区）**，前期暂不纳入南部土家语，避免方言混杂干扰模型训练。

## 📜 书写标准
统一采用【叶德书-彭秀模1984土家语拼音方案】，不混用其他转写体系。
拼音互转由 `tujia_nlp` 包提供（`tools/orthography_convert.py` 是早期脚本，功能已并入前者）。

## 🌐 生态与分工

| 仓库 | 职责 |
| --- | --- |
| **TujiaNLP**（本仓） | 语料授权、采集规范、正字法、数据契约 |
| [tujia-asr](https://github.com/ibaibing/tujia-asr) | 声学模型发布：音节级 CTC |
| [tujia-tts](https://github.com/ibaibing/tujia-tts) | 语音合成发布 |
| [tujia-llm](https://github.com/ibaibing/tujia-llm) | LoRA 适配器与评测协议 |

数据流：

```
音频 ──► tujia-asr       声学模型，输出音节级结果

文本 ──► tujia_nlp       IPA ↔ Ye、四调记法 ──► TTS / LLM 数据与注音
```

边界原则：

- **本仓**管语言资源与契约：音节表、正字法规则、语料授权、词典条目与包清单 schema。
- **tujia-asr / tujia-tts / tujia-llm** 管模型发布。训练代码在私有的 `*-lib` / `*-lab`。

## 📦 安装与使用

```bash
pip install tujia-nlp
```

```python
from tujia_nlp import format_syllable, normalize_shape, to_ipa, to_ye

to_ye("la35")                    # "laf"
to_ye("kaŋ35")                   # "gangf"   旧记法输入同样接受
to_ipa("gangf")                  # "kã35"    输出统一为现行口径
format_syllable("la35", "ipa")   # "la³⁵"
normalize_shape("ʐuo")           # "zuo"
```

记法约定：

- 输出（`to_ipa`）一律是现行口径：鼻化元音 `ã ẽ ĩ ũ`、`z`、`iou`。
- 输入（`to_ye`）两套都接受：早期材料的 `aŋ eŋ iŋ oŋ`、`ʐ`、`iu` 会先折算再查表。
- `ɿ`、`ə` 这类 Ye 不区分的对立只能单向：`to_ye` 能转出 Ye，`to_ipa` 不能还原。

音节表覆盖北部土家语（龙山/永顺/来凤）291 个音节，其中 227 条有语料实证、64 条按规则推断。

除 IPA ↔ Ye 之外，还有四个子模块：

```python
from tujia_nlp import corpus, phone_norm, syllable, zh_sound

syllable.split_head("a⁵⁵ji²¹")     # [("a", 55), ("ji", 21)]
syllable.tone_stats(["la³⁵"])      # 每个音节的调值分布
phone_norm.canon("d")              # ["t"]  浊塞音并入清音类
zh_sound.pinyin_to_ipa("ni3")      # ("ni", 21)
corpus.to_ipa("xi2")               # [{"ipa": "ɕi", ...}]  语料罗马字
```

`corpus` 处理语料里那套拼写（`x-`=ɕ-、`hh-`=ɣ-、`an`=ã），与 `north.json` 的标准 Ye 表不同。

`zh_sound.text_to_syllables` 处理汉字需要可选依赖 `pypinyin`（`pip install "tujia-nlp[zh]"`），
纯拼音输入无需额外安装。

## 🛠️ 硬件与技术栈
- 开发设备：Mac Studio M2 Ultra 128GB，基于MLX实现本地离线训练/推理
- 语音模型：OpenAI Whisper、VITS、FishSpeech
- LLM底座：Qwen系列（原生适配MLX）
- 开发语言：Python 3.11+

## 📂 目录说明
```
src/tujia_nlp/     包本体：tones.py、ye.py、syllable.py、phone_norm.py、zh_sound.py
schema/            词典条目与包清单契约（JSON Schema）
tests/             单元测试（pytest）
docs/              采集规范、资源清单
tools/             早期转换脚本，功能已并入包
```

## 📚 公开Zenodo数据集说明
项目使用两套官方开源北部土家语文本语料，**不随仓库分发**，按下方 DOI 从 Zenodo 获取：
1. **V1 初代存档版（DOI：10.5281/zenodo.4446698）**
   素材残缺、拼音映射存在标注错误，仅用于学术溯源查阅，**禁止用于模型训练**；
2. **V2 扩充完整版（DOI：10.5281/zenodo.4447924）**
   本项目翻译/LLM/ASR/TTS唯一官方训练数据源，完整包含拼音对照表、词汇、课本短句、民间叙事、日常问候语。

原始数据由 Zenodo 记录 4446698 / 4447924 提供，上传者标注 `Other (Public Domain)`，该标注不是标准许可。本项目**不再分发原始文件**，只保留取数脚本、校验和与官方元数据。经 `tools/orthography_convert.py` 转换、清洗后的语料属于本项目新增工作（CC BY 4.0），原始词表仍归原权利人。

### 学术引用格式
#### V1 初代数据集
Zhou, Y., & Hill, N. W. (2021). A collection of North Tujia (Bifzivsar 北部土家语) vocabulary and textual passages for use in NLP (Version 1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.4446698
#### V2 完整版数据集
Zhou, Y., & Hill, N. W. (2021). A collection of North Tujia (Bifzivsar 北部土家语) vocabulary and textual passages for use in NLP (Version 2) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.4447924

完整数据集许可约束详见根目录 `DATASET_LICENSE.md`。

## 🤝 如何参与贡献
欢迎所有志愿者参与：
1. 土家族同胞：协助田野录音、语义校对、发音校验；
2. AI/NLP开发者：模型微调、代码优化、前端工具开发；
3. 语言学爱好者：扩充词汇、整理语法资料。

### ⚖️ 伦理规范
所有田野录音必须提前获取受访者**知情同意**，严格保护老人隐私，采集素材不可私自商用。

## 📦 开放核心词表

`data/packs/tujia-open-core/` 提供 **1,620 条可再分发的土家语核心词形**（346 个概念），格式为 `tujia.pack/v1`，Dart 端（`tujia-trans`）可直接读取，无需转换。

- **来源**：Zhou, Yulou (2020)《Proto-Bizic: A Study of Tujia Historical Phonology》，斯坦福大学本科论文
- **许可**：CC-BY-4.0（允许再分发、商业使用、修改，须署名）
- **数字化数据**：另发布于 <https://github.com/luggroo/bizic-dictionary>，经维护者许可复用

引用格式：

```
Zhou, Y. (2020). Proto-Bizic: A Study of Tujia Historical Phonology
[Bachelor thesis]. Stanford University.
```

## 📄 开源协议
- 程序源代码：**MIT License**（根目录 LICENSE 文件）
- 第三方原始语料：不再分发，版权归原权利人，详见 `DATASET_LICENSE.md`
- 本项目生成的数据（`data/inventory/` 音节表、`data/packs/tujia-open-core/` 核心词表）：**CC-BY 4.0**，须署名
- 田野原始音频：遵循每位受访者单独签署的知情同意约定

## 📌 项目进度清单
- [x] Github仓库初始化
- [ ] 完善《土家语数据采集与标注规范》
- [ ] 整理公开文献，搭建基础词汇库
- [ ] 启动田野录音采集
- [ ] Whisper增量微调 土家语ASR
- [ ] 训练土家语TTS语音合成
- [ ] 汉-土双语翻译模型
- [ ] 土家语语音对话Web Demo
- [ ] 土家语大模型SFT微调（长期目标）