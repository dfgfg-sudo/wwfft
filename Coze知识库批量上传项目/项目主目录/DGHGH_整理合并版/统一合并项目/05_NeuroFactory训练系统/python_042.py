# main_controller.py
#!/usr/bin/env python3
"""
Coze工作流增量批量自动化主控制器
"""
import asyncio
import yaml
import argparse
from datetime import datetime, timedelta
from workflow_generator import CozeWorkflowGenerator
from batch_executor import CozeBatchExecutor
from incremental_manager import IncrementalManager
import logging

class CozeAutomationController:
    def __init__(self, config_file: str = "config.yaml"):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.workflow_generator = CozeWorkflowGenerator(config_file)
        self.batch_executor = CozeBatchExecutor(
            api_key=self.config['workflow_automation']['coze_api']['api_key'],
            max_concurrent=self.config['workflow_automation']['batch_processing']['max_concurrent']
        )
        self.incremental_manager = IncrementalManager()
        
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'automation_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def run_incremental_pipeline(self, source_name: str):
        """运行增量处理管道"""
        self.logger.info(f"Starting incremental pipeline for {source_name}")
        
        # 1. 获取增量数据
        incremental_data = self.workflow_generator.detect_incremental_data(source_name)
        
        if not incremental_data:
            self.logger.info("No new data to process")
            return
        
        self.logger.info(f"Found {len(incremental_data)} new items to process")
        
        # 2. 去重检查
        unique_data = []
        for data in incremental_data:
            if not self.incremental_manager.check_data_duplicate(source_name, data):
                unique_data.append(data)
        
        if not unique_data:
            self.logger.info("All data already processed")
            return
        
        # 3. 生成工作流
        workflow_params = self.workflow_generator.generate_workflow_parameters(unique_data)
        
        # 4. 创建工作流
        workflow_id = await self.workflow_generator.create_workflow(workflow_params)
        self.logger.info(f"Created workflow: {workflow_id}")
        
        # 5. 创建批处理任务
        batch_tasks = self.batch_executor.create_batch_from_data(workflow_id, unique_data)
        
        # 6. 记录批处理开始
        batch_id = self.incremental_manager.record_batch_start(
            batch_id=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            workflow_id=workflow_id,
            total_items=len(batch_tasks)
        )
        
        # 7. 执行批处理
        self.logger.info(f"Executing batch {batch_id} with {len(batch_tasks)} tasks")
        results = await self.batch_executor.execute_batch(batch_tasks)
        
        # 8. 记录结果
        self.incremental_manager.record_batch_complete(batch_id, results)
        
        # 9. 更新状态
        for data in unique_data:
            self.incremental_manager.mark_data_processed(source_name, data)
        
        # 10. 保存检查点
        checkpoint = {
            "last_id": unique_data[-1].get('id') if unique_data else None,
            "batch_id": batch_id,
            "processed_count": len(unique_data)
        }
        self.incremental_manager.update_checkpoint(source_name, checkpoint)
        
        self.logger.info(f"Incremental pipeline completed for {source_name}")
    
    async def run_scheduled_batch(self):
        """运行定时批处理"""
        sources = self.config['workflow_automation']['data_sources']
        
        for source in sources:
            source_name = source.get('name', source['type'])
            try:
                await self.run_incremental_pipeline(source_name)
            except Exception as e:
                self.logger.error(f"Error processing {source_name}: {str(e)}")
                continue
    
    def generate_monitoring_dashboard(self):
        """生成监控仪表板"""
        import pandas as pd
        from tabulate import tabulate
        
        cursor = self.incremental_manager.conn.cursor()
        
        # 获取批处理统计
        cursor.execute('''
        SELECT 
            batch_id,
            workflow_id,
            total_items,
            processed_items,
            failed_items,
            status,
            start_time,
            end_time
        FROM batch_records
        ORDER BY start_time DESC
        LIMIT 10
        ''')
        
        batches = cursor.fetchall()
        
        df = pd.DataFrame(batches, columns=[
            'Batch ID', 'Workflow ID', 'Total', 'Processed', 
            'Failed', 'Status', 'Start Time', 'End Time'
        ])
        
        print("=== Coze自动化处理监控仪表板 ===")
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n最近10个批处理任务:")
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
        
        # 统计信息
        cursor.execute('SELECT COUNT(*) FROM batch_records')
        total_batches = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(total_items) FROM batch_records')
        total_items = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(failed_items) FROM batch_records')
        failed_items = cursor.fetchone()[0] or 0
        
        success_rate = ((total_items - failed_items) / total_items * 100) if total_items > 0 else 0
        
        print(f"\n总体统计:")
        print(f"- 总批次数: {total_batches}")
        print(f"- 总处理项: {total_items}")
        print(f"- 失败项: {failed_items}")
        print(f"- 成功率: {success_rate:.2f}%")

async def main():
    parser = argparse.ArgumentParser(description='Coze工作流增量批量自动化处理器')
    parser.add_argument('--config', type=str, default='config.yaml', help='配置文件路径')
    parser.add_argument('--mode', type=str, choices=['run', 'monitor', 'test'], 
                       default='run', help='运行模式')
    parser.add_argument('--source', type=str, help='指定数据源')
    parser.add_argument('--batch-size', type=int, help='批处理大小')
    
    args = parser.parse_args()
    
    controller = CozeAutomationController(args.config)
    
    if args.mode == 'run':
        if args.source:
            await controller.run_incremental_pipeline(args.source)
        else:
            await controller.run_scheduled_batch()
    
    elif args.mode == 'monitor':
        controller.generate_monitoring_dashboard()
    
    elif args.mode == 'test':
        # 测试模式
        print("运行测试...")
        # 这里可以添加测试代码

if __name__ == "__main__":
    asyncio.run(main())