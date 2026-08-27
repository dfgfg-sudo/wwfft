# packages/core/src/ai_engine/requirement_analyzer.py
import json
import re
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import openai
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

class ProjectType(Enum):
    """项目类型枚举"""
    ECOMMERCE = "电子商务"
    BLOG = "博客平台"
    SAAS = "SaaS应用"
    CMS = "内容管理系统"
    SOCIAL = "社交网络"
    ANALYTICS = "数据分析平台"
    MOBILE_APP = "移动应用"
    DESKTOP_APP = "桌面应用"
    API_SERVICE = "API服务"
    LIBRARY = "代码库"

@dataclass
class TechnologyRecommendation:
    """技术推荐"""
    category: str
    technology: str
    version: str
    rationale: str
    alternatives: List[str]
    dependencies: List[str]

@dataclass
class FeatureSpecification:
    """功能规格"""
    name: str
    description: str
    priority: int
    user_stories: List[str]
    acceptance_criteria: List[str]
    estimated_effort: str
    dependencies: List[str]
    technical_requirements: Dict[str, Any]

@dataclass
class DatabaseDesign:
    """数据库设计"""
    tables: List[Dict]
    relationships: List[Dict]
    indexes: List[Dict]
    constraints: List[Dict]
    migration_strategy: str
    seed_data: Dict[str, List]

@dataclass
class APIDesign:
    """API设计"""
    endpoints: List[Dict]
    authentication: Dict
    rate_limiting: Dict
    versioning: str
    error_handling: Dict

class RequirementAnalyzer:
    """需求分析引擎"""
    
    def __init__(self, openai_api_key: str, config_path: str = "config/patterns.yaml"):
        """
        初始化需求分析器
        
        Args:
            openai_api_key: OpenAI API密钥
            config_path: 配置文件路径
        """
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.llm = ChatOpenAI(
            temperature=0.3,
            model_name="gpt-4",
            openai_api_key=openai_api_key,
            request_timeout=60
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化向量数据库（用于相似需求检索）
        self.vector_store = None
        self._init_vector_store()
        
        # 技术栈知识库
        self.tech_knowledge_base = self._load_tech_knowledge()
        
    def _init_vector_store(self):
        """初始化向量数据库"""
        # 加载历史项目文档
        documents = []
        
        # 添加示例项目文档
        examples = [
            ("电商平台", "需要用户注册、商品展示、购物车、订单管理、支付集成、后台管理等功能"),
            ("博客系统", "需要文章发布、分类标签、评论系统、用户订阅、SEO优化、Markdown编辑器"),
            ("SaaS应用", "需要多租户、订阅计费、仪表板、数据报表、API接口、Webhook支持"),
            ("内容管理系统", "需要多用户权限、内容发布、工作流审批、版本控制、媒体库管理"),
            ("社交网络", "需要用户资料、关注系统、消息功能、动态发布、社区管理、内容分享")
        ]
        
        for title, desc in examples:
            documents.append(Document(
                page_content=desc,
                metadata={"title": title, "type": "example"}
            ))
        
        if documents:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
    
    def _load_tech_knowledge(self) -> Dict:
        """加载技术栈知识库"""
        return {
            "电子商务": {
                "frontend": {
                    "technology": "React + TypeScript",
                    "framework": "Next.js",
                    "state_management": "Redux Toolkit",
                    "ui_library": "Ant Design",
                    "version": "Latest",
                    "rationale": "适合电商的高性能SSR和SEO需求",
                    "dependencies": ["react", "react-dom", "next", "antd", "redux-toolkit"]
                },
                "backend": {
                    "technology": "Node.js",
                    "framework": "NestJS",
                    "database": "PostgreSQL + Redis",
                    "orm": "TypeORM",
                    "api_documentation": "Swagger/OpenAPI",
                    "version": "Latest",
                    "rationale": "企业级架构，支持微服务扩展",
                    "dependencies": ["@nestjs/core", "typeorm", "pg", "redis", "@nestjs/swagger"]
                },
                "mobile": {
                    "technology": "React Native",
                    "framework": "Expo",
                    "state_management": "MobX",
                    "version": "Latest",
                    "rationale": "跨平台，快速开发",
                    "dependencies": ["react-native", "expo", "mobx", "react-navigation"]
                },
                "devops": {
                    "containerization": "Docker",
                    "orchestration": "Kubernetes",
                    "ci_cd": "GitHub Actions",
                    "monitoring": "Prometheus + Grafana",
                    "logging": "ELK Stack"
                }
            },
            # 更多项目类型的配置...
        }
    
    def analyze(self, description: str, user_preferences: Dict = None) -> Dict[str, Any]:
        """
        分析用户需求
        
        Args:
            description: 自然语言需求描述
            user_preferences: 用户偏好设置
            
        Returns:
            详细的需求分析结果
        """
        print("🔍 开始分析用户需求...")
        
        # 1. 预处理和清理
        cleaned_description = self._preprocess_description(description)
        
        # 2. 查找相似项目
        similar_projects = self._find_similar_projects(cleaned_description)
        
        # 3. 提取核心需求
        core_requirements = self._extract_core_requirements(cleaned_description)
        
        # 4. 识别项目类型
        project_type = self._identify_project_type(cleaned_description, core_requirements)
        
        # 5. 使用AI进行深度分析
        ai_analysis = self._ai_deep_analysis(cleaned_description, project_type)
        
        # 6. 生成功能规格
        feature_specs = self._generate_feature_specifications(
            cleaned_description, 
            project_type, 
            ai_analysis.get("features", [])
        )
        
        # 7. 技术选型
        tech_choices = self._select_technologies(
            project_type, 
            feature_specs, 
            user_preferences
        )
        
        # 8. 数据库设计
        database_design = self._design_database(project_type, feature_specs)
        
        # 9. API设计
        api_design = self._design_apis(project_type, feature_specs)
        
        # 10. UI/UX建议
        ui_design = self._suggest_ui_design(project_type, feature_specs)
        
        # 11. 项目结构设计
        project_structure = self._design_project_structure(project_type, tech_choices)
        
        # 12. 估算时间和成本
        estimation = self._estimate_timeline_and_cost(feature_specs, tech_choices)
        
        # 13. 生成开发计划
        development_plan = self._create_development_plan(feature_specs)
        
        return {
            "project_type": project_type,
            "core_requirements": core_requirements,
            "feature_specifications": feature_specs,
            "technology_choices": tech_choices,
            "database_design": database_design,
            "api_design": api_design,
            "ui_design_suggestions": ui_design,
            "project_structure": project_structure,
            "similar_projects": similar_projects,
            "estimation": estimation,
            "development_plan": development_plan,
            "risk_assessment": self._assess_risks(feature_specs, tech_choices),
            "success_metrics": self._define_success_metrics(project_type)
        }
    
    def _preprocess_description(self, description: str) -> str:
        """预处理需求描述"""
        # 移除多余空白
        cleaned = re.sub(r'\s+', ' ', description.strip())
        
        # 提取中文和英文部分
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        english_pattern = re.compile(r'[a-zA-Z]+')
        
        chinese_parts = chinese_pattern.findall(cleaned)
        english_parts = english_pattern.findall(cleaned)
        
        # 保留关键信息
        keywords = []
        for part in chinese_parts + english_parts:
            if len(part) > 1:  # 忽略单个字符
                keywords.append(part)
        
        return ' '.join(keywords) if keywords else cleaned
    
    def _find_similar_projects(self, description: str) -> List[Dict]:
        """查找相似项目"""
        if not self.vector_store:
            return []
        
        try:
            docs = self.vector_store.similarity_search(description, k=3)
            return [
                {
                    "title": doc.metadata.get("title", "未知"),
                    "description": doc.page_content[:100] + "...",
                    "similarity_score": 0.8  # 简化评分
                }
                for doc in docs
            ]
        except Exception as e:
            print(f"向量搜索失败: {e}")
            return []
    
    def _extract_core_requirements(self, description: str) -> List[str]:
        """提取核心需求点"""
        prompt = f"""
        请从以下用户描述中提取核心软件需求点：
        
        描述：{description}
        
        要求：
        1. 每个需求点应该明确、具体、可测试
        2. 使用动词开头（如：支持、实现、提供、允许等）
        3. 区分功能需求和非功能需求
        4. 按优先级排序
        
        格式：
        [
          "需求点1 - [高/中/低]优先级",
          "需求点2 - [高/中/低]优先级"
        ]
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是资深的产品经理，擅长需求分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            # 解析JSON或纯文本
            if result.startswith('[') and result.endswith(']'):
                return json.loads(result)
            else:
                # 提取行
                lines = [line.strip() for line in result.split('\n') if line.strip()]
                return lines
                
        except Exception as e:
            print(f"AI提取失败: {e}")
            return self._rule_based_extraction(description)
    
    def _rule_based_extraction(self, description: str) -> List[str]:
        """基于规则的需求提取"""
        requirements = []
        description_lower = description.lower()
        
        # 常见需求模式
        patterns = {
            "用户管理": ["用户", "注册", "登录", "账户", "权限"],
            "数据管理": ["添加", "删除", "修改", "查询", "列表", "详情"],
            "文件处理": ["上传", "下载", "图片", "文件", "视频"],
            "支付功能": ["支付", "订单", "交易", "结算", "金额"],
            "搜索功能": ["搜索", "查找", "筛选", "过滤", "排序"],
            "通知系统": ["通知", "消息", "提醒", "邮件", "短信"],
            "报表统计": ["报表", "统计", "分析", "图表", "数据"],
            "移动端支持": ["手机", "移动", "app", "响应式", "适配"]
        }
        
        for category, keywords in patterns.items():
            if any(keyword in description_lower for keyword in keywords):
                requirements.append(f"{category}功能")
        
        # 如果没有检测到，返回通用需求
        if not requirements:
            requirements = [
                "用户注册登录 - 高优先级",
                "数据管理功能 - 高优先级",
                "后台管理系统 - 中优先级",
                "移动端适配 - 中优先级"
            ]
        
        return requirements
    
    def _identify_project_type(self, description: str, requirements: List[str]) -> str:
        """识别项目类型"""
        # 使用AI进行精确识别
        prompt = f"""
        请根据以下描述和需求，确定最适合的项目类型：
        
        描述：{description}
        需求：{', '.join(requirements)}
        
        可选类型：
        - 电子商务 (电商平台、在线商店)
        - 博客平台 (内容发布、博客系统)
        - SaaS应用 (软件即服务、多租户)
        - 内容管理系统 (CMS、后台管理)
        - 社交网络 (社区、社交平台)
        - 数据分析平台 (报表、可视化)
        - API服务 (接口服务、微服务)
        - 其他 (请说明)
        
        请只返回类型名称，如：电子商务
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是软件架构师，擅长项目分类。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            project_type = response.choices[0].message.content.strip()
            
            # 验证类型是否有效
            valid_types = [pt.value for pt in ProjectType]
            if project_type in valid_types:
                return project_type
            
        except Exception as e:
            print(f"AI类型识别失败: {e}")
        
        # 回退到规则匹配
        description_lower = description.lower()
        
        type_keywords = {
            "电子商务": ["电商", "购物", "商品", "订单", "支付", "库存", "物流"],
            "博客平台": ["博客", "文章", "发布", "评论", "标签", "分类"],
            "SaaS应用": ["saas", "订阅", "多租户", "企业", "服务", "计费"],
            "内容管理系统": ["cms", "内容", "管理", "发布", "媒体", "分类"],
            "社交网络": ["社交", "社区", "用户", "关注", "消息", "动态"],
            "数据分析平台": ["数据", "分析", "报表", "统计", "可视化", "图表"],
            "API服务": ["api", "接口", "服务", "微服务", "网关"]
        }
        
        scores = {}
        for project_type, keywords in type_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in description_lower:
                    score += 2
                for req in requirements:
                    if keyword in req.lower():
                        score += 1
            scores[project_type] = score
        
        # 返回得分最高的类型
        return max(scores.items(), key=lambda x: x[1])[0] if scores else "其他"
    
    def _ai_deep_analysis(self, description: str, project_type: str) -> Dict:
        """AI深度分析"""
        prompt = f"""
        作为资深软件架构师，请对以下{project_type}项目需求进行深度分析：
        
        需求描述：{description}
        
        请提供以下分析：
        1. 核心功能模块
        2. 技术挑战点
        3. 推荐架构模式
        4. 关键业务逻辑
        5. 潜在扩展点
        6. 安全考虑
        7. 性能要求
        
        以JSON格式返回：
        {{
            "core_modules": ["模块1", "模块2"],
            "technical_challenges": ["挑战1", "挑战2"],
            "architecture_pattern": "模式名称",
            "business_logic": ["逻辑点1", "逻辑点2"],
            "extension_points": ["扩展点1", "扩展点2"],
            "security_considerations": ["安全考虑1", "安全考虑2"],
            "performance_requirements": ["性能要求1", "性能要求2"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是资深软件架构师，擅长系统设计和分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            result = response.choices[0].message.content.strip()
            # 尝试解析JSON
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {}
                
        except Exception as e:
            print(f"AI深度分析失败: {e}")
            return {}
    
    def _generate_feature_specifications(self, description: str, project_type: str, ai_features: List[str]) -> List[Dict]:
        """生成详细功能规格"""
        # 构建功能模板
        template_features = self.config.get("project_templates", {}).get(project_type, {}).get("features", [])
        
        # 合并AI分析的功能
        all_features = list(set(template_features + ai_features))
        
        if not all_features:
            all_features = self._get_default_features(project_type)
        
        # 为每个功能生成详细规格
        feature_specs = []
        
        for i, feature_name in enumerate(all_features):
            spec = self._generate_single_feature_spec(feature_name, project_type, i + 1)
            if spec:
                feature_specs.append(spec)
        
        return feature_specs
    
    def _generate_single_feature_spec(self, feature_name: str, project_type: str, priority: int) -> Dict:
        """生成单个功能的详细规格"""
        prompt = f"""
        为{project_type}系统的"{feature_name}"功能生成详细规格：
        
        请提供：
        1. 功能描述（详细说明）
        2. 用户故事（至少3个）
        3. 验收标准（具体可测试）
        4. 预估工作量（人天）
        5. 依赖关系（依赖哪些其他功能）
        6. 技术要求（需要什么技术实现）
        
        以JSON格式返回：
        {{
            "name": "{feature_name}",
            "description": "详细描述",
            "priority": {priority},
            "user_stories": ["故事1", "故事2", "故事3"],
            "acceptance_criteria": ["标准1", "标准2", "标准3"],
            "estimated_effort": "X人天",
            "dependencies": ["依赖功能1", "依赖功能2"],
            "technical_requirements": {{"前端": "要求", "后端": "要求", "数据库": "要求"}}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是资深产品经理，擅长功能规格定义。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except Exception as e:
            print(f"功能规格生成失败: {e}")
        
        # 返回默认规格
        return {
            "name": feature_name,
            "description": f"{project_type}系统的{feature_name}功能",
            "priority": priority,
            "user_stories": [
                f"作为用户，我希望使用{feature_name}，以便...",
                f"作为管理员，我需要管理{feature_name}，以便..."
            ],
            "acceptance_criteria": [
                f"{feature_name}功能可以正常使用",
                f"{feature_name}的错误处理完善",
                f"{feature_name}的性能满足要求"
            ],
            "estimated_effort": "2-3人天",
            "dependencies": [],
            "technical_requirements": {}
        }
    
    def _select_technologies(self, project_type: str, features: List[Dict], user_preferences: Dict = None) -> Dict:
        """技术选型"""
        # 从知识库获取基础推荐
        base_recommendations = self.tech_knowledge_base.get(project_type, {})
        
        # 如果有用户偏好，进行调整
        if user_preferences:
            base_recommendations = self._apply_user_preferences(base_recommendations, user_preferences)
        
        # 根据功能需求调整技术栈
        adjusted_recommendations = self._adjust_tech_for_features(base_recommendations, features)
        
        # 验证技术栈的兼容性
        validated_recommendations = self._validate_tech_stack(adjusted_recommendations)
        
        return validated_recommendations
    
    def _apply_user_preferences(self, recommendations: Dict, preferences: Dict) -> Dict:
        """应用用户偏好"""
        if not preferences:
            return recommendations
        
        # 应用前端偏好
        if "frontend" in preferences and "frontend" in recommendations:
            frontend_pref = preferences["frontend"]
            if "technology" in frontend_pref:
                recommendations["frontend"]["technology"] = frontend_pref["technology"]
            if "framework" in frontend_pref:
                recommendations["frontend"]["framework"] = frontend_pref["framework"]
        
        # 应用后端偏好
        if "backend" in preferences and "backend" in recommendations:
            backend_pref = preferences["backend"]
            if "technology" in backend_pref:
                recommendations["backend"]["technology"] = backend_pref["technology"]
            if "framework" in backend_pref:
                recommendations["backend"]["framework"] = backend_pref["framework"]
            if "database" in backend_pref:
                recommendations["backend"]["database"] = backend_pref["database"]
        
        return recommendations
    
    def _adjust_tech_for_features(self, recommendations: Dict, features: List[Dict]) -> Dict:
        """根据功能需求调整技术栈"""
        # 分析功能需求的技术要求
        tech_requirements = self._analyze_tech_requirements(features)
        
        # 调整技术栈
        adjusted = recommendations.copy()
        
        # 如果需要实时功能
        if tech_requirements.get("real_time", False):
            adjusted["backend"]["technology"] = "Node.js + Socket.io"
            if "dependencies" not in adjusted["backend"]:
                adjusted["backend"]["dependencies"] = []
            adjusted["backend"]["dependencies"].append("socket.io")
        
        # 如果需要大数据处理
        if tech_requirements.get("big_data", False):
            adjusted["backend"]["technology"] = "Python + FastAPI"
            adjusted["backend"]["database"] = "PostgreSQL + TimescaleDB"
        
        # 如果需要机器学习
        if tech_requirements.get("ml_ai", False):
            adjusted["backend"]["technology"] = "Python"
            adjusted["backend"]["framework"] = "FastAPI"
            if "dependencies" not in adjusted["backend"]:
                adjusted["backend"]["dependencies"] = []
            adjusted["backend"]["dependencies"].extend(["scikit-learn", "tensorflow", "pandas"])
        
        return adjusted
    
    def _analyze_tech_requirements(self, features: List[Dict]) -> Dict:
        """分析功能的技术要求"""
        requirements = {
            "real_time": False,
            "big_data": False,
            "ml_ai": False,
            "file_processing": False,
            "payment": False,
            "search": False
        }
        
        for feature in features:
            name = feature["name"].lower()
            desc = feature["description"].lower()
            
            if any(word in name or word in desc for word in ["实时", "聊天", "即时", "推送"]):
                requirements["real_time"] = True
            
            if any(word in name or word in desc for word in ["大数据", "分析", "报表", "统计"]):
                requirements["big_data"] = True
            
            if any(word in name or word in desc for word in ["智能", "推荐", "预测", "机器学习"]):
                requirements["ml_ai"] = True
            
            if any(word in name or word in desc for word in ["文件", "图片", "视频", "上传"]):
                requirements["file_processing"] = True
            
            if any(word in name or word in desc for word in ["支付", "订单", "交易"]):
                requirements["payment"] = True
            
            if any(word in name or word in desc for word in ["搜索", "查找", "筛选"]):
                requirements["search"] = True
        
        return requirements
    
    def _validate_tech_stack(self, recommendations: Dict) -> Dict:
        """验证技术栈的兼容性"""
        validated = recommendations.copy()
        
        # 验证前端技术栈
        if "frontend" in validated:
            frontend = validated["frontend"]
            if frontend["technology"] == "React" and frontend.get("framework") == "Next.js":
                # React + Next.js 是合理组合
                pass
            elif frontend["technology"] == "Vue.js" and frontend.get("framework") == "Nuxt.js":
                # Vue + Nuxt 是合理组合
                pass
            else:
                # 默认使用合理组合
                frontend["technology"] = "React"
                frontend["framework"] = "Next.js"
        
        # 验证后端技术栈
        if "backend" in validated:
            backend = validated["backend"]
            if backend["technology"] == "Node.js" and backend.get("framework") == "NestJS":
                # Node.js + NestJS 是合理组合
                pass
            elif backend["technology"] == "Python" and backend.get("framework") == "FastAPI":
                # Python + FastAPI 是合理组合
                pass
            elif backend["technology"] == "Java" and backend.get("framework") == "Spring Boot":
                # Java + Spring Boot 是合理组合
                pass
            else:
                # 默认使用合理组合
                backend["technology"] = "Node.js"
                backend["framework"] = "NestJS"
        
        return validated
    
    def _design_database(self, project_type: str, features: List[Dict]) -> Dict:
        """设计数据库"""
        # 获取基础表结构
        base_tables = self.config.get("database_templates", {}).get(project_type, [])
        
        # 为每个功能扩展表结构
        all_tables = []
        for table_template in base_tables:
            table = self._extend_table_for_features(table_template, features)
            all_tables.append(table)
        
        # 添加功能特定的表
        feature_tables = self._create_feature_tables(features)
        all_tables.extend(feature_tables)
        
        # 设计表间关系
        relationships = self._design_relationships(all_tables)
        
        # 设计索引
        indexes = self._design_indexes(all_tables)
        
        # 设计约束
        constraints = self._design_constraints(all_tables)
        
        return {
            "tables": all_tables,
            "relationships": relationships,
            "indexes": indexes,
            "constraints": constraints,
            "migration_strategy": "渐进式迁移",
            "seed_data": self._generate_seed_data(project_type)
        }
    
    def _extend_table_for_features(self, table_template: Dict, features: List[Dict]) -> Dict:
        """根据功能需求扩展表结构"""
        table = table_template.copy()
        
        # 为特定功能添加字段
        for feature in features:
            feature_name = feature["name"].lower()
            
            if "用户" in feature_name and table["name"] == "users":
                # 为用户表添加额外字段
                if "fields" not in table:
                    table["fields"] = {}
                
                # 添加通用字段
                table["fields"].update({
                    "avatar": {"type": "string", "nullable": True, "description": "头像"},
                    "bio": {"type": "text", "nullable": True, "description": "个人简介"},
                    "settings": {"type": "json", "nullable": True, "description": "用户设置"}
                })
        
        return table
    
    def _create_feature_tables(self, features: List[Dict]) -> List[Dict]:
        """创建功能特定的表"""
        tables = []
        
        for feature in features:
            feature_name = feature["name"].lower()
            
            if "文章" in feature_name or "博客" in feature_name:
                tables.append({
                    "name": "articles",
                    "fields": {
                        "id": {"type": "uuid", "primary_key": True},
                        "title": {"type": "string", "nullable": False},
                        "content": {"type": "text", "nullable": False},
                        "author_id": {"type": "uuid", "foreign_key": "users.id"},
                        "category_id": {"type": "uuid", "foreign_key": "categories.id", "nullable": True},
                        "status": {"type": "string", "default": "draft"},
                        "created_at": {"type": "timestamp", "default": "CURRENT_TIMESTAMP"},
                        "updated_at": {"type": "timestamp", "default": "CURRENT_TIMESTAMP"}
                    },
                    "description": "文章表"
                })
            
            if "商品" in feature_name or "产品" in feature_name:
                tables.append({
                    "name": "products",
                    "fields": {
                        "id": {"type": "uuid", "primary_key": True},
                        "name": {"type": "string", "nullable": False},
                        "description": {"type": "text", "nullable": True},
                        "price": {"type": "decimal", "precision": 10, "scale": 2},
                        "stock": {"type": "integer", "default": 0},
                        "category_id": {"type": "uuid", "foreign_key": "categories.id"},
                        "images": {"type": "json", "nullable": True},
                        "attributes": {"type": "json", "nullable": True},
                        "created_at": {"type": "timestamp", "default": "CURRENT_TIMESTAMP"}
                    },
                    "description": "商品表"
                })
        
        return tables
    
    def _design_apis(self, project_type: str, features: List[Dict]) -> Dict:
        """设计API接口"""
        # 基础API端点
        base_endpoints = self.config.get("api_templates", {}).get(project_type, [])
        
        # 为每个功能添加API端点
        all_endpoints = []
        
        for endpoint_template in base_endpoints:
            endpoint = endpoint_template.copy()
            all_endpoints.append(endpoint)
        
        # 添加功能特定的API
        for feature in features:
            feature_name = feature["name"].lower()
            
            if "用户" in feature_name:
                all_endpoints.extend(self._create_user_apis())
            if "文章" in feature_name or "内容" in feature_name:
                all_endpoints.extend(self._create_content_apis())
            if "商品" in feature_name:
                all_endpoints.extend(self._create_product_apis())
        
        return {
            "endpoints": all_endpoints,
            "authentication": {
                "type": "JWT",
                "token_expiry": "24h",
                "refresh_token": True
            },
            "rate_limiting": {
                "enabled": True,
                "limit": "100 requests per minute",
                "strategy": "token bucket"
            },
            "versioning": "v1",
            "error_handling": {
                "standard_format": True,
                "error_codes": {
                    "400": "Bad Request",
                    "401": "Unauthorized",
                    "403": "Forbidden",
                    "404": "Not Found",
                    "500": "Internal Server Error"
                }
            }
        }
    
    def _create_user_apis(self) -> List[Dict]:
        """创建用户相关API"""
        return [
            {
                "endpoint": "/api/v1/auth/register",
                "method": "POST",
                "description": "用户注册",
                "request": {
                    "body": {
                        "email": "string",
                        "password": "string",
                        "name": "string"
                    }
                },
                "response": {
                    "success": {"token": "string", "user": "object"},
                    "errors": ["用户已存在", "验证失败"]
                }
            },
            {
                "endpoint": "/api/v1/auth/login",
                "method": "POST",
                "description": "用户登录",
                "request": {
                    "body": {
                        "email": "string",
                        "password": "string"
                    }
                },
                "response": {
                    "success": {"token": "string", "user": "object"},
                    "errors": ["用户不存在", "密码错误"]
                }
            }
        ]
    
    def _suggest_ui_design(self, project_type: str, features: List[Dict]) -> Dict:
        """提供UI/UX设计建议"""
        design_templates = {
            "电子商务": {
                "design_style": "现代简约，突出商品",
                "color_palette": {
                    "primary": "#1890ff",
                    "secondary": "#52c41a",
                    "accent": "#faad14",
                    "background": "#f5f5f5",
                    "text": "#333333"
                },
                "component_library": "Ant Design",
                "layout_suggestions": [
                    "响应式网格布局",
                    "清晰的导航结构",
                    "突出的搜索和购物车",
                    "商品分类展示"
                ]
            },
            "博客平台": {
                "design_style": "内容优先，阅读友好",
                "color_palette": {
                    "primary": "#262626",
                    "secondary": "#595959",
                    "accent": "#1890ff",
                    "background": "#ffffff",
                    "text": "#262626"
                },
                "component_library": "Tailwind CSS",
                "layout_suggestions": [
                    "简洁的阅读区域",
                    "清晰的导航菜单",
                    "相关的文章推荐",
                    "友好的评论区"
                ]
            }
        }
        
        base_design = design_templates.get(project_type, design_templates["电子商务"])
        
        # 根据功能调整设计
        adjusted_design = base_design.copy()
        
        if any("移动" in f["name"].lower() for f in features):
            adjusted_design["layout_suggestions"].append("移动优先设计")
        
        if any("管理" in f["name"].lower() for f in features):
            adjusted_design["layout_suggestions"].append("后台管理面板")
        
        return adjusted_design
    
    def _design_project_structure(self, project_type: str, tech_choices: Dict) -> Dict:
        """设计项目结构"""
        base_structure = {
            "frontend": ["src/", "public/", "components/", "pages/", "styles/", "utils/"],
            "backend": ["src/", "config/", "models/", "controllers/", "services/", "middleware/"],
            "shared": ["types/", "constants/", "utils/"],
            "tests": ["unit/", "integration/", "e2e/"],
            "docs": ["api/", "deployment/", "user-guide/"],
            "infrastructure": ["docker/", "kubernetes/", "scripts/"]
        }
        
        # 根据技术栈调整结构
        if tech_choices.get("frontend", {}).get("technology") == "React":
            base_structure["frontend"].extend(["hooks/", "context/", "store/"])
        
        if tech_choices.get("backend", {}).get("framework") == "NestJS":
            base_structure["backend"] = ["src/", "test/", "dist/"]
        
        return base_structure
    
    def _estimate_timeline_and_cost(self, features: List[Dict], tech_choices: Dict) -> Dict:
        """估算时间和成本"""
        # 计算总工作量
        total_effort = 0
        for feature in features:
            effort = feature.get("estimated_effort", "1人天")
            # 提取数字
            match = re.search(r'(\d+)', effort)
            if match:
                total_effort += int(match.group(1))
            else:
                total_effort += 2  # 默认2人天
        
        # 考虑技术复杂度
        tech_complexity = self._calculate_tech_complexity(tech_choices)
        adjusted_effort = total_effort * tech_complexity
        
        # 计算时间线
        man_days = adjusted_effort
        calendar_days = man_days * 1.5  # 考虑沟通和会议时间
        
        # 计算成本（假设每天1000元）
        cost_per_day = 1000
        estimated_cost = man_days * cost_per_day
        
        return {
            "total_man_days": man_days,
            "calendar_days": calendar_days,
            "estimated_cost": f"¥{estimated_cost:,}",
            "phases": [
                {"phase": "需求与设计", "percentage": 15, "days": round(calendar_days * 0.15)},
                {"phase": "前端开发", "percentage": 30, "days": round(calendar_days * 0.3)},
                {"phase": "后端开发", "percentage": 35, "days": round(calendar_days * 0.35)},
                {"phase": "测试与部署", "percentage": 20, "days": round(calendar_days * 0.2)}
            ],
            "team_recommendation": self._recommend_team_size(man_days)
        }
    
    def _calculate_tech_complexity(self, tech_choices: Dict) -> float:
        """计算技术复杂度"""
        complexity = 1.0
        
        # 前端复杂度
        frontend = tech_choices.get("frontend", {})
        if frontend.get("technology") == "React":
            complexity *= 1.2
        if frontend.get("state_management") == "Redux":
            complexity *= 1.1
        
        # 后端复杂度
        backend = tech_choices.get("backend", {})
        if backend.get("framework") == "NestJS":
            complexity *= 1.3
        if backend.get("database") == "PostgreSQL + Redis":
            complexity *= 1.2
        
        return complexity
    
    def _recommend_team_size(self, man_days: int) -> Dict:
        """推荐团队规模"""
        if man_days <= 10:
            return {"size": 1, "roles": ["全栈工程师"]}
        elif man_days <= 30:
            return {"size": 2, "roles": ["前端工程师", "后端工程师"]}
        elif man_days <= 60:
            return {"size": 3, "roles": ["前端工程师", "后端工程师", "UI/UX设计师"]}
        else:
            return {"size": 4, "roles": ["前端工程师", "后端工程师", "UI/UX设计师", "测试工程师"]}
    
    def _create_development_plan(self, features: List[Dict]) -> List[Dict]:
        """创建开发计划"""
        # 按优先级排序功能
        sorted_features = sorted(features, key=lambda x: x.get("priority", 1))
        
        development_plan = []
        sprint_duration = 10  # 每个sprint 10天
        current_sprint = 1
        sprint_capacity = 5  # 每个sprint能完成的工作量
        
        for feature in sorted_features:
            effort = self._parse_effort(feature.get("estimated_effort", "1人天"))
            
            development_plan.append({
                "sprint": current_sprint,
                "feature": feature["name"],
                "description": feature["description"],
                "priority": feature["priority"],
                "tasks": self._break_down_tasks(feature),
                "acceptance_criteria": feature.get("acceptance_criteria", []),
                "estimated_effort": f"{effort}人天",
                "dependencies": feature.get("dependencies", [])
            })
            
            sprint_capacity -= effort
            if sprint_capacity <= 0:
                current_sprint += 1
                sprint_capacity = 5
        
        return development_plan
    
    def _parse_effort(self, effort_str: str) -> int:
        """解析工作量字符串"""
        match = re.search(r'(\d+)', effort_str)
        return int(match.group(1)) if match else 2
    
    def _break_down_tasks(self, feature: Dict) -> List[str]:
        """拆解任务"""
        feature_name = feature["name"]
        
        tasks = [
            f"设计{feature_name}的数据库模型",
            f"实现{feature_name}的API接口",
            f"开发{feature_name}的前端组件",
            f"编写{feature_name}的单元测试",
            f"集成测试{feature_name}功能"
        ]
        
        # 根据功能描述添加特定任务
        description = feature["description"].lower()
        if any(word in description for word in ["用户", "权限", "认证"]):
            tasks.append("实现用户认证和授权")
        
        if any(word in description for word in ["文件", "图片", "上传"]):
            tasks.append("实现文件上传处理")
        
        if any(word in description for word in ["搜索", "查询", "筛选"]):
            tasks.append("实现搜索算法和过滤")
        
        return tasks
    
    def _assess_risks(self, features: List[Dict], tech_choices: Dict) -> List[Dict]:
        """风险评估"""
        risks = []
        
        # 技术风险
        tech_risk = {
            "category": "技术风险",
            "description": "新技术栈的学习曲线和集成问题",
            "probability": "中",
            "impact": "高",
            "mitigation": "提前进行技术验证和原型开发"
        }
        risks.append(tech_risk)
        
        # 需求风险
        if len(features) > 10:
            req_risk = {
                "category": "需求风险",
                "description": "需求过多可能导致范围蔓延",
                "probability": "高",
                "impact": "中",
                "mitigation": "优先实现核心功能，迭代开发"
            }
            risks.append(req_risk)
        
        # 性能风险
        if any("实时" in f["name"] for f in features):
            perf_risk = {
                "category": "性能风险",
                "description": "实时功能可能带来性能压力",
                "probability": "中",
                "impact": "中",
                "mitigation": "使用WebSocket优化，负载测试"
            }
            risks.append(perf_risk)
        
        return risks
    
    def _define_success_metrics(self, project_type: str) -> Dict:
        """定义成功指标"""
        metrics = {
            "电子商务": {
                "user_metrics": ["注册用户数", "活跃用户数", "转化率"],
                "business_metrics": ["订单数", "交易额", "客单价"],
                "technical_metrics": ["页面加载时间", "API响应时间", "错误率"]
            },
            "博客平台": {
                "user_metrics": ["阅读量", "评论数", "分享数"],
                "business_metrics": ["订阅用户数", "广告收入", "内容质量"],
                "technical_metrics": ["页面性能", "SEO排名", "可用性"]
            }
        }
        
        return metrics.get(project_type, metrics["电子商务"])
    
    def _get_default_features(self, project_type: str) -> List[str]:
        """获取默认功能列表"""
        defaults = {
            "电子商务": [
                "用户注册登录",
                "商品管理",
                "购物车功能",
                "订单系统",
                "支付集成",
                "后台管理",
                "数据统计"
            ],
            "博客平台": [
                "文章管理",
                "分类标签",
                "评论系统",
                "用户订阅",
                "搜索功能",
                "SEO优化",
                "后台编辑"
            ],
            "SaaS应用": [
                "多租户支持",
                "用户管理",
                "订阅计费",
                "仪表板",
                "数据报表",
                "API接口",
                "系统设置"
            ]
        }
        
        return defaults.get(project_type, ["用户管理", "数据管理", "系统设置"])