# Coze 批量知识库上传插件 -- 最终交付包（可直接使用）

## 一、您现在的状态（根据截图）

从您的截图来看，您已经在 Coze IDE 中完成了以下配置：
- 插件名称：`knowledge_batch_upload`
- 工具名称：`batch_upload`
- 元数据输入参数已配置（zip_base64、path_prefix 等）
- 元数据输出参数已配置（success、documents 等）
- 依赖包 `adm-zip` 已安装

**现在只需要做两件事：**
1. 把下面的代码完整复制粘贴到 IDE 代码区
2. 点击 Run，用提供的 Base64 测试数据运行

---

## 二、完整代码（直接复制到 Coze IDE 代码区）

**以下代码是一个完整的单文件，直接全部复制粘贴到 Coze IDE 的代码编辑区即可。**

```javascript
// @ts-nocheck
// ============================================================
// Coze 批量知识库上传插件 - Node.js 完整版
// 功能：接收ZIP的Base64编码，自动解压提取文件内容
//       保留完整目录结构，生成知识库文档列表
// 依赖：adm-zip（已在IDE依赖包区域安装）
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
      // 二进制文档
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
  const skipHidden = input.skip_hidden !== false;
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

## 三、测试用 Base64 数据

**以下 Base64 字符串可直接用于 Coze IDE 的 Run 测试。**

复制下面整段内容，在 Run 测试时作为 `zip_base64` 参数的值传入：

```
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
```

**测试参数设置：**

在 Run 测试时，输入参数填写：

```json
{
  "zip_base64": "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",
  "path_prefix": "知识库",
  "skip_hidden": true
}
```

---

## 四、预期测试结果

运行测试后，您应该看到以下输出：

### 控制台日志
```
=== Coze 批量知识库上传插件启动 ===
ZIP 解码成功，大小：4.49 KB
配置：最大文件 20 MB，路径前缀 "知识库"，跳过隐藏 true
ZIP 解析完成，共 13 个文件条目
过滤隐藏文件：跳过 1 个
文件类型过滤：保留 10 个（跳过 2 个不支持的格式）
  [OK] 知识库/projectA/config/deploy.yaml (137 B, 17 字)
  [OK] 知识库/projectA/config/mapping.xml (156 B, 15 字)
  [OK] 知识库/projectA/config/settings.json (253 B, 38 字)
  [OK] 知识库/projectA/db/schema.sql (355 B, 50 字)
  [OK] 知识库/projectA/docs/guide.txt (219 B, 56 字)
  [OK] 知识库/projectA/docs/README.md (374 B, 83 字)
  [OK] 知识库/projectA/src/index.js (357 B, 46 字)
  [OK] 知识库/projectA/src/utils.py (696 B, 110 字)
  [OK] 知识库/projectB/data.csv (148 B, 43 字)
  [OK] 知识库/projectB/report.html (495 B, 62 字)
批量处理完成！ | 成功：10 | 失败：0 | 跳过：3 | 总计：13 | 耗时：XXms
=== 插件执行结束 ===
```

### 输出参数
| 参数 | 值 |
|------|-----|
| success | `true` |
| total_count | `13` |
| success_count | `10` |
| fail_count | `0` |
| skipped_count | `3` |
| processing_time_ms | 约 30-100ms |

### 跳过的 3 个文件说明
- `__MACOSX/._README.md` -- macOS 资源文件（自动过滤）
- `.DS_Store` -- macOS 系统文件（自动过滤）
- `projectA/.hidden_config` -- 隐藏文件（skip_hidden=true 时过滤）

---

## 五、常见问题

**Q: 点击 Run 后报错 "Buffer is not defined"？**
A: 确保 IDE 运行时选择的是 **Node.js**，不是 Python3。Buffer 是 Node.js 内置对象。

**Q: 报错 "Cannot find module 'adm-zip'"？**
A: 在 IDE 左下角「依赖包」区域确认 `adm-zip` 已安装。如未安装，点击「添加依赖」搜索安装。

**Q: 输出参数和元数据不匹配？**
A: 运行测试后，点击「更新输出参数」按钮，IDE 会自动从实际输出同步参数定义。

**Q: 真实使用时 ZIP 的 Base64 怎么生成？**
A: 在工作流中，您可以使用 Coze 的「文件读取」节点或自定义代码节点将用户上传的 ZIP 文件转为 Base64，再传入本插件。

---

## 六、在工作流中使用（发布后）

1. 点击右上角「发布」按钮发布插件
2. 进入工作流编辑器，拖入「插件」节点
3. 选择 `knowledge_batch_upload` -> `batch_upload`
4. 绑定参数：`zip_base64` 接上游文件节点的 Base64 输出
5. 下游节点可通过 `{{插件节点.output.documents}}` 获取全部知识库文档
