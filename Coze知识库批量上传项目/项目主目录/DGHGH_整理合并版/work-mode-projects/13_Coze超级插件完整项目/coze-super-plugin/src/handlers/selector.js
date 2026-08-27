/**
 * 选择器节点处理器
 * 根据条件评估结果选择执行true_branch或false_branch
 */

class SelectorHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[selector] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[selector] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['condition'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.condition !== 'string' && typeof this.inputs.condition !== 'boolean') {
      throw new Error('参数 condition 必须是字符串或布尔值');
    }
  }

  async process() {
    const condition = this.inputs.condition;
    const trueBranch = this.inputs.true_branch;
    const falseBranch = this.inputs.false_branch;

    // 评估条件
    const conditionResult = this.evaluateCondition(condition);

    // 选择分支
    const selectedBranch = conditionResult ? trueBranch : falseBranch;
    const branchName = conditionResult ? 'true_branch' : 'false_branch';

    // 执行分支（如果有）
    let branchResult = null;
    if (selectedBranch !== undefined && selectedBranch !== null) {
      if (typeof selectedBranch === 'function') {
        branchResult = await selectedBranch();
      } else if (typeof selectedBranch === 'object' && selectedBranch.handler) {
        branchResult = selectedBranch;
      } else {
        branchResult = selectedBranch;
      }
    }

    return {
      condition: condition,
      condition_result: conditionResult,
      selected_branch: branchName,
      branch_output: branchResult,
      executed: true
    };
  }

  evaluateCondition(condition) {
    if (typeof condition === 'boolean') {
      return condition;
    }

    if (typeof condition === 'string') {
      const trimmed = condition.trim().toLowerCase();

      // 布尔字符串
      if (trimmed === 'true' || trimmed === '1' || trimmed === 'yes') return true;
      if (trimmed === 'false' || trimmed === '0' || trimmed === 'no') return false;

      // 表达式求值（安全方式）
      try {
        // 仅允许比较和逻辑运算
        const sanitized = condition.replace(/[^0-9a-zA-Z_\s=!<>&|().+\-*\/%]/g, '');
        const result = new Function('return ' + sanitized)();
        return Boolean(result);
      } catch (e) {
        // 如果无法求值，默认为false
        return false;
      }
    }

    return false;
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
      return { success: true, outputs: { result }, logs: ['[selector] 自动修复成功(retry)'] };
    }
    if (strategy === 'default_false_branch') {
      // 如果没有false_branch，使用默认值
      if (this.inputs.false_branch === undefined) {
        this.inputs.false_branch = { default: true };
        const result = await this.process();
        return { success: true, outputs: { result }, logs: ['[selector] 自动修复成功(使用默认false_branch)'] };
      }
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('condition') || error.message.includes('条件')) return 'CONDITION_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('Selector处理器启动');
  const handlerInstance = new SelectorHandler({
    inputs: input,
    name: 'selector',
    requiredInputs: ['condition'],
    autoFixStrategies: ['retry', 'default_false_branch']
  });
  return await handlerInstance.execute();
}

module.exports = SelectorHandler;
