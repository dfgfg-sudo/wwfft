/**
 * 提示词优化处理器
 * 对输入的prompt进行优化，支持多种优化类型
 */

class PromptOptHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[prompt_opt] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[prompt_opt] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['prompt'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.prompt !== 'string' || this.inputs.prompt.trim() === '') {
      throw new Error('参数 prompt 不能为空字符串');
    }
  }

  async process() {
    const prompt = this.inputs.prompt;
    const optimizeType = this.inputs.optimize_type || 'general';
    const language = this.inputs.language || 'zh';
    const max_length = this.inputs.max_length || 2000;

    let optimizedPrompt = prompt;
    const optimizations = [];

    switch (optimizeType) {
      case 'general':
        optimizedPrompt = this.optimizeGeneral(prompt, language);
        optimizations.push('结构化', '添加上下文', '明确角色');
        break;
      case 'concise':
        optimizedPrompt = this.optimizeConcise(prompt, max_length);
        optimizations.push('精简', '去除冗余');
        break;
      case 'detailed':
        optimizedPrompt = this.optimizeDetailed(prompt, language);
        optimizations.push('增加细节', '添加示例', '明确约束');
        break;
      case 'chain_of_thought':
      case 'cot':
        optimizedPrompt = this.optimizeChainOfThought(prompt, language);
        optimizations.push('思维链', '逐步推理');
        break;
      case 'role_play':
        optimizedPrompt = this.optimizeRolePlay(prompt, language);
        optimizations.push('角色扮演', '设定角色');
        break;
      case 'few_shot':
        optimizedPrompt = this.optimizeFewShot(prompt, language);
        optimizations.push('少样本学习', '添加示例');
        break;
      case 'structured':
        optimizedPrompt = this.optimizeStructured(prompt, language);
        optimizations.push('结构化输出', '格式规范');
        break;
      case 'safety':
        optimizedPrompt = this.optimizeSafety(prompt, language);
        optimizations.push('安全约束', '边界限制');
        break;
      default:
        optimizedPrompt = this.optimizeGeneral(prompt, language);
        optimizations.push('通用优化');
    }

    // 截断处理
    if (optimizedPrompt.length > max_length) {
      optimizedPrompt = optimizedPrompt.substring(0, max_length - 3) + '...';
      optimizations.push('长度截断');
    }

    return {
      original_prompt: prompt,
      optimized_prompt: optimizedPrompt,
      optimize_type: optimizeType,
      language: language,
      optimizations: optimizations,
      original_length: prompt.length,
      optimized_length: optimizedPrompt.length,
      improvement_ratio: optimizedPrompt.length > 0 ? (optimizedPrompt.length / prompt.length).toFixed(2) : '0',
      executed: true
    };
  }

  optimizeGeneral(prompt, language) {
    const prefix = language === 'zh' ? '# 角色设定\n你是一个专业的AI助手。\n\n# 任务描述\n' : '# Role\nYou are a professional AI assistant.\n\n# Task\n';
    const suffix = language === 'zh' ? '\n\n# 输出要求\n请提供清晰、准确、结构化的回答。' : '\n\n# Output Requirements\nPlease provide clear, accurate, and structured responses.';
    return prefix + prompt.trim() + suffix;
  }

  optimizeConcise(prompt, maxLength) {
    // 移除多余空白和重复
    let concise = prompt.replace(/\s+/g, ' ').trim();
    // 移除常见冗余词
    const redundantPhrases = ['请帮我', '请帮我', '能不能', '可以的话', '如果可以的话', '麻烦'];
    for (const phrase of redundantPhrases) {
      concise = concise.replace(new RegExp(phrase, 'g'), '');
    }
    return concise.trim();
  }

  optimizeDetailed(prompt, language) {
    const sections = language === 'zh'
      ? ['# 任务背景', '# 具体要求', '# 输入内容', '# 输出格式', '# 注意事项']
      : ['# Background', '# Requirements', '# Input', '# Output Format', '# Notes'];

    let detailed = this.optimizeGeneral(prompt, language);
    detailed += '\n\n';
    for (const section of sections) {
      detailed += section + '\n[请在此补充内容]\n\n';
    }
    return detailed;
  }

  optimizeChainOfThought(prompt, language) {
    const cotPrefix = language === 'zh'
      ? '# 思维链推理\n请按照以下步骤逐步分析和推理：\n\n'
      : '# Chain of Thought\nPlease analyze and reason step by step:\n\n';
    const steps = language === 'zh'
      ? ['1. 理解问题：分析问题的核心要素', '2. 收集信息：识别相关的背景知识', '3. 推理分析：逐步推导得出结论', '4. 验证结论：检查推理的合理性', '5. 输出结果：提供最终答案']
      : ['1. Understand: Analyze core elements of the problem', '2. Gather: Identify relevant background knowledge', '3. Reason: Step-by-step derivation', '4. Verify: Check reasoning validity', '5. Output: Provide final answer'];

    return cotPrefix + steps.join('\n') + '\n\n# 问题\n' + prompt.trim();
  }

  optimizeRolePlay(prompt, language) {
    const rolePrefix = language === 'zh'
      ? '# 角色设定\n你现在是一位资深的领域专家，拥有丰富的经验和专业知识。\n\n# 交互规则\n- 始终以专家的身份回答\n- 使用专业但易懂的语言\n- 提供有深度的见解\n\n# 用户问题\n'
      : '# Role\nYou are now a senior domain expert with extensive experience and expertise.\n\n# Rules\n- Always respond as an expert\n- Use professional but accessible language\n- Provide in-depth insights\n\n# User Question\n';
    return rolePrefix + prompt.trim();
  }

  optimizeFewShot(prompt, language) {
    const fewShotPrefix = language === 'zh'
      ? '# 少样本示例\n以下是几个示例，请参考这些示例的模式来回答：\n\n## 示例1\n输入：示例输入\n输出：示例输出\n\n## 示例2\n输入：示例输入\n输出：示例输出\n\n# 实际任务\n'
      : '# Few-shot Examples\nHere are some examples to guide your response:\n\n## Example 1\nInput: example input\nOutput: example output\n\n## Example 2\nInput: example input\nOutput: example output\n\n# Actual Task\n';
    return fewShotPrefix + prompt.trim();
  }

  optimizeStructured(prompt, language) {
    const structPrefix = language === 'zh'
      ? '# 结构化输出要求\n请按照以下格式输出结果：\n\n```\n{\n  "summary": "简要总结",\n  "details": "详细说明",\n  "suggestions": ["建议1", "建议2"],\n  "confidence": 0.95\n}\n```\n\n# 输入内容\n'
      : '# Structured Output\nPlease output in the following format:\n\n```\n{\n  "summary": "brief summary",\n  "details": "detailed explanation",\n  "suggestions": ["suggestion1", "suggestion2"],\n  "confidence": 0.95\n}\n```\n\n# Input\n';
    return structPrefix + prompt.trim();
  }

  optimizeSafety(prompt, language) {
    const safetyPrefix = language === 'zh'
      ? '# 安全约束\n- 不输出有害、歧视性或不当内容\n- 保护用户隐私，不收集敏感信息\n- 遇到不确定的问题时明确说明\n- 遵守法律法规和道德准则\n\n# 任务\n'
      : '# Safety Constraints\n- Do not output harmful, discriminatory, or inappropriate content\n- Protect user privacy, do not collect sensitive information\n- Clearly state when uncertain\n- Comply with laws, regulations, and ethical standards\n\n# Task\n';
    return safetyPrefix + prompt.trim();
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
      // 使用默认优化类型
      this.inputs.optimize_type = 'general';
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[prompt_opt] 自动修复成功(retry, 使用general优化)'] };
    }
    if (strategy === 'increase_length') {
      // 增加最大长度限制
      this.inputs.max_length = 4000;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[prompt_opt] 自动修复成功(增加长度限制)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('prompt') || error.message.includes('提示词')) return 'PROMPT_ERROR';
    if (error.message.includes('type') || error.message.includes('类型')) return 'TYPE_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('PromptOpt处理器启动');
  const handlerInstance = new PromptOptHandler({
    inputs: input,
    name: 'prompt_opt',
    requiredInputs: ['prompt'],
    autoFixStrategies: ['retry', 'increase_length']
  });
  return await handlerInstance.execute();
}

module.exports = PromptOptHandler;
