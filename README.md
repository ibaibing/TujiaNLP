# TujiaNLP
利用AI技术抢救、保护濒危**北部土家语（龙山苗儿滩标准音）**
> 土家语目前仅高龄土家族母语者掌握，面临语言消亡风险。本开源公益项目旨在数字化留存语言资料，构建土家语AI语音、翻译与对话模型。

## 🎯 项目目标
1. 田野采集土家语音频，建立规范双语标注数据集；
2. 训练土家语ASR（语音识别）、TTS（语音合成）；
3. 实现土家语 ↔ 汉语机器翻译；
4. 搭建土家语对话AI（模块化流水线先行，远期开展LLM微调）；
5. 产出轻量化学习工具，用于土家语传承科普。

> ⚠️ 范围限定：**北部土家语（龙山/永顺/来凤片区）**，前期暂不纳入南部土家语，避免方言混杂干扰模型训练。

## 📜 书写标准
统一采用【叶德书-彭秀模1984土家语拼音方案】，禁止混用海外Brassett拼音。
两套拼音互转工具存放于 `tools/orthography_convert.py`。

## 🛠️ 硬件与技术栈
- 开发设备：Mac Studio M2 Ultra 128GB，基于MLX实现本地离线训练/推理
- 语音模型：OpenAI Whisper、VITS、FishSpeech
- LLM底座：Qwen系列（原生适配MLX）
- 开发语言：Python 3.11+

## 📂 目录说明
docs/ 规范文档、学术资料、田野采集模板
tools/ 数据集处理、录音工具、拼音转换脚本
dataset/ 双语词汇、短句文本（原始音频不存入 Git 版本库）
speech/ ASR 语音识别、TTS 语音合成训练代码
translation/ 汉土双语翻译模型
llm/ 对话流水线脚本、LLM 微调实验代码
demo_web/ 静态网页演示程序（词典、翻译、发音工具）

## 📚 公开Zenodo数据集说明
项目归档两套官方开源北部土家语文本语料，原始文件存放路径：`dataset/raw_zenodo/`
1. **V1 初代存档版（DOI：10.5281/zenodo.4446698）**
   素材残缺、拼音映射存在标注错误，仅用于学术溯源查阅，**禁止用于模型训练**；
2. **V2 扩充完整版（DOI：10.5281/zenodo.4447924）**
   本项目翻译/LLM/ASR/TTS唯一官方训练数据源，完整包含拼音对照表、词汇、课本短句、民间叙事、日常问候语。

原始数据由 Zenodo 记录 4446698 / 4447924 提供，上传者标注 `Other (Public Domain)`；该标注不是标准许可，且底层词表版权归 Brassett 等原作者。本项目不再分发原始文件，仅提供取数脚本。经 `tools/orthography_convert.py` 转换、清洗后的标准化语料存放于 `dataset/processed/`，其许可仅覆盖本项目新增的转换与标注工作。

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

## 📄 开源协议
- 程序源代码：**MIT License**（根目录 LICENSE 文件）
- 第三方原始语料：版权归原权利人，本项目不授予许可、不再分发，详见 `dataset/raw_zenodo/README.md`
- 项目自行生成的标准化数据与标注：**CC-BY 4.0**（不含原始词表全文）
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