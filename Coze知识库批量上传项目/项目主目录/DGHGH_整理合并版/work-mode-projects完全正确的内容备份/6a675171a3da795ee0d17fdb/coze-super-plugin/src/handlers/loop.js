/**
 * 循环节点处理器
 * 遍历数组中的每个元素，对每个元素执行loop_body逻辑
 */

class LoopHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[loop] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[loop] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['array'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (!Array.isArray(this.inputs.array)) {
      throw new Error('参数 array 必须是数组');
    }
  }

  async process() {
    const array = this.inputs.array;
    const loopBody = this.inputs.loop_body;
    const maxIterations = this.inputs.max_iterations || 1000;

    if (array.length > maxIterations) {
      throw new Error('数组长度超过最大迭代限制: ' + maxIterations);
    }

    const results = [];
    const errors = [];
    const index = this.inputs.start_index || 0;

    for (let i = index; i < array.length; i++) {
      const item = array[i];
      try {
        let itemResult;
        if (typeof loopBody === 'function') {
          itemResult = await loopBody(item, i, array);
        } else if (typeof loopBody === 'object' && loopBody !== null) {
          // 如果loop_body是配置对象，模拟执行
          itemResult = await this.executeLoopBody(item, i, array, loopBody);
        } else {
          // 默认行为：返回元素本身
          itemResult = { index: i, value: item, processed: true };
        }
        results.push({ index: i, success: true, result: itemResult });
      } catch (err) {
        errors.push({ index: i, error: err.message });
        if (this.inputs.break_on_error) {
          break;
        }
      }
    }

    return {
      total_items: array.length,
      processed: results.length,
      results: results,
      errors: errors,
      has_errors: errors.length > 0,
      executed: true
    };
  }

  async executeLoopBody(item, index, array, bodyConfig) {
    await new Promise(resolve => setTimeout(resolve, 5));

    const operation = bodyConfig.operation || 'identity';
    const field = bodyConfig.field || null;

    switch (operation) {
      case 'identity':
        return item;
      case 'extract':
        return field && item[field] !== undefined ? item[field] : null;
      case 'transform':
        if (field && item[field] !== undefined) {
          const transformed = { ...item };
          transformed[field] = String(item[field]).toUpperCase();
          return transformed;
        }
        return item;
      case 'filter':
        if (bodyConfig.condition) {
          const conditionFn = new Function('item', 'index', 'return ' + bodyConfig.condition);
          return conditionFn(item, index) ? item : null;
        }
        return item;
      case 'count':
        return 1;
      default:
        return { index: index, value: item, operation: operation };
    }
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
      // 跳过错误项后重试
      if (this.inputs.break_on_error) {
        this.inputs.break_on_error = false;
      }
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[loop] 自动修复成功(retry)'] };
    }
    if (strategy === 'increase_limit') {
      this.inputs.max_iterations = (this.inputs.max_iterations || 1000) * 10;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[loop] 自动修复成功(增加迭代限制)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('超过最大') || error.message.includes('limit')) return 'LIMIT_EXCEEDED';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('Loop处理器启动');
  const handlerInstance = new LoopHandler({
    inputs: input,
    name: 'loop',
    requiredInputs: ['array'],
    autoFixStrategies: ['retry', 'increase_limit']
  });
  return await handlerInstance.execute();
}

module.exports = LoopHandler;
