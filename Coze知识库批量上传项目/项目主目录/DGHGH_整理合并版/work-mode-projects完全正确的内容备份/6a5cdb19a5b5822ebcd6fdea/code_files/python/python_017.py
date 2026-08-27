# packages/core/src/ai_engine/code_generator.py
import os
import json
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import shutil
import zipfile
import tempfile
from datetime import datetime

class CodeGenerator:
    """代码生成引擎"""
    
    def __init__(self, templates_dir: str):
        """
        初始化代码生成器
        
        Args:
            templates_dir: 模板目录路径
        """
        self.templates_dir = Path(templates_dir)
        
        # 初始化Jinja2环境
        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # 注册自定义过滤器
        self._register_filters()
        
        # 加载配置
        self.config = self._load_config()
        
    def _register_filters(self):
        """注册自定义过滤器"""
        self.jinja_env.filters['camel_case'] = self._to_camel_case
        self.jinja_env.filters['pascal_case'] = self._to_pascal_case
        self.jinja_env.filters['snake_case'] = self._to_snake_case
        self.jinja_env.filters['kebab_case'] = self._to_kebab_case
        self.jinja_env.filters['pluralize'] = self._pluralize
        self.jinja_env.filters['singularize'] = self._singularize
    
    def _load_config(self) -> Dict:
        """加载配置"""
        config_path = self.templates_dir / "config" / "generator_config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def generate_project(self, project_spec: Dict, output_dir: str) -> Dict[str, str]:
        """
        生成完整项目
        
        Args:
            project_spec: 项目规格
            output_dir: 输出目录
            
        Returns:
            生成的文件路径和内容字典
        """
        print(f"🚀 开始生成项目: {project_spec.get('project_name', '未命名项目')}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        # 1. 生成项目配置文件
        generated_files.update(self._generate_config_files(project_spec, output_path))
        
        # 2. 生成源代码
        generated_files.update(self._generate_source_code(project_spec, output_path))
        
        # 3. 生成数据库文件
        generated_files.update(self._generate_database_files(project_spec, output_path))
        
        # 4. 生成API文档
        generated_files.update(self._generate_api_documentation(project_spec, output_path))
        
        # 5. 生成部署配置
        generated_files.update(self._generate_deployment_configs(project_spec, output_path))
        
        # 6. 生成测试文件
        generated_files.update(self._generate_test_files(project_spec, output_path))
        
        # 7. 生成文档
        generated_files.update(self._generate_documentation(project_spec, output_path))
        
        # 8. 生成工具脚本
        generated_files.update(self._generate_utility_scripts(project_spec, output_path))
        
        print(f"✅ 项目生成完成，共生成 {len(generated_files)} 个文件")
        
        return generated_files
    
    def generate_zip(self, project_spec: Dict, output_zip: str) -> str:
        """
        生成项目ZIP包
        
        Args:
            project_spec: 项目规格
            output_zip: 输出ZIP文件路径
            
        Returns:
            ZIP文件路径
        """
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 生成项目文件
            generated_files = self.generate_project(project_spec, temp_dir)
            
            # 创建ZIP文件
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, content in generated_files.items():
                    # 确保文件在临时目录中
                    if not file_path.startswith(temp_dir):
                        file_path = os.path.join(temp_dir, file_path)
                    
                    # 添加到ZIP
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
            
            print(f"📦 ZIP包生成完成: {output_zip}")
            return output_zip
    
    def _generate_config_files(self, project_spec: Dict, output_path: Path) -> Dict[str, str]:
        """生成配置文件"""
        files = {}
        tech_stack = project_spec.get("technology_choices", {})
        project_name = project_spec.get("project_name", "my-project")
        
        # 根据技术栈生成不同的配置文件
        if "frontend" in tech_stack:
            frontend_tech = tech_stack["frontend"].get("technology", "").lower()
            
            if "react" in frontend_tech:
                files.update(self._generate_react_configs(project_spec, output_path))
            elif "vue" in frontend_tech:
                files.update(self._generate_vue_configs(project_spec, output_path))
            elif "angular" in frontend_tech:
                files.update(self._generate_angular_configs(project_spec, output_path))
        
        if "backend" in tech_stack:
            backend_tech = tech_stack["backend"].get("technology", "").lower()
            
            if "node" in backend_tech:
                files.update(self._generate_nodejs_configs(project_spec, output_path))
            elif "python" in backend_tech:
                files.update(self._generate_python_configs(project_spec, output_path))
            elif "java" in backend_tech:
                files.update(self._generate_java_configs(project_spec, output_path))
        
        # 通用配置文件
        files.update(self._generate_common_configs(project_spec, output_path))
        
        return files
    
    def _generate_react_configs(self, project_spec: Dict, output_path: Path) -> Dict[str, str]:
        """生成React配置文件"""
        files = {}
        frontend_dir = output_path / "frontend"
        frontend_dir.mkdir(exist_ok=True)
        
        # package.json
        template = self._get_template("frontend/react/package.json.j2")
        if template:
            content = template.render(
                project_name=project_spec.get("project_name", "react-app"),
                description=project_spec.get("description", ""),
                author=project_spec.get("author", "AutoCode Pro"),
                dependencies=self._get_react_dependencies(project_spec)
            )
            
            file_path = frontend_dir / "package.json"
            file_path.write_text(content, encoding='utf-8')
            files[str(file_path)] = content
        
        # tsconfig.json
        template = self._get_template("frontend/react/tsconfig.json.j2")
        if template:
            content = template.render()
            file_path = frontend_dir / "tsconfig.json"
            file_path.write_text(content, encoding='utf-8')
            files[str(file_path)] = content
        
        # vite.config.ts
        template = self._get_template("frontend/react/vite.config.ts.j2")
        if template:
            content = template.render()
            file_path = frontend_dir / "vite.config.ts"
            file_path.write_text(content, encoding='utf-8')
            files[str(file_path)] = content
        
        return files
    
    def _generate_nodejs_configs(self, project_spec: Dict, output_path: Path) -> Dict[str, str]:
        """生成Node.js配置文件"""
        files = {}
        backend_dir = output_path / "backend"
        backend_dir.mkdir(exist_ok=True)
        
        # package.json
        template = self._get_template("backend/nodejs/package.json.j2")
        if template:
            content = template.render(
                project_name=project_spec.get("project_name", "backend"),
                description=project_spec.get("description", ""),
                dependencies=self._get_nodejs_dependencies(project_spec)
            )
            
            file_path = backend_dir / "package.json"
            file_path.write_text(content, encoding='utf-8')
            files[str(file_path)] = content
        
        # tsconfig.json
        template = self._get_template("backend/nodejs/tsconfig.json.j2")
        if template:
            content = template.render()
            file_path = backend_dir / "tsconfig.json"
            file_path.write_text(content, encoding='utf-8')
            files[str(file_path)] = content
        
        # .env
        template = self._get_template("backend/nodejs/env.j2")
        if template:
            content = template.render(
                db_config=project_spec.get("database_design", {}),
                project_type=project_spec.get("project_type", "")
            )
            file_path = backend_dir / ".env.example"
            file_path.write_text(content, encoding='utf-8')
            files[str(file_path)] = content
        
        return files
    
    def _generate_source_code(self, project_spec: Dict, output_path: Path) -> Dict[str, str]:
        """生成源代码"""
        files = {}
        
        # 生成前端代码
        if "frontend" in project_spec.get("technology_choices", {}):
            files.update(self._generate_frontend_code(project_spec, output_path))
        
        # 生成后端代码
        if "backend" in project_spec.get("technology_choices", {}):
            files.update(self._generate_backend_code(project_spec, output_path))
        
        return files
    
    def _generate_frontend_code(self, project_spec: Dict, output_path: Path) -> Dict[str, str]:
        """生成前端代码"""
        files = {}
        tech_stack = project_spec.get("technology_choices", {})
        frontend_tech = tech_stack.get("frontend", {}).get("technology", "").lower()
        
        frontend_dir = output_path / "frontend"
        frontend_dir.mkdir(exist_ok=True)
        
        if "react" in frontend_tech:
            files.update(self._generate_react_code(project_spec, frontend_dir))
        elif "vue" in frontend_tech:
            files.update(self._generate_vue_code(project_spec, frontend_dir))
        elif "angular" in frontend_tech:
            files.update(self._generate_angular_code(project_spec, frontend_dir))
        
        return files
    
    def _generate_react_code(self, project_spec: Dict, output_path: Path) -> Dict[str, str]:
        """生成React代码"""
        files = {}
        
        # 创建目录结构
        src_dir = output_path / "src"
        src_dir.mkdir(exist_ok=True)
        
        for subdir in ["components", "pages", "hooks", "store", "utils", "styles"]:
            (src_dir / subdir).mkdir(exist_ok=True)
        
        # 生成App.jsx/tsx
        template = self._get_template("frontend/react/App.jsx.j2")
        if template:
            content = template.render(
                pages=self._get_react_pages(project_spec),
                features=project_spec.get("feature_specifications", [])
            )
            
            file_path = src_dir / "App.jsx"
            file_path.write_text(content, encoding='utf-8')
            files[str(file_path)] = content
        
        # 生成main.jsx/tsx
        template = self._get_template("frontend/react/main.jsx.j2")
        if template:
            content = template.render()
            file_path = src_dir / "main.jsx"
            file_path.write_text(content, encoding='utf-8')
            files[str(file_path)] = content
        
        # 生成页面组件
        files.update(self._generate_react_pages(project_spec, src_dir / "pages"))
        
        # 生成公共组件
        files.update(self._generate_react_components(project_spec, src_dir / "components"))
        
        # 生成状态管理
        files.update(self._generate_react_state(project_spec, src_dir / "store"))
        
        # 生成工具函数
        files.update(self._generate_react_utils(project_spec, src_dir / "utils"))
        
        # 生成样式文件
        files.update(self._generate_react_styles(project_spec, src_dir / "styles"))
        
        return files
    
    def _generate_backend_code(self, project_spec: Dict, output_path: Path) -> Dict[str, str]:
        """生成后端代码"""
        files = {}
        tech_stack = project_spec.get("technology_choices", {})
        backend_tech = tech_stack.get("backend", {}).get("technology", "").lower()
        backend_framework = tech_stack.get("backend", {}).get("framework", "").lower()
        
        backend_dir = output_path / "backend"
        backend_dir.mkdir(exist_ok=True)
        
        if "node" in backend_tech and "nest" in backend_framework:
            files.update(self._generate_nestjs_code(project_spec, backend_dir))
        elif "node" in backend_tech and "express" in backend_framework:
            files.update(self._generate_express_code(project_spec, backend_dir))
        elif "python" in backend_tech and "fastapi" in backend_framework:
            files.update(self._generate_fastapi_code(project_spec, backend_dir))
        elif "python" in backend_tech and "django" in backend_framework:
            files.update(self._generate_django_code(project_spec, backend_dir))
        elif "java" in backend_tech and "spring" in backend_framework:
            files.update(self._generate_springboot_code(project_spec, backend_dir))
        
        return files
    
    def _generate_nestjs_code(self, project_spec: Dict, output_path: Path) -> Dict[str, str]:
        """生成NestJS代码"""
        files = {}
        
        # 创建目录结构
        src_dir = output_path / "src"
        src_dir.mkdir(exist_ok=True)
        
        for subdir in ["modules", "common", "config", "database"]:
            (src_dir / subdir).mkdir(exist_ok=True)
        
        # 生成main.ts
        template = self._get_template("backend/nodejs/nestjs/main.ts.j2")
        if template:
            content = template.render(
                project_name=project_spec.get("project_name", "app"),
                port=3000
            )
            
            file_path = src_dir / "main.ts"
            file_path.write_text(content, encoding='utf-8')
            files[str(file_path)] = content
        
        # 生成app.module.ts
        template = self._get_template("backend/nodejs/nestjs/app.module.ts.j2")
        if template:
            modules = self._get_nestjs_modules(project_spec)
            content = template.render(modules=modules)
            
            file_path = src_dir / "app.module.ts"
            file_path.write_text(content, encoding='utf-8')
            files[str(file_path)] = content
        
        # 生成模块
        for module_name in self._get_nestjs_modules(project_spec):
            files.update(self._generate_nestjs_module(project_spec, src_dir, module_name))
        
        # 生成实体
        database_design = project_spec.get("database_design", {})
        if database_design and "tables" in database_design:
            files.update(self._generate_nestjs_entities(database_design["tables"], src_dir))
        
        return files
    
    def _generate_database_files(self, project_spec: Dict, output_path: Path) -> Dict[str, str]:
        """生成数据库文件"""
        files = {}
        database_dir = output_path / "database"
        database_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        for subdir in ["migrations", "seeds", "schemas"]:
            (database_dir / subdir).mkdir(exist_ok=True)
        
        # 生成数据库模式
        database_design = project_spec.get("database_design", {})
        if database_design and "tables" in database_design:
            files.update(self._generate_sql_schemas(database_design["tables"], database_dir))
            files.update(self._generate_migration_scripts(database_design["tables"], database_dir / "migrations"))
            files.update(self._generate_seed_data(database_design.get("seed_data", {}), database_dir / "seeds"))
        
        return files
    
    def _get_template(self, template_path: str):
        """获取模板"""
        try:
            return self.jinja_env.get_template(template_path)
        except TemplateNotFound:
            print(f"模板未找到: {template_path}")
            return None
    
    def _to_camel_case(self, text: str) -> str:
        """转换为驼峰命名"""
        import re
        words = re.split(r'[_\-\s]+', text)
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    
    def _to_pascal_case(self, text: str) -> str:
        """转换为帕斯卡命名"""
        import re
        words = re.split(r'[_\-\s]+', text)
        return ''.join(word.capitalize() for word in words)
    
    def _to_snake_case(self, text: str) -> str:
        """转换为蛇形命名"""
        import re
        text = re.sub(r'([A-Z]+)', r'_\1', text)
        text = re.sub(r'[-\s]+', '_', text)
        return text.lower().strip('_')
    
    def _to_kebab_case(self, text: str) -> str:
        """转换为短横线命名"""
        import re
        text = re.sub(r'([A-Z]+)', r'-\1', text)
        text = re.sub(r'[_\s]+', '-', text)
        return text.lower().strip('-')
    
    def _pluralize(self, text: str) -> str:
        """转换为复数形式"""
        if text.endswith('y'):
            return text[:-1] + 'ies'
        elif text.endswith('s') or text.endswith('x') or text.endswith('z'):
            return text + 'es'
        else:
            return text + 's'
    
    def _singularize(self, text: str) -> str:
        """转换为单数形式"""
        if text.endswith('ies'):
            return text[:-3] + 'y'
        elif text.endswith('es'):
            return text[:-2]
        elif text.endswith('s'):
            return text[:-1]
        return text
    
    def _get_react_dependencies(self, project_spec: Dict) -> List[str]:
        """获取React依赖"""
        dependencies = [
            "react", "react-dom",
            "react-router-dom", "axios",
            "@reduxjs/toolkit", "react-redux"
        ]
        
        # 根据功能添加依赖
        features = project_spec.get("feature_specifications", [])
        for feature in features:
            if any(word in feature["name"].lower() for word in ["图表", "数据可视化"]):
                dependencies.append("recharts")
            if any(word in feature["name"].lower() for word in ["表单", "验证"]):
                dependencies.append("react-hook-form")
            if any(word in feature["name"].lower() for word in ["编辑器", "富文本"]):
                dependencies.append("react-quill")
        
        return dependencies
    
    def _get_nodejs_dependencies(self, project_spec: Dict) -> List[str]:
        """获取Node.js依赖"""
        dependencies = [
            "@nestjs/core", "@nestjs/common",
            "@nestjs/platform-express",
            "typeorm", "pg", "class-validator",
            "class-transformer", "@nestjs/swagger"
        ]
        
        # 根据功能添加依赖
        features = project_spec.get("feature_specifications", [])
        for feature in features:
            if any(word in feature["name"].lower() for word in ["认证", "登录"]):
                dependencies.append("@nestjs/jwt")
                dependencies.append("passport")
            if any(word in feature["name"].lower() for word in ["文件", "上传"]):
                dependencies.append("multer")
            if any(word in feature["name"].lower() for word in ["邮件", "通知"]):
                dependencies.append("nodemailer")
        
        return dependencies
    
    def _get_react_pages(self, project_spec: Dict) -> List[str]:
        """获取React页面列表"""
        project_type = project_spec.get("project_type", "")
        
        page_map = {
            "电子商务": ["首页", "商品列表", "商品详情", "购物车", "结算", "订单列表", "用户中心"],
            "博客平台": ["首页", "文章列表", "文章详情", "分类", "标签", "关于", "联系"],
            "SaaS应用": ["仪表板", "用户管理", "设置", "账单", "报表", "帮助"],
            "内容管理系统": ["登录", "仪表板", "内容管理", "媒体库", "用户管理", "系统设置"]
        }
        
        return page_map.get(project_type, ["首页", "关于", "联系"])
    
    def _generate_react_pages(self, project_spec: Dict, pages_dir: Path) -> Dict[str, str]:
        """生成React页面组件"""
        files = {}
        pages = self._get_react_pages(project_spec)
        
        for page in pages:
            template = self._get_template("frontend/react/page.jsx.j2")
            if template:
                content = template.render(
                    page_name=page,
                    project_type=project_spec.get("project_type", ""),
                    features=project_spec.get("feature_specifications", [])
                )
                
                file_name = f"{self._to_pascal_case(page)}.jsx"
                file_path = pages_dir / file_name
                file_path.write_text(content, encoding='utf-8')
                files[str(file_path)] = content
        
        return files
    
    def _get_nestjs_modules(self, project_spec: Dict) -> List[str]:
        """获取NestJS模块列表"""
        project_type = project_spec.get("project_type", "")
        
        module_map = {
            "电子商务": ["AuthModule", "UsersModule", "ProductsModule", "OrdersModule", "PaymentsModule"],
            "博客平台": ["AuthModule", "UsersModule", "ArticlesModule", "CategoriesModule", "CommentsModule"],
            "SaaS应用": ["AuthModule", "UsersModule", "TenantsModule", "SubscriptionsModule", "AnalyticsModule"],
            "内容管理系统": ["AuthModule", "UsersModule", "ContentModule", "MediaModule", "SettingsModule"]
        }
        
        return module_map.get(project_type, ["AuthModule", "UsersModule", "AppModule"])