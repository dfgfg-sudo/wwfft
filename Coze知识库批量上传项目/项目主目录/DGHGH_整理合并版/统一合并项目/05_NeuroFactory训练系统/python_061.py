# workflow_generator.py
import json
import yaml
from jinja2 import Environment, FileSystemLoader
import asyncio
from datetime import datetime
from typing import Dict, List, Any
import hashlib

class CozeWorkflowGenerator:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader('.'),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.incremental_state = self.load_state()
    
    def load_state(self) -> Dict:
        """加载增量处理状态"""
        try:
            with open('state.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"last_run": None, "processed_ids": []}
    
    def save_state(self):
        """保存处理状态"""
        with open('state.json', 'w') as f:
            json.dump(self.incremental_state, f, indent=2)
    
    def detect_incremental_data(self, data_source: Dict) -> List[Dict]:
        """检测增量数据"""
        # 这里根据配置的增量字段获取新数据
        last_run = self.incremental_state.get('last_run')
        processed_ids = set(self.incremental_state.get('processed_ids', []))
        
        # 示例：从数据库获取增量数据
        incremental_data = []
        # 实际实现需要连接数据源
        
        return incremental_data
    
    def generate_workflow_parameters(self, data_batch: List[Dict]) -> Dict[str, Any]:
        """生成工作流参数"""
        template = self.jinja_env.get_template(
            self.config['workflow_automation']['templates']['workflow_template_path']
        )
        
        workflow_params = {
            "workflow_name": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "workflow_description": f"Auto-generated batch workflow",
            "nodes": [],
            "edges": [],
            "batch_id": hashlib.md5(str(data_batch).encode()).hexdigest()[:8],
            "data_count": len(data_batch),
            "generated_at": datetime.now().isoformat()
        }
        
        # 根据数据生成节点
        for i, data_item in enumerate(data_batch):
            node = {
                "id": f"node_{i}",
                "type": "llm",
                "config": {
                    "model": "gpt-4",
                    "prompt": self.generate_prompt(data_item),
                    "temperature": 0.7
                },
                "data": data_item
            }
            workflow_params["nodes"].append(node)
            
            if i > 0:
                workflow_params["edges"].append({
                    "source": f"node_{i-1}",
                    "target": f"node_{i}"
                })
        
        return json.loads(template.render(workflow_params))
    
    def generate_prompt(self, data_item: Dict) -> str:
        """根据数据生成提示词模板"""
        prompt_template = """
        请处理以下数据：
        - ID: {{id}}
        - 内容: {{content}}
        - 类型: {{type}}
        
        处理要求：
        1. 分析内容的关键信息
        2. 提取主要实体
        3. 生成摘要
        4. 分类标签
        
        请以JSON格式返回结果。
        """
        return self.jinja_env.from_string(prompt_template).render(**data_item)
    
    async def create_workflow(self, workflow_params: Dict) -> str:
        """通过Coze API创建工作流"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.config['workflow_automation']['coze_api']['api_key']}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.config['workflow_automation']['coze_api']['base_url']}/v1/workflows"
            
            async with session.post(url, headers=headers, json=workflow_params) as response:
                if response.status == 201:
                    result = await response.json()
                    return result.get('workflow_id')
                else:
                    raise Exception(f"Failed to create workflow: {await response.text()}")
    
    async def execute_workflow(self, workflow_id: str, input_data: Dict) -> Dict:
        """执行工作流"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.config['workflow_automation']['coze_api']['api_key']}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.config['workflow_automation']['coze_api']['base_url']}/v1/workflows/{workflow_id}/execute"
            
            async with session.post(url, headers=headers, json={"inputs": input_data}) as response:
                return await response.json()