/**
 * 问答处理器
 * 根据question在answer知识库中匹配最佳答案，支持模糊匹配和相似度计算
 */

class QAHandler {
  constructor(config) {
    this.config = config;
    this.inputs = config.inputs || {};
    this.outputs = {};
    this.qaStore = [];
  }

  async execute() {
    try {
      this.validateInputs();
      const result = await this.process();
      this.outputs.result = result;
      return { success: true, outputs: this.outputs, logs: ['[qa] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[qa] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['question'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.question !== 'string' || this.inputs.question.trim() === '') {
      throw new Error('参数 question 不能为空字符串');
    }
  }

  async process() {
    const question = this.inputs.question;
    const answer = this.inputs.answer;
    const qaPairs = this.inputs.qa_pairs || this.inputs.faqs || [];
    const threshold = this.inputs.threshold || 0.6;
    const topK = this.inputs.top_k || 1;
    const matchMode = this.inputs.match_mode || 'fuzzy';

    // 如果直接提供了answer，直接返回
    if (answer !== undefined && answer !== null) {
      return {
        question: question,
        answer: answer,
        source: 'direct',
        confidence: 1.0,
        matched: true,
        executed: true
      };
    }

    // 在QA对中匹配
    if (!Array.isArray(qaPairs) || qaPairs.length === 0) {
      return {
        question: question,
        answer: null,
        source: 'none',
        confidence: 0,
        matched: false,
        reason: '没有可用的QA知识库',
        executed: true
      };
    }

    // 计算相似度
    const scoredResults = [];
    for (const qa of qaPairs) {
      const qaQuestion = qa.question || qa.q || '';
      const qaAnswer = qa.answer || qa.a || '';
      let score = 0;

      switch (matchMode) {
        case 'exact':
          score = qaQuestion === question ? 1.0 : 0;
          break;
        case 'contains':
          score = question.includes(qaQuestion) || qaQuestion.includes(question) ? 0.8 : 0;
          break;
        case 'fuzzy':
        default:
          score = this.calculateSimilarity(question, qaQuestion);
          break;
      }

      scoredResults.push({
        question: qaQuestion,
        answer: qaAnswer,
        score: score,
        matched: score >= threshold,
        metadata: qa.metadata || {}
      });
    }

    // 排序并取topK
    scoredResults.sort((a, b) => b.score - a.score);
    const topResults = scoredResults.slice(0, topK);
    const bestMatch = topResults[0];

    return {
      question: question,
      answer: bestMatch && bestMatch.matched ? bestMatch.answer : null,
      best_score: bestMatch ? bestMatch.score : 0,
      confidence: bestMatch ? bestMatch.score : 0,
      matched: bestMatch ? bestMatch.matched : false,
      source: bestMatch && bestMatch.matched ? 'qa_store' : 'none',
      top_results: topResults,
      total_candidates: qaPairs.length,
      match_mode: matchMode,
      threshold: threshold,
      executed: true
    };
  }

  calculateSimilarity(str1, str2) {
    if (!str1 || !str2) return 0;
    if (str1 === str2) return 1;

    const s1 = str1.toLowerCase().trim();
    const s2 = str2.toLowerCase().trim();

    // Jaccard相似度（基于字符集）
    const set1 = new Set(s1.split(/\s+/));
    const set2 = new Set(s2.split(/\s+/));
    const intersection = new Set([...set1].filter(x => set2.has(x)));
    const union = new Set([...set1, ...set2]);
    const jaccardScore = union.size > 0 ? intersection.size / union.size : 0;

    // 编辑距离相似度
    const editDistance = this.levenshteinDistance(s1, s2);
    const maxLen = Math.max(s1.length, s2.length);
    const editScore = maxLen > 0 ? 1 - (editDistance / maxLen) : 0;

    // 关键词匹配得分
    const words1 = s1.split(/\s+/);
    const words2 = s2.split(/\s+/);
    let keywordMatches = 0;
    for (const w of words1) {
      if (w.length > 1 && s2.includes(w)) keywordMatches++;
    }
    const keywordScore = words1.length > 0 ? keywordMatches / words1.length : 0;

    // 综合得分
    return (jaccardScore * 0.3 + editScore * 0.4 + keywordScore * 0.3);
  }

  levenshteinDistance(s1, s2) {
    const matrix = [];
    for (let i = 0; i <= s2.length; i++) {
      matrix[i] = [i];
    }
    for (let j = 0; j <= s1.length; j++) {
      matrix[0][j] = j;
    }
    for (let i = 1; i <= s2.length; i++) {
      for (let j = 1; j <= s1.length; j++) {
        if (s2.charAt(i - 1) === s1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }
    return matrix[s2.length][s1.length];
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
      // 使用模糊匹配模式
      this.inputs.match_mode = 'fuzzy';
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[qa] 自动修复成功(retry, 模糊匹配)'] };
    }
    if (strategy === 'lower_threshold') {
      this.inputs.threshold = 0.3;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[qa] 自动修复成功(降低阈值)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('question') || error.message.includes('问题')) return 'QUESTION_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('QA处理器启动');
  const handlerInstance = new QAHandler({
    inputs: input,
    name: 'qa',
    requiredInputs: ['question'],
    autoFixStrategies: ['retry', 'lower_threshold']
  });
  return await handlerInstance.execute();
}

module.exports = QAHandler;
