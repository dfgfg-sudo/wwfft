/**
 * JSON序列化处理器
 * 将data对象序列化为JSON字符串，支持格式化和过滤
 */

class JSONSerializeHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[json_serialize] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[json_serialize] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['data'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
  }

  async process() {
    const data = this.inputs.data;
    const pretty = this.inputs.pretty !== false;
    const indent = this.inputs.indent || 2;
    const filter = this.inputs.filter;
    const replacer = this.inputs.replacer;

    let dataToSerialize = data;

    // 应用过滤器
    if (filter) {
      if (Array.isArray(filter) && typeof data === 'object' && !Array.isArray(data)) {
        // 过滤指定字段
        const filtered = {};
        for (const key of filter) {
          if (data[key] !== undefined) {
            filtered[key] = data[key];
          }
        }
        dataToSerialize = filtered;
      } else if (typeof filter === 'function') {
        dataToSerialize = filter(data);
      }
    }

    // 检查循环引用
    this.checkCircular(dataToSerialize);

    // 序列化
    let jsonString;
    try {
      if (pretty) {
        jsonString = JSON.stringify(dataToSerialize, replacer, indent);
      } else {
        jsonString = JSON.stringify(dataToSerialize, replacer);
      }
    } catch (err) {
      throw new Error('JSON序列化失败: ' + err.message);
    }

    // 处理特殊类型（如Date、BigInt等）
    const sanitized = this.sanitizeForSerialization(dataToSerialize);
    let sanitizedJson;
    try {
      if (pretty) {
        sanitizedJson = JSON.stringify(sanitized, replacer, indent);
      } else {
        sanitizedJson = JSON.stringify(sanitized, replacer);
      }
    } catch (err) {
      sanitizedJson = jsonString;
    }

    return {
      json_string: sanitizedJson,
      original_type: Array.isArray(data) ? 'array' : typeof data,
      byte_length: Buffer.byteLength(sanitizedJson, 'utf-8'),
      char_length: sanitizedJson.length,
      key_count: typeof data === 'object' && !Array.isArray(data) ? Object.keys(data).length : (Array.isArray(data) ? data.length : 0),
      pretty: pretty,
      executed: true
    };
  }

  checkCircular(obj, seen) {
    seen = seen || new WeakSet();
    if (typeof obj !== 'object' || obj === null) return;

    if (seen.has(obj)) {
      throw new Error('检测到循环引用，无法序列化');
    }
    seen.add(obj);

    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        this.checkCircular(obj[key], seen);
      }
    }
  }

  sanitizeForSerialization(obj) {
    if (obj === null || obj === undefined) return obj;
    if (obj instanceof Date) return obj.toISOString();
    if (typeof obj === 'bigint') return obj.toString();
    if (typeof obj !== 'object') return obj;
    if (Array.isArray(obj)) {
      return obj.map(item => this.sanitizeForSerialization(item));
    }
    if (obj.toJSON && typeof obj.toJSON === 'function') {
      return obj.toJSON();
    }
    const result = {};
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'function' || typeof value === 'symbol') continue;
      result[key] = this.sanitizeForSerialization(value);
    }
    return result;
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
      return { success: true, outputs: { result }, logs: ['[json_serialize] 自动修复成功(retry)'] };
    }
    if (strategy === 'remove_circular') {
      // 移除循环引用后重试
      const sanitized = this.deepCloneSafe(this.inputs.data);
      this.inputs.data = sanitized;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[json_serialize] 自动修复成功(移除循环引用)'] };
    }
    return { success: false };
  }

  deepCloneSafe(obj, seen) {
    seen = seen || new Map();
    if (obj === null || typeof obj !== 'object') return obj;
    if (seen.has(obj)) return '[Circular]';
    seen.set(obj, true);
    if (Array.isArray(obj)) {
      return obj.map(item => this.deepCloneSafe(item, seen));
    }
    if (obj instanceof Date) return new Date(obj);
    const clone = {};
    for (const [key, value] of Object.entries(obj)) {
      clone[key] = this.deepCloneSafe(value, seen);
    }
    return clone;
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('循环') || error.message.includes('circular')) return 'CIRCULAR_REFERENCE';
    if (error.message.includes('序列化') || error.message.includes('serialize')) return 'SERIALIZATION_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('JSONSerialize处理器启动');
  const handlerInstance = new JSONSerializeHandler({
    inputs: input,
    name: 'json_serialize',
    requiredInputs: ['data'],
    autoFixStrategies: ['retry', 'remove_circular']
  });
  return await handlerInstance.execute();
}

module.exports = JSONSerializeHandler;
