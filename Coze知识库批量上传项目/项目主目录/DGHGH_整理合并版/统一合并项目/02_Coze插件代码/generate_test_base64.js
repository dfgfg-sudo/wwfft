/**
 * 生成 Coze IDE 测试用的 ZIP Base64 数据
 */
const AdmZip = require('adm-zip');
const fs = require('fs');
const path = require('path');

const zip = new AdmZip();

// === 创建测试文件 ===

// 1. Markdown 文件（含 YAML front matter）
zip.addFile('projectA/docs/README.md', Buffer.from(
`---
title: 项目A说明文档
author: 张三
date: 2026-07-21
---

# 项目A说明文档

## 简介
这是一个测试项目，用于验证 Coze 批量知识库上传插件功能。

## 功能特点
- 支持多种文件格式解析
- 保留完整目录结构
- 自动编码检测与修复
- 安全过滤（隐藏文件/路径穿越）

## 使用方式
1. 将文件夹压缩为 ZIP
2. 在 Coze 工作流中调用本插件
3. 自动提取全部文件内容到知识库
`, 'utf-8'));

// 2. 纯文本文件
zip.addFile('projectA/docs/guide.txt', Buffer.from(
`使用指南

第一步：准备 ZIP 文件
在文件管理器中选中要上传的文件夹，右键压缩为 ZIP。

第二步：上传 ZIP
在 Coze 工作流中将 ZIP 文件转为 Base64 传入插件。

第三步：查看结果
插件会自动解压 ZIP，提取所有文件内容，保留目录结构。
`, 'utf-8'));

// 3. JSON 配置文件
zip.addFile('projectA/config/settings.json', Buffer.from(
JSON.stringify({
  name: '测试项目',
  version: '1.0.0',
  description: '用于测试的配置文件',
  features: ['批量上传', '目录结构保留', '安全过滤', '编码检测'],
  database: { type: 'postgresql', host: 'localhost', port: 5432 },
  logging: { level: 'info', file: '/var/log/app.log' }
}, null, 2), 'utf-8'));

// 4. JavaScript 源代码
zip.addFile('projectA/src/index.js', Buffer.from(
`/**
 * 主入口文件
 * @module index
 */

const express = require('express');
const app = express();

app.use(express.json());

app.get('/', (req, res) => {
  res.json({ message: 'Hello World', status: 'ok' });
});

app.get('/api/docs', (req, res) => {
  res.json({ documents: [], total: 0 });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port \${PORT}`);
});
`, 'utf-8'));

// 5. Python 源代码
zip.addFile('projectA/src/utils.py', Buffer.from(
`#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""工具函数模块"""

import os
import json
from typing import List, Dict, Optional

def load_config(path: str) -> dict:
    """加载配置文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_file_list(directory: str) -> List[str]:
    """获取目录下所有文件"""
    files = []
    for item in os.listdir(directory):
        full_path = os.path.join(directory, item)
        if os.path.isfile(full_path):
            files.append(full_path)
    return files

def format_size(bytes_val: int) -> str:
    """格式化文件大小"""
    if bytes_val == 0:
        return '0 B'
    units = ['B', 'KB', 'MB', 'GB']
    k = 1024
    i = 0
    size = bytes_val
    while size >= k and i < len(units) - 1:
        size /= k
        i += 1
    return f'{size:.2f} {units[i]}'
`, 'utf-8'));

// 6. CSV 数据文件
zip.addFile('projectB/data.csv', Buffer.from(
`序号,名称,类型,状态,创建时间
1,知识库A,文档库,已上线,2026-01-15
2,知识库B,代码库,测试中,2026-03-20
3,知识库C,混合库,规划中,2026-06-10
4,知识库D,图片库,已归档,2025-12-01
`, 'utf-8'));

// 7. HTML 报告文件
zip.addFile('projectB/report.html', Buffer.from(
`<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="description" content="批量上传测试报告">
  <meta name="keywords" content="Coze,知识库,批量上传">
  <title>批量上传测试报告</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; }
    h1 { color: #333; }
    .status { color: green; }
  </style>
</head>
<body>
  <h1>批量上传测试报告</h1>
  <p>本报告记录了批量知识库上传功能的测试结果。</p>
  <h2>测试环境</h2>
  <p>Node.js v22.16.0 | Coze IDE | adm-zip v0.5.18</p>
  <h2>测试结论</h2>
  <p class="status">所有测试用例通过，功能正常。</p>
  <script>console.log('test script removed');</script>
</body>
</html>`, 'utf-8'));

// 8. YAML 配置
zip.addFile('projectA/config/deploy.yaml', Buffer.from(
`server:
  host: 0.0.0.0
  port: 8080
  timeout: 30

database:
  type: postgresql
  name: knowledge_db
  user: admin
  password: "${'DB_PASSWORD'}"

logging:
  level: info
  file: /var/log/app.log
  max_size: 100MB
`, 'utf-8'));

// 9. SQL 文件
zip.addFile('projectA/db/schema.sql', Buffer.from(
`-- 知识库表结构
CREATE TABLE IF NOT EXISTS knowledge_documents (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  content TEXT,
  file_path VARCHAR(512),
  format VARCHAR(50),
  word_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_doc_path ON knowledge_documents(file_path);
CREATE INDEX IF NOT EXISTS idx_doc_format ON knowledge_documents(format);
`, 'utf-8'));

// 10. XML 配置文件
zip.addFile('projectA/config/mapping.xml', Buffer.from(
`<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <mappings>
    <mapping from="doc" to="document"/>
    <mapping from="md" to="markdown"/>
    <mapping from="txt" to="text"/>
  </mappings>
  <settings>
    <autoDetect>true</autoDetect>
    <encoding>utf-8</encoding>
  </settings>
</configuration>
`, 'utf-8'));

// 11. 隐藏文件（应该被过滤）
zip.addFile('projectA/.hidden_config', Buffer.from('这是隐藏文件，应该被自动过滤', 'utf-8'));

// 12. macOS 资源文件（应该被过滤）
zip.addFile('__MACOSX/._README.md', Buffer.from('macos resource fork data', 'utf-8'));

// 13. .DS_Store（应该被过滤）
zip.addFile('.DS_Store', Buffer.from('DSSTORE', 'utf-8'));

// === 保存并输出 Base64 ===
const zipBuffer = zip.toBuffer();
const base64 = zipBuffer.toString('base64');

// 保存 ZIP 文件
const zipPath = path.join(__dirname, 'test_sample.zip');
fs.writeFileSync(zipPath, zipBuffer);

// 保存 Base64 到文件
const b64Path = path.join(__dirname, 'test_sample_base64.txt');
fs.writeFileSync(b64Path, base64);

// 输出信息
console.log('============================================================');
console.log('Coze IDE 测试数据生成完成');
console.log('============================================================');
console.log();console.log(`ZIP 文件大小: ${(zipBuffer.length / 1024).toFixed(2)} KB`);
console.log(`Base64 长度: ${base64.length} 字符`);
console.log();console.log('文件已保存:');
console.log(`  - ${zipPath}`);
console.log(`  - ${b64Path}`);
console.log();
console.log('=== 以下是可直接用于 Coze IDE 测试的 Base64 字符串 ===');
console.log();
// 输出前 500 字符预览
console.log('前 500 字符预览:');
console.log(base64.substring(0, 500));
console.log('...');
console.log();
console.log('完整 Base64 已保存到 test_sample_base64.txt');
console.log('请复制该文件的全部内容，在 Coze IDE 的 Run 测试中作为 zip_base64 参数传入。');
