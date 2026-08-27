/**
 * Coze 批量知识库上传插件 - 入口文件
 *
 * 功能概述：
 *   1. 接收用户上传的 ZIP 压缩包（含一个或多个文件夹的完整目录）
 *   2. 安全解压并遍历所有文件，保留原始目录结构
 *   3. 按文件类型提取文本内容，生成知识库文档
 *   4. 输出结构化结果，供 Coze 工作流知识库节点直接使用
 *
 * 安全保障：
 *   - 只读 ZIP，不修改源文件
 *   - 文件类型白名单过滤，拒绝危险格式
 *   - 路径穿越防御，禁止 ../ 等非法路径
 *   - 内存控制，大文件分块处理
 *   - 编码自动检测，乱码自动修复
 */

import {
  KnowledgeBatchUploader,
  type BatchUploadInput,
  type BatchUploadResult,
  type KnowledgeDocument,
} from './uploader';
import {
  SECURITY_CONFIG,
  validateFileType,
  sanitizePath,
  detectEncoding,
} from './security';
import { FileParser, type ParseResult } from './parser';
import { ZipProcessor, type ZipFileInfo } from './zip-processor';

// ========== 导出所有公共模块 ==========

export {
  KnowledgeBatchUploader,
  FileParser,
  ZipProcessor,
  SECURITY_CONFIG,
  validateFileType,
  sanitizePath,
  detectEncoding,
};

export type {
  BatchUploadInput,
  BatchUploadResult,
  KnowledgeDocument,
  ParseResult,
  ZipFileInfo,
};

// ========== 便捷函数：一键调用 ==========

/**
 * 一键批量处理 ZIP 包，提取知识库文档
 *
 * @param zipBuffer - ZIP 文件的 Buffer 数据
 * @param options - 可选配置（覆盖策略、文件过滤等）
 * @returns 处理结果，包含所有知识库文档和统计信息
 *
 * @example
 * ```typescript
 * import { batchUploadFromZip } from 'coze-knowledge-batch-upload';
 * import * as fs from 'fs';
 *
 * const zipData = fs.readFileSync('my-folder.zip');
 * const result = await batchUploadFromZip(zipData, {
 *   allowedExtensions: ['.md', '.txt', '.pdf', '.docx'],
 *   maxFileSize: 10 * 1024 * 1024, // 10MB
 * });
 *
 * console.log(`成功处理 ${result.successCount} 个文档`);
 * result.documents.forEach(doc => {
 *   console.log(`[${doc.path}] ${doc.title} (${doc.wordCount} 字)`);
 * });
 * ```
 */
export async function batchUploadFromZip(
  zipBuffer: Buffer | Uint8Array,
  options?: Partial<BatchUploadInput['options']>
): Promise<BatchUploadResult> {
  const uploader = new KnowledgeBatchUploader();
  return uploader.processZip(zipBuffer, options);
}
