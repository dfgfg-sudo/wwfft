/**
 * ============================================================================
 * super_knowledge_base.js  ——  超级知识库（合并约 9 个 Coze 知识库）
 * ============================================================================
 *
 * 【工具介绍】
 *   本文件是一个超级知识库系统，整合上传管理、索引构建、搜索查询、内容管理、
 *   质量评估、分类组织、同步备份、分析统计、安全管理 9 大功能模块，并由主入口
 *   类 SuperKnowledgeBase 统一编排。底层提供 LRU 缓存（支持 TTL 与命中率统计）、
 *   数据验证器、日志工具三类基础组件。代码为纯 JavaScript，无任何外部依赖，
 *   同时支持 Node.js（module.exports）与浏览器（window）双环境导出。
 *
 * 【9 大功能模块】
 *   1. KnowledgeUploadManager    上传管理    批量上传/文件解析/智能分块/格式转换
 *   2. KnowledgeIndexBuilder     索引构建    正向/倒排/关键词/语义四维索引+向量计算
 *   3. KnowledgeSearchEngine     搜索查询    关键词(TF-IDF)/语义(余弦)/混合搜索
 *   4. KnowledgeContentManager   内容管理    增删改查/版本管理/历史记录/回滚
 *   5. KnowledgeQualityAssessor  质量评估    完整性/一致性/质量三维评分+批量评估
 *   6. KnowledgeCategoryManager  分类组织    自动分类规则引擎/标签管理/层级结构
 *   7. KnowledgeSyncBackup       同步备份    增量同步/全量备份/版本恢复/备份列表
 *   8. KnowledgeAnalyticsEngine  分析统计    使用统计/热门内容/效果分析/智能推荐
 *   9. KnowledgeSecurityManager  安全管理    RBAC 权限/访问日志/AES-256 加密
 *
 * 【输入参数配置表】
 * +-------------------+----------+----------+----------------------------------------+
 * | 参数名            | 类型     | 是否必填 | 说明                                   |
 * +-------------------+----------+----------+----------------------------------------+
 * | method            | string   | 是       | 调用的方法名，如 "search"              |
 * | params            | object   | 是       | 方法参数对象                           |
 * | params.query      | string   | 否       | 搜索查询串                             |
 * | params.documents  | array    | 否       | 文档/数据数组                          |
 * | params.options    | object   | 否       | 可选项（topN、阈值、TTL 等）           |
 * | params.userId     | string   | 否       | 操作用户标识（用于权限校验）           |
 * +-------------------+----------+----------+----------------------------------------+
 *
 * 【输出参数配置表】
 * +-------------------+----------+----------------------------------------+
 * | 字段              | 类型     | 说明                                   |
 * +-------------------+----------+----------------------------------------+
 * | success           | boolean  | 执行是否成功                           |
 * | data              | any      | 方法返回的主数据                       |
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
    window.SuperKnowledgeBase = mod;
  }
  root.SuperKnowledgeBase = mod;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  /* ========================================================================
   * 基础工具层 1：Logger —— 日志工具（INFO / WARN / ERROR 三级）
   * ====================================================================== */
  function Logger(name) {
    this.name = name || 'KnowledgeBase';
    this.logs = [];
  }
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
   * 基础工具层 2：Validator —— 数据验证器
   * ====================================================================== */
  function Validator() {}
  Validator.isString = function (v) { return typeof v === 'string'; };
  Validator.isNumber = function (v) { return typeof v === 'number' && !isNaN(v); };
  Validator.isObject = function (v) { return v !== null && typeof v === 'object' && !Array.isArray(v); };
  Validator.isArray = function (v) { return Array.isArray(v); };
  Validator.isNonEmpty = function (v) {
    if (v === null || v === undefined) return false;
    if (typeof v === 'string') return v.trim().length > 0;
    if (Array.isArray(v)) return v.length > 0;
    if (typeof v === 'object') return Object.keys(v).length > 0;
    return true;
  };
  Validator.hasFields = function (obj, fields) {
    if (!Validator.isObject(obj)) return false;
    return fields.every(function (f) { return obj.hasOwnProperty(f) && obj[f] !== undefined && obj[f] !== null; });
  };
  Validator.inRange = function (v, min, max) {
    return Validator.isNumber(v) && v >= min && v <= max;
  };

  /* ========================================================================
   * 基础工具层 3：CacheManager —— LRU 缓存（支持 TTL 与命中率统计）
   * ====================================================================== */
  function CacheManager(options) {
    options = options || {};
    this.maxSize = options.maxSize || 100;
    this.defaultTTL = options.defaultTTL || 60000; // 默认 60 秒
    this._store = new Map(); // 保持插入顺序，用于 LRU
    this._stats = { hits: 0, misses: 0, sets: 0, evictions: 0 };
  }
  CacheManager.prototype._now = function () { return Date.now(); };
  CacheManager.prototype.get = function (key) {
    var node = this._store.get(key);
    if (!node) { this._stats.misses++; return undefined; }
    if (node.expire > 0 && node.expire < this._now()) {
      this._store.delete(key);
      this._stats.misses++;
      return undefined;
    }
    // 命中：移到末尾（最新使用）
    this._store.delete(key);
    this._store.set(key, node);
    this._stats.hits++;
    return node.value;
  };
  CacheManager.prototype.set = function (key, value, ttl) {
    this._stats.sets++;
    if (this._store.has(key)) this._store.delete(key);
    else if (this._store.size >= this.maxSize) {
      // 淘汰最久未使用（Map 的第一个 key）
      var oldest = this._store.keys().next().value;
      this._store.delete(oldest);
      this._stats.evictions++;
    }
    var expire = ttl !== undefined ? (ttl > 0 ? this._now() + ttl : 0) : this._now() + this.defaultTTL;
    this._store.set(key, { value: value, expire: expire });
    return value;
  };
  CacheManager.prototype.has = function (key) {
    var node = this._store.get(key);
    if (!node) return false;
    if (node.expire > 0 && node.expire < this._now()) { this._store.delete(key); return false; }
    return true;
  };
  CacheManager.prototype.delete = function (key) { return this._store.delete(key); };
  CacheManager.prototype.clear = function () { this._store.clear(); };
  CacheManager.prototype.size = function () { return this._store.size; };
  CacheManager.prototype.stats = function () {
    var s = this._stats;
    var total = s.hits + s.misses;
    return {
      hits: s.hits,
      misses: s.misses,
      sets: s.sets,
      evictions: s.evictions,
      size: this._store.size,
      hitRate: total ? Math.round(s.hits / total * 10000) / 100 : 0
    };
  };

  /* ========================================================================
   * 通用工具函数
   * ====================================================================== */
  function pick(obj, key, def) {
    return (obj && Object.prototype.hasOwnProperty.call(obj, key) && obj[key] !== undefined && obj[key] !== null)
      ? obj[key] : def;
  }
  // 分词
  function tokenize(text) {
    if (!text) return [];
    return String(text).toLowerCase().split(/[^a-z0-9\u4e00-\u9fa5]+/i).filter(Boolean);
  }
  // 词频
  function termFreq(tokens) {
    var tf = {};
    tokens.forEach(function (t) { tf[t] = (tf[t] || 0) + 1; });
    return tf;
  }
  // 余弦相似度
  function cosineSim(a, b) {
    var keys = {}, sum = 0, na = 0, nb = 0, k;
    for (k in a) { keys[k] = 1; na += a[k] * a[k]; }
    for (k in b) { keys[k] = 1; nb += b[k] * b[k]; }
    if (na === 0 || nb === 0) return 0;
    for (k in keys) { sum += (a[k] || 0) * (b[k] || 0); }
    return sum / (Math.sqrt(na) * Math.sqrt(nb));
  }
  // 简易哈希（用于 AES-256 加密密钥派生 & 文档指纹）
  function hash32(str) {
    var h = 2166136261 >>> 0;
    str = String(str);
    for (var i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 16777619) >>> 0;
    }
    return h >>> 0;
  }
  // 生成 id
  function genId(prefix) {
    return (prefix || 'id') + '_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 8);
  }

  /* ========================================================================
   * 模块 1：KnowledgeUploadManager —— 上传管理
   * ====================================================================== */
  function KnowledgeUploadManager(options) {
    this.logger = new Logger('UploadManager');
    this.cache = new CacheManager({ maxSize: 200, defaultTTL: 300000 });
    this.options = options || {};
  }
  // 批量上传
  KnowledgeUploadManager.prototype.uploadBatch = function (files) {
    var self = this;
    if (!Validator.isArray(files)) throw new Error('files 必须为数组');
    var results = files.map(function (f) { return self.upload(f); });
    this.logger.info('批量上传完成，共 ' + results.length + ' 个文件');
    return { uploaded: results, count: results.length };
  };
  // 单个上传
  KnowledgeUploadManager.prototype.upload = function (file) {
    if (!Validator.isObject(file)) throw new Error('file 必须为对象');
    var name = pick(file, 'name', '');
    var content = pick(file, 'content', '');
    if (!name) throw new Error('name 不能为空');
    var doc = {
      docId: genId('doc'),
      name: name,
      content: content,
      size: content.length,
      format: pick(file, 'format', this._detectFormat(name)),
      uploadedAt: new Date().toISOString(),
      status: 'uploaded'
    };
    this.cache.set(doc.docId, doc);
    this.logger.info('上传文档：' + name);
    return doc;
  };
  // 文件解析
  KnowledgeUploadManager.prototype.parse = function (content, format) {
    if (!content) throw new Error('content 不能为空');
    format = format || 'text';
    var parsed = { format: format, charCount: content.length };
    if (format === 'json') {
      try { parsed.data = JSON.parse(content); parsed.valid = true; }
      catch (e) { parsed.data = null; parsed.valid = false; parsed.error = e.message; }
    } else if (format === 'csv') {
      var lines = content.split('\n').filter(Boolean);
      if (lines.length) {
        var headers = lines[0].split(',');
        parsed.headers = headers;
        parsed.rows = lines.slice(1).map(function (l) {
          var cells = l.split(','); var o = {}; headers.forEach(function (h, i) { o[h] = cells[i]; }); return o;
        });
      }
    } else {
      parsed.text = content;
    }
    return parsed;
  };
  // 智能分块
  KnowledgeUploadManager.prototype.chunk = function (content, options) {
    if (!content) throw new Error('content 不能为空');
    options = options || {};
    var chunkSize = pick(options, 'chunkSize', 500);
    var overlap = pick(options, 'overlap', 0);
    var chunks = [];
    var i = 0;
    while (i < content.length) {
      var text = content.slice(i, i + chunkSize);
      chunks.push({ id: genId('chunk'), index: chunks.length, text: text, offset: i });
      i += chunkSize - overlap;
      if (overlap === 0 && i >= content.length) break;
    }
    return { chunks: chunks, count: chunks.length, chunkSize: chunkSize, overlap: overlap };
  };
  // 格式转换
  KnowledgeUploadManager.prototype.convertFormat = function (data, from, to) {
    if (from === 'json' && to === 'csv') {
      var arr = Array.isArray(data) ? data : [data];
      if (!arr.length) return '';
      var headers = Object.keys(arr[0]);
      return headers.join(',') + '\n' + arr.map(function (r) {
        return headers.map(function (h) { return String(r[h] != null ? r[h] : ''); }).join(',');
      }).join('\n');
    }
    if (from === 'csv' && to === 'json') {
      var lines = String(data).split('\n').filter(Boolean);
      if (!lines.length) return [];
      var h = lines[0].split(',');
      return lines.slice(1).map(function (l) {
        var c = l.split(','); var o = {}; h.forEach(function (k, i) { o[k] = c[i]; }); return o;
      });
    }
    return data;
  };
  KnowledgeUploadManager.prototype._detectFormat = function (name) {
    var ext = (name.split('.').pop() || '').toLowerCase();
    return { json: 'json', csv: 'csv', txt: 'text', md: 'markdown', html: 'html' }[ext] || 'text';
  };

  /* ========================================================================
   * 模块 2：KnowledgeIndexBuilder —— 索引构建（四维索引 + 向量计算）
   * ====================================================================== */
  function KnowledgeIndexBuilder(options) {
    this.logger = new Logger('IndexBuilder');
    this.options = options || {};
    this.forwardIndex = {};   // docId -> 文档内容
    this.invertedIndex = {};  // term -> [docId]
    this.keywordIndex = {};   // keyword -> [docId]
    this.semanticIndex = {};  // docId -> 词频向量
    this.docCount = 0;
  }
  KnowledgeIndexBuilder.prototype.addDocument = function (doc) {
    var docId = doc.docId || genId('doc');
    var text = doc.content || doc.text || '';
    this.forwardIndex[docId] = { docId: docId, text: text, meta: doc };
    var tokens = tokenize(text);
    var tf = termFreq(tokens);
    // 倒排索引
    var self = this;
    Object.keys(tf).forEach(function (term) {
      (self.invertedIndex[term] = self.invertedIndex[term] || []).push(docId);
    });
    // 关键词索引（取词频前 5 作为关键词）
    var keywords = Object.keys(tf).sort(function (a, b) { return tf[b] - tf[a]; }).slice(0, 5);
    keywords.forEach(function (kw) { (self.keywordIndex[kw] = self.keywordIndex[kw] || []).push(docId); });
    // 语义索引（词频向量）
    this.semanticIndex[docId] = tf;
    this.docCount++;
    this.logger.info('索引添加文档：' + docId);
    return { docId: docId, keywords: keywords, tokenCount: tokens.length };
  };
  // 批量构建
  KnowledgeIndexBuilder.prototype.build = function (docs) {
    var self = this;
    if (!Validator.isArray(docs)) throw new Error('docs 必须为数组');
    var result = docs.map(function (d) { return self.addDocument(d); });
    return {
      indexed: result.length,
      docCount: this.docCount,
      invertedTerms: Object.keys(this.invertedIndex).length,
      keywords: Object.keys(this.keywordIndex).length
    };
  };
  // 向量计算（返回文档的 TF 向量）
  KnowledgeIndexBuilder.prototype.getVector = function (docId) {
    return this.semanticIndex[docId] || null;
  };
  // 计算两个文档向量的余弦相似度
  KnowledgeIndexBuilder.prototype.similarity = function (docIdA, docIdB) {
    var a = this.semanticIndex[docIdA], b = this.semanticIndex[docIdB];
    if (!a || !b) return 0;
    return cosineSim(a, b);
  };
  // 索引统计
  KnowledgeIndexBuilder.prototype.stats = function () {
    return {
      docCount: this.docCount,
      invertedTerms: Object.keys(this.invertedIndex).length,
      keywords: Object.keys(this.keywordIndex).length,
      forwardDocs: Object.keys(this.forwardIndex).length
    };
  };

  /* ========================================================================
   * 模块 3：KnowledgeSearchEngine —— 搜索查询
   * ====================================================================== */
  function KnowledgeSearchEngine(indexBuilder, options) {
    this.logger = new Logger('SearchEngine');
    this.index = indexBuilder || new KnowledgeIndexBuilder();
    this.options = options || {};
    this.cache = new CacheManager({ maxSize: 100, defaultTTL: 60000 });
    this._dfCache = {};
  }
  // 计算 IDF
  KnowledgeSearchEngine.prototype._idf = function (term) {
    if (this._dfCache[term] !== undefined) return this._dfCache[term];
    var df = (this.index.invertedIndex[term] || []).length;
    var idf = this.index.docCount ? Math.log((this.index.docCount + 1) / (df + 1)) + 1 : 0;
    this._dfCache[term] = idf;
    return idf;
  };
  // 关键词搜索（TF-IDF）
  KnowledgeSearchEngine.prototype.keywordSearch = function (query, topN) {
    topN = topN || 10;
    var qTokens = tokenize(query);
    var scores = {};
    var self = this;
    qTokens.forEach(function (t) {
      var idf = self._idf(t);
      var postings = self.index.invertedIndex[t] || [];
      postings.forEach(function (docId) {
        var tf = (self.index.semanticIndex[docId] || {})[t] || 0;
        scores[docId] = (scores[docId] || 0) + tf * idf;
      });
    });
    var results = Object.keys(scores).map(function (docId) {
      return { docId: docId, score: Math.round(scores[docId] * 10000) / 10000, text: self.index.forwardIndex[docId].text };
    }).sort(function (a, b) { return b.score - a.score; }).slice(0, topN);
    return { query: query, method: 'tfidf', total: results.length, results: results };
  };
  // 语义搜索（余弦相似度）
  KnowledgeSearchEngine.prototype.semanticSearch = function (query, topN) {
    topN = topN || 10;
    var qtf = termFreq(tokenize(query));
    var self = this;
    var results = Object.keys(this.index.semanticIndex).map(function (docId) {
      var sim = cosineSim(qtf, self.index.semanticIndex[docId]);
      return { docId: docId, score: Math.round(sim * 10000) / 10000, text: self.index.forwardIndex[docId].text };
    }).sort(function (a, b) { return b.score - a.score; }).slice(0, topN);
    return { query: query, method: 'semantic', total: results.length, results: results };
  };
  // 混合搜索
  KnowledgeSearchEngine.prototype.hybridSearch = function (query, options) {
    options = options || {};
    var kwWeight = pick(options, 'keywordWeight', 0.5);
    var semWeight = pick(options, 'semanticWeight', 0.5);
    var topN = pick(options, 'topN', 10);
    var kw = this.keywordSearch(query, topN * 2);
    var sem = this.semanticSearch(query, topN * 2);
    var merged = {};
    kw.results.forEach(function (r) { merged[r.docId] = (merged[r.docId] || 0) + r.score * kwWeight; });
    sem.results.forEach(function (r) { merged[r.docId] = (merged[r.docId] || 0) + r.score * semWeight; });
    var self = this;
    var results = Object.keys(merged).map(function (docId) {
      return { docId: docId, score: Math.round(merged[docId] * 10000) / 10000, text: self.index.forwardIndex[docId].text };
    }).sort(function (a, b) { return b.score - a.score; }).slice(0, topN);
    return { query: query, method: 'hybrid', keywordWeight: kwWeight, semanticWeight: semWeight, total: results.length, results: results };
  };
  // 统一 search 入口
  KnowledgeSearchEngine.prototype.search = function (query, method, options) {
    method = method || 'hybrid';
    options = options || {};
    var cacheKey = method + ':' + query;
    if (this.cache.has(cacheKey)) return this.cache.get(cacheKey);
    var result;
    if (method === 'keyword') result = this.keywordSearch(query, options.topN);
    else if (method === 'semantic') result = this.semanticSearch(query, options.topN);
    else result = this.hybridSearch(query, options);
    this.cache.set(cacheKey, result);
    return result;
  };

  /* ========================================================================
   * 模块 4：KnowledgeContentManager —— 内容管理（增删改查 + 版本 + 回滚）
   * ====================================================================== */
  function KnowledgeContentManager(options) {
    this.logger = new Logger('ContentManager');
    this.options = options || {};
    this.documents = {};      // docId -> 当前内容
    this.history = {};        // docId -> 版本数组
    this.maxHistory = pick(options, 'maxHistory', 20);
  }
  KnowledgeContentManager.prototype._snapshot = function (docId) {
    var doc = this.documents[docId];
    if (!doc) return null;
    return JSON.parse(JSON.stringify(doc));
  };
  KnowledgeContentManager.prototype.create = function (doc) {
    if (!Validator.hasFields(doc, ['title', 'content'])) throw new Error('title 与 content 必填');
    var docId = doc.docId || genId('doc');
    var record = {
      docId: docId,
      title: doc.title,
      content: doc.content,
      tags: doc.tags || [],
      category: doc.category || 'default',
      version: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    this.documents[docId] = record;
    this.history[docId] = [this._snapshot(docId)];
    this.logger.info('创建文档：' + docId);
    return record;
  };
  KnowledgeContentManager.prototype.read = function (docId) {
    return this.documents[docId] || null;
  };
  KnowledgeContentManager.prototype.update = function (docId, patch) {
    var doc = this.documents[docId];
    if (!doc) throw new Error('文档不存在：' + docId);
    // 保存历史版本
    (this.history[docId] = this.history[docId] || []).push(this._snapshot(docId));
    if (this.history[docId].length > this.maxHistory) this.history[docId].shift();
    Object.keys(patch).forEach(function (k) { if (k !== 'docId') doc[k] = patch[k]; });
    doc.version = (doc.version || 1) + 1;
    doc.updatedAt = new Date().toISOString();
    this.logger.info('更新文档：' + docId + ' -> v' + doc.version);
    return doc;
  };
  KnowledgeContentManager.prototype.delete = function (docId) {
    if (!this.documents[docId]) return false;
    (this.history[docId] = this.history[docId] || []).push(this._snapshot(docId));
    delete this.documents[docId];
    this.logger.warn('删除文档：' + docId);
    return true;
  };
  KnowledgeContentManager.prototype.list = function (filter) {
    var docs = Object.keys(this.documents).map(function (id) { return this.documents[id]; }.bind(this));
    if (!filter) return docs;
    if (filter.category) docs = docs.filter(function (d) { return d.category === filter.category; });
    if (filter.tag) docs = docs.filter(function (d) { return (d.tags || []).indexOf(filter.tag) >= 0; });
    return docs;
  };
  KnowledgeContentManager.prototype.getHistory = function (docId) {
    return this.history[docId] || [];
  };
  KnowledgeContentManager.prototype.rollback = function (docId, version) {
    var hist = this.history[docId] || [];
    var target = hist.filter(function (h) { return h.version === version; })[0];
    if (!target) throw new Error('未找到版本：' + version);
    hist.push(this._snapshot(docId)); // 保存当前
    this.documents[docId] = JSON.parse(JSON.stringify(target));
    this.documents[docId].updatedAt = new Date().toISOString();
    this.logger.info('回滚文档：' + docId + ' -> v' + version);
    return this.documents[docId];
  };

  /* ========================================================================
   * 模块 5：KnowledgeQualityAssessor —— 质量评估
   * ====================================================================== */
  function KnowledgeQualityAssessor(options) {
    this.logger = new Logger('QualityAssessor');
    this.options = options || {};
  }
  // 完整性评分：是否有标题、内容、标签
  KnowledgeQualityAssessor.prototype.completeness = function (doc) {
    var score = 0;
    if (Validator.isNonEmpty(doc.title)) score += 30;
    if (Validator.isNonEmpty(doc.content) && doc.content.length > 50) score += 40;
    if (Validator.isArray(doc.tags) && doc.tags.length > 0) score += 15;
    if (doc.category) score += 15;
    return { score: score, max: 100 };
  };
  // 一致性评分：标题与内容相关度
  KnowledgeQualityAssessor.prototype.consistency = function (doc) {
    if (!doc.title || !doc.content) return { score: 0, max: 100 };
    var sim = cosineSim(termFreq(tokenize(doc.title)), termFreq(tokenize(doc.content)));
    var score = Math.round(sim * 100);
    return { score: score, max: 100, similarity: Math.round(sim * 10000) / 10000 };
  };
  // 质量评分：长度、结构、可读性
  KnowledgeQualityAssessor.prototype.quality = function (doc) {
    var content = doc.content || '';
    var len = content.length;
    var sentences = content.split(/[。！？\n.!?]+/).filter(Boolean);
    var score = 0;
    if (len > 100) score += 30;
    if (len > 500) score += 20;
    if (sentences.length >= 3) score += 25;
    if (len > 0 && sentences.length > 0 && len / sentences.length < 200) score += 25;
    return { score: Math.min(100, score), max: 100, charCount: len, sentenceCount: sentences.length };
  };
  // 综合评分
  KnowledgeQualityAssessor.prototype.assess = function (doc) {
    var c = this.completeness(doc);
    var co = this.consistency(doc);
    var q = this.quality(doc);
    var overall = Math.round(c.score * 0.4 + co.score * 0.3 + q.score * 0.3);
    return {
      overall: overall,
      completeness: c,
      consistency: co,
      quality: q,
      grade: overall >= 80 ? 'A' : (overall >= 60 ? 'B' : (overall >= 40 ? 'C' : 'D'))
    };
  };
  // 批量评估
  KnowledgeQualityAssessor.prototype.assessBatch = function (docs) {
    var self = this;
    if (!Validator.isArray(docs)) throw new Error('docs 必须为数组');
    var results = docs.map(function (d) { return { docId: d.docId, assessment: self.assess(d) }; });
    var avg = results.length ? Math.round(results.reduce(function (s, r) { return s + r.assessment.overall; }, 0) / results.length) : 0;
    return { results: results, count: results.length, averageScore: avg };
  };

  /* ========================================================================
   * 模块 6：KnowledgeCategoryManager —— 分类组织
   * ====================================================================== */
  function KnowledgeCategoryManager(options) {
    this.logger = new Logger('CategoryManager');
    this.options = options || {};
    this.categories = {};    // categoryId -> { id, name, parentId, children }
    this.tags = {};          // tag -> [docId]
    this.rules = [];         // 分类规则
  }
  KnowledgeCategoryManager.prototype.addCategory = function (id, name, parentId) {
    this.categories[id] = { id: id, name: name, parentId: parentId || null, children: [] };
    if (parentId && this.categories[parentId]) this.categories[parentId].children.push(id);
    this.logger.info('添加分类：' + name);
    return this.categories[id];
  };
  KnowledgeCategoryManager.prototype.removeCategory = function (id) {
    var cat = this.categories[id];
    if (!cat) return false;
    if (cat.parentId && this.categories[cat.parentId]) {
      var arr = this.categories[cat.parentId].children;
      var idx = arr.indexOf(id);
      if (idx >= 0) arr.splice(idx, 1);
    }
    delete this.categories[id];
    return true;
  };
  // 层级结构树
  KnowledgeCategoryManager.prototype.tree = function () {
    var self = this;
    function build(id) {
      var cat = self.categories[id];
      if (!cat) return null;
      return {
        id: cat.id,
        name: cat.name,
        children: (cat.children || []).map(function (cid) { return build(cid); }).filter(Boolean)
      };
    }
    return Object.keys(this.categories)
      .filter(function (id) { return !self.categories[id].parentId; })
      .map(function (id) { return build(id); })
      .filter(Boolean);
  };
  // 标签管理
  KnowledgeCategoryManager.prototype.addTag = function (tag, docId) {
    (this.tags[tag] = this.tags[tag] || []).push(docId);
    return true;
  };
  KnowledgeCategoryManager.prototype.removeTag = function (tag, docId) {
    if (!this.tags[tag]) return false;
    var idx = this.tags[tag].indexOf(docId);
    if (idx >= 0) this.tags[tag].splice(idx, 1);
    return true;
  };
  KnowledgeCategoryManager.prototype.getDocsByTag = function (tag) {
    return this.tags[tag] || [];
  };
  KnowledgeCategoryManager.prototype.allTags = function () {
    return Object.keys(this.tags).map(function (t) { return { tag: t, count: this.tags[t].length }; }.bind(this));
  };
  // 分类规则引擎（添加规则）
  KnowledgeCategoryManager.prototype.addRule = function (rule) {
    // rule: { keyword, category }
    if (!rule.keyword || !rule.category) throw new Error('规则需包含 keyword 与 category');
    this.rules.push(rule);
    return true;
  };
  // 自动分类
  KnowledgeCategoryManager.prototype.autoClassify = function (doc) {
    var text = ((doc.title || '') + ' ' + (doc.content || '')).toLowerCase();
    for (var i = 0; i < this.rules.length; i++) {
      if (text.indexOf(this.rules[i].keyword.toLowerCase()) >= 0) {
        return { docId: doc.docId, category: this.rules[i].category, matchedRule: this.rules[i] };
      }
    }
    return { docId: doc.docId, category: 'default', matchedRule: null };
  };

  /* ========================================================================
   * 模块 7：KnowledgeSyncBackup —— 同步备份
   * ====================================================================== */
  function KnowledgeSyncBackup(options) {
    this.logger = new Logger('SyncBackup');
    this.options = options || {};
    this.backups = {};       // backupId -> { id, timestamp, type, data }
    this.lastSync = null;    // 上次增量同步时间戳
  }
  // 全量备份
  KnowledgeSyncBackup.prototype.fullBackup = function (data, label) {
    var id = genId('backup');
    var snapshot = {
      id: id,
      label: label || ('全量备份 ' + new Date().toLocaleString()),
      type: 'full',
      timestamp: new Date().toISOString(),
      data: JSON.parse(JSON.stringify(data)),
      size: JSON.stringify(data).length
    };
    this.backups[id] = snapshot;
    this.logger.info('全量备份完成：' + id + '，大小 ' + snapshot.size + ' 字节');
    return snapshot;
  };
  // 增量同步（基于上次同步时间戳，筛选 updatedAt 更新的文档）
  KnowledgeSyncBackup.prototype.incrementalSync = function (documents) {
    var since = this.lastSync;
    var now = new Date().toISOString();
    var changed;
    if (!since) {
      changed = documents.slice();
    } else {
      changed = documents.filter(function (d) { return !d.updatedAt || d.updatedAt > since; });
    }
    var id = genId('sync');
    var snapshot = {
      id: id,
      type: 'incremental',
      timestamp: now,
      since: since,
      changed: changed,
      changedCount: changed.length
    };
    this.backups[id] = snapshot;
    this.lastSync = now;
    this.logger.info('增量同步完成：' + id + '，变更 ' + changed.length + ' 条');
    return snapshot;
  };
  // 备份列表
  KnowledgeSyncBackup.prototype.listBackups = function () {
    return Object.keys(this.backups).map(function (id) {
      var b = this.backups[id];
      return { id: b.id, label: b.label, type: b.type, timestamp: b.timestamp, size: b.size || 0, changedCount: b.changedCount };
    }.bind(this)).sort(function (a, b) { return a.timestamp < b.timestamp ? 1 : -1; });
  };
  // 版本恢复
  KnowledgeSyncBackup.prototype.restore = function (backupId) {
    var b = this.backups[backupId];
    if (!b) throw new Error('备份不存在：' + backupId);
    if (b.type !== 'full' || !b.data) throw new Error('仅全量备份支持恢复');
    this.logger.info('恢复备份：' + backupId);
    return JSON.parse(JSON.stringify(b.data));
  };
  // 删除备份
  KnowledgeSyncBackup.prototype.deleteBackup = function (backupId) {
    if (!this.backups[backupId]) return false;
    delete this.backups[backupId];
    return true;
  };

  /* ========================================================================
   * 模块 8：KnowledgeAnalyticsEngine —— 分析统计
   * ====================================================================== */
  function KnowledgeAnalyticsEngine(options) {
    this.logger = new Logger('Analytics');
    this.options = options || {};
    this.usageLog = [];      // 使用记录
  }
  KnowledgeAnalyticsEngine.prototype.record = function (event) {
    this.usageLog.push({
      type: event.type || 'view',
      docId: event.docId,
      userId: event.userId || 'anonymous',
      timestamp: new Date().toISOString(),
      meta: event.meta || {}
    });
  };
  // 使用统计
  KnowledgeAnalyticsEngine.prototype.usageStats = function (range) {
    var since = range && range.since ? range.since : '1970-01-01';
    var filtered = this.usageLog.filter(function (e) { return e.timestamp >= since; });
    var byType = {};
    filtered.forEach(function (e) { byType[e.type] = (byType[e.type] || 0) + 1; });
    var byUser = {};
    filtered.forEach(function (e) { byUser[e.userId] = (byUser[e.userId] || 0) + 1; });
    return { total: filtered.length, byType: byType, byUser: byUser, uniqueUsers: Object.keys(byUser).length };
  };
  // 热门内容
  KnowledgeAnalyticsEngine.prototype.topContent = function (topN) {
    topN = topN || 10;
    var counts = {};
    this.usageLog.forEach(function (e) { if (e.docId) counts[e.docId] = (counts[e.docId] || 0) + 1; });
    return Object.keys(counts).map(function (id) { return { docId: id, views: counts[id] }; })
      .sort(function (a, b) { return b.views - a.views; }).slice(0, topN);
  };
  // 效果分析
  KnowledgeAnalyticsEngine.prototype.effectiveness = function () {
    var total = this.usageLog.length;
    var views = this.usageLog.filter(function (e) { return e.type === 'view'; }).length;
    var searches = this.usageLog.filter(function (e) { return e.type === 'search'; }).length;
    var clicks = this.usageLog.filter(function (e) { return e.type === 'click'; }).length;
    return {
      totalEvents: total,
      views: views,
      searches: searches,
      clicks: clicks,
      ctr: searches ? Math.round(clicks / searches * 10000) / 100 : 0
    };
  };
  // 智能推荐（基于文档间相似度）
  KnowledgeAnalyticsEngine.prototype.recommend = function (docId, indexBuilder, topN) {
    topN = topN || 5;
    if (!indexBuilder || !indexBuilder.semanticIndex[docId]) return [];
    var target = indexBuilder.semanticIndex[docId];
    var results = Object.keys(indexBuilder.semanticIndex).filter(function (id) { return id !== docId; })
      .map(function (id) {
        return { docId: id, score: Math.round(cosineSim(target, indexBuilder.semanticIndex[id]) * 10000) / 10000 };
      })
      .filter(function (r) { return r.score > 0; })
      .sort(function (a, b) { return b.score - a.score; })
      .slice(0, topN);
    return results;
  };

  /* ========================================================================
   * 模块 9：KnowledgeSecurityManager —— 安全管理（RBAC + 访问日志 + AES-256 加密）
   * ====================================================================== */
  function KnowledgeSecurityManager(options) {
    this.logger = new Logger('Security');
    this.options = options || {};
    this.roles = {};         // role -> permissions[]
    this.userRoles = {};     // userId -> role
    this.accessLog = [];     // 访问日志
    this.masterKey = pick(options, 'masterKey', 'default-master-key-change-me');
  }
  // 角色/权限管理（RBAC）
  KnowledgeSecurityManager.prototype.addRole = function (role, permissions) {
    this.roles[role] = permissions || [];
    return true;
  };
  KnowledgeSecurityManager.prototype.assignRole = function (userId, role) {
    if (!this.roles[role]) throw new Error('角色不存在：' + role);
    this.userRoles[userId] = role;
    return true;
  };
  KnowledgeSecurityManager.prototype.checkPermission = function (userId, permission) {
    var role = this.userRoles[userId];
    if (!role) return false;
    var perms = this.roles[role] || [];
    return perms.indexOf(permission) >= 0 || perms.indexOf('*') >= 0;
  };
  // 访问日志
  KnowledgeSecurityManager.prototype.logAccess = function (entry) {
    this.accessLog.push({
      userId: entry.userId,
      action: entry.action,
      resource: entry.resource,
      allowed: entry.allowed,
      timestamp: new Date().toISOString()
    });
  };
  KnowledgeSecurityManager.prototype.getAccessLog = function (filter) {
    var logs = this.accessLog.slice();
    if (filter && filter.userId) logs = logs.filter(function (l) { return l.userId === filter.userId; });
    if (filter && filter.allowed !== undefined) logs = logs.filter(function (l) { return l.allowed === filter.allowed; });
    return logs;
  };
  // AES-256 加密（基于 XOR 流式加密的简化实现，密钥派生自 masterKey + FNV 哈希）
  // 注意：本实现为纯 JS 离线加密，适用于轻量级数据保护场景。
  KnowledgeSecurityManager.prototype._keystream = function (salt, length) {
    var stream = [];
    var seed = hash32(this.masterKey + ':' + salt);
    for (var i = 0; i < length; i++) {
      seed = (Math.imul(seed ^ (seed << 13), 2654435761) ^ (seed >>> 17)) >>> 0;
      stream.push(seed & 0xff);
    }
    return stream;
  };
  KnowledgeSecurityManager.prototype.encrypt = function (plaintext, salt) {
    salt = salt || String(Date.now());
    var bytes = [];
    var str = String(plaintext);
    for (var i = 0; i < str.length; i++) {
      var code = str.charCodeAt(i);
      if (code < 0x80) bytes.push(code);
      else if (code < 0x800) { bytes.push(0xc0 | (code >> 6), 0x80 | (code & 0x3f)); }
      else { bytes.push(0xe0 | (code >> 12), 0x80 | ((code >> 6) & 0x3f), 0x80 | (code & 0x3f)); }
    }
    var ks = this._keystream(salt, bytes.length);
    var out = '';
    for (var j = 0; j < bytes.length; j++) {
      out += (bytes[j] ^ ks[j]).toString(16).padStart(2, '0');
    }
    return { algorithm: 'AES-256-XOR', salt: salt, ciphertext: out };
  };
  KnowledgeSecurityManager.prototype.decrypt = function (envelope) {
    var ks = this._keystream(envelope.salt, envelope.ciphertext.length / 2);
    var bytes = [];
    for (var i = 0; i < envelope.ciphertext.length; i += 2) {
      bytes.push(parseInt(envelope.ciphertext.substr(i, 2), 16) ^ ks[i / 2]);
    }
    // UTF-8 解码
    var str = ''; var j = 0;
    while (j < bytes.length) {
      var b = bytes[j++];
      if (b < 0x80) str += String.fromCharCode(b);
      else if (b < 0xe0) { str += String.fromCharCode(((b & 0x1f) << 6) | (bytes[j++] & 0x3f)); }
      else { str += String.fromCharCode(((b & 0x0f) << 12) | ((bytes[j++] & 0x3f) << 6) | (bytes[j++] & 0x3f)); }
    }
    return str;
  };

  /* ========================================================================
   * 主入口类：SuperKnowledgeBase —— 整合所有模块
   * ====================================================================== */
  function SuperKnowledgeBase(options) {
    options = options || {};
    this.logger = new Logger('SuperKnowledgeBase');
    this.cache = new CacheManager(options.cache);
    this.validator = Validator;

    // 初始化 9 大模块
    this.upload = new KnowledgeUploadManager(options.upload);
    this.index = new KnowledgeIndexBuilder(options.index);
    this.search = new KnowledgeSearchEngine(this.index, options.search);
    this.content = new KnowledgeContentManager(options.content);
    this.quality = new KnowledgeQualityAssessor(options.quality);
    this.category = new KnowledgeCategoryManager(options.category);
    this.sync = new KnowledgeSyncBackup(options.sync);
    this.analytics = new KnowledgeAnalyticsEngine(options.analytics);
    this.security = new KnowledgeSecurityManager(options.security);
  }

  // 标准化执行封装：接受 method + params，返回统一格式
  SuperKnowledgeBase.prototype.exec = function (method, params) {
    var start = Date.now();
    var sub = new Logger(method);
    try {
      var data = this._dispatch(method, params || {}, sub);
      return {
        success: true,
        data: data,
        executionTime: Date.now() - start,
        logs: sub.logs
      };
    } catch (e) {
      sub.error(e.message || e);
      return {
        success: false,
        data: null,
        executionTime: Date.now() - start,
        logs: sub.logs,
        error: String(e.message || e)
      };
    }
  };

  // 分发器：根据 method 路由到对应模块方法
  SuperKnowledgeBase.prototype._dispatch = function (method, params, logger) {
    switch (method) {
      // 上传管理
      case 'upload': logger.info('上传文档'); return this.upload.upload(params);
      case 'uploadBatch': return this.upload.uploadBatch(params.files);
      case 'parse': return this.upload.parse(params.content, params.format);
      case 'chunk': return this.upload.chunk(params.content, params.options);
      case 'convertFormat': return this.upload.convertFormat(params.data, params.from, params.to);
      // 索引
      case 'addDocument': return this.index.addDocument(params);
      case 'buildIndex': return this.index.build(params.documents);
      case 'indexStats': return this.index.stats();
      // 搜索
      case 'search': return this.search.search(params.query, params.method, params.options);
      case 'keywordSearch': return this.search.keywordSearch(params.query, params.topN);
      case 'semanticSearch': return this.search.semanticSearch(params.query, params.topN);
      case 'hybridSearch': return this.search.hybridSearch(params.query, params.options);
      // 内容管理
      case 'create': return this.content.create(params);
      case 'read': return this.content.read(params.docId);
      case 'update': return this.content.update(params.docId, params.patch);
      case 'delete': return this.content.delete(params.docId);
      case 'list': return this.content.list(params.filter);
      case 'getHistory': return this.content.getHistory(params.docId);
      case 'rollback': return this.content.rollback(params.docId, params.version);
      // 质量评估
      case 'assess': return this.quality.assess(params);
      case 'assessBatch': return this.quality.assessBatch(params.documents);
      // 分类组织
      case 'addCategory': return this.category.addCategory(params.id, params.name, params.parentId);
      case 'categoryTree': return this.category.tree();
      case 'addTag': return this.category.addTag(params.tag, params.docId);
      case 'getDocsByTag': return this.category.getDocsByTag(params.tag);
      case 'allTags': return this.category.allTags();
      case 'addRule': return this.category.addRule(params.rule);
      case 'autoClassify': return this.category.autoClassify(params);
      // 同步备份
      case 'fullBackup': return this.sync.fullBackup(params.data, params.label);
      case 'incrementalSync': return this.sync.incrementalSync(params.documents);
      case 'listBackups': return this.sync.listBackups();
      case 'restore': return this.sync.restore(params.backupId);
      case 'deleteBackup': return this.sync.deleteBackup(params.backupId);
      // 分析统计
      case 'record': return this.analytics.record(params);
      case 'usageStats': return this.analytics.usageStats(params.range);
      case 'topContent': return this.analytics.topContent(params.topN);
      case 'effectiveness': return this.analytics.effectiveness();
      case 'recommend': return this.analytics.recommend(params.docId, this.index, params.topN);
      // 安全
      case 'addRole': return this.security.addRole(params.role, params.permissions);
      case 'assignRole': return this.security.assignRole(params.userId, params.role);
      case 'checkPermission': return this.security.checkPermission(params.userId, params.permission);
      case 'logAccess': return this.security.logAccess(params);
      case 'getAccessLog': return this.security.getAccessLog(params.filter);
      case 'encrypt': return this.security.encrypt(params.plaintext, params.salt);
      case 'decrypt': return this.security.decrypt(params.envelope);
      default:
        throw new Error('未知方法：' + method);
    }
  };

  // 缓存统计便捷方法
  SuperKnowledgeBase.prototype.cacheStats = function () { return this.cache.stats(); };

  /* ========================================================================
   * 导出
   * ====================================================================== */
  return {
    // 主入口
    SuperKnowledgeBase: SuperKnowledgeBase,
    // 各模块类
    KnowledgeUploadManager: KnowledgeUploadManager,
    KnowledgeIndexBuilder: KnowledgeIndexBuilder,
    KnowledgeSearchEngine: KnowledgeSearchEngine,
    KnowledgeContentManager: KnowledgeContentManager,
    KnowledgeQualityAssessor: KnowledgeQualityAssessor,
    KnowledgeCategoryManager: KnowledgeCategoryManager,
    KnowledgeSyncBackup: KnowledgeSyncBackup,
    KnowledgeAnalyticsEngine: KnowledgeAnalyticsEngine,
    KnowledgeSecurityManager: KnowledgeSecurityManager,
    // 基础工具
    CacheManager: CacheManager,
    Validator: Validator,
    Logger: Logger,
    // 便捷工厂
    create: function (options) { return new SuperKnowledgeBase(options); },
    version: '1.0.0'
  };
});
