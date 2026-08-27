// ============================================================
// Coze IDE 完整可运行插件 - DeepSeek数据处理终极版
// Version: 1.0.0
// ============================================================

'use strict';

const COZE_CONFIG = {
  schema_version: '3.0',
  name: 'DeepSeekDataProcessor',
  name_en: 'DeepSeek Data Processor',
  version: '1.0.0',
  language: 'zh-CN',
  author: 'Coze Plugin Generator',
  description: '完整处理DeepSeek对话数据',
  api_protocol: 'https',
  base_url: 'https://api.coze.cn',
  api_url_prefix: '/api/v1/deepseek',
  entry_point: 'handler',
  auth: { type: 'none' },
  security_features: { input_sanitization: true, parameter_validation: true },
  compatibility: { platform: 'coze', min_version: '2024.08', api_version: 'v1', runtime: 'nodejs18' },
  scenarios: ['DeepSeek对话整理', '代码提取', '内容合并', '知识库构建'],
  tags: ['deepseek', 'conversation', 'parser', 'code', 'knowledge']
};

function parseConversations(data) {
  if (!Array.isArray(data)) return { success: false, error: '无效数据格式' };
  return {
    success: true,
    data: {
      total: data.length,
      list: data.map(c => ({
        id: c.id || '',
        title: c.title || '无标题',
        created: c.inserted_at || '',
        updated: c.updated_at || ''
      }))
    }

function extractCodeBlocks(data) {
  const blocks = [];
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
                blocks.push({ conversation: c.title, language: lang, code });
              });
  return { success: true, data: { total: blocks.length, blocks } };

function extractMessages(data) {
  const conversations = [];
    const msgs = [];
            if (f.content) msgs.push({ type: f.type, content: f.content });
    conversations.push({ id: c.id, title: c.title, messages: msgs });
  return { success: true, data: conversations };

function mergeContent(data) {
  const result = extractMessages(data);
  if (!result.success) return result;
  const merged = {
    metadata: { source: 'DeepSeek', total: result.data.length, merged_at: new Date().toISOString() },
    conversations: result.data
  return { success: true, data: merged };

function buildKnowledgeBase(data) {
  const qa = [];
  result.data.forEach(c => {
    let q = '', a = '';
    c.messages.forEach(m => {
      if (m.type === 'REQUEST') { q = m.content; a = ''; }
      else if (m.type === 'RESPONSE') a += m.content + '\n';
    if (q && a) qa.push({ question: q, answer: a });
  return { success: true, data: { total_qa: qa.length, qa_pairs: qa } };

function generateReport(data) {
  const parse = parseConversations(data);
  const code = extractCodeBlocks(data);
  const kb = buildKnowledgeBase(data);
      summary: {
        total_conversations: parse.success ? parse.data.total : 0,
        total_code_blocks: code.success ? code.data.total : 0,
        total_qa_pairs: kb.success ? kb.data.total_qa : 0

function handler(event) {
  const { action, params } = event;
  const data = params?.data || [];
  
  switch (action) {
    case 'parseConversations': return parseConversations(data);
    case 'extractCodeBlocks': return extractCodeBlocks(data);
    case 'extractMessages': return extractMessages(data);
    case 'mergeContent': return mergeContent(data);
    case 'buildKnowledgeBase': return buildKnowledgeBase(data);
    case 'generateReport': return generateReport(data);
    case 'getConfig': return { success: true, data: COZE_CONFIG };
    default: return { success: false, error: '未知操作' };

module.exports = { handler };
