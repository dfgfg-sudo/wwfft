/**
 * 长期记忆写入处理器
 * 将内容和元数据写入长期记忆存储，支持自动摘要和向量化
 */

class LongMemWriteHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[longmem_write] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[longmem_write] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['content'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.content !== 'string' || this.inputs.content.trim() === '') {
      throw new Error('参数 content 不能为空字符串');
    }
  }

  async process() {
    const content = this.inputs.content;
    const metadata = this.inputs.metadata || {};
    const autoSummarize = this.inputs.auto_summarize !== false;
    const autoEmbed = this.inputs.auto_embed !== false;
    const tags = this.inputs.tags || [];
    const importance = this.inputs.importance || 0.5;
    const userId = this.inputs.user_id || 'default';
    const sessionId = this.inputs.session_id;

    // 验证内容长度
    if (content.length > 50000) {
      throw new Error('内容过长，最大50000字符');
    }

    // 生成记忆ID
    const memoryId = 'mem_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

    // 自动摘要
    let summary = null;
    if (autoSummarize && content.length > 200) {
      summary = await this.generateSummary(content);
    }

    // 生成向量
    let embedding = null;
    if (autoEmbed) {
      embedding = await this.generateEmbedding(content);
    }

    // 提取关键词
    const keywords = this.extractKeywords(content);

    // 创建记忆条目
    const memoryEntry = {
      id: memoryId,
      content: content,
      summary: summary,
      keywords: keywords,
      tags: tags,
      metadata: {
        ...metadata,
        user_id: userId,
        session_id: sessionId,
        importance: Math.max(0, Math.min(1, importance)),
        content_length: content.length,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      embedding: embedding ? {
        model: embedding.model,
        dimensions: embedding.dimensions,
        vector: embedding.vector
      } : null,
      access_count: 0,
      last_accessed: null
    };

    // 写入存储
    this.memoryStore.push(memoryEntry);

    return {
      memory_id: memoryId,
      stored: true,
      summary: summary,
      keywords: keywords,
      tags: tags,
      metadata: memoryEntry.metadata,
      embedding_generated: autoEmbed,
      summary_generated: autoSummarize && summary !== null,
      store_size: this.memoryStore.length,
      executed: true
    };
  }

  async generateSummary(content) {
    await new Promise(resolve => setTimeout(resolve, 30));
    // 模拟摘要生成
    const sentences = content.split(/[。.!\n]/).filter(s => s.trim().length > 0);
    if (sentences.length <= 2) return content.substring(0, 200);
    return sentences.slice(0, 3).join('. ') + '.';
  }

  async generateEmbedding(content) {
    await new Promise(resolve => setTimeout(resolve, 40));
    // 模拟向量化
    return {
      model: 'text-embedding-ada-002',
      dimensions: 1536,
      vector: new Array(1536).fill(0).map(() => Math.random() * 2 - 1)
    };
  }

  extractKeywords(content) {
    // 简单关键词提取
    const stopWords = new Set(['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '上', '也', '很', '到', '说', '要', '去', '你', '会', 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they']);
    const words = content.split(/[\s,，。.!！?？;；:：""''()（）\[\]【】]+/)
      .filter(w => w.length > 1 && !stopWords.has(w.toLowerCase()));
    const freq = {};
    for (const word of words) {
      freq[word] = (freq[word] || 0) + 1;
    }
    return Object.entries(freq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([word, count]) => ({ word, count }));
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
      // 禁用摘要和向量化
      this.inputs.auto_summarize = false;
      this.inputs.auto_embed = false;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[longmem_write] 自动修复成功(retry, 禁用摘要和向量化)'] };
    }
    if (strategy === 'truncate_content') {
      // 截断内容
      if (this.inputs.content.length > 50000) {
        this.inputs.content = this.inputs.content.substring(0, 50000);
      }
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[longmem_write] 自动修复成功(截断内容)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('content') || error.message.includes('内容')) return 'CONTENT_ERROR';
    if (error.message.includes('memory') || error.message.includes('记忆')) return 'MEMORY_ERROR';
    if (error.message.includes('storage') || error.message.includes('存储')) return 'STORAGE_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('LongMemWrite处理器启动');
  const handlerInstance = new LongMemWriteHandler({
    inputs: input,
    name: 'longmem_write',
    requiredInputs: ['content'],
    autoFixStrategies: ['retry', 'truncate_content']
  });
  return await handlerInstance.execute();
}

module.exports = LongMemWriteHandler;
