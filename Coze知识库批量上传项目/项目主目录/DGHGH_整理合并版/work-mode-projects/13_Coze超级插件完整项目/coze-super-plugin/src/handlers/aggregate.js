/**
 * 变量聚合处理器
 * 将多个variables聚合为一个统一的结构化输出
 */

class AggregateHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[aggregate] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[aggregate] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['variables'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.variables !== 'object' || Array.isArray(this.inputs.variables)) {
      throw new Error('参数 variables 必须是对象');
    }
  }

  async process() {
    const variables = this.inputs.variables;
    const strategy = this.inputs.strategy || 'merge';
    const prefix = this.inputs.prefix || '';
    const includeMetadata = this.inputs.include_metadata !== false;

    const aggregated = {};
    const metadata = {
      variable_count: 0,
      types: {},
      null_count: 0,
      undefined_count: 0
    };

    for (const [key, value] of Object.entries(variables)) {
      const targetKey = prefix ? prefix + '_' + key : key;

      if (value === undefined) {
        metadata.undefined_count++;
        continue;
      }
      if (value === null) {
        metadata.null_count++;
        aggregated[targetKey] = null;
        metadata.variable_count++;
        continue;
      }

      const type = Array.isArray(value) ? 'array' : typeof value;
      metadata.types[type] = (metadata.types[type] || 0) + 1;
      metadata.variable_count++;

      switch (strategy) {
        case 'merge':
          if (typeof value === 'object' && !Array.isArray(value)) {
            Object.assign(aggregated, this.flattenObject(value, targetKey));
          } else {
            aggregated[targetKey] = value;
          }
          break;
        case 'flat':
          if (typeof value === 'object' && !Array.isArray(value)) {
            const flat = this.flattenObject(value, targetKey);
            Object.assign(aggregated, flat);
          } else {
            aggregated[targetKey] = value;
          }
          break;
        case 'array':
          if (!aggregated._items) aggregated._items = [];
          aggregated._items.push({ key: targetKey, value: value });
          break;
        case 'first':
          if (!aggregated._first) {
            aggregated._first = { key: targetKey, value: value };
          }
          break;
        default:
          aggregated[targetKey] = value;
      }
    }

    const result = {
      aggregated: aggregated,
      strategy: strategy,
      count: metadata.variable_count
    };

    if (includeMetadata) {
      result.metadata = metadata;
    }

    result.executed = true;
    return result;
  }

  flattenObject(obj, prefix) {
    const result = {};
    for (const [key, value] of Object.entries(obj)) {
      const newKey = prefix ? prefix + '_' + key : key;
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        Object.assign(result, this.flattenObject(value, newKey));
      } else {
        result[newKey] = value;
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
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[aggregate] 自动修复成功(retry)'] };
    }
    if (strategy === 'default_strategy') {
      // 回退到简单的merge策略
      this.inputs.strategy = 'merge';
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[aggregate] 自动修复成功(使用默认merge策略)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('variables') || error.message.includes('变量')) return 'VARIABLE_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('Aggregate处理器启动');
  const handlerInstance = new AggregateHandler({
    inputs: input,
    name: 'aggregate',
    requiredInputs: ['variables'],
    autoFixStrategies: ['retry', 'default_strategy']
  });
  return await handlerInstance.execute();
}

module.exports = AggregateHandler;
