/**
 * SQL自定义执行 处理器
 * 执行自定义SQL语句
 * 必要参数：sql
 */

class SQLCustomHandler {
  constructor(config) {
    this.config = config;
    this.inputs = config.inputs || {};
    this.outputs = {};
  }

  async execute() {
    try {
      // 参数验证
      this.validateInputs();
      
      // 核心逻辑
      const result = await this.process();
      
      // 设置输出
      this.outputs.result = result;
      
      return {
        success: true,
        outputs: this.outputs,
        logs: [`[${this.config.name}] 执行成功`]
      };
    } catch (error) {
      // 自动修复尝试
      const fixed = await this.attemptFix(error);
      if (fixed) {
        return fixed;
      }
      
      return {
        success: false,
        error: error.message,
        errorCode: this.classifyError(error),
        logs: [`[${this.config.name}] 执行失败: ${error.message}`]
      };
    }
  }

  validateInputs() {
    // 验证必要参数
    const required = this.config.requiredInputs || ['sql'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error(`缺少必要参数: ${key}`);
      }
    }
  }

  async process() {
    const sql = this.inputs.sql;
    const params = this.inputs.params || [];
    const dbConfig = this.inputs.dbConfig || {};

    // SQL安全校验
    this.validateSQL(sql);

    const result = await this.executeSQL(sql, params, dbConfig);
    return result;
  }

  validateSQL(sql) {
    const forbidden = ['drop', 'truncate'];
    const lower = sql.toLowerCase();
    for (const word of forbidden) {
      if (lower.includes(word)) {
        throw new Error(`包含禁止执行的SQL关键字: ${word}`);
      }
    }
  }

  async executeSQL(sql, params, dbConfig) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          sql,
          executed: true,
          rows: [{ id: 1, data: '示例数据' }],
          rowCount: 1,
          dbType: dbConfig.type || 'mysql'
        });
      }, 200);
    });
  }

  async attemptFix(error) {
    // 自动修复策略
    const strategies = this.config.autoFixStrategies || [];
    for (const strategy of strategies) {
      try {
        const result = await this.applyFix(strategy, error);
        if (result.success) return result;
      } catch (e) {
        continue;
      }
    }
    return null;
  }

  async applyFix(strategy, error) {
    if (strategy === 'remove_forbidden' && error.message.includes('禁止')) {
      return { success: false };
    }
    if (strategy === 'retry') {
      const result = await this.process();
      return { success: true, outputs: { result }, logs: [`[${this.config.name}] 自动修复成功`] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('connection')) return 'CONNECTION_ERROR';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('permission') || error.message.includes('权限')) return 'PERMISSION_DENIED';
    if (error.message.includes('禁止')) return 'FORBIDDEN';
    return 'UNKNOWN_ERROR';
  }
}

module.exports = SQLCustomHandler;

/**
 * 入口函数
 * @param {Object} params - 调用参数
 * @param {Object} params.input - 输入数据
 * @param {Object} params.logger - 日志记录器
 * @returns {Promise<Object>} 执行结果
 */
async function handler({ input, logger }) {
  const config = {
    name: 'sql_custom',
    inputs: input || {},
    requiredInputs: ['sql'],
    autoFixStrategies: ['remove_forbidden', 'retry']
  };
  
  const instance = new SQLCustomHandler(config);
  const result = await instance.execute();
  
  if (logger && result.logs) {
    result.logs.forEach(log => {
      if (typeof logger.info === 'function') logger.info(log);
      else if (typeof logger.log === 'function') logger.log(log);
    });
  }
  
  return result;
}

module.exports.handler = handler;
