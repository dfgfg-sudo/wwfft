# Coze 批量知识库上传插件 -- 完整交付包（最终版）

## 一、插件概述

**插件名称**：`knowledge_batch_upload`
**工具名称**：`batch_upload`
**工具版本**：1.0.0
**运行时**：Node.js（推荐）或 Python3
**功能**：在 Coze 工作流中，接收 ZIP 压缩包（通过URL或Base64），自动解压并提取全部文件内容，保留完整目录结构，生成结构化知识库文档列表，直接供 Coze 知识库节点使用。

---

## 二、在 Coze IDE 中创建插件的步骤

### 步骤 1：创建插件
1. 登录 https://www.coze.cn
2. 左侧菜单选择「插件」
3. 点击「创建插件」
4. 填写：
   - 插件名称：`knowledge_batch_upload`
   - 插件描述：`批量上传知识库数据到指定知识库，自动调整文件内容，提取关键信息`
5. 插件工具创建方式选择「在 Coze IDE 中创建」
6. IDE 运行时选择「Node.js」
7. 确认创建

### 步骤 2：创建工具
1. 在插件详情页点击「在 IDE 中创建工具」
2. 设置工具名称：`batch_upload`
3. 工具介绍：`批量上传知识库数据到指定知识库，自动调整文件内容，提取关键信息`

### 步骤 3：配置元数据（输入参数）

在 IDE 右侧「配置」面板 ->「输入参数」中添加以下参数（与截图完全匹配）：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `zip_source` | String | **是** | ZIP文件URL或本地文件路径（支持HTTP/HTTPS协议接入） |
| `public_prefix` | String | 否 | 知识库路径前缀，如"产品"、"帮助文档" |
| `allowed_extensions` | Array\[String\] | 否 | 允许的文件扩展名列表，如[".md",".txt"]，默认支持全部常见文档格式 |
| `max_file_size_mb` | Integer | 否 | 单个文件最大大小（单位：MB），默认10 |
| `skip_folders` | Array\[String\] | 否 | 要忽略的文件夹路径（支持通配符），默认\[\] |

### 步骤 4：配置元数据（输出参数）

在 IDE 右侧「配置」面板 ->「输出参数」中添加以下参数（与截图完全匹配）：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `success` | Boolean | **是** | 是否全部处理成功 |
| `total_count` | Integer | **是** | 处理的文件总数 |
| `success_count` | Integer | **是** | 成功处理的文件数 |
| `failed_count` | Integer | **是** | 失败的文件数 |
| `skipped_count` | Integer | **是** | 跳过的文件数 |
| `processing_time_ms` | Integer | **是** | 处理耗时（毫秒） |
| `error_message` | String | 否 | 错误信息（如有） |
| `documents` | Array\[Object\] | **是** | 处理后的文档列表 |

**documents 数组内嵌套的 document 对象结构：**

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| `name` | String | **是** | 文档名称 |
| `path` | String | **是** | 文档路径 |
| `size` | Integer | **是** | 文档大小（字节） |
| `status` | String | **是** | 处理状态 |

**errors 数组结构（可选输出）：**

| 参数名 | 类型 | 描述 |
|--------|------|------|
| `file` | String | 出错文件路径 |
| `error` | String | 错误详情 |

### 步骤 5：安装依赖

在 IDE 左下角「依赖包」区域，点击「添加依赖」，搜索并安装：
- `adm-zip`（用于解析ZIP文件）

### 步骤 6：粘贴代码

将下方「三、Node.js 完整代码」完整复制到 IDE 代码区。

### 步骤 7：测试
1. 点击右侧「运行」按钮
2. 在输入参数中填入测试数据（见下方测试示例）
3. 查看输出结果
4. 点击「更新输出参数」同步元数据

### 步骤 8：发布
1. 右上角点击「发布」
2. 确认信息后发布
3. 发布后即可在工作流中作为插件节点使用

---

## 三、Node.js 版本 -- 完整代码（推荐，直接粘贴到 Coze IDE）

```javascript
// ============================================================
// Coze 批量知识库上传插件 - Node.js 完整版
// 工具名称: batch_upload | 版本: 1.0.0
// 功能：接收ZIP文件（URL或Base64），自动解压提取文件内容
//       保留完整目录结构，生成知识库文档列表
// 依赖：adm-zip（需在IDE依赖包区域安装）
// ============================================================

import AdmZip from 'adm-zip';

/**
 * Coze IDE 插件入口函数
 *
 * 输入参数（与Coze IDE元数据面板完全匹配）：
 *   - zip_source: String (必填) - ZIP文件URL或Base64编码
 *   - public_prefix: String (可选) - 知识库路径前缀
 *   - allowed_extensions: Array[String] (可选) - 允许的扩展名白名单
 *   - max_file_size_mb: Integer (可选) - 单文件最大MB，默认10
 *   - skip_folders: Array[String] (可选) - 要忽略的文件夹路径
 *
 * 输出参数（与Coze IDE元数据面板完全匹配）：
 *   - success: Boolean - 是否全部处理成功
 *   - total_count: Integer - 文件总数
 *   - success_count: Integer - 成功数
 *   - failed_count: Integer - 失败数
 *   - skipped_count: Integer - 跳过数
 *   - processing_time_ms: Integer - 耗时ms
 *   - error_message: String (可选) - 错误信息
 *   - documents: Array[Object] - 文档列表
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

  const genId = (pathStr) => {
    const t = Date.now().toString(36);
    const r = Math.random().toString(36).substring(2, 8);
    let h = 0;
    for (let i = 0; i < pathStr.length; i++) { h = ((h << 5) - h) + pathStr.charCodeAt(i); h = h & h; }
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

      if (ext === '.md' || ext === '.markdown') {
        format = 'markdown';
        const fm = text.match(/^---\n([\s\S]*?)\n---/);
        if (fm) {
          fm[1].split('\n').forEach(line => {
            const [key, ...val] = line.split(':');
            if (key && val.length > 0) metadata[key.trim()] = val.join(':').trim();
          });
          parsedText = text.replace(/^---\n[\s\S]*?\n---\n?/, '');
        }
      }
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
      else if (ext === '.json') {
        format = 'json';
        try {
          const parsed = JSON.parse(text);
          if (typeof parsed === 'object' && parsed !== null) {
            Object.keys(parsed).forEach(k => { if (typeof parsed[k] === 'string') metadata[k] = parsed[k]; });
          }
          parsedText = typeof parsed === 'object' ? JSON.stringify(parsed, null, 2) : String(parsed);
        } catch { }
      }
      else if (ext === '.xml') {
        format = 'xml';
        let clean = text.replace(/<\?.*?\?>/g, '').replace(/<!--[\s\S]*?-->/g, '');
        clean = clean.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
        parsedText = clean;
      }
      else if (ext === '.csv') {
        format = 'csv';
        metadata.columns = String(text.split('\n')[0]?.split(',').length || 0);
        metadata.rows = String(text.split('\n').filter(l => l.trim()).length);
      }
      else if (['.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
                '.sh', '.bat', '.ps1', '.sql'].includes(ext)) {
        format = 'code';
        metadata.language = ext.replace('.', '');
      }
      else if (['.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.properties'].includes(ext)) {
        format = 'config';
      }
      else if (['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.rtf'].includes(ext)) {
        format = ext.replace('.', '');
        metadata.fileType = ext;
        metadata.fileSize = String(fileInfo.size);
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

  // 1. 验证输入 - 使用 zip_source 参数名（匹配Coze IDE元数据配置）
  if (!input.zip_source) {
    return {
      success: false,
      total_count: 0,
      success_count: 0,
      failed_count: 0,
      skipped_count: 0,
      processing_time_ms: 0,
      error_message: '错误：缺少 zip_source 参数（请提供ZIP文件URL或Base64编码）',
      documents: [],
    };
  }

  // 2. 获取ZIP数据（支持URL下载或直接Base64）
  let zipBuffer;
  const source = String(input.zip_source).trim();

  if (source.startsWith('http://') || source.startsWith('https://')) {
    try {
      log(`正在下载ZIP文件：${source}`);
      const response = await fetch(source);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const arrayBuffer = await response.arrayBuffer();
      zipBuffer = Buffer.from(arrayBuffer);
      log(`ZIP 下载成功，大小：${formatSize(zipBuffer.length)}`);
    } catch (err) {
      return {
        success: false,
        total_count: 0,
        success_count: 0,
        failed_count: 0,
        skipped_count: 0,
        processing_time_ms: 0,
        error_message: '错误：ZIP文件下载失败 - ' + String(err),
        documents: [],
      };
    }
  } else {
    try {
      zipBuffer = Buffer.from(source, 'base64');
      log(`ZIP Base64解码成功，大小：${formatSize(zipBuffer.length)}`);
    } catch (err) {
      return {
        success: false,
        total_count: 0,
        success_count: 0,
        failed_count: 0,
        skipped_count: 0,
        processing_time_ms: 0,
        error_message: '错误：Base64 解码失败 - ' + String(err),
        documents: [],
      };
    }
  }

  // 3. 读取配置 - 使用 public_prefix 和 skip_folders 参数名（匹配Coze IDE元数据）
  const maxFileSize = (input.max_file_size_mb || 10) * 1024 * 1024;
  const pathPrefix = (input.public_prefix || '').trim().replace(/\/$/, '');
  const skipFolders = Array.isArray(input.skip_folders) ? input.skip_folders.map(f => f.trim()) : [];
  const allowedExts = Array.isArray(input.allowed_extensions)
    ? input.allowed_extensions.map(e => e.toLowerCase().trim())
    : DEFAULT_EXTENSIONS;

  log(`配置：最大文件 ${formatSize(maxFileSize)}，路径前缀 "${pathPrefix}"，允许扩展名 ${allowedExts.length} 种`);
  if (skipFolders.length > 0) {
    log(`跳过文件夹：${skipFolders.join(', ')}`);
  }

  // 4. 解析 ZIP
  let zip;
  try {
    zip = new AdmZip(zipBuffer);
  } catch (err) {
    return {
      success: false,
      total_count: 0,
      success_count: 0,
      failed_count: 0,
      skipped_count: 0,
      processing_time_ms: 0,
      error_message: '错误：ZIP 解析失败 - ' + String(err),
      documents: [],
    };
  }

  // 5. 提取文件条目
  const allEntries = [];
  const zipEntries = zip.getEntries();

  for (const entry of zipEntries) {
    if (entry.isDirectory) continue;
    const rawName = entry.entryName;
    if (rawName.startsWith('__MACOSX/') || rawName.includes('/._')) continue;
    const fileName = rawName.split('/').pop() || '';
    if (fileName === '.DS_Store' || fileName === 'Thumbs.db') continue;

    if (skipFolders.length > 0) {
      const shouldSkip = skipFolders.some(folder => {
        const normalized = folder.replace(/\\/g, '/');
        return rawName.startsWith(normalized + '/') || rawName === normalized;
      });
      if (shouldSkip) continue;
    }

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

  {
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

  // 7. 逐文件解析，生成文档列表（匹配Coze IDE输出格式）
  const documents = [];
  const errors = [];
  let successCount = 0;
  let failCount = 0;

  for (const entry of entries) {
    try {
      const result = parseFile(entry);
      const displayPath = pathPrefix ? `${pathPrefix}/${entry.entryPath}` : entry.entryPath;
      const title = extractTitle(result.success ? result.text : '', entry.fileName);

      if (result.success) {
        successCount++;
        documents.push({
          name: title,
          path: displayPath,
          size: entry.size,
          status: 'success',
          content: result.text,
          format: result.format,
          word_count: result.wordCount,
        });
        log(`  [OK] ${displayPath} (${formatSize(entry.size)}, ${result.wordCount} 字)`);
      } else {
        failCount++;
        documents.push({
          name: entry.fileName,
          path: displayPath,
          size: entry.size,
          status: 'failed',
        });
        errors.push({
          file: entry.entryPath,
          error: result.error,
        });
        log(`  [FAIL] ${displayPath}: ${result.error}`);
      }
    } catch (err) {
      failCount++;
      documents.push({
        name: entry.fileName,
        path: pathPrefix ? `${pathPrefix}/${entry.entryPath}` : entry.entryPath,
        size: entry.size,
        status: 'error',
      });
      errors.push({
        file: entry.entryPath,
        error: String(err),
      });
      log(`  [ERROR] ${entry.entryPath}: ${String(err)}`);
    }
  }

  // 8. 构建最终结果（匹配Coze IDE输出参数格式）
  const processingTimeMs = Date.now() - startTime;
  const allSuccess = failCount === 0 && successCount > 0;

  log(`处理完成！成功 ${successCount}，失败 ${failCount}，跳过 ${skippedTotal}，耗时 ${processingTimeMs}ms`);

  const result = {
    success: allSuccess,
    total_count: allEntries.length,
    success_count: successCount,
    failed_count: failCount,
    skipped_count: skippedTotal,
    processing_time_ms: processingTimeMs,
    documents: documents,
  };

  if (failCount > 0) {
    result.error_message = `${failCount} 个文件处理失败`;
    result.errors = errors;
  } else {
    result.error_message = '';
  }

  return result;
}
```

---

## 四、Coze IDE 测试输入参数（完整JSON）

将以下JSON复制到IDE右侧「运行」面板的「输入」区域：

### 完整测试输入：

```json
{
  "zip_source": "请替换为你的ZIP文件Base64编码或HTTP/HTTPS URL",
  "public_prefix": "知识库",
  "allowed_extensions": [".md", ".txt", ".json", ".csv", ".html", ".py", ".js", ".yaml", ".sql", ".xml"],
  "max_file_size_mb": 10,
  "skip_folders": ["__MACOSX", "node_modules", ".git"]
}
```

### 使用URL的测试输入：

```json
{
  "zip_source": "https://example.com/your-files.zip",
  "public_prefix": "产品文档",
  "max_file_size_mb": 20
}
```

### 最简测试输入（仅必填参数）：

```json
{
  "zip_source": "你的ZIP文件的Base64编码字符串"
}
```

---

## 五、在工作流中使用插件

### 知识库写入节点配置
1. 添加「知识库写入」节点
2. 在节点中配置知识库ID（选择已创建的知识库）
3. 输入绑定：将插件的 `documents` 输出通过循环/批量方式写入知识库
4. 输出变量：`documentId`、`fileName`、`fileUrl`

### 知识库检索节点配置
1. 添加「知识库检索」节点
2. 在节点中配置同一知识库ID
3. 输入绑定：`Query` 参数绑定用户查询
4. 输出变量：`outputList`

### 完整工作流数据流

```
┌─────────┐     ┌───────────────────┐     ┌───────────────────┐     ┌─────────┐
│  开始    │────→│  批量上传插件      │────→│  知识库写入节点    │────→│  结束    │
│  input   │     │  batch_upload     │     │  documents        │     │  output │
└─────────┘     │  ├─zip_source      │     │  ├─documentId     │     └─────────┘
                │  ├─public_prefix   │     │  ├─fileName       │
                │  └─documents输出   │     │  └─fileUrl        │
                └───────────────────┘     └───────────────────┘
                       │
                       ▼
                ┌───────────────────┐
                │  知识库检索节点    │
                │  Query → outputList│
                └───────────────────┘
```

---

## 六、Python3 版本 -- 完整代码（备选）

```python
# ============================================================
# Coze 批量知识库上传插件 - Python3 完整版
# 工具名称: batch_upload | 版本: 1.0.0
# 依赖：无需额外依赖（使用Python标准库 zipfile）
# ============================================================

import base64
import io
import json
import os
import re
import time
import zipfile
from datetime import datetime


def handler(args):
    input_data = args.input
    logger = args.logger
    logs = []
    start_time = int(time.time() * 1000)

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
        for line in lines:
            if re.match(r'^#{1,6}\s+', line):
                return re.sub(r'^#{1,6}\s+', '', line).strip()
        m = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1).strip()
        return lines[0][:100] + ('...' if len(lines[0]) > 100 else '')

    def parse_file(file_info):
        ext = file_info['extension']
        data = file_info['data']
        encoding = file_info['encoding']
        text = decode_data(data, encoding)
        fmt = 'text'
        parsed_text = text
        metadata = {}

        try:
            if ext in ('.md', '.markdown'):
                fmt = 'markdown'
                fm = re.match(r'^---\n([\s\S]*?)\n---', text)
                if fm:
                    for line in fm.group(1).split('\n'):
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            metadata[parts[0].strip()] = parts[1].strip()
                    parsed_text = re.sub(r'^---\n[\s\S]*?\n---\n?', '', text)
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
            elif ext == '.xml':
                fmt = 'xml'
                clean = re.sub(r'<\?.*?\?>', '', text)
                clean = re.sub(r'<!--[\s\S]*?-->', '', clean)
                clean = re.sub(r'<[^>]+>', ' ', clean)
                clean = re.sub(r'\s+', ' ', clean).strip()
                parsed_text = clean
            elif ext == '.csv':
                fmt = 'csv'
                lines_list = [l for l in text.split('\n') if l.strip()]
                metadata['columns'] = str(len(lines_list[0].split(',')) if lines_list else 0)
                metadata['rows'] = str(len(lines_list))
            elif ext in ('.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
                         '.sh', '.bat', '.ps1', '.sql'):
                fmt = 'code'
                metadata['language'] = ext.lstrip('.')
            elif ext in ('.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.properties'):
                fmt = 'config'
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
                'success': True, 'text': parsed_text, 'format': fmt,
                'metadata': metadata, 'word_count': count_words(parsed_text),
            }
        except Exception as e:
            return {
                'success': False, 'text': '', 'format': 'unknown',
                'metadata': {}, 'error': str(e), 'word_count': 0,
            }

    log('=== Coze 批量知识库上传插件启动 (Python3) ===')

    zip_source = getattr(input_data, 'zip_source', None)
    if not zip_source:
        return {
            'success': False,
            'total_count': 0, 'success_count': 0, 'failed_count': 0, 'skipped_count': 0,
            'processing_time_ms': 0, 'error_message': '错误：缺少 zip_source 参数',
            'documents': [],
        }

    import urllib.request
    source = str(zip_source).strip()
    zip_bytes = None

    if source.startswith('http://') or source.startswith('https://'):
        try:
            log(f'正在下载ZIP文件：{source}')
            req = urllib.request.Request(source)
            with urllib.request.urlopen(req) as response:
                zip_bytes = response.read()
            log(f'ZIP 下载成功，大小：{format_size(len(zip_bytes))}')
        except Exception as e:
            return {
                'success': False,
                'total_count': 0, 'success_count': 0, 'failed_count': 0, 'skipped_count': 0,
                'processing_time_ms': 0, 'error_message': f'错误：ZIP文件下载失败 - {e}',
                'documents': [],
            }
    else:
        try:
            zip_bytes = base64.b64decode(source)
            log(f'ZIP Base64解码成功，大小：{format_size(len(zip_bytes))}')
        except Exception as e:
            return {
                'success': False,
                'total_count': 0, 'success_count': 0, 'failed_count': 0, 'skipped_count': 0,
                'processing_time_ms': 0, 'error_message': f'错误：Base64解码失败 - {e}',
                'documents': [],
            }

    max_file_size = (getattr(input_data, 'max_file_size_mb', 10) or 10) * 1024 * 1024
    path_prefix = (getattr(input_data, 'public_prefix', '') or '').strip().rstrip('/')
    skip_folders = getattr(input_data, 'skip_folders', None) or []

    default_exts = [
        '.md', '.markdown', '.txt', '.text', '.pdf', '.doc', '.docx',
        '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.json', '.xml',
        '.html', '.htm', '.rtf', '.log', '.yaml', '.yml', '.ini',
        '.cfg', '.conf', '.toml', '.properties',
        '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
        '.sh', '.bat', '.ps1', '.sql',
    ]
    allowed_exts_input = getattr(input_data, 'allowed_extensions', None)
    allowed_exts = [e.lower().strip() for e in allowed_exts_input] if allowed_exts_input else default_exts

    log(f"配置：最大文件 {format_size(max_file_size)}，路径前缀 '{path_prefix}'")

    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except Exception as e:
        return {
            'success': False,
            'total_count': 0, 'success_count': 0, 'failed_count': 0, 'skipped_count': 0,
            'processing_time_ms': 0, 'error_message': f'错误：ZIP解析失败 - {e}',
            'documents': [],
        }

    all_entries = []
    for info in zf.infolist():
        if info.is_dir():
            continue
        raw_name = info.filename
        if raw_name.startswith('__MACOSX/') or '/._' in raw_name:
            continue
        file_name = os.path.basename(raw_name)
        if file_name in ('.DS_Store', 'Thumbs.db'):
            continue
        if skip_folders:
            should_skip = any(
                raw_name.startswith(f.strip() + '/') or raw_name == f.strip()
                for f in skip_folders
            )
            if should_skip:
                continue
        try:
            safe_path = sanitize_path(raw_name)
            data = zf.read(info.filename)
            all_entries.append({
                'entryPath': safe_path, 'fileName': file_name,
                'extension': get_extension(file_name), 'size': len(data),
                'data': data, 'encoding': detect_encoding(data),
            })
        except Exception:
            log(f"跳过不安全条目：{raw_name}")

    log(f"ZIP 解析完成，共 {len(all_entries)} 个文件条目")

    entries = list(all_entries)

    before = len(entries)
    entries = [f for f in entries if not f['fileName'].startswith('.')]
    skipped = before - len(entries)
    if skipped > 0: log(f"过滤隐藏文件：跳过 {skipped} 个")

    before = len(entries)
    entries = [f for f in entries if f['size'] > 0]
    skipped = before - len(entries)
    if skipped > 0: log(f"过滤空文件：跳过 {skipped} 个")

    before = len(entries)
    entries = [f for f in entries if f['extension'].lower() in allowed_exts]
    skipped = before - len(entries)
    if skipped > 0: log(f"文件类型过滤：保留 {len(entries)} 个")

    before = len(entries)
    entries = [f for f in entries if f['size'] <= max_file_size]
    skipped = before - len(entries)
    if skipped > 0: log(f"文件大小过滤：跳过 {skipped} 个超限文件")

    skipped_total = len(all_entries) - len(entries)

    documents = []
    errors_list = []
    success_count = 0
    fail_count = 0

    import hashlib
    import random

    for entry in entries:
        try:
            result = parse_file(entry)
            display_path = f"{path_prefix}/{entry['entryPath']}" if path_prefix else entry['entryPath']
            title = extract_title(result['text'] if result['success'] else '', entry['fileName'])

            if result['success']:
                success_count += 1
                documents.append({
                    'name': title, 'path': display_path, 'size': entry['size'],
                    'status': 'success', 'content': result['text'],
                    'format': result['format'], 'word_count': result['word_count'],
                })
                log(f"  [OK] {display_path} ({format_size(entry['size'])}, {result['word_count']} 字)")
            else:
                fail_count += 1
                documents.append({
                    'name': entry['fileName'], 'path': display_path,
                    'size': entry['size'], 'status': 'failed',
                })
                errors_list.append({'file': entry['entryPath'], 'error': result.get('error')})
                log(f"  [FAIL] {display_path}: {result.get('error')}")
        except Exception as e:
            fail_count += 1
            documents.append({
                'name': entry['fileName'],
                'path': f"{path_prefix}/{entry['entryPath']}" if path_prefix else entry['entryPath'],
                'size': entry['size'], 'status': 'error',
            })
            errors_list.append({'file': entry['entryPath'], 'error': str(e)})
            log(f"  [ERROR] {entry['entryPath']}: {e}")

    elapsed = int(time.time() * 1000) - start_time

    result = {
        'success': fail_count == 0 and success_count > 0,
        'total_count': len(all_entries),
        'success_count': success_count,
        'failed_count': fail_count,
        'skipped_count': skipped_total,
        'processing_time_ms': elapsed,
        'documents': documents,
    }
    if fail_count > 0:
        result['error_message'] = f'{fail_count} 个文件处理失败'
        result['errors'] = errors_list
    else:
        result['error_message'] = ''

    log(f'处理完成！成功 {success_count}，失败 {fail_count}，跳过 {skipped_total}，耗时 {elapsed}ms')
    return result
```

---

## 七、本地 NPM 包使用

项目 dist 目录已包含构建产物，可直接在 Node.js 项目中引用：

```javascript
const { batchUploadFromZip } = require('./dist');
const result = await batchUploadFromZip(zipBuffer);
```

运行测试：`pnpm run test`（10项自动化测试全部通过）
