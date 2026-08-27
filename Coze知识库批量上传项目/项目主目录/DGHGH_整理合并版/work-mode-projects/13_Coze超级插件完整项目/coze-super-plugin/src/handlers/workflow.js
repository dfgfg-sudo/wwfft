/**
 * 工作流节点处理器
 * 根据workflowId调用指定的工作流，并将data作为输入数据传递给工作流执行
 */

class WorkflowHandler {
  constructor(config) {
    this.config = config;
    this.inputs = config.inputs || {};
    this.outputs = {};
    this.workflowRegistry = {};
  }

  async execute() {
    try {
      this.validateInputs();
      const result = await this.process();
      this.outputs.result = result;
      return { success: true, outputs: this.outputs, logs: ['[workflow] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[workflow] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['workflowId'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.workflowId !== 'string' || this.inputs.workflowId.trim() === '') {
      throw new Error('参数 workflowId 必须是非空字符串');
    }
  }

  async process() {
    const workflowId = this.inputs.workflowId;
    const data = this.inputs.data || {};

    // 加载工作流定义（模拟）
    const workflowDef = await this.loadWorkflow(workflowId);
    if (!workflowDef) {
      throw new Error('工作流不存在: ' + workflowId);
    }

    // 执行工作流步骤
    const steps = workflowDef.steps || [];
    const context = { ...data };
    const stepResults = [];

    for (let i = 0; i < steps.length; i++) {
      const step = steps[i];
      const stepResult = await this.executeStep(step, context);
      stepResults.push({ step: step.name, result: stepResult });
      if (step.output_key) {
        context[step.output_key] = stepResult;
      }
    }

    return {
      workflowId: workflowId,
      input_data: data,
      output_data: context,
      steps_executed: steps.length,
      step_results: stepResults,
      executed: true
    };
  }

  async loadWorkflow(workflowId) {
    await new Promise(resolve => setTimeout(resolve, 20));

    // 模拟工作流定义
    const workflows = {
      'default_workflow': {
        id: 'default_workflow',
        name: '默认工作流',
        steps: [
          { name: 'input_parse', type: 'transform', output_key: 'parsed' },
          { name: 'process', type: 'transform', output_key: 'processed' },
          { name: 'output', type: 'output', output_key: 'result' }
        ]
      }
    };

    return workflows[workflowId] || {
      id: workflowId,
      name: '动态工作流',
      steps: [
        { name: 'init', type: 'init', output_key: 'initialized' },
        { name: 'execute', type: 'process', output_key: 'result' }
      ]
    };
  }

  async executeStep(step, context) {
    await new Promise(resolve => setTimeout(resolve, 10));
    switch (step.type) {
      case 'init':
        return { status: 'initialized', context_keys: Object.keys(context) };
      case 'transform':
        return { status: 'transformed', data: context };
      case 'process':
        return { status: 'processed', data: context };
      case 'output':
        return { status: 'complete', output: context };
      default:
        return { status: 'unknown_step', type: step.type };
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
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[workflow] 自动修复成功(retry)'] };
    }
    if (strategy === 'default_data') {
      if (!this.inputs.data) {
        this.inputs.data = {};
        const result = await this.process();
        return { success: true, outputs: { result }, logs: ['[workflow] 自动修复成功(使用默认data)'] };
      }
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('connection') || error.message.includes('ECONNREFUSED')) return 'CONNECTION_ERROR';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('不存在') || error.message.includes('not found')) return 'NOT_FOUND';
    if (error.message.includes('permission') || error.message.includes('权限')) return 'PERMISSION_DENIED';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('Workflow处理器启动');
  const handlerInstance = new WorkflowHandler({
    inputs: input,
    name: 'workflow',
    requiredInputs: ['workflowId'],
    autoFixStrategies: ['retry', 'default_data']
  });
  return await handlerInstance.execute();
}

module.exports = WorkflowHandler;
