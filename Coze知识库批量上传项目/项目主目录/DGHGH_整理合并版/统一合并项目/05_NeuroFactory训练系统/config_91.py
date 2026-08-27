"""
function authentication(config) {
  if (config.auth_type === 'api_key' && config.api_key) {
    return { 'X-API-Key': config.api_key };
  }
  if (config.auth_type === 'bearer' && config.bearer_token) {
    return { 'Authorization': `Bearer ${config.bearer_token}` };
  }
  if (config.auth_type === 'both' && config.api_key && config.bearer_token) {
    return {
      'X-API-Key': config.api_key,
      'Authorization': `Bearer ${config.bearer_token}`
    };
  }
  throw new Error('认证配置错误：请提供有效的认证信息');
}
"""
