/**
 * ZIP 处理模块
 * 负责 ZIP 压缩包的安全解压、遍历、文件提取
 */
import type { ZipFileInfo } from './types';
export type { ZipFileInfo };
/** ZIP 处理器 */
export declare class ZipProcessor {
    private zip;
    private entries;
    /**
     * 加载 ZIP 文件
     * @param zipBuffer - ZIP 文件 Buffer
     * @throws 如果 ZIP 格式无效或超过大小限制
     */
    load(zipBuffer: Buffer | Uint8Array): void;
    /**
     * 获取所有文件条目
     */
    getEntries(): ZipFileInfo[];
    /**
     * 按扩展名过滤文件
     */
    filterByExtension(extensions: string[]): ZipFileInfo[];
    /**
     * 按大小过滤文件
     * @param maxSize - 最大字节数
     */
    filterBySize(maxSize: number): ZipFileInfo[];
    /**
     * 过滤隐藏文件（以 . 开头）
     */
    filterHidden(skip: boolean): ZipFileInfo[];
    /**
     * 过滤空文件
     */
    filterEmpty(skip: boolean): ZipFileInfo[];
    /**
     * 获取目录树结构
     * @returns 格式化的目录树字符串
     */
    getDirectoryTree(): string;
    /**
     * 获取文件总数
     */
    getFileCount(): number;
    /**
     * 获取总大小
     */
    getTotalSize(): number;
    /**
     * 获取统计摘要
     */
    getSummary(): string;
    private formatSize;
}
//# sourceMappingURL=zip-processor.d.ts.map