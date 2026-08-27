/**
 * 变量赋值处理器
 * 将var_value赋值给var_name指定的变量，支持类型转换和条件赋值
 */

class VarAssignHandler {
  constructor(config) {
    this.config = config;
    this.inputs = config.inputs || {};
    this.outputs = {};
    this.variableStore = {};
  }

  async execute() {
    try {
      this.validateInputs();
      const result = await this.process();
      this.outputs.result = result;
      return { success: true, outputs: this.outputs, logs: ['[var_assign] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[var_assign] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['var_name', 'var_value'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.var_name !== 'string' || this.inputs.var_name.trim() === '') {
      throw new Error('参数 var_name 必须是非空字符串');
    }
    if (!/^[a-zA-Z_$][a-zA-Z0-9_$]*$/.test(this.inputs.var_name)) {
      throw new Error('参数 var_name 不是合法的变量名: ' + this.inputs.var_name);
    }
  }

  async process() {
    const varName = this.inputs.var_name;
    let varValue = this.inputs.var_value;
    const type = this.inputs.type || 'auto';
    const scope = this.inputs.scope || 'local';
    const overwrite = this.inputs.overwrite !== false;
    const condition = this.inputs.condition;

    // 检查条件
    if (condition !== undefined) {
      const shouldAssign = this.evaluateCondition(condition, varValue);
      if (!shouldAssign) {
        return {
          var_name: varName,
          assigned: false,
          reason: '条件不满足',
          current_value: this.variableStore[varName] || null,
          executed: true
        };
      }
    }

    // 检查是否已存在
    if (!overwrite && this.variableStore[varName] !== undefined) {
      return {
        var_name: varName,
        assigned: false,
        reason: '变量已存在且不允许覆盖',
        current_value: this.variableStore[varName],
        executed: true
      };
    }

    // 类型转换
    const convertedValue = this.convertType(varValue, type);

    // 存储变量
    this.variableStore[varName] = convertedValue;

    // 获取路径赋值
    const path = this.inputs.path;
    if (path) {
      this.setByPath(this.variableStore, varName, path, convertedValue);
    }

    return {
      var_name: varName,
      var_value: convertedValue,
      original_value: varValue,
      type: type,
      scope: scope,
      assigned: true,
      executed: true
    };
  }

  convertType(value, type) {
    if (type === 'auto' || type === undefined) {
      return value;
    }

    switch (type.toLowerCase()) {
      case 'string':
        return String(value);
      case 'number':
        const num = Number(value);
        if (isNaN(num)) throw new Error('无法将值转换为number类型: ' + value);
        return num;
      case 'integer':
      case 'int':
        const intVal = parseInt(value, 10);
        if (isNaN(intVal)) throw new Error('无法将值转换为integer类型: ' + value);
        return intVal;
      case 'float':
        const floatVal = parseFloat(value);
        if (isNaN(floatVal)) throw new Error('无法将值转换为float类型: ' + value);
        return floatVal;
      case 'boolean':
      case 'bool':
        if (typeof value === 'boolean') return value;
        if (typeof value === 'string') {
          return value === 'true' || value === '1' || value === 'yes';
        }
        return Boolean(value);
      case 'array':
        if (Array.isArray(value)) return value;
        if (typeof value === 'string') {
          try { return JSON.parse(value); } catch (e) { return value.split(','); }
        }
        return [value];
      case 'object':
        if (typeof value === 'object' && !Array.isArray(value)) return value;
        if (typeof value === 'string') {
          try { return JSON.parse(value); } catch (e) { return { value: value }; }
        }
        return { value: value };
      case 'json':
        if (typeof value === 'string') {
          try { return JSON.parse(value); } catch (e) { throw new Error('JSON类型转换失败: ' + e.message); }
        }
        return value;
      default:
        return value;
    }
  }

  evaluateCondition(condition, value) {
    if (typeof condition === 'boolean') return condition;
    if (typeof condition === 'function') return condition(value);
    if (typeof condition === 'string') {
      switch (condition) {
        case 'not_null': return value !== null && value !== undefined;
        case 'not_empty': return value !== null && value !== undefined && value !== '';
        case 'is_number': return typeof value === 'number' && !isNaN(value);
        case 'is_string': return typeof value === 'string';
        case 'is_positive': return typeof value === 'number' && value > 0;
        case 'is_negative': return typeof value === 'number' && value < 0;
        default: return true;
      }
    }
    return true;
  }

  setByPath(obj, varName, path, value) {
    const keys = path.split('.');
    let current = obj[varName] || {};
    for (let i = 0; i < keys.length - 1; i++) {
      if (!current[keys[i]]) current[keys[i]] = {};
      current = current[keys[i]];
    }
    current[keys[keys.length - 1]] = value;
    obj[varName] = obj[varName] || current;
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
      // 允许覆盖后重试
      this.inputs.overwrite = true;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[var_assign] 自动修复成功(retry, 允许覆盖)'] };
    }
    if (strategy === 'auto_type') {
      // 自动类型推断后重试
      this.inputs.type = 'auto';
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[var_assign] 自动修复成功(自动类型推断)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('变量') || error.message.includes('var')) return 'VARIABLE_ERROR';
    if (error.message.includes('类型') || error.message.includes('type')) return 'TYPE_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('VarAssign处理器启动');
  const handlerInstance = new VarAssignHandler({
    inputs: input,
    name: 'var_assign',
    requiredInputs: ['var_name', 'var_value'],
    autoFixStrategies: ['retry', 'auto_type']
  });
  return await handlerInstance.execute();
}

module.exports = VarAssignHandler;
