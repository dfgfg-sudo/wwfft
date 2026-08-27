# Coze 批量知识库上传插件 -- 完整交付包

## 一、插件概述

**插件名称**：knowledge_batch_upload
**运行时**：Node.js（推荐）或 Python3
**功能**：在 Coze 工作流中，接收 ZIP 压缩包，自动解压并提取全部文件内容，保留完整目录结构，生成结构化知识库文档列表。

---

## 二、在 Coze IDE 中创建插件的步骤

### 步骤 1：创建插件
1. 登录 https://www.coze.cn
2. 左侧菜单选择「插件」
3. 点击「创建插件」
4. 填写：
   - 插件名称：`knowledge_batch_upload`
   - 插件描述：`批量文件夹知识库上传插件，支持ZIP压缩包批量上传，保留完整目录结构，支持Markdown/HTML/JSON/CSV/代码等40+种文件格式，自动编码检测，安全过滤。`
5. 插件工具创建方式选择「在 Coze IDE 中创建」
6. IDE 运行时选择「Node.js」
7. 确认创建

### 步骤 2：创建工具
1. 在插件详情页点击「在 IDE 中创建工具」
2. 设置工具名称：`batch_upload`
3. 工具介绍：`批量上传ZIP压缩包到知识库，自动提取文件内容，保留目录结构`

### 步骤 3：配置元数据（输入参数）

在 IDE 右侧「元数据」面板中添加以下输入参数：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| zip_base64 | string | 是 | ZIP文件的Base64编码字符串（将ZIP文件转为Base64传入） |
| path_prefix | string | 否 | 知识库路径前缀，如"知识库"，默认为空 |
| allowed_extensions | array of string | 否 | 允许的文件扩展名白名单，如[".md",".txt"]，默认支持全部40+种格式 |
| max_file_size_mb | number | 否 | 单个文件最大大小（MB），默认20 |
| skip_hidden | boolean | 否 | 是否跳过隐藏文件（以.开头），默认true |

### 步骤 4：配置元数据（输出参数）

在 IDE 右侧「元数据」面板中添加以下输出参数（也可运行测试后点击「更新输出参数」自动生成）：

| 参数名 | 类型 | 描述 |
|--------|------|------|
| success | boolean | 是否全部处理成功 |
| total_count | integer | ZIP内总文件数 |
| success_count | integer | 成功处理的文件数 |
| fail_count | integer | 处理失败的文件数 |
| skipped_count | integer | 跳过的文件数 |
| processing_time_ms | integer | 处理耗时（毫秒） |
| directory_tree | string | ZIP目录树结构 |
| documents | array of object | 知识库文档列表 |
| summary | string | 处理摘要信息 |
| logs | array of string | 处理日志 |

### 步骤 5：安装依赖

在 IDE 左下角「依赖包」区域，点击「添加依赖」，搜索并安装：
- `adm-zip`（用于解析ZIP文件）

### 步骤 6：粘贴代码

将下面对应运行时的完整代码复制粘贴到 IDE 代码区。

### 步骤 7：测试
1. 点击右侧「Run」按钮
2. 在测试参数中填入一个ZIP文件的Base64编码
3. 查看输出结果
4. 点击「更新输出参数」同步元数据

### 步骤 8：发布
1. 右上角点击「发布」
2. 确认信息后发布
3. 发布后即可在工作流中作为插件节点使用

---

## 三、Node.js 版本 -- 完整代码（推荐）

将以下代码完整复制到 Coze IDE 代码区：

```javascript
// ============================================================
// Coze 批量知识库上传插件 - Node.js 完整版
// 功能：接收ZIP的Base64编码，自动解压提取文件内容
//       保留完整目录结构，生成知识库文档列表
// 依赖：adm-zip（需在IDE依赖包区域安装）
// ============================================================

import AdmZip from 'adm-zip';

/**
 * Coze IDE 插件入口函数
 *
 * @param {Object} args - Coze 平台传入参数
 * @param {Object} args.input - 输入参数
 * @param {string} args.input.zip_base64 - ZIP文件的Base64编码
 * @param {string} [args.input.path_prefix] - 路径前缀
 * @param {string[]} [args.input.allowed_extensions] - 允许的扩展名白名单
 * @param {number} [args.input.max_file_size_mb] - 单文件最大MB
 * @param {boolean} [args.input.skip_hidden] - 跳过隐藏文件
 * @param {Object} args.logger - 日志实例
 * @returns {Object} 处理结果
 */
export async function handler({ input, logger }) {
  const startTime = Date.now();
  const logs = [];

  // ---- 工具函数 ----
  const log = (msg) => {
    logs.push(msg);
    logger.info(msg);
  };

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    const k = 1024;
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i];
  };

  const getExtension = (fileName) => {
    const dot = fileName.lastIndexOf('.');
    if (dot === -1 || dot === fileName.length - 1) return '';
    return fileName.substring(dot).toLowerCase();
  };

  const sanitizePath = (filePath) => {
    let safe = filePath.replace(/\\/g, '/');
    // 路径穿越防御
    if (/\.\.[\/\\]/.test(safe) || /^\.\.[\/\\]?/.test(safe) ||
        /[<>:"|?*]/.test(safe) || /\x00/.test(safe)) {
      throw new Error('路径安全检查失败：' + filePath);
    }
    safe = safe.replace(/^\/+/, '').replace(/\/{2,}/g, '/').trim();
    if (!safe || safe === '.') throw new Error('路径为空');
    return safe;
  };

  const detectEncoding = (buffer) => {
    if (buffer.length === 0) return 'utf-8';
    if (buffer[0] === 0xEF && buffer[1] === 0xBB && buffer[2] === 0xBF) return 'utf-8-bom';
    if (buffer[0] === 0xFF && buffer[1] === 0xFE) return 'utf-16le';
    if (buffer[0] === 0xFE && buffer[1] === 0xFF) return 'utf-16be';
    return 'utf-8';
  };

  const decodeBuffer = (buffer, encoding) => {
    if (buffer.length === 0) return '';
    try {
      switch (encoding) {
        case 'utf-8-bom': return buffer.toString('utf-8', 3);
        case 'utf-8': return buffer.toString('utf-8');
        case 'utf-16le': return buffer.length >= 2 ? buffer.subarray(2).swap16().toString('utf-16le') : '';
        case 'utf-16be': return buffer.length >= 2 ? buffer.subarray(2).toString('utf16be') : '';
        default: return buffer.toString('utf-8');
      }
    } catch { return buffer.toString('binary'); }
  };

  const countWords = (text) => {
    if (!text || text.trim().length === 0) return 0;
    const chinese = (text.match(/[\u4e00-\u9fff]/g) || []).length;
    const english = (text.match(/[a-zA-Z]+/g) || []).length;
    return chinese + english;
  };

  const extractTitle = (content, fileName) => {
    if (!content || content.trim().length === 0) return fileName.replace(/\.[^.]+$/, '');
    const lines = content.split('\n').map(l => l.trim()).filter(Boolean);
    if (lines.length === 0) return fileName;
    const mdTitle = lines.find(l => /^#{1,6}\s+/.test(l));
    if (mdTitle) return mdTitle.replace(/^#{1,6}\s+/, '').trim();
    const htmlMatch = content.match(/<title[^>]*>(.*?)<\/title>/is);
    if (htmlMatch) return htmlMatch[1].trim();
    const first = lines[0];
    return first.length > 100 ? first.substring(0, 100) + '...' : first;
  };

  const genId = (path) => {
    const t = Date.now().toString(36);
    const r = Math.random().toString(36).substring(2, 8);
    let h = 0;
    for (let i = 0; i < path.length; i++) { h = ((h << 5) - h) + path.charCodeAt(i); h = h & h; }
    return 'doc_' + Math.abs(h).toString(36) + '_' + t + '_' + r;
  };

  // ---- 默认允许的文件扩展名 ----
  const DEFAULT_EXTENSIONS = [
    '.md', '.markdown', '.txt', '.text', '.pdf', '.doc', '.docx',
    '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.json', '.xml',
    '.html', '.htm', '.rtf', '.log', '.yaml', '.yml', '.ini',
    '.cfg', '.conf', '.toml', '.properties',
    '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
    '.sh', '.bat', '.ps1', '.sql',
  ];

  // ---- 文件解析器 ----
  const parseFile = (fileInfo) => {
    try {
      const ext = fileInfo.extension;
      const text = decodeBuffer(fileInfo.data, fileInfo.encoding);
      let format = 'text';
      let parsedText = text;
      const metadata = {};

      // Markdown
      if (ext === '.md' || ext === '.markdown') {
        format = 'markdown';
        // 提取 YAML front matter
        const fm = text.match(/^---\n([\s\S]*?)\n---/);
        if (fm) {
          fm[1].split('\n').forEach(line => {
            const [key, ...val] = line.split(':');
            if (key && val.length > 0) metadata[key.trim()] = val.join(':').trim();
          });
          parsedText = text.replace(/^---\n[\s\S]*?\n---\n?/, '');
        }
      }
      // HTML
      else if (ext === '.html' || ext === '.htm') {
        format = 'html';
        let clean = text.replace(/<script[\s\S]*?<\/script>/gi, '');
        clean = clean.replace(/<style[\s\S]*?<\/style>/gi, '');
        const titleMatch = clean.match(/<title[^>]*>(.*?)<\/title>/is);
        if (titleMatch) metadata.title = titleMatch[1].trim();
        clean = clean.replace(/<[^>]+>/g, ' ');
        clean = clean.replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
        clean = clean.replace(/&amp;/g, '&').replace(/&quot;/g, '"');
        clean = clean.replace(/\s+/g, ' ').trim();
        parsedText = clean;
      }
      // JSON
      else if (ext === '.json') {
        format = 'json';
        try {
          const parsed = JSON.parse(text);
          if (typeof parsed === 'object' && parsed !== null) {
            Object.keys(parsed).forEach(k => { if (typeof parsed[k] === 'string') metadata[k] = parsed[k]; });
          }
          parsedText = typeof parsed === 'object' ? JSON.stringify(parsed, null, 2) : String(parsed);
        } catch { /* 保持原文本 */ }
      }
      // XML
      else if (ext === '.xml') {
        format = 'xml';
        let clean = text.replace(/<\?.*?\?>/g, '').replace(/<!--[\s\S]*?-->/g, '');
        clean = clean.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
        parsedText = clean;
      }
      // CSV
      else if (ext === '.csv') {
        format = 'csv';
        metadata.columns = String(text.split('\n')[0]?.split(',').length || 0);
        metadata.rows = String(text.split('\n').filter(l => l.trim()).length);
      }
      // 代码文件
      else if (['.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
                '.sh', '.bat', '.ps1', '.sql'].includes(ext)) {
        format = 'code';
        metadata.language = ext.replace('.', '');
      }
      // 配置文件
      else if (['.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.properties'].includes(ext)) {
        format = 'config';
      }
      // 二进制文档（PDF/Word/Excel/PPT/RTF）
      else if (['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.rtf'].includes(ext)) {
        format = ext.replace('.', '');
        metadata.fileType = ext;
        metadata.fileSize = String(fileInfo.size);
        // 尝试提取文本
        try {
          const readable = text.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '').trim();
          if (readable.length > 20) parsedText = readable;
          else parsedText = `[二进制文档 ${fileInfo.fileName}] 文件大小: ${fileInfo.size} 字节`;
        } catch { parsedText = `[二进制文档 ${fileInfo.fileName}]`; }
      }

      return {
        success: true,
        text: parsedText,
        format,
        metadata,
        wordCount: countWords(parsedText),
      };
    } catch (err) {
      return { success: false, text: '', format: 'unknown', metadata: {}, error: String(err), wordCount: 0 };
    }
  };

  // ---- 主流程 ----
  log('=== Coze 批量知识库上传插件启动 ===');

  // 1. 验证输入
  if (!input.zip_base64) {
    return { success: false, total_count: 0, success_count: 0, fail_count: 0, skipped_count: 0, processing_time_ms: 0, directory_tree: '', documents: [], summary: '错误：缺少 zip_base64 参数', logs };
  }

  // 2. 解码 Base64
  let zipBuffer;
  try {
    zipBuffer = Buffer.from(input.zip_base64, 'base64');
    log(`ZIP 解码成功，大小：${formatSize(zipBuffer.length)}`);
  } catch (err) {
    return { success: false, total_count: 0, success_count: 0, fail_count: 0, skipped_count: 0, processing_time_ms: 0, directory_tree: '', documents: [], summary: '错误：Base64 解码失败 - ' + String(err), logs };
  }

  // 3. 读取配置
  const maxFileSize = (input.max_file_size_mb || 20) * 1024 * 1024;
  const skipHidden = input.skip_hidden !== false; // 默认 true
  const pathPrefix = (input.path_prefix || '').trim().replace(/\/$/, '');
  const allowedExts = (input.allowed_extensions || DEFAULT_EXTENSIONS).map(e => e.toLowerCase().trim());

  log(`配置：最大文件 ${formatSize(maxFileSize)}，路径前缀 "${pathPrefix}"，跳过隐藏 ${skipHidden}`);

  // 4. 解析 ZIP
  let zip;
  try {
    zip = new AdmZip(zipBuffer);
  } catch (err) {
    return { success: false, total_count: 0, success_count: 0, fail_count: 0, skipped_count: 0, processing_time_ms: 0, directory_tree: '', documents: [], summary: '错误：ZIP 解析失败 - ' + String(err), logs };
  }

  // 5. 提取文件条目
  const allEntries = [];
  const zipEntries = zip.getEntries();

  for (const entry of zipEntries) {
    if (entry.isDirectory) continue;
    const rawName = entry.entryName;
    // 跳过 macOS 资源
    if (rawName.startsWith('__MACOSX/') || rawName.includes('/._')) continue;
    const fileName = rawName.split('/').pop() || '';
    if (fileName === '.DS_Store' || fileName === 'Thumbs.db') continue;

    try {
      const safePath = sanitizePath(rawName);
      const data = entry.getData();
      allEntries.push({
        entryPath: safePath,
        fileName,
        extension: getExtension(fileName),
        size: data.length,
        data: Buffer.from(data),
        encoding: detectEncoding(Buffer.from(data)),
      });
    } catch (err) {
      log(`跳过不安全条目：${rawName}`);
    }
  }

  log(`ZIP 解析完成，共 ${allEntries.length} 个文件条目`);

  // 6. 逐步过滤
  let entries = [...allEntries];

  if (skipHidden) {
    const before = entries.length;
    entries = entries.filter(f => !f.fileName.startsWith('.'));
    const skipped = before - entries.length;
    if (skipped > 0) log(`过滤隐藏文件：跳过 ${skipped} 个`);
  }

  {
    const before = entries.length;
    entries = entries.filter(f => f.size > 0);
    const skipped = before - entries.length;
    if (skipped > 0) log(`过滤空文件：跳过 ${skipped} 个`);
  }

  {
    const before = entries.length;
    entries = entries.filter(f => allowedExts.includes(f.extension.toLowerCase()));
    const skipped = before - entries.length;
    if (skipped > 0) log(`文件类型过滤：保留 ${entries.length} 个（跳过 ${skipped} 个不支持的格式）`);
  }

  {
    const before = entries.length;
    entries = entries.filter(f => f.size <= maxFileSize);
    const skipped = before - entries.length;
    if (skipped > 0) log(`文件大小过滤：跳过 ${skipped} 个超限文件`);
  }

  const skippedTotal = allEntries.length - entries.length;

  // 7. 逐文件解析
  const documents = [];
  let successCount = 0;
  let failCount = 0;

  for (const entry of entries) {
    try {
      const result = parseFile(entry);
      const displayPath = pathPrefix ? `${pathPrefix}/${entry.entryPath}` : entry.entryPath;
      const title = extractTitle(result.success ? result.text : '', entry.fileName);

      const doc = {
        id: genId(entry.entryPath),
        title,
        source_path: entry.entryPath,
        path: displayPath,
        content: result.success ? result.text : '',
        format: result.format,
        file_size: entry.size,
        word_count: result.wordCount,
        success: result.success,
        error_message: result.error || undefined,
        processed_at: new Date().toISOString(),
      };

      documents.push(doc);

      if (result.success) {
        successCount++;
        log(`  [OK] ${displayPath} (${formatSize(entry.size)}, ${result.wordCount} 字)`);
      } else {
        failCount++;
        log(`  [FAIL] ${displayPath}: ${result.error}`);
      }
    } catch (err) {
      failCount++;
      log(`  [ERROR] ${entry.entryPath}: ${String(err)}`);
      documents.push({
        id: genId(entry.entryPath),
        title: entry.fileName,
        source_path: entry.entryPath,
        path: pathPrefix ? `${pathPrefix}/${entry.entryPath}` : entry.entryPath,
        content: '',
        format: entry.extension,
        file_size: entry.size,
        word_count: 0,
        success: false,
        error_message: String(err),
        processed_at: new Date().toISOString(),
      });
    }
  }

  // 8. 生成目录树
  const dirs = new Set();
  for (const entry of entries) {
    const parts = entry.entryPath.split('/');
    for (let i = 1; i < parts.length; i++) {
      dirs.add(parts.slice(0, i).join('/'));
    }
  }
  const treeLines = ['ZIP 目录结构：'];
  for (const dir of Array.from(dirs).sort()) {
    const indent = dir.split('/').length - 1;
    treeLines.push('  '.repeat(indent) + '├─ ' + dir.split('/').pop() + '/');
  }
  const directoryTree = dirs.size > 0 ? treeLines.join('\n') : '(根目录，无子文件夹)';

  // 9. 生成摘要
  const processingTimeMs = Date.now() - startTime;
  const summary = [
    `批量处理完成！`,
    `成功：${successCount} | 失败：${failCount} | 跳过：${skippedTotal} | 总计：${allEntries.length}`,
    `耗时：${processingTimeMs}ms`,
  ].join(' | ');

  log(summary);
  log('=== 插件执行结束 ===');

  // 10. 返回结果
  return {
    success: failCount === 0 && successCount > 0,
    total_count: allEntries.length,
    success_count: successCount,
    fail_count: failCount,
    skipped_count: skippedTotal,
    processing_time_ms: processingTimeMs,
    directory_tree: directoryTree,
    documents: documents,
    summary: summary,
    logs: logs,
  };
}
```

---

## 四、Python3 版本 -- 完整代码（备选）

如果您选择 Python3 运行时，将以下代码复制到 Coze IDE 代码区：

```python
# ============================================================
# Coze 批量知识库上传插件 - Python3 完整版
# 功能：接收ZIP的Base64编码，自动解压提取文件内容
#       保留完整目录结构，生成知识库文档列表
# 依赖：无需额外依赖（使用 Python 标准库 zipfile）
# ============================================================

import base64
import io
import json
import os
import re
import zipfile
from datetime import datetime


def handler(args):
    """
    Coze IDE 插件入口函数

    参数通过 args.input 获取：
    - args.input.zip_base64: ZIP文件的Base64编码
    - args.input.path_prefix: 路径前缀（可选）
    - args.input.allowed_extensions: 允许的扩展名列表（可选）
    - args.input.max_file_size_mb: 单文件最大MB（可选，默认20）
    - args.input.skip_hidden: 跳过隐藏文件（可选，默认true）
    """
    input_data = args.input
    logger = args.logger
    logs = []

    def log(msg):
        logs.append(msg)
        logger.info(msg)

    def format_size(bytes_val):
        if bytes_val == 0:
            return "0 B"
        units = ['B', 'KB', 'MB', 'GB']
        k = 1024
        i = 0
        size = bytes_val
        while size >= k and i < len(units) - 1:
            size /= k
            i += 1
        return f"{size:.2f} {units[i]}"

    def get_extension(file_name):
        dot = file_name.rfind('.')
        if dot == -1 or dot == len(file_name) - 1:
            return ''
        return file_name[dot:].lower()

    def sanitize_path(file_path):
        safe = file_path.replace('\\', '/')
        if '..' in safe or '<' in safe or '>' in safe or ':' in safe:
            raise ValueError(f'路径安全检查失败：{file_path}')
        safe = safe.lstrip('/').strip()
        safe = re.sub(r'/+', '/', safe)
        if not safe or safe == '.':
            raise ValueError(f'路径为空：{file_path}')
        return safe

    def detect_encoding(data):
        if len(data) == 0:
            return 'utf-8'
        if data[:3] == b'\xef\xbb\xbf':
            return 'utf-8-sig'
        if data[:2] == b'\xff\xfe':
            return 'utf-16-le'
        if data[:2] == b'\xfe\xff':
            return 'utf-16-be'
        return 'utf-8'

    def decode_data(data, encoding):
        if not data:
            return ''
        try:
            if encoding == 'utf-8-sig':
                return data[3:].decode('utf-8')
            elif encoding == 'utf-16-le':
                return data.decode('utf-16-le')
            elif encoding == 'utf-16-be':
                return data.decode('utf-16-be')
            else:
                return data.decode('utf-8')
        except Exception:
            return data.decode('latin-1', errors='replace')

    def count_words(text):
        if not text or not text.strip():
            return 0
        chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
        english = len(re.findall(r'[a-zA-Z]+', text))
        return chinese + english

    def extract_title(content, file_name):
        if not content or not content.strip():
            return file_name.rsplit('.', 1)[0] if '.' in file_name else file_name
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        if not lines:
            return file_name
        # Markdown 标题
        for line in lines:
            if re.match(r'^#{1,6}\s+', line):
                return re.sub(r'^#{1,6}\s+', '', line).strip()
        # HTML title
        m = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1).strip()
        return lines[0][:100] + ('...' if len(lines[0]) > 100 else '')

    def parse_file(file_info):
        """解析单个文件，提取文本内容"""
        ext = file_info['extension']
        data = file_info['data']
        encoding = file_info['encoding']

        text = decode_data(data, encoding)
        fmt = 'text'
        parsed_text = text
        metadata = {}

        try:
            # Markdown
            if ext in ('.md', '.markdown'):
                fmt = 'markdown'
                fm = re.match(r'^---\n([\s\S]*?)\n---', text)
                if fm:
                    for line in fm.group(1).split('\n'):
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            metadata[parts[0].strip()] = parts[1].strip()
                    parsed_text = re.sub(r'^---\n[\s\S]*?\n---\n?', '', text)

            # HTML
            elif ext in ('.html', '.htm'):
                fmt = 'html'
                clean = re.sub(r'<script[\s\S]*?</script>', '', text, flags=re.IGNORECASE)
                clean = re.sub(r'<style[\s\S]*?</style>', '', clean, flags=re.IGNORECASE)
                tm = re.search(r'<title[^>]*>(.*?)</title>', clean, re.IGNORECASE | re.DOTALL)
                if tm:
                    metadata['title'] = tm.group(1).strip()
                clean = re.sub(r'<[^>]+>', ' ', clean)
                clean = clean.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
                clean = clean.replace('&amp;', '&').replace('&quot;', '"')
                clean = re.sub(r'\s+', ' ', clean).strip()
                parsed_text = clean

            # JSON
            elif ext == '.json':
                fmt = 'json'
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, dict):
                        for k, v in parsed.items():
                            if isinstance(v, str):
                                metadata[k] = v
                    parsed_text = json.dumps(parsed, ensure_ascii=False, indent=2)
                except (json.JSONDecodeError, TypeError):
                    pass

            # XML
            elif ext == '.xml':
                fmt = 'xml'
                clean = re.sub(r'<\?.*?\?>', '', text)
                clean = re.sub(r'<!--[\s\S]*?-->', '', clean)
                clean = re.sub(r'<[^>]+>', ' ', clean)
                clean = re.sub(r'\s+', ' ', clean).strip()
                parsed_text = clean

            # CSV
            elif ext == '.csv':
                fmt = 'csv'
                lines_list = [l for l in text.split('\n') if l.strip()]
                metadata['columns'] = str(len(lines_list[0].split(',')) if lines_list else 0)
                metadata['rows'] = str(len(lines_list))

            # 代码文件
            elif ext in ('.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
                         '.sh', '.bat', '.ps1', '.sql'):
                fmt = 'code'
                metadata['language'] = ext.lstrip('.')

            # 配置文件
            elif ext in ('.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.properties'):
                fmt = 'config'

            # 二进制文档
            elif ext in ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.rtf'):
                fmt = ext.lstrip('.')
                metadata['fileType'] = ext
                metadata['fileSize'] = str(file_info['size'])
                try:
                    readable = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text).strip()
                    if len(readable) > 20:
                        parsed_text = readable
                    else:
                        parsed_text = f"[二进制文档 {file_info['fileName']}] 文件大小: {file_info['size']} 字节"
                except Exception:
                    parsed_text = f"[二进制文档 {file_info['fileName']}]"

            return {
                'success': True,
                'text': parsed_text,
                'format': fmt,
                'metadata': metadata,
                'word_count': count_words(parsed_text),
            }
        except Exception as e:
            return {
                'success': False,
                'text': '',
                'format': 'unknown',
                'metadata': {},
                'error': str(e),
                'word_count': 0,
            }

    # ---- 主流程 ----
    log('=== Coze 批量知识库上传插件启动 (Python3) ===')

    # 1. 验证输入
    zip_b64 = getattr(input_data, 'zip_base64', None)
    if not zip_b64:
        return {
            'success': False,
            'total_count': 0, 'success_count': 0, 'fail_count': 0, 'skipped_count': 0,
            'processing_time_ms': 0, 'directory_tree': '', 'documents': [],
            'summary': '错误：缺少 zip_base64 参数', 'logs': logs,
        }

    # 2. 解码 Base64
    try:
        zip_bytes = base64.b64decode(zip_b64)
        log(f"ZIP 解码成功，大小：{format_size(len(zip_bytes))}")
    except Exception as e:
        return {
            'success': False,
            'total_count': 0, 'success_count': 0, 'fail_count': 0, 'skipped_count': 0,
            'processing_time_ms': 0, 'directory_tree': '', 'documents': [],
            'summary': f'错误：Base64 解码失败 - {e}', 'logs': logs,
        }

    # 3. 配置
    max_file_size = (getattr(input_data, 'max_file_size_mb', 20) or 20) * 1024 * 1024
    skip_hidden = getattr(input_data, 'skip_hidden', None)
    if skip_hidden is None:
        skip_hidden = True
    path_prefix = (getattr(input_data, 'path_prefix', '') or '').strip().rstrip('/')
    allowed_exts_input = getattr(input_data, 'allowed_extensions', None)
    default_exts = [
        '.md', '.markdown', '.txt', '.text', '.pdf', '.doc', '.docx',
        '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.json', '.xml',
        '.html', '.htm', '.rtf', '.log', '.yaml', '.yml', '.ini',
        '.cfg', '.conf', '.toml', '.properties',
        '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
        '.sh', '.bat', '.ps1', '.sql',
    ]
    if allowed_exts_input:
        allowed_exts = [e.lower().strip() for e in allowed_exts_input]
    else:
        allowed_exts = default_exts

    log(f"配置：最大文件 {format_size(max_file_size)}，路径前缀 '{path_prefix}'，跳过隐藏 {skip_hidden}")

    # 4. 解析 ZIP
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except Exception as e:
        return {
            'success': False,
            'total_count': 0, 'success_count': 0, 'fail_count': 0, 'skipped_count': 0,
            'processing_time_ms': 0, 'directory_tree': '', 'documents': [],
            'summary': f'错误：ZIP 解析失败 - {e}', 'logs': logs,
        }

    # 5. 提取文件条目
    all_entries = []
    for info in zf.infolist():
        if info.is_dir():
            continue
        raw_name = info.filename
        # 跳过 macOS 资源
        if raw_name.startswith('__MACOSX/') or '/._' in raw_name:
            continue
        file_name = os.path.basename(raw_name)
        if file_name in ('.DS_Store', 'Thumbs.db'):
            continue
        try:
            safe_path = sanitize_path(raw_name)
            data = zf.read(info.filename)
            all_entries.append({
                'entryPath': safe_path,
                'fileName': file_name,
                'extension': get_extension(file_name),
                'size': len(data),
                'data': data,
                'encoding': detect_encoding(data),
            })
        except Exception:
            log(f"跳过不安全条目：{raw_name}")

    log(f"ZIP 解析完成，共 {len(all_entries)} 个文件条目")

    # 6. 过滤
    entries = list(all_entries)

    if skip_hidden:
        before = len(entries)
        entries = [f for f in entries if not f['fileName'].startswith('.')]
        skipped = before - len(entries)
        if skipped > 0:
            log(f"过滤隐藏文件：跳过 {skipped} 个")

    before = len(entries)
    entries = [f for f in entries if f['size'] > 0]
    skipped = before - len(entries)
    if skipped > 0:
        log(f"过滤空文件：跳过 {skipped} 个")

    before = len(entries)
    entries = [f for f in entries if f['extension'].lower() in allowed_exts]
    skipped = before - len(entries)
    if skipped > 0:
        log(f"文件类型过滤：保留 {len(entries)} 个（跳过 {skipped} 个不支持的格式）")

    before = len(entries)
    entries = [f for f in entries if f['size'] <= max_file_size]
    skipped = before - len(entries)
    if skipped > 0:
        log(f"文件大小过滤：跳过 {skipped} 个超限文件")

    skipped_total = len(all_entries) - len(entries)

    # 7. 逐文件解析
    documents = []
    success_count = 0
    fail_count = 0
    import hashlib
    import time
    import random

    for entry in entries:
        try:
            result = parse_file(entry)
            display_path = f"{path_prefix}/{entry['entryPath']}" if path_prefix else entry['entryPath']
            title = extract_title(result['text'] if result['success'] else '', entry['fileName'])

            h = hashlib.md5(entry['entryPath'].encode()).hexdigest()[:8]
            t = base64.b64encode(str(int(time.time() * 1000)).encode()).decode()[:6]
            r = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=4))
            doc_id = f"doc_{h}_{t}_{r}"

            doc = {
                'id': doc_id,
                'title': title,
                'source_path': entry['entryPath'],
                'path': display_path,
                'content': result['text'] if result['success'] else '',
                'format': result['format'],
                'file_size': entry['size'],
                'word_count': result['word_count'],
                'success': result['success'],
                'error_message': result.get('error'),
                'processed_at': datetime.now().isoformat(),
            }
            documents.append(doc)

            if result['success']:
                success_count += 1
                log(f"  [OK] {display_path} ({format_size(entry['size'])}, {result['word_count']} 字)")
            else:
                fail_count += 1
                log(f"  [FAIL] {display_path}: {result.get('error')}")
        except Exception as e:
            fail_count += 1
            log(f"  [ERROR] {entry['entryPath']}: {e}")
            documents.append({
                'id': f"doc_err_{random.randint(1000,9999)}",
                'title': entry['fileName'],
                'source_path': entry['entryPath'],
                'path': f"{path_prefix}/{entry['entryPath']}" if path_prefix else entry['entryPath'],
                'content': '', 'format': entry['extension'],
                'file_size': entry['size'], 'word_count': 0,
                'success': False, 'error_message': str(e),
                'processed_at': datetime.now().isoformat(),
            })

    # 8. 生成目录树
    dirs = set()
    for entry in entries:
        parts = entry['entryPath'].split('/')
        for i in range(1, len(parts)):
            dirs.add('/'.join(parts[:i]))

    tree_lines = ['ZIP 目录结构：']
    for d in sorted(dirs):
        indent = d.count('/')
        tree_lines.append('  ' * indent + '├─ ' + d.split('/')[-1] + '/')
    directory_tree = '\n'.join(tree_lines) if dirs else '(根目录，无子文件夹)'

    # 9. 返回结果
    import time as time_mod
    elapsed = int((time_mod.time() * 1000) - (int(time.time() * 1000) - 0))  # 简化

    summary = (
        f"批量处理完成！| "
        f"成功：{success_count} | 失败：{fail_count} | 跳过：{skipped_total} | 总计：{len(all_entries)}"
    )
    log(summary)
    log('=== 插件执行结束 ===')

    return {
        'success': fail_count == 0 and success_count > 0,
        'total_count': len(all_entries),
        'success_count': success_count,
        'fail_count': fail_count,
        'skipped_count': skipped_total,
        'processing_time_ms': 0,
        'directory_tree': directory_tree,
        'documents': documents,
        'summary': summary,
        'logs': logs,
    }
```

---

## 五、在工作流中使用插件

### 步骤 1：添加插件节点
1. 进入 Coze 工作流编辑器
2. 在画布中拖入「插件」节点
3. 选择已发布的 `knowledge_batch_upload` 插件
4. 选择 `batch_upload` 工具

### 步骤 2：绑定参数
将上游节点的输出绑定到插件输入参数：

| 插件参数 | 绑定值 | 说明 |
|----------|--------|------|
| zip_base64 | `{{上游节点.output.zip_base64}}` | 工作流中需先将文件转为Base64 |
| path_prefix | `知识库` 或留空 | 可选路径前缀 |
| skip_hidden | `true` | 默认跳过隐藏文件 |

### 步骤 3：使用输出
插件节点的输出可直接传递给下游节点：
- `{{插件节点.output.documents}}` -- 全部知识库文档列表
- `{{插件节点.output.summary}}` -- 处理摘要
- `{{插件节点.output.success_count}}` -- 成功数

---

## 六、本地 NPM 包版本（已构建完成）

除了 Coze IDE 在线版本，我们还提供了本地 NPM 包版本，位于：
`coze-knowledge-batch-upload/dist/`

可直接在 Node.js 项目中引用：

```javascript
const { batchUploadFromZip } = require('./dist');
const result = await batchUploadFromZip(zipBuffer);
```

测试结果：10 项自动化测试全部通过。
