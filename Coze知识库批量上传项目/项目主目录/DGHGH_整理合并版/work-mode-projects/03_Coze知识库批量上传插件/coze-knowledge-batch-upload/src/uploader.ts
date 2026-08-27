/**
 * 批量上传核心模块
 * 编排 ZIP 解压 -> 文件过滤 -> 文本提取 -> 文档生成的完整流程
 */

import type {
  BatchUploadInput,
  BatchUploadOptions,
  BatchUploadResult,
  KnowledgeDocument,
} from './types';
import { DEFAULT_OPTIONS } from './types';
export type { BatchUploadInput, BatchUploadResult, KnowledgeDocument };
import { ZipProcessor } from './zip-processor';
import { FileParser } from './parser';
import {
  validateFileType,
  generateDocId,
  extractTitle,
  formatFileSize,
} from './security';

/** 批量知识库上传器 */
export class KnowledgeBatchUploader {
  private zipProcessor: ZipProcessor;
  private fileParser: FileParser;
  private logs: string[] = [];

  constructor() {
    this.zipProcessor = new ZipProcessor();
    this.fileParser = new FileParser();
  }

  /**
   * 处理 ZIP 压缩包，批量提取知识库文档
   *
   * @param zipBuffer - ZIP 文件 Buffer
   * @param customOptions - 自定义配置（可选，覆盖默认值）
   * @returns 完整的批量上传结果
   */
  async processZip(
    zipBuffer: Buffer | Uint8Array,
    customOptions?: Partial<BatchUploadOptions>
  ): Promise<BatchUploadResult> {
    const startTime = Date.now();
    this.logs = [];

    // 合并配置
    const options: BatchUploadOptions = {
      ...DEFAULT_OPTIONS,
      ...customOptions,
    };

    this.log('开始处理 ZIP 压缩包...');
    this.log(`配置：最大文件 ${formatFileSize(options.maxFileSize)}，最大 ZIP ${formatFileSize(options.maxZipSize)}`);

    // 1. 验证 ZIP 大小
    const totalSize = zipBuffer.length;
    if (totalSize > options.maxZipSize) {
      return this.buildErrorResult(
        0,
        `ZIP 文件过大：${formatFileSize(totalSize)}，超过限制 ${formatFileSize(options.maxZipSize)}`
      );
    }

    // 2. 加载并解析 ZIP
    try {
      this.zipProcessor.load(zipBuffer);
    } catch (err) {
      return this.buildErrorResult(
        0,
        `ZIP 解析失败：${err instanceof Error ? err.message : String(err)}`
      );
    }

    const allEntries = this.zipProcessor.getEntries();
    this.log(`ZIP 解析完成，共 ${allEntries.length} 个文件条目`);
    this.log(this.zipProcessor.getSummary());

    // 3. 逐步过滤（在局部数组上链式过滤）
    let entries = [...allEntries];

    // 3a. 跳过隐藏文件
    if (options.skipHiddenFiles) {
      const before = entries.length;
      entries = entries.filter(f => !f.fileName.startsWith('.'));
      const skipped = before - entries.length;
      if (skipped > 0) {
        this.log(`过滤隐藏文件：跳过 ${skipped} 个`);
      }
    }

    // 3b. 跳过空文件
    if (options.skipEmptyFiles) {
      const before = entries.length;
      entries = entries.filter(f => f.size > 0);
      const skipped = before - entries.length;
      if (skipped > 0) {
        this.log(`过滤空文件：跳过 ${skipped} 个`);
      }
    }

    // 3c. 按扩展名过滤
    const allowedLower = options.allowedExtensions.map(e => e.toLowerCase());
    const beforeExt = entries.length;
    entries = entries.filter(f => allowedLower.includes(f.extension.toLowerCase()));
    const skippedExt = beforeExt - entries.length;
    if (skippedExt > 0) {
      this.log(`文件类型过滤：保留 ${entries.length} 个（跳过 ${skippedExt} 个不支持的格式）`);
    }

    // 3d. 按大小过滤
    const beforeSize = entries.length;
    entries = entries.filter(f => f.size <= options.maxFileSize);
    const skippedSize = beforeSize - entries.length;
    if (skippedSize > 0) {
      this.log(`文件大小过滤：跳过 ${skippedSize} 个超限文件`);
    }

    const skippedTotal = allEntries.length - entries.length;

    // 4. 逐文件解析，生成知识库文档
    const documents: KnowledgeDocument[] = [];
    let successCount = 0;
    let failCount = 0;

    for (const entry of entries) {
      try {
        const doc = this.processEntry(entry, options);
        documents.push(doc);

        if (doc.success) {
          successCount++;
          this.log(`  [OK] ${doc.path} (${formatFileSize(doc.fileSize)}, ${doc.wordCount} 字)`);
        } else {
          failCount++;
          this.log(`  [FAIL] ${doc.path}: ${doc.errorMessage}`);
        }
      } catch (err) {
        failCount++;
        const errorMsg = err instanceof Error ? err.message : String(err);
        this.log(`  [ERROR] ${entry.entryPath}: ${errorMsg}`);

        documents.push({
          id: generateDocId(entry.entryPath),
          title: entry.fileName,
          sourcePath: entry.entryPath,
          path: this.buildDisplayPath(entry.entryPath, options.pathPrefix),
          content: '',
          format: entry.extension,
          fileSize: entry.size,
          wordCount: 0,
          success: false,
          errorMessage: errorMsg,
          processedAt: new Date().toISOString(),
        });
      }
    }

    const processingTimeMs = Date.now() - startTime;

    // 5. 构建结果
    this.log(`处理完成！成功 ${successCount}，失败 ${failCount}，跳过 ${skippedTotal}，耗时 ${processingTimeMs}ms`);

    return {
      success: failCount === 0 && successCount > 0,
      documents,
      successCount,
      failCount,
      skippedCount: skippedTotal,
      totalCount: allEntries.length,
      directoryTree: this.zipProcessor.getDirectoryTree(),
      processingTimeMs,
      logs: this.logs,
      zipStructureSummary: this.zipProcessor.getSummary(),
    };
  }

  /**
   * 处理单个 ZIP 条目
   */
  private processEntry(
    entry: Parameters<typeof this.fileParser.parse>[0],
    options: BatchUploadOptions
  ): KnowledgeDocument {
    // 解析文件内容
    const parseResult = this.fileParser.parse(entry);

    // 构建文档路径（保留目录结构）
    const displayPath = this.buildDisplayPath(entry.entryPath, options.pathPrefix);

    if (!parseResult.success) {
      return {
        id: generateDocId(entry.entryPath),
        title: entry.fileName,
        sourcePath: entry.entryPath,
        path: displayPath,
        content: '',
        format: entry.extension,
        fileSize: entry.size,
        wordCount: 0,
        success: false,
        errorMessage: parseResult.error || '未知解析错误',
        processedAt: new Date().toISOString(),
      };
    }

    // 提取标题
    const title = extractTitle(parseResult.text, entry.fileName);

    return {
      id: generateDocId(entry.entryPath),
      title,
      sourcePath: entry.entryPath,
      path: displayPath,
      content: parseResult.text,
      format: parseResult.format,
      fileSize: entry.size,
      wordCount: parseResult.wordCount,
      success: true,
      processedAt: new Date().toISOString(),
    };
  }

  /**
   * 构建知识库显示路径
   * 保留原始目录结构，可选添加前缀
   */
  private buildDisplayPath(entryPath: string, prefix: string): string {
    const cleanPath = entryPath.replace(/\\/g, '/');
    if (prefix && prefix.trim()) {
      return `${prefix.trim().replace(/\/$/, '')}/${cleanPath}`;
    }
    return cleanPath;
  }

  /**
   * 构建错误结果
   */
  private buildErrorResult(totalCount: number, errorMessage: string): BatchUploadResult {
    return {
      success: false,
      documents: [],
      successCount: 0,
      failCount: 0,
      skippedCount: totalCount,
      totalCount,
      directoryTree: '',
      processingTimeMs: 0,
      logs: [errorMessage],
      zipStructureSummary: '',
    };
  }

  /**
   * 记录日志
   */
  private log(message: string): void {
    this.logs.push(message);
  }
}
