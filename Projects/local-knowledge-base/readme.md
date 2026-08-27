# 最强本地知识库系统

✅ 完全离线 - 隐私数据不出本地
✅ 中文优化 - DeepSeek模型中文理解超强
✅ 零成本 - 全部开源免费

## 功能特性

- **解决数据孤岛问题**：统一管理多种格式的文档（PDF、Word、Markdown、文本等）
- **提升检索效率**：使用FAISS向量数据库，实现快速相似度搜索
- **解决知识更新滞后**：支持增量更新知识库，无需重新构建
- **完全离线运行**：所有数据和模型都存储在本地，保护隐私
- **中文优化**：使用DeepSeek中文嵌入模型，理解中文更准确
- **零成本**：全部使用开源免费工具和模型

## 系统架构

```
├── main.py              # 主命令行接口
├── requirements.txt     # 依赖包
├── src/                 # 核心模块
│   ├── embedding.py     # 嵌入模型（DeepSeek）
│   ├── document_processor.py  # 文档处理器
│   ├── retriever.py     # 向量检索器（FAISS）
│   └── knowledge_base.py      # 知识库管理
└── data/                # 数据存储
    ├── models/          # 模型缓存
    └── knowledge_bases/ # 知识库数据
```

## 安装说明

### 1. 安装Python

确保系统已安装Python 3.8+，可从[Python官网](https://www.python.org/)下载安装。

### 2. 安装依赖

```bash
# 进入项目目录
cd D:\local-knowledge-base

# 安装依赖
python -m pip install -r requirements.txt
```

### 3. 下载DeepSeek嵌入模型

首次运行时，系统会自动下载DeepSeek中文嵌入模型到本地。

## 使用方法

### 1. 构建知识库

```bash
# 构建知识库，指定文档目录和知识库名称
python main.py build -d "D:\documents" -n "my_knowledge_base"
```

### 2. 查询知识库

```bash
# 查询知识库
python main.py query -n "my_knowledge_base" -q "你的问题"
```

### 3. 更新知识库

```bash
# 更新知识库，添加新文档
python main.py update -n "my_knowledge_base" -d "D:\new_documents"
```

### 4. 列出所有知识库

```bash
# 列出所有知识库
python main.py list-kbs
```

## 支持的文档格式

- PDF (.pdf)
- Word (.docx)
- Markdown (.md)
- 文本文件 (.txt, .log, .csv)

## 性能优化

1. **文档分块**：默认分块大小为512字符，可根据需要调整
2. **批量处理**：支持批量文档处理，提高效率
3. **FAISS索引**：使用FAISS进行向量检索，速度快
4. **缓存机制**：模型和索引会缓存到本地，加速后续操作

## 注意事项

1. **首次运行**：首次运行时会下载DeepSeek嵌入模型，需要联网
2. **内存要求**：处理大量文档时，建议系统内存至少8GB
3. **CPU使用**：默认在CPU上运行，无需GPU
4. **数据安全**：所有数据都存储在本地，不会上传到任何服务器

## 示例

### 构建知识库

```bash
python main.py build -d "D:\我的文档" -n "个人知识库"
```

### 查询知识库

```bash
python main.py query -n "个人知识库" -q "如何使用Python进行数据分析"
```

### 更新知识库

```bash
python main.py update -n "个人知识库" -d "D:\新文档"
```

## 故障排除

- **模型下载失败**：检查网络连接，确保可以访问Hugging Face
- **文档加载失败**：确保文档格式正确，权限足够
- **内存不足**：减少一次性处理的文档数量
- **查询速度慢**：考虑增加FAISS索引的优化参数

## 许可证

本项目使用MIT许可证，完全开源免费。
