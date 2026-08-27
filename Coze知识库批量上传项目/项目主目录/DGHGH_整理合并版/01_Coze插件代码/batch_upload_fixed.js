'use strict';

const AdmZip = require('adm-zip');
const path = require('path');

/**
 * Coze批量知识库上传插件 (batch_upload)
 * 功能：接收ZIP的Base64编码，自动解压提取文件内容，保留完整目录结构，生成知识库文档列表
 *
 * 输入参数:
 *   - zip_base64         {string}  ZIP文件的Base64编码字符串
 *   - path_prefix        {string}  [可选] 文档路径前缀，用于在知识库中组织目录结构
 *   - allowed_extensions {string[]} [可选] 允许处理的文件扩展名列表，如 ['.txt','.md','.pdf']，不传则不过滤
 *   - max_file_size_mb   {number}  [可选] 单个文件最大大小(MB)，超过则跳过，默认10MB
 *   - skip_hidden        {boolean} [可选] 是否跳过隐藏文件(以.开头的文件/目录)，默认true
 *
 * 返回:
 *   { success, total_count, success_count, fail_count, skipped_count, processing_time_ms, directory_tree, documents, summary, logs }
 */

async function handler({ input, logger }) {
    const startTime = Date.now();
    const logs = [];
    const documents = [];
    const errors = [];
    const skipped = [];

    function addLog(level, message) {
        const entry = {
            timestamp: new Date().toISOString(),
            level: level,
            message: message
        };
        logs.push(entry);
        if (logger) {
            const logMethod = level === 'error' ? logger.error :
                              level === 'warn' ? logger.warn :
                              logger.info;
            if (logMethod) {
                logMethod(message);
            }
        }
    }

    try {
        // ========== 参数校验与默认值 ==========
        const zipBase64 = input.zip_base64;
        if (!zipBase64 || typeof zipBase64 !== 'string' || zipBase64.trim() === '') {
            throw new Error('缺少必需参数: zip_base64');
        }

        const pathPrefix = input.path_prefix || '';
        const allowedExtensions = input.allowed_extensions || [];
        const maxFileSizeMB = input.max_file_size_mb || 10;
        const maxFileSizeBytes = maxFileSizeMB * 1024 * 1024;
        const skipHidden = input.skip_hidden !== undefined ? input.skip_hidden : true;

        addLog('info', '开始处理ZIP文件上传');
        addLog('info', '参数: path_prefix=' + (pathPrefix || '(无)') + ', max_file_size=' + maxFileSizeMB + 'MB, skip_hidden=' + skipHidden);

        // ========== 解码Base64并加载ZIP ==========
        addLog('info', '正在解码Base64数据...');
        let zipBuffer;
        try {
            zipBuffer = Buffer.from(zipBase64, 'base64');
            addLog('info', 'Base64解码成功，数据大小: ' + (zipBuffer.length / 1024).toFixed(2) + ' KB');
        } catch (e) {
            throw new Error('Base64解码失败: ' + e.message);
        }

        addLog('info', '正在解析ZIP文件...');
        let zip;
        try {
            zip = new AdmZip(zipBuffer);
        } catch (e) {
            throw new Error('ZIP文件解析失败: ' + e.message);
        }

        const entries = zip.getEntries();
        addLog('info', 'ZIP文件解析成功，共发现 ' + entries.length + ' 个条目');

        // ========== 构建目录树 ==========
        const directoryTree = { name: pathPrefix || 'root', type: 'directory', children: [] };
        const dirMap = new Map();
        dirMap.set(pathPrefix || '', directoryTree);

        function ensureDir(dirPath) {
            const normalizedPath = dirPath.replace(/\\/g, '/').replace(/\/+$/, '');
            if (dirMap.has(normalizedPath)) {
                return dirMap.get(normalizedPath);
            }

            const parts = normalizedPath.split('/').filter(Boolean);
            let currentPath = '';
            let currentNode = directoryTree;

            for (let i = 0; i < parts.length; i++) {
                const prevPath = currentPath;
                currentPath = currentPath ? currentPath + '/' + parts[i] : parts[i];

                if (dirMap.has(currentPath)) {
                    currentNode = dirMap.get(currentPath);
                } else {
                    const newNode = { name: parts[i], type: 'directory', children: [] };
                    currentNode.children.push(newNode);
                    currentNode = newNode;
                    dirMap.set(currentPath, newNode);
                }
            }

            return currentNode;
        }

        function addFileToTree(dirPath, fileName) {
            const parentNode = ensureDir(dirPath);
            const fileNode = { name: fileName, type: 'file' };
            parentNode.children.push(fileNode);
            return fileNode;
        }

        // ========== 遍历处理每个条目 ==========
        let totalCount = 0;
        let successCount = 0;
        let failCount = 0;
        let skippedCount = 0;

        for (let i = 0; i < entries.length; i++) {
            const entry = entries[i];
            totalCount++;

            try {
                const entryName = entry.entryName;

                // 跳过目录条目
                if (entry.isDirectory) {
                    addLog('info', '[' + (i + 1) + '/' + entries.length + '] 跳过目录: ' + entryName);
                    skippedCount++;
                    skipped.push({ path: entryName, reason: '目录条目' });
                    continue;
                }

                // 跳过隐藏文件
                const fileName = path.basename(entryName);
                const dirName = path.dirname(entryName);
                if (skipHidden && (fileName.startsWith('.') || entryName.split('/').some(part => part.startsWith('.')))) {
                    addLog('info', '[' + (i + 1) + '/' + entries.length + '] 跳过隐藏文件: ' + entryName);
                    skippedCount++;
                    skipped.push({ path: entryName, reason: '隐藏文件' });
                    continue;
                }

                // 检查文件扩展名
                const ext = path.extname(fileName).toLowerCase();
                if (allowedExtensions.length > 0 && !allowedExtensions.includes(ext)) {
                    addLog('info', '[' + (i + 1) + '/' + entries.length + '] 跳过不支持的扩展名(' + ext + '): ' + entryName);
                    skippedCount++;
                    skipped.push({ path: entryName, reason: '不支持的扩展名: ' + ext });
                    continue;
                }

                // 检查文件大小
                const fileSize = entry.header.size;
                if (fileSize > maxFileSizeBytes) {
                    addLog('warn', '[' + (i + 1) + '/' + entries.length + '] 文件超过大小限制(' + (fileSize / 1024 / 1024).toFixed(2) + 'MB > ' + maxFileSizeMB + 'MB): ' + entryName);
                    skippedCount++;
                    skipped.push({ path: entryName, reason: '文件超过大小限制: ' + (fileSize / 1024 / 1024).toFixed(2) + 'MB' });
                    continue;
                }

                // 提取文件内容
                const fileContent = entry.getData();
                let contentText;
                try {
                    contentText = fileContent.toString('utf-8');
                } catch (textErr) {
                    // 如果不是UTF-8文本，尝试以base64存储
                    contentText = fileContent.toString('base64');
                    addLog('warn', '文件非UTF-8文本，已转为base64存储: ' + entryName);
                }

                const docPath = pathPrefix ? pathPrefix + '/' + entryName : entryName;

                const doc = {
                    path: docPath.replace(/\\/g, '/'),
                    filename: fileName,
                    extension: ext,
                    size_bytes: fileSize,
                    size_display: formatFileSize(fileSize),
                    content: contentText,
                    encoding: contentText === fileContent.toString('base64') ? 'base64' : 'utf-8'
                };

                documents.push(doc);
                addFileToTree(dirName, fileName);
                successCount++;

                addLog('info', '[' + (i + 1) + '/' + entries.length + '] 成功处理: ' + entryName + ' (' + formatFileSize(fileSize) + ')');

            } catch (entryErr) {
                addLog('error', '[' + (i + 1) + '/' + entries.length + '] 处理失败: ' + entry.entryName + ' - ' + entryErr.message);
                failCount++;
                errors.push({ path: entry.entryName, error: entryErr.message });
            }
        }

        // ========== 构建摘要 ==========
        const processingTimeMs = Date.now() - startTime;

        const summary = {
            total_entries: entries.length,
            total_count: totalCount,
            success_count: successCount,
            fail_count: failCount,
            skipped_count: skippedCount,
            processing_time_ms: processingTimeMs,
            max_file_size_mb: maxFileSizeMB,
            allowed_extensions: allowedExtensions,
            skip_hidden: skipHidden,
            errors: errors,
            skipped: skipped
        };

        addLog('info', '处理完成。总计: ' + totalCount + ', 成功: ' + successCount + ', 失败: ' + failCount + ', 跳过: ' + skippedCount + ', 耗时: ' + processingTimeMs + 'ms');

        return {
            success: failCount === 0,
            total_count: totalCount,
            success_count: successCount,
            fail_count: failCount,
            skipped_count: skippedCount,
            processing_time_ms: processingTimeMs,
            directory_tree: directoryTree,
            documents: documents,
            summary: summary,
            logs: logs
        };

    } catch (err) {
        const processingTimeMs = Date.now() - startTime;
        addLog('error', '插件执行失败: ' + err.message);

        return {
            success: false,
            total_count: 0,
            success_count: 0,
            fail_count: 1,
            skipped_count: 0,
            processing_time_ms: processingTimeMs,
            directory_tree: null,
            documents: [],
            summary: {
                error: err.message,
                errors: [{ error: err.message }],
                processing_time_ms: processingTimeMs
            },
            logs: logs
        };
    }
}

/**
 * 格式化文件大小为可读字符串
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
}

/**
 * 辅助函数：从目录树中提取扁平化的文件路径列表
 */
function flattenTree(node, basePath) {
    const results = [];
    const currentPath = basePath ? basePath + '/' + node.name : node.name;

    if (node.type === 'file') {
        results.push(currentPath);
    } else if (node.type === 'directory' && node.children) {
        for (let i = 0; i < node.children.length; i++) {
            results.push.apply(results, flattenTree(node.children[i], currentPath));
        }
    }

    return results;
}

module.exports = {
    handler: handler,
    formatFileSize: formatFileSize,
    flattenTree: flattenTree
};