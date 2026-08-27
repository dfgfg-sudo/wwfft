# batch_executor.py
import asyncio
import aiohttp
from typing import List, Dict, Any
import logging
from dataclasses import dataclass
from concurrent.futures import Semaphore
import time

@dataclass
class BatchTask:
    workflow_id: str
    data: Dict[str, Any]
    priority: int = 1
    retry_count: int = 0

class CozeBatchExecutor:
    def __init__(self, api_key: str, max_concurrent: int = 5):
        self.api_key = api_key
        self.max_concurrent = max_concurrent
        self.semaphore = Semaphore(max_concurrent)
        self.base_url = "https://api.coze.cn/v1"
        self.logger = self.setup_logger()
    
    def setup_logger(self):
        logger = logging.getLogger('CozeBatchExecutor')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    async def execute_single_task(self, task: BatchTask, session: aiohttp.ClientSession) -> Dict:
        """执行单个任务"""
        async with self.semaphore:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/workflows/{task.workflow_id}/execute"
            
            try:
                async with session.post(
                    url, 
                    headers=headers, 
                    json={"inputs": task.data},
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        self.logger.info(f"Task completed: {task.workflow_id}")
                        return {
                            "success": True,
                            "data": result,
                            "task": task
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Task failed: {error_text}")
                        
                        if task.retry_count < 3:
                            task.retry_count += 1
                            await asyncio.sleep(2 ** task.retry_count)  # 指数退避
                            return await self.execute_single_task(task, session)
                        
                        return {
                            "success": False,
                            "error": error_text,
                            "task": task
                        }
                        
            except Exception as e:
                self.logger.error(f"Task execution error: {str(e)}")
                
                if task.retry_count < 3:
                    task.retry_count += 1
                    await asyncio.sleep(2 ** task.retry_count)
                    return await self.execute_single_task(task, session)
                
                return {
                    "success": False,
                    "error": str(e),
                    "task": task
                }
    
    async def execute_batch(self, tasks: List[BatchTask]) -> List[Dict]:
        """批量执行任务"""
        async with aiohttp.ClientSession() as session:
            task_coroutines = [
                self.execute_single_task(task, session)
                for task in tasks
            ]
            
            results = await asyncio.gather(*task_coroutines, return_exceptions=True)
            
            # 处理结果
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Task raised exception: {str(result)}")
                    processed_results.append({
                        "success": False,
                        "error": str(result)
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
    
    def create_batch_from_data(self, workflow_id: str, data_list: List[Dict]) -> List[BatchTask]:
        """从数据列表创建批处理任务"""
        tasks = []
        for i, data in enumerate(data_list):
            task = BatchTask(
                workflow_id=workflow_id,
                data=data,
                priority=len(data_list) - i  # 让后面的数据先处理
            )
            tasks.append(task)
        return tasks