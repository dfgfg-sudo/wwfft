/**
 * JSON反序列化处理器
 * 将JSON字符串解析为JavaScript对象，支持容错和自动修复
 */

class JSONDeserializeHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[json_deserialize] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[json_deserialize] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['json_string'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.json_string !== 'string') {
      throw new Error('参数 json_string 必须是字符串');
    }
  }

  async process() {
    const jsonString = this.inputs.json_string;
    const reviver = this.inputs.reviver || null;
    const strict = this.inputs.strict !== false;

    let parsed;
    try {
      parsed = JSON.parse(jsonString, reviver);
    } catch (parseError) {
      if (strict) {
        throw new Error('JSON解析失败: ' + parseError.message);
      }
      // 非严格模式：尝试修复
      const fixedJson = this.attemptFixJSON(jsonString);
      try {
        parsed = JSON.parse(fixedJson, reviver);
      } catch (secondError) {
        throw new Error('JSON解析失败（修复后仍失败）: ' + secondError.message);
      }
    }

    // 转换特殊类型
    const converted = this.convertTypes(parsed);

    return {
      data: converted,
      original_length: jsonString.length,
      type: Array.isArray(converted) ? 'array' : typeof converted,
      key_count: typeof converted === 'object' && converted !== null && !Array.isArray(converted)
        ? Object.keys(converted).length
        : (Array.isArray(converted) ? converted.length : 0),
      executed: true
    };
  }

  attemptFixJSON(jsonString) {
    let fixed = jsonString;

    // 移除BOM
    fixed = fixed.replace(/^\uFEFF/, '');

    // 移除尾部逗号
    fixed = fixed.replace(/,\s*}/g, '}').replace(/,\s*\]/g, ']');

    // 修复单引号为双引号
    fixed = fixed.replace(/'/g, '"');

    // 修复未引用的键名
    fixed = fixed.replace(/([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)(\s*:)/g, '$1"$2"$3');

    // 移除注释
    fixed = fixed.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

    // 修复NaN和Infinity
    fixed = fixed.replace(/\bNaN\b/g, 'null').replace(/\bInfinity\b/g, 'null').replace(/\b-Infinity\b/g, 'null');

    // 修复undefined
    fixed = fixed.replace(/\bundefined\b/g, 'null');

    return fixed;
  }

  convertTypes(obj) {
    if (obj === null || obj === undefined) return obj;
    if (typeof obj === 'string') {
      // 检测ISO日期字符串
      const isoDateRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$/;
      if (isoDateRegex.test(obj)) {
        const date = new Date(obj);
        if (!isNaN(date.getTime())) return date;
      }
      return obj;
    }
    if (Array.isArray(obj)) {
      return obj.map(item => this.convertTypes(item));
    }
    if (typeof obj === 'object') {
      const result = {};
      for (const [key, value] of Object.entries(obj)) {
        result[key] = this.convertTypes(value);
      }
      return result;
    }
    return obj;
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
      // 非严格模式下重试
      this.inputs.strict = false;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[json_deserialize] 自动修复成功(retry, 非严格模式)'] };
    }
    if (strategy === 'trim_whitespace') {
      // 去除空白字符后重试
      this.inputs.json_string = this.inputs.json_string.trim();
      this.inputs.strict = false;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[json_deserialize] 自动修复成功(去除空白字符)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('解析') || error.message.includes('parse')) return 'PARSE_ERROR';
    if (error.message.includes('语法') || error.message.includes('syntax')) return 'SYNTAX_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('JSONDeserialize处理器启动');
  const handlerInstance = new JSONDeserializeHandler({
    inputs: input,
    name: 'json_deserialize',
    requiredInputs: ['json_string'],
    autoFixStrategies: ['retry', 'trim_whitespace']
  });
  return await handlerInstance.execute();
}

module.exports = JSONDeserializeHandler;
