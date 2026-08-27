/**
 * 自动化测试脚本
 * 创建测试 ZIP 文件，验证完整处理流程
 */

const path = require('path');
const fs = require('fs');
const AdmZip = require('adm-zip');

const projectRoot = path.resolve(__dirname, '..');
const distDir = path.join(projectRoot, 'dist');

async function createTestZip() {
  const zip = new AdmZip();

  // 创建测试文件夹结构：
  // projectA/
  //   docs/
  //     README.md
  //     guide.txt
  //   config/
  //     settings.json
  //   src/
  //     index.js
  //     utils.py
  // projectB/
  //   data.csv
  //   report.html

  // Markdown 文件（含 YAML front matter）
  zip.addFile(
    'projectA/docs/README.md',
    Buffer.from(`---
title: 项目A说明文档
author: 张三
---

# 项目A说明文档

## 简介
这是一个测试项目，用于验证批量知识库上传功能。

## 功能特点
- 支持多种文件格式
- 保留完整目录结构
- 自动编码检测
`, 'utf-8')
  );

  // 纯文本文件
  zip.addFile(
    'projectA/docs/guide.txt',
    Buffer.from('使用指南\n\n1. 准备ZIP文件\n2. 上传到工作流\n3. 自动处理\n', 'utf-8')
  );

  // JSON 配置文件
  zip.addFile(
    'projectA/config/settings.json',
    Buffer.from(JSON.stringify({
      name: '测试项目',
      version: '1.0.0',
      description: '用于测试的配置文件',
      features: ['批量上传', '目录结构保留', '安全过滤']
    }, null, 2), 'utf-8')
  );

  // JavaScript 源代码
  zip.addFile(
    'projectA/src/index.js',
    Buffer.from(`/**
 * 主入口文件
 * @module index
 */

const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello World');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port \${PORT}`);
});
`, 'utf-8')
  );

  // Python 源代码
  zip.addFile(
    'projectA/src/utils.py',
    Buffer.from(`#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""工具函数模块"""

import os
import json

def load_config(path):
    """加载配置文件"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_file_list(directory):
    """获取目录下所有文件"""
    files = []
    for item in os.listdir(directory):
        full_path = os.path.join(directory, item)
        if os.path.isfile(full_path):
            files.append(full_path)
    return files
`, 'utf-8')
  );

  // CSV 数据文件
  zip.addFile(
    'projectB/data.csv',
    Buffer.from('序号,名称,类型,状态\n1,知识库A,文档库,已上线\n2,知识库B,代码库,测试中\n3,知识库C,混合库,规划中\n', 'utf-8')
  );

  // HTML 报告文件
  zip.addFile(
    'projectB/report.html',
    Buffer.from(`<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="description" content="测试报告">
  <title>批量上传测试报告</title>
</head>
<body>
  <h1>批量上传测试报告</h1>
  <p>本报告记录了批量知识库上传功能的测试结果。</p>
  <h2>测试环境</h2>
  <p>Node.js v22.16.0</p>
  <h2>测试结论</h2>
  <p>所有测试用例通过，功能正常。</p>
  <script>console.log('test')</script>
</body>
</html>`, 'utf-8')
  );

  // YAML 配置
  zip.addFile(
    'projectA/config/deploy.yaml',
    Buffer.from(`server:
  host: 0.0.0.0
  port: 8080

database:
  type: postgresql
  name: knowledge_db

logging:
  level: info
  file: /var/log/app.log
`, 'utf-8')
  );

  // SQL 文件
  zip.addFile(
    'projectA/db/schema.sql',
    Buffer.from(`-- 知识库表结构
CREATE TABLE knowledge_documents (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  content TEXT,
  file_path VARCHAR(512),
  format VARCHAR(50),
  word_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doc_path ON knowledge_documents(file_path);
`, 'utf-8')
  );

  // 隐藏文件（应该被过滤）
  zip.addFile(
    'projectA/.hidden',
    Buffer.from('这是隐藏文件，应该被跳过', 'utf-8')
  );

  // macOS 资源文件（应该被过滤）
  zip.addFile(
    '__MACOSX/._test',
    Buffer.from('macos resource fork', 'utf-8')
  );

  return zip.toBuffer();
}

async function runTest() {
  console.log('='.repeat(60));
  console.log('Coze 批量知识库上传插件 - 自动化测试');
  console.log('='.repeat(60));
  console.log();

  // 检查 dist 目录
  if (!fs.existsSync(path.join(distDir, 'index.js'))) {
    console.error('错误：构建产物不存在，请先运行 pnpm run build');
    process.exit(1);
  }

  // 导入模块
  console.log('1. 加载模块...');
  const { batchUploadFromZip, KnowledgeBatchUploader, SECURITY_CONFIG } = require(distDir);
  console.log('   模块加载成功');
  console.log();

  // 创建测试 ZIP
  console.log('2. 创建测试 ZIP 文件...');
  const testZipBuffer = await createTestZip();
  console.log(`   测试 ZIP 创建完成，大小：${(testZipBuffer.length / 1024).toFixed(2)} KB`);
  console.log();

  // 运行批量处理
  console.log('3. 执行批量处理...');
  const result = await batchUploadFromZip(testZipBuffer, {
    pathPrefix: '知识库',
  });
  console.log();

  // 输出结果
  console.log('4. 处理结果：');
  console.log('-'.repeat(40));
  console.log(`   总文件数：${result.totalCount}`);
  console.log(`   成功处理：${result.successCount}`);
  console.log(`   处理失败：${result.failCount}`);
  console.log(`   跳过文件：${result.skippedCount}`);
  console.log(`   处理耗时：${result.processingTimeMs}ms`);
  console.log(`   整体状态：${result.success ? '成功' : '部分失败'}`);
  console.log();

  // 目录树
  console.log('5. 目录结构：');
  console.log('-'.repeat(40));
  console.log(result.directoryTree);
  console.log();

  // 文档列表
  console.log('6. 文档详情：');
  console.log('-'.repeat(40));
  for (const doc of result.documents) {
    const status = doc.success ? 'OK' : 'FAIL';
    console.log(`   [${status}] ${doc.path}`);
    console.log(`         标题: ${doc.title}`);
    console.log(`         格式: ${doc.format} | 大小: ${doc.fileSize}B | 字数: ${doc.wordCount}`);
    if (doc.errorMessage) {
      console.log(`         错误: ${doc.errorMessage}`);
    }
    console.log();
  }

  // 处理日志
  console.log('7. 处理日志：');
  console.log('-'.repeat(40));
  for (const log of result.logs) {
    console.log(`   ${log}`);
  }
  console.log();

  // 测试验证
  console.log('8. 测试验证：');
  console.log('-'.repeat(40));
  const tests = [
    {
      name: 'ZIP 文件正确解析',
      pass: result.totalCount >= 9, // 至少 9 个有效文件
    },
    {
      name: '文件全部处理成功',
      pass: result.successCount === 9 && result.failCount === 0,
    },
    {
      name: '隐藏文件被过滤',
      pass: result.skippedCount >= 1,
    },
    {
      name: '目录结构完整保留',
      pass: result.documents.some(d => d.path.includes('projectA/docs/')),
    },
    {
      name: '路径前缀正确添加',
      pass: result.documents.every(d => d.path.startsWith('知识库/')),
    },
    {
      name: 'Markdown 正确解析',
      pass: result.documents.find(d => d.format === 'markdown')?.wordCount > 0,
    },
    {
      name: 'HTML 正确解析（标签去除）',
      pass: (() => {
        const htmlDoc = result.documents.find(d => d.format === 'html');
        return htmlDoc && !htmlDoc.content.includes('<script>');
      })(),
    },
    {
      name: 'JSON 正确解析',
      pass: result.documents.find(d => d.format === 'json')?.wordCount > 0,
    },
    {
      name: '代码文件保留原始格式',
      pass: result.documents.some(d => d.format === 'code'),
    },
    {
      name: 'CSV 正确解析',
      pass: result.documents.find(d => d.format === 'csv')?.wordCount > 0,
    },
  ];

  let allPassed = true;
  for (const test of tests) {
    const icon = test.pass ? 'PASS' : 'FAIL';
    if (!test.pass) allPassed = false;
    console.log(`   [${icon}] ${test.name}`);
  }
  console.log();

  // 最终结论
  console.log('='.repeat(60));
  if (allPassed) {
    console.log('所有测试通过！插件功能完整可用。');
  } else {
    console.log('部分测试未通过，请检查上方 FAIL 项。');
  }
  console.log('='.repeat(60));

  return allPassed;
}

runTest()
  .then(success => process.exit(success ? 0 : 1))
  .catch(err => {
    console.error('测试执行出错：', err);
    process.exit(1);
  });
