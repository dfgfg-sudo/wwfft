/**
 * 全功能测试 - 验证所有7种模式
 */
const AdmZip = require('adm-zip');
const fs = require('fs');
const path = require('path');

async function createTestZip() {
  const zip = new AdmZip();
  zip.addFile('projectA/docs/README.md', Buffer.from('# 项目A\n\n这是测试文档。\n\n## 功能\n- 批量上传\n- 检索\n- 删除\n', 'utf-8'));
  zip.addFile('projectA/docs/guide.txt', Buffer.from('使用指南\n\n第一步：准备ZIP\n第二步：上传\n', 'utf-8'));
  zip.addFile('projectA/config/settings.json', Buffer.from(JSON.stringify({name: '测试', version: '1.0'}, null, 2), 'utf-8'));
  zip.addFile('projectA/src/index.js', Buffer.from('const app = require("express");\napp.listen(3000);\n', 'utf-8'));
  zip.addFile('projectA/src/utils.py', Buffer.from('# utils\ndef load_config(path):\n    pass\n', 'utf-8'));
  zip.addFile('projectB/data.csv', Buffer.from('id,name,status\n1,test,ok\n', 'utf-8'));
  zip.addFile('projectB/report.html', Buffer.from('<html><head><title>报告</title></head><body><h1>测试报告</h1><p>内容</p></body></html>', 'utf-8'));
  zip.addFile('projectA/config/deploy.yaml', Buffer.from('server:\n  port: 8080\n', 'utf-8'));
  zip.addFile('projectA/db/schema.sql', Buffer.from('CREATE TABLE docs (id INT);\n', 'utf-8'));
  zip.addFile('projectA/config/mapping.xml', Buffer.from('<?xml version="1.0"?><config><item key="a">1</item></config>', 'utf-8'));
  zip.addFile('projectA/.hidden', Buffer.from('hidden', 'utf-8'));
  zip.addFile('__MACOSX/._test', Buffer.from('macos', 'utf-8'));
  return zip.toBuffer();
}

// 模拟 Coze 环境运行 handler
async function runTest() {
  console.log('='.repeat(60));
  console.log('Coze 全能知识库插件 - 全功能测试');
  console.log('='.repeat(60));

  const testZip = await createTestZip();
  const zipBase64 = testZip.toString('base64');
  console.log('\n测试 ZIP 大小：' + (testZip.length / 1024).toFixed(2) + ' KB');

  // 编译 TypeScript 并加载
  console.log('\n编译 TypeScript...');
  const { execSync } = require('child_process');
  execSync('npx tsc --target ES2022 --module commonjs --esModuleInterop --skipLibCheck --outDir dist_test COZE_IDE_TYPE_SAFE_FULL.ts', {
    cwd: path.resolve(__dirname),
    stdio: 'inherit',
  });

  const { handler } = require('./dist_test/COZE_IDE_TYPE_SAFE_FULL');
  const mockLogger = {
    info: (msg) => console.log('  [LOG] ' + msg),
    error: (msg) => console.error('  [ERR] ' + msg),
    warn: (msg) => console.warn('  [WARN] ' + msg),
  };

  const tests = [
    {
      name: '模式1: batch_upload（批量上传）',
      mode: 'batch_upload',
      input: { mode: 'batch_upload', zip_base64, path_prefix: '知识库' },
      checks: [
        (r) => r.success === true,
        (r) => r.total_count >= 10,
        (r) => r.success_count >= 9,
        (r) => r.documents.length >= 9,
        (r) => r.documents[0].doc_id,
        (r) => r.documents[0].title,
        (r) => r.documents[0].content.length > 0,
        (r) => r.documents[0].metadata,
        (r) => r.documents[0].status === 'success',
        (r) => r.directory_tree.length > 0,
        (r) => r.skipped_count >= 1,
      ],
    },
    {
      name: '模式6: file_search（文件搜索）',
      mode: 'file_search',
      input: { mode: 'file_search', zip_base64, file_keyword: 'README' },
      checks: [
        (r) => r.success === true,
        (r) => r.total_count === 1,
        (r) => r.documents[0].source_path.includes('README.md'),
      ],
    },
    {
      name: '模式7: content_search（全文搜索）',
      mode: 'content_search',
      input: { mode: 'content_search', zip_base64, query: '批量上传' },
      checks: [
        (r) => r.success === true,
        (r) => r.total_count >= 1,
        (r) => r.documents[0].content.includes('批量上传'),
      ],
    },
    {
      name: '模式4: memory_write（记忆写入）',
      mode: 'memory_write',
      input: { mode: 'memory_write', memory_key: 'test_key', memory_value: '测试记忆值' },
      checks: [
        (r) => r.success === true,
        (r) => r.memory.key === 'test_key',
        (r) => r.memory.value === '测试记忆值',
      ],
    },
    {
      name: '模式5: memory_read（记忆读取）',
      mode: 'memory_read',
      input: { mode: 'memory_read', memory_key: 'test_key' },
      checks: [
        (r) => r.success === true,
        (r) => r.memory.value === '测试记忆值',
      ],
    },
  ];

  let allPassed = true;

  for (const test of tests) {
    console.log('\n' + '-'.repeat(40));
    console.log('测试：' + test.name);
    console.log('-'.repeat(40));

    try {
      const result = await handler({ input: test.input, logger: mockLogger });
      let passed = 0;
      let failed = 0;

      for (const check of test.checks) {
        try {
          if (check(result)) {
            passed++;
          } else {
            failed++;
            console.log('  [FAIL] 检查不通过');
          }
        } catch (e) {
          failed++;
          console.log('  [FAIL] 检查异常：' + String(e));
        }
      }

      const status = failed === 0 ? 'PASS' : 'FAIL';
      if (failed > 0) allPassed = false;
      console.log('  结果：[' + status + '] 通过 ' + passed + '/' + (passed + failed) + ' 项检查');
      console.log('  摘要：' + result.summary);
      console.log('  耗时：' + result.processing_time_ms + 'ms');
    } catch (e) {
      console.log('  [ERROR] ' + String(e));
      allPassed = false;
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log(allPassed ? '所有测试通过！' : '部分测试未通过');
  console.log('='.repeat(60));

  // 清理
  try { fs.rmSync(path.join(__dirname, 'dist_test'), { recursive: true }); } catch {}
}


// Auto-generated exports
module.exports = {
  createTestZip,
  runTest,
};
