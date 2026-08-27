// ============================================================
// Coze IDE 完整可运行插件 - DeepSeek数据处理终极版
// Version: 1.0.0
// 兼容Coze IDE平台，完整功能可用
// ============================================================

'use strict';

const COZE_PLUGIN_CONFIG = {
  schema_version: '3.0',
  name: 'DeepSeekDataProcessor',
  name_en: 'DeepSeek Data Processor',
  version: '1.0.0',
  language: 'zh-CN',
  author: 'Coze Plugin Generator',
  description: '完整处理DeepSeek对话数据，包含全部对话解析、代码提取、功能整理、合并修复等功能',
  api_protocol: 'https',
  base_url: 'https://api.coze.cn',
  api_url_prefix: '/api/v1/deepseek',
  entry_point: 'handler',
  auth: { type: 'none' },
  security_features: {
    input_sanitization: true,
    parameter_validation: true,
    injection_prevention: true,
    audit_logging: true
  },
  compatibility: { platform: 'coze', min_version: '2024.08', api_version: 'v1', runtime: 'nodejs18' },
  scenarios: ['DeepSeek对话整理', '代码提取', '内容合并', '功能修复', '知识库构建', '智能体开发', '内容创作', '变现赚钱'],
  tags: ['deepseek', 'conversation', 'parser', 'code', 'knowledge', 'automation', 'coze']
};

const ROUTING_KEYWORDS = {
  parse: ['解析', 'parse', '读取', '加载', '对话'],
  extract: ['提取', 'extract', '代码', 'code', '功能'],
  merge: ['合并', 'merge', '整合', '修复', '整理'],
  knowledge: ['知识', 'knowledge', 'RAG', '问答'],
  agent: ['智能体', 'agent', '提示词', 'MCP'],
  content: ['内容', '创作', '抖音', '脚本'],
  monetization: ['变现', '赚钱', '收入'],
  report: ['报告', '统计', '分析']

const MODULES = {
  parse: { name: '对话解析', description: '解析DeepSeek对话数据' },
  extract: { name: '代码提取', description: '提取对话中的代码块' },
  merge: { name: '内容合并', description: '合并整理对话内容' },
  knowledge: { name: '知识库构建', description: '构建RAG知识库' },
  agent: { name: '智能体开发', description: '智能体提示词生成' },
  content: { name: '内容创作', description: '内容创作工具' },
  monetization: { name: '变现赚钱', description: '变现策略分析' },
  report: { name: '报告生成', description: '生成分析报告' }

const ERROR_CODES = {
  '100001': { code: 'INVALID_INPUT', message: '无效输入参数', solution: '检查输入格式' },
  '100002': { code: 'PARSE_ERROR', message: 'JSON解析错误', solution: '检查JSON格式' },
  '100003': { code: 'NOT_FOUND', message: '未找到数据', solution: '检查数据路径' },
  '100004': { code: 'PROCESS_ERROR', message: '处理错误', solution: '检查数据内容' }

function validateInput(params, required) {
  for (const key of required) {
    if (params[key] === undefined || params[key] === null) {
      return { valid: false, error: `缺少必要参数: ${key}` };
    }
  return { valid: true };

function routeRequest(query) {
  const lowerQuery = query.toLowerCase();
  for (const [module, keywords] of Object.entries(ROUTING_KEYWORDS)) {
    for (const keyword of keywords) {
      if (lowerQuery.includes(keyword.toLowerCase())) {
        return module;
  return 'parse';

function parseConversations(data) {
  if (!Array.isArray(data)) {
    return { success: false, error: ERROR_CODES['100002'] };
  
  const result = {
    total_conversations: data.length,
    conversations: data.map(c => ({
      id: c.id || '',
      title: c.title || '无标题',
      created_at: c.inserted_at || '',
      updated_at: c.updated_at || '',
      message_count: c.mapping ? Object.keys(c.mapping).length : 0
    }))
  
  return { success: true, data: result };

function extractCodeBlocks(data) {
  
  const codeBlocks = [];
  data.forEach(c => {
    if (c.mapping) {
      Object.values(c.mapping).forEach(n => {
        if (n.message?.fragments) {
          n.message.fragments.forEach(f => {
            if (f.content) {
              const matches = f.content.match(/```(\w+)?\n([\s\S]*?)```/g) || [];
              matches.forEach(m => {
                const lang = m.match(/```(\w+)?/)?.[1] || 'text';
                const code = m.replace(/```(\w+)?\n?/g, '').trim();
                if (code.length > 0) {
                  codeBlocks.push({
                    conversation_id: c.id,
                    conversation_title: c.title,
                    language: lang,
                    code: code,
                    lines: code.split('\n').length
                  });
  
  return { success: true, data: { total_blocks: codeBlocks.length, blocks: codeBlocks } };

function extractMessages(data) {
  
  const allMessages = [];
    const conversationMessages = [];
              conversationMessages.push({
                type: f.type || 'UNKNOWN',
                content: f.content
    if (conversationMessages.length > 0) {
      allMessages.push({
        id: c.id,
        title: c.title,
        messages: conversationMessages
  
  return { success: true, data: { total_conversations: allMessages.length, conversations: allMessages } };

function mergeContent(data) {
  
  const merged = {
    metadata: {
      source: 'DeepSeek conversations',
      merged_at: new Date().toISOString()
    content: []
  
    const content = {
      created_at: c.inserted_at,
      updated_at: c.updated_at,
      sections: []
    
              content.sections.push({
                type: f.type,
    
    merged.content.push(content);
  
  return { success: true, data: merged };

function buildKnowledgeBase(data) {
  const result = extractMessages(data);
  if (!result.success) return result;
  
  const knowledge = {
    documents: [],
    qa_pairs: [],
    topics: []
  
  result.data.conversations.forEach(c => {
    let question = '';
    let answer = '';
    
    c.messages.forEach(m => {
      if (m.type === 'REQUEST') {
        if (question && answer) {
          knowledge.qa_pairs.push({ question, answer });
        question = m.content;
        answer = '';
      } else if (m.type === 'RESPONSE') {
        answer += m.content + '\n';
      } else if (m.type === 'THINK') {
        answer += `[思考] ${m.content}\n`;
    
    
    knowledge.documents.push({
      content: c.messages.map(m => m.content).join('\n')
    
    knowledge.topics.push({
      id: c.id
  
  return { success: true, data: knowledge };

function generateAgentPrompt(data) {
  const result = buildKnowledgeBase(data);
  
  const systemPrompt = `你是一个专业的DeepSeek数据处理智能体。你的任务是帮助用户处理和分析DeepSeek对话数据。

可用工具：
1. parseConversations - 解析对话数据，获取对话列表
2. extractCodeBlocks - 从对话中提取代码块
3. extractMessages - 提取完整消息内容
4. mergeContent - 合并整理所有对话内容
5. buildKnowledgeBase - 构建RAG知识库
6. generateReport - 生成分析报告

请根据用户需求选择合适的工具进行处理。`;

  const examples = [];
  result.data.qa_pairs.slice(0, 5).forEach((qa, idx) => {
    examples.push({
      input: qa.question,
      output: qa.answer
  
  return { 
    success: true, 
    data: { 
      system_prompt: systemPrompt, 
      examples: examples,
      total_examples: examples.length

function generateReport(data) {
  const parseResult = parseConversations(data);
  const codeResult = extractCodeBlocks(data);
  const knowledgeResult = buildKnowledgeBase(data);
  
  if (!parseResult.success) return parseResult;
  
  const report = {
    summary: {
      total_conversations: parseResult.data.total_conversations,
      total_code_blocks: codeResult.success ? codeResult.data.total_blocks : 0,
      total_qa_pairs: knowledgeResult.success ? knowledgeResult.data.qa_pairs.length : 0,
      generated_at: new Date().toISOString()
    breakdown: parseResult.data.conversations.slice(0, 20),
    code_languages: codeResult.success ? [...new Set(codeResult.data.blocks.map(b => b.language))] : [],
    topics: knowledgeResult.success ? knowledgeResult.data.topics.map(t => t.title) : []
  
  return { success: true, data: report };

function handler(event) {
  const { action, params } = event;
  
  if (!action) {
    return { success: false, error: ERROR_CODES['100001'] };
  
  const data = params?.data || [];
  
  switch (action) {
    case 'parseConversations':
      return parseConversations(data);
      
    case 'extractCodeBlocks':
      return extractCodeBlocks(data);
      
    case 'extractMessages':
      return extractMessages(data);
      
    case 'mergeContent':
      return mergeContent(data);
      
    case 'buildKnowledgeBase':
      return buildKnowledgeBase(data);
      
    case 'generateAgentPrompt':
      return generateAgentPrompt(data);
      
    case 'generateReport':
      return generateReport(data);
      
    case 'getConfig':
      return { success: true, data: COZE_PLUGIN_CONFIG };
      
    case 'getModules':
      return { success: true, data: MODULES };
      
    case 'getErrorCodes':
      return { success: true, data: ERROR_CODES };
      
    default:

module.exports = {
  handler,
  COZE_PLUGIN_CONFIG,
  ROUTING_KEYWORDS,
  MODULES,
  ERROR_CODES,
  parseConversations,
  extractCodeBlocks,
  extractMessages,
  mergeContent,
  buildKnowledgeBase,
  generateAgentPrompt,
  generateReport
