# Coze 知识库超大文件备份（分片存储）

本分支 `bigfiles` 专门存放因超过 GitHub 100MB 单文件限制、无法普通提交的超大文件。
所有大文件已被切成 **80MB 分片**，按原目录结构存放在 `<原相对路径>.parts/` 目录下，
每个分片目录含 `manifest.json`（记录原文件大小、sha256、分片清单与各分片 sha256）。

## 目录结构
```
Coze知识库批量上传项目/项目主目录/
├── extracted_0628/conversations.json.parts/
│   ├── manifest.json
│   ├── part000
│   ├── part001
│   └── ...
├── 完整知识库_终极完整版.md.parts/
└── ...
split.py          切片脚本
merge_restore.py  合并恢复脚本（带 sha256 校验）
```

## 恢复方法
克隆仓库并切到 bigfiles 分支后，对每个 `.parts` 目录运行：
```bash
python merge_restore.py "<路径>.parts" [输出目录]
```
脚本会按顺序拼接分片，并校验每个分片与原文件的 sha256，确保完整无误。

## 已备份文件清单（共 9 个，合计约 5.64 GB）
| 原相对路径 | 大小 | 分片数 |
|---|---|---|
| extracted_0628/conversations.json | 300.1 MB | 4 |
| 完整知识库_最终版/knowledge_base/FINAL_RAG_KNOWLEDGE_BASE_COMPLETE.json | 200.7 MB | 3 |
| 完整知识库_最终版/knowledge_base/FINAL_KNOWLEDGE_BASE_COMPLETE.json | 197.9 MB | 3 |
| 完整知识库_最终版/data/raw/conversations1.json | 165.7 MB | 3 |
| 完整知识库_最终版/data/raw/merged_conversations.json | 128.0 MB | 2 |
| 完整知识库_最终版/data/processed/其他.json | 122.0 MB | 2 |
| DGHGH_整理合并版/05_DeepSeek对话数据/conversations.json | 107.3 MB | 2 |
| 完整知识库_终极完整版.md | 3150.8 MB | 40 |
| 完整知识库_深度去重版.md | 1402.9 MB | 18 |
