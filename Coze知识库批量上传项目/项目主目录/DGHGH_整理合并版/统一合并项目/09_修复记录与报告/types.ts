/**
 * 类型定义文件
 * 定义插件中所有核心数据结构
 */

/** ZIP 压缩包内单个文件的信息 */
export interface ZipFileInfo {
  /** 文件在 ZIP 内的相对路径（如 "projectA/docs/README.md"） */
  entryPath: string;
  /** 文件名（如 "README.md"） */
  fileName: string;
  /** 文件扩展名（如 ".md"） */
  extension: string;
  /** 文件大小（字节） */
  size: number;
  /** 是否为目录 */
  isDirectory: boolean;
  /** 文件内容 Buffer */
  data: Buffer;
  /** 编码检测结果 */
  encoding: string;
}

/** 文件解析结果 */
export interface ParseResult {
  /** 是否解析成功 */
  success: boolean;
  /** 提取的纯文本内容 */
  text: string;
  /** 原始格式标记（markdown/html/text/plain） */
  format: string;
  /** 元数据（标题、作者等，如有） */
  metadata: Record<string, string>;
  /** 错误信息（解析失败时） */
  error?: string;
  /** 字数统计 */
  wordCount: number;
}

/** 知识库文档（最终输出结构） */
export interface KnowledgeDocument {
  /** 文档唯一标识 */
  id: string;
  /** 文档标题（取自文件名或首行） */
  title: string;
  /** 原始文件在 ZIP 中的路径 */
  sourcePath: string;
  /** 文档在知识库中的显示路径 */
  path: string;
  /** 纯文本内容 */
  content: string;
  /** 文件格式 */
  format: string;
  /** 文件大小（字节） */
  fileSize: number;
  /** 字数统计 */
  wordCount: number;
  /** 是否处理成功 */
  success: boolean;
  /** 失败原因 */
  errorMessage?: string;
  /** 处理时间戳 */
  processedAt: string;
}

/** 批量上传输入参数 */
export interface BatchUploadInput {
  /** ZIP 文件的 Buffer 数据 */
  zipBuffer: Buffer | Uint8Array;
  /** 可选配置 */
  options: BatchUploadOptions;
}

/** 批量上传配置选项 */
export interface BatchUploadOptions {
  /** 允许的文件扩展名白名单（为空则使用默认） */
  allowedExtensions: string[];
  /** 单个文件最大大小（字节），默认 20MB */
  maxFileSize: number;
  /** ZIP 包最大总大小（字节），默认 500MB */
  maxZipSize: number;
  /** 路径前缀（可选，用于在知识库中统一分类） */
  pathPrefix: string;
  /** 是否在文件名冲突时覆盖，默认 false（重命名） */
  overwriteOnConflict: boolean;
  /** 是否跳过隐藏文件（以 . 开头），默认 true */
  skipHiddenFiles: boolean;
  /** 是否跳过空文件，默认 true */
  skipEmptyFiles: boolean;
  /** 并发处理数，默认 5 */
  concurrency: number;
}

/** 批量上传结果 */
export interface BatchUploadResult {
  /** 是否全部成功 */
  success: boolean;
  /** 成功处理的文档列表 */
  documents: KnowledgeDocument[];
  /** 成功计数 */
  successCount: number;
  /** 失败计数 */
  failCount: number;
  /** 跳过计数（因文件类型/大小/隐藏等原因） */
  skippedCount: number;
  /** 总文件数 */
  totalCount: number;
  /** 目录树结构 */
  directoryTree: string;
  /** 总处理时间（毫秒） */
  processingTimeMs: number;
  /** 详细日志 */
  logs: string[];
  /** ZIP 内原始目录结构摘要 */
  zipStructureSummary: string;
}

/** 安全配置 */
export interface SecurityConfig {
  /** 默认允许的文件扩展名 */
  allowedExtensions: string[];
  /** 禁止的路径模式 */
  forbiddenPathPatterns: RegExp[];
  /** 最大文件大小（字节） */
  maxFileSize: number;
  /** 最大 ZIP 总大小（字节） */
  maxZipSize: number;
  /** 禁止的文件名模式 */
  forbiddenFileNamePatterns: RegExp[];
}

/** 默认配置常量 */
export const DEFAULT_OPTIONS: BatchUploadOptions = {
  allowedExtensions: [
    '.md', '.markdown',
    '.txt', '.text',
    '.pdf',
    '.doc', '.docx',
    '.xls', '.xlsx',
    '.ppt', '.pptx',
    '.csv',
    '.json', '.xml',
    '.html', '.htm',
    '.rtf',
    '.log',
    '.yaml', '.yml',
    '.ini', '.cfg', '.conf',
    '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
    '.sh', '.bat', '.ps1',
    '.sql',
    '.toml',
    '.properties',
  ],
  maxFileSize: 20 * 1024 * 1024,   // 20MB
  maxZipSize: 500 * 1024 * 1024,  // 500MB
  pathPrefix: '',
  overwriteOnConflict: false,
  skipHiddenFiles: true,
  skipEmptyFiles: true,
  concurrency: 5,
};
