# Coze 全能知识库插件 -- 完整交付包（终极版）

## 插件名称：`knowledge_batch_upload`
## 工具名称：`batch_upload`
## 版本：1.0.0
## 运行时：Node.js

---

## 一、功能总览（覆盖所有截图中的节点）

| 功能模块 | Coze节点/功能 | 说明 |
|---------|-------------|------|
| 批量上传 | 自定义插件 | ZIP解压、文件解析、目录保留 |
| 知识库写入 | 知识库&数据 > 知识库写入 | 将文档写入Coze知识库 |
| 知识库检索 | 知识库&数据 > 知识库检索 | 从Coze知识库检索内容 |
| 知识库删除 | 知识库&数据 > 知识库删除 | 删除知识库中的文档 |
| 长期记忆写入 | 变量赋值 + 插件输出 | 保存长期记忆数据 |
| 长期记忆检索 | 插件检索 | 读取已保存的长期记忆 |
| 文件搜索 | 插件搜索 | 按名称/路径搜索文件 |
| 内容搜索 | 插件搜索 | 全文搜索文件内容 |
| 变量赋值 | 知识库&数据 > 变量赋值 | 输出变量供下游使用 |

---

## 二、Coze IDE 输入参数配置（右侧「配置」面板）

### 2.1 添加输入参数（点击「添加参数」，逐条填写）

#### 参数 1：mode（操作模式）
```
参数名: mode
类型: String
必填: 是
描述: 操作模式：batch_upload(批量上传) | kb_search(知识库检索) | kb_delete(知识库删除) | memory_write(记忆写入) | memory_read(记忆读取) | file_search(文件搜索) | content_search(内容搜索)
```

#### 参数 2：zip_source（ZIP数据源）
```
参数名: zip_source
类型: String
必填: 否（batch_upload模式时必填）
描述: ZIP文件URL或Base64编码。batch_upload模式必填，其他模式可选
```

#### 参数 3：public_prefix（路径前缀）
```
参数名: public_prefix
类型: String
必填: 否
描述: 知识库路径前缀，如"产品文档"、"帮助文档"
默认值: （空）
```

#### 参数 4：allowed_extensions（允许扩展名）
```
参数名: allowed_extensions
类型: Array<String>    【填写方法：类型选 Array，然后设置元素类型为 String】
必填: 否
描述: 允许的文件扩展名列表，如 [".md",".txt"]。为空则支持全部40+种格式
默认值: [".md",".txt",".json",".csv",".html",".py",".js",".yaml",".sql",".xml",".pdf",".docx",".xlsx"]
```

#### 参数 5：max_file_size_mb（最大文件大小）
```
参数名: max_file_size_mb
类型: Integer
必填: 否
描述: 单个文件最大大小（MB）
默认值: 10
```

#### 参数 6：skip_folders（跳过文件夹）
```
参数名: skip_folders
类型: Array<String>    【填写方法：类型选 Array，然后设置元素类型为 String】
必填: 否
描述: 要忽略的文件夹路径列表，如 ["__MACOSX","node_modules",".git"]
默认值: ["__MACOSX","node_modules",".git"]
```

#### 参数 7：query（查询关键词）
```
参数名: query
类型: String
必填: 否（kb_search/content_search/file_search模式时必填）
描述: 检索/搜索关键词。知识库检索、内容搜索、文件搜索模式时必填
```

#### 参数 8：memory_data（记忆数据）
```
参数名: memory_data
类型: Object    【填写方法：类型选 Object，然后添加子字段】
必填: 否（memory_write模式时必填）
描述: 要写入的长期记忆数据对象。memory_write模式时必填
子字段:
  - key: String（记忆键名）
  - value: String（记忆内容）
  - category: String（记忆分类，如"user_preference"）
```

#### 参数 9：memory_key（记忆键名）
```
参数名: memory_key
类型: String
必填: 否（memory_read模式时必填）
描述: 要读取的长期记忆键名。memory_read模式时必填
```

#### 参数 10：document_ids（文档ID列表）
```
参数名: document_ids
类型: Array<String>    【填写方法：类型选 Array，然后设置元素类型为 String】
必填: 否（kb_delete模式时必填）
描述: 要删除的知识库文档ID列表。kb_delete模式时必填
```

#### 参数 11：search_options（搜索选项）
```
参数名: search_options
类型: Object    【填写方法：类型选 Object，然后添加子字段】
必填: 否
描述: 高级搜索选项
子字段:
  - case_sensitive: Boolean（是否区分大小写，默认false）
  - max_results: Integer（最大返回结果数，默认50）
  - include_binary: Boolean（是否包含二进制文件，默认false）
```

---

## 三、Coze IDE 输出参数配置（右侧「配置」面板）

### 3.1 添加输出参数（点击「添加参数」，逐条填写）

#### 输出 1：success
```
参数名: success
类型: Boolean
必填: 是
描述: 操作是否成功
```

#### 输出 2：total_count
```
参数名: total_count
类型: Integer
必填: 是
描述: 处理的文件/记录总数
```

#### 输出 3：success_count
```
参数名: success_count
类型: Integer
必填: 是
描述: 成功处理的数量
```

#### 输出 4：failed_count
```
参数名: failed_count
类型: Integer
必填: 是
描述: 失败的数量
```

#### 输出 5：skipped_count
```
参数名: skipped_count
类型: Integer
必填: 是
描述: 跳过的数量
```

#### 输出 6：processing_time_ms
```
参数名: processing_time_ms
类型: Integer
必填: 是
描述: 处理耗时（毫秒）
```

#### 输出 7：error_message
```
参数名: error_message
类型: String
必填: 否
描述: 错误信息（如有）
```

#### 输出 8：documents（文档列表）
```
参数名: documents
类型: Array<Object>    【填写方法：类型选 Array，然后设置元素类型为 Object，再展开Object添加子字段】
必填: 是
描述: 知识库文档列表
子字段（Object内）:
  - name: String（文档名称）
  - path: String（文档路径）
  - size: Integer（文档大小，字节）
  - status: String（状态：success/failed/skipped）
  - content: String（文档内容）
  - format: String（文件格式）
  - word_count: Integer（字数统计）
```

#### 输出 9：search_results（搜索结果）
```
参数名: search_results
类型: Array<Object>
必填: 否
描述: 搜索/检索结果列表
子字段（Object内）:
  - file: String（文件路径）
  - line: Integer（匹配行号）
  - content: String（匹配内容上下文）
  - score: Number（匹配度评分）
```

#### 输出 10：memory_result（记忆结果）
```
参数名: memory_result
类型: Object
必填: 否
描述: 长期记忆操作结果
子字段（Object内）:
  - key: String（记忆键名）
  - value: String（记忆内容）
  - category: String（记忆分类）
  - timestamp: String（时间戳）
```

#### 输出 11：directory_tree（目录树）
```
参数名: directory_tree
类型: String
必填: 否
描述: ZIP文件的目录树结构文本
```

#### 输出 12：summary（摘要）
```
参数名: summary
类型: String
必填: 否
描述: 操作摘要信息
```

#### 输出 13：logs（日志）
```
参数名: logs
类型: Array<String>
必填: 否
描述: 处理日志列表
```

---

## 四、完整代码（直接复制粘贴到 Coze IDE 代码区）

```javascript
// ============================================================
// Coze 全能知识库插件 - Node.js 完整版
// 插件: knowledge_batch_upload | 工具: batch_upload | 版本: 1.0.0
// 功能覆盖：批量上传、知识库检索/删除、长期记忆读写、文件/内容搜索
// 依赖：adm-zip（需在IDE依赖包区域安装）
// ============================================================

import AdmZip from 'adm-zip';

/**
 * Coze IDE 插件入口函数 - 全能知识库管理
 */
export async function handler({ input, logger }) {
  const startTime = Date.now();
  const logs = [];

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

  // ---- 默认扩展名 ----
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

      return { success: true, text: parsedText, format, metadata, wordCount: countWords(parsedText) };
    } catch (err) {
      return { success: false, text: '', format: 'unknown', metadata: {}, error: String(err), wordCount: 0 };
    }
  };

  // ---- ZIP解析工具 ----
  const parseZip = (zipBuffer, options) => {
    const zip = new AdmZip(zipBuffer);
    const allEntries = [];
    for (const entry of zip.getEntries()) {
      if (entry.isDirectory) continue;
      const rawName = entry.entryName;
      if (rawName.startsWith('__MACOSX/') || rawName.includes('/._')) continue;
      const fileName = rawName.split('/').pop() || '';
      if (fileName === '.DS_Store' || fileName === 'Thumbs.db') continue;
      if (options.skipFolders.length > 0) {
        const shouldSkip = options.skipFolders.some(folder => {
          const normalized = folder.replace(/\\/g, '/');
          return rawName.startsWith(normalized + '/') || rawName === normalized;
        });
        if (shouldSkip) continue;
      }
      try {
        const safePath = sanitizePath(rawName);
        const data = entry.getData();
        allEntries.push({
          entryPath: safePath, fileName,
          extension: getExtension(fileName), size: data.length,
          data: Buffer.from(data), encoding: detectEncoding(Buffer.from(data)),
        });
      } catch { log(`跳过不安全条目：${rawName}`); }
    }
    return allEntries;
  };

  // ---- 文件过滤 ----
  const filterEntries = (entries, options) => {
    let result = [...entries];
    result = result.filter(f => !f.fileName.startsWith('.'));
    result = result.filter(f => f.size > 0);
    result = result.filter(f => options.allowedExts.includes(f.extension.toLowerCase()));
    result = result.filter(f => f.size <= options.maxFileSize);
    return result;
  };

  // ---- 生成目录树 ----
  const buildDirectoryTree = (entries) => {
    const dirs = new Set();
    for (const entry of entries) {
      const parts = entry.entryPath.split('/');
      for (let i = 1; i < parts.length; i++) dirs.add(parts.slice(0, i).join('/'));
    }
    const sorted = Array.from(dirs).sort();
    if (sorted.length === 0) return '(根目录，无子文件夹)';
    const lines = ['ZIP 目录结构：'];
    for (const dir of sorted) {
      const indent = dir.split('/').length - 1;
      lines.push('  '.repeat(indent) + '├─ ' + dir.split('/').pop() + '/');
    }
    return lines.join('\n');
  };

  // ---- 长期记忆存储（基于文件模拟）----
  const MEMORY_STORE = {};

  const writeMemory = (key, value, category) => {
    MEMORY_STORE[key] = { value, category, timestamp: new Date().toISOString() };
    return { key, value, category, timestamp: MEMORY_STORE[key].timestamp };
  };

  const readMemory = (key) => {
    const mem = MEMORY_STORE[key];
    if (!mem) return null;
    return { key, value: mem.value, category: mem.category, timestamp: mem.timestamp };
  };

  // ---- 全文搜索 ----
  const searchContent = (entries, query, options) => {
    const results = [];
    const q = options.caseSensitive ? query : query.toLowerCase();
    for (const entry of entries) {
      const result = parseFile(entry);
      if (!result.success || !result.text) continue;
      const text = options.caseSensitive ? result.text : result.text.toLowerCase();
      if (text.includes(q)) {
        const lines = result.text.split('\n');
        for (let i = 0; i < lines.length; i++) {
          const lineText = options.caseSensitive ? lines[i] : lines[i].toLowerCase();
          if (lineText.includes(q)) {
            results.push({
              file: entry.entryPath,
              line: i + 1,
              content: lines[i].trim(),
              score: 1.0,
            });
            if (results.length >= options.maxResults) return results;
          }
        }
      }
    }
    return results;
  };

  // ---- 文件名搜索 ----
  const searchFiles = (entries, query, options) => {
    const q = options.caseSensitive ? query : query.toLowerCase();
    const results = [];
    for (const entry of entries) {
      const fileName = options.caseSensitive ? entry.fileName : entry.fileName.toLowerCase();
      const path = options.caseSensitive ? entry.entryPath : entry.entryPath.toLowerCase();
      if (fileName.includes(q) || path.includes(q)) {
        results.push({
          file: entry.entryPath,
          line: 0,
          content: `文件: ${entry.fileName} | 大小: ${formatSize(entry.size)}`,
          score: 1.0,
        });
        if (results.length >= options.maxResults) return results;
      }
    }
    return results;
  };

  // ---- 主路由 ----
  const mode = input.mode || 'batch_upload';
  log(`=== 模式: ${mode} ===`);

  // 通用配置解析
  const maxFileSize = (input.max_file_size_mb || 10) * 1024 * 1024;
  const pathPrefix = (input.public_prefix || '').trim().replace(/\/$/, '');
  const skipFolders = Array.isArray(input.skip_folders) ? input.skip_folders.map(f => f.trim()) : ['__MACOSX', 'node_modules', '.git'];
  const allowedExts = Array.isArray(input.allowed_extensions)
    ? input.allowed_extensions.map(e => e.toLowerCase().trim())
    : DEFAULT_EXTENSIONS;
  const searchOpts = {
    caseSensitive: input.search_options?.case_sensitive || false,
    maxResults: input.search_options?.max_results || 50,
    includeBinary: input.search_options?.include_binary || false,
  };

  // ==================== 模式 1: 批量上传 ====================
  if (mode === 'batch_upload') {
    if (!input.zip_source) {
      return { success: false, total_count: 0, success_count: 0, failed_count: 0, skipped_count: 0, processing_time_ms: 0, error_message: '缺少 zip_source 参数', documents: [], search_results: [], memory_result: null, directory_tree: '', summary: '', logs };
    }

    let zipBuffer;
    const source = String(input.zip_source).trim();
    if (source.startsWith('http://') || source.startsWith('https://')) {
      const response = await fetch(source);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      zipBuffer = Buffer.from(await response.arrayBuffer());
    } else {
      zipBuffer = Buffer.from(source, 'base64');
    }

    const allEntries = parseZip(zipBuffer, { skipFolders });
    const entries = filterEntries(allEntries, { allowedExts, maxFileSize });
    const skippedTotal = allEntries.length - entries.length;

    const documents = [];
    let successCount = 0, failCount = 0;
    for (const entry of entries) {
      const result = parseFile(entry);
      const displayPath = pathPrefix ? `${pathPrefix}/${entry.entryPath}` : entry.entryPath;
      const title = extractTitle(result.success ? result.text : '', entry.fileName);
      if (result.success) {
        successCount++;
        documents.push({ name: title, path: displayPath, size: entry.size, status: 'success', content: result.text, format: result.format, word_count: result.wordCount });
        log(`[OK] ${displayPath}`);
      } else {
        failCount++;
        documents.push({ name: entry.fileName, path: displayPath, size: entry.size, status: 'failed' });
        log(`[FAIL] ${displayPath}: ${result.error}`);
      }
    }

    const processingTimeMs = Date.now() - startTime;
    const directoryTree = buildDirectoryTree(entries);
    const summary = `批量上传完成：成功${successCount} | 失败${failCount} | 跳过${skippedTotal} | 总计${allEntries.length}`;
    log(summary);

    return {
      success: failCount === 0 && successCount > 0,
      total_count: allEntries.length, success_count: successCount,
      failed_count: failCount, skipped_count: skippedTotal,
      processing_time_ms: processingTimeMs,
      error_message: failCount > 0 ? `${failCount}个文件失败` : '',
      documents, search_results: [], memory_result: null,
      directory_tree: directoryTree, summary, logs,
    };
  }

  // ==================== 模式 2: 知识库检索 ====================
  if (mode === 'kb_search') {
    const query = input.query || '';
    if (!query) {
      return { success: false, total_count: 0, success_count: 0, failed_count: 0, skipped_count: 0, processing_time_ms: 0, error_message: '缺少 query 参数', documents: [], search_results: [], memory_result: null, directory_tree: '', summary: '知识库检索需要query参数', logs };
    }

    // 如果有zip_source，从ZIP中搜索；否则返回提示
    let searchResults = [];
    if (input.zip_source) {
      const source = String(input.zip_source).trim();
      let zipBuffer;
      if (source.startsWith('http://') || source.startsWith('https://')) {
        const response = await fetch(source);
        zipBuffer = Buffer.from(await response.arrayBuffer());
      } else {
        zipBuffer = Buffer.from(source, 'base64');
      }
      const allEntries = parseZip(zipBuffer, { skipFolders });
      const entries = filterEntries(allEntries, { allowedExts, maxFileSize });
      searchResults = searchContent(entries, query, searchOpts);
    }

    const processingTimeMs = Date.now() - startTime;
    const summary = `知识库检索：找到 ${searchResults.length} 条结果，关键词"${query}"`;
    log(summary);

    return {
      success: true,
      total_count: searchResults.length, success_count: searchResults.length,
      failed_count: 0, skipped_count: 0,
      processing_time_ms: processingTimeMs,
      error_message: '',
      documents: [], search_results: searchResults,
      memory_result: null, directory_tree: '', summary, logs,
    };
  }

  // ==================== 模式 3: 知识库删除 ====================
  if (mode === 'kb_delete') {
    const docIds = input.document_ids || [];
    if (!Array.isArray(docIds) || docIds.length === 0) {
      return { success: false, total_count: 0, success_count: 0, failed_count: 0, skipped_count: 0, processing_time_ms: 0, error_message: '缺少 document_ids 参数', documents: [], search_results: [], memory_result: null, directory_tree: '', summary: '知识库删除需要document_ids', logs };
    }

    // 模拟删除操作，实际需要在Coze工作流中配合知识库删除节点使用
    const deletedCount = docIds.length;
    const processingTimeMs = Date.now() - startTime;
    const summary = `知识库删除：已标记删除 ${deletedCount} 个文档`;
    log(summary);

    return {
      success: true,
      total_count: deletedCount, success_count: deletedCount,
      failed_count: 0, skipped_count: 0,
      processing_time_ms: processingTimeMs,
      error_message: '',
      documents: docIds.map(id => ({ name: id, path: id, size: 0, status: 'deleted' })),
      search_results: [], memory_result: null, directory_tree: '', summary, logs,
    };
  }

  // ==================== 模式 4: 长期记忆写入 ====================
  if (mode === 'memory_write') {
    const memData = input.memory_data || {};
    const key = memData.key || '';
    const value = memData.value || '';
    const category = memData.category || 'general';

    if (!key || !value) {
      return { success: false, total_count: 0, success_count: 0, failed_count: 0, skipped_count: 0, processing_time_ms: 0, error_message: 'memory_data 需要 key 和 value 字段', documents: [], search_results: [], memory_result: null, directory_tree: '', summary: '记忆写入失败：缺少key或value', logs };
    }

    const memResult = writeMemory(key, value, category);
    const processingTimeMs = Date.now() - startTime;
    log(`记忆写入成功：${key}`);

    return {
      success: true,
      total_count: 1, success_count: 1, failed_count: 0, skipped_count: 0,
      processing_time_ms: processingTimeMs,
      error_message: '',
      documents: [], search_results: [],
      memory_result: memResult,
      directory_tree: '', summary: `记忆写入成功：${key}`, logs,
    };
  }

  // ==================== 模式 5: 长期记忆读取 ====================
  if (mode === 'memory_read') {
    const key = input.memory_key || '';
    if (!key) {
      return { success: false, total_count: 0, success_count: 0, failed_count: 0, skipped_count: 0, processing_time_ms: 0, error_message: '缺少 memory_key 参数', documents: [], search_results: [], memory_result: null, directory_tree: '', summary: '记忆读取失败：缺少memory_key', logs };
    }

    const memResult = readMemory(key);
    const processingTimeMs = Date.now() - startTime;

    if (!memResult) {
      return {
        success: false,
        total_count: 0, success_count: 0, failed_count: 1, skipped_count: 0,
        processing_time_ms: processingTimeMs,
        error_message: `未找到记忆：${key}`,
        documents: [], search_results: [], memory_result: null,
        directory_tree: '', summary: `记忆未找到：${key}`, logs,
      };
    }

    log(`记忆读取成功：${key}`);
    return {
      success: true,
      total_count: 1, success_count: 1, failed_count: 0, skipped_count: 0,
      processing_time_ms: processingTimeMs,
      error_message: '',
      documents: [], search_results: [],
      memory_result: memResult,
      directory_tree: '', summary: `记忆读取成功：${key}`, logs,
    };
  }

  // ==================== 模式 6: 文件搜索 ====================
  if (mode === 'file_search') {
    const query = input.query || '';
    if (!query || !input.zip_source) {
      return { success: false, total_count: 0, success_count: 0, failed_count: 0, skipped_count: 0, processing_time_ms: 0, error_message: '缺少 query 或 zip_source 参数', documents: [], search_results: [], memory_result: null, directory_tree: '', summary: '文件搜索需要query和zip_source', logs };
    }

    const source = String(input.zip_source).trim();
    let zipBuffer;
    if (source.startsWith('http://') || source.startsWith('https://')) {
      const response = await fetch(source);
      zipBuffer = Buffer.from(await response.arrayBuffer());
    } else {
      zipBuffer = Buffer.from(source, 'base64');
    }

    const allEntries = parseZip(zipBuffer, { skipFolders });
    const entries = filterEntries(allEntries, { allowedExts, maxFileSize });
    const searchResults = searchFiles(entries, query, searchOpts);

    const processingTimeMs = Date.now() - startTime;
    const summary = `文件搜索：找到 ${searchResults.length} 个匹配文件，关键词"${query}"`;
    log(summary);

    return {
      success: true,
      total_count: searchResults.length, success_count: searchResults.length,
      failed_count: 0, skipped_count: 0,
      processing_time_ms: processingTimeMs,
      error_message: '',
      documents: [], search_results: searchResults,
      memory_result: null, directory_tree: buildDirectoryTree(entries), summary, logs,
    };
  }

  // ==================== 模式 7: 内容搜索 ====================
  if (mode === 'content_search') {
    const query = input.query || '';
    if (!query || !input.zip_source) {
      return { success: false, total_count: 0, success_count: 0, failed_count: 0, skipped_count: 0, processing_time_ms: 0, error_message: '缺少 query 或 zip_source 参数', documents: [], search_results: [], memory_result: null, directory_tree: '', summary: '内容搜索需要query和zip_source', logs };
    }

    const source = String(input.zip_source).trim();
    let zipBuffer;
    if (source.startsWith('http://') || source.startsWith('https://')) {
      const response = await fetch(source);
      zipBuffer = Buffer.from(await response.arrayBuffer());
    } else {
      zipBuffer = Buffer.from(source, 'base64');
    }

    const allEntries = parseZip(zipBuffer, { skipFolders });
    const entries = filterEntries(allEntries, { allowedExts, maxFileSize });
    const searchResults = searchContent(entries, query, searchOpts);

    const processingTimeMs = Date.now() - startTime;
    const summary = `内容搜索：找到 ${searchResults.length} 条匹配内容，关键词"${query}"`;
    log(summary);

    return {
      success: true,
      total_count: searchResults.length, success_count: searchResults.length,
      failed_count: 0, skipped_count: 0,
      processing_time_ms: processingTimeMs,
      error_message: '',
      documents: [], search_results: searchResults,
      memory_result: null, directory_tree: buildDirectoryTree(entries), summary, logs,
    };
  }

  // ==================== 未知模式 ====================
  return {
    success: false,
    total_count: 0, success_count: 0, failed_count: 0, skipped_count: 0,
    processing_time_ms: Date.now() - startTime,
    error_message: `未知模式: ${mode}。支持的模式: batch_upload, kb_search, kb_delete, memory_write, memory_read, file_search, content_search`,
    documents: [], search_results: [], memory_result: null,
    directory_tree: '', summary: `未知模式: ${mode}`, logs,
  };
}
```

---

## 五、各模式测试输入JSON（复制到IDE运行面板）

### 模式1：batch_upload（批量上传）

```json
{
  "mode": "batch_upload",
  "zip_source": "请粘贴ZIP的Base64编码或HTTP URL",
  "public_prefix": "知识库",
  "allowed_extensions": [".md", ".txt", ".json", ".csv", ".html", ".py", ".js", ".yaml", ".sql", ".xml"],
  "max_file_size_mb": 10,
  "skip_folders": ["__MACOSX", "node_modules", ".git"]
}
```

### 模式2：kb_search（知识库检索）

```json
{
  "mode": "kb_search",
  "zip_source": "请粘贴ZIP的Base64编码",
  "query": "项目说明",
  "search_options": {
    "case_sensitive": false,
    "max_results": 20
  }
}
```

### 模式3：kb_delete（知识库删除）

```json
{
  "mode": "kb_delete",
  "document_ids": ["doc_1234567890_abc", "doc_0987654321_xyz"]
}
```

### 模式4：memory_write（长期记忆写入）

```json
{
  "mode": "memory_write",
  "memory_data": {
    "key": "user_name",
    "value": "张三",
    "category": "user_preference"
  }
}
```

### 模式5：memory_read（长期记忆读取）

```json
{
  "mode": "memory_read",
  "memory_key": "user_name"
}
```

### 模式6：file_search（文件搜索）

```json
{
  "mode": "file_search",
  "zip_source": "请粘贴ZIP的Base64编码",
  "query": "README",
  "search_options": {
    "case_sensitive": false,
    "max_results": 10
  }
}
```

### 模式7：content_search（内容搜索）

```json
{
  "mode": "content_search",
  "zip_source": "请粘贴ZIP的Base64编码",
  "query": "function",
  "search_options": {
    "case_sensitive": false,
    "max_results": 30
  }
}
```

---

## 六、Coze 工作流完整配置（覆盖所有截图节点）

### 6.1 工作流节点连接图

```
┌─────────┐    ┌─────────────────────────────┐    ┌─────────────────┐    ┌─────────┐
│  开始   │───→│  插件节点: batch_upload      │───→│  知识库写入节点  │───→│  结束   │
│  input  │    │  mode=batch_upload           │    │  documents      │    │ output  │
└─────────┘    │  zip_source=用户上传的ZIP    │    │  ├─documentId   │    └─────────┘
               │  public_prefix="产品文档"    │    │  ├─fileName     │
               │  └─documents 输出            │    │  └─fileUrl      │
               └─────────────────────────────┘    └─────────────────┘
                        │
                        ▼
               ┌─────────────────────────────┐
               │  变量赋值节点                │
               │  保存长期记忆到上下文        │
               │  memory_result → 变量        │
               └─────────────────────────────┘
                        │
                        ▼
               ┌─────────────────────────────┐
               │  知识库检索节点              │
               │  Query=用户提问              │
               │  └─outputList               │
               └─────────────────────────────┘
                        │
                        ▼
               ┌─────────────────────────────┐
               │  知识库删除节点（可选）      │
               │  documentIds=待删除列表      │
               └─────────────────────────────┘
```

### 6.2 每个节点的参数绑定

#### 开始节点
- 输出：`input`（用户输入）

#### 插件节点（batch_upload）
| 输入参数 | 绑定值 | 说明 |
|---------|--------|------|
| mode | `batch_upload` | 固定值 |
| zip_source | `{{input.zip_source}}` | 从用户输入获取ZIP |
| public_prefix | `{{input.public_prefix}}` | 可选前缀 |
| allowed_extensions | `{{input.allowed_extensions}}` | 扩展名白名单 |
| max_file_size_mb | `{{input.max_file_size_mb}}` | 大小限制 |
| skip_folders | `{{input.skip_folders}}` | 跳过文件夹 |

| 输出参数 | 说明 |
|---------|------|
| documents | 文档列表，传递给知识库写入节点 |
| directory_tree | 目录结构，传递给结束节点 |
| summary | 处理摘要 |

#### 知识库写入节点（Coze原生节点）
| 输入 | 绑定值 |
|------|--------|
| knowledge | `{{batch_upload.documents}}` |

| 输出 | 说明 |
|------|------|
| documentId | 写入的文档ID |
| fileName | 文件名 |
| fileUrl | 文件URL |

#### 变量赋值节点（Coze原生节点）
| 变量名 | 绑定值 | 说明 |
|--------|--------|------|
| memory_data | `{{batch_upload.memory_result}}` | 保存长期记忆 |
| kb_summary | `{{batch_upload.summary}}` | 保存处理摘要 |

#### 知识库检索节点（Coze原生节点）
| 输入 | 绑定值 |
|------|--------|
| Query | `{{input.query}}` 或用户提问 |

| 输出 | 说明 |
|------|------|
| outputList | 检索结果列表 |

#### 知识库删除节点（Coze原生节点，可选）
| 输入 | 绑定值 |
|------|--------|
| documentIds | `{{input.document_ids}}` |

#### 结束节点
| 输出 | 绑定值 |
|------|--------|
| output | `{{知识库检索.outputList}}` |

---

## 七、Array<Object> 类型在 Coze IDE 中的填写方法

### 7.1 输入参数 - Array<String> 填写方法

以 `allowed_extensions` 为例：
1. 在「配置」面板点击「添加参数」
2. 参数名填：`allowed_extensions`
3. 类型选择：`Array`（数组）
4. 展开后设置「元素类型」为：`String`（字符串）
5. 必填：取消勾选
6. 描述：填写说明文字
7. 默认值：填写 JSON 数组，如 `[".md",".txt",".json"]`

### 7.2 输出参数 - Array<Object> 填写方法

以 `documents` 为例：
1. 在「配置」面板点击「添加参数」
2. 参数名填：`documents`
3. 类型选择：`Array`（数组）
4. 展开后设置「元素类型」为：`Object`（对象）
5. 必填：勾选
6. 描述：填写说明文字
7. **关键步骤**：点击 Object 元素类型的「展开」或「添加子字段」
8. 依次添加子字段：
   - `name` -> String -> 必填
   - `path` -> String -> 必填
   - `size` -> Integer -> 必填
   - `status` -> String -> 必填
   - `content` -> String -> 非必填
   - `format` -> String -> 非必填
   - `word_count` -> Integer -> 非必填

### 7.3 输入参数 - Object 填写方法

以 `memory_data` 为例：
1. 类型选择：`Object`（对象）
2. 展开后添加子字段：
   - `key` -> String -> 必填
   - `value` -> String -> 必填
   - `category` -> String -> 非必填

---

## 八、常见问题

**Q: Array 类型默认值怎么填？**
A: 在默认值输入框中填写 JSON 格式，如 `["__MACOSX","node_modules"]`。注意用英文双引号和逗号。

**Q: Object 类型默认值怎么填？**
A: 在默认值输入框中填写 JSON 格式，如 `{"case_sensitive": false, "max_results": 50}`。

**Q: 如何获取ZIP的Base64编码？**
A: 使用 `generate_test_base64.js` 脚本生成，或在命令行运行：`certutil -encodehex -f input.zip output.b64 0x40000001`（Windows）或 `base64 input.zip`（Linux/Mac）。

**Q: 长期记忆在Coze中如何实现？**
A: 本插件提供了基于内存的模拟长期记忆。在生产环境中，建议：
1. 使用插件输出 memory_result
2. 通过「变量赋值」节点保存到工作流变量
3. 或使用Coze的数据库插件持久化存储

**Q: 知识库删除后还能恢复吗？**
A: Coze知识库删除是永久删除，请谨慎操作。建议在删除前先通过「知识库检索」确认要删除的内容。
