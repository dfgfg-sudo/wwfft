/**
 * 安全模块
 * 提供文件类型校验、路径净化、编码检测等安全功能
 */

import type { SecurityConfig } from './types';

/** 全局安全配置 */
export const SECURITY_CONFIG: SecurityConfig = {
  allowedExtensions: [
    '.md', '.markdown', '.txt', '.text',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.csv', '.json', '.xml', '.html', '.htm', '.rtf', '.log',
    '.yaml', '.yml', '.ini', '.cfg', '.conf', '.toml', '.properties',
    '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h',
    '.sh', '.bat', '.ps1', '.sql',
  ],
  forbiddenPathPatterns: [
    /\.\.[\/\\]/,          // 路径穿越 ../
    /^\.\.[\/\\]?/,        // 根路径穿越 ../
    /[\/\\]\.\.[\/\\]?/,   // 中间穿越 /../
    /[<>:"|?*]/,           // Windows 非法字符
    /\x00/,                // NULL 字节注入
  ],
  maxFileSize: 20 * 1024 * 1024,
  maxZipSize: 500 * 1024 * 1024,
  forbiddenFileNamePatterns: [
    /^\./,                 // 隐藏文件
    /\.exe$/i,             // 可执行文件
    /\.msi$/i,
    /\.bat$/i,             // 虽然在白名单中也保留检查
    /\.cmd$/i,
    /\.sh$/i,
    /\.ps1$/i,
    /\.dll$/i,
    /\.so$/i,
    /\.dylib$/i,
    /\.app$/i,
    /\.deb$/i,
    /\.rpm$/i,
    /\.sys$/i,
    /\.com$/i,
    /\.vbs$/i,
    /\.wsf$/i,
    /\.jar$/i,
    /\.war$/i,
    /\.class$/i,
  ],
};

/**
 * 验证文件类型是否在允许列表中
 * @param fileName - 文件名
 * @param customAllowed - 自定义白名单（可选）
 * @returns 是否允许
 */
export function validateFileType(
  fileName: string,
  customAllowed?: string[]
): boolean {
  const ext = getExtension(fileName).toLowerCase();

  if (!ext) return false;

  const allowed = customAllowed || SECURITY_CONFIG.allowedExtensions;
  return allowed.includes(ext);
}

/**
 * 净化文件路径，防止路径穿越攻击
 * @param filePath - 原始路径
 * @returns 净化后的安全路径
 * @throws 如果路径不合法则抛出错误
 */
export function sanitizePath(filePath: string): string {
  // 统一分隔符
  let safe = filePath.replace(/\\/g, '/');

  // 检查所有禁止模式
  for (const pattern of SECURITY_CONFIG.forbiddenPathPatterns) {
    if (pattern.test(safe)) {
      throw new Error(`路径安全检查失败：检测到非法路径模式 "${filePath}"`);
    }
  }

  // 移除开头的 /
  safe = safe.replace(/^\/+/, '');

  // 压缩多余斜杠
  safe = safe.replace(/\/{2,}/g, '/');

  // 去除首尾空白
  safe = safe.trim();

  if (!safe || safe === '.') {
    throw new Error(`路径为空或无效："${filePath}"`);
  }

  return safe;
}

/**
 * 检测文件编码
 * 支持检测 UTF-8 (带/不带 BOM)、GBK/GB2312/GB18030、UTF-16 LE/BE
 *
 * @param buffer - 文件内容 Buffer
 * @returns 检测到的编码名称
 */
export function detectEncoding(buffer: Buffer): string {
  if (buffer.length === 0) return 'utf-8';

  // UTF-8 BOM
  if (buffer.length >= 3 &&
      buffer[0] === 0xEF &&
      buffer[1] === 0xBB &&
      buffer[2] === 0xBF) {
    return 'utf-8-bom';
  }

  // UTF-16 LE BOM
  if (buffer.length >= 2 &&
      buffer[0] === 0xFF &&
      buffer[1] === 0xFE) {
    return 'utf-16le';
  }

  // UTF-16 BE BOM
  if (buffer.length >= 2 &&
      buffer[0] === 0xFE &&
      buffer[1] === 0xFF) {
    return 'utf-16be';
  }

  // 尝试判断是否为有效 UTF-8
  if (isValidUtf8(buffer)) {
    return 'utf-8';
  }

  // 默认假设为 GBK（中文环境常见）
  return 'gbk';
}

/**
 * 检查 Buffer 是否为有效 UTF-8 编码
 */
function isValidUtf8(buffer: Buffer): boolean {
  let i = 0;
  while (i < buffer.length) {
    const byte = buffer[i];

    if (byte <= 0x7F) {
      // ASCII
      i++;
    } else if ((byte & 0xE0) === 0xC0) {
      // 2 字节序列
      if (i + 1 >= buffer.length || (buffer[i + 1] & 0xC0) !== 0x80) return false;
      const cp = ((byte & 0x1F) << 6) | (buffer[i + 1] & 0x3F);
      if (cp < 0x80) return false; // 过长编码
      i += 2;
    } else if ((byte & 0xF0) === 0xE0) {
      // 3 字节序列
      if (i + 2 >= buffer.length ||
          (buffer[i + 1] & 0xC0) !== 0x80 ||
          (buffer[i + 2] & 0xC0) !== 0x80) return false;
      const cp = ((byte & 0x0F) << 12) |
                  ((buffer[i + 1] & 0x3F) << 6) |
                  (buffer[i + 2] & 0x3F);
      if (cp < 0x800 || (cp >= 0xD800 && cp <= 0xDFFF)) return false;
      i += 3;
    } else if ((byte & 0xF8) === 0xF0) {
      // 4 字节序列
      if (i + 3 >= buffer.length ||
          (buffer[i + 1] & 0xC0) !== 0x80 ||
          (buffer[i + 2] & 0xC0) !== 0x80 ||
          (buffer[i + 3] & 0xC0) !== 0x80) return false;
      const cp = ((byte & 0x07) << 18) |
                  ((buffer[i + 1] & 0x3F) << 12) |
                  ((buffer[i + 2] & 0x3F) << 6) |
                  (buffer[i + 3] & 0x3F);
      if (cp < 0x10000 || cp > 0x10FFFF) return false;
      i += 4;
    } else {
      return false;
    }
  }
  return true;
}

/**
 * 提取文件扩展名
 */
export function getExtension(fileName: string): string {
  const lastDot = fileName.lastIndexOf('.');
  if (lastDot === -1 || lastDot === fileName.length - 1) return '';
  return fileName.substring(lastDot).toLowerCase();
}

/**
 * 生成唯一文档 ID
 */
export function generateDocId(path: string): string {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  const hash = simpleHash(path);
  return `doc_${hash}_${timestamp}_${random}`;
}

/**
 * 简单哈希函数（用于生成可读 ID，非加密用途）
 */
function simpleHash(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // 转为 32 位整数
  }
  return Math.abs(hash).toString(36);
}

/**
 * 从文件内容首行提取标题
 */
export function extractTitle(content: string, fileName: string): string {
  if (!content || content.trim().length === 0) {
    return fileName.replace(/\.[^.]+$/, ''); // 去掉扩展名
  }

  const lines = content.split('\n').map(l => l.trim()).filter(Boolean);
  if (lines.length === 0) return fileName;

  // Markdown 标题
  const mdTitle = lines.find(l => /^#{1,6}\s+/.test(l));
  if (mdTitle) {
    return mdTitle.replace(/^#{1,6}\s+/, '').trim();
  }

  // HTML title 标签
  const htmlMatch = content.match(/<title[^>]*>(.*?)<\/title>/is);
  if (htmlMatch && htmlMatch[1]) {
    return htmlMatch[1].trim();
  }

  // 第一行作为标题（截取前 100 字符）
  const firstLine = lines[0];
  return firstLine.length > 100 ? firstLine.substring(0, 100) + '...' : firstLine;
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i];
}
