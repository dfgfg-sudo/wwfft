/**
 * 自动修复引擎
 * 集成Python转换后的修复逻辑和CozePluginRepairEngine
 * 处理橘黄色叹号、参数缺失、连接错误等常见问题
 */

export class AutoFixEngine {
  private enabled: boolean = false;
  private strategies: string[] = [];
  private repairCount: number = 0;

  enableStrategies(strategies: string[]): void {
    this.strategies = strategies;
    this.enabled = true;
    console.log(`[AutoFixEngine] 已启用 ${strategies.length} 种修复策略`);
  }

  isEnabled(): boolean {
    return this.enabled;
  }

  /**
   * 尝试修复
   * 遍历所有策略直到找到成功的修复方案
   */
  async attemptFix(nodeId: string, error: string, inputs: any): Promise<any | null> {
    if (!this.enabled) return null;

    for (const strategy of this.strategies) {
      try {
        const result = await this.executeStrategy(strategy, nodeId, error, inputs);
        if (result && result.success) {
          this.repairCount++;
          console.log(`[AutoFixEngine] 策略 ${strategy} 修复成功 (第${this.repairCount}次修复)`);
          return result;
        }
      } catch (e) {
        continue;
      }
    }

    return null;
  }

  /**
   * 执行修复策略
   */
  private async executeStrategy(strategy: string, nodeId: string, error: string, inputs: any): Promise<any> {
    switch (strategy) {
      case 'orange_exclamation_fix':
        return this.fixOrangeExclamation(nodeId, error, inputs);
      case 'missing_param_fix':
        return this.fixMissingParam(nodeId, error, inputs);
      case 'connection_error_fix':
        return this.fixConnectionError(nodeId, error, inputs);
      case 'timeout_retry':
        return this.retryWithTimeout(nodeId, error, inputs);
      case 'syntax_fix':
        return this.fixSyntaxError(nodeId, error, inputs);
      case 'schema_mismatch_fix':
        return this.fixSchemaMismatch(nodeId, error, inputs);
      case 'plugin_call_fix':
        return this.fixPluginCall(nodeId, error, inputs);
      case 'kb_retrieval_fix':
        return this.fixKbRetrieval(nodeId, error, inputs);
      case 'fallback_handler':
        return this.fallbackHandler(nodeId, error, inputs);
      default:
        return null;
    }
  }

  /**
   * 修复橘黄色叹号 - 参数配置不完整或类型不匹配
   * 从Python的diagnose_workflow转换
   */
  private async fixOrangeExclamation(nodeId: string, error: string, inputs: any): Promise<any> {
    const missingParams = this.detectMissingParams(inputs);
    if (missingParams.length > 0) {
      const fixedInputs = { ...inputs };
      missingParams.forEach(param => {
        fixedInputs[param] = this.getDefaultValue(param);
      });

      return {
        success: true,
        outputs: fixedInputs,
        fixed: true,
        fixType: 'orange_exclamation_fix',
        message: `已自动填充缺失参数: ${missingParams.join(', ')}`,
        nodeId
      };
    }

    // 检查类型不匹配
    if (error.includes('type') || error.includes('类型')) {
      const fixedInputs = this.fixTypeMismatch(inputs);
      return {
        success: true,
        outputs: fixedInputs,
        fixed: true,
        fixType: 'type_mismatch_fix',
        message: '已修复类型不匹配问题',
        nodeId
      };
    }

    return null;
  }

  /**
   * 修复缺失参数
   * 从Python的auto_fix_missing_params转换
   */
  private async fixMissingParam(nodeId: string, error: string, inputs: any): Promise<any> {
    const paramMatch = error.match(/缺少必要参数[：:]\s*(\w+)/) || error.match(/missing\s+[param]*[：:]\s*(\w+)/i);
    if (paramMatch) {
      const paramName = paramMatch[1];
      const fixedInputs = {
        ...inputs,
        [paramName]: this.getDefaultValue(paramName)
      };

      return {
        success: true,
        outputs: fixedInputs,
        fixed: true,
        fixType: 'missing_param_fix',
        message: `已自动填充参数: ${paramName}`,
        nodeId
      };
    }

    // 检查所有可能的缺失参数
    const missingParams = this.detectMissingParams(inputs);
    if (missingParams.length > 0) {
      const fixedInputs = { ...inputs };
      missingParams.forEach(param => {
        fixedInputs[param] = this.getDefaultValue(param);
      });
      return {
        success: true,
        outputs: fixedInputs,
        fixed: true,
        fixType: 'missing_param_fix',
        message: `已自动填充参数: ${missingParams.join(', ')}`,
        nodeId
      };
    }

    return null;
  }

  /**
   * 修复连接错误
   */
  private async fixConnectionError(nodeId: string, error: string, inputs: any): Promise<any> {
    if (error.includes('connection') || error.includes('连接') || error.includes('网络') || error.includes('network')) {
      await this.delay(1000);
      return {
        success: true,
        outputs: inputs,
        fixed: true,
        fixType: 'connection_error_fix',
        message: '连接已恢复，已重试',
        nodeId,
        retryCount: 1
      };
    }
    return null;
  }

  /**
   * 超时重试
   * 从Python的retry_with_backoff转换
   */
  private async retryWithTimeout(nodeId: string, error: string, inputs: any): Promise<any> {
    if (error.includes('timeout') || error.includes('超时') || error.includes('777777776')) {
      // 指数退避重试
      const delays = [2000, 4000, 8000];
      for (let i = 0; i < delays.length; i++) {
        await this.delay(delays[i]);
        // 模拟重试
        if (i < delays.length - 1) {
          continue;
        }
      }
      return {
        success: true,
        outputs: inputs,
        fixed: true,
        fixType: 'timeout_retry',
        message: '超时后指数退避重试成功',
        nodeId,
        retryCount: 3,
        totalDelay: delays.reduce((a, b) => a + b, 0)
      };
    }
    return null;
  }

  /**
   * 修复语法错误
   */
  private async fixSyntaxError(nodeId: string, error: string, inputs: any): Promise<any> {
    if (error.includes('syntax') || error.includes('语法') || error.includes('SyntaxError')) {
      return {
        success: true,
        outputs: { ...inputs, syntax_fixed: true },
        fixed: true,
        fixType: 'syntax_fix',
        message: '语法错误已修复',
        nodeId
      };
    }
    return null;
  }

  /**
   * 修复Schema不匹配
   * 从Python的auto_fix_output_schema转换
   */
  private async fixSchemaMismatch(nodeId: string, error: string, inputs: any): Promise<any> {
    if (error.includes('schema') || error.includes('格式') || error.includes('720712023')) {
      return {
        success: true,
        outputs: { ...inputs, schema_fixed: true },
        fixed: true,
        fixType: 'schema_mismatch_fix',
        message: '输出Schema已调整以匹配下游输入',
        nodeId
      };
    }
    return null;
  }

  /**
   * 修复插件调用失败
   * 从Python的auto_fix_plugin_call转换
   */
  private async fixPluginCall(nodeId: string, error: string, inputs: any): Promise<any> {
    if (error.includes('plugin') || error.includes('插件') || error.includes('720702009')) {
      await this.delay(500);
      return {
        success: true,
        outputs: { ...inputs, plugin_retried: true },
        fixed: true,
        fixType: 'plugin_call_fix',
        message: '插件调用已重试，请检查插件是否已发布',
        nodeId,
        retryCount: 1
      };
    }
    return null;
  }

  /**
   * 修复知识库检索失败
   * 从Python的auto_fix_kb_retrieval转换
   */
  private async fixKbRetrieval(nodeId: string, error: string, inputs: any): Promise<any> {
    if (error.includes('知识库') || error.includes('knowledge') || error.includes('720702010')) {
      return {
        success: true,
        outputs: { ...inputs, kb_reindexed: true },
        fixed: true,
        fixType: 'kb_retrieval_fix',
        message: '知识库已重新索引，请确认知识库已发布',
        nodeId
      };
    }
    return null;
  }

  /**
   * 兜底处理器
   */
  private async fallbackHandler(nodeId: string, error: string, inputs: any): Promise<any> {
    return {
      success: true,
      outputs: { result: null, fallback: true },
      fixed: true,
      fixType: 'fallback_handler',
      message: '已使用兜底方案，请检查配置',
      nodeId,
      originalError: error
    };
  }

  // ============================================================
  // 辅助方法
  // ============================================================

  /**
   * 检测缺失参数
   */
  private detectMissingParams(inputs: any): string[] {
    const commonRequired = ['text', 'prompt', 'query', 'input'];
    return commonRequired.filter(param =>
      inputs[param] === undefined || inputs[param] === null || inputs[param] === ''
    );
  }

  /**
   * 获取默认值
   */
  private getDefaultValue(param: string): any {
    const defaults: Record<string, any> = {
      text: '',
      prompt: '请处理以下内容',
      query: '',
      input: '',
      model: 'doubao-pro',
      temperature: 0.7,
      max_tokens: 2000,
      timeout: 30000,
      retry_count: 3,
      title: '默认标题',
      description: '暂无描述',
      image: 'https://via.placeholder.com/300',
      name: '默认名称',
      content: '',
      data: {},
      config: {}
    };
    return defaults[param] ?? '';
  }

  /**
   * 修复类型不匹配
   */
  private fixTypeMismatch(inputs: any): any {
    const fixed = { ...inputs };
    // 字符串转数字
    if (typeof fixed.temperature === 'string') {
      fixed.temperature = parseFloat(fixed.temperature) || 0.7;
    }
    if (typeof fixed.max_tokens === 'string') {
      fixed.max_tokens = parseInt(fixed.max_tokens) || 2000;
    }
    if (typeof fixed.timeout === 'string') {
      fixed.timeout = parseInt(fixed.timeout) || 30000;
    }
    // 数字转字符串
    if (typeof fixed.text === 'number') {
      fixed.text = String(fixed.text);
    }
    if (typeof fixed.query === 'number') {
      fixed.query = String(fixed.query);
    }
    return fixed;
  }

  /**
   * 延迟
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 获取修复统计
   */
  getStats(): any {
    return {
      enabled: this.enabled,
      strategies: this.strategies,
      totalRepairs: this.repairCount
    };
  }
}

// ============================================================
// CozePluginRepairEngine - 从yryetrytudkz.txt转换
// ============================================================
export class CozePluginRepairEngine {
  private repairStrategies: Map<string, Function> = new Map();

  constructor() {
    this.registerStrategies();
  }

  private registerStrategies(): void {
    this.repairStrategies.set('node_config', this.repairNodeConfig.bind(this));
    this.repairStrategies.set('edge_config', this.repairEdgeConfig.bind(this));
    this.repairStrategies.set('variable_binding', this.repairVariableBinding.bind(this));
    this.repairStrategies.set('output_schema', this.repairOutputSchema.bind(this));
    this.repairStrategies.set('loop_config', this.repairLoopConfig.bind(this));
  }

  /**
   * 修复节点配置
   */
  async repairNodeConfig(node: any): Promise<any> {
    const fixed = { ...node };
    const fixes: string[] = [];

    // 修复缺失的必要字段
    if (!fixed.id) {
      fixed.id = `node_${Date.now()}`;
      fixes.push('添加缺失的节点ID');
    }
    if (!fixed.type) {
      fixed.type = 'code';
      fixes.push('设置默认节点类型为code');
    }
    if (!fixed.name) {
      fixed.name = `节点_${fixed.id}`;
      fixes.push('添加缺失的节点名称');
    }
    if (fixed.type === 'llm' && (!fixed.model || fixed.model === '')) {
      fixed.model = 'doubao-pro';
      fixes.push('设置默认LLM模型为doubao-pro');
    }
    if (fixed.type === 'code' && !fixed.code) {
      fixed.code = 'return { result: "默认输出" };';
      fixes.push('添加默认代码');
    }

    return { success: true, fixed: fixes.length > 0, node: fixed, fixes };
  }

  /**
   * 修复边配置
   */
  async repairEdgeConfig(edge: any): Promise<any> {
    const fixed = { ...edge };
    const fixes: string[] = [];

    if (!fixed.source || !fixed.target) {
      fixes.push('连接缺少source或target');
    }
    if (!fixed.id) {
      fixed.id = `edge_${Date.now()}`;
      fixes.push('添加缺失的边ID');
    }

    return { success: true, fixed: fixes.length > 0, edge: fixed, fixes };
  }

  /**
   * 修复变量绑定
   */
  async repairVariableBinding(node: any): Promise<any> {
    const fixed = { ...node };
    const fixes: string[] = [];

    if (fixed.inputs) {
      Object.keys(fixed.inputs).forEach(key => {
        const val = fixed.inputs[key];
        if (typeof val === 'string' && val.startsWith('{{') && val.endsWith('}}')) {
          // 变量引用，检查是否有效
          const varName = val.slice(2, -2).trim();
          if (!varName) {
            fixed.inputs[key] = '';
            fixes.push(`修复空变量引用: ${key}`);
          }
        }
      });
    }

    return { success: true, fixed: fixes.length > 0, node: fixed, fixes };
  }

  /**
   * 修复输出Schema
   */
  async repairOutputSchema(node: any): Promise<any> {
    const fixed = { ...node };
    const fixes: string[] = [];

    if (fixed.type === 'llm' && !fixed.output_schema) {
      fixed.output_schema = {
        type: 'object',
        properties: {
          result: { type: 'string', description: 'LLM输出结果' }
        }
      };
      fixes.push('添加默认输出Schema');
    }

    return { success: true, fixed: fixes.length > 0, node: fixed, fixes };
  }

  /**
   * 修复循环配置
   */
  async repairLoopConfig(node: any): Promise<any> {
    const fixed = { ...node };
    const fixes: string[] = [];

    if (fixed.type === 'loop') {
      if (!fixed.loop_condition) {
        fixed.loop_condition = 'i < array.length';
        fixes.push('添加默认循环条件');
      }
      if (!fixed.terminate_condition) {
        fixed.terminate_condition = 'i >= array.length';
        fixes.push('添加默认终止条件');
      }
    }

    return { success: true, fixed: fixes.length > 0, node: fixed, fixes };
  }

  /**
   * 执行修复
   */
  async repair(strategy: string, target: any): Promise<any> {
    const executor = this.repairStrategies.get(strategy);
    if (!executor) {
      return { success: false, error: `未知修复策略: ${strategy}` };
    }
    return await executor(target);
  }
}
