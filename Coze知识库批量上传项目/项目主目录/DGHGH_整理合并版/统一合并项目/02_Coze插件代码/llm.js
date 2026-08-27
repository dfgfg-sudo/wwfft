/**
 * 大模型节点处理器
 * 调用大语言模型API，根据给定的prompt、model、temperature和max_tokens生成回复
 */

class LLMHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[llm] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[llm] 执行失败: ' + error.message] };
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
    const model = this.inputs.model || 'gpt-3.5-turbo';
    const temperature = this.inputs.temperature !== undefined ? this.inputs.temperature : 0.7;
    const maxTokens = this.inputs.max_tokens || 2048;

    // 参数范围校验与自动修正
    const safeTemp = Math.max(0, Math.min(2, Number(temperature)));
    const safeMaxTokens = Math.max(1, Math.min(8192, Number(maxTokens)));

    // 模拟大模型调用（实际环境中替换为真实API调用）
    const llmResponse = await this.callLLM({
      prompt,
      model,
      temperature: safeTemp,
      max_tokens: safeMaxTokens
    });

    return {
      text: llmResponse.text,
      model: model,
      usage: {
        prompt_tokens: llmResponse.prompt_tokens,
        completion_tokens: llmResponse.completion_tokens,
        total_tokens: llmResponse.total_tokens
      },
      finish_reason: llmResponse.finish_reason
    };
  }

  async callLLM(params) {
    // 模拟API调用延迟
    await new Promise(resolve => setTimeout(resolve, 50));

    const estimatedPromptTokens = Math.ceil(params.prompt.length / 4);
    const generatedText = `[LLM(${params.model})] 基于提示词生成的回复内容。温度: ${params.temperature}`;
    const completionTokens = Math.ceil(generatedText.length / 4);

    return {
      text: generatedText,
      prompt_tokens: estimatedPromptTokens,
      completion_tokens: completionTokens,
      total_tokens: estimatedPromptTokens + completionTokens,
      finish_reason: 'stop'
    };
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
      return { success: true, outputs: { result }, logs: ['[llm] 自动修复成功(retry)'] };
    }
    if (strategy === 'truncate_prompt') {
      if (this.inputs.prompt && this.inputs.prompt.length > 4000) {
        this.inputs.prompt = this.inputs.prompt.substring(0, 4000);
        const result = await this.process();
        return { success: true, outputs: { result }, logs: ['[llm] 自动修复成功(截断prompt)'] };
      }
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('connection') || error.message.includes('ECONNREFUSED')) return 'CONNECTION_ERROR';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('permission') || error.message.includes('权限')) return 'PERMISSION_DENIED';
    if (error.message.includes('rate') || error.message.includes('quota')) return 'RATE_LIMIT';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('LLM处理器启动');
  const handlerInstance = new LLMHandler({
    inputs: input,
    name: 'llm',
    requiredInputs: ['prompt'],
    autoFixStrategies: ['retry', 'truncate_prompt']
  });
  return await handlerInstance.execute();
}

module.exports = LLMHandler;
