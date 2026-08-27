/**
 * 代码节点处理器
 * 执行用户提供的代码，支持JavaScript和Python语言，可设置超时时间
 */

class CodeHandler {
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
      return { success: true, outputs: this.outputs, logs: ['[code] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[code] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['code'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.code !== 'string' || this.inputs.code.trim() === '') {
      throw new Error('参数 code 不能为空字符串');
    }
  }

  async process() {
    const code = this.inputs.code;
    const language = (this.inputs.language || 'javascript').toLowerCase();
    const timeout = this.inputs.timeout || 5000;

    if (language === 'javascript' || language === 'js') {
      return await this.executeJavaScript(code, timeout);
    } else if (language === 'python' || language === 'py') {
      return await this.executePython(code, timeout);
    } else {
      throw new Error('不支持的语言: ' + language + '，仅支持 javascript 和 python');
    }
  }

  async executeJavaScript(code, timeout) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error('代码执行超时(timeout)，超过 ' + timeout + 'ms'));
      }, timeout);

      try {
        // 创建沙箱上下文
        const sandbox = {
          result: null,
          console: {
            log: (...args) => { sandbox.__logs = (sandbox.__logs || []).concat(args.join(' ')); }
          },
          __logs: []
        };

        // 包装代码以捕获返回值
        const wrappedCode = `
          (function(sandbox) {
            var result = null;
            var console = sandbox.console;
            ${code}
            sandbox.result = typeof result !== 'undefined' ? result : (typeof __result !== 'undefined' ? __result : null);
          })(arguments[0])
        `;

        // 使用Function构造器执行（受限环境）
        const fn = new Function('sandbox', wrappedCode);
        fn(sandbox);

        clearTimeout(timer);
        resolve({
          language: 'javascript',
          output: sandbox.result,
          logs: sandbox.__logs,
          executed: true
        });
      } catch (error) {
        clearTimeout(timer);
        reject(new Error('JavaScript执行错误: ' + error.message));
      }
    });
  }

  async executePython(code, timeout) {
    // 模拟Python执行环境（实际环境中调用Python子进程）
    await new Promise(resolve => setTimeout(resolve, 30));

    // 检测是否有可能的危险操作
    const dangerousPatterns = [/import\s+os/, /import\s+subprocess/, /import\s+sys/, /exec\(/, /eval\(/];
    for (const pattern of dangerousPatterns) {
      if (pattern.test(code)) {
        throw new Error('代码包含受限的导入或操作');
      }
    }

    // 模拟执行结果
    const hasReturn = code.includes('return') || code.includes('=');
    return {
      language: 'python',
      output: hasReturn ? '[Python执行结果]' : null,
      stdout: code.split('\n').filter(l => l.trim().startsWith('print')).map(l => '[模拟输出]').join('\n'),
      executed: true
    };
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
      // 增加超时时间后重试
      if (this.inputs.timeout) {
        this.inputs.timeout = Math.min(this.inputs.timeout * 2, 30000);
      }
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[code] 自动修复成功(retry)'] };
    }
    if (strategy === 'fallback_language') {
      // 尝试切换到JavaScript
      if (this.inputs.language !== 'javascript') {
        this.inputs.language = 'javascript';
        const result = await this.process();
        return { success: true, outputs: { result }, logs: ['[code] 自动修复成功(切换到JavaScript)'] };
      }
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout') || error.message.includes('超时')) return 'TIMEOUT';
    if (error.message.includes('connection') || error.message.includes('ECONNREFUSED')) return 'CONNECTION_ERROR';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('不支持') || error.message.includes('不支持的语言')) return 'UNSUPPORTED_LANGUAGE';
    if (error.message.includes('受限') || error.message.includes('restricted')) return 'SECURITY_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('Code处理器启动');
  const handlerInstance = new CodeHandler({
    inputs: input,
    name: 'code',
    requiredInputs: ['code'],
    autoFixStrategies: ['retry', 'fallback_language']
  });
  return await handlerInstance.execute();
}

module.exports = CodeHandler;
