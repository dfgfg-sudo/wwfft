/**
 * 意图识别处理器
 * 根据user_input与预定义的intents列表进行匹配，识别用户意图
 */

class IntentHandler {
  constructor(config) {
    this.config = config;
    this.inputs = config.inputs || {};
    this.outputs = {};
  }

  async execute() {
    try {
      this.validateInputs();
      const result = await this.process();
      this.outputs.result = result;
      return { success: true, outputs: this.outputs, logs: ['[intent] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[intent] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['user_input', 'intents'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.user_input !== 'string' || this.inputs.user_input.trim() === '') {
      throw new Error('参数 user_input 不能为空字符串');
    }
    if (!Array.isArray(this.inputs.intents)) {
      throw new Error('参数 intents 必须是数组');
    }
  }

  async process() {
    const userInput = this.inputs.user_input;
    const intents = this.inputs.intents;
    const threshold = this.inputs.threshold || 0.5;

    const scoredIntents = [];

    for (const intent of intents) {
      const score = this.calculateScore(userInput, intent);
      scoredIntents.push({
        intent: intent.name || intent.id || 'unknown',
        score: score,
        matched: score >= threshold,
        data: intent
      });
    }

    // 按分数排序
    scoredIntents.sort((a, b) => b.score - a.score);

    const topIntent = scoredIntents.length > 0 ? scoredIntents[0] : null;
    const matchedIntents = scoredIntents.filter(i => i.matched);

    return {
      user_input: userInput,
      top_intent: topIntent ? topIntent.intent : null,
      top_score: topIntent ? topIntent.score : 0,
      matched_intents: matchedIntents.map(i => i.intent),
      all_scores: scoredIntents.map(i => ({ intent: i.intent, score: i.score })),
      confidence: topIntent ? topIntent.score : 0,
      executed: true
    };
  }

  calculateScore(input, intent) {
    const intentName = (intent.name || intent.id || '').toLowerCase();
    const keywords = intent.keywords || intent.samples || [];
    const inputLower = input.toLowerCase();

    let score = 0;
    let totalChecks = 0;

    // 检查意图名称是否出现在输入中
    if (intentName && inputLower.includes(intentName)) {
      score += 0.4;
    }
    totalChecks++;

    // 检查关键词匹配
    if (Array.isArray(keywords)) {
      for (const keyword of keywords) {
        const kwLower = String(keyword).toLowerCase();
        if (inputLower.includes(kwLower)) {
          score += 0.3 / keywords.length;
        }
      }
    }
    totalChecks++;

    // 检查正则匹配
    if (intent.pattern) {
      try {
        const regex = new RegExp(intent.pattern, 'i');
        if (regex.test(input)) {
          score += 0.3;
        }
      } catch (e) {
        // 忽略无效正则
      }
    }
    totalChecks++;

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
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[intent] 自动修复成功(retry)'] };
    }
    if (strategy === 'lower_threshold') {
      // 降低匹配阈值后重试
      this.inputs.threshold = 0.2;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[intent] 自动修复成功(降低阈值)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('intents') || error.message.includes('意图')) return 'INTENT_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('Intent处理器启动');
  const handlerInstance = new IntentHandler({
    inputs: input,
    name: 'intent',
    requiredInputs: ['user_input', 'intents'],
    autoFixStrategies: ['retry', 'lower_threshold']
  });
  return await handlerInstance.execute();
}

module.exports = IntentHandler;
