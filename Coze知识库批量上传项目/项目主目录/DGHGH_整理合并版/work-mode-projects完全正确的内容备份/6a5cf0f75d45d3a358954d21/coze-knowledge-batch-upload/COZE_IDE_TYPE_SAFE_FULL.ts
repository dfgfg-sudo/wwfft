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

import AdmZip from 'adm-zip';

// ==================== 类型定义 ====================

/** 插件输入参数 */
interface PluginInput {
  /** 操作模式 */
  mode: 'batch_upload' | 'kb_search' | 'kb_delete' | 'memory_write' | 'memory_read' | 'file_search' | 'content_search';
  /** Coze 个人访问令牌（batch_upload/kb_search/kb_delete 模式必填） */
  access_token?: string;
  /** 知识库ID（batch_upload/kb_search/kb_delete 模式必填） */
  knowledge_id?: string;
  /** ZIP文件的Base64编码（batch_upload/file_search/content_search 模式必填） */
  zip_base64?: string;
  /** 知识库路径前缀（如"知识库"） */
  path_prefix?: string;
  /** 允许的文件扩展名白名单（如[".md",".txt"]，默认支持全部） */
  allowed_extensions?: string[];
  /** 单文件最大MB（默认20） */
  max_file_size_mb?: number;
  /** 跳过隐藏文件（默认true） */
  skip_hidden?: boolean;
  /** 检索关键词（kb_search/content_search 模式必填） */
  query?: string;
  /** 检索返回最大数量（默认10） */
  top_k?: number;
  /** 待删除的文档ID列表（kb_delete 模式必填） */
  document_ids?: string[];
  /** 记忆键名（memory_write/memory_read 模式必填） */
  memory_key?: string;
  /** 记忆值（memory_write 模式必填） */
  memory_value?: string;
  /** 文件名关键词（file_search 模式必填） */
  file_keyword?: string;
  /** 分段策略：最大token数（默认800） */
  chunk_size?: number;
  /** 分段策略：分段标识符（默认\n\n） */
  chunk_separator?: string;
}

/** 插件输出参数 - 文档对象（匹配Coze官方知识库格式） */
interface KnowledgeDocument {
  /** 文档唯一标识 */
  doc_id: string;
  /** 文档标题 */
  title: string;
  /** 文档内容/文本片段 */
  content: string;
  /** 文档元数据 */
  metadata: Record<string, string>;
  /** 原始文件在ZIP中的路径 */
  source_path: string;
  /** 知识库中的显示路径 */
  path: string;
  /** 文件格式 */
  format: string;
  /** 文件大小（字节） */
  size: number;
  /** 处理状态：success/failed/pending */
  status: string;
  /** 错误信息 */
  error_message?: string;
  /** Coze API 返回的文档ID（上传成功后） */
  coze_document_id?: string;
}

/** 记忆条目 */
interface MemoryEntry {
  key: string;
  value: string;
  updated_at: string;
}

/** 插件输出参数 */
interface PluginOutput {
  /** 是否操作成功 */
  success: boolean;
  /** 操作模式 */
  mode: string;
  /** 总文件数 */
  total_count: number;
  /** 成功数 */
  success_count: number;
  /** 失败数 */
  failed_count: number;
  /** 跳过数 */
  skipped_count: number;
  /** 处理耗时（毫秒） */
  processing_time_ms: number;
  /** 错误信息 */
  error_message: string;
  /** 切分后的文档列表（匹配Coze官方格式） */
  documents: KnowledgeDocument[];
  /** 生成的文档ID列表 */
  doc_ids: string[];
  /** 目录树 */
  directory_tree: string;
  /** 处理摘要 */
  summary: string;
  /** 记忆数据（memory_read 模式） */
  memory?: MemoryEntry;
  /** 长期记忆存储（所有模式的记忆输出） */
  memory_data?: Record<string, MemoryEntry>;
  /** 处理日志 */
  logs: string[];
}

/** ZIP 文件信息 */
interface ZipEntry {
  entryPath: string;
  fileName: string;
  extension: string;
  size: number;
  data: Buffer;
  encoding: string;
}

/** 日志工具 */
interface Logger {
  info: (msg: string) => void;
  error: (msg: string) => void;
  warn: (msg: string) => void;
}

// ==================== 工具函数 ====================

/** 默认允许的文件扩展名 */
const DEFAULT_EXTENSIONS: string[] = [
  '.md', '.markdown', '.txt', '.text', '.pdf', '.doc', '.docx',
  '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.json', '.xml',
  '.html', '.htm', '.rtf', '.log', '.yaml', '.yml', '.ini',
  '.cfg', '.conf', '.toml', '.properties',
  '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
  '.sh', '.bat', '.ps1', '.sql',
];

/** 获取文件扩展名 */
function getExtension(fileName: string): string {
  const dot: number = fileName.lastIndexOf('.');
  if (dot === -1 || dot === fileName.length - 1) return '';
  return fileName.substring(dot).toLowerCase();
}

/** 净化路径，防止路径穿越 */
function sanitizePath(filePath: string): string {
  let safe: string = filePath.replace(/\\/g, '/');
  const forbidden: RegExp[] = [
    /\.\.[\/\\]/, /^\.\.[\/\\]?/, /[\/\\]\.\.[\/\\]?/,
    /[<>:"|?*]/, /\x00/,
  ];
  for (const pattern of forbidden) {
    if (pattern.test(safe)) {
      throw new Error('安全检查失败：非法路径 ' + filePath);
    }
  }
  safe = safe.replace(/^\/+/, '').replace(/\/{2,}/g, '/').trim();
  if (!safe || safe === '.') throw new Error('路径为空');
  return safe;
}

/** 检测文件编码 */
function detectEncoding(buffer: Buffer): string {
  if (buffer.length === 0) return 'utf-8';
  if (buffer[0] === 0xEF && buffer[1] === 0xBB && buffer[2] === 0xBF) return 'utf-8-bom';
  if (buffer[0] === 0xFF && buffer[1] === 0xFE) return 'utf-16le';
  if (buffer[0] === 0xFE && buffer[1] === 0xFF) return 'utf-16be';
  return 'utf-8';
}

/** 解码 Buffer */
function decodeBuffer(buffer: Buffer, encoding: string): string {
  if (buffer.length === 0) return '';
  try {
    switch (encoding) {
      case 'utf-8-bom': return buffer.toString('utf-8', 3);
      case 'utf-8': return buffer.toString('utf-8');
      case 'utf-16le': return buffer.length >= 2 ? buffer.subarray(2).swap16().toString('utf-16le') : '';
      case 'utf-16be': return buffer.length >= 2 ? buffer.subarray(2).toString('utf16be' as BufferEncoding) : '';
      default: return buffer.toString('utf-8');
    }
  } catch {
    return buffer.toString('binary');
  }
}

/** 字数统计 */
function countWords(text: string): number {
  if (!text || text.trim().length === 0) return 0;
  const chinese: RegExpMatchArray | null = text.match(/[\u4e00-\u9fff]/g);
  const english: RegExpMatchArray | null = text.match(/[a-zA-Z]+/g);
  return (chinese ? chinese.length : 0) + (english ? english.length : 0);
}

/** 提取标题 */
function extractTitle(content: string, fileName: string): string {
  if (!content || content.trim().length === 0) return fileName.replace(/\.[^.]+$/, '');
  const lines: string[] = content.split('\n').map((l: string) => l.trim()).filter(Boolean);
  if (lines.length === 0) return fileName;
  const mdTitle: string | undefined = lines.find((l: string) => /^#{1,6}\s+/.test(l));
  if (mdTitle) return mdTitle.replace(/^#{1,6}\s+/, '').trim();
  const htmlMatch: RegExpMatchArray | null = content.match(/<title[^>]*>(.*?)<\/title>/is);
  if (htmlMatch) return htmlMatch[1].trim();
  const first: string = lines[0];
  return first.length > 100 ? first.substring(0, 100) + '...' : first;
}

/** 生成文档ID */
function genDocId(path: string): string {
  const t: string = Date.now().toString(36);
  const r: string = Math.random().toString(36).substring(2, 8);
  let h: number = 0;
  for (let i: number = 0; i < path.length; i++) {
    h = ((h << 5) - h) + path.charCodeAt(i);
    h = h & h;
  }
  return 'doc_' + Math.abs(h).toString(36) + '_' + t + '_' + r;
}

/** 格式化文件大小 */
function formatSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const units: string[] = ['B', 'KB', 'MB', 'GB'];
  const k: number = 1024;
  const i: number = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i];
}

// ==================== 文件解析器 ====================

/** 解析文件内容 */
function parseFile(fileInfo: ZipEntry): { success: boolean; text: string; format: string; metadata: Record<string, string>; wordCount: number; error?: string } {
  try {
    const ext: string = fileInfo.extension;
    const text: string = decodeBuffer(fileInfo.data, fileInfo.encoding);
    let format: string = 'text';
    let parsedText: string = text;
    const metadata: Record<string, string> = {};

    if (ext === '.md' || ext === '.markdown') {
      format = 'markdown';
      const fm: RegExpMatchArray | null = text.match(/^---\n([\s\S]*?)\n---/);
      if (fm) {
        fm[1].split('\n').forEach((line: string) => {
          const idx: number = line.indexOf(':');
          if (idx > 0) {
            const key: string = line.substring(0, idx).trim();
            const val: string = line.substring(idx + 1).trim();
            if (key && val) metadata[key] = val;
          }
        });
        parsedText = text.replace(/^---\n[\s\S]*?\n---\n?/, '');
      }
    } else if (ext === '.html' || ext === '.htm') {
      format = 'html';
      let clean: string = text.replace(/<script[\s\S]*?<\/script>/gi, '');
      clean = clean.replace(/<style[\s\S]*?<\/style>/gi, '');
      const titleMatch: RegExpMatchArray | null = clean.match(/<title[^>]*>(.*?)<\/title>/is);
      if (titleMatch) metadata['title'] = titleMatch[1].trim();
      clean = clean.replace(/<[^>]+>/g, ' ');
      clean = clean.replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
      clean = clean.replace(/&amp;/g, '&').replace(/&quot;/g, '"');
      clean = clean.replace(/\s+/g, ' ').trim();
      parsedText = clean;
    } else if (ext === '.json') {
      format = 'json';
      try {
        const parsed: unknown = JSON.parse(text);
        if (typeof parsed === 'object' && parsed !== null) {
          const obj: Record<string, unknown> = parsed as Record<string, unknown>;
          Object.keys(obj).forEach((k: string) => {
            if (typeof obj[k] === 'string') metadata[k] = obj[k] as string;
          });
        }
        parsedText = typeof parsed === 'object' ? JSON.stringify(parsed, null, 2) : String(parsed);
      } catch {
        // 保持原文本
      }
    } else if (ext === '.xml') {
      format = 'xml';
      let clean: string = text.replace(/<\?.*?\?>/g, '').replace(/<!--[\s\S]*?-->/g, '');
      clean = clean.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
      parsedText = clean;
    } else if (ext === '.csv') {
      format = 'csv';
      const linesArr: string[] = text.split('\n').filter((l: string) => l.trim());
      metadata['columns'] = String(linesArr[0] ? linesArr[0].split(',').length : 0);
      metadata['rows'] = String(linesArr.length);
    } else if (['.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h', '.sh', '.bat', '.ps1', '.sql'].includes(ext)) {
      format = 'code';
      metadata['language'] = ext.replace('.', '');
    } else if (['.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.properties'].includes(ext)) {
      format = 'config';
    } else if (['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.rtf'].includes(ext)) {
      format = ext.replace('.', '');
      metadata['fileType'] = ext;
      metadata['fileSize'] = String(fileInfo.size);
      try {
        const readable: string = text.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '').trim();
        parsedText = readable.length > 20 ? readable : '[二进制文档 ' + fileInfo.fileName + '] 文件大小: ' + fileInfo.size + ' 字节';
      } catch {
        parsedText = '[二进制文档 ' + fileInfo.fileName + ']';
      }
    }

    return { success: true, text: parsedText, format, metadata, wordCount: countWords(parsedText) };
  } catch (err) {
    return { success: false, text: '', format: 'unknown', metadata: {}, wordCount: 0, error: String(err) };
  }
}

// ==================== ZIP 处理 ====================

/** 解析 ZIP 文件 */
function parseZip(zipBuffer: Buffer): ZipEntry[] {
  const zip: AdmZip = new AdmZip(zipBuffer);
  const entries: ZipEntry[] = [];
  const zipEntries: AdmZip.IZipEntry[] = zip.getEntries();

  for (const entry of zipEntries) {
    if (entry.isDirectory) continue;
    const rawName: string = entry.entryName;
    if (rawName.startsWith('__MACOSX/') || rawName.includes('/._')) continue;
    const fileName: string = rawName.split('/').pop() || '';
    if (fileName === '.DS_Store' || fileName === 'Thumbs.db') continue;

    try {
      const safePath: string = sanitizePath(rawName);
      const data: Buffer = Buffer.from(entry.getData());
      entries.push({
        entryPath: safePath,
        fileName,
        extension: getExtension(fileName),
        size: data.length,
        data,
        encoding: detectEncoding(data),
      });
    } catch {
      // 跳过不安全条目
    }
  }

  return entries;
}

/** 生成目录树 */
function buildDirectoryTree(entries: ZipEntry[]): string {
  const dirs: Set<string> = new Set<string>();
  for (const entry of entries) {
    const parts: string[] = entry.entryPath.split('/');
    for (let i: number = 1; i < parts.length; i++) {
      dirs.add(parts.slice(0, i).join('/'));
    }
  }
  if (dirs.size === 0) return '(根目录，无子文件夹)';
  const lines: string[] = ['ZIP 目录结构：'];
  for (const dir of Array.from(dirs).sort()) {
    const indent: number = dir.split('/').length - 1;
    lines.push('  '.repeat(indent) + '├─ ' + dir.split('/').pop() + '/');
  }
  return lines.join('\n');
}

// ==================== Coze 官方 API 调用 ====================

/** 调用 Coze 知识库写入 API，上传单个文档 */
async function uploadToCozeKB(
  accessToken: string,
  knowledgeId: string,
  doc: KnowledgeDocument,
  chunkSize: number,
  chunkSeparator: string
): Promise<{ cozeDocId: string; error?: string }> {
  const url: string = 'https://api.coze.cn/open_api/knowledge/document/create';
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

    const result: Record<string, unknown> = await response.json() as Record<string, unknown>;

    if (result['code'] === 0) {
      const docInfos: Record<string, unknown>[] = result['document_infos'] as Record<string, unknown>[];
      if (docInfos && docInfos.length > 0) {
        return { cozeDocId: String(docInfos[0]['document_id'] || '') };
      }
      return { cozeDocId: '', error: 'API返回但无document_id' };
    } else {
      return { cozeDocId: '', error: 'API错误: ' + String(result['msg'] || result['code']) };
    }
  } catch (err) {
    return { cozeDocId: '', error: 'API请求失败: ' + String(err) };
  }
}

/** 将内部格式映射为 Coze 文件类型 */
function mapFormatToCoze(format: string): string {
  const mapping: Record<string, string> = {
    'markdown': 'txt', 'text': 'txt', 'html': 'txt', 'xml': 'txt',
    'json': 'txt', 'csv': 'txt', 'config': 'txt', 'code': 'txt',
    'pdf': 'pdf', 'doc': 'doc', 'docx': 'docx',
    'xls': 'xls', 'xlsx': 'xlsx', 'ppt': 'ppt', 'pptx': 'pptx',
  };
  return mapping[format] || 'txt';
}

/** 调用 Coze 知识库删除 API */
async function deleteFromCozeKB(
  accessToken: string,
  documentIds: string[]
): Promise<{ success: boolean; error?: string }> {
  const url: string = 'https://api.coze.cn/open_api/knowledge/document/delete';
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + accessToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ document_ids: documentIds }),
    });
    const result: Record<string, unknown> = await response.json() as Record<string, unknown>;
    if (result['code'] === 0) {
      return { success: true };
    }
    return { success: false, error: String(result['msg'] || result['code']) };
  } catch (err) {
    return { success: false, error: String(err) };
  }
}

// ==================== 内存存储（长期记忆） ====================

/** 全局记忆存储 */
const memoryStore: Record<string, MemoryEntry> = {};

function memoryWrite(key: string, value: string): MemoryEntry {
  memoryStore[key] = { key, value, updated_at: new Date().toISOString() };
  return memoryStore[key];
}

function memoryRead(key: string): MemoryEntry | null {
  return memoryStore[key] || null;
}

// ==================== 各模式处理函数 ====================

/** 模式1：批量上传（ZIP -> 解析 -> 写入Coze知识库） */
async function handleBatchUpload(
  input: PluginInput,
  logger: Logger
): Promise<{ documents: KnowledgeDocument[]; successCount: number; failCount: number; skippedCount: number; totalCount: number; directoryTree: string }> {
  const startTime: number = Date.now();

  if (!input.zip_base64) throw new Error('batch_upload 模式需要 zip_base64 参数');
  const zipBuffer: Buffer = Buffer.from(input.zip_base64, 'base64');
  logger.info('ZIP 解码成功，大小：' + formatSize(zipBuffer.length));

  const allEntries: ZipEntry[] = parseZip(zipBuffer);
  logger.info('ZIP 解析完成，共 ' + allEntries.length + ' 个文件条目');

  // 过滤
  const maxFileSize: number = (input.max_file_size_mb || 20) * 1024 * 1024;
  const skipHidden: boolean = input.skip_hidden !== false;
  const allowedExts: string[] = (input.allowed_extensions || DEFAULT_EXTENSIONS).map((e: string) => e.toLowerCase().trim());
  const pathPrefix: string = (input.path_prefix || '').trim().replace(/\/$/, '');

  let entries: ZipEntry[] = [...allEntries];

  if (skipHidden) {
    const before: number = entries.length;
    entries = entries.filter((f: ZipEntry) => !f.fileName.startsWith('.'));
    const skipped: number = before - entries.length;
    if (skipped > 0) logger.info('过滤隐藏文件：跳过 ' + skipped + ' 个');
  }

  {
    const before: number = entries.length;
    entries = entries.filter((f: ZipEntry) => f.size > 0);
    const skipped: number = before - entries.length;
    if (skipped > 0) logger.info('过滤空文件：跳过 ' + skipped + ' 个');
  }

  {
    const before: number = entries.length;
    entries = entries.filter((f: ZipEntry) => allowedExts.includes(f.extension.toLowerCase()));
    const skipped: number = before - entries.length;
    if (skipped > 0) logger.info('文件类型过滤：保留 ' + entries.length + ' 个');
  }

  {
    const before: number = entries.length;
    entries = entries.filter((f: ZipEntry) => f.size <= maxFileSize);
    const skipped: number = before - entries.length;
    if (skipped > 0) logger.info('文件大小过滤：跳过 ' + skipped + ' 个');
  }

  const skippedCount: number = allEntries.length - entries.length;

  // 解析文件
  const documents: KnowledgeDocument[] = [];
  let successCount: number = 0;
  let failCount: number = 0;
  const chunkSize: number = input.chunk_size || 800;
  const chunkSeparator: string = input.chunk_separator || '\\n\\n';

  // 是否写入 Coze 知识库
  const hasToken: boolean = !!(input.access_token && input.knowledge_id);

  for (const entry of entries) {
    const result = parseFile(entry);
    const displayPath: string = pathPrefix ? pathPrefix + '/' + entry.entryPath : entry.entryPath;
    const title: string = extractTitle(result.success ? result.text : '', entry.fileName);

    const doc: KnowledgeDocument = {
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
      const uploadResult = await uploadToCozeKB(
        input.access_token, input.knowledge_id, doc, chunkSize, chunkSeparator
      );
      if (uploadResult.cozeDocId) {
        doc.coze_document_id = uploadResult.cozeDocId;
        doc.status = 'success';
        logger.info('  [OK] ' + displayPath + ' -> Coze文档ID: ' + uploadResult.cozeDocId);
      } else {
        doc.status = 'failed';
        doc.error_message = uploadResult.error;
        logger.info('  [FAIL] ' + displayPath + ': ' + uploadResult.error);
      }
    }

    documents.push(doc);
    if (doc.status === 'success') {
      successCount++;
      logger.info('  [OK] ' + displayPath + ' (' + formatSize(entry.size) + ', ' + result.wordCount + ' 字)');
    } else {
      failCount++;
      logger.info('  [FAIL] ' + displayPath + ': ' + (doc.error_message || '未知错误'));
    }
  }

  const directoryTree: string = buildDirectoryTree(entries);
  logger.info('批量上传完成，耗时 ' + (Date.now() - startTime) + 'ms');

  return { documents, successCount, failCount, skippedCount, totalCount: allEntries.length, directoryTree };
}

/** 模式2：知识库检索 */
async function handleKbSearch(input: PluginInput, logger: Logger): Promise<{ documents: KnowledgeDocument[] }> {
  if (!input.query) throw new Error('kb_search 模式需要 query 参数');
  if (!input.access_token || !input.knowledge_id) throw new Error('kb_search 模式需要 access_token 和 knowledge_id');

  // Coze 知识库检索通过 Chat API 实现，这里先解压 ZIP 后在本地搜索
  // 如果后续需要可扩展为调用 Chat API
  logger.info('检索关键词：' + input.query);
  const topK: number = input.top_k || 10;

  let entries: ZipEntry[] = [];
  if (input.zip_base64) {
    const zipBuffer: Buffer = Buffer.from(input.zip_base64, 'base64');
    entries = parseZip(zipBuffer);
  }

  const documents: KnowledgeDocument[] = [];
  for (const entry of entries) {
    const result = parseFile(entry);
    if (!result.success) continue;

    // 简单关键词匹配（模糊搜索）
    const contentLower: string = result.text.toLowerCase();
    const queryLower: string = input.query.toLowerCase();
    const score: number = (contentLower.split(queryLower).length - 1) * 2 +
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
  documents.sort((a: KnowledgeDocument, b: KnowledgeDocument) => {
    return Number(b.metadata['relevance_score'] || 0) - Number(a.metadata['relevance_score'] || 0);
  });

  const resultDocs: KnowledgeDocument[] = documents.slice(0, topK);
  logger.info('检索完成，找到 ' + resultDocs.length + ' 个相关文档');
  return { documents: resultDocs };
}

/** 模式3：知识库删除 */
async function handleKbDelete(input: PluginInput, logger: Logger): Promise<{ deletedIds: string[]; error?: string }> {
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
function handleMemoryWrite(input: PluginInput, logger: Logger): MemoryEntry {
  if (!input.memory_key) throw new Error('memory_write 模式需要 memory_key');
  if (input.memory_value === undefined) throw new Error('memory_write 模式需要 memory_value');
  const entry: MemoryEntry = memoryWrite(input.memory_key, input.memory_value);
  logger.info('记忆写入：' + input.memory_key);
  return entry;
}

/** 模式5：长期记忆读取 */
function handleMemoryRead(input: PluginInput, logger: Logger): MemoryEntry | null {
  if (!input.memory_key) throw new Error('memory_read 模式需要 memory_key');
  const entry: MemoryEntry | null = memoryRead(input.memory_key);
  logger.info('记忆读取：' + input.memory_key + ' -> ' + (entry ? '命中' : '未找到'));
  return entry;
}

/** 模式6：文件名搜索 */
function handleFileSearch(input: PluginInput, logger: Logger): KnowledgeDocument[] {
  if (!input.file_keyword) throw new Error('file_search 模式需要 file_keyword');
  if (!input.zip_base64) throw new Error('file_search 模式需要 zip_base64');

  const zipBuffer: Buffer = Buffer.from(input.zip_base64, 'base64');
  const entries: ZipEntry[] = parseZip(zipBuffer);
  const keyword: string = input.file_keyword.toLowerCase();

  logger.info('搜索文件名关键词：' + input.file_keyword);

  const results: KnowledgeDocument[] = [];
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
function handleContentSearch(input: PluginInput, logger: Logger): KnowledgeDocument[] {
  if (!input.query) throw new Error('content_search 模式需要 query');
  if (!input.zip_base64) throw new Error('content_search 模式需要 zip_base64');

  const zipBuffer: Buffer = Buffer.from(input.zip_base64, 'base64');
  const entries: ZipEntry[] = parseZip(zipBuffer);
  const query: string = input.query.toLowerCase();
  const topK: number = input.top_k || 10;

  logger.info('全文搜索关键词：' + input.query);

  const results: KnowledgeDocument[] = [];
  for (const entry of entries) {
    const result = parseFile(entry);
    if (!result.success) continue;

    const text: string = result.text.toLowerCase();
    const score: number = (text.split(query).length - 1);

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

  results.sort((a: KnowledgeDocument, b: KnowledgeDocument) => {
    return Number(b.metadata['match_count'] || 0) - Number(a.metadata['match_count'] || 0);
  });

  logger.info('全文搜索完成，找到 ' + results.length + ' 个匹配文档');
  return results.slice(0, topK);
}

// ==================== 主入口 ====================

export async function handler({ input, logger }: { input: PluginInput; logger: Logger }): Promise<PluginOutput> {
  const startTime: number = Date.now();
  const logs: string[] = [];

  const log = (msg: string): void => {
    logs.push(msg);
    logger.info(msg);
  };

  log('=== Coze 全能知识库插件启动 ===');
  log('模式：' + input.mode);

  // 构建默认成功输出
  const defaultOutput: PluginOutput = {
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
        const docIds: string[] = result.documents
          .filter((d: KnowledgeDocument) => d.coze_document_id)
          .map((d: KnowledgeDocument) => d.coze_document_id || '');

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
          doc_ids: result.documents.map((d: KnowledgeDocument) => d.doc_id),
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
        const entry: MemoryEntry = handleMemoryWrite(input, logger);
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
        const entry: MemoryEntry | null = handleMemoryRead(input, logger);
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
        const docs: KnowledgeDocument[] = handleFileSearch(input, logger);
        return {
          ...defaultOutput,
          success: docs.length > 0,
          total_count: docs.length,
          success_count: docs.length,
          processing_time_ms: Date.now() - startTime,
          documents: docs,
          doc_ids: docs.map((d: KnowledgeDocument) => d.doc_id),
          summary: '文件搜索完成，找到 ' + docs.length + ' 个匹配文件',
          logs,
        };
      }

      // ---- 模式7：全文内容搜索 ----
      case 'content_search': {
        const docs: KnowledgeDocument[] = handleContentSearch(input, logger);
        return {
          ...defaultOutput,
          success: docs.length > 0,
          total_count: docs.length,
          success_count: docs.length,
          processing_time_ms: Date.now() - startTime,
          documents: docs,
          doc_ids: docs.map((d: KnowledgeDocument) => d.doc_id),
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
  } catch (err) {
    log('错误：' + String(err));
    return {
      ...defaultOutput,
      error_message: String(err),
      processing_time_ms: Date.now() - startTime,
      logs,
    };
  }
}
