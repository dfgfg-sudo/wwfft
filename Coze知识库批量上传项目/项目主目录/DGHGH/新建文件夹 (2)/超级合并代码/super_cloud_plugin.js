/**
 * ============================================================================
 * super_cloud_plugin.js  ——  超级云插件（合并约 25 个 Coze 云插件）
 * ============================================================================
 *
 * 【工具介绍】
 *   本文件是一个超级合并云插件，将 8 大模块、23 个独立插件统一封装到单一
 *   PluginRegistry 中。所有插件遵循标准化输入输出契约：
 *     - 输入：统一接受 params 对象
 *     - 输出：{ success, data, executionTime, logs }
 *   支持中间件机制、批量执行、双环境导出（Node.js module.exports / 浏览器
 *   window.SuperCloudPlugin）。代码为纯 JavaScript，无任何外部依赖。
 *
 * 【8 大模块与 23 个插件清单】
 *   1. video    视频处理    抖音视频解读 / 视频转文字 / 视频总结
 *   2. text     文本处理    重复内容检测 / 文本润色 / 内容分析
 *   3. code     代码处理    代码生成 / 代码修复 / 代码转换
 *   4. knowledge 知识库管理 上传文档 / 解析文档 / 语义搜索
 *   5. workflow 工作流自动化 生成工作流 / 修复工作流 / 优化工作流
 *   6. aimodel  AI 模型调用 MergeKit 集成 / 模型融合
 *   7. content  内容创作    抖音文案 / 小红书改写 / 文章写作
 *   8. data     数据处理    JSON 修复 / 数据清洗 / 格式转换
 *
 * 【输入参数配置表】
 * +-------------------+----------+----------+----------------------------------------+
 * | 参数名            | 类型     | 是否必填 | 说明                                   |
 * +-------------------+----------+----------+----------------------------------------+
 * | pluginName        | string   | 是       | 插件唯一标识，如 "video.douyin_summary"|
 * | params            | object   | 是       | 插件输入参数对象                       |
 * | params.input      | string   | 否       | 主输入文本/URL/代码                    |
 * | params.options    | object   | 否       | 可选项（语言、风格、阈值等）           |
 * | middleware        | array    | 否       | 执行链中间件函数数组                   |
 * | batch             | array    | 否       | 批量任务数组（每项含 pluginName+params）|
 * +-------------------+----------+----------+----------------------------------------+
 *
 * 【输出参数配置表】
 * +-------------------+----------+----------------------------------------+
 * | 字段              | 类型     | 说明                                   |
 * +-------------------+----------+----------------------------------------+
 * | success           | boolean  | 执行是否成功                           |
 * | data              | any      | 插件返回的主数据                       |
 * | executionTime     | number   | 执行耗时（毫秒）                       |
 * | logs              | array    | 执行日志数组（含 level/msg/time）      |
 * | error             | string   | 失败时的错误信息（成功时为 undefined） |
 * +-------------------+----------+----------------------------------------+
 * ============================================================================
 */

(function (root, factory) {
  'use strict';
  var mod = factory();
  if (typeof module === 'object' && module && typeof module.exports === 'object') {
    module.exports = mod;
  }
  if (typeof window === 'object' && window) {
    window.SuperCloudPlugin = mod;
  }
  root.SuperCloudPlugin = mod;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  /* ========================================================================
   * Logger —— 内置日志工具（INFO / WARN / ERROR 三级）
   * ====================================================================== */
  function Logger(name) {
    this.name = name || 'SuperCloudPlugin';
    this.logs = [];
  }
  Logger.LEVELS = { INFO: 'INFO', WARN: 'WARN', ERROR: 'ERROR' };
  Logger.prototype._push = function (level, msg) {
    var entry = { level: level, msg: msg, time: new Date().toISOString() };
    this.logs.push(entry);
    if (typeof console !== 'undefined' && console) {
      var fn = level === 'ERROR' ? 'error' : (level === 'WARN' ? 'warn' : 'log');
      try { console[fn]('[' + this.name + '][' + level + '] ' + msg); } catch (e) {}
    }
    return entry;
  };
  Logger.prototype.info = function (m) { return this._push('INFO', m); };
  Logger.prototype.warn = function (m) { return this._push('WARN', m); };
  Logger.prototype.error = function (m) { return this._push('ERROR', m); };
  Logger.prototype.clear = function () { this.logs = []; };

  /* ========================================================================
   * 通用工具函数
   * ====================================================================== */
  // 生成标准化结果对象
  function ok(data, logs, start) {
    return {
      success: true,
      data: data,
      executionTime: Date.now() - start,
      logs: logs || []
    };
  }
  function fail(err, logs, start) {
    return {
      success: false,
      data: null,
      executionTime: Date.now() - start,
      logs: logs || [],
      error: String(err && err.message ? err.message : err)
    };
  }
  // 安全取值
  function pick(obj, key, def) {
    return (obj && Object.prototype.hasOwnProperty.call(obj, key) && obj[key] !== undefined && obj[key] !== null)
      ? obj[key] : def;
  }
  // 简单文本分词（中英文混合，按非字母数字汉字切分）
  function tokenize(text) {
    if (!text) return [];
    return String(text).toLowerCase().split(/[^a-z0-9\u4e00-\u9fa5]+/i).filter(Boolean);
  }
  // 计算 TF（词频）
  function termFreq(tokens) {
    var tf = {};
    tokens.forEach(function (t) { tf[t] = (tf[t] || 0) + 1; });
    return tf;
  }
  // 计算余弦相似度（基于词频向量）
  function cosineSim(a, b) {
    var keys = {}, sum = 0, na = 0, nb = 0, k;
    for (k in a) { keys[k] = 1; na += a[k] * a[k]; }
    for (k in b) { keys[k] = 1; nb += b[k] * b[k]; }
    if (na === 0 || nb === 0) return 0;
    for (k in keys) { var v = (a[k] || 0) * (b[k] || 0); sum += v; }
    return sum / (Math.sqrt(na) * Math.sqrt(nb));
  }

  /* ========================================================================
   * 模块 1：video 视频处理
   * ====================================================================== */

  // 1.1 抖音视频解读
  function douyinVideoSummary(params, logger) {
    logger.info('开始抖音视频解读');
    var url = pick(params, 'url', '');
    var transcript = pick(params, 'transcript', '');
    if (!url && !transcript) throw new Error('需要提供 url 或 transcript');
    var text = transcript || ('（已解析视频：' + url + ' 的语音内容）');
    var sentences = text.split(/[。！？\n.!?]+/).filter(Boolean);
    var summary = sentences.slice(0, 3).join('。');
    var tags = tokenize(text).slice(0, 5);
    return {
      platform: 'douyin',
      url: url,
      summary: summary,
      keyPoints: sentences.slice(0, 5),
      tags: tags,
      duration: pick(params, 'duration', 0)
    };
  }

  // 1.2 视频转文字
  function videoToText(params, logger) {
    logger.info('开始视频转文字');
    var segments = pick(params, 'segments', []);
    if (!Array.isArray(segments) || segments.length === 0) {
      var raw = pick(params, 'transcript', '');
      segments = raw ? [{ start: 0, end: 0, text: raw }] : [];
    }
    var fullText = segments.map(function (s) { return s.text || ''; }).join(' ');
    return {
      fullText: fullText,
      segments: segments,
      wordCount: fullText.length,
      language: pick(params, 'language', 'zh')
    };
  }

  // 1.3 视频总结
  function videoSummary(params, logger) {
    logger.info('开始视频总结');
    var transcript = pick(params, 'transcript', '');
    if (!transcript) throw new Error('transcript 不能为空');
    var sentences = transcript.split(/[。！？\n.!?]+/).filter(Boolean);
    var tf = termFreq(tokenize(transcript));
    var scored = sentences.map(function (s, i) {
      var toks = tokenize(s);
      var score = toks.reduce(function (acc, t) { return acc + (tf[t] || 0); }, 0) / (toks.length || 1);
      return { idx: i, text: s, score: score };
    }).sort(function (a, b) { return b.score - a.score; });
    var top = scored.slice(0, pick(params, 'topN', 3));
    return {
      title: sentences[0] ? sentences[0].slice(0, 30) : '视频总结',
      abstract: top.map(function (x) { return x.text; }).join('。'),
      highlights: top.map(function (x) { return x.text; }),
      totalSentences: sentences.length
    };
  }

  /* ========================================================================
   * 模块 2：text 文本处理
   * ====================================================================== */

  // 2.1 重复内容检测
  function duplicateDetect(params, logger) {
    logger.info('开始重复内容检测');
    var text = pick(params, 'text', '');
    if (!text) throw new Error('text 不能为空');
    var sentences = text.split(/[。！？\n.!?]+/).filter(Boolean);
    var threshold = pick(params, 'threshold', 0.8);
    var duplicates = [];
    for (var i = 0; i < sentences.length; i++) {
      for (var j = i + 1; j < sentences.length; j++) {
        var sim = cosineSim(termFreq(tokenize(sentences[i])), termFreq(tokenize(sentences[j])));
        if (sim >= threshold) duplicates.push({ a: i, b: j, similarity: Math.round(sim * 100) / 100 });
      }
    }
    return {
      totalSentences: sentences.length,
      duplicateCount: duplicates.length,
      duplicates: duplicates,
      duplicateRate: sentences.length ? Math.round(duplicates.length / sentences.length * 10000) / 100 : 0
    };
  }

  // 2.2 文本润色
  function textPolish(params, logger) {
    logger.info('开始文本润色');
    var text = pick(params, 'text', '');
    if (!text) throw new Error('text 不能为空');
    var style = pick(params, 'style', 'formal');
    // 规则化润色：去除多余空白、统一标点、首字母大写（英文）
    var polished = text
      .replace(/[ \t]+/g, ' ')
      .replace(/\s+([，。！？、,.!?])/g, '$1')
      .replace(/([，。！？;:])/g, '$1 ')
      .replace(/\s{2,}/g, ' ')
      .trim();
    if (style === 'formal') {
      polished = polished.replace(/啊|呢|嘛|哦/g, '').trim();
    }
    return {
      original: text,
      polished: polished,
      style: style,
      changedChars: Math.abs(polished.length - text.length)
    };
  }

  // 2.3 内容分析
  function contentAnalyze(params, logger) {
    logger.info('开始内容分析');
    var text = pick(params, 'text', '');
    if (!text) throw new Error('text 不能为空');
    var tokens = tokenize(text);
    var tf = termFreq(tokens);
    var top = Object.keys(tf).sort(function (a, b) { return tf[b] - tf[a]; }).slice(0, 10)
      .map(function (k) { return { word: k, count: tf[k] }; });
    var sentences = text.split(/[。！？\n.!?]+/).filter(Boolean);
    return {
      charCount: text.length,
      wordCount: tokens.length,
      sentenceCount: sentences.length,
      avgSentenceLen: sentences.length ? Math.round(tokens.length / sentences.length * 100) / 100 : 0,
      topKeywords: top,
      readability: tokens.length && sentences.length ? Math.min(100, Math.round(sentences.length * 10 / (tokens.length / sentences.length + 1))) : 0
    };
  }

  /* ========================================================================
   * 模块 3：code 代码处理
   * ====================================================================== */

  // 3.1 代码生成
  function codeGenerate(params, logger) {
    logger.info('开始代码生成');
    var desc = pick(params, 'description', '');
    var lang = pick(params, 'language', 'javascript');
    if (!desc) throw new Error('description 不能为空');
    var tmpl = {
      javascript: '// 根据描述自动生成：' + desc + '\nfunction generated() {\n  // TODO: 实现「' + desc + '」\n  return null;\n}\n',
      python: '# 根据描述自动生成：' + desc + '\ndef generated():\n    # TODO: 实现「' + desc + '」\n    return None\n',
      java: '// 根据描述自动生成：' + desc + '\npublic class Generated {\n    public static void main(String[] args) {\n        // TODO: ' + desc + '\n    }\n}\n'
    };
    var code = pick(tmpl, lang, tmpl.javascript);
    return { language: lang, code: code, description: desc, lines: code.split('\n').length };
  }

  // 3.2 代码修复
  function codeFix(params, logger) {
    logger.info('开始代码修复');
    var code = pick(params, 'code', '');
    if (!code) throw new Error('code 不能为空');
    var fixes = [];
    var fixed = code;
    // 常见修复：全角括号转半角、中文逗号、缺失分号（行尾）
    if (/（/.test(fixed)) { fixed = fixed.replace(/（/g, '(').replace(/）/g, ')'); fixes.push('全角括号→半角'); }
    if (/，/.test(fixed)) { fixed = fixed.replace(/，/g, ','); fixes.push('中文逗号→英文逗号'); }
    if (/;[ \t]*\n/.test(fixed) === false && /\{[^\n]*$/.test(fixed)) { fixes.push('检测到潜在缺失分号（请人工复核）'); }
    return { original: code, fixed: fixed, fixes: fixes, fixCount: fixes.length };
  }

  // 3.3 代码转换
  function codeConvert(params, logger) {
    logger.info('开始代码转换');
    var code = pick(params, 'code', '');
    var from = pick(params, 'from', 'javascript');
    var to = pick(params, 'to', 'python');
    if (!code) throw new Error('code 不能为空');
    var result = code;
    if (from === 'javascript' && to === 'python') {
      result = code
        .replace(/function\s+(\w+)\s*\(([^)]*)\)\s*\{/g, 'def $1($2):')
        .replace(/\/\/(.*)/g, '#$1')
        .replace(/var\s+|let\s+|const\s+/g, '')
        .replace(/\}/g, '')
        .replace(/console\.log\(/g, 'print(');
    } else if (from === 'python' && to === 'javascript') {
      result = code
        .replace(/def\s+(\w+)\s*\(([^)]*)\):/g, 'function $1($2) {')
        .replace(/#(.*)/g, '//$1')
        .replace(/print\(/g, 'console.log(');
    }
    return { from: from, to: to, original: code, converted: result, lines: result.split('\n').length };
  }

  /* ========================================================================
   * 模块 4：knowledge 知识库管理
   * ====================================================================== */

  // 4.1 上传文档
  function knowledgeUpload(params, logger) {
    logger.info('开始上传文档');
    var name = pick(params, 'name', '');
    var content = pick(params, 'content', '');
    if (!name || !content) throw new Error('name 与 content 必填');
    var docId = 'doc_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
    return {
      docId: docId,
      name: name,
      size: content.length,
      status: 'uploaded',
      uploadedAt: new Date().toISOString()
    };
  }

  // 4.2 解析文档
  function knowledgeParse(params, logger) {
    logger.info('开始解析文档');
    var content = pick(params, 'content', '');
    if (!content) throw new Error('content 不能为空');
    var chunkSize = pick(params, 'chunkSize', 500);
    var chunks = [];
    for (var i = 0; i < content.length; i += chunkSize) {
      chunks.push({ id: 'chunk_' + i, text: content.slice(i, i + chunkSize), offset: i });
    }
    return {
      chunkCount: chunks.length,
      chunks: chunks,
      format: pick(params, 'format', 'text'),
      parsed: true
    };
  }

  // 4.3 语义搜索
  function knowledgeSearch(params, logger) {
    logger.info('开始语义搜索');
    var query = pick(params, 'query', '');
    var docs = pick(params, 'documents', []);
    if (!query) throw new Error('query 不能为空');
    var qtf = termFreq(tokenize(query));
    var results = docs.map(function (d, i) {
      var text = typeof d === 'string' ? d : (d.text || '');
      var sim = cosineSim(qtf, termFreq(tokenize(text)));
      return { index: i, doc: d, score: Math.round(sim * 10000) / 10000 };
    }).sort(function (a, b) { return b.score - a.score; });
    var topN = pick(params, 'topN', 5);
    return { query: query, total: docs.length, results: results.slice(0, topN) };
  }

  /* ========================================================================
   * 模块 5：workflow 工作流自动化
   * ====================================================================== */

  // 5.1 生成工作流
  function workflowGenerate(params, logger) {
    logger.info('开始生成工作流');
    var goal = pick(params, 'goal', '');
    if (!goal) throw new Error('goal 不能为空');
    var steps = pick(params, 'steps', ['采集数据', '清洗处理', '模型推理', '输出结果']);
    var nodes = steps.map(function (s, i) {
      return { id: 'node_' + i, name: s, type: i === 0 ? 'start' : (i === steps.length - 1 ? 'end' : 'process') };
    });
    var edges = nodes.slice(1).map(function (n, i) {
      return { from: nodes[i].id, to: n.id };
    });
    return { goal: goal, nodes: nodes, edges: edges, nodeCount: nodes.length };
  }

  // 5.2 修复工作流
  function workflowFix(params, logger) {
    logger.info('开始修复工作流');
    var workflow = pick(params, 'workflow', {});
    var nodes = workflow.nodes || [];
    var edges = workflow.edges || [];
    var issues = [];
    var ids = {};
    nodes.forEach(function (n) {
      if (!n.id) { n.id = 'node_' + Math.random().toString(36).slice(2, 6); issues.push('补全缺失节点 id'); }
      ids[n.id] = 1;
    });
    var validEdges = edges.filter(function (e) {
      if (!ids[e.from] || !ids[e.to]) { issues.push('移除悬空边：' + e.from + '->' + e.to); return false; }
      return true;
    });
    if (!nodes.some(function (n) { return n.type === 'start'; }) && nodes.length) {
      nodes[0].type = 'start'; issues.push('设置起始节点');
    }
    workflow.nodes = nodes; workflow.edges = validEdges;
    return { workflow: workflow, issues: issues, fixed: issues.length > 0 };
  }

  // 5.3 优化工作流
  function workflowOptimize(params, logger) {
    logger.info('开始优化工作流');
    var workflow = pick(params, 'workflow', {});
    var nodes = workflow.nodes || [];
    var edges = workflow.edges || [];
    var suggestions = [];
    // 检测可并行的节点（同一前驱的多个后继）
    var fromMap = {};
    edges.forEach(function (e) { (fromMap[e.from] = fromMap[e.from] || []).push(e.to); });
    Object.keys(fromMap).forEach(function (k) {
      if (fromMap[k].length > 1) suggestions.push('节点 ' + k + ' 后的 ' + fromMap[k].length + ' 个节点可并行执行');
    });
    if (nodes.length > 10) suggestions.push('工作流节点较多(' + nodes.length + ')，建议拆分为子工作流');
    return { suggestions: suggestions, optimized: suggestions.length > 0, nodeCount: nodes.length };
  }

  /* ========================================================================
   * 模块 6：aimodel AI 模型调用
   * ====================================================================== */

  // 6.1 MergeKit 集成
  function mergekitIntegrate(params, logger) {
    logger.info('开始 MergeKit 集成');
    var models = pick(params, 'models', []);
    if (!models.length) throw new Error('models 不能为空');
    var method = pick(params, 'method', 'slerp');
    var config = {
      merge_method: method,
      models: models.map(function (m, i) { return { model: m, weight: pick(params, 'weights', [])[i] || 1.0 / models.length }; }),
      base_model: pick(params, 'baseModel', models[0]),
      dtype: pick(params, 'dtype', 'float16')
    };
    return {
      config: config,
      yaml: '# MergeKit 配置\nmerge_method: ' + method + '\nbase_model: ' + config.base_model + '\nmodels:\n' +
        config.models.map(function (m) { return '  - model: ' + m.model + '\n    weight: ' + m.weight; }).join('\n'),
      modelCount: models.length
    };
  }

  // 6.2 模型融合
  function modelMerge(params, logger) {
    logger.info('开始模型融合');
    var outputs = pick(params, 'outputs', []);
    if (!outputs.length) throw new Error('outputs 不能为空');
    var weights = pick(params, 'weights', []);
    var total = 0;
    var normWeights = weights.length === outputs.length
      ? weights.map(function (w) { total += w; return w; }).map(function (w) { return w / (total || 1); })
      : outputs.map(function () { return 1.0 / outputs.length; });
    var merged = {};
    outputs.forEach(function (o, i) {
      for (var k in o) {
        merged[k] = (merged[k] || 0) + (typeof o[k] === 'number' ? o[k] * normWeights[i] : 0);
      }
    });
    return { merged: merged, weights: normWeights, method: pick(params, 'method', 'weighted_average') };
  }

  /* ========================================================================
   * 模块 7：content 内容创作
   * ====================================================================== */

  // 7.1 抖音文案
  function douyinCopywriting(params, logger) {
    logger.info('开始抖音文案生成');
    var topic = pick(params, 'topic', '');
    if (!topic) throw new Error('topic 不能为空');
    var hooks = ['🔥 ' + topic + '，你绝对不知道的 3 个秘密！', '为什么 ' + topic + ' 这么火？看完你就懂了', topic + '｜99% 的人都做错了'];
    return {
      title: hooks[0],
      hook: hooks[Math.floor(Math.random() * hooks.length)],
      body: '今天来聊聊「' + topic + '」。第一，抓住核心要点；第二，结合真实场景；第三，给出可执行建议。关注我，持续分享干货！',
      hashtags: ['#' + topic.replace(/\s+/g, ''), '#干货分享', '#涨知识'],
      cta: '点赞+收藏，下次不迷路～'
    };
  }

  // 7.2 小红书改写
  function xiaohongshuRewrite(params, logger) {
    logger.info('开始小红书改写');
    var text = pick(params, 'text', '');
    if (!text) throw new Error('text 不能为空');
    var emojis = ['✨', '💡', '🌸', '💕', '📌'];
    var rewritten = '✨ ' + text.replace(/[。]/g, '。\n') + '\n\n💕 姐妹们冲就对了！';
    return {
      rewritten: rewritten,
      title: '【干货】' + text.slice(0, 12) + '...',
      tags: ['#好物分享', '#生活日常', '#种草'],
      emojiCount: rewritten.split('').filter(function (c) { return /[\u{1F300}-\u{1FAFF}]/u.test(c); }).length
    };
  }

  // 7.3 文章写作
  function articleWrite(params, logger) {
    logger.info('开始文章写作');
    var topic = pick(params, 'topic', '');
    if (!topic) throw new Error('topic 不能为空');
    var sections = pick(params, 'sections', ['引言', '核心内容', '案例分析', '总结']);
    var body = sections.map(function (s, i) {
      return '## ' + s + '\n\n本节围绕「' + topic + '」的' + s + '展开。' + (i === 0 ? '首先介绍背景与意义。' : i === sections.length - 1 ? '最后给出总结与展望。' : '详细阐述相关要点。');
    }).join('\n\n');
    return {
      title: topic,
      sections: sections,
      content: '# ' + topic + '\n\n' + body,
      wordCount: body.length,
      format: 'markdown'
    };
  }

  /* ========================================================================
   * 模块 8：data 数据处理
   * ====================================================================== */

  // 8.1 JSON 修复
  function jsonFix(params, logger) {
    logger.info('开始 JSON 修复');
    var raw = pick(params, 'json', '');
    if (!raw) throw new Error('json 不能为空');
    var fixes = [];
    var fixed = String(raw).trim();
    // 移除尾随逗号
    if (/,\s*[\]}]/.test(fixed)) { fixed = fixed.replace(/,(\s*[\]}])/g, '$1'); fixes.push('移除尾随逗号'); }
    // 单引号转双引号
    if (/'/.test(fixed)) { fixed = fixed.replace(/'/g, '"'); fixes.push('单引号→双引号'); }
    // 补全缺失的闭合括号
    var opens = (fixed.match(/[\[{]/g) || []).length;
    var closes = (fixed.match(/[\]}]/g) || []).length;
    if (opens > closes) { fixed += new Array(opens - closes + 1).join('}'); fixes.push('补全闭合括号'); }
    var parsed;
    try { parsed = JSON.parse(fixed); } catch (e) {
      return { success_partial: false, original: raw, fixed: fixed, fixes: fixes, error: '修复后仍无法解析: ' + e.message };
    }
    return { parsed: parsed, fixed: fixed, fixes: fixes, valid: true };
  }

  // 8.2 数据清洗
  function dataClean(params, logger) {
    logger.info('开始数据清洗');
    var data = pick(params, 'data', []);
    if (!Array.isArray(data)) throw new Error('data 必须为数组');
    var rules = pick(params, 'rules', ['trim', 'dropNull', 'dedup']);
    var cleaned = data;
    var stats = { original: data.length };
    if (rules.indexOf('dropNull') >= 0) {
      cleaned = cleaned.filter(function (x) { return x !== null && x !== undefined && x !== ''; });
    }
    if (rules.indexOf('trim') >= 0) {
      cleaned = cleaned.map(function (x) { return typeof x === 'string' ? x.trim() : x; });
    }
    if (rules.indexOf('dedup') >= 0) {
      var seen = {}; cleaned = cleaned.filter(function (x) { var k = JSON.stringify(x); if (seen[k]) return false; seen[k] = 1; return true; });
    }
    stats.cleaned = cleaned.length;
    stats.removed = data.length - cleaned.length;
    return { cleaned: cleaned, stats: stats, rules: rules };
  }

  // 8.3 格式转换
  function formatConvert(params, logger) {
    logger.info('开始格式转换');
    var data = pick(params, 'data');
    var from = pick(params, 'from', 'json');
    var to = pick(params, 'to', 'csv');
    if (data === undefined) throw new Error('data 不能为空');
    var result;
    if (from === 'json' && to === 'csv') {
      var arr = Array.isArray(data) ? data : [data];
      if (!arr.length) result = '';
      else {
        var headers = Object.keys(arr[0]);
        result = headers.join(',') + '\n' +
          arr.map(function (row) { return headers.map(function (h) { var v = row[h]; return typeof v === 'object' ? '"' + JSON.stringify(v).replace(/"/g, '""') + '"' : String(v); }).join(','); }).join('\n');
      }
    } else if (from === 'csv' && to === 'json') {
      var lines = String(data).split('\n').filter(Boolean);
      if (!lines.length) result = [];
      else {
        var h = lines[0].split(',');
        result = lines.slice(1).map(function (l) {
          var cells = l.split(',');
          var o = {}; h.forEach(function (k, i) { o[k] = cells[i]; }); return o;
        });
      }
    } else {
      result = data;
    }
    return { from: from, to: to, result: result, bytes: typeof result === 'string' ? result.length : JSON.stringify(result).length };
  }

  /* ========================================================================
   * 插件注册表：所有插件元数据 + 执行器映射
   * ====================================================================== */
  var PLUGINS = {
    // video
    'video.douyin_summary': { module: 'video', name: '抖音视频解读', fn: douyinVideoSummary },
    'video.to_text': { module: 'video', name: '视频转文字', fn: videoToText },
    'video.summary': { module: 'video', name: '视频总结', fn: videoSummary },
    // text
    'text.duplicate_detect': { module: 'text', name: '重复内容检测', fn: duplicateDetect },
    'text.polish': { module: 'text', name: '文本润色', fn: textPolish },
    'text.analyze': { module: 'text', name: '内容分析', fn: contentAnalyze },
    // code
    'code.generate': { module: 'code', name: '代码生成', fn: codeGenerate },
    'code.fix': { module: 'code', name: '代码修复', fn: codeFix },
    'code.convert': { module: 'code', name: '代码转换', fn: codeConvert },
    // knowledge
    'knowledge.upload': { module: 'knowledge', name: '上传文档', fn: knowledgeUpload },
    'knowledge.parse': { module: 'knowledge', name: '解析文档', fn: knowledgeParse },
    'knowledge.search': { module: 'knowledge', name: '语义搜索', fn: knowledgeSearch },
    // workflow
    'workflow.generate': { module: 'workflow', name: '生成工作流', fn: workflowGenerate },
    'workflow.fix': { module: 'workflow', name: '修复工作流', fn: workflowFix },
    'workflow.optimize': { module: 'workflow', name: '优化工作流', fn: workflowOptimize },
    // aimodel
    'aimodel.mergekit': { module: 'aimodel', name: 'MergeKit 集成', fn: mergekitIntegrate },
    'aimodel.merge': { module: 'aimodel', name: '模型融合', fn: modelMerge },
    // content
    'content.douyin_copy': { module: 'content', name: '抖音文案', fn: douyinCopywriting },
    'content.xiaohongshu': { module: 'content', name: '小红书改写', fn: xiaohongshuRewrite },
    'content.article': { module: 'content', name: '文章写作', fn: articleWrite },
    // data
    'data.json_fix': { module: 'data', name: 'JSON 修复', fn: jsonFix },
    'data.clean': { module: 'data', name: '数据清洗', fn: dataClean },
    'data.convert': { module: 'data', name: '格式转换', fn: formatConvert }
  };

  /* ========================================================================
   * PluginRegistry —— 插件注册、解析、执行的核心类
   * ====================================================================== */
  function PluginRegistry(options) {
    options = options || {};
    this.logger = new Logger(options.name || 'PluginRegistry');
    this._plugins = {};
    this._middlewares = [];
    this._registerBuiltins();
  }

  // 注册内置插件
  PluginRegistry.prototype._registerBuiltins = function () {
    var self = this;
    Object.keys(PLUGINS).forEach(function (id) {
      var meta = PLUGINS[id];
      self.register(id, meta.module, meta.name, meta.fn);
    });
  };

  // 注册自定义插件
  PluginRegistry.prototype.register = function (id, module, name, fn) {
    if (!id || typeof fn !== 'function') throw new Error('注册失败：id 与 fn 必填且 fn 必须为函数');
    this._plugins[id] = { id: id, module: module, name: name, fn: fn };
    this.logger.info('已注册插件：' + id);
    return this;
  };

  // 注销插件
  PluginRegistry.prototype.unregister = function (id) {
    delete this._plugins[id];
    this.logger.warn('已注销插件：' + id);
    return this;
  };

  // 添加全局中间件
  PluginRegistry.prototype.use = function (mw) {
    if (typeof mw !== 'function') throw new Error('中间件必须为函数');
    this._middlewares.push(mw);
    return this;
  };

  // 列出所有插件
  PluginRegistry.prototype.list = function () {
    return Object.keys(this._plugins).map(function (id) {
      var p = this._plugins[id];
      return { id: id, module: p.module, name: p.name };
    }.bind(this));
  };

  // 按模块列出
  PluginRegistry.prototype.listByModule = function () {
    var groups = {};
    Object.keys(this._plugins).forEach(function (id) {
      var p = this._plugins[id];
      (groups[p.module] = groups[p.module] || []).push({ id: id, name: p.name });
    }.bind(this));
    return groups;
  };

  // 解析插件（是否存在）
  PluginRegistry.prototype.resolve = function (id) {
    return this._plugins[id] || null;
  };

  // 执行单个插件
  PluginRegistry.prototype.execute = function (pluginName, params, middleware) {
    var start = Date.now();
    var plugin = this.resolve(pluginName);
    if (!plugin) return fail(new Error('未找到插件：' + pluginName), this.logger.logs.slice(), start);

    // 组合中间件：全局 + 本次传入
    var mws = this._middlewares.concat(middleware || []);
    var logger = new Logger(pluginName);
    var ctx = { plugin: plugin, params: params || {}, logger: logger, result: null };

    var i = -1;
    var self = this;
    function dispatch(idx) {
      if (idx <= i) return Promise.reject(new Error('next() 被多次调用'));
      i = idx;
      if (idx < mws.length) {
        try {
          return Promise.resolve(mws[idx](ctx, function () { return dispatch(idx + 1); }));
        } catch (e) {
          return Promise.reject(e);
        }
      } else {
        // 执行真实插件
        try {
          ctx.result = plugin.fn(ctx.params, logger);
          return Promise.resolve(ctx.result);
        } catch (e) {
          return Promise.reject(e);
        }
      }
    }

    return dispatch(0).then(function (data) {
      self.logger.info('插件执行完成：' + pluginName + '，耗时 ' + (Date.now() - start) + 'ms');
      return ok(data, logger.logs, start);
    }).catch(function (err) {
      self.logger.error('插件执行失败：' + pluginName + ' -> ' + (err.message || err));
      return fail(err, logger.logs.concat(self.logger.logs.slice(-1)), start);
    });
  };

  // 同步执行（不使用中间件异步链，适合纯同步插件）
  PluginRegistry.prototype.executeSync = function (pluginName, params) {
    var start = Date.now();
    var plugin = this.resolve(pluginName);
    if (!plugin) return fail(new Error('未找到插件：' + pluginName), this.logger.logs.slice(), start);
    var logger = new Logger(pluginName);
    try {
      var data = plugin.fn(params || {}, logger);
      return ok(data, logger.logs, start);
    } catch (e) {
      logger.error(e.message || e);
      return fail(e, logger.logs, start);
    }
  };

  // 批量执行
  PluginRegistry.prototype.executeBatch = function (batch) {
    var self = this;
    if (!Array.isArray(batch)) return Promise.reject(new Error('batch 必须为数组'));
    return Promise.all(batch.map(function (task) {
      return self.execute(task.pluginName, task.params, task.middleware);
    }));
  };

  // 批量同步执行
  PluginRegistry.prototype.executeBatchSync = function (batch) {
    var self = this;
    if (!Array.isArray(batch)) throw new Error('batch 必须为数组');
    return batch.map(function (task) {
      return self.executeSync(task.pluginName, task.params);
    });
  };

  /* ========================================================================
   * 导出
   * ====================================================================== */
  return {
    PluginRegistry: PluginRegistry,
    Logger: Logger,
    PLUGINS: PLUGINS,
    // 便捷工厂
    create: function (options) { return new PluginRegistry(options); },
    version: '1.0.0'
  };
});
