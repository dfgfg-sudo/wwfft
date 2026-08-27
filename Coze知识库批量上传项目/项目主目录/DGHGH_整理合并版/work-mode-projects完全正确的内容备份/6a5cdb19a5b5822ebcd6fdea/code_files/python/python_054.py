# incremental_manager.py
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
import hashlib

class IncrementalManager:
    def __init__(self, db_path: str = "incremental_state.db"):
        self.conn = sqlite3.connect(db_path)
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        cursor = self.conn.cursor()
        
        # 创建增量状态表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS incremental_state (
            source_name TEXT PRIMARY KEY,
            last_processed_id TEXT,
            last_processed_time TIMESTAMP,
            checkpoint_data TEXT,
            metadata TEXT
        )
        ''')
        
        # 创建批处理记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS batch_records (
            batch_id TEXT PRIMARY KEY,
            workflow_id TEXT,
            total_items INTEGER,
            processed_items INTEGER,
            failed_items INTEGER,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            status TEXT,
            results TEXT
        )
        ''')
        
        # 创建数据哈希表（用于去重）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_hashes (
            data_hash TEXT PRIMARY KEY,
            source_name TEXT,
            processed_time TIMESTAMP,
            FOREIGN KEY (source_name) REFERENCES incremental_state (source_name)
        )
        ''')
        
        self.conn.commit()
    
    def get_last_checkpoint(self, source_name: str) -> Optional[Dict]:
        """获取最后一个检查点"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT last_processed_id, last_processed_time, checkpoint_data '
            'FROM incremental_state WHERE source_name = ?',
            (source_name,)
        )
        
        row = cursor.fetchone()
        if row:
            return {
                "last_processed_id": row[0],
                "last_processed_time": row[1],
                "checkpoint_data": json.loads(row[2]) if row[2] else {}
            }
        return None
    
    def update_checkpoint(self, source_name: str, checkpoint_data: Dict):
        """更新检查点"""
        cursor = self.conn.cursor()
        
        checkpoint_json = json.dumps(checkpoint_data)
        
        cursor.execute('''
        INSERT OR REPLACE INTO incremental_state 
        (source_name, last_processed_id, last_processed_time, checkpoint_data)
        VALUES (?, ?, ?, ?)
        ''', (
            source_name,
            checkpoint_data.get('last_id'),
            datetime.now().isoformat(),
            checkpoint_json
        ))
        
        self.conn.commit()
    
    def record_batch_start(self, batch_id: str, workflow_id: str, total_items: int) -> str:
        """记录批处理开始"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
        INSERT INTO batch_records 
        (batch_id, workflow_id, total_items, start_time, status)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            batch_id,
            workflow_id,
            total_items,
            datetime.now().isoformat(),
            'running'
        ))
        
        self.conn.commit()
        return batch_id
    
    def record_batch_complete(self, batch_id: str, results: List[Dict]):
        """记录批处理完成"""
        cursor = self.conn.cursor()
        
        success_count = sum(1 for r in results if r.get('success'))
        failed_count = len(results) - success_count
        
        cursor.execute('''
        UPDATE batch_records 
        SET end_time = ?, status = ?, processed_items = ?, failed_items = ?, results = ?
        WHERE batch_id = ?
        ''', (
            datetime.now().isoformat(),
            'completed',
            len(results),
            failed_count,
            json.dumps(results),
            batch_id
        ))
        
        self.conn.commit()
    
    def check_data_duplicate(self, source_name: str, data: Dict) -> bool:
        """检查数据是否已处理（基于哈希）"""
        data_hash = self.generate_data_hash(data)
        
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT 1 FROM data_hashes WHERE data_hash = ? AND source_name = ?',
            (data_hash, source_name)
        )
        
        return cursor.fetchone() is not None
    
    def mark_data_processed(self, source_name: str, data: Dict):
        """标记数据已处理"""
        data_hash = self.generate_data_hash(data)
        
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR IGNORE INTO data_hashes (data_hash, source_name, processed_time)
        VALUES (?, ?, ?)
        ''', (data_hash, source_name, datetime.now().isoformat()))
        
        self.conn.commit()
    
    def generate_data_hash(self, data: Dict) -> str:
        """生成数据哈希值"""
        # 移除可能变化的字段（如时间戳）
        stable_data = {k: v for k, v in data.items() if k not in ['timestamp', 'updated_at']}
        data_str = json.dumps(stable_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()