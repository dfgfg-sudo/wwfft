/**
 * 安全模块
 * 提供文件类型校验、路径净化、编码检测等安全功能
 */
import type { SecurityConfig } from './types';
/** 全局安全配置 */
export declare const SECURITY_CONFIG: SecurityConfig;
/**
 * 验证文件类型是否在允许列表中
 * @param fileName - 文件名
 * @param customAllowed - 自定义白名单（可选）
 * @returns 是否允许
 */
export declare function validateFileType(fileName: string, customAllowed?: string[]): boolean;
/**
 * 净化文件路径，防止路径穿越攻击
 * @param filePath - 原始路径
 * @returns 净化后的安全路径
 * @throws 如果路径不合法则抛出错误
 */
export declare function sanitizePath(filePath: string): string;
/**
 * 检测文件编码
 * 支持检测 UTF-8 (带/不带 BOM)、GBK/GB2312/GB18030、UTF-16 LE/BE
 *
 * @param buffer - 文件内容 Buffer
 * @returns 检测到的编码名称
 */
export declare function detectEncoding(buffer: Buffer): string;
/**
 * 提取文件扩展名
 */
export declare function getExtension(fileName: string): string;
/**
 * 生成唯一文档 ID
 */
export declare function generateDocId(path: string): string;
/**
 * 从文件内容首行提取标题
 */
export declare function extractTitle(content: string, fileName: string): string;
/**
 * 格式化文件大小
 */
export declare function formatFileSize(bytes: number): string;
//# sourceMappingURL=security.d.ts.map