"""
// weather-plugin.js
const coze = require('@coze-dev/coze-node-sdk');
const axios = require('axios');
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 300 }); // 5分钟缓存

/**
 * 主函数 - Coze 入口
 * @param {Object} args - { city, district, language, units }
 * @returns {Object} 标准化响应
 */
async function main(args) {
  const { city, district = '', language = 'zh-CN', units = 'metric' } = args;
  
  // 参数校验
  if (!city || typeof city !== 'string') {
    return { success: false, code: 400, message: '城市名称不能为空' };
  }

  // 构建缓存键
  const cacheKey = `weather:${city}:${district}:${language}:${units}`;
  const cached = cache.get(cacheKey);
  if (cached) {
    return { success: true, code: 200, message: '缓存命中', data: cached, fromCache: true };
  }

  try {
    // 调用真实 API（示例用模拟数据）
    const mockData = {
      location: { city, district: district || '市区' },
      current: {
        temperature: 25,
        humidity: 60,
        weather: '晴',
        wind_speed: 3.2,
        feels_like: 26,
        uv_index: 5,
        pressure: 1013,
        visibility: 10,
        update_time: new Date().toISOString()
      }
    };

    // 增强数据：生成生活建议
    const recommendations = generateRecommendations(mockData.current);
    const result = {
      ...mockData,
      recommendations,
      health_indices: calculateHealthIndices(mockData.current),
      display: formatDisplay(mockData.current, units)
    };

    // 写入缓存
    cache.set(cacheKey, result);

    return {
      success: true,
      code: 200,
      message: '成功获取天气',
      data: result,
      fromCache: false,
      metadata: { timestamp: new Date().toISOString() }
    };
  } catch (error) {
    return {
      success: false,
      code: 500,
      message: `服务异常: ${error.message}`,
      data: null
    };
  }
}

/** 辅助函数：生成生活建议 */
function generateRecommendations(current) {
  const { temperature, humidity, weather } = current;
  let clothing = '';
  if (temperature >= 28) clothing = '炎热，穿短袖、短裤，注意防晒';
  else if (temperature >= 22) clothing = '温暖，T恤、薄外套即可';
  else if (temperature >= 15) clothing = '凉爽，长袖、薄毛衣';
  else if (temperature >= 5) clothing = '较冷，毛衣、厚外套';
  else clothing = '寒冷，羽绒服、帽子手套';

  let activity = '适合户外活动';
  if (weather.includes('雨')) activity = '不适宜户外，建议室内运动';
  else if (weather.includes('雪')) activity = '路面湿滑，谨慎出行';

  return { clothing, activity };
}

/** 辅助函数：健康指数 */
function calculateHealthIndices(current) {
  const { temperature, humidity } = current;
  const comfort = Math.max(0, 100 - Math.abs(temperature - 22) * 2 - Math.abs(humidity - 50) * 0.5);
  return { comfort };
}

/** 辅助函数：格式化显示 */
function formatDisplay(current, units) {
  const isMetric = units === 'metric';
  return {
    temperature: isMetric ? `${current.temperature}°C` : `${Math.round(current.temperature * 9/5 + 32)}°F`,
    humidity: `${current.humidity}%`,
    wind: `${current.wind_speed} m/s`
  };
}

// 注册 Coze 工具
const tool = new coze.Tool(
  {
    name: '智能天气助手',
    description: '查询实时天气并生成生活建议',
    parameters: {
      type: coze.ParameterType.Object,
      properties: {
        city: { type: coze.ParameterType.String, description: '城市名称' },
        district: { type: coze.ParameterType.String, description: '区县（可选）' },
        language: { type: coze.ParameterType.String, enum: ['zh-CN', 'en-US'], default: 'zh-CN' },
        units: { type: coze.ParameterType.String, enum: ['metric', 'imperial'], default: 'metric' }
      },
      required: ['city']
    }
  },
  main
);

module.exports = tool;
"""
