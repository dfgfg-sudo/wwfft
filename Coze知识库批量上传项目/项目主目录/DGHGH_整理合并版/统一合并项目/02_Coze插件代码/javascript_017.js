// 安全实践示例
class SecureConfig {
  static getApiKey() {
    // 1. 优先使用环境变量
    if (process.env.CHILD_PROCESS_KEY) {
      return process.env.CHILD_PROCESS_KEY;
    }
    
    // 2. 使用密钥管理服务（如AWS KMS、腾讯云KMS）
    if (process.env.KMS_ENCRYPTED_KEY) {
      return this.decryptWithKMS(process.env.KMS_ENCRYPTED_KEY);
    }
    
    // 3. 临时方案：配置文件（不推荐生产环境）
    const config = require('../config/secure.json');
    return config.apiKey;
  }
  
  static decryptWithKMS(encrypted) {
    // 实现KMS解密逻辑
    // 这需要具体的云服务SDK
  }
}

// Auto-generated exports
module.exports = {
  SecureConfig,
};
