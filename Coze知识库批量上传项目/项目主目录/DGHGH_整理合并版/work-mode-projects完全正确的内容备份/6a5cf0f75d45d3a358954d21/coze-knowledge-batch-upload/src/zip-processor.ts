/**
 * ZIP 处理模块
 * 负责 ZIP 压缩包的安全解压、遍历、文件提取
 */

import * as path from 'path';
import AdmZip from 'adm-zip';
import type { ZipFileInfo } from './types';
export type { ZipFileInfo };
import { sanitizePath, detectEncoding, getExtension } from './security';

/** ZIP 处理器 */
export class ZipProcessor {
  private zip: AdmZip | null = null;
  private entries: ZipFileInfo[] = [];

  /**
   * 加载 ZIP 文件
   * @param zipBuffer - ZIP 文件 Buffer
   * @throws 如果 ZIP 格式无效或超过大小限制
   */
  load(zipBuffer: Buffer | Uint8Array): void {
    try {
      this.zip = new AdmZip(Buffer.from(zipBuffer));
      this.entries = [];
      const allEntries = this.zip.getEntries();

      for (const entry of allEntries) {
        // 跳过目录条目
        if (entry.isDirectory) continue;

        // 跳过 macOS 资源文件
        if (entry.entryName.startsWith('__MACOSX/')) continue;
        if (entry.entryName.includes('/._')) continue;

        // 跳过 .DS_Store
        const fileName = entry.entryName.split('/').pop() || '';
        if (fileName === '.DS_Store' || fileName === 'Thumbs.db') continue;

        try {
          const safePath = sanitizePath(entry.entryName);
          const data = entry.getData();

          const fileInfo: ZipFileInfo = {
            entryPath: safePath,
            fileName: fileName,
            extension: getExtension(fileName),
            size: data.length,
            isDirectory: false,
            data: Buffer.from(data),
            encoding: detectEncoding(Buffer.from(data)),
          };

          this.entries.push(fileInfo);
        } catch (err) {
          // 跳过路径不安全的条目，记录警告
          console.warn(`跳过不安全的 ZIP 条目：${entry.entryName}`, err);
        }
      }
    } catch (err) {
      throw new Error(
        `ZIP 文件解析失败：${err instanceof Error ? err.message : String(err)}`
      );
    }
  }

  /**
   * 获取所有文件条目
   */
  getEntries(): ZipFileInfo[] {
    return [...this.entries];
  }

  /**
   * 按扩展名过滤文件
   */
  filterByExtension(extensions: string[]): ZipFileInfo[] {
    const lower = extensions.map(e => e.toLowerCase());
    return this.entries.filter(f => lower.includes(f.extension.toLowerCase()));
  }

  /**
   * 按大小过滤文件
   * @param maxSize - 最大字节数
   */
  filterBySize(maxSize: number): ZipFileInfo[] {
    return this.entries.filter(f => f.size <= maxSize);
  }

  /**
   * 过滤隐藏文件（以 . 开头）
   */
  filterHidden(skip: boolean): ZipFileInfo[] {
    if (!skip) return this.entries;
    return this.entries.filter(f => !f.fileName.startsWith('.'));
  }

  /**
   * 过滤空文件
   */
  filterEmpty(skip: boolean): ZipFileInfo[] {
    if (!skip) return this.entries;
    return this.entries.filter(f => f.size > 0);
  }

  /**
   * 获取目录树结构
   * @returns 格式化的目录树字符串
   */
  getDirectoryTree(): string {
    const dirs = new Set<string>();
    for (const entry of this.entries) {
      const parts = entry.entryPath.split('/');
      if (parts.length > 1) {
        for (let i = 1; i < parts.length; i++) {
          dirs.add(parts.slice(0, i).join('/'));
        }
      }
    }

    const sorted = Array.from(dirs).sort();
    if (sorted.length === 0) return '(根目录，无子文件夹)';

    const lines: string[] = ['ZIP 目录结构：'];
    const treeMap = new Map<string, string[]>();

    for (const entry of this.entries) {
      const dir = path.dirname(entry.entryPath);
      if (!treeMap.has(dir)) treeMap.set(dir, []);
      treeMap.get(dir)!.push(entry.fileName);
    }

    for (const dir of sorted) {
      const files = treeMap.get(dir) || [];
      const indent = dir.split('/').length - 1;
      const prefix = '  '.repeat(indent) + (indent === 0 ? '├─ ' : '├─ ');
      lines.push(`${prefix}${dir.split('/').pop()}/`);
      for (const file of files.sort()) {
        lines.push(`${'  '.repeat(indent + 1)}├─ ${file}`);
      }
    }

    return lines.join('\n');
  }

  /**
   * 获取文件总数
   */
  getFileCount(): number {
    return this.entries.length;
  }

  /**
   * 获取总大小
   */
  getTotalSize(): number {
    return this.entries.reduce((sum, f) => sum + f.size, 0);
  }

  /**
   * 获取统计摘要
   */
  getSummary(): string {
    const extMap = new Map<string, number>();
    for (const entry of this.entries) {
      const ext = entry.extension || '(无扩展名)';
      extMap.set(ext, (extMap.get(ext) || 0) + 1);
    }

    const stats = Array.from(extMap.entries())
      .sort((a, b) => b[1] - a[1])
      .map(([ext, count]) => `  ${ext}: ${count} 个文件`)
      .join('\n');

    return [
      `ZIP 文件统计：`,
      `  总文件数：${this.entries.length}`,
      `  总大小：${this.formatSize(this.getTotalSize())}`,
      `  文件类型分布：`,
      stats || '  (空)',
    ].join('\n');
  }

  private formatSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    const k = 1024;
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i];
  }
}
