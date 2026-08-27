// 使用Redis缓存
const redis = require('redis')
const client = redis.createClient({
  url: process.env.REDIS_URL
})

// 缓存需求分析结果
async function getCachedAnalysis(description) {
  const cacheKey = `analysis:${hash(description)}`
  const cached = await client.get(cacheKey)
  
  if (cached) {
    return JSON.parse(cached)
  }
  
  // 重新分析并缓存
  const analysis = await analyzeRequirements(description)
  await client.setex(cacheKey, 3600, JSON.stringify(analysis)) // 缓存1小时
  
  return analysis
}

// 缓存生成的项目
async function cacheProject(projectId, project) {
  const cacheKey = `project:${projectId}`
  await client.setex(cacheKey, 1800, JSON.stringify(project)) // 缓存30分钟
}