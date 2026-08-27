#!/usr/bin/env python3
"""
Coze工作流批量修复工具
用于修复存储在PostgreSQL中的工作流配置错误
"""
import psycopg2
import json
import re
from typing import Dict, List, Any
from datetime import datetime

class CozeWorkflowFixer:
    def __init__(self, db_params: Dict):
        self.conn = psycopg2.connect(**db_params)
        self.cur = self.conn.cursor()
        
    def fetch_workflows_with_errors(self) -> List[Dict]:
        """获取所有存在错误的工作流"""
        query = """
        SELECT id, name, definition, config, error_count
        FROM coze_workflows 
        WHERE error_count > 0 
           OR definition::text LIKE '%error%'
           OR EXISTS (
               SELECT 1 FROM coze_executions 
               WHERE workflow_id = coze_workflows.id 
               AND status = 'failed'
               AND completed_at > NOW() - INTERVAL '7 days'
           )
        """
        self.cur.execute(query)
        return [
            {
                'id': row[0],
                'name': row[1],
                'definition': row[2],
                'config': row[3],
                'error_count': row[4]
            }
            for row in self.cur.fetchall()
        ]
    
    def detect_and_fix_errors(self, workflow: Dict) -> Dict:
        """检测并修复工作流中的各种错误"""
        definition = workflow['definition']
        fixes_applied = []
        
        # 1. 检查并修复PostgreSQL节点连接配置
        fixes_applied.extend(self._fix_postgres_connections(definition))
        
        # 2. 修复SQL语法错误
        fixes_applied.extend(self._fix_sql_syntax(definition))
        
        # 3. 修复缺失的变量映射
        fixes_applied.extend(self._fix_missing_mappings(definition))
        
        # 4. 修复数据类型转换问题
        fixes_applied.extend(self._fix_data_type_conversions(definition))
        
        # 5. 修复条件逻辑错误
        fixes_applied.extend(self._fix_condition_errors(definition))
        
        return {
            'workflow_id': workflow['id'],
            'fixes_applied': fixes_applied,
            'new_definition': definition,
            'fixed_at': datetime.now().isoformat()
        }
    
    def _fix_postgres_connections(self, definition: Dict) -> List[str]:
        """修复数据库连接配置"""
        fixes = []
        
        if 'nodes' in definition:
            for i, node in enumerate(definition['nodes']):
                if node.get('type') == 'postgres':
                    config = node.get('config', {})
                    
                    # 修复旧版连接格式
                    if 'connectionString' in config:
                        old_conn = config['connectionString']
                        if 'localhost' in old_conn:
                            new_conn = old_conn.replace('localhost', 'production-db.example.com')
                            config['connectionString'] = new_conn
                            fixes.append(f"Updated connection string in node {node.get('name', i)}")
                    
                    # 添加SSL模式如果缺失
                    if 'connectionString' in config and 'sslmode' not in config['connectionString']:
                        config['connectionString'] += '?sslmode=require'
                        fixes.append(f"Added SSL mode to connection in node {node.get('name', i)}")
        
        return fixes
    
    def _fix_sql_syntax(self, definition: Dict) -> List[str]:
        """修复SQL语法问题"""
        fixes = []
        
        if 'nodes' in definition:
            for i, node in enumerate(definition['nodes']):
                if node.get('type') == 'postgres':
                    config = node.get('config', {})
                    sql = config.get('sql', '')
                    
                    # 修复缺少分号
                    if sql and not sql.strip().endswith(';'):
                        config['sql'] = sql.rstrip() + ';'
                        fixes.append(f"Added missing semicolon in node {node.get('name', i)}")
                    
                    # 修复SELECT * 问题
                    if 'SELECT *' in sql and 'LIMIT' not in sql:
                        # 添加限制避免返回过多数据
                        if not re.search(r'LIMIT\s+\d+', sql, re.IGNORECASE):
                            config['sql'] = re.sub(r'$', ' LIMIT 1000', sql)
                            fixes.append(f"Added LIMIT clause in node {node.get('name', i)}")
        
        return fixes
    
    def _fix_missing_mappings(self, definition: Dict) -> List[str]:
        """修复缺失的变量映射"""
        fixes = []
        
        if 'nodes' in definition:
            for i, node in enumerate(definition['nodes']):
                config = node.get('config', {})
                
                # 检查PostgreSQL节点的输入映射
                if node.get('type') == 'postgres':
                    if 'inputMapping' not in config:
                        config['inputMapping'] = {}
                        fixes.append(f"Added inputMapping to PostgreSQL node {node.get('name', i)}")
                    
                    # 如果SQL中有变量但映射中不存在，添加默认映射
                    sql = config.get('sql', '')
                    if sql:
                        variables = re.findall(r'\$\{(\w+)\}', sql)  # 查找 ${variable} 模式
                        for var in variables:
                            if var not in config['inputMapping']:
                                config['inputMapping'][var] = f"{{{{input.{var}}}}}"
                                fixes.append(f"Added mapping for variable ${var} in node {node.get('name', i)}")
        
        return fixes
    
    def _fix_data_type_conversions(self, definition: Dict) -> List[str]:
        """修复数据类型转换问题"""
        fixes = []
        
        if 'nodes' in definition:
            for i, node in enumerate(definition['nodes']):
                config = node.get('config', {})
                
                # 为可能产生类型错误的SQL添加CAST
                if node.get('type') == 'postgres':
                    sql = config.get('sql', '')
                    if sql:
                        # 修复常见的字符串转数字问题
                        patterns = [
                            (r'(\w+)\s*=\s*(\'\d+\')', r"\1 = \2::integer"),
                            (r'WHERE\s+id\s*=\s*(\'\w+\')', r"WHERE id = \1::uuid"),
                        ]
                        
                        for pattern, replacement in patterns:
                            if re.search(pattern, sql, re.IGNORECASE):
                                config['sql'] = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)
                                fixes.append(f"Added type casting in node {node.get('name', i)}")
        
        return fixes
    
    def save_fixed_workflow(self, workflow_id: str, new_definition: Dict):
        """保存修复后的工作流到数据库"""
        update_query = """
        UPDATE coze_workflows 
        SET definition = %s, 
            error_count = 0,
            updated_at = NOW(),
            config = jsonb_set(
                COALESCE(config, '{}'::jsonb),
                '{last_fixed}',
                to_jsonb(NOW())
            )
        WHERE id = %s
        """
        
        self.cur.execute(update_query, (json.dumps(new_definition), workflow_id))
        
        # 记录修复历史
        history_query = """
        INSERT INTO coze_fix_history 
        (workflow_id, fixes_applied, fixed_at, fixed_by)
        VALUES (%s, %s, NOW(), 'auto_fixer')
        """
        self.cur.execute(history_query, (workflow_id, json.dumps({'auto_fixed': True})))
        
        self.conn.commit()
    
    def run_batch_fix(self, limit: int = 100):
        """批量运行修复"""
        workflows = self.fetch_workflows_with_errors()[:limit]
        
        print(f"Found {len(workflows)} workflows with errors")
        
        for workflow in workflows:
            print(f"\nProcessing workflow: {workflow['name']} (ID: {workflow['id']})")
            
            try:
                result = self.detect_and_fix_errors(workflow)
                
                if result['fixes_applied']:
                    print(f"  Applied fixes: {len(result['fixes_applied'])}")
                    for fix in result['fixes_applied']:
                        print(f"    - {fix}")
                    
                    self.save_fixed_workflow(workflow['id'], result['new_definition'])
                    print(f"  ✓ Successfully saved fixed workflow")
                else:
                    print(f"  ✓ No fixes needed")
                    
            except Exception as e:
                print(f"  ✗ Error fixing workflow: {str(e)}")
        
        print(f"\nBatch fix completed. Processed {len(workflows)} workflows.")

# 使用示例
if __name__ == "__main__":
    db_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'coze_platform',
        'user': 'coze_admin',
        'password': 'your_password'
    }
    
    fixer = CozeWorkflowFixer(db_params)
    fixer.run_batch_fix(limit=50)