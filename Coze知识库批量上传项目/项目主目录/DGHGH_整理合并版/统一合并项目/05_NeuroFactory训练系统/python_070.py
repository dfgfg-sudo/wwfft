"""
# src/ai/ci_cd_parser.py
from typing import Dict, List, Optional, Any
import json
import yaml
import re
from enum import Enum
from pydantic import BaseModel, Field
import openai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

class PipelineStep(str, Enum):
    \"\"\"流水线步骤枚举\"\"\"
    LINT = "代码检查"
    BUILD = "构建"
    TEST_UNIT = "单元测试"
    TEST_INTEGRATION = "集成测试"
    TEST_E2E = "端到端测试"
    SECURITY_SCAN = "安全扫描"
    DOCKER_BUILD = "Docker构建"
    DEPLOY_STAGING = "部署到测试环境"
    DEPLOY_PRODUCTION = "部署到生产环境"
    NOTIFICATION = "通知"
    DATABASE_MIGRATION = "数据库迁移"

class TechnologyStack(BaseModel):
    \"\"\"技术栈模型\"\"\"
    language: str = Field(..., description="编程语言")
    framework: Optional[str] = Field(None, description="框架")
    package_manager: Optional[str] = Field(None, description="包管理器")
    build_tool: Optional[str] = Field(None, description="构建工具")
    test_framework: Optional[str] = Field(None, description="测试框架")

class DeploymentTarget(BaseModel):
    \"\"\"部署目标模型\"\"\"
    platform: str = Field(..., description="平台: kubernetes, docker-compose, aws, etc.")
    service_type: Optional[str] = Field(None, description="服务类型: web, api, worker, etc.")
    scaling: Optional[Dict] = Field(None, description="扩缩容配置")

class CICDRequirements(BaseModel):
    \"\"\"CI/CD需求模型\"\"\"
    project_type: str = Field(..., description="项目类型: webapp, api, mobile, library")
    tech_stack: TechnologyStack
    pipeline_steps: List[PipelineStep]
    deployment_targets: List[DeploymentTarget]
    branch_strategy: Optional[str] = Field("github-flow", description="分支策略")
    notifications: Optional[List[str]] = Field(["slack", "email"], description="通知方式")
    monitoring: Optional[List[str]] = Field(["prometheus"], description="监控")
    special_requirements: Optional[List[str]] = Field([], description="特殊需求")
    
    class Config:
        use_enum_values = True

class CICDParser:
    \"\"\"CI/CD需求解析器\"\"\"
    
    def __init__(self, openai_api_key: str):
        \"\"\"初始化解析器\"\"\"
        self.openai_api_key = openai_api_key
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.llm = ChatOpenAI(
            temperature=0.3,
            model_name="gpt-4",
            openai_api_key=openai_api_key
        )
        
        # 预定义的技术栈识别模式
        self.tech_patterns = {
            "languages": {
                "python": ["python", "py", "django", "flask", "fastapi"],
                "javascript": ["javascript", "js", "node", "nodejs", "react", "vue", "angular"],
                "typescript": ["typescript", "ts"],
                "java": ["java", "spring", "springboot"],
                "go": ["go", "golang", "gin"],
                "rust": ["rust"],
                "php": ["php", "laravel"],
                "ruby": ["ruby", "rails"]
            },
            "frameworks": {
                "react": ["react", "nextjs"],
                "vue": ["vue", "nuxt"],
                "angular": ["angular"],
                "django": ["django"],
                "flask": ["flask"],
                "fastapi": ["fastapi"],
                "spring": ["spring", "springboot"],
                "express": ["express", "expressjs"]
            },
            "databases": {
                "postgresql": ["postgres", "postgresql"],
                "mysql": ["mysql", "mariadb"],
                "mongodb": ["mongodb", "mongo"],
                "redis": ["redis"]
            }
    🤖 CI/CD工作流智能生成器

🎯 项目概述

这是一个通过自然语言描述自动生成CI/CD工作流的AI工具。用户只需用中文或英文描述需求，系统就能自动生成完整的CI/CD配置文件。

📦 完整项目实现

1. 项目初始化配置
"""
