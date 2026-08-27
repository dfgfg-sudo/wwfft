// ============================================================
// 知识库文件夹批量上传 - 本地 UI 服务器
// 文件名: kb_ui_server.js
// 端口: 18789 (与 OpenClaw 网关一致)
// 功能:
//   1. 提供 kb_folder_upload_ui.html 静态服务
//   2. 接收 UI 端 POST 请求，调用 knowledge_base_folder_upload.js 的 handler
//   3. 返回 JSON 结果给浏览器
// 启动: node kb_ui_server.js
// 访问: http://127.0.0.1:18789
// ============================================================

'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.env.KB_UI_PORT || 18789;
const HOST = '127.0.0.1';
const ROOT_DIR = __dirname;

const kbUploader = require('./knowledge_base_folder_upload.js');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.png': 'image/png',
  '.ico': 'image/x-icon'
};

function sendJson(res, statusCode, data) {
  const body = JSON.stringify(data, null, 2);
  res.writeHead(statusCode, { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' });
  res.end(body);
}

function sendFile(res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('404 Not Found: ' + path.basename(filePath));
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
    res.end(data);
  });
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let totalSize = 0;
    const MAX_BODY = 50 * 1024 * 1024; // 50MB
    req.on('data', chunk => {
      totalSize += chunk.length;
      if (totalSize > MAX_BODY) {
        reject(new Error('Body too large (max 50MB)'));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    req.on('error', reject);
  });
}

const server = http.createServer(async (req, res) => {
  const parsed = url.parse(req.url, true);
  const pathname = decodeURIComponent(parsed.pathname || '/');

  // CORS 预检
  if (req.method === 'OPTIONS') {
    res.writeHead(200, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    });
    res.end();
    return;
  }

  // 路由: 健康检查
  if (pathname === '/health' || pathname === '/') {
    sendJson(res, 200, {
      status: 'ok',
      service: 'Coze 知识库文件夹批量上传 - UI 服务器',
      version: '1.0.0',
      endpoints: {
        'GET /': '本信息',
        'GET /ui': '打开 UI 页面',
        'GET /api/manifest': '获取插件清单',
        'POST /api/upload': '触发上传（参数同 handler）',
        'GET /api/scan?folder_path=...': '预扫描文件夹（不实际上传）'
      }
    });
    return;
  }

  // 路由: UI 页面
  if (pathname === '/ui' || pathname === '/index.html') {
    sendFile(res, path.join(ROOT_DIR, 'kb_folder_upload_ui.html'));
    return;
  }

  // 路由: 插件清单
  if (pathname === '/api/manifest' && req.method === 'GET') {
    sendFile(res, path.join(ROOT_DIR, 'manifest.json'));
    return;
  }

  // 路由: 预扫描（只扫描不上传）
  if (pathname === '/api/scan' && req.method === 'GET') {
    const folderPath = parsed.query.folder_path;
    if (!folderPath) {
      sendJson(res, 400, { success: false, error: 'folder_path 参数缺失' });
      return;
    }
    try {
      const params = { ...kbUploader.DEFAULT_PARAMS, folder_path: folderPath };
      const { allFiles, scanReports } = kbUploader.utils.collectFiles(params);
      sendJson(res, 200, {
        success: true,
        total_files: allFiles.length,
        scan_reports: scanReports,
        files: allFiles.slice(0, 100).map(f => ({
          relative_path: f.relative_path,
          size: f.size,
          extension: f.extension
        })),
        truncated: allFiles.length > 100
      });
    } catch (err) {
      sendJson(res, 500, { success: false, error: err.message });
    }
    return;
  }

  // 路由: 触发上传
  if (pathname === '/api/upload' && req.method === 'POST') {
    try {
      const body = await readBody(req);
      let input;
      try {
        input = JSON.parse(body);
      } catch (e) {
        sendJson(res, 400, { success: false, error: '请求体不是合法 JSON: ' + e.message });
        return;
      }
      // 调用 handler
      const result = await kbUploader.handler(input);
      const statusCode = result.success ? 200 : (result.status === 'validation_failed' ? 400 : 500);
      sendJson(res, statusCode, result);
    } catch (err) {
      sendJson(res, 500, { success: false, error: err.message });
    }
    return;
  }

  // 路由: 静态文件
  const safePath = path.normalize(pathname).replace(/^(\.\.[/\\])+/, '');
  const filePath = path.join(ROOT_DIR, safePath);
  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    sendFile(res, filePath);
    return;
  }

  // 404
  sendJson(res, 404, { success: false, error: '路径不存在: ' + pathname });
});

server.listen(PORT, HOST, () => {
  console.log('============================================================');
  console.log(' Coze 知识库文件夹批量上传 - UI 服务器');
  console.log('============================================================');
  console.log(` 服务地址:  http://${HOST}:${PORT}`);
  console.log(` UI 页面:   http://${HOST}:${PORT}/ui`);
  console.log(` 健康检查:  http://${HOST}:${PORT}/health`);
  console.log(` 上传接口:  POST http://${HOST}:${PORT}/api/upload`);
  console.log(` 预扫描:    GET  http://${HOST}:${PORT}/api/scan?folder_path=...`);
  console.log('------------------------------------------------------------');
  console.log(' 按 Ctrl+C 退出');
  console.log('============================================================');
});

process.on('SIGINT', () => {
  console.log('\n正在关闭服务器...');
  server.close(() => process.exit(0));
});

process.on('uncaughtException', (err) => {
  console.error('未捕获异常:', err.message);
});

process.on('unhandledRejection', (reason) => {
  console.error('未处理的 Promise 拒绝:', reason);
});
