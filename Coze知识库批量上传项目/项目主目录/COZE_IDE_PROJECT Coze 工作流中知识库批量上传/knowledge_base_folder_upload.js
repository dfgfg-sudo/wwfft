'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const PLUGIN_META = {
  name: 'KnowledgeBaseFolderUploader',
  name_cn: '知识库文件夹批量上传节点',
  version: '1.0.0',
  description: '在 Coze 工作流中扩展原生知识库节点，支持直接上传整个目录和完整文件夹作为知识库',
  entry_point: 'handler',
  runtime: 'nodejs18',
  api_version: 'v1',
  min_coze_version: '2024.08',
  node_type: 'knowledge_base_folder_upload',
  icon: '📁',
  category: 'knowledge',
  tags: ['知识库', '文件夹', '批量上传', '目录', 'RAG', 'Coze', '工作流节点']
};

const SECURITY_POLICY = {
  allowed_extensions: ['.txt', '.md', '.markdown', '.json', '.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.go', '.rs', '.c', '.cpp', '.h', '.hpp', '.yaml', '.yml', '.xml', '.html', '.htm', '.css', '.csv', '.tsv', '.log', '.ini', '.conf', '.cfg', '.rst', '.asciidoc', '.adoc', '.org', '.tex'],
  blocked_extensions: ['.exe', '.bat', '.cmd', '.sh', '.ps1', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite', '.zip', '.rar', '.7z', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.flv', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'],
  max_file_size: 10 * 1024 * 1024,
  max_files_per_batch: 0,
  prevent_path_traversal: true,
  input_sanitization: true,
  rate_limit_per_second: 10,
  max_retry: 3,
  retry_interval_ms: 1000,
  audit_logging: true
};

const DEFAULT_PARAMS = {
  folder_path: '',
  dataset_id: '',
  access_token: '',
  upload_mode: 'document',
  chunk_size: 500,
  chunk_overlap: 50,
  recursive: true,
  preserve_structure: true,
  deduplicate: true,
  enable_retry: true,
  naming_rule: 'relative_path',
  custom_extensions: [],
  exclude_dirs: ['node_modules', '.git', '.svn', '__pycache__', '.idea', '.vscode', 'dist', 'build'],
  exclude_prefixes: ['.', '~', 'Thumbs.db'],
  concurrency: 5,
  return_preview: false,
  preview_max_chars: 500
};

function sanitizeString(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
}

function isPathSafe(targetPath, rootPath) {
  if (!SECURITY_POLICY.prevent_path_traversal) return true;
  const resolvedTarget = path.resolve(targetPath);
  const resolvedRoot = path.resolve(rootPath);
  return resolvedTarget === resolvedRoot || resolvedTarget.startsWith(resolvedRoot + path.sep);
}

function isExtensionAllowed(filePath, customExt) {
  const ext = path.extname(filePath).toLowerCase();
  const allowed = (customExt && customExt.length > 0) ? customExt.map(e => e.toLowerCase().startsWith('.') ? e.toLowerCase() : '.' + e.toLowerCase()) : SECURITY_POLICY.allowed_extensions;
  if (SECURITY_POLICY.blocked_extensions.includes(ext)) return false;
  return allowed.includes(ext);
}

function shouldExclude(filePath, excludeDirs, excludePrefixes) {
  const parts = filePath.split(path.sep);
  for (const part of parts) { if (excludeDirs.includes(part)) return true; }
  const basename = path.basename(filePath);
  for (const prefix of excludePrefixes) { if (basename.startsWith(prefix)) return true; }
  return false;
}

function md5(text) {
  return crypto.createHash('md5').update(text, 'utf8').digest('hex');
}

function readFileSafe(filePath) {
  try {
    const buffer = fs.readFileSync(filePath);
    if (buffer.length >= 3 && buffer[0] === 0xEF && buffer[1] === 0xBB && buffer[2] === 0xBF) {
      return buffer.slice(3).toString('utf8');
    }
    return buffer.toString('utf8');
  } catch (err) {
    return null;
  }
}

function scanDirectory(rootPath, params) {
  const results = [];
  const stack = [rootPath];
  const excludeDirs = params.exclude_dirs || [];
  const excludePrefixes = params.exclude_prefixes || [];
  const customExt = params.custom_extensions || [];
  const recursive = params.recursive !== false;

  while (stack.length > 0) {
    const currentDir = stack.pop();
    let entries;
    try { entries = fs.readdirSync(currentDir, { withFileTypes: true }); } catch (err) { continue; }
    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);
      if (!isPathSafe(fullPath, rootPath)) continue;
      if (entry.isDirectory()) {
        if (recursive && !excludeDirs.includes(entry.name)) { stack.push(fullPath); }
      } else if (entry.isFile()) {
        if (shouldExclude(fullPath, excludeDirs, excludePrefixes)) continue;
        if (!isExtensionAllowed(fullPath, customExt)) continue;
        try {
          const stat = fs.statSync(fullPath);
          if (stat.size > SECURITY_POLICY.max_file_size) continue;
          results.push({
            absolute_path: fullPath,
            relative_path: path.relative(rootPath, fullPath),
            name: entry.name,
            extension: path.extname(fullPath).toLowerCase(),
            size: stat.size,
            mtime: stat.mtimeMs
          });
        } catch (err) { continue; }
      }
    }
  }
  return results;
}

function chunkText(text, chunkSize, overlap) {
  if (!text || text.length <= chunkSize) return [text || ''];
  const chunks = [];
  let start = 0;
  while (start < text.length) {
    const end = Math.min(start + chunkSize, text.length);
    chunks.push(text.slice(start, end));
    start = end - overlap;
    if (start >= text.length) break;
  }
  return chunks;
}

function createRateLimiter(maxPerSecond) {
  let tokens = maxPerSecond;
  let lastRefill = Date.now();
  return () => new Promise(resolve => {
    const tryAcquire = () => {
      const now = Date.now();
      const newTokens = Math.floor((now - lastRefill) / 1000) * maxPerSecond;
      if (newTokens > 0) { tokens = Math.min(maxPerSecond, tokens + newTokens); lastRefill = now; }
      if (tokens > 0) { tokens--; resolve(); }
      else setTimeout(tryAcquire, 100);
    };
    tryAcquire();
  });
}

async function runWithConcurrency(tasks, concurrency) {
  const results = [];
  const executing = new Set();
  for (let i = 0; i < tasks.length; i++) {
    const p = Promise.resolve().then(() => tasks[i]()).then(r => { results[i] = r; });
    executing.add(p);
    p.finally(() => executing.delete(p));
    if (executing.size >= concurrency) await Promise.race(executing);
  }
  await Promise.all(executing);
  return results;
}

async function callCozeKnowledgeApi(apiPath, payload, accessToken, retryConfig) {
  const maxRetry = retryConfig?.enable_retry ? (SECURITY_POLICY.max_retry || 0) : 0;
  const interval = SECURITY_POLICY.retry_interval_ms || 1000;
  let lastError = null;
  for (let attempt = 0; attempt <= maxRetry; attempt++) {
    try {
      const resp = await fetch('https://api.coze.cn' + apiPath, {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + accessToken, 'Content-Type': 'application/json', 'User-Agent': 'Coze-KB-Folder-Uploader/1.0.0' },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      if (!resp.ok || data.code !== 0) throw new Error('Coze API error: ' + data.code + ' ' + (data.msg || resp.statusText));
      return { success: true, data: data.data || data };
    } catch (err) {
      lastError = err;
      if (attempt < maxRetry) await new Promise(r => setTimeout(r, interval * (attempt + 1)));
    }
  }
  return { success: false, error: lastError ? lastError.message : 'Unknown error' };
}

function validateAndMergeParams(input) {
  const params = { ...DEFAULT_PARAMS };
  if (input && typeof input === 'object') {
    for (const key of Object.keys(input)) { if (key in params) params[key] = input[key]; }
  }
  if (SECURITY_POLICY.input_sanitization) {
    params.folder_path = sanitizeString(params.folder_path);
    params.dataset_id = sanitizeString(params.dataset_id);
    params.access_token = sanitizeString(params.access_token);
  }
  const errors = [];
  if (!params.folder_path) errors.push('folder_path 不能为空');
  if (!params.dataset_id) errors.push('dataset_id 不能为空');
  if (!params.access_token) errors.push('access_token 不能为空');
  return { params, errors };
}

function collectFiles(params) {
  const folderPaths = Array.isArray(params.folder_path) ? params.folder_path : [params.folder_path];
  const allFiles = [];
  const scanReports = [];
  for (const fp of folderPaths) {
    const resolved = path.resolve(fp);
    if (!fs.existsSync(resolved)) { scanReports.push({ folder: resolved, status: 'not_found', file_count: 0 }); continue; }
    const stat = fs.statSync(resolved);
    if (!stat.isDirectory()) {
      if (isExtensionAllowed(resolved, params.custom_extensions)) {
        allFiles.push({
          absolute_path: resolved,
          relative_path: path.basename(resolved),
          name: path.basename(resolved),
          extension: path.extname(resolved).toLowerCase(),
          size: stat.size,
          mtime: stat.mtimeMs
        });
      }
      scanReports.push({ folder: resolved, status: 'single_file', file_count: 1 });
      continue;
    }
    const files = scanDirectory(resolved, params);
    for (const f of files) { allFiles.push({ ...f, root_folder: resolved }); }
    scanReports.push({ folder: resolved, status: 'scanned', file_count: files.length });
  }
  return { allFiles, scanReports };
}

function processFileContents(allFiles, params) {
  const seen = new Set();
  const processed = [];
  let skippedDuplicate = 0, skippedEmpty = 0;
  for (const file of allFiles) {
    const content = readFileSafe(file.absolute_path);
    if (content === null) { skippedEmpty++; continue; }
    const trimmed = content.trim();
    if (!trimmed) { skippedEmpty++; continue; }
    if (params.deduplicate) {
      const hash = md5(trimmed);
      if (seen.has(hash)) { skippedDuplicate++; continue; }
      seen.add(hash);
    }
    let docName = file.name;
    if (params.naming_rule === 'relative_path') docName = file.relative_path.replace(/[/\\]/g, '_');
    else if (params.naming_rule === 'absolute_path') docName = file.absolute_path.replace(/[/\\]/g, '_');
    let chunks = [trimmed];
    if (params.upload_mode === 'chunk') chunks = chunkText(trimmed, params.chunk_size, params.chunk_overlap);
    processed.push({
      file: file,
      doc_name: docName,
      content: trimmed,
      chunks: chunks,
      chunk_count: chunks.length,
      meta: {
        source_path: file.relative_path,
        extension: file.extension,
        size: file.size,
        mtime: file.mtime,
        root_folder: file.root_folder || '',
        preserve_structure: params.preserve_structure
      }
    });
  }
  return { processed, skippedDuplicate, skippedEmpty };
}

async function uploadToKnowledgeBase(processed, params, onProgress) {
  const accessToken = params.access_token;
  const datasetId = params.dataset_id;
  const concurrency = Math.max(1, Math.min(params.concurrency || 5, 20));
  const rateLimiter = createRateLimiter(SECURITY_POLICY.rate_limit_per_second);
  const apiPath = '/open_api/v2/knowledge/document/create';
  const total = processed.length;
  let succeeded = 0, failed = 0;
  const failures = [];
  const documentIds = [];

  const tasks = processed.map((item, idx) => async () => {
    await rateLimiter();
    try {
      const payload = {
        dataset_id: datasetId,
        document_bases: [{
          name: item.doc_name,
          source_info: { file_base64: Buffer.from(item.content, 'utf8').toString('base64'), file_type: 'text' }
        }],
        chunk_strategy: {
          chunk_type: params.upload_mode === 'chunk' ? 0 : (params.upload_mode === 'file' ? 2 : 1),
          max_tokens: params.chunk_size,
          overlap_tokens: params.chunk_overlap
        }
      };
      if (params.preserve_structure) payload.document_bases[0].source_info.meta_info = JSON.stringify(item.meta);
      const result = await callCozeKnowledgeApi(apiPath, payload, accessToken, params);
      if (result.success) {
        succeeded++;
        if (result.data && result.data.document_infos && result.data.document_infos[0]) {
          documentIds.push(result.data.document_infos[0].document_id);
        }
        if (onProgress) onProgress({ index: idx + 1, total, status: 'success', doc_name: item.doc_name });
      } else {
        failed++;
        failures.push({ doc_name: item.doc_name, error: result.error, index: idx });
        if (onProgress) onProgress({ index: idx + 1, total, status: 'failed', doc_name: item.doc_name, error: result.error });
      }
    } catch (err) {
      failed++;
      failures.push({ doc_name: item.doc_name, error: err.message, index: idx });
      if (onProgress) onProgress({ index: idx + 1, total, status: 'failed', doc_name: item.doc_name, error: err.message });
    }
  });
  await runWithConcurrency(tasks, concurrency);
  return { total, succeeded, failed, failures, documentIds };
}

async function handler(input) {
  const startTime = Date.now();
  const requestId = 'kb_upload_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  const auditLog = [];
  try {
    const parsed = typeof input === 'string' ? JSON.parse(input) : (input || {});
    auditLog.push({ step: 'parse_input', timestamp: Date.now(), status: 'ok' });
    const { params, errors } = validateAndMergeParams(parsed);
    if (errors.length > 0) {
      return { success: false, status: 'validation_failed', request_id: requestId, errors: errors, metadata: { version: PLUGIN_META.version, timestamp: Date.now() } };
    }
    auditLog.push({ step: 'validate_params', timestamp: Date.now(), status: 'ok' });
    const { allFiles, scanReports } = collectFiles(params);
    auditLog.push({ step: 'scan_folders', timestamp: Date.now(), status: 'ok', total_files: allFiles.length, scan_reports: scanReports });
    if (allFiles.length === 0) {
      return { success: false, status: 'no_files_found', request_id: requestId, message: '在指定目录下未找到任何符合条件的文件', scan_reports: scanReports, metadata: { version: PLUGIN_META.version, timestamp: Date.now() } };
    }
    if (SECURITY_POLICY.max_files_per_batch > 0 && allFiles.length > SECURITY_POLICY.max_files_per_batch) {
      return { success: false, status: 'too_many_files', request_id: requestId, message: '单次批量上传文件数 ' + allFiles.length + ' 超过上限 ' + SECURITY_POLICY.max_files_per_batch, metadata: { version: PLUGIN_META.version, timestamp: Date.now() } };
    }
    const { processed, skippedDuplicate, skippedEmpty } = processFileContents(allFiles, params);
    auditLog.push({ step: 'process_contents', timestamp: Date.now(), status: 'ok', processed_count: processed.length, skipped_duplicate: skippedDuplicate, skipped_empty: skippedEmpty });
    const uploadResult = await uploadToKnowledgeBase(processed, params, (progress) => {
      auditLog.push({ step: 'upload_progress', timestamp: Date.now(), ...progress });
    });
    auditLog.push({ step: 'upload_complete', timestamp: Date.now(), status: uploadResult.failed === 0 ? 'ok' : 'partial', ...uploadResult });

    let preview = null;
    if (params.return_preview) {
      preview = processed.slice(0, 10).map(p => ({
        doc_name: p.doc_name,
        source_path: p.meta.source_path,
        size: p.meta.size,
        chunk_count: p.chunk_count,
        content_preview: p.content.slice(0, params.preview_max_chars)
      }));
    }

    const processingTimeMs = Date.now() - startTime;
    return {
      success: uploadResult.failed === 0,
      status: uploadResult.failed === 0 ? 'success' : (uploadResult.succeeded > 0 ? 'partial_success' : 'failed'),
      request_id: requestId,
      plugin: PLUGIN_META.name,
      version: PLUGIN_META.version,
      summary: {
        total_files_scanned: allFiles.length,
        total_documents_processed: processed.length,
        skipped_duplicate: skippedDuplicate,
        skipped_empty: skippedEmpty,
        uploaded_succeeded: uploadResult.succeeded,
        uploaded_failed: uploadResult.failed,
        document_ids: uploadResult.documentIds,
        processing_time_ms: processingTimeMs
      },
      scan_reports: scanReports,
      failures: uploadResult.failures,
      preview: preview,
      audit_log: SECURITY_POLICY.audit_logging ? auditLog : undefined,
      metadata: { timestamp: Date.now(), version: PLUGIN_META.version, request_id: requestId, security_policy_applied: true, rate_limited: true, retry_enabled: params.enable_retry }
    };
  } catch (err) {
    return {
      success: false,
      status: 'error',
      request_id: requestId,
      error: { code: 'KNOWLEDGE_BASE_FOLDER_UPLOAD_ERROR', message: err.message, stack: process.env.NODE_ENV === 'development' ? err.stack : undefined },
      audit_log: SECURITY_POLICY.audit_logging ? auditLog : undefined,
      metadata: { timestamp: Date.now(), version: PLUGIN_META.version, request_id: requestId }
    };
  }
}

module.exports = {
  handler,
  PLUGIN_META,
  SECURITY_POLICY,
  DEFAULT_PARAMS,
  utils: {
    sanitizeString,
    isPathSafe,
    isExtensionAllowed,
    shouldExclude,
    md5,
    readFileSafe,
    scanDirectory,
    chunkText,
    validateAndMergeParams,
    collectFiles,
    processFileContents,
    uploadToKnowledgeBase
  }
};

if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('[Coze IDE 插件] ' + PLUGIN_META.name + ' v' + PLUGIN_META.version);
    console.log('用法: node knowledge_base_folder_upload.js \'<JSON参数>\'');
    process.exit(0);
  }
  (async () => {
    try {
      const result = await handler(args[0]);
      console.log(JSON.stringify(result, null, 2));
    } catch (e) { console.error('运行失败:', e.message); process.exit(1); }
  })();
}
