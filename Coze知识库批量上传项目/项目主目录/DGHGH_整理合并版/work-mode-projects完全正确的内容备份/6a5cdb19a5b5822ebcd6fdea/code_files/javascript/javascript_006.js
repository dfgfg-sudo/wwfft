const { BaseNode } = require('coze-plugin-sdk');
const JsonParser = require('../parsers/json-parser');
const YamlParser = require('../parsers/yaml-parser');
const ZipParser = require('../parsers/zip-parser');
const CozeAPIClient = require('../utils/coze-api-client');

class WorkflowImporterNode extends BaseNode {
  constructor() {
    super('workflow-importer');
    
    // 初始化解析器
    this.parsers = {
      'json': new JsonParser(),
      'yaml': new YamlParser(),
      'yml': new YamlParser(),
      'zip': new ZipParser()
    };
    
    // 初始化API客户端
    this.apiClient = new CozeAPIClient();
  }
  
  async execute(inputs, context) {
    try {
      const { configFile, targetWorkspace, overrideExisting } = inputs;
      
      // 1. 验证输入
      if (!configFile || !configFile.content) {
        throw new Error('未提供有效的配置文件');
      }
      
      // 2. 确定文件类型
      const fileExt = this.getFileExtension(configFile.name);
      const parser = this.parsers[fileExt];
      
      if (!parser) {
        throw new Error(`不支持的文件格式: ${fileExt}`);
      }
      
      // 3. 解析配置文件
      const workflowData = await parser.parse(configFile.content);
      
      // 4. 验证数据结构
      this.validateWorkflowData(workflowData);
      
      // 5. 调用Coze API创建工作流
      const result = await this.apiClient.createWorkflow({
        workspaceId: targetWorkspace || context.workspaceId,
        workflowData,
        options: {
          override: overrideExisting
        }
      });
      
      // 6. 返回成功结果
      return {
        success: true,
        workflowId: result.id,
        workflowName: result.name,
        errorMessage: null
      };
      
    } catch (error) {
      // 错误处理
      console.error('导入工作流失败:', error);
      
      return {
        success: false,
        workflowId: null,
        workflowName: null,
        errorMessage: error.message
      };
    }
  }
  
  getFileExtension(filename) {
    return filename.toLowerCase().split('.').pop();
  }
  
  validateWorkflowData(data) {
    // 基本验证规则
    const requiredFields = ['name', 'nodes'];
    for (const field of requiredFields) {
      if (!data[field]) {
        throw new Error(`配置文件缺少必需字段: ${field}`);
      }
    }
    
    // 验证节点结构
    if (!Array.isArray(data.nodes)) {
      throw new Error('nodes字段必须是数组');
    }
    
    // 可以添加更多验证规则
    // 例如：节点类型验证、连接关系验证等
  }
  
  // 节点配置元数据
  static get metadata() {
    return require('../../config/node-config.json').importerNode;
  }
}

module.exports = WorkflowImporterNode;