/*
 * 工具介绍：超级提示词引擎，合并3个提示词（角色设定、任务执行、输出格式），支持动态组合、A/B测试和质量评估
 *
 * 输入参数配置：
 * | 名称 | 描述 | 类型 | 必填 |
 * |------|------|------|------|
 * | role | 角色类型(architect/coder/writer) | string | 否 |
 * | task | 任务类型(code/solve/create) | string | 否 |
 * | output_format | 输出格式(structured/code/document) | string | 否 |
 * | params | 动态参数对象 | object | 否 |
 * | preset | 预设模板名称 | string | 否 |
 *
 * 输出参数配置：
 * | 名称 | 描述 | 类型 |
 * |------|------|------|
 * | prompt | 生成的提示词 | string |
 * | score | 质量评分(0-100) | number |
 * | dimensions | 各维度评分 | object |
 * | suggestions | 优化建议 | array |
 */

'use strict';

// ============================================================
// 角色提示词配置 - 合并自第1个提示词
// ============================================================
const ROLE_PROMPTS = {
  architect: {
    name: 'AI架构师',
    description: '严谨高效的AI架构师与自动化工程师',
    template: '你是一位严谨高效的AI架构师与自动化工程师，擅长系统设计、技术选型与全链路方案落地。' +
      '你以工程化思维拆解复杂问题，坚持架构清晰、职责单一、可扩展可维护的设计原则。' +
      '在分析问题时，先理解业务目标与约束条件，再给出分层解耦的技术方案，并说明关键决策的权衡依据。'
  },
  coder: {
    name: '代码专家',
    description: '精通多语言的编程专家',
    template: '你是一位精通多语言、多范式的编程专家，熟悉主流框架与最佳实践。' +
      '你编写的代码遵循可读性、健壮性与性能并重的原则，注重异常处理、边界条件与单元测试。' +
      '回答时给出可直接运行的代码片段，并解释关键逻辑、复杂度与潜在风险点。'
  },
  writer: {
    name: '内容创作者',
    description: '创意丰富的内容创作者',
    template: '你是一位创意丰富、表达精准的内容创作者，擅长把复杂概念转化为通俗易懂的语言。' +
      '你注重结构层次、叙事节奏与读者共鸣，能根据受众调整语气风格。' +
      '创作时先明确主题立意与目标读者，再组织素材、打磨措辞，确保内容有信息密度与传播力。'
  }
};

// ============================================================
// 任务提示词配置 - 合并自第2个提示词
// ============================================================
const TASK_PROMPTS = {
  code: {
    name: '代码生成',
    description: '根据需求生成代码',
    template: '请根据需求生成高质量代码：1) 明确输入输出与边界条件；2) 优先采用业界通用方案；' +
      '3) 代码需包含必要注释与错误处理；4) 给出使用示例与复杂度分析。需求：{requirement}'
  },
  solve: {
    name: '问题解决',
    description: '分析和解决问题',
    template: '请按"先理解问题、后解决问题"的方式处理：1) 复述并拆解问题本质；' +
      '2) 列出可能的解决路径并比较权衡；3) 选定方案并给出执行步骤；4) 说明验证方式与回退策略。问题：{problem}'
  },
  create: {
    name: '内容创作',
    description: '创作各类内容',
    template: '请按以下要求创作内容：1) 明确主题、受众与目标；2) 搭建清晰的结构骨架；' +
      '3) 充实素材并打磨表达；4) 检查逻辑连贯性与可读性。主题：{topic}'
  }
};

// ============================================================
// 输出格式提示词配置 - 合并自第3个提示词
// ============================================================
const OUTPUT_PROMPTS = {
  structured: {
    name: '结构化输出',
    template: '请以结构化格式输出，使用清晰的标题层级、列表与表格组织信息，关键结论前置，便于快速检索与复用。'
  },
  code: {
    name: '代码格式',
    template: '请以代码块格式输出，使用正确的语言标识符，代码需完整可运行，关键步骤附中文注释。'
  },
  document: {
    name: '文档格式',
    template: '请以正式文档格式输出，包含标题、摘要、正文、示例与小结，段落层次分明，语言规范通顺。'
  }
};

// ============================================================
// 预设模板配置 - 常用场景一键组合
// ============================================================
const PRESETS = {
  'api-development': { role: 'architect', task: 'code', outputFormat: 'code', name: 'API开发' },
  'bug-fix': { role: 'coder', task: 'solve', outputFormat: 'code', name: 'Bug修复' },
  'tech-blog': { role: 'writer', task: 'create', outputFormat: 'document', name: '技术博客' },
  'code-review': { role: 'coder', task: 'solve', outputFormat: 'structured', name: '代码审查' },
  'system-design': { role: 'architect', task: 'solve', outputFormat: 'document', name: '系统设计' },
  'content-marketing': { role: 'writer', task: 'create', outputFormat: 'document', name: '内容营销' }
};

// ============================================================
// 提示词组合引擎 - 负责模块解析、参数填充与优化去冗余
// ============================================================
class PromptComposer {
  constructor() {
    this.rolePrompts = ROLE_PROMPTS;
    this.taskPrompts = TASK_PROMPTS;
    this.outputPrompts = OUTPUT_PROMPTS;
    this.presets = PRESETS;
  }

  /**
   * 组合提示词
   * @param {Object} options - 组合选项
   * @param {string} options.role - 角色类型
   * @param {string} options.task - 任务类型
   * @param {string} options.output_format - 输出格式
   * @param {Object} options.params - 动态参数
   * @param {string} options.preset - 预设名称
   * @returns {Object} { prompt, meta }
   */
  compose(options) {
    if (!options || typeof options !== 'object') {
      throw new Error('compose 参数必须为对象');
    }

    let role = options.role;
    let task = options.task;
    let outputFormat = options.output_format;
    let params = options.params || {};

    // 预设优先：若指定 preset，则以预设为基础并允许参数覆盖
    if (options.preset) {
      const preset = this.presets[options.preset];
      if (!preset) {
        throw new Error('未找到预设模板: ' + options.preset);
      }
      role = role || preset.role;
      task = task || preset.task;
      outputFormat = outputFormat || preset.outputFormat;
    }

    // 收集各模块片段
    const segments = [];
    const meta = { role, task, outputFormat, preset: options.preset || null };

    // 角色模块
    if (role && this.rolePrompts[role]) {
      segments.push(this.fillParams(this.rolePrompts[role].template, params));
    }
    // 任务模块
    if (task && this.taskPrompts[task]) {
      segments.push(this.fillParams(this.taskPrompts[task].template, params));
    }
    // 输出格式模块
    if (outputFormat && this.outputPrompts[outputFormat]) {
      segments.push(this.fillParams(this.outputPrompts[outputFormat].template, params));
    }

    if (segments.length === 0) {
      throw new Error('未提供任何有效的 role/task/output_format 或 preset');
    }

    // 合并并优化去冗余
    const rawPrompt = segments.join('\n\n');
    const prompt = this.optimize(rawPrompt);

    return { prompt, meta };
  }

  /**
   * 动态参数填充，替换 {param} 占位符
   * @param {string} template - 模板字符串
   * @param {Object} params - 参数对象
   * @returns {string} 填充后的字符串
   */
  fillParams(template, params) {
    if (typeof template !== 'string') return '';
    if (!params || typeof params !== 'object') return template;

    return template.replace(/\{(\w+)\}/g, (match, key) => {
      if (Object.prototype.hasOwnProperty.call(params, key)) {
        return String(params[key]);
      }
      return match; // 未找到参数则保留原占位符
    });
  }

  /**
   * 优化去冗余：合并连续空行、去除重复句、统一标点
   * @param {string} prompt - 原始提示词
   * @returns {string} 优化后的提示词
   */
  optimize(prompt) {
    if (typeof prompt !== 'string') return '';

    let result = prompt;

    // 合并连续空白行为单个换行
    result = result.replace(/\n{3,}/g, '\n\n');
    // 去除行首尾多余空白
    result = result.split('\n').map(line => line.trim()).join('\n').trim();
    // 去除完全重复的句子（按句号分割）
    const seen = new Set();
    const sentences = result.split(/(?<=。)/);
    const deduped = sentences.filter(s => {
      const key = s.trim();
      if (!key) return false;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
    result = deduped.join('').trim();

    return result;
  }
}

// ============================================================
// 提示词效果评估器 - 5维度加权评分与优化建议
// ============================================================
class PromptEvaluator {
  constructor() {
    // 五个维度的权重，总和为 1
    this.weights = {
      completeness: 0.25, // 完整性
      clarity: 0.20,      // 清晰度
      specificity: 0.20,  // 具体性
      structure: 0.20,    // 结构性
      constraint: 0.15    // 约束性
    };
  }

  /**
   * 评估提示词，返回各维度评分与加权总分
   * @param {string} prompt - 提示词
   * @returns {Object} { score, dimensions }
   */
  evaluate(prompt) {
    if (typeof prompt !== 'string' || !prompt.trim()) {
      return { score: 0, dimensions: {} };
    }

    const dimensions = {
      completeness: this._scoreCompleteness(prompt),
      clarity: this._scoreClarity(prompt),
      specificity: this._scoreSpecificity(prompt),
      structure: this._scoreStructure(prompt),
      constraint: this._scoreConstraint(prompt)
    };

    const score = Math.round(
      dimensions.completeness * this.weights.completeness +
      dimensions.clarity * this.weights.clarity +
      dimensions.specificity * this.weights.specificity +
      dimensions.structure * this.weights.structure +
      dimensions.constraint * this.weights.constraint
    );

    return { score, dimensions };
  }

  /**
   * 获取质量评分(0-100)
   */
  getScore(prompt) {
    return this.evaluate(prompt).score;
  }

  /**
   * 获取优化建议
   */
  getSuggestions(prompt) {
    const { dimensions } = this.evaluate(prompt);
    const suggestions = [];

    if (dimensions.completeness < 70) {
      suggestions.push('完整性不足：建议补充任务背景、输入输出说明与验收标准。');
    }
    if (dimensions.clarity < 70) {
      suggestions.push('清晰度不足：建议减少模糊表述，使用明确动词与可量化描述。');
    }
    if (dimensions.specificity < 70) {
      suggestions.push('具体性不足：建议补充技术栈、版本、数据规模等具体约束。');
    }
    if (dimensions.structure < 70) {
      suggestions.push('结构性不足：建议使用编号列表、分步骤描述，关键信息前置。');
    }
    if (dimensions.constraint < 70) {
      suggestions.push('约束性不足：建议明确禁止事项、字数/时长限制与输出边界。');
    }

    if (suggestions.length === 0) {
      suggestions.push('提示词质量良好，无需额外优化。');
    }

    return suggestions;
  }

  // 完整性评分：基于关键词覆盖度
  _scoreCompleteness(prompt) {
    const keywords = ['需求', '目标', '输入', '输出', '约束', '背景', '验收', '示例'];
    let count = 0;
    keywords.forEach(kw => {
      if (prompt.includes(kw)) count++;
    });
    return Math.min(100, Math.round((count / keywords.length) * 100));
  }

  // 清晰度评分：基于平均句长与模糊词数量
  _scoreClarity(prompt) {
    const sentences = prompt.split(/[。；！？\n]/).filter(s => s.trim());
    if (sentences.length === 0) return 50;
    const avgLen = prompt.length / sentences.length;
    // 平均句长 15-40 字为最佳区间
    let score = 100 - Math.abs(avgLen - 27) * 2;
    // 模糊词扣分
    const vagueWords = ['大概', '可能', '一些', '等等', '之类', '相关'];
    vagueWords.forEach(w => {
      if (prompt.includes(w)) score -= 8;
    });
    return Math.max(0, Math.min(100, Math.round(score)));
  }

  // 具体性评分：基于数字、专有名词与量化描述
  _scoreSpecificity(prompt) {
    let score = 40;
    // 数字出现
    const numberMatches = prompt.match(/\d+/g);
    if (numberMatches) score += numberMatches.length * 6;
    // 量化关键词
    const specWords = ['版本', '大小', '数量', '毫秒', '秒', 'MB', 'GB', '%', '限制', '不超过'];
    specWords.forEach(w => {
      if (prompt.includes(w)) score += 7;
    });
    return Math.max(0, Math.min(100, Math.round(score)));
  }

  // 结构性评分：基于列表、编号、换行层次
  _scoreStructure(prompt) {
    let score = 30;
    if (/\n/.test(prompt)) score += 15;
    if (/[1-9][）)]/.test(prompt)) score += 20; // 编号列表
    if (/[、，；]/.test(prompt)) score += 10;
    if (/[:：]/.test(prompt)) score += 10; // 冒号分层
    if (/\n\s*\n/.test(prompt)) score += 15; // 段落分隔
    return Math.max(0, Math.min(100, Math.round(score)));
  }

  // 约束性评分：基于禁止/限制/边界类表述
  _scoreConstraint(prompt) {
    let score = 40;
    const constraintWords = ['不要', '禁止', '必须', '限制', '不超过', '不超过', '避免', '确保', '只能', '不得'];
    constraintWords.forEach(w => {
      if (prompt.includes(w)) score += 8;
    });
    return Math.max(0, Math.min(100, Math.round(score)));
  }
}

// ============================================================
// A/B测试框架 - 实验管理与统计显著性检验
// ============================================================
class PromptABTest {
  constructor() {
    this.experiments = new Map();
    this.nextId = 1;
  }

  /**
   * 创建实验
   * @param {string} name - 实验名称
   * @param {string} promptA - A 版本提示词
   * @param {string} promptB - B 版本提示词
   * @returns {number} 实验ID
   */
  createExperiment(name, promptA, promptB) {
    const id = this.nextId++;
    this.experiments.set(id, {
      id,
      name: name || ('实验' + id),
      promptA,
      promptB,
      samplesA: [],
      samplesB: [],
      createdAt: new Date().toISOString(),
      result: null
    });
    return id;
  }

  /**
   * 添加样本
   * @param {number} experimentId - 实验ID
   * @param {string} variant - 'A' 或 'B'
   * @param {number} score - 样本评分
   */
  addSample(experimentId, variant, score) {
    const exp = this.experiments.get(experimentId);
    if (!exp) throw new Error('实验不存在: ' + experimentId);
    if (variant !== 'A' && variant !== 'B') throw new Error('variant 必须为 A 或 B');
    if (typeof score !== 'number' || score < 0 || score > 100) {
      throw new Error('score 必须为 0-100 之间的数字');
    }
    if (variant === 'A') {
      exp.samplesA.push(score);
    } else {
      exp.samplesB.push(score);
    }
  }

  /**
   * 统计显著性检验（基于双样本 t 检验近似）
   * @param {number} experimentId - 实验ID
   * @returns {Object} 分析结果
   */
  analyze(experimentId) {
    const exp = this.experiments.get(experimentId);
    if (!exp) throw new Error('实验不存在: ' + experimentId);

    const statsA = this._calcStats(exp.samplesA);
    const statsB = this._calcStats(exp.samplesB);

    // 计算t值（Welch t检验近似）
    let tValue = 0;
    let pValue = 1;
    let significant = false;

    if (statsA.n > 1 && statsB.n > 1 && statsA.variance >= 0 && statsB.variance >= 0) {
      const denom = Math.sqrt(statsA.variance / statsA.n + statsB.variance / statsB.n);
      if (denom > 0) {
        tValue = (statsA.mean - statsB.mean) / denom;
        // 简化的p值估算：|t|>1.96 视为显著（α=0.05）
        pValue = this._approxPValue(Math.abs(tValue), statsA.n + statsB.n - 2);
        significant = Math.abs(tValue) > 1.96;
      }
    }

    const result = {
      experimentId: exp.id,
      name: exp.name,
      variantA: { ...statsA, scores: exp.samplesA },
      variantB: { ...statsB, scores: exp.samplesB },
      tValue: Number(tValue.toFixed(4)),
      pValue: Number(pValue.toFixed(4)),
      significant,
      winner: significant ? (statsA.mean > statsB.mean ? 'A' : 'B') : null,
      recommendation: this._buildRecommendation(statsA, statsB, significant)
    };

    exp.result = result;
    return result;
  }

  /**
   * 列出所有实验
   */
  listExperiments() {
    const list = [];
    this.experiments.forEach(exp => {
      list.push({
        id: exp.id,
        name: exp.name,
        samplesA: exp.samplesA.length,
        samplesB: exp.samplesB.length,
        createdAt: exp.createdAt,
        analyzed: !!exp.result
      });
    });
    return list;
  }

  // 计算基本统计量
  _calcStats(samples) {
    const n = samples.length;
    if (n === 0) {
      return { n: 0, mean: 0, variance: 0, min: 0, max: 0 };
    }
    const sum = samples.reduce((a, b) => a + b, 0);
    const mean = sum / n;
    const variance = n > 1
      ? samples.reduce((acc, s) => acc + (s - mean) ** 2, 0) / (n - 1)
      : 0;
    return {
      n,
      mean: Number(mean.toFixed(2)),
      variance: Number(variance.toFixed(2)),
      min: Math.min(...samples),
      max: Math.max(...samples)
    };
  }

  // 简化p值估算（基于正态近似）
  _approxPValue(absT, df) {
    // 使用标准正态分布的简化近似
    if (absT >= 2.576) return 0.01;
    if (absT >= 1.96) return 0.05;
    if (absT >= 1.645) return 0.10;
    if (absT >= 1.282) return 0.20;
    return 0.50;
  }

  // 构建推荐结论
  _buildRecommendation(statsA, statsB, significant) {
    if (statsA.n < 2 || statsB.n < 2) {
      return '样本量不足（每组至少需要2个样本），请继续采集数据。';
    }
    if (!significant) {
      return '两组差异未达显著水平（p>0.05），暂无法判定优劣，建议增加样本量。';
    }
    const winner = statsA.mean > statsB.mean ? 'A' : 'B';
    const diff = Math.abs(statsA.mean - statsB.mean).toFixed(2);
    return '版本' + winner + '显著优于另一版本（均值差' + diff + '），建议采用版本' + winner + '。';
  }
}

// ============================================================
// 超级提示词引擎 - 统一入口，整合组合、评估与A/B测试
// ============================================================
class SuperPromptEngine {
  constructor() {
    this.composer = new PromptComposer();
    this.evaluator = new PromptEvaluator();
    this.abTest = new PromptABTest();
  }

  /**
   * 生成提示词
   * @param {Object} options - 同 compose 选项
   * @returns {Object} { prompt, score, dimensions, suggestions, meta }
   */
  generate(options) {
    const { prompt, meta } = this.composer.compose(options);
    const { score, dimensions } = this.evaluator.evaluate(prompt);
    const suggestions = this.evaluator.getSuggestions(prompt);
    return { prompt, score, dimensions, suggestions, meta };
  }

  /**
   * 使用预设模板生成提示词
   * @param {string} presetName - 预设名称
   * @param {Object} params - 动态参数
   * @returns {Object} 同 generate 返回
   */
  usePreset(presetName, params) {
    return this.generate({ preset: presetName, params: params || {} });
  }

  /**
   * 评估提示词
   * @param {string} prompt - 提示词
   * @returns {Object} { score, dimensions, suggestions }
   */
  evaluatePrompt(prompt) {
    const { score, dimensions } = this.evaluator.evaluate(prompt);
    const suggestions = this.evaluator.getSuggestions(prompt);
    return { score, dimensions, suggestions };
  }

  /**
   * 运行A/B测试（内置示例：对比两个预设）
   * @param {Object} [config] - { presetA, presetB, params, samples }
   * @returns {Object} 测试分析结果
   */
  runABTest(config) {
    const cfg = config || {};
    const presetA = cfg.presetA || 'api-development';
    const presetB = cfg.presetB || 'bug-fix';
    const params = cfg.params || { requirement: '用户登录接口', problem: '登录超时', topic: 'API优化' };
    const sampleCount = cfg.samples || 10;

    const resultA = this.usePreset(presetA, params);
    const resultB = this.usePreset(presetB, params);

    const expId = this.abTest.createExperiment(
      presetA + ' vs ' + presetB,
      resultA.prompt,
      resultB.prompt
    );

    // 模拟采样：基于基础评分加入随机扰动
    for (let i = 0; i < sampleCount; i++) {
      const scoreA = Math.max(0, Math.min(100, resultA.score + Math.round((Math.random() - 0.5) * 20)));
      const scoreB = Math.max(0, Math.min(100, resultB.score + Math.round((Math.random() - 0.5) * 20)));
      this.abTest.addSample(expId, 'A', scoreA);
      this.abTest.addSample(expId, 'B', scoreB);
    }

    return this.abTest.analyze(expId);
  }

  /**
   * 列出所有可用预设
   */
  listPresets() {
    const list = [];
    Object.keys(this.composer.presets).forEach(key => {
      const p = this.composer.presets[key];
      list.push({ key, name: p.name, role: p.role, task: p.task, outputFormat: p.outputFormat });
    });
    return list;
  }
}

// ============================================================
// 便捷函数 - 快速调用入口
// ============================================================

/**
 * 创建引擎实例
 * @returns {SuperPromptEngine}
 */
function createEngine() {
  return new SuperPromptEngine();
}

/**
 * 快速生成提示词
 * @param {Object} options - 同 compose 选项
 * @returns {Object} 生成结果
 */
function generatePrompt(options) {
  const engine = new SuperPromptEngine();
  return engine.generate(options);
}

/**
 * 快速评估提示词
 * @param {string} prompt - 提示词
 * @returns {Object} 评估结果
 */
function evaluatePrompt(prompt) {
  const engine = new SuperPromptEngine();
  return engine.evaluatePrompt(prompt);
}

/**
 * 快速运行A/B测试
 * @param {Object} config - 测试配置
 * @returns {Object} 测试结果
 */
function runABTest(config) {
  const engine = new SuperPromptEngine();
  return engine.runABTest(config);
}

// ============================================================
// 模块导出 - 同时兼容 Node.js 与浏览器环境
// ============================================================
const exportsObj = {
  // 常量
  ROLE_PROMPTS,
  TASK_PROMPTS,
  OUTPUT_PROMPTS,
  PRESETS,
  // 类
  PromptComposer,
  PromptEvaluator,
  PromptABTest,
  SuperPromptEngine,
  // 便捷函数
  createEngine,
  generatePrompt,
  evaluatePrompt,
  runABTest
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = exportsObj;
}
if (typeof window !== 'undefined') {
  window.SuperPrompt = exportsObj;
}
