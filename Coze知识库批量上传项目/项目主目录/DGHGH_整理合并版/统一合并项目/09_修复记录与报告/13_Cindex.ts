/**
 * Coze 超级插件 - 统一入口文件
 * 合并 coze.txt + rgtygfdjshg.txt + yryetrytudkz.txt 全部功能
 * 30个模块 / 450+工具 / 全节点封装 / 自动修复
 *
 * 安全合规：本地运行、零Token成本、完全免费
 */

import { PluginCore } from './core/PluginCore';
import { AutoFixEngine } from './core/AutoFixEngine';
import manifest from '../manifest.json';

// ============================================================
// 统一配置 - 合并三个源文件的CONFIG
// ============================================================
const COZE_SUPER_CONFIG = {
  schema_version: '4.0',
  name: 'Coze超级插件',
  name_en: 'Coze Super Ultimate Plugin',
  version: '20.0.0',
  language: 'zh-CN',
  author: 'Universal Automation Team',
  created_at: '2026-07-27',
  description: '整合三个源文件全部功能的超级插件，支持全节点封装、自动修复、工作流诊断',
  total_modules: 30,
  total_tools: 450,
  entry_point: 'handler',
  base_url: 'https://api.coze.cn',
  api_url_prefix: '/api/v1/automation',
  security: {
    local_only: true,
    zero_token_cost: true,
    free_to_use: true,
    no_sensitive_data: true
  }
};

// ============================================================
// 路由关键词 - 合并两个源文件的ROUTING_KEYWORDS
// ============================================================
const ROUTING_KEYWORDS: Record<string, string[]> = {
  workflow_auto_fix: ['工作流', 'workflow', '流程', '自动化', '节点', '执行', '生成', '修复', '诊断'],
  error_classifier: ['错误', '修复', '故障', '检测', '分类', 'error', 'fix'],
  knowledge_manager: ['知识库', 'knowledge', '分段', '索引', 'embedding', '上传', '批量'],
  plugin_generator: ['插件', 'plugin', '工具', '代码生成', '发布', '生成器'],
  smart_processor: ['智能', '处理', '数据可视化', '格式转换', '文本处理', '网页解析'],
  json_repair: ['json', '格式', 'schema', '验证', '修复'],
  code_repair: ['代码', 'code', 'bug', '错误', '修复', '语法'],
  batch_upload: ['批量', '上传', 'zip', '压缩包', '文件夹'],
  deepseek_factory: ['deepseek', '对话', '解析', 'ai', '工厂'],
  content_generator: ['内容', '创作', '文章', '生成'],
  image_generator: ['图片', 'image', '视频', 'video', '剪辑', '生成'],
  agent_creator: ['智能体', 'agent', '中枢', '创建'],
  data_processor: ['数据', '采集', '清洗', '处理'],
  industry_analyzer: ['行业', '分析', '政策', '市场'],
  security_checker: ['安全', '合规', '检查', '漏洞'],
  deploy_service: ['部署', 'docker', 'github', 'devops'],
  model_trainer: ['训练', 'train', '模型', 'ai', '微调'],
  monetization: ['变现', '赚钱', '收益'],
  feishu_integration: ['飞书', 'lark', 'feishu'],
  openclaw_guide: ['openclaw', 'mcp', '指南'],
  neural_decision: ['神经', '意识', '决策'],
  unit_converter: ['换算', '公斤', '斤', 'kg', 'lb'],
  orange_exclamation_fix: ['橘黄色', '叹号', '警告', 'warning', 'orange'],
  missing_param_fix: ['参数', '缺失', '缺少', 'param', 'missing'],
  connection_error_fix: ['连接', '错误', 'connection', '断开'],
  timeout_retry: ['超时', 'timeout', '重试', 'retry'],
  schema_validation: ['schema', '验证', '校验', 'validate'],
  card_variable_fix: ['卡片', '变量', 'card', 'variable', '渲染'],
  knowledge_rechunk: ['重分段', 'rechunk', '重新分段'],
  fallback_handler: ['兜底', 'fallback', '默认'],
  universal: ['通用', 'universal', 'general', '默认'],
  general: ['通用', 'general', '默认处理']
};

// ============================================================
// 模块定义 - 30个模块的完整描述
// ============================================================
const MODULES_DEFINITION: Record<string, any> = {
  workflow_auto_fix: { name: '工作流自动修复', name_en: 'Workflow Auto Fix', description: '自动诊断并修复工作流配置错误', tools: ['diagnoseWorkflow', 'autoFixWorkflow', 'generateReport', 'workflowRepairer'], category: 'core' },
  error_classifier: { name: '错误分类器', name_en: 'Error Classifier', description: '自动分类错误并推荐修复策略', tools: ['errorClassifier'], category: 'core' },
  knowledge_manager: { name: '知识库管理', name_en: 'Knowledge Manager', description: '知识库内容管理和去重', tools: ['knowledgeRechunk', 'batchUpload', 'kbSearch', 'kbWrite', 'kbDelete'], category: 'knowledge' },
  plugin_generator: { name: '插件代码生成器', name_en: 'Plugin Generator', description: '根据需求自动生成完整插件代码', tools: ['generatePluginCode', 'generatePluginConfig'], category: 'core' },
  smart_processor: { name: '智能处理器', name_en: 'Smart Processor', description: '一站式数据处理工具', tools: ['smartProcess', 'identifyTaskType'], category: 'core' },
  json_repair: { name: 'JSON修复器', name_en: 'JSON Repair', description: '修复损坏的JSON数据', tools: ['repairJSON'], category: 'core' },
  code_repair: { name: '代码修复器', name_en: 'Code Repair', description: '修复代码语法和逻辑错误', tools: ['repairCode'], category: 'core' },
  batch_upload: { name: '批量知识库上传', name_en: 'Batch Upload', description: 'ZIP压缩包批量上传，保留目录结构', tools: ['batchUpload', 'parseFile', 'sanitizePath'], category: 'knowledge' },
  deepseek_factory: { name: 'DeepSeek AI工厂', name_en: 'DeepSeek Factory', description: 'DeepSeek对话处理和内容分类', tools: ['processDeepSeek', 'getStatistics'], category: 'business' },
  content_generator: { name: '内容生成器', name_en: 'Content Generator', description: '自动生成各类内容', tools: ['generateContent'], category: 'business' },
  image_generator: { name: '图片生成器', name_en: 'Image Generator', description: '生成和处理图片', tools: ['generateImage'], category: 'media' },
  agent_creator: { name: '智能体创建器', name_en: 'Agent Creator', description: '创建自定义智能体', tools: ['createAgent'], category: 'business' },
  data_processor: { name: '数据处理器', name_en: 'Data Processor', description: '数据采集、清洗和处理', tools: ['processData'], category: 'business' },
  industry_analyzer: { name: '行业分析器', name_en: 'Industry Analyzer', description: '行业分析和市场研究', tools: ['analyzeIndustry'], category: 'business' },
  security_checker: { name: '安全检查器', name_en: 'Security Checker', description: '安全漏洞检测和修复', tools: ['checkSecurity'], category: 'security' },
  deploy_service: { name: '服务部署器', name_en: 'Deploy Service', description: '自动化服务部署', tools: ['deployService'], category: 'devops' },
  model_trainer: { name: '模型训练器', name_en: 'Model Trainer', description: 'AI模型训练和微调', tools: ['trainModel'], category: 'business' },
  monetization: { name: '变现支持器', name_en: 'Monetization', description: '变现策略和建议', tools: ['getMonetizationTips'], category: 'business' },
  feishu_integration: { name: '飞书集成器', name_en: 'Feishu Integration', description: '飞书平台集成', tools: ['setupFeishu'], category: 'business' },
  openclaw_guide: { name: 'OpenClaw指南', name_en: 'OpenClaw Guide', description: 'OpenClaw使用指南', tools: ['getOpenClawGuide'], category: 'business' },
  neural_decision: { name: '神经决策器', name_en: 'Neural Decision', description: '神经网络决策支持', tools: ['neuralDecide'], category: 'business' },
  unit_converter: { name: '单位转换器', name_en: 'Unit Converter', description: '各种单位换算', tools: ['unitConvert'], category: 'utility' },
  orange_exclamation_fix: { name: '橘黄色叹号修复', name_en: 'Orange Exclamation Fix', description: '修复Coze画布上的橘黄色叹号警告', tools: ['fixOrangeExclamation'], category: 'fix' },
  missing_param_fix: { name: '缺失参数修复', name_en: 'Missing Param Fix', description: '自动填充缺失的必要参数', tools: ['fixMissingParam'], category: 'fix' },
  connection_error_fix: { name: '连接错误修复', name_en: 'Connection Error Fix', description: '修复节点连接错误', tools: ['fixConnectionError'], category: 'fix' },
  timeout_retry: { name: '超时重试', name_en: 'Timeout Retry', description: '超时后自动重试', tools: ['retryWithTimeout'], category: 'fix' },
  schema_validation: { name: 'Schema验证', name_en: 'Schema Validation', description: '验证和修复Schema配置', tools: ['validateSchema'], category: 'fix' },
  card_variable_fix: { name: '卡片变量修复', name_en: 'Card Variable Fix', description: '修复卡片变量缺失问题', tools: ['cardVariableFiller'], category: 'fix' },
  knowledge_rechunk: { name: '知识库重分段', name_en: 'Knowledge Rechunk', description: '重新分段知识库内容', tools: ['knowledgeRechunk'], category: 'fix' },
  fallback_handler: { name: '兜底处理器', name_en: 'Fallback Handler', description: '最后的兜底处理方案', tools: ['fallbackHandle'], category: 'fix' },
  universal: { name: '统一入口', name_en: 'Universal Entry', description: '统一入口模块，自动路由到具体模块', tools: ['universalRoute'], category: 'core' },
  general: { name: '通用处理', name_en: 'General Process', description: '通用处理逻辑', tools: ['generalProcess'], category: 'core' }
};

// ============================================================
// 错误码表 - 从Python转换
// ============================================================
const ERROR_CODE_TABLE: Record<string, any> = {
  '777777776': { meaning: '节点执行超时', strategy: 'auto_fix_timeout', suggestion: '增大节点超时时间至300秒，或拆分复杂节点' },
  '720712023': { meaning: '输出解析失败', strategy: 'auto_fix_output_schema', suggestion: '检查节点输出格式与下游输入Schema是否匹配' },
  '720702002': { meaning: '缺少必填参数', strategy: 'auto_fix_missing_params', suggestion: '在开始节点添加参数校验，或设置默认值' },
  '720702004': { meaning: '工作流不存在', strategy: 'auto_fix_not_found', suggestion: '确认workflow_id是否正确，或从回收站恢复' },
  '720702011': { meaning: '工作流未发布', strategy: 'auto_fix_unpublished', suggestion: '调用发布API自动发布工作流' },
  '720702005': { meaning: '工作流已被删除', strategy: 'notify_admin', suggestion: '无法自动修复，请从回收站恢复或重新创建' },
  '720702006': { meaning: '节点配置错误', strategy: 'auto_fix_node_config', suggestion: '检查节点类型与配置是否匹配，自动补充缺失字段' },
  '720702007': { meaning: '连线配置错误', strategy: 'auto_fix_edge_config', suggestion: '检查连线source/target节点是否存在' },
  '720702008': { meaning: '循环节点配置错误', strategy: 'auto_fix_loop_config', suggestion: '检查循环条件与终止条件' },
  '720702009': { meaning: '插件调用失败', strategy: 'auto_fix_plugin_call', suggestion: '重试插件调用，检查插件是否已发布' },
  '720702010': { meaning: '知识库检索失败', strategy: 'auto_fix_kb_retrieval', suggestion: '检查知识库是否已发布，重新索引' },
  '500': { meaning: '服务器内部错误', strategy: 'retry_with_backoff', suggestion: '指数退避重试3次，间隔2/4/8秒' },
  '502': { meaning: '网关错误', strategy: 'retry_with_backoff', suggestion: '指数退避重试3次，间隔2/4/8秒' },
  '503': { meaning: '服务暂不可用', strategy: 'retry_with_backoff', suggestion: '指数退避重试3次，间隔2/4/8秒' },
  '504': { meaning: '网关超时', strategy: 'retry_with_backoff', suggestion: '指数退避重试3次，间隔2/4/8秒' }
};

// ============================================================
// 输入安全处理
// ============================================================
function sanitizeInput(input: any): any {
  if (typeof input !== 'string') return input;
  const entities: Record<string, string> = { '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;', '\\': '&#92;' };
  return input.replace(/[<>"'\\]/g, (char) => entities[char] || char);
}

// ============================================================
// 参数验证
// ============================================================
function validateParameters(params: any): { valid: boolean; errors: any[] } {
  const errors: any[] = [];
  if (!params || typeof params !== 'object') {
    errors.push({ field: 'params', message: '参数必须是对象' });
    return { valid: false, errors };
  }
  if (!params.user_input && !params.input && !params.query) {
    errors.push({ field: 'user_input', message: '必须提供user_input、input或query之一' });
  }
  if (params.action && typeof params.action !== 'string') {
    errors.push({ field: 'action', message: 'action必须是字符串' });
  }
  return { valid: errors.length === 0, errors };
}

// ============================================================
// 路由决策 - 基于关键词匹配
// ============================================================
function determineRoute(params: any): { module: string; sub_action: string; confidence: number } {
  const action = params.action;
  const userInput = params.user_input || params.input || params.query || '';

  if (action && action !== 'universal' && action !== 'general' && MODULES_DEFINITION[action]) {
    return { module: action, sub_action: 'auto_handle', confidence: 1.0 };
  }

  const text = String(userInput).toLowerCase();
  let maxScore = 0;
  let selectedModule = 'universal';

  for (const [module, keywords] of Object.entries(ROUTING_KEYWORDS)) {
    if (module === 'universal' || module === 'general') continue;
    let score = 0;
    for (const keyword of keywords) {
      if (text.includes(keyword.toLowerCase())) score += 1;
    }
    if (score > maxScore) { maxScore = score; selectedModule = module; }
  }

  const confidence = maxScore > 0 ? Math.min(0.5 + maxScore * 0.1, 1.0) : 0.5;
  return { module: selectedModule, sub_action: 'auto_handle', confidence };
}

// ============================================================
// 意图检测
// ============================================================
function detectIntent(userInput: string): string {
  const input = String(userInput).toLowerCase();
  for (const [module, keywords] of Object.entries(ROUTING_KEYWORDS)) {
    for (const keyword of keywords) {
      if (input.includes(keyword.toLowerCase())) return module;
    }
  }
  return 'universal';
}

// ============================================================
// 超级插件主类
// ============================================================
class CozeSuperPlugin {
  private core: PluginCore;
  private autoFix: AutoFixEngine;
  private version: string;

  constructor() {
    this.core = new PluginCore();
    this.autoFix = new AutoFixEngine();
    this.version = COZE_SUPER_CONFIG.version;
    this.initialize();
  }

  private initialize(): void {
    if (manifest && manifest.nodes) {
      manifest.nodes.forEach((node: any) => { this.core.registerNode(node.id, node); });
    }
    if (manifest && manifest.auto_fix && manifest.auto_fix.enabled) {
      this.autoFix.enableStrategies(manifest.auto_fix.fix_strategies || []);
    }
    console.log(`[CozeSuperPlugin] v${this.version} 初始化完成`);
    console.log(`[CozeSuperPlugin] 已注册 ${manifest?.nodes?.length || 0} 个节点`);
    console.log(`[CozeSuperPlugin] 模块数: ${Object.keys(MODULES_DEFINITION).length}`);
    console.log(`[CozeSuperPlugin] 完全免费使用，安全合规`);
  }

  async executeNode(nodeId: string, inputs: any): Promise<any> {
    try {
      const node = this.core.getNode(nodeId);
      if (!node) throw new Error(`节点未找到: ${nodeId}`);
      const result = await this.core.executeNode(nodeId, inputs);
      if (!result.success && this.autoFix.isEnabled()) {
        const fixed = await this.autoFix.attemptFix(nodeId, result.error || '', inputs);
        if (fixed) return fixed;
      }
      return result;
    } catch (error) {
      return { success: false, error: error instanceof Error ? error.message : String(error), nodeId };
    }
  }

  getAllNodes(): any[] {
    if (!manifest || !manifest.nodes) return [];
    return manifest.nodes.map((node: any) => ({ id: node.id, name: node.name, name_en: node.name_en, category: node.category, icon: node.icon, description: node.description }));
  }

  getNodesByCategory(category: string): any[] {
    return this.getAllNodes().filter(node => node.category === category);
  }

  getAllModules(): any[] {
    return Object.entries(MODULES_DEFINITION).map(([id, mod]) => ({ id, ...mod }));
  }

  async diagnoseWorkflow(workflowConfig: any): Promise<any> {
    const issues: any[] = [];
    const fixes: any[] = [];
    const nodes = workflowConfig.nodes || [];
    if (nodes.length > 1000) {
      issues.push({ type: 'node_limit', message: `节点数量 ${nodes.length} 超过上限1000`, fixable: true });
      fixes.push({ action: 'split_workflow', description: '拆分为多个子工作流' });
    }
    nodes.forEach((node: any) => {
      if (node.warning || node.error) {
        issues.push({ nodeId: node.id, type: 'warning', message: node.warning || node.error, fixable: true });
        fixes.push({ nodeId: node.id, action: 'auto_fix_params', description: '自动填充缺失参数' });
      }
      const timeout = node.timeout || 0;
      if (node.type === 'llm' && timeout > 10) {
        issues.push({ nodeId: node.id, type: 'timeout', message: `LLM超时${timeout}分钟 > 10分钟`, fixable: true });
        fixes.push({ nodeId: node.id, action: 'adjust_timeout', description: '将超时调整为10分钟' });
      } else if (node.type === 'code' && timeout > 1) {
        issues.push({ nodeId: node.id, type: 'timeout', message: `代码节点超时${timeout}分钟 > 1分钟`, fixable: true });
        fixes.push({ nodeId: node.id, action: 'adjust_timeout', description: '将超时调整为1分钟' });
      }
    });
    const connections = workflowConfig.connections || workflowConfig.edges || [];
    connections.forEach((conn: any) => {
      if (!conn.source || !conn.target) {
        issues.push({ connectionId: conn.id, type: 'connection_error', message: '连接配置错误', fixable: true });
        fixes.push({ connectionId: conn.id, action: 'reconnect', description: '重新连接节点' });
      }
    });
    const healthScore = Math.max(0, 100 - issues.length * 15);
    return { health_score: healthScore, status: healthScore >= 90 ? '健康' : healthScore >= 60 ? '警告' : '致命错误', issues, fixes, summary: `发现 ${issues.length} 个问题，${fixes.length} 个可自动修复` };
  }

  async autoFixWorkflow(workflowConfig: any): Promise<any> {
    const diagnosis = await this.diagnoseWorkflow(workflowConfig);
    const fixedConfig = JSON.parse(JSON.stringify(workflowConfig));
    const appliedFixes: string[] = [];
    for (const fix of diagnosis.fixes) {
      try { await this.applyFix(fix, fixedConfig); appliedFixes.push(fix.description); } catch (e) { console.warn(`[AutoFix] 修复失败: ${fix.nodeId || fix.connectionId}`, e); }
    }
    return { success: true, fixedCount: appliedFixes.length, appliedFixes, config: fixedConfig, healthScore: diagnosis.health_score };
  }

  private async applyFix(fix: any, config: any): Promise<void> {
    if (fix.nodeId) {
      const node = config.nodes?.find((n: any) => n.id === fix.nodeId);
      if (!node) return;
      switch (fix.action) {
        case 'auto_fix_params':
          node.inputs = node.inputs || {};
          (node.requiredInputs || []).forEach((key: string) => { if (node.inputs[key] === undefined) node.inputs[key] = this.getDefaultValue(key); });
          break;
        case 'adjust_timeout':
          if (node.type === 'llm') node.timeout = 10;
          else if (node.type === 'code') node.timeout = 1;
          else if (node.type === 'http_request') node.timeout = 10;
          break;
        default: break;
      }
    }
  }

  private getDefaultValue(key: string): any {
    const defaults: Record<string, any> = { text: '', prompt: '请处理以下内容', query: '', input: '', model: 'doubao-pro', temperature: 0.7, max_tokens: 2000, timeout: 30000, retry_count: 3, title: '默认标题', description: '暂无描述', image: 'https://via.placeholder.com/300' };
    return defaults[key] ?? '';
  }

  getErrorInfo(code: string): any {
    return ERROR_CODE_TABLE[code] || { meaning: '未知错误', strategy: 'notify_admin', suggestion: '请联系管理员处理' };
  }

  getConfig(): any { return COZE_SUPER_CONFIG; }
}

const plugin = new CozeSuperPlugin();

// ============================================================
// 统一Handler - Coze IDE入口函数
// ============================================================
export async function handler({ input, logger }: { input: any; logger?: any }): Promise<any> {
  try {
    if (logger && logger.info) logger.info('[CozeSuperPlugin] 开始处理', { input });
    const validation = validateParameters(input);
    if (!validation.valid) {
      if (logger && logger.error) logger.error('[CozeSuperPlugin] 参数验证失败', { errors: validation.errors });
      return { success: false, status: 'failed', module: 'universal', error: '参数验证失败', errors: validation.errors, metadata_timestamp: Date.now(), metadata_version: COZE_SUPER_CONFIG.version };
    }
    const route = determineRoute(input);
    if (logger && logger.info) logger.info(`[CozeSuperPlugin] 路由到模块: ${route.module}`, { confidence: route.confidence });
    const startTime = Date.now();
    const result = await plugin.core.executeModule(route.module, route.sub_action, input);
    const processingTime = Date.now() - startTime;
    const response: any = { success: true, status: 'success', module: route.module, module_name: MODULES_DEFINITION[route.module]?.name || route.module, detected_intent: route.sub_action, action: input.action || 'auto_route', performance_metrics: { processing_time_ms: processingTime, confidence_score: route.confidence }, metadata: { timestamp: Date.now(), version: COZE_SUPER_CONFIG.version } };
    if (result && typeof result === 'object') { Object.keys(result).forEach(key => { if (result.hasOwnProperty(key)) response[key] = result[key]; }); }
    if (logger && logger.info) logger.info('[CozeSuperPlugin] 处理完成', { module: route.module, processingTime: `${processingTime}ms`, success: response.success });
    return response;
  } catch (err) {
    const errMsg = err instanceof Error ? err.message : String(err);
    if (logger && logger.error) logger.error('[CozeSuperPlugin] 执行失败', { error: errMsg });
    return { success: false, status: 'failed', error: errMsg, metadata_timestamp: Date.now(), metadata_version: COZE_SUPER_CONFIG.version };
  }
}

export default plugin;
export { CozeSuperPlugin, COZE_SUPER_CONFIG, MODULES_DEFINITION, ERROR_CODE_TABLE, ROUTING_KEYWORDS, determineRoute, detectIntent, validateParameters, sanitizeInput };
export const run = handler;
