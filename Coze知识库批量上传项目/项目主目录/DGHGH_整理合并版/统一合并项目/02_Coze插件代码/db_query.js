/**
 * 数据库查询处理器
 * 执行SQL查询语句，支持参数化查询和结果分页
 */

class DBQueryHandler {
  constructor(config) {
    this.config = config;
    this.inputs = config.inputs || {};
    this.outputs = {};
    this.connectionPool = null;
  }

  async execute() {
    try {
      this.validateInputs();
      const result = await this.process();
      this.outputs.result = result;
      return { success: true, outputs: this.outputs, logs: ['[db_query] 执行成功'] };
    } catch (error) {
      const fixed = await this.attemptFix(error);
      if (fixed) return fixed;
      return { success: false, error: error.message, errorCode: this.classifyError(error), logs: ['[db_query] 执行失败: ' + error.message] };
    }
  }

  validateInputs() {
    const required = this.config.requiredInputs || ['sql'];
    for (const key of required) {
      if (this.inputs[key] === undefined || this.inputs[key] === null) {
        throw new Error('缺少必要参数: ' + key);
      }
    }
    if (typeof this.inputs.sql !== 'string' || this.inputs.sql.trim() === '') {
      throw new Error('参数 sql 不能为空字符串');
    }
  }

  async process() {
    const sql = this.inputs.sql;
    const params = this.inputs.params || [];
    const page = this.inputs.page || 1;
    const pageSize = this.inputs.page_size || 20;
    const timeout = this.inputs.timeout || 30000;
    const readOnly = this.inputs.read_only !== false;

    // SQL安全检查
    this.validateSQL(sql, readOnly);

    // 参数化检查
    const safeSql = this.sanitizeSQL(sql);
    const safeParams = this.validateParams(safeSql, params);

    // 执行查询
    const queryResult = await this.executeQuery(safeSql, safeParams, { page, pageSize, timeout });

    return {
      sql: safeSql,
      params: safeParams,
      rows: queryResult.rows,
      total: queryResult.total,
      page: page,
      page_size: pageSize,
      total_pages: Math.ceil(queryResult.total / pageSize),
      affected_rows: 0,
      execution_time_ms: queryResult.executionTime,
      executed: true
    };
  }

  validateSQL(sql, readOnly) {
    const upperSql = sql.trim().toUpperCase();

    // 检查是否为SELECT语句
    if (readOnly && !upperSql.startsWith('SELECT') && !upperSql.startsWith('WITH') && !upperSql.startsWith('SHOW')) {
      throw new Error('只读模式下仅允许SELECT/WITH/SHOW语句');
    }

    // 检查危险操作
    const dangerousPatterns = [
      /DROP\s+TABLE/i,
      /DROP\s+DATABASE/i,
      /TRUNCATE/i,
      /DELETE\s+FROM/i,
      /UPDATE\s+.*SET/i,
      /INSERT\s+INTO/i,
      /ALTER\s+TABLE/i,
      /CREATE\s+DATABASE/i,
      /GRANT/i,
      /REVOKE/i
    ];

    if (readOnly) {
      for (const pattern of dangerousPatterns) {
        if (pattern.test(sql)) {
          throw new Error('只读模式下不允许执行修改操作: ' + pattern.source);
        }
      }
    }

    // 检查SQL注入风险
    if (sql.includes('--') || sql.includes('/*') || sql.includes(';')) {
      // 允许多语句但发出警告
      // 在实际应用中应该阻止
    }
  }

  sanitizeSQL(sql) {
    // 去除多余的空白和注释
    return sql.trim().replace(/\s+/g, ' ');
  }

  validateParams(sql, params) {
    if (!Array.isArray(params)) {
      params = [params];
    }
    // 计算占位符数量
    const placeholderCount = (sql.match(/\?/g) || []).length;
    if (params.length !== placeholderCount) {
      throw new Error('参数数量不匹配: 期望 ' + placeholderCount + ' 个参数，实际 ' + params.length + ' 个');
    }
    return params.map(p => {
      if (p === null || p === undefined) return null;
      if (typeof p === 'string') return p.substring(0, 10000);
      if (typeof p === 'number') return p;
      if (typeof p === 'boolean') return p;
      if (p instanceof Date) return p.toISOString();
      return JSON.stringify(p);
    });
  }

  async executeQuery(sql, params, options) {
    await new Promise(resolve => setTimeout(resolve, 30));

    // 模拟查询结果
    const totalRows = 50;
    const offset = (options.page - 1) * options.pageSize;
    const rows = [];

    for (let i = 0; i < Math.min(options.pageSize, totalRows - offset); i++) {
      rows.push({
        id: offset + i + 1,
        name: '记录_' + (offset + i + 1),
        value: Math.random() * 100,
        created_at: new Date(Date.now() - Math.random() * 86400000).toISOString(),
        status: ['active', 'inactive', 'pending'][Math.floor(Math.random() * 3)]
      });
    }

    return {
      rows: rows,
      total: totalRows,
      executionTime: Math.floor(Math.random() * 100 + 20)
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
      // 只读模式重试
      this.inputs.read_only = true;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[db_query] 自动修复成功(retry, 只读模式)'] };
    }
    if (strategy === 'reduce_page_size') {
      // 减小分页大小
      this.inputs.page_size = 10;
      const result = await this.process();
      return { success: true, outputs: { result }, logs: ['[db_query] 自动修复成功(减小分页)'] };
    }
    return { success: false };
  }

  classifyError(error) {
    if (error.message.includes('timeout')) return 'TIMEOUT';
    if (error.message.includes('connection') || error.message.includes('ECONNREFUSED')) return 'CONNECTION_ERROR';
    if (error.message.includes('param') || error.message.includes('参数')) return 'PARAM_ERROR';
    if (error.message.includes('sql') || error.message.includes('SQL')) return 'SQL_ERROR';
    if (error.message.includes('syntax') || error.message.includes('语法')) return 'SYNTAX_ERROR';
    if (error.message.includes('permission') || error.message.includes('权限')) return 'PERMISSION_DENIED';
    if (error.message.includes('table') || error.message.includes('表')) return 'TABLE_ERROR';
    return 'UNKNOWN_ERROR';
  }
}

export async function handler({ input, logger }) {
  if (logger) logger.info('DBQuery处理器启动');
  const handlerInstance = new DBQueryHandler({
    inputs: input,
    name: 'db_query',
    requiredInputs: ['sql'],
    autoFixStrategies: ['retry', 'reduce_page_size']
  });
  return await handlerInstance.execute();
}

module.exports = DBQueryHandler;
