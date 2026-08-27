/**
 * 知识库检索处理器
 * 在指定知识库中检索与query相关的文档，返回topK个最相关的结果
 */

class KBSearchHandler {
  constructor(config) {
    this.config = config;
    this.inputs = config.inputs || {};
    this.outputs = {};
    this.kbStore = new Map();
  }

  async execute() {
    try {
      this.validateInputs();
      const result = await this.process();
      this.outputs.result = result;
      return { success: true, outputs: this.outputs, logs: ['[kb_search] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[kb_search] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['query', 'kbId'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.query !== 'string' || this.inputs.query.trim() === '') {
      throw new Error('参数 query 不能为空字符串');
    }
    if (typeof this.inputs.kbId !== 'string' || this.inputs.kbId.trim() === '') {
      throw new Error('参数 kbId 必须是非空字符串');
    }
  }

  async process() {
    const query = this.inputs.query;
    const kbId = this.inputs.kbId;
    const topK = this.inputs.topK || 5;
    const threshold = this.inputs.threshold || 0.5;
    const searchMode = this.inputs.search_mode || 'semantic';
    const filters = this.inputs.filters || {};

    // 加载知识库
    const knowledgeBase = await this.loadKnowledgeBase(kbId);
    if (!knowledgeBase) {
      throw new Error('知识库不存在: ' + kbId);
    }

    // 执行检索
    const results = await this.search(knowledgeBase, query, {
      topK, threshold, searchMode, filters
    });

    return {
      query: query,
      kb_id: kbId,
      kb_name: knowledgeBase.name,
      search_mode: searchMode,
      top_k: topK,
      threshold: threshold,
      results: results,
      total_results: results.length,
      total_documents: knowledgeBase.documents.length,
      executed: true
    };
  }

  async loadKnowledgeBase(kbId) {
    await new Promise(resolve => setTimeout(resolve, 30));

    // 模拟知识库
    const kbs = {
      'default_kb': {
        id: 'default_kb',
        name: '默认知识库',
        documents: [
          { id: 'doc_1', title: '产品介绍', content: '这是一个关于产品功能的详细介绍文档...', tags: ['product', 'intro'], source: 'manual' },
          { id: 'doc_2', title: '使用指南', content: '如何使用本产品的详细步骤和说明...', tags: ['guide', 'usage'], source: 'manual' },
          { id: 'doc_3', title: '常见问题', content: '用户常遇到的问题及解答汇总...', tags: ['faq', 'help'], source: 'auto' },
          { id: 'doc_4', title: 'API文档', content: '所有API接口的详细说明和示例代码...', tags: ['api', 'dev'], source: 'auto' },
          { id: 'doc_5', title: '更新日志', content: '版本更新记录和新功能说明...', tags: ['changelog', 'release'], source: 'auto' }
        ],
        embeddings: true
      }
    };

    return kbs[kbId] || {
      id: kbId,
      name: '知识库_' + kbId,
      documents: [
        { id: 'doc_' + kbId + '_1', title: '文档1', content: '示例文档内容...', tags: [], source: 'auto' },
        { id: 'doc_' + kbId + '_2', title: '文档2', content: '更多文档内容...', tags: [], source: 'auto' }
      ],
      embeddings: true
    };
  }

  async search(kb, query, options) {
    await new Promise(resolve => setTimeout(resolve, 50));

    const scored = [];

    for (const doc of kb.documents) {
      // 应用过滤器
      if (!this.matchFilters(doc, options.filters)) continue;

      let score = 0;

      switch (options.searchMode) {
        case 'semantic':
          score = this.semanticScore(query, doc);
          break;
        case 'keyword':
          score = this.keywordScore(query, doc);
          break;
        case 'hybrid':
          score = this.semanticScore(query, doc) * 0.6 + this.keywordScore(query, doc) * 0.4;
          break;
        default:
          score = this.semanticScore(query, doc);
      }

      scored.push({
        document: doc,
        score: score,
        matched: score >= options.threshold
      });
    }

    // 排序并取topK
    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, options.topK).map(item => ({
      id: item.document.id,
      title: item.document.title,
      content: item.document.content,
      score: item.score,
      tags: item.document.tags,
      source: item.document.source,
      metadata: {
        kb_id: kb.id,
        relevance: item.score.toFixed(4)
      }
    }));
  }

  matchFilters(doc, filters) {
    if (!filters || Object.keys(filters).length === 0) return true;
    for (const [key, value] of Object.entries(filters)) {
      if (key === 'tags') {
        if (!Array.isArray(value)) value = [value];
        if (!value.some(v => doc.tags && doc.tags.includes(v))) return false;
      } else if (key === 'source') {
        if (doc.source !== value) return false;
      } else if (doc[key] !== value) {
        return false;
      }
    }
    return true;
  }

  semanticScore(query, doc) {
    // 模拟语义相似度计算
    const queryWords = query.toLowerCase().split(/\s+/);
    const docText = (doc.title + ' ' + doc.content).toLowerCase();
    let matchCount = 0;
    for (const word of queryWords) {
      if (word.length > 1 && docText.includes(word)) matchCount++;
    }
    const baseScore = matchCount / Math.max(queryWords.length, 1);
    // 添加一些随机性模拟向量检索
    return Math.min(baseScore + 0.2 + Math.random() * 0.3, 1.0);
  }

  keywordScore(query, doc) {
    const queryWords = query.toLowerCase().split(/\s+/).filter(w => w.length > 0);
    const docText = (doc.title + ' ' + doc.content).toLowerCase();
    let score = 0;
    for (const word of queryWords) {
      if (docText.includes(word)) {
        score += 1 / queryWords.length;
      }
    }
    return score;
  }

  async attemptFix(error) {
    const strategies = this.config.autoFixStrategies || ['retry'];
    for (const strategy of strategies) {
      try {
        const result = await this.applyFix(strategy, error);
        if (result.success) return result;
      } catch (e) { continue; }
    }
    return null;
  }

  async applyFix(strategy, error) {
    if (strategy === 'retry') {
      // 使用hybrid搜索
      this.inputs.search_mode = 'hybrid';
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[kb_search] 自动修复成功(retry, hybrid模式)'] };
    }
    if (strategy === 'lower_threshold') {
      this.inputs.threshold = 0.1;
      this.inputs.topK = Math.max(this.inputs.topK || 5, 10);
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[kb_search] 自动修复成功(降低阈值)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('kb') || error.message.includes('知识库')) return 'KB_ERROR';
    if (error.message.includes('query') || error.message.includes('查询')) return 'QUERY_ERROR';
    if (error.message.includes('不存在') || error.message.includes('not found')) return 'NOT_FOUND';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('KBSearch处理器启动');
  const handlerInstance = new KBSearchHandler({
    inputs: input,
    name: 'kb_search',
    requiredInputs: ['query', 'kbId'],
    autoFixStrategies: ['retry', 'lower_threshold']
  });
  return await handlerInstance.execute();
}

module.exports = KBSearchHandler;
