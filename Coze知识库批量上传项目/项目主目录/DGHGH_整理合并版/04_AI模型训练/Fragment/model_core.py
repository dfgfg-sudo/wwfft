"""
# -*- coding: utf-8 -*-
\"\"\"
AIDatasetPack Pro - 企业级AI数据集智能打包工具
版本：v5.0 最终完整版
功能：自动合并相同格式文件、深度内容对比、智能压缩、完整验证、全自动化
\"\"\"

import os
import sys
import zipfile
import hashlib
import fnmatch
import json
import shutil
import threading
import concurrent.futures
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# ========== 1. 文件格式合并与内容对比核心引擎 ==========
class FileMerger:
    \"\"\"自动合并相同后缀的重复文件，支持深度内容对比\"\"\"

    def __init__(self):
        self.hash_cache = {}

    def get_file_hash(self, file_path: str, block_size=65536) -> str:
        \"\"\"计算文件SHA256哈希（带缓存）\"\"\"
        if file_path in self.hash_cache:
            return self.hash_cache[file_path]
        sha = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(block_size), b''):
                sha.update(chunk)
        h = sha.hexdigest()
        self.hash_cache[file_path] = h
        return h

    def find_duplicates_by_content(self, directory: str, exclude_patterns=None) -> Dict:
        \"\"\"基于内容哈希查找重复文件（相同后缀自动归类）\"\"\"
        groups = defaultdict(list)  # (ext, hash) -> files
        for root, dirs, files in os.walk(directory):
            if exclude_patterns:
                dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, p) for p in exclude_patterns)]
                files = [f for f in files if not any(fnmatch.fnmatch(f, p) for p in exclude_patterns)]
            for f in files:
                path = os.path.join(root, f)
                ext = os.path.splitext(f)[1].lower()
                try:
                    h = self.get_file_hash(path)
                    groups[(ext, h)].append(path)
                except:
                    continue
        # 保留重复组（大于1个文件）
        duplicates = {k: v for k, v in groups.items() if len(v) > 1}
        return duplicates

    def deep_compare_files(self, file1: str, file2: str) -> Dict:
        \"\"\"深度对比两个文件的内容差异\"\"\"
        result = {"identical": False, "similarity": 0.0, "diff_positions": []}
        if not os.path.exists(file1) or not os.path.exists(file2):
            return result
        size1 = os.path.getsize(file1)
        size2 = os.path.getsize(file2)
        if size1 != size2:
            result["similarity"] = min(size1, size2) / max(size1, size2)
        else:
            h1 = self.get_file_hash(file1)
            h2 = self.get_file_hash(file2)
            if h1 == h2:
                result["identical"] = True
                result["similarity"] = 1.0
                return result
            # 逐字节比较小文件
            if size1 < 10 * 1024 * 1024:
                with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                    b1 = f1.read()
                    b2 = f2.read()
                matches = sum(1 for a, b in zip(b1, b2) if a == b)
                result["similarity"] = matches / max(len(b1), len(b2))
                # 记录前100个差异位置
                for i, (a, b) in enumerate(zip(AIDatasetPack Pro 最终完整文档

本项目及文档严格遵循“无变动保留原文内容”原则
整合了对话历史中全部版本（v1.0 ~ v5.0）的所有代码、架构图、功能描述、技术说明、兴趣映射及使用指南，经修复错误、去重、融合后形成此最终完整版。
版本：v5.0 最终完整版
发布日期：2026-06-28

---

目录

1. 项目背景与目标
2. 系统架构设计
3. 核心功能模块
4. 完整源代码（最终合并版）
5. 快速开始指南
6. 企业级特性详解
7. 兴趣话题映射：财富与生存知识
8. 版本演进与修复记录
9. 结语

---

1. 项目背景与目标

AIDatasetPack Pro 是一款企业级AI数据集智能打包工具，旨在解决大规模数据集处理中的痛点：

· 重复文件占用存储空间
· 文件格式混乱，难以统一
· 压缩效率低，传输成本高
· 缺乏完整性校验，数据易损
· 与深度学习框架集成不便

核心目标：实现 全自动化、高压缩率、强一致性、易集成 的数据集打包流程。

---

2. 系统架构设计

```mermaid
graph TD
    subgraph "🎯 核心架构层"
        A[🏢 AIDatasetPack Pro v5.0] --> B[📁 企业级数据源]
        B --> C{🔄 自动化处理管道}
    end
    
    subgraph "🔧 智能预处理引擎"
        C --> D[🔄 FileMerger]
        D --> D1[📊 格式分析器]
        D --> D2[🔍 重复检测器]
        D --> D3[🔄 智能合并器]
        D --> D4[📈 深度内容对比器]
    end
    
    subgraph "🚀 并行压缩引擎"
        C --> E[⚡ 多线程处理器]
        E --> E1[🧵 线程池管理]
        E --> E2[📊 实时进度跟踪]
        E --> E3[⚡ 负载均衡]
    end
    
    subgraph "🗜️ 压缩与输出"
        C --> F[📦 ZIP_DEFLATED/STORED]
        F --> F1[🐘 Zip64大文件支持]
        F --> F2[🔒 SHA256校验生成]
        F --> F3[📋 元数据JSON生成]
    end
    
    subgraph "🧠 AI训练集成"
        C --> G[🤖 ZipImageDataset]
        G --> G1[🖼️ 懒加载]
        G --> G2[⚡ 缓存机制]
        G --> G3[🔄 变换管道]
    end
    
    classDef arch fill:#e3f2fd,stroke:#1565c0
    classDef pre fill:#f3e5f5,stroke:#7b1fa2
    classDef comp fill:#e8f5e8,stroke:#2e7d32
    classDef out fill:#fff3e0,stroke:#ef6c00
    classDef train fill:#fce4ec,stroke:#c2185b
    class A,B,C arch
    class D,D1,D2,D3,D4 pre
    class E,E1,E2,E3 comp
    class F,F1,F2,F3 out
    class G,G1,G2,G3 train
"""
