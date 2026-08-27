/**
 * 文件解析模块
 * 支持多种格式的文本提取：Markdown、HTML、JSON、XML、CSV、代码源文件等
 */
import type { ParseResult, ZipFileInfo } from './types';
export type { ParseResult };
/** 文件解析器 */
export declare class FileParser {
    /**
     * 解析单个文件，提取纯文本内容
     * @param file - ZIP 文件信息
     * @returns 解析结果
     */
    parse(file: ZipFileInfo): ParseResult;
    /** Markdown 解析：保留标题结构，提取纯文本 */
    private parseMarkdown;
    /** HTML 解析：去除标签，提取文本 */
    private parseHtml;
    /** JSON 解析：格式化为可读文本 */
    private parseJson;
    /** XML 解析：去除标签，提取文本 */
    private parseXml;
    /** CSV 解析：表格格式化 */
    private parseCsv;
    /** 配置文件解析：保持原始格式 */
    private parseConfig;
    /** 纯文本解析 */
    private parseText;
    /** 代码文件解析：保留原始代码 */
    private parseCode;
    /** 二进制文档处理（PDF/Word/Excel/PPT/RTF）
     *  注意：在纯 Node.js 环境中，完整解析二进制文档需要额外依赖
     *  这里提供基本处理：记录文件信息，提取可能的文本片段
     */
    private parseBinaryDocument;
    /** 从二进制数据中提取可读文本片段 */
    private extractTextSnippets;
    /** 解码 Buffer 为字符串，支持多种编码 */
    private decodeBuffer;
    /** 字数统计（支持中英文混合） */
    private countWords;
}
//# sourceMappingURL=parser.d.ts.map