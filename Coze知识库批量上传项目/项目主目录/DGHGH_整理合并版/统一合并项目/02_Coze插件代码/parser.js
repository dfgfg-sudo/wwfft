"use strict";
/**
 * 文件解析模块
 * 支持多种格式的文本提取：Markdown、HTML、JSON、XML、CSV、代码源文件等
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.FileParser = void 0;
/** 文件解析器 */
class FileParser {
    /**
     * 解析单个文件，提取纯文本内容
     * @param file - ZIP 文件信息
     * @returns 解析结果
     */
    parse(file) {
        try {
            switch (file.extension) {
                case '.md':
                case '.markdown':
                    return this.parseMarkdown(file);
                case '.html':
                case '.htm':
                    return this.parseHtml(file);
                case '.json':
                    return this.parseJson(file);
                case '.xml':
                    return this.parseXml(file);
                case '.csv':
                    return this.parseCsv(file);
                case '.yaml':
                case '.yml':
                case '.toml':
                case '.ini':
                case '.cfg':
                case '.conf':
                case '.properties':
                    return this.parseConfig(file);
                case '.txt':
                case '.text':
                case '.log':
                    return this.parseText(file);
                case '.py':
                case '.js':
                case '.ts':
                case '.java':
                case '.go':
                case '.rs':
                case '.c':
                case '.cpp':
                case '.h':
                case '.sh':
                case '.bat':
                case '.ps1':
                case '.sql':
                    return this.parseCode(file);
                case '.pdf':
                case '.doc':
                case '.docx':
                case '.xls':
                case '.xlsx':
                case '.ppt':
                case '.pptx':
                case '.rtf':
                    return this.parseBinaryDocument(file);
                default:
                    return this.parseText(file);
            }
        }
        catch (err) {
            return {
                success: false,
                text: '',
                format: 'unknown',
                metadata: {},
                error: `解析失败：${err instanceof Error ? err.message : String(err)}`,
                wordCount: 0,
            };
        }
    }
    /** Markdown 解析：保留标题结构，提取纯文本 */
    parseMarkdown(file) {
        const text = this.decodeBuffer(file.data, file.encoding);
        // 提取元数据（YAML front matter）
        const metadata = {};
        const frontMatterMatch = text.match(/^---\n([\s\S]*?)\n---/);
        if (frontMatterMatch) {
            const lines = frontMatterMatch[1].split('\n');
            for (const line of lines) {
                const [key, ...valueParts] = line.split(':');
                if (key && valueParts.length > 0) {
                    metadata[key.trim()] = valueParts.join(':').trim();
                }
            }
        }
        // 去掉 YAML front matter，只保留正文
        const content = frontMatterMatch
            ? text.replace(/^---\n[\s\S]*?\n---\n?/, '')
            : text;
        return {
            success: true,
            text: content,
            format: 'markdown',
            metadata,
            wordCount: this.countWords(content),
        };
    }
    /** HTML 解析：去除标签，提取文本 */
    parseHtml(file) {
        const text = this.decodeBuffer(file.data, file.encoding);
        // 去除 script 和 style
        let cleaned = text.replace(/<script[\s\S]*?<\/script>/gi, '');
        cleaned = cleaned.replace(/<style[\s\S]*?<\/style>/gi, '');
        // 提取 meta 信息
        const metadata = {};
        const metaMatches = cleaned.matchAll(/<meta\s+([^>]+)>/gi);
        for (const match of metaMatches) {
            const nameMatch = match[1].match(/name\s*=\s*["']([^"']+)["']/i);
            const contentMatch = match[1].match(/content\s*=\s*["']([^"']+)["']/i);
            if (nameMatch && contentMatch) {
                metadata[nameMatch[1]] = contentMatch[1];
            }
        }
        // 提取 title
        const titleMatch = cleaned.match(/<title[^>]*>(.*?)<\/title>/is);
        if (titleMatch) {
            metadata['title'] = titleMatch[1].trim();
        }
        // 去除所有 HTML 标签
        cleaned = cleaned.replace(/<[^>]+>/g, ' ');
        // 解码 HTML 实体
        cleaned = cleaned
            .replace(/&nbsp;/g, ' ')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&amp;/g, '&')
            .replace(/&quot;/g, '"')
            .replace(/&#39;/g, "'")
            .replace(/&#x([0-9a-fA-F]+);/g, (_, hex) => String.fromCharCode(parseInt(hex, 16)))
            .replace(/&#(\d+);/g, (_, num) => String.fromCharCode(parseInt(num, 10)));
        // 压缩空白
        cleaned = cleaned.replace(/\s+/g, ' ').trim();
        return {
            success: true,
            text: cleaned,
            format: 'html',
            metadata,
            wordCount: this.countWords(cleaned),
        };
    }
    /** JSON 解析：格式化为可读文本 */
    parseJson(file) {
        const text = this.decodeBuffer(file.data, file.encoding);
        const metadata = {};
        try {
            const parsed = JSON.parse(text);
            // 提取顶层 key 作为元数据
            if (typeof parsed === 'object' && parsed !== null) {
                for (const key of Object.keys(parsed)) {
                    if (typeof parsed[key] === 'string') {
                        metadata[key] = parsed[key];
                    }
                }
            }
            // 格式化为可读文本
            const formatted = typeof parsed === 'object'
                ? JSON.stringify(parsed, null, 2)
                : String(parsed);
            return {
                success: true,
                text: formatted,
                format: 'json',
                metadata,
                wordCount: this.countWords(formatted),
            };
        }
        catch {
            // JSON 格式不正确，作为纯文本处理
            return {
                success: true,
                text: text,
                format: 'json',
                metadata: {},
                wordCount: this.countWords(text),
            };
        }
    }
    /** XML 解析：去除标签，提取文本 */
    parseXml(file) {
        const text = this.decodeBuffer(file.data, file.encoding);
        let cleaned = text.replace(/<\?.*?\?>/g, ''); // 去除 XML 声明
        cleaned = cleaned.replace(/<!--[\s\S]*?-->/g, ''); // 去除注释
        cleaned = cleaned.replace(/<[^>]+>/g, ' '); // 去除标签
        cleaned = cleaned.replace(/\s+/g, ' ').trim();
        // 解码 XML 实体
        cleaned = cleaned
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&amp;/g, '&')
            .replace(/&quot;/g, '"')
            .replace(/&apos;/g, "'");
        return {
            success: true,
            text: cleaned,
            format: 'xml',
            metadata: {},
            wordCount: this.countWords(cleaned),
        };
    }
    /** CSV 解析：表格格式化 */
    parseCsv(file) {
        const text = this.decodeBuffer(file.data, file.encoding);
        const lines = text.split(/\r?\n/).filter(l => l.trim());
        // 提取元数据
        const metadata = {};
        metadata['columns'] = String(lines[0]?.split(',').length || 0);
        metadata['rows'] = String(lines.length);
        // 保持原始格式（CSV 天然可读）
        return {
            success: true,
            text: lines.join('\n'),
            format: 'csv',
            metadata,
            wordCount: this.countWords(text),
        };
    }
    /** 配置文件解析：保持原始格式 */
    parseConfig(file) {
        const text = this.decodeBuffer(file.data, file.encoding);
        return {
            success: true,
            text: text,
            format: 'config',
            metadata: {},
            wordCount: this.countWords(text),
        };
    }
    /** 纯文本解析 */
    parseText(file) {
        const text = this.decodeBuffer(file.data, file.encoding);
        return {
            success: true,
            text: text,
            format: 'text',
            metadata: {},
            wordCount: this.countWords(text),
        };
    }
    /** 代码文件解析：保留原始代码 */
    parseCode(file) {
        const text = this.decodeBuffer(file.data, file.encoding);
        const metadata = {};
        metadata['language'] = file.extension.replace('.', '');
        return {
            success: true,
            text: text,
            format: 'code',
            metadata,
            wordCount: this.countWords(text),
        };
    }
    /** 二进制文档处理（PDF/Word/Excel/PPT/RTF）
     *  注意：在纯 Node.js 环境中，完整解析二进制文档需要额外依赖
     *  这里提供基本处理：记录文件信息，提取可能的文本片段
     */
    parseBinaryDocument(file) {
        const metadata = {};
        metadata['fileType'] = file.extension;
        metadata['fileSize'] = String(file.size);
        metadata['encoding'] = file.encoding;
        // 尝试从文件中提取可读文本片段
        const sample = this.extractTextSnippets(file.data);
        if (sample) {
            return {
                success: true,
                text: sample,
                format: file.extension.replace('.', ''),
                metadata,
                wordCount: this.countWords(sample),
            };
        }
        // 无法提取文本，返回文件信息
        return {
            success: true,
            text: `[二进制文档 ${file.fileName}] 文件大小: ${file.size} 字节。此格式需要在 Coze 云端环境通过专用解析器处理。`,
            format: file.extension.replace('.', ''),
            metadata,
            wordCount: this.countWords(`[二进制文档 ${file.fileName}]`),
        };
    }
    /** 从二进制数据中提取可读文本片段 */
    extractTextSnippets(data) {
        // 尝试 UTF-8 解码
        try {
            const text = data.toString('utf-8');
            // 过滤掉大部分控制字符，只保留可读文本
            const readable = text.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '');
            if (readable.trim().length > 20) {
                return readable.trim();
            }
        }
        catch {
            // 忽略
        }
        return '';
    }
    /** 解码 Buffer 为字符串，支持多种编码 */
    decodeBuffer(buffer, encoding) {
        if (buffer.length === 0)
            return '';
        try {
            switch (encoding) {
                case 'utf-8-bom':
                    return buffer.toString('utf-8', 3); // 跳过 BOM
                case 'utf-8':
                    return buffer.toString('utf-8');
                case 'utf-16le':
                    // Node.js 支持 UTF-16 LE
                    if (buffer.length >= 2) {
                        return buffer.subarray(2).swap16().toString('utf-16le');
                    }
                    return '';
                case 'utf-16be':
                    if (buffer.length >= 2) {
                        return buffer.subarray(2).toString('utf16be');
                    }
                    return '';
                case 'gbk':
                default:
                    // 先尝试 UTF-8，再尝试 Latin1（GBK 近似）
                    try {
                        return buffer.toString('utf-8');
                    }
                    catch {
                        return buffer.toString('latin1');
                    }
            }
        }
        catch {
            // 最后兜底
            return buffer.toString('binary');
        }
    }
    /** 字数统计（支持中英文混合） */
    countWords(text) {
        if (!text || text.trim().length === 0)
            return 0;
        // 中文按字计数，英文按词计数
        const chinese = (text.match(/[\u4e00-\u9fff]/g) || []).length;
        const english = (text.match(/[a-zA-Z]+/g) || []).length;
        return chinese + english;
    }
}
exports.FileParser = FileParser;
//# sourceMappingURL=parser.js.map

// Auto-generated exports
module.exports = {
  FileParser,
  chinese,
  english,
};
