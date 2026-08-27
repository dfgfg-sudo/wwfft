const ConversationsParser = require('./index');

class ConversationsPlugin {
  constructor() {
    this.parser = new ConversationsParser();
    this.initialized = false;
  }

  async initialize() {
    if (!this.initialized) {
      const result = await this.parser.loadData();
      this.initialized = result.success;
      return result;
    return { success: true, message: 'Already initialized' };

  async handleRequest(command, params) {
    switch (command) {
      case 'parseConversations':
        return await this.parseConversations(params);
      case 'extractCodeBlocks':
        return await this.extractCodeBlocks(params);
      case 'generateDocumentation':
        return await this.generateDocumentation(params);
      case 'listSystems':
        return await this.listSystems(params);
      case 'executeModule':
        return await this.executeModule(params);
      case 'runAllModules':
        return await this.runAllModules(params);
      case 'getAnalysis':
        return await this.getAnalysis(params);
      default:
        return { success: false, message: `Unknown command: ${command}` };

  async parseConversations(params) {
    try {
      const conversations = this.parser.getAllConversations();
      return {
        success: true,
        data: conversations,
        count: conversations.length
      };
    } catch (error) {
      return { success: false, message: error.message };

  async extractCodeBlocks(params) {
      const codeBlocks = this.parser.extractAllCodeBlocks();
      const filtered = params?.language 
        ? codeBlocks.filter(cb => cb.language === params.language)
        : codeBlocks;
        data: filtered,
        count: filtered.length

  async generateDocumentation(params) {
      const doc = this.parser.generateDocumentation();
      const format = params?.format || 'markdown';
      
      if (params?.saveToFile) {
        const fs = require('fs');
        const path = require('path');
        const outputPath = path.join(__dirname, 'documentation.md');
        fs.writeFileSync(outputPath, doc);
          data: doc,
          savedTo: outputPath,
          format: format
      

  async listSystems(params) {
      const modules = this.parser.extractSystemModules();
      const info = modules.map(m => ({
        name: m.name,
        type: m.type,
        source: m.conversationTitle
      }));
        data: info,
        count: info.length

  async executeModule(params) {
      const moduleName = params?.moduleName;
      if (!moduleName) {
        return { success: false, message: 'moduleName is required' };
      
      const result = await this.parser.executeModule(moduleName);

  async runAllModules(params) {
      const results = this.parser.runAllModules();
        data: results,
        successCount: results.filter(r => r.status === 'success').length,
        totalCount: results.length

  async getAnalysis(params) {
      const analysis = this.parser.getCompleteAnalysis();
        data: analysis

module.exports = ConversationsPlugin;