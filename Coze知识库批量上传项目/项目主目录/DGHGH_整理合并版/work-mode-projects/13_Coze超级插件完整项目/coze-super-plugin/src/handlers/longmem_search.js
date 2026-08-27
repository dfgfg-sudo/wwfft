/**
 * 长期记忆检索处理器
 * 在长期记忆存储中检索与query相关的内容，支持语义和关键词检索
 */

class LongMemSearchHandler {
  constructor(config) {
    this.config = config;
    this.inputs = config.inputs || {};
    this.outputs = {};
    this.memoryStore = [];
  }

  async execute() {
    try {
      this.validateInputs();
      const result = await this.process();
      this.outputs.result = result;
      return { success: true, outputs: this.outputs, logs: ['[longmem_search] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[longmem_search] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['query'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.query !== 'string' || this.inputs.query.trim() === '') {
      throw new Error('参数 query 不能为空字符串');
    }
  }

  async process() {
    const query = this.inputs.query;
    const topK = this.inputs.topK || 5;
    const threshold = this.inputs.threshold || 0.3;
    const searchMode = this.inputs.search_mode || 'hybrid';
    const userId = this.inputs.user_id;
    const sessionId = this.inputs.session_id;
    const tags = this.inputs.tags;
    const timeRange = this.inputs.time_range;
    const minImportance = this.inputs.min_importance || 0;

    // 加载记忆
    const memories = await this.loadMemories(userId, sessionId);

    // 应用过滤
    let filtered = this.applyFilters(memories, { userId, sessionId, tags, timeRange, minImportance });

    // 执行检索
    const results = await this.search(filtered, query, { topK, threshold, searchMode });

    // 更新访问计数
    for (const result of results) {
      result.access_count = (result.access_count || 0) + 1;
      result.last_accessed = new Date().toISOString();
    }

    return {
      query: query,
      search_mode: searchMode,
      top_k: topK,
      threshold: threshold,
      results: results,
      total_results: results.length,
      total_memories_searched: filtered.length,
      filters: { userId, sessionId, tags, timeRange, minImportance },
      executed: true
    };
  }

  async loadMemories(userId, sessionId) {
    await new Promise(resolve => setTimeout(resolve, 30));

    // 模拟记忆存储
    return [
      {
        id: 'mem_1',
        content: '用户喜欢使用Python编程，尤其擅长数据分析和机器学习。',
        summary: '用户编程偏好',
        keywords: [{ word: 'Python', count: 1 }, { word: '编程', count: 1 }],
        tags: ['preference', 'programming'],
        metadata: { user_id: 'default', importance: 0.8, created_at: '2026-07-20T10:00:00Z' },
        access_count: 3,
        last_accessed: '2026-07-25T14:00:00Z',
        embedding: { model: 'ada-002', dimensions: 1536, vector: [] }
      },
      {
        id: 'mem_2',
        content: '用户之前询问过关于数据库设计的问题，对关系型数据库有基础了解。',
        summary: '用户数据库知识背景',
        keywords: [{ word: '数据库', count: 2 }, { word: '设计', count: 1 }],
        tags: ['knowledge', 'database'],
        metadata: { user_id: 'default', importance: 0.6, created_at: '2026-07-22T15:00:00Z' },
        access_count: 1,
        last_accessed: '2026-07-22T15:30:00Z',
        embedding: { model: 'ada-002', dimensions: 1536, vector: [] }
      },
      {
        id: 'mem_3',
        content: '用户的工作是软件开发工程师，主要使用JavaScript和TypeScript。',
        summary: '用户职业信息',
        keywords: [{ word: '软件开发', count: 1 }, { word: 'JavaScript', count: 1 }],
        tags: ['profile', 'career'],
        metadata: { user_id: 'default', importance: 0.9, created_at: '2026-07-19T09:00:00Z' },
        access_count: 5,
        last_accessed: '2026-07-26T10:00:00Z',
        embedding: { model: 'ada-002', dimensions: 1536, vector: [] }
      }
    ];
  }

  applyFilters(memories, filters) {
    let filtered = [...memories];

    if (filters.userId) {
      filtered = filtered.filter(m => m.metadata.user_id === filters.userId);
    }
    if (filters.sessionId) {
      filtered = filtered.filter(m => m.metadata.session_id === filters.sessionId);
    }
    if (filters.tags && filters.tags.length > 0) {
      filtered = filtered.filter(m =>
        m.tags && filters.tags.some(t => m.tags.includes(t))
      );
    }
    if (filters.minImportance > 0) {
      filtered = filtered.filter(m => (m.metadata.importance || 0) >= filters.minImportance);
    }
    if (filters.timeRange) {
      const start = filters.timeRange.start ? new Date(filters.timeRange.start) : null;
      const end = filters.timeRange.end ? new Date(filters.timeRange.end) : null;
      filtered = filtered.filter(m => {
        const created = new Date(m.metadata.created_at);
        if (start && created < start) return false;
        if (end && created > end) return false;
        return true;
      });
    }

    return filtered;
  }

  async search(memories, query, options) {
    await new Promise(resolve => setTimeout(resolve, 40));

    const scored = [];

    for (const mem of memories) {
      let score = 0;

      switch (options.searchMode) {
        case 'semantic':
          score = this.semanticScore(query, mem);
          break;
        case 'keyword':
          score = this.keywordScore(query, mem);
          break;
        case 'hybrid':
        default:
          score = this.semanticScore(query, mem) * 0.6 + this.keywordScore(query, mem) * 0.4;
      }

      // 考虑重要性权重
      score = score * 0.7 + (mem.metadata.importance || 0.5) * 0.3;

      if (score >= options.threshold) {
        scored.push({
          ...mem,
          score: score,
          relevance: score.toFixed(4)
        });
      }
    }

    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, options.topK);
  }

  semanticScore(query, memory) {
    // 模拟语义相似度
    const queryWords = query.toLowerCase().split(/\s+/);
    const memText = (memory.content + ' ' + (memory.summary || '')).toLowerCase();
    let matches = 0;
    for (const word of queryWords) {
      if (word.length > 1 && memText.includes(word)) matches++;
    }
    return Math.min((matches / Math.max(queryWords.length, 1)) + 0.3, 1.0);
  }

  keywordScore(query, memory) {
    const queryWords = query.toLowerCase().split(/\s+/).filter(w => w.length > 0);
    const memText = (memory.content + ' ' + (memory.summary || '')).toLowerCase();
    let score = 0;
    for (const word of queryWords) {
      if (memText.includes(word)) score += 1 / queryWords.length;
    }
    // 检查关键词匹配
    if (memory.keywords) {
      for (const kw of memory.keywords) {
        if (query.toLowerCase().includes(kw.word.toLowerCase())) {
          score += 0.2;
        }
      }
    }
    return Math.min(score, 1.0);
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
      // 使用hybrid模式
      this.inputs.search_mode = 'hybrid';
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[longmem_search] 自动修复成功(retry, hybrid模式)'] };
    }
    if (strategy === 'lower_threshold') {
      this.inputs.threshold = 0.1;
      this.inputs.topK = Math.max(this.inputs.topK || 5, 10);
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[longmem_search] 自动修复成功(降低阈值)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('query') || error.message.includes('查询')) return 'QUERY_ERROR';
    if (error.message.includes('memory') || error.message.includes('记忆')) return 'MEMORY_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('LongMemSearch处理器启动');
  const handlerInstance = new LongMemSearchHandler({
    inputs: input,
    name: 'longmem_search',
    requiredInputs: ['query'],
    autoFixStrategies: ['retry', 'lower_threshold']
  });
  return await handlerInstance.execute();
}

module.exports = LongMemSearchHandler;
