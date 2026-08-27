/**
 * 输入处理器
 * 解析和验证输入参数，支持多种数据来源和格式转换
 */

class InputHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[input] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[input] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['params'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
  }

  async process() {
    const params = this.inputs.params;
    const schema = this.inputs.schema;
    const source = this.inputs.source || 'direct';
    const parseMode = this.inputs.parse_mode || 'auto';
    const strict = this.inputs.strict !== false;

    let parsedParams = params;

    // 根据来源解析
    switch (source) {
      case 'query_string':
      case 'query':
        parsedParams = this.parseQueryString(params);
        break;
      case 'json':
        parsedParams = this.parseJSON(params, parseMode);
        break;
      case 'form':
      case 'form_data':
        parsedParams = this.parseFormData(params);
        break;
      case 'headers':
        parsedParams = this.parseHeaders(params);
        break;
      case 'path':
        parsedParams = this.parsePath(params, this.inputs.path_pattern);
        break;
      case 'direct':
      default:
        // 直接使用传入参数
        if (typeof params === 'string') {
          parsedParams = this.parseJSON(params, parseMode);
        }
        break;
    }

    // Schema验证
    let validationResult = { valid: true, errors: [], warnings: [] };
    if (schema) {
      validationResult = this.validateSchema(parsedParams, schema, strict);
      if (!validationResult.valid && strict) {
        throw new Error('参数验证失败: ' + validationResult.errors.join('; '));
      }
    }

    // 类型转换
    if (schema) {
      parsedParams = this.applySchemaTypes(parsedParams, schema);
    }

    // 设置默认值
    if (schema) {
      parsedParams = this.applyDefaults(parsedParams, schema);
    }

    return {
      source: source,
      parsed_params: parsedParams,
      param_count: typeof parsedParams === 'object' ? Object.keys(parsedParams).length : 1,
      validation: validationResult,
      schema_applied: !!schema,
      executed: true
    };
  }

  parseQueryString(qs) {
    if (typeof qs !== 'string') return qs;
    const params = {};
    const pairs = qs.replace(/^\?/, '').split('&');
    for (const pair of pairs) {
      const [key, value] = pair.split('=');
      if (key) {
        const decodedKey = decodeURIComponent(key);
        const decodedValue = value !== undefined ? decodeURIComponent(value.replace(/\+/g, ' ')) : '';
        // 处理数组参数
        if (decodedKey.endsWith('[]')) {
          const arrKey = decodedKey.slice(0, -2);
          if (!params[arrKey]) params[arrKey] = [];
          params[arrKey].push(decodedValue);
        } else {
          params[decodedKey] = decodedValue;
        }
      }
    }
    return params;
  }

  parseJSON(data, mode) {
    if (typeof data !== 'string') return data;
    if (mode === 'auto') {
      try {
        return JSON.parse(data);
      } catch (e) {
        // 尝试解析为查询字符串
        return this.parseQueryString(data);
      }
    }
    try {
      return JSON.parse(data);
    } catch (e) {
      if (mode === 'lenient') {
        return { raw: data };
      }
      throw new Error('JSON解析失败: ' + e.message);
    }
  }

  parseFormData(data) {
    if (typeof data !== 'string') return data;
    return this.parseQueryString(data);
  }

  parseHeaders(headers) {
    if (typeof headers !== 'object') return headers;
    const parsed = {};
    for (const [key, value] of Object.entries(headers)) {
      const normalizedKey = key.toLowerCase().replace(/-/g, '_');
      parsed[normalizedKey] = value;
    }
    return parsed;
  }

  parsePath(path, pattern) {
    if (!pattern || typeof path !== 'string') return { path };
    const paramNames = pattern.match(/:(\w+)/g) || [];
    const names = paramNames.map(n => n.slice(1));
    const regexPattern = pattern.replace(/:(\w+)/g, '([^/]+)');
    const regex = new RegExp('^' + regexPattern + '$');
    const match = path.match(regex);
    if (!match) return { path, matched: false };
    const params = {};
    names.forEach((name, i) => {
      params[name] = match[i + 1];
    });
    return { path, matched: true, params };
  }

  validateSchema(data, schema, strict) {
    const result = { valid: true, errors: [], warnings: [] };

    if (!schema.properties) return result;

    const requiredFields = schema.required || [];

    // 检查必填字段
    for (const field of requiredFields) {
      if (data[field] === undefined || data[field] === null) {
        result.errors.push('缺少必填字段: ' + field);
        result.valid = false;
      }
    }

    // 检查字段类型
    for (const [field, value] of Object.entries(data)) {
      const fieldSchema = schema.properties[field];
      if (!fieldSchema) {
        if (strict) {
          result.errors.push('未定义的字段: ' + field);
          result.valid = false;
        } else {
          result.warnings.push('未定义的字段: ' + field);
        }
        continue;
      }

      if (fieldSchema.type) {
        const typeValid = this.checkType(value, fieldSchema.type);
        if (!typeValid) {
          result.errors.push(`字段 ${field} 类型不匹配，期望 ${fieldSchema.type}`);
          result.valid = false;
        }
      }

      // 检查枚举值
      if (fieldSchema.enum && !fieldSchema.enum.includes(value)) {
        result.errors.push(`字段 ${field} 值不在允许范围内`);
        result.valid = false;
      }

      // 检查范围
      if (typeof value === 'number') {
        if (fieldSchema.minimum !== undefined && value < fieldSchema.minimum) {
          result.errors.push(`字段 ${field} 值小于最小值 ${fieldSchema.minimum}`);
          result.valid = false;
        }
        if (fieldSchema.maximum !== undefined && value > fieldSchema.maximum) {
          result.errors.push(`字段 ${field} 值大于最大值 ${fieldSchema.maximum}`);
          result.valid = false;
        }
      }

      // 检查字符串长度
      if (typeof value === 'string') {
        if (fieldSchema.minLength !== undefined && value.length < fieldSchema.minLength) {
          result.errors.push(`字段 ${field} 长度小于最小长度 ${fieldSchema.minLength}`);
          result.valid = false;
        }
        if (fieldSchema.maxLength !== undefined && value.length > fieldSchema.maxLength) {
          result.errors.push(`字段 ${field} 长度超过最大长度 ${fieldSchema.maxLength}`);
          result.valid = false;
        }
      }
    }

    return result;
  }

  checkType(value, type) {
    switch (type) {
      case 'string': return typeof value === 'string';
      case 'number': return typeof value === 'number' && !isNaN(value);
      case 'integer': return typeof value === 'number' && Number.isInteger(value);
      case 'boolean': return typeof value === 'boolean';
      case 'array': return Array.isArray(value);
      case 'object': return typeof value === 'object' && !Array.isArray(value) && value !== null;
      default: return true;
    }
  }

  applySchemaTypes(data, schema) {
    if (!schema.properties) return data;
    const result = { ...data };
    for (const [field, fieldSchema] of Object.entries(schema.properties)) {
      if (result[field] !== undefined && fieldSchema.type) {
        result[field] = this.convertType(result[field], fieldSchema.type);
      }
    }
    return result;
  }

  convertType(value, type) {
    switch (type) {
      case 'string': return String(value);
      case 'number': return Number(value);
      case 'integer': return parseInt(value, 10);
      case 'boolean':
        if (typeof value === 'boolean') return value;
        return value === 'true' || value === '1' || value === 1;
      default: return value;
    }
  }

  applyDefaults(data, schema) {
    if (!schema.properties) return data;
    const result = { ...data };
    for (const [field, fieldSchema] of Object.entries(schema.properties)) {
      if (result[field] === undefined && fieldSchema.default !== undefined) {
        result[field] = fieldSchema.default;
      }
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
      // 非严格模式重试
      this.inputs.strict = false;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[input] 自动修复成功(retry, 非严格模式)'] };
    }
    if (strategy === 'auto_parse') {
      // 自动解析模式
      this.inputs.parse_mode = 'auto';
      this.inputs.strict = false;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[input] 自动修复成功(自动解析模式)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('schema') || error.message.includes('验证')) return 'VALIDATION_ERROR';
    if (error.message.includes('parse') || error.message.includes('解析')) return 'PARSE_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('Input处理器启动');
  const handlerInstance = new InputHandler({
    inputs: input,
    name: 'input',
    requiredInputs: ['params'],
    autoFixStrategies: ['retry', 'auto_parse']
  });
  return await handlerInstance.execute();
}

module.exports = InputHandler;
