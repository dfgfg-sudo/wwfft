/**
 * ============================================================================
 * Coze 工作流全自动安全修复引擎 - WorkflowAutoFixer (CJS 版)
 * Coze 终极超级插件
 * ============================================================================
 * 
 * 功能概述:
 *   本模块提供一套完整的工作流诊断、自动修复、报告生成、错误分类、
 *   知识库分块、卡片变量填充等企业级自动化工具链。所有函数均采用 
 *   CommonJS 规范编写，可直接在 Node.js 环境中运行。
 * 
 * 设计原则:
 *   1. 安全优先: 所有输入均经过严格校验，防止非法数据注入
 *   2. 元数据驱动: 每个函数均附带完整的 JSON Schema 输入/输出定义
 *   3. 零依赖: 仅使用 Node.js 内置模块，确保可移植性
 *   4. 教学友好: 代码结构清晰，先理解问题、后解决问题
 * 
 * 适用版本: Node.js >= 14.0.0
 * 许可证: MIT
 * ============================================================================
 */

'use strict';

// ============================================================================
// 安全校验工具层 (Security Validation Layer)
// ============================================================================

/**
 * 校验输入是否为有效的对象
 * @param {*} value - 待校验的值
 * @param {string} paramName - 参数名称（用于错误提示）
 * @returns {object} - 校验通过的对象
 * @throws {TypeError} - 校验失败时抛出
 */
function validateObject(value, paramName) {
  if (value === null || value === undefined) {
    throw new TypeError(`参数 "${paramName}" 不能为空，期望类型为 object，实际收到 ${value}`);
  }
  if (typeof value !== 'object' || Array.isArray(value)) {
    throw new TypeError(`参数 "${paramName}" 类型错误，期望 object，实际收到 ${typeof value}`);
  }
  return value;
}

/**
 * 校验输入是否为有效的字符串
 * @param {*} value - 待校验的值
 * @param {string} paramName - 参数名称
 * @param {number} [maxLength=10000] - 最大允许长度
 * @returns {string} - 校验通过的字符串
 * @throws {TypeError} - 校验失败时抛出
 */
function validateString(value, paramName, maxLength = 10000) {
  if (typeof value !== 'string') {
    throw new TypeError(`参数 "${paramName}" 类型错误，期望 string，实际收到 ${typeof value}`);
  }
  if (value.length > maxLength) {
    throw new RangeError(`参数 "${paramName}" 长度超出限制，最大允许 ${maxLength} 字符，实际 ${value.length}`);
  }
  // 基础 XSS 防护：检测危险脚本标签
  const dangerousPattern = /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi;
  if (dangerousPattern.test(value)) {
    throw new SecurityError(`参数 "${paramName}" 包含危险的脚本内容，已被拦截`);
  }
  return value;
}

/**
 * 校验输入是否为有效的数字
 * @param {*} value - 待校验的值
 * @param {string} paramName - 参数名称
 * @param {number} [min=-Infinity] - 最小值
 * @param {number} [max=Infinity] - 最大值
 * @returns {number} - 校验通过的数字
 * @throws {TypeError|RangeError} - 校验失败时抛出
 */
function validateNumber(value, paramName, min = -Infinity, max = Infinity) {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    throw new TypeError(`参数 "${paramName}" 类型错误，期望 number，实际收到 ${typeof value}`);
  }
  if (value < min || value > max) {
    throw new RangeError(`参数 "${paramName}" 超出有效范围 [${min}, ${max}]，实际值为 ${value}`);
  }
  return value;
}

/**
 * 校验输入是否为有效的数组
 * @param {*} value - 待校验的值
 * @param {string} paramName - 参数名称
 * @returns {Array} - 校验通过的数组
 * @throws {TypeError} - 校验失败时抛出
 */
function validateArray(value, paramName) {
  if (!Array.isArray(value)) {
    throw new TypeError(`参数 "${paramName}" 类型错误，期望 array，实际收到 ${typeof value}`);
  }
  return value;
}

/**
 * 自定义安全错误类
 */
class SecurityError extends Error {
  constructor(message) {
    super(message);
    this.name = 'SecurityError';
    this.code = 'SECURITY_VIOLATION';
  }
}

/**
 * 深度克隆对象（防止外部修改内部状态）
 * @param {object} obj - 待克隆的对象
 * @returns {object} - 克隆后的新对象
 */
function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (Array.isArray(obj)) return obj.map(item => deepClone(item));
  const cloned = {};
  for (const key of Object.keys(obj)) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      cloned[key] = deepClone(obj[key]);
    }
  }
  return cloned;
}

/**
 * 安全字符串转义（用于报告输出）
 * @param {string} str - 原始字符串
 * @returns {string} - 转义后的字符串
 */
function escapeHtml(str) {
  if (typeof str !== 'string') return str;
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  };
  return str.replace(/[&<>"'\/]/g, s => map[s]);
}

// ============================================================================
// 核心功能层 - 工作流诊断与修复
// ============================================================================

/**
 * 诊断工作流配置的健康状况
 * 
 * 功能说明:
 *   遍历工作流节点配置，检测常见问题如孤立节点、循环依赖、
 *   缺失必要参数、节点类型不合法等，并给出健康评分与修复建议。
 * 
 * @param {object} config - 工作流配置对象
 * @param {Array} config.nodes - 工作流节点数组
 * @returns {object} - 诊断结果
 *   @returns {number} health_score - 健康评分 (0-100)
 *   @returns {Array} issues - 发现的问题列表
 *   @returns {Array} suggestions - 优化建议列表
 */
function diagnoseWorkflow(config) {
  // ---- 安全校验层 ----
  const safeConfig = validateObject(config, 'config');
  const nodes = validateArray(safeConfig.nodes, 'config.nodes');

  // ---- 初始化诊断结果 ----
  const issues = [];
  const suggestions = [];
  let healthScore = 100;

  // ---- 节点基础校验 ----
  if (nodes.length === 0) {
    issues.push({
      level: 'error',
      code: 'EMPTY_WORKFLOW',
      message: '工作流节点列表为空，至少需要一个节点才能构成有效工作流',
      target: null
    });
    healthScore = 0;
    return { health_score: healthScore, issues, suggestions };
  }

  const nodeIds = new Set();
  const nodeMap = new Map();
  const validNodeTypes = new Set([
    'start', 'end', 'llm', 'code', 'condition', 'http',
    'knowledge', 'variable', 'loop', 'delay', 'plugin'
  ]);

  // ---- 遍历节点进行逐项检测 ----
  for (let i = 0; i < nodes.length; i++) {
    const node = nodes[i];
    const nodeRef = `nodes[${i}]`;

    // 节点必须为对象
    if (!node || typeof node !== 'object' || Array.isArray(node)) {
      issues.push({
        level: 'error',
        code: 'INVALID_NODE_TYPE',
        message: `第 ${i + 1} 个节点类型无效，期望为对象`,
        target: nodeRef
      });
      healthScore -= 15;
      continue;
    }

    // 节点 ID 必填且唯一
    if (!node.id || typeof node.id !== 'string') {
      issues.push({
        level: 'error',
        code: 'MISSING_NODE_ID',
        message: `第 ${i + 1} 个节点缺少有效的 "id" 字段`,
        target: nodeRef
      });
      healthScore -= 10;
    } else if (nodeIds.has(node.id)) {
      issues.push({
        level: 'error',
        code: 'DUPLICATE_NODE_ID',
        message: `发现重复的节点 ID: "${node.id}"`,
        target: node.id
      });
      healthScore -= 10;
    } else {
      nodeIds.add(node.id);
      nodeMap.set(node.id, { index: i, node });
    }

    // 节点类型合法性校验
    if (!node.type || !validNodeTypes.has(node.type)) {
      issues.push({
        level: 'warning',
        code: 'UNKNOWN_NODE_TYPE',
        message: `节点 "${node.id || i}" 的类型 "${node.type}" 不在标准类型列表中，可能导致兼容性问题`,
        target: node.id || nodeRef
      });
      healthScore -= 5;
    }

    // 起始节点与结束节点唯一性检查
    if (node.type === 'start' || node.type === 'end') {
      const sameTypeCount = nodes.filter(n => n.type === node.type).length;
      if (sameTypeCount > 1) {
        issues.push({
          level: 'warning',
          code: `MULTIPLE_${node.type.toUpperCase()}_NODES`,
          message: `存在 ${sameTypeCount} 个 "${node.type}" 类型节点，建议仅保留一个`,
          target: node.id
        });
        healthScore -= 3;
      }
    }

    // 输入输出连接检查
    if (node.inputs && Array.isArray(node.inputs)) {
      for (const input of node.inputs) {
        if (input.source && !nodeMap.has(input.source) && !nodeIds.has(input.source)) {
          issues.push({
            level: 'error',
            code: 'DANGLING_INPUT_REFERENCE',
            message: `节点 "${node.id}" 引用了不存在的上游节点: "${input.source}"`,
            target: node.id
          });
          healthScore -= 8;
        }
      }
    }
  }

  // ---- 循环依赖检测 (DFS) ----
  const visited = new Set();
  const recursionStack = new Set();

  function hasCycle(nodeId, path) {
    visited.add(nodeId);
    recursionStack.add(nodeId);
    const nodeData = nodeMap.get(nodeId);
    if (!nodeData) return false;

    const node = nodeData.node;
    if (node.inputs && Array.isArray(node.inputs)) {
      for (const input of node.inputs) {
        const sourceId = input.source;
        if (!sourceId) continue;
        if (!visited.has(sourceId)) {
          if (hasCycle(sourceId, path.concat(sourceId))) return true;
        } else if (recursionStack.has(sourceId)) {
          issues.push({
            level: 'error',
            code: 'CIRCULAR_DEPENDENCY',
            message: `检测到循环依赖: ${path.concat(sourceId).join(' -> ')}`,
            target: nodeId
          });
          healthScore -= 20;
          return true;
        }
      }
    }
    recursionStack.delete(nodeId);
    return false;
  }

  for (const id of nodeIds) {
    if (!visited.has(id)) {
      hasCycle(id, [id]);
    }
  }

  // ---- 孤立节点检测 ----
  const referencedIds = new Set();
  for (const id of nodeIds) {
    const nodeData = nodeMap.get(id);
    if (nodeData && nodeData.node.inputs) {
      for (const input of nodeData.node.inputs) {
        if (input.source) referencedIds.add(input.source);
      }
    }
    if (nodeData && nodeData.node.outputs) {
      for (const output of nodeData.node.outputs) {
        if (output.target) referencedIds.add(output.target);
      }
    }
  }

  for (const id of nodeIds) {
    const nodeData = nodeMap.get(id);
    if (nodeData && nodeData.node.type !== 'start' && nodeData.node.type !== 'end') {
      if (!referencedIds.has(id)) {
        issues.push({
          level: 'warning',
          code: 'ORPHAN_NODE',
          message: `节点 "${id}" 为孤立节点，没有任何其他节点引用它`,
          target: id
        });
        healthScore -= 4;
      }
    }
  }

  // ---- 生成优化建议 ----
  if (nodes.length > 50) {
    suggestions.push({
      code: 'LARGE_WORKFLOW',
      message: `工作流包含 ${nodes.length} 个节点，建议拆分为子工作流以提升可维护性`,
      priority: 'medium'
    });
  }

  if (issues.filter(i => i.level === 'error').length === 0) {
    suggestions.push({
      code: 'HEALTHY_WORKFLOW',
      message: '当前工作流未发现错误，建议定期运行诊断以保持健康状态',
      priority: 'low'
    });
  }

  // 建议为每个节点添加描述
  const missingDescCount = nodes.filter(n => !n.description).length;
  if (missingDescCount > 0) {
    suggestions.push({
      code: 'MISSING_DESCRIPTIONS',
      message: `有 ${missingDescCount} 个节点缺少描述信息，建议补充以提高可读性`,
      priority: 'low'
    });
  }

  // ---- 最终评分归一化 ----
  healthScore = Math.max(0, Math.min(100, Math.round(healthScore)));

  return {
    health_score: healthScore,
    issues: issues,
    suggestions: suggestions
  };
}

/**
 * 自动修复工作流配置中的已知问题
 * 
 * 功能说明:
 *   基于诊断结果，自动执行一系列安全的修复操作，包括去除孤立节点、
 *   修复断裂的连接引用、规范化节点类型名称、补充缺失的默认参数等。
 *   原始配置不会被修改，返回一个全新的修复后副本。
 * 
 * @param {object} config - 原始工作流配置对象
 * @returns {object} - 修复结果
 *   @returns {object} fixed - 修复后的工作流配置
 *   @returns {Array} fixes - 已执行的修复操作列表
 */
function autoFixWorkflow(config) {
  // ---- 安全校验层 ----
  const safeConfig = validateObject(config, 'config');
  const originalNodes = validateArray(safeConfig.nodes, 'config.nodes');

  // ---- 深度克隆，确保不修改原始数据 ----
  const fixedConfig = deepClone(safeConfig);
  const fixes = [];

  if (!Array.isArray(fixedConfig.nodes)) {
    fixedConfig.nodes = [];
  }

  const nodeMap = new Map();
  const validNodeTypes = new Set([
    'start', 'end', 'llm', 'code', 'condition', 'http',
    'knowledge', 'variable', 'loop', 'delay', 'plugin'
  ]);
  const typeAliases = {
    'begin': 'start',
    'finish': 'end',
    'ai': 'llm',
    'if': 'condition',
    'api': 'http',
    'kb': 'knowledge',
    'var': 'variable',
    'for': 'loop',
    'wait': 'delay'
  };

  // ---- 第一步: 规范化节点 ID 和类型 ----
  const seenIds = new Set();
  for (let i = 0; i < fixedConfig.nodes.length; i++) {
    const node = fixedConfig.nodes[i];
    if (!node || typeof node !== 'object') {
      fixes.push({
        type: 'remove',
        target: `nodes[${i}]`,
        reason: '节点不是有效对象，已移除',
        original: node
      });
      fixedConfig.nodes.splice(i, 1);
      i--;
      continue;
    }

    // 修复缺失的 ID
    if (!node.id || typeof node.id !== 'string') {
      const newId = `node_auto_${Date.now()}_${i}`;
      fixes.push({
        type: 'assign',
        target: `nodes[${i}].id`,
        reason: '节点缺少有效 ID，已自动分配',
        original: node.id,
        current: newId
      });
      node.id = newId;
    }

    // 处理重复 ID
    if (seenIds.has(node.id)) {
      const oldId = node.id;
      node.id = `${node.id}_dup_${Date.now()}_${i}`;
      fixes.push({
        type: 'rename',
        target: oldId,
        reason: `检测到重复 ID，已重命名为 "${node.id}"`,
        original: oldId,
        current: node.id
      });
    }
    seenIds.add(node.id);
    nodeMap.set(node.id, { index: i, node });

    // 规范化节点类型
    if (node.type && typeAliases[node.type.toLowerCase()]) {
      const originalType = node.type;
      node.type = typeAliases[node.type.toLowerCase()];
      fixes.push({
        type: 'normalize',
        target: node.id,
        reason: `节点类型别名 "${originalType}" 已标准化为 "${node.type}"`,
        original: originalType,
        current: node.type
      });
    }

    // 标记非法类型
    if (node.type && !validNodeTypes.has(node.type)) {
      fixes.push({
        type: 'warn',
        target: node.id,
        reason: `节点类型 "${node.type}" 不在标准列表中，未自动修改以避免破坏业务逻辑`,
        original: node.type,
        current: node.type
      });
    }
  }

  // ---- 第二步: 修复断裂的输入连接 ----
  for (let i = 0; i < fixedConfig.nodes.length; i++) {
    const node = fixedConfig.nodes[i];
    if (!node.inputs || !Array.isArray(node.inputs)) {
      node.inputs = [];
      fixes.push({
        type: 'assign',
        target: `${node.id}.inputs`,
        reason: '节点缺少 inputs 数组，已初始化为空数组',
        original: node.inputs,
        current: []
      });
      continue;
    }

    for (let j = node.inputs.length - 1; j >= 0; j--) {
      const input = node.inputs[j];
      if (!input || typeof input !== 'object') {
        fixes.push({
          type: 'remove',
          target: `${node.id}.inputs[${j}]`,
          reason: '输入项不是有效对象，已移除',
          original: input
        });
        node.inputs.splice(j, 1);
        continue;
      }

      if (input.source && !nodeMap.has(input.source)) {
        fixes.push({
          type: 'remove',
          target: `${node.id}.inputs[${j}]`,
          reason: `引用了不存在的上游节点 "${input.source}"，已移除该输入连接`,
          original: input.source,
          current: null
        });
        node.inputs.splice(j, 1);
      }
    }
  }

  // ---- 第三步: 移除孤立节点（保留 start 和 end） ----
  const referencedIds = new Set();
  for (const node of fixedConfig.nodes) {
    if (node.inputs) {
      for (const input of node.inputs) {
        if (input.source) referencedIds.add(input.source);
      }
    }
    if (node.outputs) {
      for (const output of node.outputs) {
        if (output.target) referencedIds.add(output.target);
      }
    }
  }

  for (let i = fixedConfig.nodes.length - 1; i >= 0; i--) {
    const node = fixedConfig.nodes[i];
    if (node.type !== 'start' && node.type !== 'end' && !referencedIds.has(node.id)) {
      fixes.push({
        type: 'remove',
        target: node.id,
        reason: '孤立节点（无任何连接），已自动移除',
        original: node.id
      });
      fixedConfig.nodes.splice(i, 1);
    }
  }

  // ---- 第四步: 确保存在 start 和 end 节点 ----
  const hasStart = fixedConfig.nodes.some(n => n.type === 'start');
  const hasEnd = fixedConfig.nodes.some(n => n.type === 'end');

  if (!hasStart) {
    const startNode = {
      id: 'start_auto',
      type: 'start',
      description: '自动生成的起始节点',
      outputs: []
    };
    fixedConfig.nodes.unshift(startNode);
    fixes.push({
      type: 'insert',
      target: 'start_auto',
      reason: '工作流缺少 start 节点，已自动插入',
      original: null,
      current: startNode
    });
  }

  if (!hasEnd) {
    const endNode = {
      id: 'end_auto',
      type: 'end',
      description: '自动生成的结束节点',
      inputs: []
    };
    fixedConfig.nodes.push(endNode);
    fixes.push({
      type: 'insert',
      target: 'end_auto',
      reason: '工作流缺少 end 节点，已自动插入',
      original: null,
      current: endNode
    });
  }

  return {
    fixed: fixedConfig,
    fixes: fixes
  };
}

/**
 * 生成工作流诊断与修复的报告文本
 * 
 * 功能说明:
 *   将诊断结果和修复记录格式化为人类可读的文本报告，
 *   支持 Markdown 风格排版，便于存档或展示。
 * 
 * @param {string} workflowName - 工作流名称
 * @param {object} diagnosis - 诊断结果对象 (由 diagnoseWorkflow 返回)
 * @param {Array} fixes - 修复操作列表 (由 autoFixWorkflow 返回)
 * @returns {string} - 格式化的报告文本
 */
function generateReport(workflowName, diagnosis, fixes) {
  // ---- 安全校验层 ----
  const safeWorkflowName = validateString(workflowName, 'workflowName', 200);
  const safeDiagnosis = validateObject(diagnosis, 'diagnosis');
  const safeFixes = validateArray(fixes, 'fixes');

  const healthScore = validateNumber(safeDiagnosis.health_score, 'diagnosis.health_score', 0, 100);
  const issues = validateArray(safeDiagnosis.issues || [], 'diagnosis.issues');
  const suggestions = validateArray(safeDiagnosis.suggestions || [], 'diagnosis.suggestions');

  // ---- 构建报告 ----
  const lines = [];
  lines.push(`# 工作流诊断与修复报告`);
  lines.push(`## 基本信息`);
  lines.push(`- **工作流名称**: ${escapeHtml(safeWorkflowName)}`);
  lines.push(`- **生成时间**: ${new Date().toISOString()}`);
  lines.push(`- **健康评分**: ${healthScore}/100`);
  lines.push('');

  // 评分可视化
  const barLength = 20;
  const filled = Math.round((healthScore / 100) * barLength);
  const empty = barLength - filled;
  const bar = '█'.repeat(filled) + '░'.repeat(empty);
  lines.push(`评分可视化: [${bar}] ${healthScore}%`);
  lines.push('');

  // 问题汇总
  lines.push(`## 问题汇总 (${issues.length} 项)`);
  if (issues.length === 0) {
    lines.push('未发现任何问题，工作流状态良好。');
  } else {
    const errorCount = issues.filter(i => i.level === 'error').length;
    const warningCount = issues.filter(i => i.level === 'warning').length;
    lines.push(`- 错误: ${errorCount} 项`);
    lines.push(`- 警告: ${warningCount} 项`);
    lines.push('');
    for (let i = 0; i < issues.length; i++) {
      const issue = issues[i];
      const icon = issue.level === 'error' ? '❌' : '⚠️';
      lines.push(`${icon} **${issue.code}** (目标: ${escapeHtml(String(issue.target || 'N/A'))})`);
      lines.push(`   ${escapeHtml(String(issue.message))}`);
    }
  }
  lines.push('');

  // 修复记录
  lines.push(`## 自动修复记录 (${safeFixes.length} 项)`);
  if (safeFixes.length === 0) {
    lines.push('未执行任何自动修复操作。');
  } else {
    for (let i = 0; i < safeFixes.length; i++) {
      const fix = safeFixes[i];
      lines.push(`${i + 1}. **[${fix.type.toUpperCase()}]** 目标: \`${escapeHtml(String(fix.target))}\``);
      lines.push(`   原因: ${escapeHtml(String(fix.reason))}`);
      if (fix.original !== undefined) {
        lines.push(`   原值: \`${escapeHtml(JSON.stringify(fix.original).slice(0, 100))}\``);
      }
      if (fix.current !== undefined) {
        lines.push(`   新值: \`${escapeHtml(JSON.stringify(fix.current).slice(0, 100))}\``);
      }
    }
  }
  lines.push('');

  // 优化建议
  lines.push(`## 优化建议 (${suggestions.length} 项)`);
  if (suggestions.length === 0) {
    lines.push('暂无额外建议。');
  } else {
    for (const suggestion of suggestions) {
      const priorityIcon = suggestion.priority === 'high' ? '🔴' : suggestion.priority === 'medium' ? '🟡' : '🟢';
      lines.push(`${priorityIcon} **${suggestion.code}** (优先级: ${suggestion.priority || 'low'})`);
      lines.push(`   ${escapeHtml(String(suggestion.message))}`);
    }
  }
  lines.push('');

  // 页脚
  lines.push('---');
  lines.push(`*报告由 Coze 工作流全自动安全修复引擎生成*`);

  return lines.join('\n');
}

// ============================================================================
// 核心功能层 - 错误分类与工作流修复
// ============================================================================

/**
 * 错误分类器 - 分析错误信息并输出修复策略
 * 
 * 功能说明:
 *   接收包含错误消息和错误代码的输入，基于内置的错误模式库，
 *   自动判定目标模块、选择修复策略、给出建议操作。
 * 
 * @param {object} inp - 输入对象
 * @param {string} inp.error_message - 错误消息文本
 * @param {string} inp.error_code - 错误代码
 * @returns {object} - 分类结果
 *   @returns {string} target_module - 目标模块标识
 *   @returns {string} repair_strategy - 修复策略代码
 *   @returns {string} original_error_code - 原始错误代码
 *   @returns {string} suggested_action - 建议执行的操作描述
 */
function errorClassifier(inp) {
  // ---- 安全校验层 ----
  const safeInput = validateObject(inp, 'inp');
  const errorMessage = validateString(safeInput.error_message || safeInput.errorMessage || '', 'inp.error_message', 5000);
  const errorCode = validateString(safeInput.error_code || safeInput.errorCode || 'UNKNOWN', 'inp.error_code', 100);

  // ---- 错误模式库 ----
  const patterns = [
    {
      module: 'llm',
      codes: ['LLM_TIMEOUT', 'LLM_RATE_LIMIT', 'TOKEN_EXCEEDED', 'MODEL_NOT_FOUND'],
      keywords: ['timeout', 'rate limit', 'token', 'model', 'llm', 'gpt', 'claude'],
      strategy: 'retry_with_backoff',
      action: '增加重试次数并启用指数退避策略，或切换至备用大模型节点'
    },
    {
      module: 'http',
      codes: ['HTTP_404', 'HTTP_500', 'HTTP_503', 'CONNECTION_REFUSED', 'DNS_ERROR'],
      keywords: ['http', 'connection', 'refused', 'timeout', 'dns', '404', '500', '503'],
      strategy: 'fallback_endpoint',
      action: '检查 API 地址与鉴权配置，启用备用端点或增加超时时间'
    },
    {
      module: 'knowledge',
      codes: ['KB_NOT_FOUND', 'KB_SEARCH_EMPTY', 'CHUNK_ERROR', 'EMBEDDING_FAIL'],
      keywords: ['knowledge', 'kb', 'chunk', 'embedding', 'vector', 'search'],
      strategy: 'reindex_and_retry',
      action: '重新索引知识库文档，检查分块大小与重叠参数设置'
    },
    {
      module: 'code',
      codes: ['CODE_EXEC_ERROR', 'SYNTAX_ERROR', 'IMPORT_ERROR', 'TIMEOUT'],
      keywords: ['syntax', 'import', 'undefined', 'reference', 'exception', 'traceback'],
      strategy: 'sanitize_and_retry',
      action: '审查代码节点的语法与依赖，限制执行时长并增加输入校验'
    },
    {
      module: 'variable',
      codes: ['VAR_NOT_FOUND', 'TYPE_MISMATCH', 'NULL_REFERENCE'],
      keywords: ['variable', 'undefined', 'null', 'type', 'reference', 'missing'],
      strategy: 'inject_defaults',
      action: '为缺失的变量注入默认值，或在流程上游增加非空校验节点'
    },
    {
      module: 'condition',
      codes: ['COND_EVAL_FAIL', 'BOOLEAN_PARSE_ERROR'],
      keywords: ['condition', 'boolean', 'eval', 'expression', 'if'],
      strategy: 'rewrite_expression',
      action: '简化条件表达式，使用显式布尔转换并增加边界测试'
    },
    {
      module: 'workflow',
      codes: ['CYCLE_DETECTED', 'ORPHAN_NODE', 'MISSING_START', 'MISSING_END'],
      keywords: ['cycle', 'orphan', 'workflow', 'start', 'end', 'node'],
      strategy: 'structural_repair',
      action: '运行 autoFixWorkflow 进行结构修复，消除循环依赖与孤立节点'
    }
  ];

  // ---- 匹配逻辑 ----
  let bestMatch = {
    target_module: 'unknown',
    repair_strategy: 'manual_review',
    original_error_code: errorCode,
    suggested_action: '未识别到已知错误模式，建议人工审查日志并联系技术支持'
  };

  const lowerMessage = errorMessage.toLowerCase();
  const lowerCode = errorCode.toLowerCase();
  let maxScore = 0;

  for (const pattern of patterns) {
    let score = 0;

    // 代码完全匹配
    if (pattern.codes.some(c => c.toLowerCase() === lowerCode)) {
      score += 100;
    }

    // 代码前缀匹配
    if (pattern.codes.some(c => lowerCode.startsWith(c.toLowerCase()))) {
      score += 50;
    }

    // 关键词匹配
    for (const keyword of pattern.keywords) {
      if (lowerMessage.includes(keyword.toLowerCase())) {
        score += 10;
      }
    }

    if (score > maxScore) {
      maxScore = score;
      bestMatch = {
        target_module: pattern.module,
        repair_strategy: pattern.strategy,
        original_error_code: errorCode,
        suggested_action: pattern.action
      };
    }
  }

  return bestMatch;
}

/**
 * 工作流修复器 - 基于 JSON 字符串修复工作流结构
 * 
 * 功能说明:
 *   接收工作流的 JSON 字符串表示，尝试解析并自动修复其中
 *   的结构性问题，返回修复后的工作流对象与状态标识。
 * 
 * @param {object} inp - 输入对象
 * @param {string} inp.workflow_json_str - 工作流配置的 JSON 字符串
 * @returns {object} - 修复结果
 *   @returns {object} repaired_workflow - 修复后的工作流对象
 *   @returns {string} status - 修复状态 (success | partial | failed)
 */
function workflowRepairer(inp) {
  // ---- 安全校验层 ----
  const safeInput = validateObject(inp, 'inp');
  const jsonStr = validateString(safeInput.workflow_json_str || safeInput.workflowJsonStr || '', 'inp.workflow_json_str', 100000);

  if (!jsonStr.trim()) {
    return {
      repaired_workflow: { nodes: [], edges: [] },
      status: 'failed'
    };
  }

  // ---- 解析 JSON ----
  let workflow;
  try {
    workflow = JSON.parse(jsonStr);
  } catch (parseError) {
    // 尝试常见 JSON 修复
    let repairedStr = jsonStr;
    // 修复尾随逗号
    repairedStr = repairedStr.replace(/,(\s*[}\]])/g, '$1');
    // 修复单引号
    repairedStr = repairedStr.replace(/'/g, '"');
    // 修复未加引号的键
    repairedStr = repairedStr.replace(/([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:/g, '$1"$2":');

    try {
      workflow = JSON.parse(repairedStr);
    } catch (secondError) {
      return {
        repaired_workflow: { raw: jsonStr.slice(0, 500), parse_error: parseError.message },
        status: 'failed'
      };
    }
  }

  // ---- 结构修复 ----
  if (!workflow || typeof workflow !== 'object') {
    return {
      repaired_workflow: { nodes: [], edges: [] },
      status: 'failed'
    };
  }

  if (!Array.isArray(workflow.nodes)) {
    workflow.nodes = [];
  }

  // 运行自动修复以规范化结构
  const repairResult = autoFixWorkflow(workflow);
  const status = repairResult.fixes.length > 0 ? 'partial' : 'success';

  return {
    repaired_workflow: repairResult.fixed,
    status: status
  };
}

// ============================================================================
// 核心功能层 - 知识库与卡片工具
// ============================================================================

/**
 * 知识库文本分块工具
 * 
 * 功能说明:
 *   将长文档按指定大小切分为重叠的文本块，便于向量化存储与检索。
 *   支持智能边界检测（优先在句号、换行处切断），避免切断语义单元。
 * 
 * @param {object} inp - 输入对象
 * @param {string} inp.document_text - 待分块的原始文档文本
 * @param {number} [inp.chunk_size=500] - 每个块的最大字符数
 * @param {number} [inp.overlap=50] - 相邻块之间的重叠字符数
 * @returns {object} - 分块结果
 *   @returns {Array} chunks - 文本块数组
 *   @returns {number} chunk_count - 块的总数量
 *   @returns {string} status - 处理状态 (success | empty | error)
 */
function knowledgeRechunk(inp) {
  // ---- 安全校验层 ----
  const safeInput = validateObject(inp, 'inp');
  const documentText = validateString(safeInput.document_text || safeInput.documentText || '', 'inp.document_text', 500000);
  const chunkSize = validateNumber(safeInput.chunk_size || safeInput.chunkSize || 500, 'inp.chunk_size', 100, 10000);
  const overlap = validateNumber(safeInput.overlap || safeInput.overlap || 50, 'inp.overlap', 0, chunkSize - 1);

  // ---- 空内容快速返回 ----
  if (!documentText.trim()) {
    return {
      chunks: [],
      chunk_count: 0,
      status: 'empty'
    };
  }

  // ---- 智能分块算法 ----
  const chunks = [];
  const text = documentText;
  const step = chunkSize - overlap;
  let startIndex = 0;

  while (startIndex < text.length) {
    let endIndex = Math.min(startIndex + chunkSize, text.length);

    // 如果不是最后一块，尝试在最近的语义边界处切断
    if (endIndex < text.length) {
      // 优先找句号、问号、感叹号后的空格或换行
      const boundarySearch = text.slice(startIndex, endIndex + 1);
      const match = boundarySearch.match(/[.!?。！？\n](?:\s|\n|$)/);
      if (match && match.index !== undefined) {
        const candidateEnd = startIndex + match.index + 1;
        if (candidateEnd > startIndex + chunkSize * 0.5) {
          endIndex = candidateEnd;
        }
      } else {
        // 退而求其次，找空格或换行
        const lastSpace = boundarySearch.lastIndexOf(' ');
        const lastNewline = boundarySearch.lastIndexOf('\n');
        const boundaryPos = Math.max(lastSpace, lastNewline);
        if (boundaryPos > chunkSize * 0.5) {
          endIndex = startIndex + boundaryPos;
        }
      }
    }

    const chunk = text.slice(startIndex, endIndex).trim();
    if (chunk) {
      chunks.push({
        index: chunks.length,
        text: chunk,
        start: startIndex,
        end: endIndex,
        length: chunk.length
      });
    }

    startIndex += Math.max(step, 1);
    // 防止死循环: 确保至少前进一个字符
    if (endIndex <= startIndex) {
      startIndex = endIndex;
    }
  }

  return {
    chunks: chunks,
    chunk_count: chunks.length,
    status: 'success'
  };
}

/**
 * 卡片变量填充器
 * 
 * 功能说明:
 *   解析卡片模板中的变量占位符（如 {{variable_name}}），
 *   对比用户提供的变量，自动识别缺失项、填充默认值、
 *   并生成最终渲染预览。
 * 
 * @param {object} inp - 输入对象
 * @param {string} inp.card_template - 卡片模板字符串，包含 {{var}} 占位符
 * @param {object} inp.provided_vars - 用户提供的变量键值对
 * @returns {object} - 填充结果
 *   @returns {Array} missing_variables - 缺失的变量名列表
 *   @returns {object} auto_filled_values - 自动填充的变量值
 *   @returns {object} final_variables - 所有最终变量（含用户提供和自动填充）
 *   @returns {string} rendered_preview - 渲染后的预览文本
 */
function cardVariableFiller(inp) {
  // ---- 安全校验层 ----
  const safeInput = validateObject(inp, 'inp');
  const cardTemplate = validateString(safeInput.card_template || safeInput.cardTemplate || '', 'inp.card_template', 50000);
  const providedVars = validateObject(safeInput.provided_vars || safeInput.providedVars || {}, 'inp.provided_vars');

  // ---- 提取模板变量 ----
  // 匹配 {{variable_name}} 或 {{{variable_name}}} 格式
  const variableRegex = /\{\{?\{?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}?\}?\}/g;
  const requiredVars = new Set();
  let match;

  while ((match = variableRegex.exec(cardTemplate)) !== null) {
    requiredVars.add(match[1]);
  }

  // ---- 默认值库 ----
  const defaultValues = {
    'user_name': '用户',
    'bot_name': 'AI助手',
    'date': new Date().toISOString().split('T')[0],
    'time': new Date().toTimeString().split(' ')[0],
    'datetime': new Date().toISOString(),
    'company': '贵公司',
    'email': 'example@example.com',
    'phone': '138****8888',
    'greeting': '您好',
    'farewell': '祝您生活愉快',
    'status': '处理中',
    'priority': '普通',
    'score': '0',
    'count': '0',
    'url': 'https://example.com',
    'image_url': 'https://via.placeholder.com/400x200'
  };

  // ---- 对比与填充 ----
  const missingVariables = [];
  const autoFilledValues = {};
  const finalVariables = {};

  for (const varName of requiredVars) {
    if (providedVars[varName] !== undefined && providedVars[varName] !== null && providedVars[varName] !== '') {
      finalVariables[varName] = String(providedVars[varName]);
    } else if (defaultValues[varName] !== undefined) {
      autoFilledValues[varName] = defaultValues[varName];
      finalVariables[varName] = defaultValues[varName];
    } else {
      missingVariables.push(varName);
      finalVariables[varName] = `{{${varName}}}`; // 保留占位符
    }
  }

  // ---- 渲染预览 ----
  let renderedPreview = cardTemplate;
  for (const varName of requiredVars) {
    const regex = new RegExp(`\\{\\{?\\{?\\s*${varName}\\s*\\}?\\}?\\}`, 'g');
    renderedPreview = renderedPreview.replace(regex, escapeHtml(String(finalVariables[varName] || '')));
  }

  return {
    missing_variables: missingVariables,
    auto_filled_values: autoFilledValues,
    final_variables: finalVariables,
    rendered_preview: renderedPreview
  };
}

// ============================================================================
// 元数据定义层 (JSON Schema)
// ============================================================================

/**
 * 函数元数据注册表
 * 每个条目包含: input_schema, output_schema, description, version
 */
const metadataRegistry = {
  diagnoseWorkflow: {
    version: '1.0.0',
    description: '诊断工作流配置的健康状况，返回健康评分、问题列表与优化建议',
    input_schema: {
      type: 'object',
      required: ['config'],
      properties: {
        config: {
          type: 'object',
          required: ['nodes'],
          description: '工作流配置对象',
          properties: {
            nodes: {
              type: 'array',
              description: '工作流节点数组',
              items: {
                type: 'object',
                required: ['id', 'type'],
                properties: {
                  id: { type: 'string', description: '节点唯一标识符', minLength: 1, maxLength: 128 },
                  type: { type: 'string', description: '节点类型', enum: ['start', 'end', 'llm', 'code', 'condition', 'http', 'knowledge', 'variable', 'loop', 'delay', 'plugin'] },
                  description: { type: 'string', description: '节点描述', maxLength: 500 },
                  inputs: {
                    type: 'array',
                    description: '输入连接列表',
                    items: {
                      type: 'object',
                      properties: {
                        source: { type: 'string', description: '上游节点 ID' },
                        target_field: { type: 'string', description: '目标字段名' }
                      }
                    }
                  },
                  outputs: {
                    type: 'array',
                    description: '输出连接列表',
                    items: {
                      type: 'object',
                      properties: {
                        target: { type: 'string', description: '下游节点 ID' },
                        source_field: { type: 'string', description: '源字段名' }
                      }
                    }
                  },
                  params: { type: 'object', description: '节点特定参数' }
                }
              }
            }
          }
        }
      }
    },
    output_schema: {
      type: 'object',
      required: ['health_score', 'issues', 'suggestions'],
      properties: {
        health_score: {
          type: 'number',
          description: '工作流健康评分，范围为 0 到 100',
          minimum: 0,
          maximum: 100
        },
        issues: {
          type: 'array',
          description: '发现的问题列表',
          items: {
            type: 'object',
            properties: {
              level: { type: 'string', enum: ['error', 'warning'], description: '问题严重程度' },
              code: { type: 'string', description: '问题错误码' },
              message: { type: 'string', description: '问题描述' },
              target: { type: 'string', description: '问题目标节点或位置' }
            }
          }
        },
        suggestions: {
          type: 'array',
          description: '优化建议列表',
          items: {
            type: 'object',
            properties: {
              code: { type: 'string', description: '建议编码' },
              message: { type: 'string', description: '建议内容' },
              priority: { type: 'string', enum: ['high', 'medium', 'low'], description: '优先级' }
            }
          }
        }
      }
    }
  },

  autoFixWorkflow: {
    version: '1.0.0',
    description: '自动修复工作流配置中的已知问题，返回修复后的配置与修复记录',
    input_schema: {
      type: 'object',
      required: ['config'],
      properties: {
        config: {
          type: 'object',
          required: ['nodes'],
          description: '原始工作流配置对象',
          properties: {
            nodes: {
              type: 'array',
              description: '工作流节点数组'
            }
          }
        }
      }
    },
    output_schema: {
      type: 'object',
      required: ['fixed', 'fixes'],
      properties: {
        fixed: {
          type: 'object',
          description: '修复后的工作流配置对象'
        },
        fixes: {
          type: 'array',
          description: '已执行的修复操作列表',
          items: {
            type: 'object',
            properties: {
              type: { type: 'string', enum: ['remove', 'assign', 'rename', 'normalize', 'warn', 'insert'], description: '修复类型' },
              target: { type: 'string', description: '修复目标标识' },
              reason: { type: 'string', description: '修复原因' },
              original: { description: '原始值（任意类型）' },
              current: { description: '当前值（任意类型）' }
            }
          }
        }
      }
    }
  },

  generateReport: {
    version: '1.0.0',
    description: '将诊断结果和修复记录格式化为人类可读的文本报告',
    input_schema: {
      type: 'object',
      required: ['workflowName', 'diagnosis', 'fixes'],
      properties: {
        workflowName: {
          type: 'string',
          description: '工作流名称',
          minLength: 1,
          maxLength: 200
        },
        diagnosis: {
          type: 'object',
          description: '诊断结果对象（由 diagnoseWorkflow 返回）',
          required: ['health_score', 'issues', 'suggestions'],
          properties: {
            health_score: { type: 'number', minimum: 0, maximum: 100 },
            issues: { type: 'array' },
            suggestions: { type: 'array' }
          }
        },
        fixes: {
          type: 'array',
          description: '修复操作列表（由 autoFixWorkflow 返回）'
        }
      }
    },
    output_schema: {
      type: 'string',
      description: '格式化的 Markdown 风格报告文本'
    }
  },

  errorClassifier: {
    version: '1.0.0',
    description: '分析错误信息并输出目标模块、修复策略与建议操作',
    input_schema: {
      type: 'object',
      required: ['error_message', 'error_code'],
      properties: {
        error_message: {
          type: 'string',
          description: '错误消息文本',
          maxLength: 5000
        },
        error_code: {
          type: 'string',
          description: '错误代码',
          maxLength: 100
        }
      }
    },
    output_schema: {
      type: 'object',
      required: ['target_module', 'repair_strategy', 'original_error_code', 'suggested_action'],
      properties: {
        target_module: {
          type: 'string',
          description: '目标模块标识，如 llm, http, knowledge, code 等'
        },
        repair_strategy: {
          type: 'string',
          description: '修复策略代码，如 retry_with_backoff, fallback_endpoint 等'
        },
        original_error_code: {
          type: 'string',
          description: '原始错误代码'
        },
        suggested_action: {
          type: 'string',
          description: '建议执行的操作描述'
        }
      }
    }
  },

  workflowRepairer: {
    version: '1.0.0',
    description: '基于 JSON 字符串解析并修复工作流结构问题',
    input_schema: {
      type: 'object',
      required: ['workflow_json_str'],
      properties: {
        workflow_json_str: {
          type: 'string',
          description: '工作流配置的 JSON 字符串',
          maxLength: 100000
        }
      }
    },
    output_schema: {
      type: 'object',
      required: ['repaired_workflow', 'status'],
      properties: {
        repaired_workflow: {
          type: 'object',
          description: '修复后的工作流对象'
        },
        status: {
          type: 'string',
          enum: ['success', 'partial', 'failed'],
          description: '修复状态：成功、部分修复或失败'
        }
      }
    }
  },

  knowledgeRechunk: {
    version: '1.0.0',
    description: '将长文档按指定大小切分为重叠的文本块，便于向量化存储与检索',
    input_schema: {
      type: 'object',
      required: ['document_text'],
      properties: {
        document_text: {
          type: 'string',
          description: '待分块的原始文档文本',
          maxLength: 500000
        },
        chunk_size: {
          type: 'number',
          description: '每个块的最大字符数，默认 500',
          default: 500,
          minimum: 100,
          maximum: 10000
        },
        overlap: {
          type: 'number',
          description: '相邻块之间的重叠字符数，默认 50',
          default: 50,
          minimum: 0
        }
      }
    },
    output_schema: {
      type: 'object',
      required: ['chunks', 'chunk_count', 'status'],
      properties: {
        chunks: {
          type: 'array',
          description: '文本块数组',
          items: {
            type: 'object',
            properties: {
              index: { type: 'number', description: '块序号' },
              text: { type: 'string', description: '块文本内容' },
              start: { type: 'number', description: '起始字符索引' },
              end: { type: 'number', description: '结束字符索引' },
              length: { type: 'number', description: '块长度' }
            }
          }
        },
        chunk_count: {
          type: 'number',
          description: '块的总数量'
        },
        status: {
          type: 'string',
          enum: ['success', 'empty', 'error'],
          description: '处理状态'
        }
      }
    }
  },

  cardVariableFiller: {
    version: '1.0.0',
    description: '解析卡片模板变量，识别缺失项、填充默认值并生成渲染预览',
    input_schema: {
      type: 'object',
      required: ['card_template', 'provided_vars'],
      properties: {
        card_template: {
          type: 'string',
          description: '卡片模板字符串，包含 {{var}} 占位符',
          maxLength: 50000
        },
        provided_vars: {
          type: 'object',
          description: '用户提供的变量键值对',
          additionalProperties: { type: 'string' }
        }
      }
    },
    output_schema: {
      type: 'object',
      required: ['missing_variables', 'auto_filled_values', 'final_variables', 'rendered_preview'],
      properties: {
        missing_variables: {
          type: 'array',
          description: '缺失的变量名列表',
          items: { type: 'string' }
        },
        auto_filled_values: {
          type: 'object',
          description: '自动填充的变量值'
        },
        final_variables: {
          type: 'object',
          description: '所有最终变量（含用户提供和自动填充）'
        },
        rendered_preview: {
          type: 'string',
          description: '渲染后的预览文本'
        }
      }
    }
  }
};

// ============================================================================
// 统一调用入口与工具函数
// ============================================================================

/**
 * 根据函数名称和输入执行对应的功能函数
 * 
 * @param {string} functionName - 要调用的函数名
 * @param {object} input - 输入参数对象
 * @returns {object} - 函数执行结果
 * @throws {Error} - 函数不存在或执行失败时抛出
 */
function executeFunction(functionName, input) {
  const validFunctions = {
    diagnoseWorkflow,
    autoFixWorkflow,
    generateReport,
    errorClassifier,
    workflowRepairer,
    knowledgeRechunk,
    cardVariableFiller
  };

  if (!validFunctions[functionName]) {
    throw new Error(`未知函数: "${functionName}"。可用的函数: ${Object.keys(validFunctions).join(', ')}`);
  }

  return validFunctions[functionName](input);
}

/**
 * 获取指定函数的 JSON Schema 元数据
 * 
 * @param {string} functionName - 函数名称
 * @returns {object|null} - 元数据对象，若不存在则返回 null
 */
function getFunctionMetadata(functionName) {
  return metadataRegistry[functionName] || null;
}

/**
 * 获取所有可用函数的名称列表
 * 
 * @returns {Array<string>} - 函数名称数组
 */
function listAvailableFunctions() {
  return Object.keys(metadataRegistry);
}

// ============================================================================
// 模块导出 (CommonJS)
// ============================================================================

module.exports = {
  // ---- 核心功能函数 ----
  diagnoseWorkflow,
  autoFixWorkflow,
  generateReport,
  errorClassifier,
  workflowRepairer,
  knowledgeRechunk,
  cardVariableFiller,

  // ---- 元数据注册表 ----
  metadataRegistry,
  getFunctionMetadata,

  // ---- 统一调用接口 ----
  executeFunction,
  listAvailableFunctions,

  // ---- 工具函数（按需导出） ----
  SecurityError,
  deepClone,
  escapeHtml,
  validateObject,
  validateString,
  validateNumber,
  validateArray
};

// ============================================================================
// 本地测试桩（仅在直接运行时执行）
// ============================================================================

if (require.main === module) {
  console.log('Coze 工作流全自动安全修复引擎已加载');
  console.log('可用函数:', listAvailableFunctions().join(', '));

  // 快速健康检查
  const testConfig = {
    nodes: [
      { id: 'start_1', type: 'start', outputs: [{ target: 'llm_1' }] },
      { id: 'llm_1', type: 'llm', inputs: [{ source: 'start_1' }], outputs: [{ target: 'end_1' }] },
      { id: 'end_1', type: 'end', inputs: [{ source: 'llm_1' }] }
    ]
  };

  const diagnosis = diagnoseWorkflow(testConfig);
  console.log('诊断评分:', diagnosis.health_score);
  console.log('发现问题:', diagnosis.issues.length);
  console.log('优化建议:', diagnosis.suggestions.length);
}
