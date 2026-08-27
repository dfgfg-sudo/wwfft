/**
 * 批处理节点处理器
 * 将items按batch_size分批，对每批数据执行process_fn处理
 */

class BatchHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[batch] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[batch] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['items'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (!Array.isArray(this.inputs.items)) {
      throw new Error('参数 items 必须是数组');
    }
  }

  async process() {
    const items = this.inputs.items;
    const batchSize = this.inputs.batch_size || 10;
    const processFn = this.inputs.process_fn;
    const concurrency = this.inputs.concurrency || 1;
    const continueOnError = this.inputs.continue_on_error !== false;

    // 安全检查batch_size
    const safeBatchSize = Math.max(1, Math.min(batchSize, items.length || 1));

    // 分批
    const batches = [];
    for (let i = 0; i < items.length; i += safeBatchSize) {
      batches.push(items.slice(i, i + safeBatchSize));
    }

    const batchResults = [];
    const allErrors = [];

    for (let i = 0; i < batches.length; i++) {
      const batch = batches[i];
      try {
        let batchResult;
        if (typeof processFn === 'function') {
          batchResult = await processFn(batch, i);
        } else if (typeof processFn === 'object' && processFn !== null) {
          batchResult = await this.executeProcessFn(batch, i, processFn);
        } else {
          batchResult = await this.defaultBatchProcess(batch, i);
        }
        batchResults.push({ batch_index: i, success: true, result: batchResult, count: batch.length });
      } catch (err) {
        allErrors.push({ batch_index: i, error: err.message, count: batch.length });
        batchResults.push({ batch_index: i, success: false, error: err.message, count: batch.length });
        if (!continueOnError) {
          break;
        }
      }
    }

    const successfulBatches = batchResults.filter(r => r.success);
    const allResults = successfulBatches.flatMap(r => {
      return Array.isArray(r.result) ? r.result : [r.result];
    });

    return {
      total_items: items.length,
      total_batches: batches.length,
      batch_size: safeBatchSize,
      processed_batches: batchResults.length,
      successful_batches: successfulBatches.length,
      failed_batches: allErrors.length,
      results: allResults,
      batch_results: batchResults,
      errors: allErrors,
      has_errors: allErrors.length > 0,
      executed: true
    };
  }

  async executeProcessFn(batch, batchIndex, fnConfig) {
    await new Promise(resolve => setTimeout(resolve, 10));
    const operation = fnConfig.operation || 'collect';

    switch (operation) {
      case 'collect':
        return batch;
      case 'count':
        return batch.length;
      case 'sum':
        return batch.reduce((sum, item) => sum + (typeof item === 'number' ? item : Number(item) || 0), 0);
      case 'average':
        const nums = batch.filter(x => typeof x === 'number');
        return nums.length > 0 ? nums.reduce((s, n) => s + n, 0) / nums.length : 0;
      case 'unique':
        return [...new Set(batch)];
      case 'sort':
        return [...batch].sort();
      default:
        return { batch: batch, operation: operation };
    }
  }

  async defaultBatchProcess(batch, batchIndex) {
    await new Promise(resolve => setTimeout(resolve, 5));
    return batch.map((item, idx) => ({
      batch: batchIndex,
      index: idx,
      value: item,
      processed: true
    }));
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
      // 出错后继续执行
      this.inputs.continue_on_error = true;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[batch] 自动修复成功(retry)'] };
    }
    if (strategy === 'reduce_batch_size') {
      // 减小批次大小后重试
      const newSize = Math.max(1, Math.floor((this.inputs.batch_size || 10) / 2));
      this.inputs.batch_size = newSize;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[batch] 自动修复成功(减小批次大小)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('memory') || error.message.includes('内存')) return 'MEMORY_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('Batch处理器启动');
  const handlerInstance = new BatchHandler({
    inputs: input,
    name: 'batch',
    requiredInputs: ['items'],
    autoFixStrategies: ['retry', 'reduce_batch_size']
  });
  return await handlerInstance.execute();
}

module.exports = BatchHandler;
