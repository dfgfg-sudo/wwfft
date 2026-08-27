class ImportErrorHandler {
  static handle(error, context) {
    const errorMap = {
      'INVALID_FORMAT': {
        code: 4001,
        message: '文件格式无效',
        userMessage: '请上传JSON、YAML或ZIP格式的文件'
      },
      'MISSING_NODES': {
        code: 4002,
        message: '配置缺少节点定义',
        userMessage: '配置文件必须包含至少一个节点'
      },
      'API_UNAUTHORIZED': {
        code: 5001,
        message: 'API认证失败',
        userMessage: '系统配置错误，请联系管理员'
      },
      'NETWORK_ERROR': {
        code: 5002,
        message: '网络连接失败',
        userMessage: '网络不稳定，请稍后重试'
      }
    };
    
    // 尝试匹配已知错误
    for (const [key, info] of Object.entries(errorMap)) {
      if (error.message.includes(key) || error.message.includes(info.message)) {
        return {
          ...info,
          details: error.message,
          timestamp: new Date().toISOString()
        };
      }
    }
    
    // 未知错误
    return {
      code: 9999,
      message: '未知错误',
      userMessage: '导入过程中发生未知错误',
      details: error.message,
      timestamp: new Date().toISOString()
    };
  }
}