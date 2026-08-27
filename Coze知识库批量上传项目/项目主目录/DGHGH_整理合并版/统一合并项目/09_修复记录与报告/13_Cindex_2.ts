/**
 * 模块执行器 - 统一入口
 * 注册所有模块并提供统一执行接口
 *
 * 本文件是 src/modules 目录的统一入口，负责：
 * 1. 集中管理所有模块定义（与 manifest.json 完全一致）
 * 2. 提供 ModuleDefinition / ModuleExecutor 类型契约
 * 3. 维护模块注册表（MODULE_REGISTRY）与执行器注册表（MODULE_EXECUTORS）
 * 4. 暴露统一的查询与执行 API
 *
 * 安全合规：本地运行、零 Token 成本、完全免费
 */

import { PluginCore } from '../core/PluginCore';
import { AutoFixEngine } from '../core/AutoFixEngine';
import manifest from '../../manifest.json';

// ============================================================
// 类型定义
// ============================================================

/**
 * 模块定义 - 描述一个模块的元信息
 */
export interface ModuleDefinition {
  /** 模块唯一标识 */
  id: string;
  /** 模块中文名称 */
  name: string;
  /** 模块英文名称 */
  name_en: string;
  /** 模块描述 */
  description: string;
  /** 模块分类 */
  category: string;
  /** 模块包含的工具列表 */
  tools: string[];
}

/**
 * 模块执行器 - 接收动作名称与参数，返回执行结果
 */
export interface ModuleExecutor {
  (action: string, params: any): Promise<any>;
}

/**
 * 模块执行结果
 */
export interface ModuleExecutionResult {
  success: boolean;
  status: string;
  module: string;
  module_name: string;
  action: string;
  result?: any;
  error?: string;
  performance_metrics?: {
    processing_time_ms: number;
  };
  metadata?: {
    timestamp: number;
    version: string;
  };
}

// ============================================================
// 模块定义注册表 - 与 manifest.json 完全一致
// 包含全部模块（核心 / 业务 / 知识 / 媒体 / 安全 / DevOps / 修复 / 工具 / 入口）
// ============================================================

export const MODULE_REGISTRY: Record<string, ModuleDefinition> = {
  // ---------- 核心模块 ----------
  workflow_auto_fix: {
    id: 'workflow_auto_fix',
    name: '工作流自动修复',
    name_en: 'Workflow Auto Fix',
    description: '自动诊断并修复工作流配置错误',
    category: 'core',
    tools: ['diagnoseWorkflow', 'autoFixWorkflow', 'generateReport', 'workflowRepairer'],
  },
  error_classifier: {
    id: 'error_classifier',
    name: '错误分类器',
    name_en: 'Error Classifier',
    description: '自动分类错误并推荐修复策略',
    category: 'core',
    tools: ['errorClassifier'],
  },
  plugin_generator: {
    id: 'plugin_generator',
    name: '插件代码生成器',
    name_en: 'Plugin Generator',
    description: '根据需求自动生成完整插件代码',
    category: 'core',
    tools: ['generatePluginCode', 'generatePluginConfig'],
  },
  smart_processor: {
    id: 'smart_processor',
    name: '智能处理器',
    name_en: 'Smart Processor',
    description: '一站式数据处理工具',
    category: 'core',
    tools: ['smartProcess', 'identifyTaskType'],
  },
  json_repair: {
    id: 'json_repair',
    name: 'JSON修复器',
    name_en: 'JSON Repair',
    description: '修复损坏的JSON数据',
    category: 'core',
    tools: ['repairJSON'],
  },
  code_repair: {
    id: 'code_repair',
    name: '代码修复器',
    name_en: 'Code Repair',
    description: '修复代码语法和逻辑错误',
    category: 'core',
    tools: ['repairCode'],
  },
  universal: {
    id: 'universal',
    name: '统一入口',
    name_en: 'Universal Entry',
    description: '统一入口模块，自动路由到具体模块',
    category: 'core',
    tools: ['universalRoute'],
  },
  general: {
    id: 'general',
    name: '通用处理',
    name_en: 'General Process',
    description: '通用处理逻辑',
    category: 'core',
    tools: ['generalProcess'],
  },

  // ---------- 知识库模块 ----------
  knowledge_manager: {
    id: 'knowledge_manager',
    name: '知识库管理',
    name_en: 'Knowledge Manager',
    description: '知识库内容管理和去重',
    category: 'knowledge',
    tools: ['knowledgeRechunk', 'batchUpload', 'kbSearch', 'kbWrite', 'kbDelete'],
  },
  batch_upload: {
    id: 'batch_upload',
    name: '批量知识库上传',
    name_en: 'Batch Upload',
    description: 'ZIP压缩包批量上传，保留目录结构',
    category: 'knowledge',
    tools: ['batchUpload', 'parseFile', 'sanitizePath'],
  },

  // ---------- 业务模块 ----------
  deepseek_factory: {
    id: 'deepseek_factory',
    name: 'DeepSeek AI工厂',
    name_en: 'DeepSeek Factory',
    description: 'DeepSeek对话处理和内容分类',
    category: 'business',
    tools: ['processDeepSeek', 'getStatistics'],
  },
  content_generator: {
    id: 'content_generator',
    name: '内容生成器',
    name_en: 'Content Generator',
    description: '自动生成各类内容',
    category: 'business',
    tools: ['generateContent'],
  },
  agent_creator: {
    id: 'agent_creator',
    name: '智能体创建器',
    name_en: 'Agent Creator',
    description: '创建自定义智能体',
    category: 'business',
    tools: ['createAgent'],
  },
  data_processor: {
    id: 'data_processor',
    name: '数据处理器',
    name_en: 'Data Processor',
    description: '数据采集、清洗和处理',
    category: 'business',
    tools: ['processData'],
  },
  industry_analyzer: {
    id: 'industry_analyzer',
    name: '行业分析器',
    name_en: 'Industry Analyzer',
    description: '行业分析和市场研究',
    category: 'business',
    tools: ['analyzeIndustry'],
  },
  model_trainer: {
    id: 'model_trainer',
    name: '模型训练器',
    name_en: 'Model Trainer',
    description: 'AI模型训练和微调',
    category: 'business',
    tools: ['trainModel'],
  },
  monetization: {
    id: 'monetization',
    name: '变现支持器',
    name_en: 'Monetization',
    description: '变现策略和建议',
    category: 'business',
    tools: ['getMonetizationTips'],
  },
  feishu_integration: {
    id: 'feishu_integration',
    name: '飞书集成器',
    name_en: 'Feishu Integration',
    description: '飞书平台集成',
    category: 'business',
    tools: ['setupFeishu'],
  },
  openclaw_guide: {
    id: 'openclaw_guide',
    name: 'OpenClaw指南',
    name_en: 'OpenClaw Guide',
    description: 'OpenClaw使用指南',
    category: 'business',
    tools: ['getOpenClawGuide'],
  },
  neural_decision: {
    id: 'neural_decision',
    name: '神经决策器',
    name_en: 'Neural Decision',
    description: '神经网络决策支持',
    category: 'business',
    tools: ['neuralDecide'],
  },

  // ---------- 媒体模块 ----------
  image_generator: {
    id: 'image_generator',
    name: '图片生成器',
    name_en: 'Image Generator',
    description: '生成和处理图片',
    category: 'media',
    tools: ['generateImage'],
  },

  // ---------- 安全模块 ----------
  security_checker: {
    id: 'security_checker',
    name: '安全检查器',
    name_en: 'Security Checker',
    description: '安全漏洞检测和修复',
    category: 'security',
    tools: ['checkSecurity'],
  },

  // ---------- DevOps 模块 ----------
  deploy_service: {
    id: 'deploy_service',
    name: '服务部署器',
    name_en: 'Deploy Service',
    description: '自动化服务部署',
    category: 'devops',
    tools: ['deployService'],
  },

  // ---------- 工具模块 ----------
  unit_converter: {
    id: 'unit_converter',
    name: '单位转换器',
    name_en: 'Unit Converter',
    description: '各种单位换算',
    category: 'utility',
    tools: ['unitConvert'],
  },

  // ---------- 修复模块 ----------
  orange_exclamation_fix: {
    id: 'orange_exclamation_fix',
    name: '橘黄色叹号修复',
    name_en: 'Orange Exclamation Fix',
    description: '修复Coze画布上的橘黄色叹号警告',
    category: 'fix',
    tools: ['fixOrangeExclamation'],
  },
  missing_param_fix: {
    id: 'missing_param_fix',
    name: '缺失参数修复',
    name_en: 'Missing Param Fix',
    description: '自动填充缺失的必要参数',
    category: 'fix',
    tools: ['fixMissingParam'],
  },
  connection_error_fix: {
    id: 'connection_error_fix',
    name: '连接错误修复',
    name_en: 'Connection Error Fix',
    description: '修复节点连接错误',
    category: 'fix',
    tools: ['fixConnectionError'],
  },
  timeout_retry: {
    id: 'timeout_retry',
    name: '超时重试',
    name_en: 'Timeout Retry',
    description: '超时后自动重试',
    category: 'fix',
    tools: ['retryWithTimeout'],
  },
  schema_validation: {
    id: 'schema_validation',
    name: 'Schema验证',
    name_en: 'Schema Validation',
    description: '验证和修复Schema配置',
    category: 'fix',
    tools: ['validateSchema'],
  },
  card_variable_fix: {
    id: 'card_variable_fix',
    name: '卡片变量修复',
    name_en: 'Card Variable Fix',
    description: '修复卡片变量缺失问题',
    category: 'fix',
    tools: ['cardVariableFiller'],
  },
  knowledge_rechunk: {
    id: 'knowledge_rechunk',
    name: '知识库重分段',
    name_en: 'Knowledge Rechunk',
    description: '重新分段知识库内容',
    category: 'fix',
    tools: ['knowledgeRechunk'],
  },
  fallback_handler: {
    id: 'fallback_handler',
    name: '兜底处理器',
    name_en: 'Fallback Handler',
    description: '最后的兜底处理方案',
    category: 'fix',
    tools: ['fallbackHandle'],
  },
};

// ============================================================
// 模块执行器注册表
// 将每个模块 id 映射到 PluginCore 中注册的执行器
// ============================================================

const pluginCore = new PluginCore();
const autoFixEngine = new AutoFixEngine();

// 启用 manifest 中声明的自动修复策略
if (manifest?.auto_fix?.enabled && Array.isArray(manifest.auto_fix.fix_strategies)) {
  autoFixEngine.enableStrategies(manifest.auto_fix.fix_strategies);
}

/**
 * 模块执行器注册表
 * 通过 PluginCore.executeModule 统一调度
 */
export const MODULE_EXECUTORS: Record<string, ModuleExecutor> = {};

// 为注册表中的每个模块绑定执行器
for (const moduleId of Object.keys(MODULE_REGISTRY)) {
  MODULE_EXECUTORS[moduleId] = async (action: string, params: any): Promise<any> => {
    const subAction = action || 'auto_handle';
    return pluginCore.executeModule(moduleId, subAction, params);
  };
}

// ============================================================
// 查询 API
// ============================================================

/**
 * 获取所有模块定义
 */
export function getAllModules(): ModuleDefinition[] {
  return Object.values(MODULE_REGISTRY);
}

/**
 * 按分类获取模块
 */
export function getModulesByCategory(category: string): ModuleDefinition[] {
  return getAllModules().filter((m) => m.category === category);
}

/**
 * 获取单个模块定义
 */
export function getModule(id: string): ModuleDefinition | undefined {
  return MODULE_REGISTRY[id];
}

/**
 * 检查模块是否存在
 */
export function hasModule(id: string): boolean {
  return id in MODULE_REGISTRY;
}

/**
 * 获取所有分类
 */
export function getAllCategories(): string[] {
  const categories = new Set<string>();
  getAllModules().forEach((m) => categories.add(m.category));
  return Array.from(categories);
}

/**
 * 获取所有工具
 */
export function getAllTools(): string[] {
  const tools = new Set<string>();
  getAllModules().forEach((m) => m.tools.forEach((t) => tools.add(t)));
  return Array.from(tools);
}

/**
 * 获取模块的工具列表
 */
export function getModuleTools(id: string): string[] {
  return MODULE_REGISTRY[id]?.tools ?? [];
}

/**
 * 根据工具名称反查所属模块
 */
export function findModuleByTool(toolName: string): ModuleDefinition | undefined {
  return getAllModules().find((m) => m.tools.includes(toolName));
}

/**
 * 获取模块总数
 */
export function getModuleCount(): number {
  return Object.keys(MODULE_REGISTRY).length;
}

/**
 * 获取工具总数
 */
export function getToolCount(): number {
  return getAllTools().length;
}

// ============================================================
// 执行 API
// ============================================================

/**
 * 执行指定模块
 * @param moduleId 模块 id
 * @param action 动作名称
 * @param params 执行参数
 */
export async function executeModule(
  moduleId: string,
  action: string,
  params: any
): Promise<ModuleExecutionResult> {
  const startTime = Date.now();
  const definition = MODULE_REGISTRY[moduleId];

  if (!definition) {
    return {
      success: false,
      status: 'failed',
      module: moduleId,
      module_name: moduleId,
      action,
      error: `模块不存在: ${moduleId}`,
      performance_metrics: { processing_time_ms: Date.now() - startTime },
      metadata: { timestamp: Date.now(), version: manifest?.version ?? 'unknown' },
    };
  }

  const executor = MODULE_EXECUTORS[moduleId];
  if (!executor) {
    return {
      success: false,
      status: 'failed',
      module: moduleId,
      module_name: definition.name,
      action,
      error: `模块执行器未注册: ${moduleId}`,
      performance_metrics: { processing_time_ms: Date.now() - startTime },
      metadata: { timestamp: Date.now(), version: manifest?.version ?? 'unknown' },
    };
  }

  try {
    const result = await executor(action, params);
    return {
      success: true,
      status: 'success',
      module: moduleId,
      module_name: definition.name,
      action,
      result,
      performance_metrics: { processing_time_ms: Date.now() - startTime },
      metadata: { timestamp: Date.now(), version: manifest?.version ?? 'unknown' },
    };
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);

    // 尝试自动修复
    if (autoFixEngine.isEnabled()) {
      try {
        const fixed = await autoFixEngine.attemptFix(moduleId, errorMsg, params);
        if (fixed) {
          return {
            success: true,
            status: 'auto_fixed',
            module: moduleId,
            module_name: definition.name,
            action,
            result: fixed,
            performance_metrics: { processing_time_ms: Date.now() - startTime },
            metadata: { timestamp: Date.now(), version: manifest?.version ?? 'unknown' },
          };
        }
      } catch {
        // 修复失败则继续返回原始错误
      }
    }

    return {
      success: false,
      status: 'failed',
      module: moduleId,
      module_name: definition.name,
      action,
      error: errorMsg,
      performance_metrics: { processing_time_ms: Date.now() - startTime },
      metadata: { timestamp: Date.now(), version: manifest?.version ?? 'unknown' },
    };
  }
}

/**
 * 统一入口执行函数
 * 根据参数自动路由到对应模块并执行
 * @param params 包含 action / user_input 等字段的参数对象
 */
export async function execute(params: any): Promise<ModuleExecutionResult> {
  const action = params?.action;

  // 显式指定模块时直接执行
  if (action && action !== 'universal' && action !== 'general' && hasModule(action)) {
    return executeModule(action, params.sub_action || 'auto_handle', params);
  }

  // 否则通过 universal 统一入口模块自动路由
  // user_input / input / query 等字段由 PluginCore 内部的路由逻辑处理
  return executeModule('universal', 'auto_handle', params);
}

// ============================================================
// 一致性校验 - 确保注册表与 manifest.json 同步
// ============================================================

/**
 * 校验 MODULE_REGISTRY 与 manifest.json 中的模块定义是否一致
 * @returns 不一致的模块列表（空数组表示完全一致）
 */
export function validateAgainstManifest(): string[] {
  const mismatches: string[] = [];
  const manifestModules: any[] = (manifest as any)?.modules ?? [];

  // 检查 manifest 中的模块是否都在注册表中
  for (const m of manifestModules) {
    const registered = MODULE_REGISTRY[m.id];
    if (!registered) {
      mismatches.push(`manifest 中存在但注册表缺失: ${m.id}`);
      continue;
    }
    if (registered.name !== m.name) mismatches.push(`${m.id}: name 不一致`);
    if (registered.name_en !== m.name_en) mismatches.push(`${m.id}: name_en 不一致`);
    if (registered.category !== m.category) mismatches.push(`${m.id}: category 不一致`);
    if (registered.description !== m.description) mismatches.push(`${m.id}: description 不一致`);
    if (JSON.stringify(registered.tools) !== JSON.stringify(m.tools)) {
      mismatches.push(`${m.id}: tools 不一致`);
    }
  }

  // 检查注册表中是否有多余的模块
  for (const id of Object.keys(MODULE_REGISTRY)) {
    if (!manifestModules.some((m) => m.id === id)) {
      mismatches.push(`注册表中存在但 manifest 缺失: ${id}`);
    }
  }

  return mismatches;
}

// ============================================================
// 默认导出
// ============================================================

export default {
  MODULE_REGISTRY,
  MODULE_EXECUTORS,
  getAllModules,
  getModulesByCategory,
  getModule,
  hasModule,
  getAllCategories,
  getAllTools,
  getModuleTools,
  findModuleByTool,
  getModuleCount,
  getToolCount,
  executeModule,
  execute,
  validateAgainstManifest,
};
