/*
 * 工具介绍：超级对话流引擎，合并8个对话流（智能客服、代码助手、内容创作、技术支持、知识问答、创作助手、数据分析、自动化助手）
 *
 * 输入参数配置：
 * | 名称 | 描述 | 类型 | 必填 |
 * |------|------|------|------|
 * | user_input | 用户输入文本 | string | 是 |
 * | dialog_type | 对话类型(customer_service/code_assistant/content_creator/tech_support/knowledge_qa/creative_assistant/data_analyst/automation_helper) | string | 否 |
 * | session_id | 会话ID，用于多轮对话 | string | 否 |
 * | context | 上下文信息 | object | 否 |
 *
 * 输出参数配置：
 * | 名称 | 描述 | 类型 |
 * |------|------|------|
 * | response | 回复内容 | string |
 * | intent | 识别的意图 | string |
 * | emotion | 情感分析结果 | object |
 * | dialog_type | 对话类型 | string |
 * | confidence | 置信度 | number |
 * | suggestions | 建议列表 | array |
 */

'use strict';

/**
 * 对话流配置集合，包含8个对话流定义
 */
const DialogFlowConfigs = {
  // 1. 智能客服对话流
  customer_service: {
    id: 'customer_service',
    name: '智能客服',
    persona: '小智',
    system_prompt: '你是"小智"，一位友好专业的智能客服代表。你需要耐心倾听用户问题，提供准确、礼貌、专业的解答，始终以用户满意为服务宗旨。',
    reply_templates: [
      '您好，我是客服小智，很高兴为您服务！请问有什么可以帮您？',
      '感谢您的咨询，关于您提到的问题，我为您详细解答如下：',
      '非常抱歉给您带来不便，我们会尽快为您处理此问题。',
      '您的反馈对我们非常重要，我会记录并跟进此事。',
      '请问还有其他需要我帮助的地方吗？'
    ]
  },
  // 2. 代码助手对话流
  code_assistant: {
    id: 'code_assistant',
    name: '代码助手',
    persona: 'CodeBot',
    system_prompt: '你是"CodeBot"，一位专业的编程助手。你精通多种编程语言，能够解答编程问题、审查代码、提供优化建议，回答严谨准确。',
    reply_templates: [
      '你好，我是CodeBot，专业编程助手，请描述你的编程问题。',
      '根据你的代码，我建议如下优化方案：',
      '这是一个常见的编程问题，解决思路如下：',
      '代码审查结果：整体结构良好，建议改进以下部分：',
      '需要我为你提供完整的代码示例吗？'
    ]
  },
  // 3. 内容创作对话流
  content_creator: {
    id: 'content_creator',
    name: '内容创作',
    persona: '创想',
    system_prompt: '你是"创想"，一位富有创意的内容创作者。你擅长撰写各类文案、文章、营销内容，文字生动有感染力。',
    reply_templates: [
      '你好，我是创想，让我们一起创造精彩内容！',
      '关于这个主题，我为你构思了如下创意方向：',
      '这是一段为你量身定制的内容：',
      '为了让内容更有吸引力，建议加入以下元素：',
      '需要我调整文风或风格吗？'
    ]
  },
  // 4. 技术支持对话流
  tech_support: {
    id: 'tech_support',
    name: '技术支持',
    persona: 'Techie',
    system_prompt: '你是"Techie"，一位经验丰富的技术支持专家。你擅长排查技术故障、提供解决方案，回答专业、细致、可操作。',
    reply_templates: [
      '你好，我是技术支持专家Techie，请描述你遇到的技术问题。',
      '根据你的问题描述，我建议按以下步骤排查：',
      '这是一个常见的技术问题，通常的解决方案是：',
      '请提供更多信息以便我精准定位问题：',
      '问题解决后，建议你做以下预防措施：'
    ]
  },
  // 5. 知识问答对话流
  knowledge_qa: {
    id: 'knowledge_qa',
    name: '知识问答',
    persona: '智学',
    system_prompt: '你是"智学"，一位知识渊博的学者。你能够回答各领域的知识问题，回答准确、深入、有理有据。',
    reply_templates: [
      '你好，我是智学，乐于与你分享知识。',
      '关于这个问题，我从以下几个方面为你解答：',
      '这是一个有趣的知识点，让我为你详细讲解：',
      '补充一些相关的背景知识，帮助你更好理解：',
      '还有什么知识你想深入了解的吗？'
    ]
  },
  // 6. 创作助手对话流
  creative_assistant: {
    id: 'creative_assistant',
    name: '创作助手',
    persona: '灵感',
    system_prompt: '你是"灵感"，一位创意写作助手。你擅长激发创作灵感、提供写作建议、协助故事构思，文字优美富有想象力。',
    reply_templates: [
      '你好，我是灵感，让我们一起开启创作之旅！',
      '关于这个创作方向，我为你提供以下灵感：',
      '这是一个可能的故事走向，供你参考：',
      '为了让作品更有深度，建议考虑以下主题：',
      '需要我帮你拓展某个情节或人物吗？'
    ]
  },
  // 7. 数据分析对话流
  data_analyst: {
    id: 'data_analyst',
    name: '数据分析',
    persona: '数析',
    system_prompt: '你是"数析"，一位专业的数据分析专家。你擅长数据解读、统计分析、数据可视化建议，分析严谨、结论可靠。',
    reply_templates: [
      '你好，我是数析，数据分析专家，请提供你的数据问题。',
      '根据数据分析，我得出以下结论：',
      '这组数据呈现的规律如下：',
      '建议从以下几个维度深入分析：',
      '需要我帮你设计数据可视化方案吗？'
    ]
  },
  // 8. 自动化助手对话流
  automation_helper: {
    id: 'automation_helper',
    name: '自动化助手',
    persona: 'AutoBot',
    system_prompt: '你是"AutoBot"，一位自动化助手专家。你擅长流程自动化、脚本编写、效率提升方案，回答实用、高效、可执行。',
    reply_templates: [
      '你好，我是AutoBot，自动化助手，帮你提升效率！',
      '针对这个任务，我建议的自动化方案如下：',
      '这是一个可以自动化的流程，步骤如下：',
      '为了提升效率，推荐使用以下自动化工具：',
      '需要我帮你编写自动化脚本吗？'
    ]
  }
};

/**
 * 意图识别引擎
 * 负责识别用户输入的意图
 */
class IntentRecognizer {
  constructor() {
    // 初始化意图关键词表
    this.intentKeywords = {
      greeting: ['你好', '您好', 'hi', 'hello', 'hey', '早上好', '晚上好', '下午好', '嗨'],
      farewell: ['再见', '拜拜', 'bye', 'goodbye', '回见', '下次见'],
      question: ['什么是', '为什么', '怎么', '如何', '哪里', '哪个', '请问', '？', '?'],
      complaint: ['投诉', '不满', '差评', '问题', '故障', '错误', 'bug', '失败'],
      request: ['帮我', '请帮', '需要', '想要', '麻烦', '可以帮', '能否'],
      feedback: ['反馈', '建议', '意见', '评价', '体验'],
      thanks: ['谢谢', '感谢', 'thanks', '多谢', '辛苦了'],
      code: ['代码', '编程', '函数', '程序', '编译', '运行', '调试', '算法'],
      data: ['数据', '分析', '统计', '报表', '图表', '指标'],
      creative: ['创作', '故事', '文案', '文章', '诗歌', '小说', '剧本']
    };
  }

  /**
   * 识别文本意图
   * @param {string} text - 用户输入文本
   * @returns {{intent: string, confidence: number, alternatives: Array}} 识别结果
   */
  recognize(text) {
    if (!text || typeof text !== 'string') {
      return { intent: 'unknown', confidence: 0, alternatives: [] };
    }
    const lowerText = text.toLowerCase();
    const scores = {};
    // 计算每个意图的匹配分数
    for (const intent in this.intentKeywords) {
      let count = 0;
      for (const keyword of this.intentKeywords[intent]) {
        if (lowerText.indexOf(keyword.toLowerCase()) !== -1) {
          count++;
        }
      }
      if (count > 0) {
        scores[intent] = count;
      }
    }
    // 按分数从高到低排序
    const sorted = Object.keys(scores).sort((a, b) => scores[b] - scores[a]);
    if (sorted.length === 0) {
      return { intent: 'unknown', confidence: 0, alternatives: [] };
    }
    const topIntent = sorted[0];
    const total = Object.values(scores).reduce((a, b) => a + b, 0);
    const confidence = Math.min(1, scores[topIntent] / Math.max(total, 1));
    const alternatives = sorted.slice(1, 4).map(function (intent) {
      return {
        intent: intent,
        confidence: Number((scores[intent] / Math.max(total, 1)).toFixed(2))
      };
    });
    return {
      intent: topIntent,
      confidence: Number(confidence.toFixed(2)),
      alternatives: alternatives
    };
  }
}

/**
 * 情感分析引擎
 * 负责分析用户输入的情感
 */
class EmotionAnalyzer {
  constructor() {
    // 积极情感词汇
    this.positiveWords = ['开心', '高兴', '满意', '喜欢', '好', '棒', '优秀', '赞', '谢谢', '感谢', '不错', '完美', '厉害'];
    // 消极情感词汇
    this.negativeWords = ['生气', '不满', '失望', '讨厌', '差', '糟', '坏', '问题', '错误', '故障', '投诉', '难用', '崩溃', '愤怒'];
    // 中性情感词汇
    this.neutralWords = ['请问', '咨询', '了解', '看看', '一般', '还行', '可以'];
  }

  /**
   * 分析文本情感
   * @param {string} text - 用户输入文本
   * @returns {{emotion: string, score: number, suggestions: Array}} 情感分析结果
   */
  analyze(text) {
    if (!text || typeof text !== 'string') {
      return { emotion: 'neutral', score: 0.5, suggestions: [] };
    }
    const lowerText = text.toLowerCase();
    let posCount = 0;
    let negCount = 0;
    let neuCount = 0;
    const self = this;
    this.positiveWords.forEach(function (w) { if (lowerText.indexOf(w) !== -1) posCount++; });
    this.negativeWords.forEach(function (w) { if (lowerText.indexOf(w) !== -1) negCount++; });
    this.neutralWords.forEach(function (w) { if (lowerText.indexOf(w) !== -1) neuCount++; });
    const total = posCount + negCount + neuCount;
    const suggestions = [];
    if (total === 0) {
      return { emotion: 'neutral', score: 0.5, suggestions: ['请提供更多信息以便我更好理解您的需求。'] };
    }
    if (posCount >= negCount && posCount >= neuCount) {
      suggestions.push('很高兴您有良好的体验，我会继续保持服务质量。');
      return { emotion: 'positive', score: Number((posCount / total).toFixed(2)), suggestions: suggestions };
    }
    if (negCount > neuCount) {
      suggestions.push('非常抱歉给您带来不好的体验，我们会尽快改进。');
      suggestions.push('请告诉我具体问题，我会全力协助您解决。');
      return { emotion: 'negative', score: Number((1 - negCount / total).toFixed(2)), suggestions: suggestions };
    }
    suggestions.push('感谢您的咨询，请告诉我更多细节。');
    return { emotion: 'neutral', score: 0.5, suggestions: suggestions };
  }
}

/**
 * 对话历史记录管理
 * 负责存储和检索多轮对话历史
 */
class DialogHistory {
  /**
   * @param {number} maxLength - 最大历史记录条数，默认50
   */
  constructor(maxLength) {
    this.maxLength = maxLength || 50;
    // 使用Map按会话ID存储历史记录
    this.history = new Map();
  }

  /**
   * 添加对话记录
   * @param {string} sessionId - 会话ID
   * @param {string} role - 角色(user/assistant)
   * @param {string} content - 内容
   */
  add(sessionId, role, content) {
    if (!sessionId) sessionId = 'default';
    if (!this.history.has(sessionId)) {
      this.history.set(sessionId, []);
    }
    const records = this.history.get(sessionId);
    records.push({
      role: role,
      content: content,
      timestamp: Date.now()
    });
    // 超过最大长度时，移除最早的记录
    while (records.length > this.maxLength) {
      records.shift();
    }
  }

  /**
   * 获取会话历史
   * @param {string} sessionId - 会话ID
   * @returns {Array} 历史记录数组
   */
  get(sessionId) {
    if (!sessionId) sessionId = 'default';
    return this.history.get(sessionId) || [];
  }

  /**
   * 清除会话历史
   * @param {string} sessionId - 会话ID
   */
  clear(sessionId) {
    if (this.history.has(sessionId)) {
      this.history.delete(sessionId);
    }
  }
}

/**
 * 上下文管理器
 * 负责管理对话上下文，支持跨会话上下文继承
 */
class ContextManager {
  constructor() {
    // 按会话ID存储上下文
    this.contexts = new Map();
    // 会话继承关系：子会话 -> 父会话
    this.inheritance = new Map();
  }

  /**
   * 设置会话继承关系，实现跨会话上下文继承
   * @param {string} childSessionId - 子会话ID
   * @param {string} parentSessionId - 父会话ID
   */
  setInheritance(childSessionId, parentSessionId) {
    this.inheritance.set(childSessionId, parentSessionId);
  }

  /**
   * 设置上下文键值
   * @param {string} sessionId - 会话ID
   * @param {string} key - 键
   * @param {*} value - 值
   */
  set(sessionId, key, value) {
    if (!sessionId) sessionId = 'default';
    if (!this.contexts.has(sessionId)) {
      this.contexts.set(sessionId, {});
    }
    this.contexts.get(sessionId)[key] = value;
  }

  /**
   * 获取上下文键值，支持跨会话继承查找
   * @param {string} sessionId - 会话ID
   * @param {string} key - 键
   * @returns {*} 值，不存在则返回undefined
   */
  get(sessionId, key) {
    if (!sessionId) sessionId = 'default';
    // 先从当前会话查找
    if (this.contexts.has(sessionId)) {
      const ctx = this.contexts.get(sessionId);
      if (Object.prototype.hasOwnProperty.call(ctx, key)) {
        return ctx[key];
      }
    }
    // 若存在继承关系，递归从父会话查找
    if (this.inheritance.has(sessionId)) {
      const parentId = this.inheritance.get(sessionId);
      return this.get(parentId, key);
    }
    return undefined;
  }

  /**
   * 获取完整上下文对象，合并继承链上的上下文
   * @param {string} sessionId - 会话ID
   * @returns {object} 上下文对象
   */
  getContext(sessionId) {
    if (!sessionId) sessionId = 'default';
    let parentContext = {};
    // 若存在继承关系，先获取父会话上下文
    if (this.inheritance.has(sessionId)) {
      parentContext = this.getContext(this.inheritance.get(sessionId));
    }
    const currentContext = this.contexts.get(sessionId) || {};
    // 合并：当前会话优先覆盖父会话
    return Object.assign({}, parentContext, currentContext);
  }
}

/**
 * 超级对话流主引擎
 * 整合意图识别、情感分析、历史记录和上下文管理
 */
class SuperDialogFlowEngine {
  constructor() {
    // 初始化所有组件
    this.configs = DialogFlowConfigs;
    this.intentRecognizer = new IntentRecognizer();
    this.emotionAnalyzer = new EmotionAnalyzer();
    this.history = new DialogHistory(50);
    this.contextManager = new ContextManager();
  }

  /**
   * 处理用户输入，返回完整回复结果
   * @param {string} text - 用户输入文本
   * @param {object} options - 选项 {dialog_type, session_id, context}
   * @returns {object} 处理结果
   */
  processInput(text, options) {
    options = options || {};
    const sessionId = options.session_id || 'default';
    const userInput = text || '';
    // 自动检测或使用指定的对话类型
    const dialogType = options.dialog_type || this.detectDialogType(userInput);
    // 识别意图
    const intentResult = this.intentRecognizer.recognize(userInput);
    // 情感分析
    const emotionResult = this.emotionAnalyzer.analyze(userInput);
    // 合并用户传入的上下文
    if (options.context && typeof options.context === 'object') {
      for (const key in options.context) {
        if (Object.prototype.hasOwnProperty.call(options.context, key)) {
          this.contextManager.set(sessionId, key, options.context[key]);
        }
      }
    }
    const context = this.contextManager.getContext(sessionId);
    // 记录用户输入到历史
    this.history.add(sessionId, 'user', userInput);
    // 生成回复
    const response = this.generateResponse(userInput, dialogType, context);
    // 记录助手回复到历史
    this.history.add(sessionId, 'assistant', response);
    // 合并建议列表
    const suggestions = emotionResult.suggestions.slice();
    return {
      response: response,
      intent: intentResult.intent,
      emotion: {
        emotion: emotionResult.emotion,
        score: emotionResult.score
      },
      dialog_type: dialogType,
      confidence: intentResult.confidence,
      suggestions: suggestions
    };
  }

  /**
   * 自动检测对话类型
   * @param {string} text - 用户输入文本
   * @returns {string} 对话类型ID
   */
  detectDialogType(text) {
    if (!text) return 'customer_service';
    const lowerText = text.toLowerCase();
    // 各对话类型的关键词特征
    const typeKeywords = {
      code_assistant: ['代码', '编程', '函数', 'bug', '程序', '编译', '调试', 'api', '代码审查', '算法'],
      content_creator: ['文案', '营销', '广告词', '内容创作', '推文', '宣传'],
      tech_support: ['故障', '报错', '无法', '崩溃', '技术支持', '排查', '异常', '登录不了'],
      knowledge_qa: ['什么是', '为什么', '解释', '科普', '原理', '定义', '历史', '知识'],
      creative_assistant: ['写故事', '小说', '诗歌', '剧本', '创作', '灵感', '角色'],
      data_analyst: ['数据分析', '统计', '报表', '图表', '指标', '数据可视化', '趋势'],
      automation_helper: ['自动化', '脚本', '批处理', '效率', '流程自动化', '定时任务'],
      customer_service: ['客服', '咨询', '投诉', '退款', '订单', '售后', '服务']
    };
    let bestType = 'customer_service';
    let bestScore = 0;
    for (const type in typeKeywords) {
      let score = 0;
      for (const kw of typeKeywords[type]) {
        if (lowerText.indexOf(kw.toLowerCase()) !== -1) {
          score++;
        }
      }
      if (score > bestScore) {
        bestScore = score;
        bestType = type;
      }
    }
    return bestType;
  }

  /**
   * 生成回复内容
   * @param {string} text - 用户输入文本
   * @param {string} dialogType - 对话类型
   * @param {object} context - 上下文
   * @returns {string} 回复内容
   */
  generateResponse(text, dialogType, context) {
    const config = this.configs[dialogType] || this.configs.customer_service;
    const templates = config.reply_templates;
    // 基于文本长度选择模板，保证回复多样性
    const index = text ? (text.length % templates.length) : 0;
    let response = templates[index];
    // 若上下文中存在用户称呼，个性化回复
    if (context && context.user_name) {
      response = context.user_name + '，' + response;
    }
    return response;
  }

  /**
   * 列出所有对话类型
   * @returns {Array} 对话类型列表
   */
  listDialogTypes() {
    return Object.keys(this.configs).map(function (key) {
      const cfg = DialogFlowConfigs[key];
      return {
        id: cfg.id,
        name: cfg.name,
        persona: cfg.persona
      };
    });
  }
}

/**
 * 创建引擎实例的便捷函数
 * @returns {SuperDialogFlowEngine} 引擎实例
 */
function createEngine() {
  return new SuperDialogFlowEngine();
}

/**
 * 快捷单轮对话函数
 * @param {string} text - 用户输入文本
 * @param {object} options - 选项
 * @returns {object} 对话结果
 */
function quickChat(text, options) {
  const engine = createEngine();
  return engine.processInput(text, options);
}

// 导出模块（Node.js环境）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    DialogFlowConfigs: DialogFlowConfigs,
    IntentRecognizer: IntentRecognizer,
    EmotionAnalyzer: EmotionAnalyzer,
    DialogHistory: DialogHistory,
    ContextManager: ContextManager,
    SuperDialogFlowEngine: SuperDialogFlowEngine,
    createEngine: createEngine,
    quickChat: quickChat
  };
}

// 导出至全局（浏览器环境）
if (typeof window !== 'undefined') {
  window.SuperDialogFlow = {
    DialogFlowConfigs: DialogFlowConfigs,
    IntentRecognizer: IntentRecognizer,
    EmotionAnalyzer: EmotionAnalyzer,
    DialogHistory: DialogHistory,
    ContextManager: ContextManager,
    SuperDialogFlowEngine: SuperDialogFlowEngine,
    createEngine: createEngine,
    quickChat: quickChat
  };
}
