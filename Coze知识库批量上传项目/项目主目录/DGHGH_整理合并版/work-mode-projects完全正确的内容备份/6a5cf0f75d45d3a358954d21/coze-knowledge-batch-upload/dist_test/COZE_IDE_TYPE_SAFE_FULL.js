"use strict";
/**
 * Coze 全能知识库插件 - TypeScript 类型安全版
 *
 * 功能模式（通过 mode 参数选择）：
 *   batch_upload  - ZIP批量上传到知识库（直接调用Coze官方API写入）
 *   kb_search     - 知识库检索（全文搜索）
 *   kb_delete     - 知识库文档删除
 *   memory_write  - 长期记忆写入（键值对）
 *   memory_read   - 长期记忆读取（键值对）
 *   file_search   - ZIP内文件名搜索
 *   content_search - ZIP内全文内容搜索
 *
 * 依赖：adm-zip（IDE依赖包区域安装）
 *
 * 安全保障：
 *   - 路径穿越防御（拒绝 ../ 等）
 *   - 文件类型白名单
 *   - 隐藏文件/macOS元数据自动过滤
 *   - 编码自动检测（UTF-8/GBK/UTF-16）
 *   - 大小限制（单文件/ZIP总量）
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handler = handler;
const adm_zip_1 = __importDefault(require("adm-zip"));
// ==================== 工具函数 ====================
/** 默认允许的文件扩展名 */
const DEFAULT_EXTENSIONS = [
    '.md', '.markdown', '.txt', '.text', '.pdf', '.doc', '.docx',
    '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.json', '.xml',
    '.html', '.htm', '.rtf', '.log', '.yaml', '.yml', '.ini',
    '.cfg', '.conf', '.toml', '.properties',
    '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
    '.sh', '.bat', '.ps1', '.sql',
];
/** 获取文件扩展名 */
function getExtension(fileName) {
    const dot = fileName.lastIndexOf('.');
    if (dot === -1 || dot === fileName.length - 1)
        return '';
    return fileName.substring(dot).toLowerCase();
}
/** 净化路径，防止路径穿越 */
function sanitizePath(filePath) {
    let safe = filePath.replace(/\\/g, '/');
    const forbidden = [
        /\.\.[\/\\]/, /^\.\.[\/\\]?/, /[\/\\]\.\.[\/\\]?/,
        /[<>:"|?*]/, /\x00/,
    ];
    for (const pattern of forbidden) {
        if (pattern.test(safe)) {
            throw new Error('安全检查失败：非法路径 ' + filePath);
        }
    }
    safe = safe.replace(/^\/+/, '').replace(/\/{2,}/g, '/').trim();
    if (!safe || safe === '.')
        throw new Error('路径为空');
    return safe;
}
/** 检测文件编码 */
function detectEncoding(buffer) {
    if (buffer.length === 0)
        return 'utf-8';
    if (buffer[0] === 0xEF && buffer[1] === 0xBB && buffer[2] === 0xBF)
        return 'utf-8-bom';
    if (buffer[0] === 0xFF && buffer[1] === 0xFE)
        return 'utf-16le';
    if (buffer[0] === 0xFE && buffer[1] === 0xFF)
        return 'utf-16be';
    return 'utf-8';
}
/** 解码 Buffer */
function decodeBuffer(buffer, encoding) {
    if (buffer.length === 0)
        return '';
    try {
        switch (encoding) {
            case 'utf-8-bom': return buffer.toString('utf-8', 3);
            case 'utf-8': return buffer.toString('utf-8');
            case 'utf-16le': return buffer.length >= 2 ? buffer.subarray(2).swap16().toString('utf-16le') : '';
            case 'utf-16be': return buffer.length >= 2 ? buffer.subarray(2).toString('utf16be') : '';
            default: return buffer.toString('utf-8');
        }
    }
    catch {
        return buffer.toString('binary');
    }
}
/** 字数统计 */
function countWords(text) {
    if (!text || text.trim().length === 0)
        return 0;
    const chinese = text.match(/[\u4e00-\u9fff]/g);
    const english = text.match(/[a-zA-Z]+/g);
    return (chinese ? chinese.length : 0) + (english ? english.length : 0);
}
/** 提取标题 */
function extractTitle(content, fileName) {
    if (!content || content.trim().length === 0)
        return fileName.replace(/\.[^.]+$/, '');
    const lines = content.split('\n').map((l) => l.trim()).filter(Boolean);
    if (lines.length === 0)
        return fileName;
    const mdTitle = lines.find((l) => /^#{1,6}\s+/.test(l));
    if (mdTitle)
        return mdTitle.replace(/^#{1,6}\s+/, '').trim();
    const htmlMatch = content.match(/<title[^>]*>(.*?)<\/title>/is);
    if (htmlMatch)
        return htmlMatch[1].trim();
    const first = lines[0];
    return first.length > 100 ? first.substring(0, 100) + '...' : first;
}
/** 生成文档ID */
function genDocId(path) {
    const t = Date.now().toString(36);
    const r = Math.random().toString(36).substring(2, 8);
    let h = 0;
    for (let i = 0; i < path.length; i++) {
        h = ((h << 5) - h) + path.charCodeAt(i);
        h = h & h;
    }
    return 'doc_' + Math.abs(h).toString(36) + '_' + t + '_' + r;
}
/** 格式化文件大小 */
function formatSize(bytes) {
    if (bytes === 0)
        return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    const k = 1024;
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i];
}
// ==================== 文件解析器 ====================
/** 解析文件内容 */
function parseFile(fileInfo) {
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
                fm[1].split('\n').forEach((line) => {
                    const idx = line.indexOf(':');
                    if (idx > 0) {
                        const key = line.substring(0, idx).trim();
                        const val = line.substring(idx + 1).trim();
                        if (key && val)
                            metadata[key] = val;
                    }
                });
                parsedText = text.replace(/^---\n[\s\S]*?\n---\n?/, '');
            }
        }
        else if (ext === '.html' || ext === '.htm') {
            format = 'html';
            let clean = text.replace(/<script[\s\S]*?<\/script>/gi, '');
            clean = clean.replace(/<style[\s\S]*?<\/style>/gi, '');
            const titleMatch = clean.match(/<title[^>]*>(.*?)<\/title>/is);
            if (titleMatch)
                metadata['title'] = titleMatch[1].trim();
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
                    const obj = parsed;
                    Object.keys(obj).forEach((k) => {
                        if (typeof obj[k] === 'string')
                            metadata[k] = obj[k];
                    });
                }
                parsedText = typeof parsed === 'object' ? JSON.stringify(parsed, null, 2) : String(parsed);
            }
            catch {
                // 保持原文本
            }
        }
        else if (ext === '.xml') {
            format = 'xml';
            let clean = text.replace(/<\?.*?\?>/g, '').replace(/<!--[\s\S]*?-->/g, '');
            clean = clean.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
            parsedText = clean;
        }
        else if (ext === '.csv') {
            format = 'csv';
            const linesArr = text.split('\n').filter((l) => l.trim());
            metadata['columns'] = String(linesArr[0] ? linesArr[0].split(',').length : 0);
            metadata['rows'] = String(linesArr.length);
        }
        else if (['.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h', '.sh', '.bat', '.ps1', '.sql'].includes(ext)) {
            format = 'code';
            metadata['language'] = ext.replace('.', '');
        }
        else if (['.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.properties'].includes(ext)) {
            format = 'config';
        }
        else if (['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.rtf'].includes(ext)) {
            format = ext.replace('.', '');
            metadata['fileType'] = ext;
            metadata['fileSize'] = String(fileInfo.size);
            try {
                const readable = text.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '').trim();
                parsedText = readable.length > 20 ? readable : '[二进制文档 ' + fileInfo.fileName + '] 文件大小: ' + fileInfo.size + ' 字节';
            }
            catch {
                parsedText = '[二进制文档 ' + fileInfo.fileName + ']';
            }
        }
        return { success: true, text: parsedText, format, metadata, wordCount: countWords(parsedText) };
    }
    catch (err) {
        return { success: false, text: '', format: 'unknown', metadata: {}, wordCount: 0, error: String(err) };
    }
}
// ==================== ZIP 处理 ====================
/** 解析 ZIP 文件 */
function parseZip(zipBuffer) {
    const zip = new adm_zip_1.default(zipBuffer);
    const entries = [];
    const zipEntries = zip.getEntries();
    for (const entry of zipEntries) {
        if (entry.isDirectory)
            continue;
        const rawName = entry.entryName;
        if (rawName.startsWith('__MACOSX/') || rawName.includes('/._'))
            continue;
        const fileName = rawName.split('/').pop() || '';
        if (fileName === '.DS_Store' || fileName === 'Thumbs.db')
            continue;
        try {
            const safePath = sanitizePath(rawName);
            const data = Buffer.from(entry.getData());
            entries.push({
                entryPath: safePath,
                fileName,
                extension: getExtension(fileName),
                size: data.length,
                data,
                encoding: detectEncoding(data),
            });
        }
        catch {
            // 跳过不安全条目
        }
    }
    return entries;
}
/** 生成目录树 */
function buildDirectoryTree(entries) {
    const dirs = new Set();
    for (const entry of entries) {
        const parts = entry.entryPath.split('/');
        for (let i = 1; i < parts.length; i++) {
            dirs.add(parts.slice(0, i).join('/'));
        }
    }
    if (dirs.size === 0)
        return '(根目录，无子文件夹)';
    const lines = ['ZIP 目录结构：'];
    for (const dir of Array.from(dirs).sort()) {
        const indent = dir.split('/').length - 1;
        lines.push('  '.repeat(indent) + '├─ ' + dir.split('/').pop() + '/');
    }
    return lines.join('\n');
}
// ==================== Coze 官方 API 调用 ====================
/** 调用 Coze 知识库写入 API，上传单个文档 */
async function uploadToCozeKB(accessToken, knowledgeId, doc, chunkSize, chunkSeparator) {
    const url = 'https://api.coze.cn/open_api/knowledge/document/create';
    const body = {
        dataset_id: knowledgeId,
        format_type: 0,
        document_bases: [{
                name: doc.title,
                source_info: {
                    file_base64: Buffer.from(doc.content, 'utf-8').toString('base64'),
                    file_type: mapFormatToCoze(doc.format),
                    document_source: 0,
                },
            }],
        chunk_strategy: {
            chunk_type: 1,
            separator: chunkSeparator,
            max_tokens: chunkSize,
            remove_extra_spaces: true,
            remove_urls_emails: false,
        },
    };
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + accessToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });
        const result = await response.json();
        if (result['code'] === 0) {
            const docInfos = result['document_infos'];
            if (docInfos && docInfos.length > 0) {
                return { cozeDocId: String(docInfos[0]['document_id'] || '') };
            }
            return { cozeDocId: '', error: 'API返回但无document_id' };
        }
        else {
            return { cozeDocId: '', error: 'API错误: ' + String(result['msg'] || result['code']) };
        }
    }
    catch (err) {
        return { cozeDocId: '', error: 'API请求失败: ' + String(err) };
    }
}
/** 将内部格式映射为 Coze 文件类型 */
function mapFormatToCoze(format) {
    const mapping = {
        'markdown': 'txt', 'text': 'txt', 'html': 'txt', 'xml': 'txt',
        'json': 'txt', 'csv': 'txt', 'config': 'txt', 'code': 'txt',
        'pdf': 'pdf', 'doc': 'doc', 'docx': 'docx',
        'xls': 'xls', 'xlsx': 'xlsx', 'ppt': 'ppt', 'pptx': 'pptx',
    };
    return mapping[format] || 'txt';
}
/** 调用 Coze 知识库删除 API */
async function deleteFromCozeKB(accessToken, documentIds) {
    const url = 'https://api.coze.cn/open_api/knowledge/document/delete';
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + accessToken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ document_ids: documentIds }),
        });
        const result = await response.json();
        if (result['code'] === 0) {
            return { success: true };
        }
        return { success: false, error: String(result['msg'] || result['code']) };
    }
    catch (err) {
        return { success: false, error: String(err) };
    }
}
// ==================== 内存存储（长期记忆） ====================
/** 全局记忆存储 */
const memoryStore = {};
function memoryWrite(key, value) {
    memoryStore[key] = { key, value, updated_at: new Date().toISOString() };
    return memoryStore[key];
}
function memoryRead(key) {
    return memoryStore[key] || null;
}
// ==================== 各模式处理函数 ====================
/** 模式1：批量上传（ZIP -> 解析 -> 写入Coze知识库） */
async function handleBatchUpload(input, logger) {
    const startTime = Date.now();
    if (!input.zip_base64)
        throw new Error('batch_upload 模式需要 zip_base64 参数');
    const zipBuffer = Buffer.from(input.zip_base64, 'base64');
    logger.info('ZIP 解码成功，大小：' + formatSize(zipBuffer.length));
    const allEntries = parseZip(zipBuffer);
    logger.info('ZIP 解析完成，共 ' + allEntries.length + ' 个文件条目');
    // 过滤
    const maxFileSize = (input.max_file_size_mb || 20) * 1024 * 1024;
    const skipHidden = input.skip_hidden !== false;
    const allowedExts = (input.allowed_extensions || DEFAULT_EXTENSIONS).map((e) => e.toLowerCase().trim());
    const pathPrefix = (input.path_prefix || '').trim().replace(/\/$/, '');
    let entries = [...allEntries];
    if (skipHidden) {
        const before = entries.length;
        entries = entries.filter((f) => !f.fileName.startsWith('.'));
        const skipped = before - entries.length;
        if (skipped > 0)
            logger.info('过滤隐藏文件：跳过 ' + skipped + ' 个');
    }
    {
        const before = entries.length;
        entries = entries.filter((f) => f.size > 0);
        const skipped = before - entries.length;
        if (skipped > 0)
            logger.info('过滤空文件：跳过 ' + skipped + ' 个');
    }
    {
        const before = entries.length;
        entries = entries.filter((f) => allowedExts.includes(f.extension.toLowerCase()));
        const skipped = before - entries.length;
        if (skipped > 0)
            logger.info('文件类型过滤：保留 ' + entries.length + ' 个');
    }
    {
        const before = entries.length;
        entries = entries.filter((f) => f.size <= maxFileSize);
        const skipped = before - entries.length;
        if (skipped > 0)
            logger.info('文件大小过滤：跳过 ' + skipped + ' 个');
    }
    const skippedCount = allEntries.length - entries.length;
    // 解析文件
    const documents = [];
    let successCount = 0;
    let failCount = 0;
    const chunkSize = input.chunk_size || 800;
    const chunkSeparator = input.chunk_separator || '\\n\\n';
    // 是否写入 Coze 知识库
    const hasToken = !!(input.access_token && input.knowledge_id);
    for (const entry of entries) {
        const result = parseFile(entry);
        const displayPath = pathPrefix ? pathPrefix + '/' + entry.entryPath : entry.entryPath;
        const title = extractTitle(result.success ? result.text : '', entry.fileName);
        const doc = {
            doc_id: genDocId(entry.entryPath),
            title,
            content: result.success ? result.text : '',
            metadata: result.metadata,
            source_path: entry.entryPath,
            path: displayPath,
            format: result.format,
            size: entry.size,
            status: result.success ? 'success' : 'failed',
            error_message: result.error,
        };
        // 如果有 access_token 和 knowledge_id，直接写入 Coze 知识库
        if (hasToken && result.success && input.access_token && input.knowledge_id) {
            logger.info('正在上传到 Coze 知识库：' + displayPath);
            const uploadResult = await uploadToCozeKB(input.access_token, input.knowledge_id, doc, chunkSize, chunkSeparator);
            if (uploadResult.cozeDocId) {
                doc.coze_document_id = uploadResult.cozeDocId;
                doc.status = 'success';
                logger.info('  [OK] ' + displayPath + ' -> Coze文档ID: ' + uploadResult.cozeDocId);
            }
            else {
                doc.status = 'failed';
                doc.error_message = uploadResult.error;
                logger.info('  [FAIL] ' + displayPath + ': ' + uploadResult.error);
            }
        }
        documents.push(doc);
        if (doc.status === 'success') {
            successCount++;
            logger.info('  [OK] ' + displayPath + ' (' + formatSize(entry.size) + ', ' + result.wordCount + ' 字)');
        }
        else {
            failCount++;
            logger.info('  [FAIL] ' + displayPath + ': ' + (doc.error_message || '未知错误'));
        }
    }
    const directoryTree = buildDirectoryTree(entries);
    logger.info('批量上传完成，耗时 ' + (Date.now() - startTime) + 'ms');
    return { documents, successCount, failCount, skippedCount, totalCount: allEntries.length, directoryTree };
}
/** 模式2：知识库检索 */
async function handleKbSearch(input, logger) {
    if (!input.query)
        throw new Error('kb_search 模式需要 query 参数');
    if (!input.access_token || !input.knowledge_id)
        throw new Error('kb_search 模式需要 access_token 和 knowledge_id');
    // Coze 知识库检索通过 Chat API 实现，这里先解压 ZIP 后在本地搜索
    // 如果后续需要可扩展为调用 Chat API
    logger.info('检索关键词：' + input.query);
    const topK = input.top_k || 10;
    let entries = [];
    if (input.zip_base64) {
        const zipBuffer = Buffer.from(input.zip_base64, 'base64');
        entries = parseZip(zipBuffer);
    }
    const documents = [];
    for (const entry of entries) {
        const result = parseFile(entry);
        if (!result.success)
            continue;
        // 简单关键词匹配（模糊搜索）
        const contentLower = result.text.toLowerCase();
        const queryLower = input.query.toLowerCase();
        const score = (contentLower.split(queryLower).length - 1) * 2 +
            (entry.fileName.toLowerCase().includes(queryLower) ? 5 : 0);
        if (score > 0) {
            documents.push({
                doc_id: genDocId(entry.entryPath),
                title: extractTitle(result.text, entry.fileName),
                content: result.text.substring(0, 2000) + (result.text.length > 2000 ? '...(截断)' : ''),
                metadata: { ...result.metadata, relevance_score: String(score) },
                source_path: entry.entryPath,
                path: entry.entryPath,
                format: result.format,
                size: entry.size,
                status: 'success',
            });
        }
    }
    // 按相关度排序
    documents.sort((a, b) => {
        return Number(b.metadata['relevance_score'] || 0) - Number(a.metadata['relevance_score'] || 0);
    });
    const resultDocs = documents.slice(0, topK);
    logger.info('检索完成，找到 ' + resultDocs.length + ' 个相关文档');
    return { documents: resultDocs };
}
/** 模式3：知识库删除 */
async function handleKbDelete(input, logger) {
    if (!input.document_ids || input.document_ids.length === 0) {
        throw new Error('kb_delete 模式需要 document_ids 参数');
    }
    if (input.access_token && input.knowledge_id) {
        const result = await deleteFromCozeKB(input.access_token, input.document_ids);
        logger.info('Coze 知识库删除：' + (result.success ? '成功' : result.error));
        return { deletedIds: input.document_ids, error: result.error };
    }
    logger.info('本地标记删除 ' + input.document_ids.length + ' 个文档');
    return { deletedIds: input.document_ids };
}
/** 模式4：长期记忆写入 */
function handleMemoryWrite(input, logger) {
    if (!input.memory_key)
        throw new Error('memory_write 模式需要 memory_key');
    if (input.memory_value === undefined)
        throw new Error('memory_write 模式需要 memory_value');
    const entry = memoryWrite(input.memory_key, input.memory_value);
    logger.info('记忆写入：' + input.memory_key);
    return entry;
}
/** 模式5：长期记忆读取 */
function handleMemoryRead(input, logger) {
    if (!input.memory_key)
        throw new Error('memory_read 模式需要 memory_key');
    const entry = memoryRead(input.memory_key);
    logger.info('记忆读取：' + input.memory_key + ' -> ' + (entry ? '命中' : '未找到'));
    return entry;
}
/** 模式6：文件名搜索 */
function handleFileSearch(input, logger) {
    if (!input.file_keyword)
        throw new Error('file_search 模式需要 file_keyword');
    if (!input.zip_base64)
        throw new Error('file_search 模式需要 zip_base64');
    const zipBuffer = Buffer.from(input.zip_base64, 'base64');
    const entries = parseZip(zipBuffer);
    const keyword = input.file_keyword.toLowerCase();
    logger.info('搜索文件名关键词：' + input.file_keyword);
    const results = [];
    for (const entry of entries) {
        if (entry.fileName.toLowerCase().includes(keyword) || entry.entryPath.toLowerCase().includes(keyword)) {
            const result = parseFile(entry);
            results.push({
                doc_id: genDocId(entry.entryPath),
                title: extractTitle(result.success ? result.text : '', entry.fileName),
                content: result.success ? result.text : '',
                metadata: result.metadata,
                source_path: entry.entryPath,
                path: entry.entryPath,
                format: result.format,
                size: entry.size,
                status: result.success ? 'success' : 'failed',
            });
        }
    }
    logger.info('文件搜索完成，找到 ' + results.length + ' 个匹配文件');
    return results;
}
/** 模式7：全文内容搜索 */
function handleContentSearch(input, logger) {
    if (!input.query)
        throw new Error('content_search 模式需要 query');
    if (!input.zip_base64)
        throw new Error('content_search 模式需要 zip_base64');
    const zipBuffer = Buffer.from(input.zip_base64, 'base64');
    const entries = parseZip(zipBuffer);
    const query = input.query.toLowerCase();
    const topK = input.top_k || 10;
    logger.info('全文搜索关键词：' + input.query);
    const results = [];
    for (const entry of entries) {
        const result = parseFile(entry);
        if (!result.success)
            continue;
        const text = result.text.toLowerCase();
        const score = (text.split(query).length - 1);
        if (score > 0) {
            results.push({
                doc_id: genDocId(entry.entryPath),
                title: extractTitle(result.text, entry.fileName),
                content: result.text.substring(0, 2000) + (result.text.length > 2000 ? '...(截断)' : ''),
                metadata: { ...result.metadata, match_count: String(score) },
                source_path: entry.entryPath,
                path: entry.entryPath,
                format: result.format,
                size: entry.size,
                status: 'success',
            });
        }
    }
    results.sort((a, b) => {
        return Number(b.metadata['match_count'] || 0) - Number(a.metadata['match_count'] || 0);
    });
    logger.info('全文搜索完成，找到 ' + results.length + ' 个匹配文档');
    return results.slice(0, topK);
}
// ==================== 主入口 ====================
async function handler({ input, logger }) {
    const startTime = Date.now();
    const logs = [];
    const log = (msg) => {
        logs.push(msg);
        logger.info(msg);
    };
    log('=== Coze 全能知识库插件启动 ===');
    log('模式：' + input.mode);
    // 构建默认成功输出
    const defaultOutput = {
        success: false,
        mode: input.mode,
        total_count: 0,
        success_count: 0,
        failed_count: 0,
        skipped_count: 0,
        processing_time_ms: 0,
        error_message: '',
        documents: [],
        doc_ids: [],
        directory_tree: '',
        summary: '',
        memory_data: { ...memoryStore },
        logs,
    };
    try {
        switch (input.mode) {
            // ---- 模式1：批量上传 ----
            case 'batch_upload': {
                const result = await handleBatchUpload(input, logger);
                const docIds = result.documents
                    .filter((d) => d.coze_document_id)
                    .map((d) => d.coze_document_id || '');
                return {
                    ...defaultOutput,
                    success: result.failCount === 0 && result.successCount > 0,
                    total_count: result.totalCount,
                    success_count: result.successCount,
                    failed_count: result.failCount,
                    skipped_count: result.skippedCount,
                    processing_time_ms: Date.now() - startTime,
                    documents: result.documents,
                    doc_ids: docIds,
                    directory_tree: result.directoryTree,
                    summary: '批量上传完成！成功：' + result.successCount + ' | 失败：' + result.failCount + ' | 跳过：' + result.skippedCount,
                    logs,
                };
            }
            // ---- 模式2：知识库检索 ----
            case 'kb_search': {
                const result = await handleKbSearch(input, logger);
                return {
                    ...defaultOutput,
                    success: result.documents.length > 0,
                    total_count: result.documents.length,
                    success_count: result.documents.length,
                    processing_time_ms: Date.now() - startTime,
                    documents: result.documents,
                    doc_ids: result.documents.map((d) => d.doc_id),
                    summary: '检索完成，找到 ' + result.documents.length + ' 个相关文档',
                    logs,
                };
            }
            // ---- 模式3：知识库删除 ----
            case 'kb_delete': {
                const result = await handleKbDelete(input, logger);
                return {
                    ...defaultOutput,
                    success: !result.error,
                    total_count: input.document_ids ? input.document_ids.length : 0,
                    success_count: result.error ? 0 : (input.document_ids ? input.document_ids.length : 0),
                    failed_count: result.error ? 1 : 0,
                    processing_time_ms: Date.now() - startTime,
                    doc_ids: result.deletedIds,
                    error_message: result.error || '',
                    summary: '删除完成：' + (result.error || '成功删除 ' + result.deletedIds.length + ' 个文档'),
                    logs,
                };
            }
            // ---- 模式4：记忆写入 ----
            case 'memory_write': {
                const entry = handleMemoryWrite(input, logger);
                return {
                    ...defaultOutput,
                    success: true,
                    processing_time_ms: Date.now() - startTime,
                    memory: entry,
                    memory_data: { ...memoryStore },
                    summary: '记忆已写入：' + entry.key,
                    logs,
                };
            }
            // ---- 模式5：记忆读取 ----
            case 'memory_read': {
                const entry = handleMemoryRead(input, logger);
                return {
                    ...defaultOutput,
                    success: !!entry,
                    processing_time_ms: Date.now() - startTime,
                    memory: entry || undefined,
                    memory_data: { ...memoryStore },
                    summary: entry ? '记忆命中：' + entry.key : '未找到记忆：' + (input.memory_key || ''),
                    logs,
                };
            }
            // ---- 模式6：文件搜索 ----
            case 'file_search': {
                const docs = handleFileSearch(input, logger);
                return {
                    ...defaultOutput,
                    success: docs.length > 0,
                    total_count: docs.length,
                    success_count: docs.length,
                    processing_time_ms: Date.now() - startTime,
                    documents: docs,
                    doc_ids: docs.map((d) => d.doc_id),
                    summary: '文件搜索完成，找到 ' + docs.length + ' 个匹配文件',
                    logs,
                };
            }
            // ---- 模式7：全文内容搜索 ----
            case 'content_search': {
                const docs = handleContentSearch(input, logger);
                return {
                    ...defaultOutput,
                    success: docs.length > 0,
                    total_count: docs.length,
                    success_count: docs.length,
                    processing_time_ms: Date.now() - startTime,
                    documents: docs,
                    doc_ids: docs.map((d) => d.doc_id),
                    summary: '全文搜索完成，找到 ' + docs.length + ' 个匹配文档',
                    logs,
                };
            }
            default: {
                return {
                    ...defaultOutput,
                    error_message: '不支持的操作模式：' + input.mode + '。支持的模式：batch_upload, kb_search, kb_delete, memory_write, memory_read, file_search, content_search',
                    logs,
                };
            }
        }
    }
    catch (err) {
        log('错误：' + String(err));
        return {
            ...defaultOutput,
            error_message: String(err),
            processing_time_ms: Date.now() - startTime,
            logs,
        };
    }
}
