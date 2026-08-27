const axios = require('axios');

class CozeAPIClient {
  constructor() {
    // 从环境变量或配置获取
    this.baseURL = process.env.COZE_API_BASE_URL || 'https://api.coze.cn/v1';
    this.apiKey = process.env.COZE_API_KEY;
    
    if (!this.apiKey) {
      console.warn('COZE_API_KEY环境变量未设置');
    }
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
  
  async createWorkflow({ workspaceId, workflowData, options = {} }) {
    try {
      // 构建请求数据
      const requestData = this.buildCreateRequest(workflowData, options);
      
      // 发送请求
      const response = await this.client.post(
        `/workspaces/${workspaceId}/workflows`,
        requestData,
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`
          }
        }
      );
      
      return response.data;
      
    } catch (error) {
      console.error('调用Coze API失败:', error.response?.data || error.message);
      
      if (error.response) {
        throw new Error(`API错误: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
      } else {
        throw new Error(`网络错误: ${error.message}`);
      }
    }
  }
  
  buildCreateRequest(workflowData, options) {
    // 这里需要根据Coze实际API要求构建请求体
    // 这是最复杂的部分，需要深入研究Coze的内部数据结构
    
    const request = {
      workflow: {
        name: workflowData.name,
        description: workflowData.description || '',
        nodes: this.convertNodes(workflowData.nodes),
        edges: workflowData.edges || [],
        variables: workflowData.variables || {},
        metadata: {
          source: 'import-plugin',
          import_time: new Date().toISOString(),
          original_format: workflowData._format
        }
      },
      options: {
        validate: true,
        publish: options.publish || false,
        override: options.override || false
      }
    };
    
    return request;
  }
  
  convertNodes(userNodes) {
    // 将用户定义的节点转换为Coze内部节点格式
    // 需要实现详尽的类型映射
    return userNodes.map(node => {
      const baseNode = {
        id: node.id,
        type: this.mapNodeType(node.type),
        name: node.name || `节点_${node.id}`,
        position: node.position || { x: 0, y: 0 }
      };
      
      // 根据节点类型添加特定配置
      switch (node.type) {
        case 'start':
          baseNode.config = { variables: node.variables };
          break;
        case 'llm':
          baseNode.config = {
            model: node.model,
            prompt: node.prompt,
            parameters: node.parameters
          };
          break;
        case 'condition':
          baseNode.config = {
            conditions: node.conditions,
            default_branch: node.default
          };
          break;
        // 更多类型处理...
        default:
          baseNode.config = node.config || {};
      }
      
      return baseNode;
    });
  }
  
  mapNodeType(userType) {
    // 节点类型映射表
    const typeMap = {
      'start': 'coze:start',
      'end': 'coze:end',
      'llm': 'coze:llm',
      'condition': 'coze:condition',
      'http': 'coze:http',
      'code': 'coze:code',
      // 更多映射...
    };
    
    return typeMap[userType] || userType;
  }
}

module.exports = CozeAPIClient;