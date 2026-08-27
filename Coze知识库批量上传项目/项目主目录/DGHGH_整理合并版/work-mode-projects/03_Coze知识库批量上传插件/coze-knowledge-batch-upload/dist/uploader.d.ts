/**
 * 批量上传核心模块
 * 编排 ZIP 解压 -> 文件过滤 -> 文本提取 -> 文档生成的完整流程
 */
import type { BatchUploadInput, BatchUploadOptions, BatchUploadResult, KnowledgeDocument } from './types';
export type { BatchUploadInput, BatchUploadResult, KnowledgeDocument };
/** 批量知识库上传器 */
export declare class KnowledgeBatchUploader {
    private zipProcessor;
    private fileParser;
    private logs;
    constructor();
    /**
     * 处理 ZIP 压缩包，批量提取知识库文档
     *
     * @param zipBuffer - ZIP 文件 Buffer
     * @param customOptions - 自定义配置（可选，覆盖默认值）
     * @returns 完整的批量上传结果
     */
    processZip(zipBuffer: Buffer | Uint8Array, customOptions?: Partial<BatchUploadOptions>): Promise<BatchUploadResult>;
    /**
     * 处理单个 ZIP 条目
     */
    private processEntry;
    /**
     * 构建知识库显示路径
     * 保留原始目录结构，可选添加前缀
     */
    private buildDisplayPath;
    /**
     * 构建错误结果
     */
    private buildErrorResult;
    /**
     * 记录日志
     */
    private log;
}
//# sourceMappingURL=uploader.d.ts.map