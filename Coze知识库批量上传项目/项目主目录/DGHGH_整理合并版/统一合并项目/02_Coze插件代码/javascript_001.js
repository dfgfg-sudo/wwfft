// packages/api-server/src/services/projectService.js
const { OpenAI } = require('openai')
const { ChatOpenAI } = require('langchain/chat_models/openai')
const { LLMChain, PromptTemplate } = require('langchain/chains')
const fs = require('fs').promises
const path = require('path')
const { v4: uuidv4 } = require('uuid')
const archiver = require('archiver')
const { promisify } = require('util')
const { pipeline } = require('stream')
const pipelineAsync = promisify(pipeline)

class ProjectService {
  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    })
    
    this.llm = new ChatOpenAI({
      openAIApiKey: process.env.OPENAI_API_KEY,
      temperature: 0.3,
      modelName: 'gpt-4'
    })
    
    this.projects = new Map() // 项目存储（实际项目中应该用数据库）
    this.templates = new Map() // 模板存储
  }
  
  /**
   * 分析用户需求
   */
  async analyzeRequirements(description, userPreferences = {}) {
    console.log('开始需求分析...')
    
    try {
      // 构建分析提示
      const prompt = PromptTemplate.fromTemplate(`
        你是一个资深软件架构师。请分析以下用户需求，并提供详细的技术方案：
        
        需求描述：{description}
        
        用户偏好：{preferences}
        
        请提供以下分析：
        1. 项目类型（电商、博客、SaaS等）
        2. 核心功能模块
        3. 推荐技术栈（前端、后端、数据库）
        4. 数据库设计建议
        5. API设计建议
        6. 部署架构建议
        7. 开发时间估算
        
        以JSON格式返回：
        {{
          "project_type": "类型",
          "core_modules": ["模块1", "模块2"],
          "technology_stack": {{
            "frontend": {{"framework": "框架", "language": "语言"}},
            "backend": {{"framework": "框架", "language": "语言"}},
            "database": "数据库"
          }},
          "database_design": {{"tables": [], "relationships": []}},
          "api_design": {{"endpoints": [], "authentication": "方案"}},
          "deployment_architecture": "架构描述",
          "timeline_estimate": "时间估算"
        }}
      `)
      
      const chain = new LLMChain({
        llm: this.llm,
        prompt: prompt
      })
      
      // 执行分析
      const result = await chain.call({
        description: description,
        preferences: JSON.stringify(userPreferences)
      })
      
      // 解析JSON结果
      let analysis
      try {
        analysis = JSON.parse(result.text)
      } catch (error) {
        // 如果解析失败，使用正则提取JSON
        const jsonMatch = result.text.match(/\{[\s\S]*\}/)
        if (jsonMatch) {
          analysis = JSON.parse(jsonMatch[0])
        } else {
          throw new Error('无法解析AI返回结果')
        }
      }
      
      // 添加分析ID和时间戳
      analysis.analysis_id = uuidv4()
      analysis.created_at = new Date().toISOString()
      analysis.original_description = description
      
      console.log('需求分析完成')
      return analysis
      
    } catch (error) {
      console.error('需求分析失败:', error)
      throw new Error(`需求分析失败: ${error.message}`)
    }
  }
  
  /**
   * 生成完整项目
   */
  async generateProject(projectData, analysisResult, userId) {
    console.log('开始生成项目...')
    
    try {
      const projectId = uuidv4()
      const projectName = projectData.name || `project-${projectId.slice(0, 8)}`
      
      // 创建项目对象
      const project = {
        id: projectId,
        name: projectName,
        description: projectData.description,
        analysis: analysisResult,
        user_id: userId,
        status: 'generating',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        files: {},
        structure: {}
      }
      
      // 生成项目结构
      project.structure = await this.generateProjectStructure(analysisResult)
      
      // 生成项目文件
      project.files = await this.generateProjectFiles(project)
      
      // 更新状态
      project.status = 'generated'
      project.updated_at = new Date().toISOString()
      
      // 存储项目
      this.projects.set(projectId, project)
      
      console.log(`项目生成完成: ${projectId}`)
      return project
      
    } catch (error) {
      console.error('项目生成失败:', error)
      throw new Error(`项目生成失败: ${error.message}`)
    }
  }
  
  /**
   * 生成项目结构
   */
  async generateProjectStructure(analysisResult) {
    const projectType = analysisResult.project_type
    const techStack = analysisResult.technology_stack
    
    const structure = {
      frontend: [],
      backend: [],
      database: [],
      infrastructure: [],
      docs: [],
      tests: []
    }
    
    // 根据项目类型和技术栈生成结构
    switch (projectType) {
      case '电子商务':
        structure.frontend = [
          'src/',
          'public/',
          'components/',
          'pages/',
          'store/',
          'utils/',
          'styles/'
        ]
        
        structure.backend = [
          'src/',
          'api/',
          'models/',
          'services/',
          'middleware/',
          'config/'
        ]
        
        structure.database = [
          'migrations/',
          'seeds/',
          'schemas/'
        ]
        break
        
      case '博客平台':
        structure.frontend = [
          'src/',
          'components/',
          'pages/',
          'layouts/',
          'utils/',
          'styles/'
        ]
        
        structure.backend = [
          'src/',
          'controllers/',
          'models/',
          'routes/',
          'middleware/'
        ]
        break
        
      // 其他项目类型...
    }
    
    // 根据技术栈调整结构
    if (techStack.frontend.framework === 'React') {
      structure.frontend.push('hooks/', 'context/')
    }
    
    if (techStack.backend.framework === 'NestJS') {
      structure.backend = ['src/', 'test/', 'dist/']
    }
    
    return structure
  }
  
  /**
   * 生成项目文件
   */
  async generateProjectFiles(project) {
    const files = {}
    const analysis = project.analysis
    
    // 1. 生成配置文件
    files['package.json'] = await this.generatePackageJson(project)
    files['README.md'] = await this.generateReadme(project)
    files['.env.example'] = await this.generateEnvExample(project)
    files['.gitignore'] = await this.generateGitignore(project)
    
    // 2. 生成前端文件
    if (analysis.technology_stack.frontend) {
      files['frontend/'] = {}
      const frontendFiles = await this.generateFrontendFiles(project)
      Object.assign(files['frontend/'], frontendFiles)
    }
    
    // 3. 生成后端文件
    if (analysis.technology_stack.backend) {
      files['backend/'] = {}
      const backendFiles = await this.generateBackendFiles(project)
      Object.assign(files['backend/'], backendFiles)
    }
    
    // 4. 生成数据库文件
    if (analysis.database_design) {
      files['database/'] = {}
      const dbFiles = await this.generateDatabaseFiles(project)
      Object.assign(files['database/'], dbFiles)
    }
    
    // 5. 生成部署配置
    files['deploy/'] = {}
    const deployFiles = await this.generateDeploymentFiles(project)
    Object.assign(files['deploy/'], deployFiles)
    
    // 6. 生成文档
    files['docs/'] = {}
    const docsFiles = await this.generateDocumentationFiles(project)
    Object.assign(files['docs/'], docsFiles)
    
    return files
  }
  
  /**
   * 生成package.json
   */
  async generatePackageJson(project) {
    const analysis = project.analysis
    const techStack = analysis.technology_stack
    
    const packageJson = {
      name: project.name,
      version: '1.0.0',
      description: project.description || 'Auto-generated project',
      main: 'backend/src/index.js',
      scripts: {
        'start': 'node backend/src/index.js',
        'dev': 'concurrently "npm run dev:backend" "npm run dev:frontend"',
        'dev:backend': 'cd backend && npm run dev',
        'dev:frontend': 'cd frontend && npm run dev',
        'build': 'concurrently "npm run build:backend" "npm run build:frontend"',
        'build:backend': 'cd backend && npm run build',
        'build:frontend': 'cd frontend && npm run build',
        'test': 'concurrently "npm run test:backend" "npm run test:frontend"',
        'lint': 'concurrently "npm run lint:backend" "npm run lint:frontend"',
        'deploy': 'bash deploy/deploy.sh'
      },
      dependencies: {},
      devDependencies: {
        'concurrently': '^8.0.0'
      },
      engines: {
        'node': '>=18.0.0',
        'npm': '>=9.0.0'
      },
      keywords: ['autogenerated', 'autocode', project.analysis.project_type],
      author: 'AutoCode Pro',
      license: 'MIT'
    }
    
    // 添加前端依赖
    if (techStack.frontend.framework === 'React') {
      packageJson.dependencies = {
        ...packageJson.dependencies,
        'react': '^18.0.0',
        'react-dom': '^18.0.0',
        'react-router-dom': '^6.0.0',
        'axios': '^1.0.0'
      }
    }
    
    // 添加后端依赖
    if (techStack.backend.framework === 'NestJS') {
      packageJson.dependencies = {
        ...packageJson.dependencies,
        '@nestjs/core': '^9.0.0',
        '@nestjs/common': '^9.0.0',
        '@nestjs/platform-express': '^9.0.0'
      }
    }
    
    return JSON.stringify(packageJson, null, 2)
  }
  
  /**
   * 生成README.md
   */
  async generateReadme(project) {
    const analysis = project.analysis
    
    return `# ${project.name}

${project.description || '这是一个自动生成的项目'}

## 项目概述

这是一个使用 AutoCode Pro 自动生成的 ${analysis.project_type} 项目。

## 功能特性

${analysis.core_modules.map(module => `- ${module}`).join('\n')}

## 技术栈

- **前端**: ${analysis.technology_stack.frontend.language} + ${analysis.technology_stack.frontend.framework}
- **后端**: ${analysis.technology_stack.backend.language} + ${analysis.technology_stack.backend.framework}
- **数据库**: ${analysis.technology_stack.database}
- **部署**: ${analysis.deployment_architecture}

## 快速开始

### 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0
- Docker (可选，用于容器化部署)

### 安装依赖

```bash
npm install
```

### 配置环境变量

复制环境变量示例文件并修改配置：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

### 启动开发环境

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 运行测试

```bash
npm run test
```

## 项目结构

```
${JSON.stringify(project.structure, null, 2)}
```

## API 文档

${analysis.api_design.endpoints.map(endpoint => `
### ${endpoint.method} ${endpoint.path}
${endpoint.description}
`).join('\n')}

## 部署

查看 [deploy/README.md](./deploy/README.md) 获取详细的部署指南。

## 许可证

MIT
`
  }
  
  /**
   * 创建项目ZIP包
   */
  async createProjectZip(projectId, outputStream) {
    const project = this.projects.get(projectId)
    if (!project) {
      throw new Error('项目不存在')
    }
    
    const archive = archiver('zip', {
      zlib: { level: 9 } // 最高压缩级别
    })
    
    // 处理错误
    archive.on('error', (err) => {
      throw err
    })
    
    // 管道输出到流
    archive.pipe(outputStream)
    
    // 添加项目文件
    await this.addFilesToArchive(archive, project.files, '')
    
    // 完成归档
    await archive.finalize()
    
    return archive
  }
  
  /**
   * 递归添加文件到归档
   */
  async addFilesToArchive(archive, files, basePath) {
    for (const [name, content] of Object.entries(files)) {
      const fullPath = path.join(basePath, name)
      
      if (typeof content === 'object') {
        // 如果是目录，递归添加
        if (name.endsWith('/')) {
          archive.append(null, { name: fullPath })
          await this.addFilesToArchive(archive, content, fullPath)
        }
      } else {
        // 如果是文件，添加内容
        archive.append(content, { name: fullPath })
      }
    }
  }
  
  /**
   * 获取用户项目列表
   */
  async getUserProjects(userId, page = 1, limit = 10) {
    // 过滤用户的项目
    const userProjects = Array.from(this.projects.values())
      .filter(project => project.user_id === userId)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    
    // 分页
    const start = (page - 1) * limit
    const end = start + limit
    
    return {
      projects: userProjects.slice(start, end),
      pagination: {
        page,
        limit,
        total: userProjects.length,
        pages: Math.ceil(userProjects.length / limit)
      }
    }
  }
  
  /**
   * 获取项目详情
   */
  async getProjectById(projectId) {
    const project = this.projects.get(projectId)
    if (!project) {
      throw new Error('项目不存在')
    }
    
    return project
  }
  
  /**
   * 更新项目
   */
  async updateProject(projectId, updates) {
    const project = this.projects.get(projectId)
    if (!project) {
      throw new Error('项目不存在')
    }
    
    // 更新项目信息
    Object.assign(project, updates, {
      updated_at: new Date().toISOString()
    })
    
    this.projects.set(projectId, project)
    return project
  }
  
  /**
   * 删除项目
   */
  async deleteProject(projectId) {
    if (!this.projects.has(projectId)) {
      throw new Error('项目不存在')
    }
    
    this.projects.delete(projectId)
    return true
  }
  
  /**
   * 克隆项目
   */
  async cloneProject(projectId, newName, userId) {
    const originalProject = this.projects.get(projectId)
    if (!originalProject) {
      throw new Error('原项目不存在')
    }
    
    const newProjectId = uuidv4()
    
    // 创建克隆项目
    const clonedProject = {
      ...originalProject,
      id: newProjectId,
      name: newName,
      user_id: userId,
      cloned_from: projectId,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    
    // 移除敏感信息
    delete clonedProject.files
    delete clonedProject.status
    
    this.projects.set(newProjectId, clonedProject)
    
    return clonedProject
  }
  
  /**
   * 获取项目模板
   */
  async getTemplates(category = null) {
    const templates = [
      {
        id: 'ecommerce-template',
        name: '电商平台模板',
        category: '电子商务',
        description: '完整的电子商务解决方案，包含用户系统、商品管理、订单处理、支付集成等',
        features: ['用户管理', '商品展示', '购物车', '订单系统', '支付集成', '后台管理'],
        technology_stack: {
          frontend: { framework: 'React', language: 'TypeScript' },
          backend: { framework: 'NestJS', language: 'TypeScript' },
          database: 'PostgreSQL'
        },
        created_at: '2024-01-01T00:00:00Z',
        usage_count: 1250
      },
      {
        id: 'blog-template',
        name: '博客平台模板',
        category: '内容管理',
        description: '现代化博客系统，支持文章发布、分类标签、评论系统、SEO优化等',
        features: ['文章管理', '分类标签', '评论系统', '用户订阅', 'SEO优化', '后台编辑'],
        technology_stack: {
          frontend: { framework: 'Vue.js', language: 'JavaScript' },
          backend: { framework: 'Express', language: 'Node.js' },
          database: 'MongoDB'
        },
        created_at: '2024-01-01T00:00:00Z',
        usage_count: 890
      },
      {
        id: 'saas-template',
        name: 'SaaS应用模板',
        category: 'SaaS',
        description: '多租户SaaS应用模板，包含用户管理、订阅计费、仪表板、API接口等',
        features: ['多租户', '用户管理', '订阅计费', '仪表板', '数据报表', 'API接口'],
        technology_stack: {
          frontend: { framework: 'React', language: 'TypeScript' },
          backend: { framework: 'NestJS', language: 'TypeScript' },
          database: 'PostgreSQL'
        },
        created_at: '2024-01-01T00:00:00Z',
        usage_count: 540
      }
    ]
    
    if (category) {
      return templates.filter(template => template.category === category)
    }
    
    return templates
  }
  
  /**
   * 从模板创建项目
   */
  async createFromTemplate(templateId, projectData, userId) {
    const templates = await this.getTemplates()
    const template = templates.find(t => t.id === templateId)
    
    if (!template) {
      throw new Error('模板不存在')
    }
    
    // 使用模板作为分析基础
    const analysis = {
      project_type: template.category,
      core_modules: template.features,
      technology_stack: template.technology_stack,
      database_design: {
        tables: [],
        relationships: []
      },
      api_design: {
        endpoints: [],
        authentication: 'JWT'
      },
      deployment_architecture: 'Docker + Nginx',
      timeline_estimate: '2-4周'
    }
    
    // 生成项目
    return await this.generateProject({
      name: projectData.name,
      description: projectData.description || template.description
    }, analysis, userId)
  }
  
  /**
   * 导出项目配置
   */
  async exportProjectConfig(projectId) {
    const project = this.projects.get(projectId)
    if (!project) {
      throw new Error('项目不存在')
    }
    
    return {
      project_id: project.id,
      name: project.name,
      description: project.description,
      analysis: project.analysis,
      structure: project.structure,
      created_at: project.created_at,
      updated_at: project.updated_at
    }
  }
  
  /**
   * 导入项目配置
   */
  async importProjectConfig(config, userId) {
    const projectId = uuidv4()
    
    const project = {
      id: projectId,
      name: config.name,
      description: config.description,
      analysis: config.analysis,
      user_id: userId,
      status: 'imported',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      files: {},
      structure: config.structure
    }
    
    this.projects.set(projectId, project)
    
    return project
  }
}

module.exports = ProjectService