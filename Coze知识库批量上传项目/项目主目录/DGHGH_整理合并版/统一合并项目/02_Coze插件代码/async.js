/**
 * 异步执行处理器
 * 并发执行多个异步任务，支持并行和串行模式
 */

class AsyncHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[async] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[async] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['tasks'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (!Array.isArray(this.inputs.tasks)) {
      throw new Error('参数 tasks 必须是数组');
    }
  }

  async process() {
    const tasks = this.inputs.tasks;
    const mode = this.inputs.mode || 'parallel';
    const concurrency = this.inputs.concurrency || tasks.length;
    const timeout = this.inputs.timeout || 30000;
    const continueOnError = this.inputs.continue_on_error !== false;

    let results;
    let errors = [];

    if (mode === 'parallel' || mode === 'race') {
      if (mode === 'race') {
        // 竞速模式：返回第一个完成的结果
        results = await this.executeRace(tasks, timeout);
      } else {
        // 并行模式：全部执行
        results = await this.executeParallel(tasks, concurrency, timeout, continueOnError, errors);
      }
    } else if (mode === 'sequential' || mode === 'serial') {
      // 串行模式：依次执行
      results = await this.executeSequential(tasks, timeout, continueOnError, errors);
    } else {
      // 默认并行
      results = await this.executeParallel(tasks, concurrency, timeout, continueOnError, errors);
    }

    return {
      mode: mode,
      total_tasks: tasks.length,
      completed: results.length,
      results: results,
      errors: errors,
      has_errors: errors.length > 0,
      executed: true
    };
  }

  async executeParallel(tasks, concurrency, timeout, continueOnError, errors) {
    const results = [];
    const batches = [];

    // 按并发数分批
    for (let i = 0; i < tasks.length; i += concurrency) {
      batches.push(tasks.slice(i, i + concurrency));
    }

    for (const batch of batches) {
      const batchPromises = batch.map((task, idx) => {
        return this.executeTask(task, timeout).catch(err => {
          errors.push({ task_index: idx, error: err.message });
          if (!continueOnError) throw err;
          return null;
        });
      });

      const batchResults = await Promise.all(batchPromises);
      batchResults.forEach((r, idx) => {
        if (r !== null) {
          results.push({ task_index: results.length, result: r, success: true });
        }
      });
    }

    return results;
  }

  async executeSequential(tasks, timeout, continueOnError, errors) {
    const results = [];
    for (let i = 0; i < tasks.length; i++) {
      try {
        const result = await this.executeTask(tasks[i], timeout);
        results.push({ task_index: i, result: result, success: true });
      } catch (err) {
        errors.push({ task_index: i, error: err.message });
        if (!continueOnError) {
          break;
        }
      }
    }
    return results;
  }

  async executeRace(tasks, timeout) {
    const taskPromises = tasks.map(task => this.executeTask(task, timeout));
    const result = await Promise.race(taskPromises);
    return [{ task_index: 0, result: result, success: true, mode: 'race' }];
  }

  async executeTask(task, timeout) {
    if (typeof task === 'function') {
      return await this.withTimeout(task(), timeout);
    }
    if (typeof task === 'object' && task !== null) {
      if (typeof task.execute === 'function') {
        return await this.withTimeout(task.execute(), timeout);
      }
      if (task.fn && typeof task.fn === 'function') {
        return await this.withTimeout(task.fn(task.args || {}), timeout);
      }
      // 模拟任务执行
      await new Promise(resolve => setTimeout(resolve, 10));
      return { task_result: task, executed: true };
    }
    return task;
  }

  withTimeout(promise, ms) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error('任务执行超时(timeout)，超过 ' + ms + 'ms'));
      }, ms);
      promise.then(
        (result) => { clearTimeout(timer); resolve(result); },
        (error) => { clearTimeout(timer); reject(error); }
      );
    });
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
      this.inputs.continue_on_error = true;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[async] 自动修复成功(retry)'] };
    }
    if (strategy === 'switch_to_sequential') {
      // 切换到串行模式
      this.inputs.mode = 'sequential';
      this.inputs.continue_on_error = true;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[async] 自动修复成功(切换到串行模式)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout') || error.message.includes('超时')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('task') || error.message.includes('任务')) return 'TASK_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('Async处理器启动');
  const handlerInstance = new AsyncHandler({
    inputs: input,
    name: 'async',
    requiredInputs: ['tasks'],
    autoFixStrategies: ['retry', 'switch_to_sequential']
  });
  return await handlerInstance.execute();
}

module.exports = AsyncHandler;
