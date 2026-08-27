/**
 * 插件节点处理器
 * 根据plugin_id调用指定的Coze插件，并将inputs传递给插件执行
 */

class PluginHandler {
  constructor(config) {
    this.config = config;
    this.inputs = config.inputs || {};
    this.outputs = {};
    this.pluginRegistry = {
      'web_search': this.webSearchPlugin.bind(this),
      'weather': this.weatherPlugin.bind(this),
      'calculator': this.calculatorPlugin.bind(this),
      'translator': this.translatorPlugin.bind(this)
    };
  }

  async execute() {
    try {
      this.validateInputs();
      const result = await this.process();
      this.outputs.result = result;
      return { success: true, outputs: this.outputs, logs: ['[plugin] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[plugin] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['plugin_id'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.plugin_id !== 'string' || this.inputs.plugin_id.trim() === '') {
      throw new Error('参数 plugin_id 必须是非空字符串');
    }
  }

  async process() {
    const pluginId = this.inputs.plugin_id;
    const pluginInputs = this.inputs.inputs || {};

    const pluginFn = this.pluginRegistry[pluginId];
    if (!pluginFn) {
      throw new Error('未找到插件: ' + pluginId);
    }

    const result = await pluginFn(pluginInputs);
    return {
      plugin_id: pluginId,
      output: result,
      executed: true
    };
  }

  async webSearchPlugin(params) {
    await new Promise(resolve => setTimeout(resolve, 30));
    const query = params.query || params.q || '';
    return {
      query: query,
      results: [
        { title: '搜索结果1: ' + query, url: 'https://example.com/1', snippet: '相关内容摘要...' },
        { title: '搜索结果2: ' + query, url: 'https://example.com/2', snippet: '相关内容摘要...' }
      ],
      total: 2
    };
  }

  async weatherPlugin(params) {
    await new Promise(resolve => setTimeout(resolve, 20));
    const city = params.city || params.location || '未知';
    return {
      city: city,
      temperature: 25,
      condition: '晴',
      humidity: 60,
      wind: '微风'
    };
  }

  async calculatorPlugin(params) {
    const expression = params.expression || params.expr || '0';
    try {
      const safeExpr = expression.replace(/[^0-9+\-*/().\s]/g, '');
      const result = eval(safeExpr);
      return { expression: expression, result: result };
    } catch (e) {
      return { expression: expression, result: null, error: '计算失败' };
    }
  }

  async translatorPlugin(params) {
    const text = params.text || '';
    const targetLang = params.target_lang || 'en';
    return {
      original: text,
      translated: '[翻译为' + targetLang + ']' + text,
      target_lang: targetLang
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
      return { success: true, outputs: { result }, logs: ['[plugin] 自动修复成功(retry)'] };
    }
    if (strategy === 'default_inputs') {
      if (!this.inputs.inputs) {
        this.inputs.inputs = {};
        const result = await this.process();
        return { success: true, outputs: { result }, logs: ['[plugin] 自动修复成功(使用默认inputs)'] };
      }
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('connection') || error.message.includes('ECONNREFUSED')) return 'CONNECTION_ERROR';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('未找到') || error.message.includes('not found')) return 'NOT_FOUND';
    if (error.message.includes('permission') || error.message.includes('权限')) return 'PERMISSION_DENIED';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('Plugin处理器启动');
  const handlerInstance = new PluginHandler({
    inputs: input,
    name: 'plugin',
    requiredInputs: ['plugin_id'],
    autoFixStrategies: ['retry', 'default_inputs']
  });
  return await handlerInstance.execute();
}

module.exports = PluginHandler;
