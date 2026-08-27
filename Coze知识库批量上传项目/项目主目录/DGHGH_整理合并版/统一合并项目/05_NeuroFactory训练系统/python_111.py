# 使用异步处理
import asyncio
from concurrent.futures import ThreadPoolExecutor

class CodeGenerator:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def generate_project_async(self, project_spec):
        # 并行生成不同部分
        tasks = [
            self._generate_frontend_async(project_spec),
            self._generate_backend_async(project_spec),
            self._generate_database_async(project_spec),
            self._generate_docs_async(project_spec)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # 合并结果
        return self._merge_results(results)