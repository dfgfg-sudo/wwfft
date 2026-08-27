"use strict";
/**
 * 类型定义文件
 * 定义插件中所有核心数据结构
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.DEFAULT_OPTIONS = void 0;
/** 默认配置常量 */
exports.DEFAULT_OPTIONS = {
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
    maxFileSize: 20 * 1024 * 1024, // 20MB
    maxZipSize: 500 * 1024 * 1024, // 500MB
    pathPrefix: '',
    overwriteOnConflict: false,
    skipHiddenFiles: true,
    skipEmptyFiles: true,
    concurrency: 5,
};
//# sourceMappingURL=types.js.map