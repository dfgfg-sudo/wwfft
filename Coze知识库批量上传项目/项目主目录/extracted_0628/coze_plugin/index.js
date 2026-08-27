const fs = require('fs');
const path = require('path');
const JSON5 = require('json5');
const CodeExecutor = require('./executor');

class ConversationsParser {
  constructor() {
    this.config = {
      filePath: 'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\extracted_0628\\conversations.json',
      userFilePath: 'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\extracted_0628\\user.json'
    };
    this.conversations = [];
    this.userInfo = null;
    this.executor = new CodeExecutor();
    this.loadedModules = {};
    this.executionHistory = [];
  }

  async loadData() {
    try {
      const convData = fs.readFileSync(this.config.filePath, 'utf-8');
      this.conversations = JSON5.parse(convData);
      
      const userData = fs.readFileSync(this.config.userFilePath, 'utf-8');
      this.userInfo = JSON5.parse(userData);
      
      return { success: true, message: '数据加载成功', count: this.conversations.length };
    } catch (error) {
      return { success: false, message: `加载失败: ${error.message}` };

  getAllConversations() {
    return this.conversations.map(conv => ({
      id: conv.id,
      title: conv.title,
      createdAt: conv.inserted_at,
      updatedAt: conv.updated_at,
      hasMapping: !!conv.mapping,
      nodeCount: conv.mapping ? Object.keys(conv.mapping).length : 0
    }));

  getConversationById(id) {
    return this.conversations.find(conv => conv.id === id);

  extractAllCodeBlocks() {
    const codeBlocks = [];
    
    this.conversations.forEach(conv => {
      if (conv.mapping) {
        Object.values(conv.mapping).forEach((node, nodeId) => {
          if (node.message && node.message.fragments) {
            node.message.fragments.forEach((frag, fragIdx) => {
              if (frag.type === 'REQUEST' && frag.content) {
                const matches = frag.content.match(/```(\w+)?\n([\s\S]*?)```/g);
                if (matches) {
                  matches.forEach((match, matchIdx) => {
                    const langMatch = match.match(/```(\w+)?/);
                    const code = match.replace(/```(\w+)?\n?/g, '').trim();
                    codeBlocks.push({
                      id: `${conv.id}-${nodeId}-${fragIdx}-${matchIdx}`,
                      conversationId: conv.id,
                      conversationTitle: conv.title,
                      language: langMatch ? langMatch[1] || 'text' : 'text',
                      code: code,
                      lineCount: code.split('\n').length,
                      nodeId: nodeId,
                      fragmentIndex: fragIdx
                    });
    
    return codeBlocks;

  extractSystemModules() {
    const modules = [];
    const modulePatterns = [
      { name: '量子增强核心系统', pattern: /class QuantumEnhancedSystem/, type: 'core' },
      { name: '全局配置中心', pattern: /class SystemConfig|class NeuroConfig/, type: 'config' },
      { name: '模型安全管理系统', pattern: /class ModelVault/, type: 'security' },
      { name: '智能数据处理系统', pattern: /class DataChef|class NeuroDataChef/, type: 'data' },
      { name: '自适应训练系统', pattern: /class NeuroTrainer|class AdaptiveTrainer/, type: 'training' },
      { name: '增强推理引擎', pattern: /class NeuroThinker|class QuantumInference/, type: 'inference' },
      { name: '企业级交互界面', pattern: /class NeuroDashboard|class EnterpriseUI/, type: 'ui' },
      { name: '安全加密子系统', pattern: /class QuantumSafeEncryptor/, type: 'security' },
      { name: '量子化记忆系统', pattern: /class QuantumMemory|class QuantizedMemory/, type: 'memory' }
    ];

        Object.values(conv.mapping).forEach(node => {
            node.message.fragments.forEach(frag => {
              if (frag.content) {
                modulePatterns.forEach(mod => {
                  if (mod.pattern.test(frag.content)) {
                    if (!modules.find(m => m.name === mod.name)) {
                      modules.push({
                        name: mod.name,
                        type: mod.type,
                        foundInFragment: true,
                        code: this._extractClassCode(frag.content, mod.pattern)

    return modules;

  _extractClassCode(content, pattern) {
    const match = content.match(new RegExp(`(${pattern.source}[\\s\\S]*?)(?=\\nclass|\\ndef\\s|$)`));
    return match ? match[1].trim() : '';

  extractFunctions() {
    const functions = [];
    const funcPattern = /def\s+(\w+)\s*\([^)]*\)/g;

                let match;
                while ((match = funcPattern.exec(frag.content)) !== null) {
                  functions.push({
                    name: match[1],
                    conversationTitle: conv.title

    return [...new Map(functions.map(f => [f.name, f])).values()];

  async executeCodeBlock(codeBlockId) {
    const codeBlocks = this.extractAllCodeBlocks();
    const codeBlock = codeBlocks.find(cb => cb.id === codeBlockId);
    
    if (!codeBlock) {
      return { success: false, message: '未找到指定的代码块' };

      const result = await this.executor.executePythonCode(codeBlock.code);
      
      this.executionHistory.push({
        timestamp: new Date().toISOString(),
        codeBlockId: codeBlockId,
        conversationTitle: codeBlock.conversationTitle,
        language: codeBlock.language,
        success: result.success,
        result: result.success ? result.result : result.error

      return {
        success: true,
        message: '代码执行完成',
        codeBlock: codeBlock,
        result: result,
        historyIndex: this.executionHistory.length - 1
      return { success: false, message: `执行错误: ${error.message}` };

  async executeModule(moduleName) {
    const modules = this.extractSystemModules();
    const module = modules.find(m => m.name === moduleName);
    
    if (!module) {
      return { success: false, message: '未找到指定的模块' };

      const parsed = this.executor._executePythonInNode(module.code);
      this.loadedModules[moduleName] = parsed;

        message: `模块 ${moduleName} 解析完成`,
        module: module,
        parsedContent: parsed
      return { success: false, message: `解析错误: ${error.message}` };

  getModuleInfo(moduleName) {
    
      return null;

    
      name: module.name,
      type: module.type,
      source: module.conversationTitle,
      classCount: parsed.classes.length,
      methodCount: parsed.classes.reduce((acc, cls) => acc + cls.methods.length, 0),
      functions: parsed.functions.map(f => f.name)

  runAllModules() {
    const results = [];

    modules.forEach(module => {
        this.loadedModules[module.name] = parsed;
        results.push({
          status: 'success',
          classes: parsed.classes.length,
          methods: parsed.classes.reduce((acc, cls) => acc + cls.methods.length, 0)
          status: 'error',
          error: error.message

    return results;

  generateDocumentation() {
    const functions = this.extractFunctions();
    
    let doc = `# Conversations.json 技术文档\n\n`;
    doc += `---\n\n`;
    doc += `## 📋 文档概览\n\n`;
    doc += `- **对话数量**: ${this.conversations.length}\n`;
    doc += `- **系统模块数**: ${modules.length}\n`;
    doc += `- **代码块数**: ${codeBlocks.length}\n`;
    doc += `- **函数数**: ${functions.length}\n`;
    
    if (this.userInfo) {
      doc += `- **用户ID**: ${this.userInfo.user_id}\n`;
      if (this.userInfo.oauth_profiles && this.userInfo.oauth_profiles[0]) {
        doc += `- **用户名**: ${this.userInfo.oauth_profiles[0].name}\n`;
    
    doc += `\n## 🧩 系统模块清单\n\n`;
    doc += `| 序号 | 模块名称 | 类型 | 来源对话 |\n`;
    doc += `|------|---------|------|----------|\n`;
    modules.forEach((mod, index) => {
      doc += `| ${index + 1} | **${mod.name}** | ${this._getTypeLabel(mod.type)} | ${mod.conversationTitle} |\n`;
    
    doc += `\n## 📦 代码块统计\n\n`;
    const langStats = {};
    codeBlocks.forEach(block => {
      langStats[block.language] = (langStats[block.language] || 0) + 1;
    doc += `| 语言 | 数量 |\n`;
    doc += `|------|------|\n`;
    Object.entries(langStats).forEach(([lang, count]) => {
      doc += `| ${lang} | ${count} |\n`;
    
    doc += `\n## 🔧 函数列表\n\n`;
    functions.forEach((func, index) => {
      doc += `${index + 1}. `${func.name}` (来自: ${func.conversationTitle})\n`;
    
    return doc;

  _getTypeLabel(type) {
    const labels = {
      'core': '核心系统',
      'config': '配置管理',
      'security': '安全模块',
      'data': '数据处理',
      'training': '训练系统',
      'inference': '推理引擎',
      'ui': '用户界面',
      'memory': '记忆系统'
    return labels[type] || type;

  getConversationContent(id) {
    const conv = this.getConversationById(id);
    if (!conv) return null;

    const contents = [];
              contents.push({
                type: frag.type,
                content: frag.content,
                codeBlocks: this._extractCodeFromContent(frag.content)

      contents: contents

  _extractCodeFromContent(content) {
    const matches = content.match(/```(\w+)?\n([\s\S]*?)```/g) || [];
    return matches.map(match => {
        code: code

  getExecutionHistory() {
    return this.executionHistory;

  getLoadedModules() {
    return Object.keys(this.loadedModules).map(name => ({
      name: name,
      content: this.loadedModules[name]

  getCompleteAnalysis() {
      metadata: {
        totalConversations: this.conversations.length,
        totalCodeBlocks: this.extractAllCodeBlocks().length,
        totalModules: this.extractSystemModules().length,
        totalFunctions: this.extractFunctions().length,
        userInfo: this.userInfo
      },
      conversations: this.getAllConversations(),
      modules: this.extractSystemModules(),
      functions: this.extractFunctions(),
      codeBlocks: this.extractAllCodeBlocks(),
      loadedModules: this.getLoadedModules(),
      executionHistory: this.getExecutionHistory()

module.exports = ConversationsParser;