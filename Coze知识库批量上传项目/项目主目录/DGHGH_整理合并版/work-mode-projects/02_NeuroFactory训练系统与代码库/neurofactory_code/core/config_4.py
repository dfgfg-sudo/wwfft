"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
多Coze JSON/OpenAPI规范文件一站式处理工具
完整稳定版本 - 解决所有闪退问题，支持TXT/JSON/YAML互相转换
\"\"\"

import json
import yaml
import os
import sys
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import chardet
from datetime import datetime
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import copy
import traceback
import queue

# ==================== 全局异常处理 ====================
def 全局异常处理(exc_type, exc_value, exc_traceback):
    \"\"\"全局异常处理器，防止程序闪退\"\"\"
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.critical(f"未捕获的异常: {error_msg}")

    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "程序错误",
            f"程序遇到意外错误:\\n\\n{exc_type.__name__}: {exc_value}\\n\\n"
            f"详细信息已记录到日志文件。"
        )
        root.destroy()
    except:
        pass

sys.excepthook = 全局异常处理

# ==================== 配置日志系统 ====================
def 配置日志系统():
    \"\"\"配置健壮的日志系统\"\"\"
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"coze_processor_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger("CozeProcessor")
    except Exception as e:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        return logging.getLogger("CozeProcessor")

logger = 配置日志系统()

class CozeJSONProcessor:
    \"\"\"Coze JSON/OpenAPI/TXT/YAML规范文件处理器 - 完整稳定版本\"\"\"

    def __init__(self):
        self.处理日志 = []
        self.合并优先级 = {}
        self.支持的OpenAPI版本 = ['2.0', '3.0.0', '3.0.1', '3.0.2', '3.0.3', '3.1.0']
        self.Coze必需节点 = ['metadata', 'interface', 'logic']
        self.批量处理线程数 = 3

    def 安全执行(self, 功能, 默认值=None, 错误信息="操作失败"):
        \"\"\"安全执行函数，防止异常传播\"\"\"
        try:
            return 功能()
        except Exception as e:
            logger.error(f"{错误信息}: {str(e)}")
            if 默认值 is not None:
                return 默认值
            raise

    def 记录日志(self, 类型: str, 位置: str, 修复方式: str, 修复前内容: Any = None, 修复后内容: Any = None):
        \"\"\"记录详细的修复日志\"\"\"
        try:
            日志条目 = {
                '时间戳': datetime.now().isoformat(),
                '类型': 类型,
                '位置': 位置,
                '修复方式': 修复方式,
                '修复前': str(修复前内容)[:500] if 修复前内容 else None,
                '修复后': str(修复后内容)[:500] if 修复后内容 else None
            }
            self.处理日志.append(日志条目)
            logger.info(f"{类型} - {位置}: {修复方式}")
            return 日志条目
        except Exception as e:
            logger.error(f"记录日志失败: {e}")
            return None

    def 获取处理统计(self) -> Dict[str, int]:
        \"\"\"获取处理统计信息\"\"\"
        try:
            统计 = {
                '总文件数': 0,
                '成功文件数': 0,
                '失败文件数': 0,
                '总修复数': len(self.处理日志),
                '格式错误修复数': len([日志 for 日志 in self.处理日志 if 日志 and '格式' in 日志['类型']]),
                '参数错误修复数': len([日志 for 日志 in self.处理日志 if 日志 and '参数' in 日志['类型']]),
                '合并冲突解决数': len([日志 for 日志 in self.处理日志 if 日志 and ('合并' in 日志['类型'] or '冲突' in 日志['类型'])])
            }
            return 统计
        except Exception as e:
            logger.error(f"获取统计失败: {e}")
            return {}

    def 检测文件编码(self, 文件路径: str) -> str:
        \"\"\"自动检测文件编码\"\"\"
        return self.安全执行(
            lambda: self._检测文件编码实现(文件路径),
            默认值='utf-8',
            错误信息=f"检测文件编码失败 {文件路径}"
        )

    def _检测文件编码实现(self, 文件路径: str) -> str:
        \"\"\"实际的编码检测实现\"\"\"
        try:
            with open(文件路径, 'rb') as 文件:
                原始数据 = 文件.read(4096)
                编码结果 = chardet.detect(原始数据)
                编码 = 编码结果.get('encoding', 'utf-8')
                if 编码 and 编码.lower() != 'ascii':
                    return 编码
                return 'utf-8'
        except Exception as e:
            self.记录日志('编码检测错误', 文件路径, '使用默认UTF-8编码', str(e), 'utf-8')
            return 'utf-8'

    def 批量读取文件(self, 文件路径列表: List[str]) -> List[Tuple[str, Dict[str, Any]]]:
        \"\"\"批量读取多个文件\"\"\"
        def 读取单个文件(文件路径: str) -> Tuple[str, Dict[str, Any]]:
            try:
                数据 = self.读取JSON文件(文件路径)
                return (文件路径, 数据)
            except Exception as 异常:
                self.记录日志('文件读取失败', 文件路径, '跳过此文件', str(异常), None)
                return (文件路径, None)

        try:
            结果列表 = []
            with ThreadPoolExecutor(max_workers=min(self.批量处理线程数, len(文件路径列表))) as 执行器:
                未来任务 = {执行器.submit(读取单个文件, 路径): 路径 for 路径 in 文件路径列表}
                for 未来 in as_completed(未来任务):
                    文件路径 = 未来任务[未来]
                    try:
                        结果 = 未来.result(timeout=30)
                        if 结果[1] is not None:
                            结果列表.append(结果)
                    except Exception as 异常:
                        self.记录日志('批量读取异常', 文件路径, '任务执行失败', str(异常), None)

            return 结果列表
        except Exception as e:
            logger.error(f"批量读取失败: {e}")
            return []

    def 读取JSON文件(self, 文件路径: str) -> Dict[str, Any]:
        \"\"\"读取JSON文件\"\"\"
        return self.安全执行(
            lambda: self._读取JSON文件实现(文件路径),
            默认值={},
            错误信息=f"读取JSON文件失败 {文件路径}"
        )

    def _读取JSON文件实现(self, 文件路径: str) -> Dict[str, Any]:
        \"\"\"实际的JSON文件读取实现\"\"\"
        编码 = self.检测文件编码(文件路径)
        编码列表 = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'utf-16', 'cp1252']

        for 编码 in 编码列表:
            try:
                with open(文件路径, 'r', encoding=编码) as 文件:
                    内容 = 文件.read()
                    return self.解析JSON文本(内容, 文件路径)
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.warning(f"使用编码 {编码} 读取失败: {e}")
                continue

        raise ValueError(f"无法读取文件 {文件路径}，所有编码尝试失败")

    def 解析JSON文本(self, json文本: str, 来源: str = "文本输入") -> Dict[str, Any]:
        \"\"\"解析JSON文本\"\"\"
        return self.安全执行(
            lambda: self._解析JSON文本实现(json文本, 来源),
            默认值={},
            错误信息=f"解析JSON文本失败 {来源}"
        )

    def _解析JSON文本实现(self, json文本: str, 来源: str) -> Dict[str, Any]:
        \"\"\"实际的JSON文本解析实现\"\"\"
        try:
            return json.loads(json文本)
        except json.JSONDecodeError as 异常:
            修复后文本 = self.修复JSON格式错误(json文本, 来源, str(异常))
            try:
                return json.loads(修复后文本)
            except json.JSONDecodeError as 二次异常:
                最终文本 = self.深度修复JSON(修复后文本, 来源)
                try:
                    return json.loads(最终文本)
                except json.JSONDecodeError:
                    self.记录日志('JSON解析错误', 来源, '自动修复失败', json文本[:200], 最终文本[:200])
                    return {}

    def 修复JSON格式错误(self, json文本: str, 来源: str, 错误信息: str) -> str:
        \"\"\"修复常见的JSON格式错误\"\"\"
        try:
            修复后文本 = json文本

            修复后文本 = re.sub(r',\\s*}', '}', 修复后文本)
            修复后文本 = re.sub(r',\\s*]', ']', 修复后文本)
            修复后文本 = re.sub(r"'([^']*)'", r'"\\1"', 修复后文本)
            修复后文本 = 修复后文本.replace('\\n', '\\\\n').replace('\\t', '\\\\t').replace('\\r', '\\\\r')
            修复后文本 = re.sub(r'//.*?$', '', 修复后文本, flags=re.MULTILINE)
            修复后文本 = re.sub(r'/\\*[\\s\\S]*?\\*/', '', 修复后文本, flags=re.DOTALL)
            修复后文本 = re.sub(r'([{,]\\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\\s*:)', r'\\1"\\2"\\3', 修复后文本)

            self.记录日志('JSON格式修复', 来源, 错误信息, json文本[:100], 修复后文本[:100])
            return 修复后文本
        except Exception as e:
            logger.error(f"JSON修复失败: {e}")
            return json文本

    def 深度修复JSON(self, json文本: str, 来源: str) -> str:
        \"\"\"深度修复JSON格式错误\"\"\"
        try:
            行列表 = [行.strip() for 行 in json文本.split('\\n') if 行.strip()]
            修复行列表 = []

            for 行 in 行列表:
                if 行.startswith(('//', '/*', '*')):
                    continue

                if ':' in 行 and not 行.startswith('"'):
                    键, 值 = 行.split(':', 1)
                    键 = 键.strip()
                    if not (键.startswith('"') and 键.endswith('"')):
                        键 = f'"{键}"'
                    修复行列表.append(f'  {键}: {值.strip()}')
                else:
                    修复行列表.append(行)

            if 修复行列表:
                修复后文本 = '{\\n' + ',\\n'.join(修复行列表) + '\\n}'
            else:
                修复后文本 = '{}'

            self.记录日志('深度JSON修复', 来源, '构建基本JSON结构', json文本[:100], 修复后文本[:100])
            return 修复后文本
        except Exception as e:
            logger.error(f"深度修复失败: {e}")
            return '{}'

    def 验证OpenAPI规范(self, openapi数据: Dict[str, Any]) -> Tuple[bool, List[str]]:
        \"\"\"验证OpenAPI规范并返回错误列表\"\"\"
        错误列表 = []

        版本 = openapi数据.get('openapi') or openapi数据.get('swagger', '')
        if not 版本:
            错误列表.append("无法识别OpenAPI版本")
        elif 版本 not in self.支持的OpenAPI版本:
            错误列表.append(f"不支持的OpenAPI版本: {版本}")

        if 版本 and 版本.startswith('3.'):
            必需字段 = ['info', 'paths']
        else:
            必需字段 = ['info', 'paths', 'swagger']

        for 字段 in 必需字段:
            if 字段 not in openapi数据:
                错误列表.append(f"缺少必需字段: {字段}")

        if 'info' in openapi数据:
            info = openapi数据['info']
            if 'title' not in info:
                错误列表.append("info中缺少title字段")
            if 'version' not in info:
                错误列表.append("info中缺少version字段")

        if 'paths' in openapi数据和 not isinstance(openapi数据['paths'], dict):
            错误列表.append("paths字段必须是对象")

        return len(错误列表) == 0, 错误列表

    def 修复OpenAPI参数错误(self, openapi数据: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"修复OpenAPI规范中的参数错误\"\"\"
        修复后数据 = copy.deepcopy(openapi数据)
        版本 = 修复后数据.get('openapi') or 修复后数据.get('swagger', '')

        if 版本.startswith('3.'):
            修复后数据 = self.修复OpenAPIV3参数(修复后数据)
        elif 版本 == '2.0':
            修复后数据 = self.修复OpenAPIV2参数(修复后数据)
        else:
            self.记录日志('OpenAPI版本未知', '参数修复', '跳过参数修复', 版本, 版本)

        return 修复后数据

    def 修复OpenAPIV3参数(self, openapi数据: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"修复OpenAPI v3版本参数问题\"\"\"
        修复后数据 = copy.deepcopy(openapi数据)

        if 'paths' in 修复后数据:
            for 路径, 方法定义 in 修复后数据['paths'].items():
                if not isinstance(方法定义, dict):
                    continue

                for 方法, 操作定义 in 方法定义.items():
                    if not isinstance(操作定义, dict):
                        continue

                    if 'parameters' in 操作定义:
                        修复后参数 = []
                        for 参数 in 操作定义['parameters']:
                            if isinstance(参数, dict):
                                修复后参数.append(self.修复单个参数V3(参数))
                        操作定义['parameters'] = 修复后参数

                    if 'requestBody' in 操作定义 and isinstance(操作定义['requestBody'], dict):
                        操作定义['requestBody'] = self.修复RequestBodyV3(操作定义['requestBody'])

        if 'components' in 修复后数据 and isinstance(修复后数据['components'], dict):
            if 'parameters' in 修复后数据['components']:
                for 参数名, 参数定义 in 修复后数据['components']['parameters'].items():
                    if isinstance(参数定义, dict):
                        修复后数据['components']['parameters'][参数名] = self.修复单个参数V3(参数定义)

            if 'schemas' in 修复后数据['components']:
                for 模型名, 模型定义 in 修复后数据['components']['schemas'].items():
                    if isinstance(模型定义, dict):
                        修复后数据['components']['schemas'][模型名] = self.修复SchemaV3(模型定义)

        return 修复后数据

    def 修复单个参数V3(self, 参数: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"修复单个OpenAPI v3参数\"\"\"
        修复后参数 = copy.deepcopy(参数)

        if 'name' not in 修复后参数:
            修复后参数['name'] = 'unknown_parameter'
            self.记录日志('参数名缺失', 'OpenAPI参数', '添加默认参数名', 参数.get('name'), 'unknown_parameter')

        if 'in' not in 修复后参数:
            修复后参数['in'] = 'query'
            self.记录日志('参数位置缺失', 'OpenAPI参数', '添加默认位置', 参数.get('in'), 'query')

        if 'schema' not in 修复后参数:
            if 'type' in 修复后参数:
                修复后参数['schema'] = {'type': 修复后参数.pop('type')}
                if 'format' in 修复后参数:
                    修复后参数['schema']['format'] = 修复后参数.pop('format')
                self.记录日志('参数schema修复', f"参数{修复后参数['name']}", '迁移type到schema', 参数.get('type'), 修复后参数['schema'])
            else:
                修复后参数['schema'] = {'type': 'string'}

        if 'required' in 修复后参数 and not isinstance(修复后参数['required'], bool):
            原始值 = 修复后参数['required']
            修复后参数['required'] = bool(修复后参数['required'])
            self.记录日志('参数required修复', f"参数{修复后参数['name']}", '转换为布尔值', 原始值, 修复后参数['required'])

        if 'description' in 修复后参数 and not isinstance(修复后参数['description'], str):
            修复后参数['description'] = str(修复后参数['description'])

        return 修复后参数

    def 修复RequestBodyV3(self, requestBody: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"修复OpenAPI v3 requestBody\"\"\"
        修复后Body = copy.deepcopy(requestBody)

        if 'content' not in 修复后Body:
            修复后Body['content'] = {
                'application/json': {
                    'schema': {'type': 'object'}
                }
            }
            self.记录日志('RequestBody修复', 'requestBody', '添加默认content', None, 修复后Body['content'])

        return 修复后Body

    def 修复SchemaV3(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"修复OpenAPI v3 schema定义\"\"\"
        修复后Schema = copy.deepcopy(schema)

        if 'type' not in 修复后Schema:
            修复后Schema['type'] = 'object'

        if 'properties' in 修复后Schema and isinstance(修复后Schema['properties'], dict):
            for 属性名, 属性定义 in 修复后Schema['properties'].items():
                if isinstance(属性定义, dict) and 'type' not in 属性定义:
                    属性定义['type'] = 'string'

        return 修复后Schema

    def 修复OpenAPIV2参数(self, openapi数据: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"修复OpenAPI v2版本参数问题\"\"\"
        修复后数据 = copy.deepcopy(openapi数据)

        if 'paths' in 修复后数据 and isinstance(修复后数据['paths'], dict):
            for 路径, 方法定义 in 修复后数据['paths'].items():
                if not isinstance(方法定义, dict):
                    continue

                for 方法, 操作定义 in 方法定义.items():
                    if isinstance(操作定义, dict) and 'parameters' in 操作定义:
                        修复后参数 = []
                        for 参数 in 操作定义['parameters']:
                            if isinstance(参数, dict):
                                修复后参数.append(self.修复单个参数V2(参数))
                        操作定义['parameters'] = 修复后参数

        return 修复后数据

    def 修复单个参数V2(self, 参数: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"修复单个OpenAPI v2参数\"\"\"
        修复后参数 = copy.deepcopy(参数)

        if 'name' not in 修复后参数:
            修复后参数['name'] = 'unknown_parameter'

        if 'in' not in 修复后参数:
            修复后参数['in'] = 'query'

        if 'type' not in 修复后参数:
            修复后参数['type'] = 'string'

        if 'required' in 修复后参数 and not isinstance(修复后参数['required'], bool):
            修复后参数['required'] = bool(修复后参数['required'])

        if 'enum' in 修复后参数 and not isinstance(修复后参数['enum'], list):
            修复后参数['enum'] = [修复后参数['enum']]

        return 修复后参数

    def 合并多个JSON文件(self, json文件列表: List[Dict[str, Any]], 优先级规则: Dict[str, Any] = None) -> Dict[str, Any]:
        \"\"\"合并多个JSON文件，处理结构冲突\"\"\"
        return self.安全执行(
            lambda: self._合并多个JSON文件实现(json文件列表, 优先级规则),
            默认值={},
            错误信息="合并JSON文件失败"
        )

    def _合并多个JSON文件实现(self, json文件列表: List[Dict[str, Any]], 优先级规则: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"实际的合并实现\"\"\"
        if not json文件列表:
            return {}

        if len(json文件列表) == 1:
            return json文件列表[0]

        合并结果 = {}
        优先级映射 = self.构建优先级映射(优先级规则, len(json文件列表))

        for 节点 in self.Coze必需节点:
            节点合并结果 = self.合并节点(节点, json文件列表, 优先级映射)
            if 节点合并结果:
                合并结果[节点] = 节点合并结果

        if 'logic' in 合并结果 and 'steps' in 合并结果['logic']:
            合并结果['logic']['steps'] = self.确保步骤唯一性(合并结果['logic']['steps'])

        验证通过, 错误列表 = self.验证Coze兼容性(合并结果)
        if not 验证通过:
            self.记录日志('合并验证警告', '合并结果', '存在兼容性问题', None, 错误列表)

        return 合并结果

    def 构建优先级映射(self, 优先级规则: Dict[str, Any], 文件数量: int) -> Dict[int, int]:
        \"\"\"构建文件优先级映射\"\"\"
        if not 优先级规则:
            return {i: i for i in range(文件数量)}

        优先级映射 = {}
        for i in range(文件数量):
            优先级 = 优先级规则.get(f'file_{i}') or 优先级规则.get(str(i)) or i
            优先级映射[i] = 优先级

        return 优先级映射

    def 合并节点(self, 节点名: str, json文件列表: List[Dict[str, Any]], 优先级映射: Dict[int, int]) -> Any:
        \"\"\"合并特定节点\"\"\"
        节点值列表 = []

        for i, json数据 in enumerate(json文件列表):
            if 节点名 in json数据:
                节点值列表.append({
                    'value': json数据[节点名],
                    'priority': 优先级映射[i],
                    'index': i
                })

        if not 节点值列表:
            return None

        节点值列表.sort(key=lambda x: x['priority'], reverse=True)

        if 节点名 == 'metadata':
            return self.合并metadata节点(节点值列表)
        elif 节点名 == 'interface':
            return self.合并interface节点(节点值列表)
        elif 节点名 == 'logic':
            return self.合并logic节点(节点值列表)
        else:
            return 节点值列表[0]['value']

    def 合并metadata节点(self, 节点值列表: List[Dict[str, Any]]) -> Dict[str, Any]:
        \"\"\"合并metadata节点\"\"\"
        合并结果 = {}
        字段优先级 = {}

        for 节点数据 in 节点值列表:
            值 = 节点数据['value']
            if isinstance(值, dict):
                for 键, 值 in 值.items():
                    当前优先级 = 节点数据['priority']
                    if 键 not in 合并结果 or 当前优先级 > 字段优先级.get(键, -1):
                        合并结果[键] = 值
                        字段优先级[键] = 当前优先级
                        if 键 in 字段优先级:
                            self.记录日志('metadata字段冲突', f"metadata.{键}", f'使用优先级{当前优先级}的值',
                                      合并结果.get(键), 值)

        return 合并结果

    def 合并interface节点(self, 节点值列表: List[Dict[str, Any]]) -> Dict[str, Any]:
        \"\"\"合并interface节点\"\"\"
        合并结果 = {'actions': [], 'responses': []}
        action映射 = {}
        response映射 = {}

        for 节点数据 in 节点值列表:
            值 = 节点数据['value']
            if isinstance(值, dict):
                if 'actions' in 值 and isinstance(值['actions'], list):
                    for action in 值['actions']:
                        if isinstance(action, dict) and 'name' in action:
                            action名 = action['name']
                            当前优先级 = 节点数据['priority']
                            if action名 not in action映射 or 当前优先级 > action映射[action名]['priority']:
                                if action名 in action映射:
                                    self.记录日志('action冲突', f"interface.actions.{action名}",
                                              f'使用优先级{当前优先级}的版本',
                                              action映射[action名]['action'], action)
                                action映射[action名] = {'action': action, 'priority': 当前优先级}

                if 'responses' in 值 and isinstance(值['responses'], list):
                    for response in 值['responses']:
                        if isinstance(response, dict) and 'name' in response:
                            response名 = response['name']
                            当前优先级 = 节点数据['priority']
                            if response名 not in response映射 or 当前优先级 > response映射[response名]['priority']:
                                if response名 in response映射:
                                    self.记录日志('response冲突', f"interface.responses.{response名}",
                                              f'使用优先级{当前优先级}的版本',
                                              response映射[response名]['response'], response)
                                response映射[response名] = {'response': response, 'priority': 当前优先级}

        合并结果['actions'] = [数据['action'] for 数据 in action映射.values()]
        合并结果['responses'] = [数据['response'] for 数据 in response映射.values()]

        return 合并结果

    def 合并logic节点(self, 节点值列表: List[Dict[str, Any]]) -> Dict[str, Any]:
        \"\"\"合并logic节点\"\"\"
        合并结果 = {'steps': []}
        步骤映射 = {}

        for 节点数据 in 节点值列表:
            值 = 节点数据['value']
            if isinstance(值, dict) and 'steps' in 值 and isinstance(值['steps'], list):
                for 步骤 in 值['steps']:
                    if isinstance(步骤, dict) and 'id' in 步骤:
                        步骤id = 步骤['id']
                        当前优先级 = 节点数据['priority']
                        if 步骤id not in 步骤映射 or 当前优先级 > 步骤映射[步骤id]['priority']:
                            if 步骤id in 步骤映射:
                                self.记录日志('logic步骤冲突', f"logic.steps.{步骤id}",
                                          f'使用优先级{当前优先级}的版本',
                                          步骤映射[步骤id]['step'], 步骤)
                            步骤映射[步骤id] = {'step': 步骤, 'priority': 当前优先级}

        合并结果['steps'] = [数据['step'] for 数据 in 步骤映射.values()]

        return 合并结果

    def 确保步骤唯一性(self, 步骤列表: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        \"\"\"确保logic步骤ID唯一性\"\"\"
        唯一步骤映射 = {}
        步骤计数器 = {}
        重复修复计数 = 0

        for 步骤 in 步骤列表:
            if not isinstance(步骤, dict):
                continue

            步骤id = 步骤.get('id', 'unknown_step')

            if 步骤id in 唯一步骤映射:
                if 步骤id not in 步骤计数器:
                    步骤计数器[步骤id] = 1
                步骤计数器[步骤id] += 1
                新id = f"{步骤id}_{步骤计数器[步骤id]}"

                self.记录日志('步骤ID重复', f"logic.steps.{步骤id}", f'重命名为{新id}', 步骤.get('id'), 新id)
                步骤['id'] = 新id
                步骤id = 新id
                重复修复计数 += 1

            唯一步骤映射[步骤id] = 步骤

        if 重复修复计数 > 0:
            self.记录日志('步骤唯一性修复', 'logic.steps', f'修复了{重复修复计数}个重复步骤ID', None, 重复修复计数)

        return list(唯一步骤映射.values())

    def JSON转YAML(self, json数据: Dict[str, Any]) -> str:
        \"\"\"将JSON数据转换为Coze YAML格式\"\"\"
        return self.安全执行(
            lambda: self._JSON转YAML实现(json数据),
            默认值="转换失败",
            错误信息="JSON转YAML失败"
        )

    def _JSON转YAML实现(self, json数据: Dict[str, Any]) -> str:
        \"\"\"实际的YAML转换实现\"\"\"
        yaml模板 = {
            'metadata': json数据.get('metadata', {}),
            'interface': json数据.get('interface', {}),
            'logic': json数据.get('logic', {})
        }

        标准化数据 = self.应用CozeYAML标准(yaml模板)

        yaml内容 = yaml.dump(
            标准化数据,
            allow_unicode=True,
            indent=2,
            default_flow_style=False,
            sort_keys=False
        )

        yaml内容 = f"# Coze插件配置\\n# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n" + yaml内容
        self.记录日志('YAML转换', 'JSON转YAML', '成功转换', None, '转换完成')
        return yaml内容

    def 应用CozeYAML标准(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"应用Coze YAML标准\"\"\"
        try:
            标准化数据 = copy.deepcopy(数据)

            for 节点 in self.Coze必需节点:
                if 节点 not in 标准化数据:
                    标准化数据[节点] = {}

            元数据 = 标准化数据['metadata']
            元数据.setdefault('name', '未命名Coze插件')
            元数据.setdefault('description', '自动生成的Coze插件')
            元数据.setdefault('version', '1.0.0')

            接口 = 标准化数据['interface']
            接口.setdefault('actions', [])
            接口.setdefault('responses', [])

            逻辑 = 标准化数据['logic']
            逻辑.setdefault('steps', [])

            return 标准化数据
        except Exception as e:
            logger.error(f"应用YAML标准失败: {e}")
            return 数据

    def YAML转JSON(self, yaml文本: str) -> Dict[str, Any]:
        \"\"\"将YAML文本转换为JSON格式\"\"\"
        return self.安全执行(
            lambda: self._YAML转JSON实现(yaml文本),
            默认值={},
            错误信息="YAML转JSON失败"
        )

    def _YAML转JSON实现(self, yaml文本: str) -> Dict[str, Any]:
        \"\"\"实际的YAML转JSON实现\"\"\"
        清理后yaml = self.清理YAML文本(yaml文本)

        json数据 = yaml.safe_load(清理后yaml)

        if json数据 is None:
            json数据 = {}

        if not isinstance(json数据, dict):
            raise ValueError("YAML必须包含字典结构")

        标准化数据 = self.应用CozeJSON标准(json数据)

        self.记录日志('YAML解析', 'YAML转JSON', '成功解析YAML为JSON', None, '解析完成')
        return 标准化数据

    def 清理YAML文本(self, yaml文本: str) -> str:
        \"\"\"清理YAML文本\"\"\"
        文本 = yaml文本.replace('\\ufeff', '')
        文本 = 文本.replace('\\r\\n', '\\n').replace('\\r', '\\n')

        行列表 = []
        for 行 in 文本.split('\\n'):
            行 = 行.rstrip()
            行 = 行.replace('\\t', '  ')

            if ': ' not in 行 and 行.endswith(':') and not 行.startswith(' '):
                行 = 行 + ' '

            行列表.append(行)

        return '\\n'.join(行列表)

    def 应用CozeJSON标准(self, 数据: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"应用Coze JSON标准\"\"\"
        标准化数据 = copy.deepcopy(数据)

        必需字段 = ['metadata', 'interface', 'logic']
        for 字段 in 必需字段:
            if 字段 not in 标准化数据:
                标准化数据[字段] = {}

        元数据 = 标准化数据['metadata']
        元数据.setdefault('name', '未命名插件')
        元数据.setdefault('description', '自动生成的Coze插件')
        元数据.setdefault('version', '1.0.0')

        接口 = 标准化数据['interface']
        接口.setdefault('actions', [])
        接口.setdefault('responses', [])

        逻辑 = 标准化数据['logic']
        逻辑.setdefault('steps', [])

        return 标准化数据

    # ==================== TXT 转 JSON ====================
    def TXT转JSON(self, txt文本: str) -> Dict[str, Any]:
        \"\"\"将TXT文本转换为JSON格式\"\"\"
        return self.安全执行(
            lambda: self._TXT转JSON实现(txt文本),
            默认值={},
            错误信息="TXT转JSON失败"
        )

    def _TXT转JSON实现(self, txt文本: str) -> Dict[str, Any]:
        \"\"\"实际的TXT转JSON实现\"\"\"
        清理后文本 = self._清理TXT文本(txt文本)

        try:
            return json.loads(清理后文本)
        except:
            pass

        try:
            return yaml.safe_load(清理后文本)
        except:
            pass

        if self._是键值对格式(清理后文本):
            return self._解析键值对TXT(清理后文本)
        elif self._是配置格式(清理后文本):
            return self._解析配置TXT(清理后文本)
        elif self._是结构化文本(清理后文本):
            return self._解析结构化TXT(清理后文本)
        else:
            return self._解析通用TXT(清理后文本)

    def _清理TXT文本(self, txt文本: str) -> str:
        \"\"\"清理TXT文本\"\"\"
        文本 = txt文本.replace('\\ufeff', '')
        文本 = 文本.replace('\\r\\n', '\\n').replace('\\r', '\\n')
        文本 = re.sub(r'\\n\\s*\\n', '\\n\\n', 文本)
        return 文本.strip()

    def _是键值对格式(self, 文本: str) -> bool:
        \"\"\"检查是否为键值对格式\"\"\"
        行列表 = 文本.split('\\n')
        键值对数量 = 0
        for 行 in 行列表:
            行 = 行.strip()
            if 行 and ':' in 行 and not 行.startswith('#'):
                键值对数量 += 1
        return 键值对数量 > len(行列表) * 0.5

    def _是配置格式(self, 文本: str) -> bool:
        \"\"\"检查是否为配置文件格式\"\"\"
        return any(标记 in 文本 for 标记 in ['[', ']', '=', '# 配置', ';'])

    def _是结构化文本(self, 文本: str) -> bool:
        \"\"\"检查是否为结构化文本\"\"\"
        行列表 = 文本.split('\\n')
        节数量 = sum(1 for 行 in 行列表 if 行.strip().startswith('[') and 行.strip().endswith(']'))
        return 节数量 > 0

    def _解析键值对TXT(self, 文本: str) -> Dict[str, Any]:
        \"\"\"解析键值对格式的TXT\"\"\"
        结果 = {}
        当前节 = 结果

        for 行 in 文本.split('\\n'):
            行 = 行.strip()
            if not 行 or 行.startswith('#'):
                continue

            if 行.startswith('[') and 行.endswith(']'):
                节名 = 行[1:-1].strip()
                结果[节名] = {}
                当前节 = 结果[节名]
                continue

            if ':' in 行:
                键, 值 = 行.split(':', 1)
                键 = 键.strip()
                值 = 值.strip()

                转换值 = self._推断值类型(值)
                当前节[键] = 转换值

        return 结果

    def _解析配置TXT(self, 文本: str) -> Dict[str, Any]:
        \"\"\"解析配置文件格式的TXT\"\"\"
        结果 = {}
        当前节 = 结果

        for 行 in 文本.split('\\n'):
            行 = 行.strip()
            if not 行 or 行.startswith(('#', ';')):
                continue

            if 行.startswith('[') and 行.endswith(']'):
                节名 = 行[1:-1].strip()
                结果[节名] = {}
                当前节 = 结果[节名]
                continue

            if '=' in 行:
                键, 值 = 行.split('=', 1)
                键 = 键.strip()
                值 = 值.strip()

                值 = 值.split('#')[0].split(';')[0].strip()

                转换值 = self._推断值类型(值)
                当前节[键] = 转换值

        return 结果

    def _解析结构化TXT(self, 文本: str) -> Dict[str, Any]:
        \"\"\"解析结构化文本\"\"\"
        结果 = {}
        当前节 = None

        for 行 in 文本.split('\\n'):
            行 = 行.strip()
            if not 行:
                continue

            if 行.endswith(':') and not 行.startswith(' '):
                节名 = 行[:-1].strip()
                结果[节名] = {}
                当前节 = 结果[节名]
                continue

            if 行.startswith('- '):
                if 当前节 is not None:
                    if 'items' not in 当前节:
                        当前节['items'] = []
                    当前节['items'].append(行[2:].strip())
                continue

            if ': ' in 行 and 当前节 is not None:
                键, 值 = 行.split(': ', 1)
                当前节[键.strip()] = self._推断值类型(值.strip())

        return 结果

    def _解析通用TXT(self, 文本: str) -> Dict[str, Any]:
        \"\"\"解析通用TXT格式\"\"\"
        行列表 = [行.strip() for 行 in 文本.split('\\n') if 行.strip()]

        if len(行列表) == 1:
            return {"content": 行列表[0]}
        else:
            return {
                "line_count": len(行列表),
                "lines": 行列表,
                "content": "\\n".join(行列表)
            }

    def _推断值类型(self, 值: str) -> Any:
        \"\"\"推断值的类型\"\"\"
        值 = 值.strip()

        if 值.lower() in ('true', 'yes', 'on'):
            return True
        if 值.lower() in ('false', 'no', 'off'):
            return False

        if 值.lower() in ('null', 'none', ''):
            return None

        try:
            if '.' in 值:
                return float(值)
            else:
                return int(值)
        except ValueError:
            pass

        if ',' in 值 and not 值.startswith('"') and not 值.startswith("'"):
            return [self._推断值类型(item.strip()) for item in 值.split(',')]

        if (值.startswith('"') and 值.endswith('"')) or (值.startswith("'") and 值.endswith("'")):
            return 值[1:-1]

        return 值

    # ==================== JSON 转 TXT ====================
    def JSON转TXT(self, json数据: Dict[str, Any]) -> str:
        \"\"\"将JSON数据转换为可读的TXT格式\"\"\"
        return self.安全执行(
            lambda: self._JSON转TXT实现(json数据),
            默认值="转换失败",
            错误信息="JSON转TXT失败"
        )

    def _JSON转TXT实现(self, json数据: Dict[str, Any]) -> str:
        \"\"\"实际的JSON转TXT实现\"\"\"
        if not json数据:
            return "空数据"

        if self._适合键值对格式(json数据):
            return self._生成键值对TXT(json数据)
        elif self._适合树状格式(json数据):
            return self._生成树状TXT(json数据)
        else:
            return self._生成结构化TXT(json数据)

    def _适合键值对格式(self, 数据: Dict[str, Any]) -> bool:
        \"\"\"检查是否适合键值对格式\"\"\"
        if not isinstance(数据, dict):
            return False

        简单值数量 = sum(1 for v in 数据.values()
                      if isinstance(v, (str, int, float, bool)) or v is None)
        return 简单值数量 > len(数据) * 0.7

    def _适合树状格式(self, 数据: Dict[str, Any]) -> bool:
        \"\"\"检查是否适合树状格式\"\"\"
        if not isinstance(数据, dict):
            return False

        嵌套数量 = sum(1 for v in 数据.values() if isinstance(v, (dict, list)))
        return 嵌套数量 > 0

    def _生成键值对TXT(self, 数据: Dict[str, Any], 缩进: str = "") -> str:
        \"\"\"生成键值对格式的TXT\"\"\"
        行列表 = []

        for 键, 值 in 数据.items():
            if isinstance(值, dict):
                行列表.append(f"{缩进}{键}:")
                行列表.append(self._生成键值对TXT(值, 缩进 + "  "))
            elif isinstance(值, list):
                行列表.append(f"{缩进}{键}:")
                for 项 in 值:
                    if isinstance(项, dict):
                        行列表.append(self._生成键值对TXT(项, 缩进 + "  "))
                    else:
                        行列表.append(f"{缩进}  - {self._格式化值(项)}")
            else:
                行列表.append(f"{缩进}{键}: {self._格式化值(值)}")

        return "\\n".join(行列表)

    def _生成树状TXT(self, 数据: Dict[str, Any], 前缀: str = "", 是最后: bool = True) -> str:
        \"\"\"生成树状格式的TXT\"\"\"
        行列表 = []
        键列表 = list(数据.keys())

        for i, 键 in enumerate(键列表):
            值 = 数据[键]
            是最后项 = i == len(键列表) - 1
            当前前缀 = "└── " if 是最后项 else "├── "
            子前缀 = "    " if 是最后项 else "│   "

            if isinstance(值, dict):
                行列表.append(f"{前缀}{当前前缀}{键}")
                行列表.append(self._生成树状TXT(值, 前缀 + 子前缀, 是最后项))
            elif isinstance(值, list):
                行列表.append(f"{前缀}{当前前缀}{键} [{len(值)}项]")
                for j, 项 in enumerate(值):
                    项是最后 = j == len(值) - 1
                    if isinstance(项, dict):
                        行列表.append(self._生成树状TXT(项, 前缀 + 子前缀, 项是最后))
                    else:
                        项前缀 = "└── " if 项是最后 else "├── "
                        行列表.append(f"{前缀}{子前缀}{项前缀}{self._格式化值(项)}")
            else:
                行列表.append(f"{前缀}{当前前缀}{键}: {self._格式化值(值)}")

        return "\\n".join(行列表)

    def _生成结构化TXT(self, 数据: Dict[str, Any], 层级: int = 0) -> str:
        \"\"\"生成结构化TXT\"\"\"
        行列表 = []
        缩进 = "  " * 层级

        for 键, 值 in 数据.items():
            if isinstance(值, dict):
                行列表.append(f"{缩进}{键}:")
                行列表.append(self._生成结构化TXT(值, 层级 + 1))
            elif isinstance(值, list):
                行列表.append(f"{缩进}{键}:")
                for 项 in 值:
                    if isinstance(项, dict):
                        行列表.append(self._生成结构化TXT(项, 层级 + 1))
                    else:
                        行列表.append(f"{缩进}  - {self._格式化值(项)}")
            else:
                行列表.append(f"{缩进}{键}: {self._格式化值(值)}")

        return "\\n".join(行列表)

    def _格式化值(self, 值: Any) -> str:
        \"\"\"格式化值用于TXT输出\"\"\"
        if 值 is None:
            return "null"
        elif isinstance(值, bool):
            return "true" if 值 else "false"
        elif isinstance(值, (int, float)):
            return str(值)
        elif isinstance(值, str):
            if '\\n' in 值:
                return f'\"\"\"\\n{值}\\n\"\"\"'
            elif any(字符 in 值 for 字符 in [' ', ':', '-', '#']):
                return f'"{值}"'
            else:
                return 值
        else:
            return str(值)

    # ==================== TXT 转 YAML ====================
    def TXT转YAML(self, txt文本: str) -> str:
        \"\"\"将TXT文本直接转换为YAML格式\"\"\"
        return self.安全执行(
            lambda: self._TXT转YAML实现(txt文本),
            默认值="转换失败",
            错误信息="TXT转YAML失败"
        )

    def _TXT转YAML实现(self, txt文本: str) -> str:
        \"\"\"实际的TXT转YAML实现\"\"\"
        json数据 = self.TXT转JSON(txt文本)
        yaml内容 = self.JSON转YAML(json数据)
        return yaml内容

    # ==================== YAML 转 TXT ====================
    def YAML转TXT(self, yaml文本: str) -> str:
        \"\"\"将YAML文本转换为可读的TXT格式\"\"\"
        return self.安全执行(
            lambda: self._YAML转TXT实现(yaml文本),
            默认值="转换失败",
            错误信息="YAML转TXT失败"
        )

    def _YAML转TXT实现(self, yaml文本: str) -> str:
        \"\"\"实际的YAML转TXT实现\"\"\"
        json数据 = self.YAML转JSON(yaml文本)
        txt内容 = self.JSON转TXT(json数据)
        return txt内容

    # ==================== 批量转换方法 ====================
    def 批量转换(self, 输入数据: Any, 源格式: str, 目标格式: str) -> Any:
        \"\"\"批量格式转换方法\"\"\"
        格式映射 = {
            ('txt', 'json'): self.TXT转JSON,
            ('txt', 'yaml'): self.TXT转YAML,
            ('json', 'txt'): self.JSON转TXT,
            ('json', 'yaml'): self.JSON转YAML,
            ('yaml', 'txt'): self.YAML转TXT,
            ('yaml', 'json'): self.YAML转JSON,
        }

        转换函数 = 格式映射.get((源格式.lower(), 目标格式.lower()))

        if not 转换函数:
            raise ValueError(f"不支持的转换: {源格式} -> {目标格式}")

        return 转换函数(输入数据)

    def 验证Coze兼容性(self, json数据: Dict[str, Any]) -> Tuple[bool, List[str]]:
        \"\"\"验证JSON数据是否符合Coze插件导入要求\"\"\"
        错误列表 = []
        警告列表 = []

        for 节点 in self.Coze必需节点:
            if 节点 not in json数据:
                错误列表.append(f"缺少必需节点: {节点}")

        if 'metadata' in json数据:
            metadata = json数据['metadata']
            if 'name' not in metadata:
                错误列表.append("metadata中缺少name字段")
            elif not isinstance(metadata['name'], str):
                错误列表.append("metadata.name必须是字符串")

            if 'description' not in metadata:
                警告列表.append("metadata中缺少description字段（建议添加）")
            elif not isinstance(metadata['description'], str):
                错误列表.append("metadata.description必须是字符串")

        if 'interface' in json数据:
            interface = json数据['interface']
            if 'actions' not in interface:
                错误列表.append("interface中缺少actions字段")
            elif not isinstance(interface['actions'], list):
                错误列表.append("interface.actions必须是数组")
            else:
                for i, action in enumerate(interface['actions']):
                    if not isinstance(action, dict):
                        错误列表.append(f"interface.actions[{i}]必须是对象")
                    elif 'name' not in action:
                        错误列表.append(f"interface.actions[{i}]缺少name字段")

        if 'logic' in json数据:
            logic = json数据['logic']
            if 'steps' not in logic:
                错误列表.append("logic中缺少steps字段")
            elif not isinstance(logic['steps'], list):
                错误列表.append("logic.steps必须是数组")
            else:
                步骤id列表 = []
                for i, 步骤 in enumerate(logic['steps']):
                    if not isinstance(步骤, dict):
                        错误列表.append(f"logic.steps[{i}]必须是对象")
                    elif 'id' not in 步骤:
                        错误列表.append(f"logic.steps[{i}]缺少id字段")
                    else:
                        步骤id = 步骤['id']
                        if 步骤id in 步骤id列表:
                            错误列表.append(f"logic.steps中存在重复ID: {步骤id}")
                        步骤id列表.append(步骤id)

        if 错误列表:
            self.记录日志('Coze兼容性验证', '验证结果', f'发现{len(错误列表)}个错误', None, 错误列表)
        if 警告列表:
            self.记录日志('Coze兼容性警告', '验证结果', f'发现{len(警告列表)}个警告', None, 警告列表)

        return len(错误列表) == 0, 错误列表 + 警告列表

    def 导出JSON文件(self, json数据: Dict[str, Any], 导出路径: str) -> bool:
        \"\"\"导出处理后的JSON文件\"\"\"
        return self.安全执行(
            lambda: self._导出JSON文件实现(json数据, 导出路径),
            默认值=False,
            错误信息=f"导出JSON文件失败 {导出路径}"
        )

    def _导出JSON文件实现(self, json数据: Dict[str, Any], 导出路径: str) -> bool:
        \"\"\"实际的导出实现\"\"\"
        if not 导出路径 or not 导出路径.strip():
            raise ValueError("导出路径不能为空")

        导出路径 = 导出路径.strip()
        if not 导出路径.endswith('.json'):
            导出路径 += '.json'

        导出目录 = os.path.dirname(导出路径)
        if 导出目录 and not os.path.exists(导出目录):
            os.makedirs(导出目录)

        if not os.access(导出目录 if 导出目录 else '.', os.W_OK):
            raise ValueError(f"没有写入权限: {导出目录}")

        with open(导出路径, 'w', encoding='utf-8') as 文件:
            json.dump(json数据, 文件, ensure_ascii=False, indent=2)

        self.记录日志('文件导出', 导出路径, '导出成功', None, f"文件大小: {os.path.getsize(导出路径)} 字节")
        return True

    def 导出YAML文件(self, yaml内容: str, 导出路径: str) -> bool:
        \"\"\"导出YAML文件\"\"\"
        return self.安全执行(
            lambda: self._导出YAML文件实现(yaml内容, 导出路径),
            默认值=False,
            错误信息=f"导出YAML文件失败 {导出路径}"
        )

    def _导出YAML文件实现(self, yaml内容: str, 导出路径: str) -> bool:
        \"\"\"实际的YAML导出实现\"\"\"
        if not 导出路径 or not 导出路径.strip():
            raise ValueError("导出路径不能为空")

        导出路径 = 导出路径.strip()
        if not 导出路径.endswith(('.yaml', '.yml')):
            导出路径 += '.yaml'

        导出目录 = os.path.dirname(导出路径)
        if 导出目录 and not os.path.exists(导出目录):
            os.makedirs(导出目录)

        if not os.access(导出目录 if 导出目录 else '.', os.W_OK):
            raise ValueError(f"没有写入权限: {导出目录}")

        with open(导出路径, 'w', encoding='utf-8') as 文件:
            文件.write(yaml内容)

        self.记录日志('YAML导出', 导出路径, '导出成功', None, f"文件大小: {os.path.getsize(导出路径)} 字节")
        return True

    def 导出TXT文件(self, txt内容: str, 导出路径: str) -> bool:
        \"\"\"导出TXT文件\"\"\"
        return self.安全执行(
            lambda: self._导出TXT文件实现(txt内容, 导出路径),
            默认值=False,
            错误信息=f"导出TXT文件失败 {导出路径}"
        )

    def _导出TXT文件实现(self, txt内容: str, 导出路径: str) -> bool:
        \"\"\"实际的TXT导出实现\"\"\"
        if not 导出路径 or not 导出路径.strip():
            raise ValueError("导出路径不能为空")

        导出路径 = 导出路径.strip()
        if not 导出路径.endswith('.txt'):
            导出路径 += '.txt'

        导出目录 = os.path.dirname(导出路径)
        if 导出目录 and not os.path.exists(导出目录):
            os.makedirs(导出目录)

        if not os.access(导出目录 if 导出目录 else '.', os.W_OK):
            raise ValueError(f"没有写入权限: {导出目录}")

        with open(导出路径, 'w', encoding='utf-8') as 文件:
            文件.write(txt内容)

        self.记录日志('TXT导出', 导出路径, '导出成功', None, f"文件大小: {os.path.getsize(导出路径)} 字节")
        return True

    def 清空日志(self):
        \"\"\"清空处理日志\"\"\"
        self.处理日志.clear()
        logger.info("处理日志已清空")

# 线程安全GUI类
class 线程安全GUI:
    \"\"\"提供线程安全的GUI操作方法\"\"\"

    def __init__(self, 主窗口):
        self.主窗口 = 主窗口
        self.队列 = queue.Queue()
        self.检查队列()

    def 检查队列(self):
        \"\"\"定期检查并执行队列中的GUI操作\"\"\"
        try:
            while True:
                任务 = self.队列.get_nowait()
                try:
                    任务()
                except Exception as e:
                    logger.error(f"GUI任务执行失败: {e}")
        except queue.Empty:
            pass
        self.主窗口.after(100, self.检查队列)

    def 安全调用(self, 函数, *参数, **关键字参数):
        \"\"\"安全地在主线程中调用GUI函数\"\"\"
        def 包装函数():
            try:
                函数(*参数, **关键字参数)
            except Exception as e:
                logger.error(f"GUI调用失败: {e}")

        self.队列.put(包装函数)

# Coze处理器图形界面
class CozeProcessorGUI:
    \"\"\"Coze处理器图形界面 - 完整稳定版本\"\"\"

    def __init__(self, 主窗口):
        try:
            self.主窗口 = 主窗口
            self.主窗口.title("Coze JSON/OpenAPI/TXT/YAML一站式处理工具 v3.0")
            self.主窗口.geometry("1200x800")

            try:
                if os.path.exists("icon.ico"):
                    self.主窗口.iconbitmap("icon.ico")
            except:
                pass

            self.处理器 = CozeJSONProcessor()
            self.当前数据 = None
            self.当前格式 = "json"
            self.线程安全器 = 线程安全GUI(主窗口)

            self.处理中 = False
            self.进度值 = tk.DoubleVar()
            self.进度值.set(0)

            self.初始化界面()
            self.状态标签.config(text="程序已就绪")

            self.主窗口.protocol("WM_DELETE_WINDOW", self.安全关闭)

            logger.info("GUI初始化完成")

        except Exception as e:
            logger.critical(f"GUI初始化失败: {e}")
            messagebox.showerror("启动错误", f"程序启动失败:\\n{str(e)}")
            sys.exit(1)

    def 安全关闭(self):
        \"\"\"安全关闭程序\"\"\"
        try:
            if self.处理中:
                if not messagebox.askyesno("确认关闭", "处理正在进行中，确定要退出吗？"):
                    return

            self.主窗口.quit()
            self.主窗口.destroy()
            sys.exit(0)
        except Exception as e:
            logger.error(f"关闭程序时出错: {e}")
            sys.exit(1)

    def 安全调用(self, 函数, *参数, **关键字参数):
        \"\"\"线程安全地调用GUI函数\"\"\"
        self.线程安全器.安全调用(函数, *参数, **关键字参数)

    def 初始化界面(self):
        \"\"\"初始化用户界面\"\"\"
        try:
            主框架 = ttk.Frame(self.主窗口, padding="10")
            主框架.pack(fill=tk.BOTH, expand=True)

            self.笔记本 = ttk.Notebook(主框架)
            self.笔记本.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            self.文件处理帧 = ttk.Frame(self.笔记本, padding="10")
            self.笔记本.add(self.文件处理帧, text="文件处理")

            self.文本处理帧 = ttk.Frame(self.笔记本, padding="10")
            self.笔记本.add(self.文本处理帧, text="文本处理")

            self.格式转换帧 = ttk.Frame(self.笔记本, padding="10")
            self.笔记本.add(self.格式转换帧, text="格式转换")

            self.初始化文件处理界面()
            self.初始化文本处理界面()
            self.初始化格式转换界面()

        except Exception as e:
            logger.error(f"界面初始化失败: {e}")
            raise

    def 初始化文件处理界面(self):
        \"\"\"初始化文件处理界面\"\"\"
        文件框架 = ttk.LabelFrame(self.文件处理帧, text="文件选择", padding="5")
        文件框架.pack(fill=tk.X, pady=5)

        列表框架 = ttk.Frame(文件框架)
        列表框架.pack(fill=tk.X, pady=5)

        self.文件列表框 = tk.Listbox(列表框架, height=8, selectmode=tk.EXTENDED)
        滚动条 = ttk.Scrollbar(列表框架, orient=tk.VERTICAL, command=self.文件列表框.yview)
        self.文件列表框.configure(yscrollcommand=滚动条.set)

        self.文件列表框.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        滚动条.pack(side=tk.RIGHT, fill=tk.Y)

        按钮框架 = ttk.Frame(文件框架)
        按钮框架.pack(fill=tk.X, pady=5)

        ttk.Button(按钮框架, text="添加JSON文件", command=self.添加JSON文件).pack(side=tk.LEFT, padx=2)
        ttk.Button(按钮框架, text="添加TXT文件", command=self.添加TXT文件).pack(side=tk.LEFT, padx=2)
        ttk.Button(按钮框架, text="添加YAML文件", command=self.添加YAML文件).pack(side=tk.LEFT, padx=2)
        ttk.Button(按钮框架, text="添加文件夹", command=self.添加文件夹).pack(side=tk.LEFT, padx=2)
        ttk.Button(按钮框架, text="清空列表", command=self.清空文件列表).pack(side=tk.LEFT, padx=2)
        ttk.Button(按钮框架, text="移除选中", command=self.移除选中文件).pack(side=tk.LEFT, padx=2)

        选项框架 = ttk.LabelFrame(self.文件处理帧, text="处理选项", padding="5")
        选项框架.pack(fill=tk.X, pady=5)

        self.自动修复Var = tk.BooleanVar(value=True)
        self.OpenAPI修复Var = tk.BooleanVar(value=True)
        self.生成日志Var = tk.BooleanVar(value=True)

        ttk.Checkbutton(选项框架, text="自动修复JSON格式错误", variable=self.自动修复Var).pack(anchor=tk.W)
        ttk.Checkbutton(选项框架, text="修复OpenAPI参数错误", variable=self.OpenAPI修复Var).pack(anchor=tk.W)
        ttk.Checkbutton(选项框架, text="生成详细处理日志", variable=self.生成日志Var).pack(anchor=tk.W)

        进度框架 = ttk.Frame(self.文件处理帧)
        进度框架.pack(fill=tk.X, pady=5)

        self.进度条 = ttk.Progressbar(进度框架, mode='determinate', variable=self.进度值)
        self.进度条.pack(fill=tk.X, pady=2)

        self.状态标签 = ttk.Label(进度框架, text="就绪")
        self.状态标签.pack(anchor=tk.W)

        操作框架 = ttk.Frame(self.文件处理帧)
        操作框架.pack(fill=tk.X, pady=10)

        ttk.Button(操作框架, text="开始处理", command=self.开始处理).pack(side=tk.LEFT, padx=5)
        ttk.Button(操作框架, text="导出JSON", command=lambda: self.导出结果("json")).pack(side=tk.LEFT, padx=5)
        ttk.Button(操作框架, text="导出YAML", command=lambda: self.导出结果("yaml")).pack(side=tk.LEFT, padx=5)
        ttk.Button(操作框架, text="导出TXT", command=lambda: self.导出结果("txt")).pack(side=tk.LEFT, padx=5)
        ttk.Button(操作框架, text="查看日志", command=self.查看日志).pack(side=tk.LEFT, padx=5)

        结果框架 = ttk.LabelFrame(self.文件处理帧, text="处理结果", padding="5")
        结果框架.pack(fill=tk.BOTH, expand=True, pady=5)

        self.结果文本框 = scrolledtext.ScrolledText(结果框架, wrap=tk.WORD)
        self.结果文本框.pack(fill=tk.BOTH, expand=True)

        self.文件列表框.bind('<Double-Button-1>', self.预览文件)

    def 初始化文本处理界面(self):
        \"\"\"初始化文本处理界面\"\"\"
        输入框架 = ttk.LabelFrame(self.文本处理帧, text="文本输入", padding="5")
        输入框架.pack(fill=tk.BOTH, expand=True, pady=5)

        self.文本输入框 = scrolledtext.ScrolledText(输入框架, wrap=tk.WORD)
        self.文本输入框.pack(fill=tk.BOTH, expand=True, pady=5)

        操作框架 = ttk.Frame(self.文本处理帧)
        操作框架.pack(fill=tk.X, pady=5)

        ttk.Button(操作框架, text="验证格式", command=self.验证格式).pack(side=tk.LEFT, padx=2)
        ttk.Button(操作框架, text="提取JSON片段", command=self.提取JSON片段).pack(side=tk.LEFT, padx=2)
        ttk.Button(操作框架, text="清空文本", command=self.清空文本).pack(side=tk.LEFT, padx=2)

    def 初始化格式转换界面(self):
        \"\"\"初始化格式转换界面\"\"\"
        转换框架 = ttk.LabelFrame(self.格式转换帧, text="格式转换", padding="5")
        转换框架.pack(fill=tk.BOTH, expand=True, pady=5)

        按钮框架 = ttk.Frame(转换框架)
        按钮框架.pack(fill=tk.X, pady=10)

        ttk.Button(按钮框架, text="TXT → JSON", command=self.TXT转JSON操作).pack(side=tk.LEFT, padx=2)
        ttk.Button(按钮框架, text="TXT → YAML", command=self.TXT转YAML操作).pack(side=tk.LEFT, padx=2)
        ttk.Button(按钮框架, text="JSON → TXT", command=self.JSON转TXT操作).pack(side=tk.LEFT, padx=2)
        ttk.Button(按钮框架, text="JSON → YAML", command=self.JSON转YAML操作).pack(side=tk.LEFT, padx=2)
        ttk.Button(按钮框架, text="YAML → TXT", command=self.YAML转TXT操作).pack(side=tk.LEFT, padx=2)
        ttk.Button(按钮框架, text="YAML → JSON", command=self.YAML转JSON操作).pack(side=tk.LEFT, padx=2)

        说明框架 = ttk.LabelFrame(转换框架, text="使用说明", padding="5")
        说明框架.pack(fill=tk.BOTH, expand=True, pady=5)

        说明文本 = \"\"\"
格式转换说明：

1. TXT → JSON：将文本格式转换为JSON结构
   - 支持键值对格式：name: value
   - 支持配置格式：[section] key=value
   - 支持结构化文本

2. TXT → YAML：将文本格式转换为YAML格式
   - 先转换为JSON，再转为YAML

3. JSON → TXT：将JSON转换为可读文本
   - 生成结构化文本格式
   - 支持树状显示和键值对显示

4. JSON → YAML：JSON转YAML格式
   - 符合Coze官方标准

5. YAML → TXT：YAML转可读文本
   - 生成易读的文本格式

6. YAML → JSON：YAML转JSON格式
   - 完整解析YAML结构
        \"\"\"

        说明文本框 = scrolledtext.ScrolledText(说明框架, wrap=tk.WORD, height=15)
        说明文本框.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        说明文本框.insert(tk.END, 说明文本)
        说明文本框.config(state=tk.DISABLED)

    def 添加JSON文件(self):
        \"\"\"添加JSON文件\"\"\"
        self.添加文件("JSON文件", "*.json")

    def 添加TXT文件(self):
        \"\"\"添加TXT文件\"\"\"
        self.添加文件("TXT文件", "*.txt")

    def 添加YAML文件(self):
        \"\"\"添加YAML文件\"\"\"
        self.添加文件("YAML文件", "*.yaml;*.yml")

    def 添加文件(self, 文件类型: str, 扩展名: str):
        \"\"\"添加文件通用方法\"\"\"
        try:
            文件路径列表 = filedialog.askopenfilenames(
                title=f"选择{文件类型}",
                filetypes=[(文件类型, 扩展名), ("所有文件", "*.*")]
            )
            for 文件路径 in 文件路径列表:
                if 文件路径 not in self.文件列表框.get(0, tk.END):
                    self.文件列表框.insert(tk.END, 文件路径)
            self.安全调用(self.状态标签.config, text=f"已添加 {len(文件路径列表)} 个{文件类型}")
        except Exception as e:
            logger.error(f"添加文件失败: {e}")
            self.安全调用(lambda: messagebox.showerror("错误", f"添加文件失败: {e}"))

    def 添加文件夹(self):
        \"\"\"添加文件夹\"\"\"
        try:
            文件夹路径 = filedialog.askdirectory(title="选择文件夹")
            if 文件夹路径:
                文件数量 = 0
                for 扩展名 in ["*.json", "*.txt", "*.yaml", "*.yml"]:
                    for 文件路径 in Path(文件夹路径).rglob(扩展名):
                        if str(文件路径) not in self.文件列表框.get(0, tk.END):
                            self.文件列表框.insert(tk.END, str(文件路径))
                            文件数量 += 1
                self.安全调用(self.状态标签.config, text=f"已从文件夹添加 {文件数量} 个文件")
        except Exception as e:
            logger.error(f"添加文件夹失败: {e}")
            self.安全调用(lambda: messagebox.showerror("错误", f"添加文件夹失败: {e}"))

    def 清空文件列表(self):
        \"\"\"清空文件列表\"\"\"
        try:
            self.文件列表框.delete(0, tk.END)
            self.安全调用(self.状态标签.config, text="文件列表已清空")
        except Exception as e:
            logger.error(f"清空文件列表失败: {e}")

    def 移除选中文件(self):
        \"\"\"移除选中文件\"\"\"
        try:
            选中项 = self.文件列表框.curselection()
            for 索引 in reversed(选中项):
                self.文件列表框.delete(索引)
            self.安全调用(self.状态标签.config, text=f"已移除 {len(选中项)} 个文件")
        except Exception as e:
            logger.error(f"移除文件失败: {e}")

    def 预览文件(self, event):
        \"\"\"预览文件\"\"\"
        try:
            选中项 = self.文件列表框.curselection()
            if 选中项:
                文件路径 = self.文件列表框.get(选中项[0])
                编码 = self.处理器.检测文件编码(文件路径)
                with open(文件路径, 'r', encoding=编码) as 文件:
                    内容 = 文件.read()
                self.文本输入框.delete(1.0, tk.END)
                self.文本输入框.insert(1.0, 内容)
                self.安全调用(self.状态标签.config, text=f"已预览: {os.path.basename(文件路径)}")
        except Exception as e:
            logger.error(f"预览文件失败: {e}")
            self.安全调用(lambda: messagebox.showerror("错误", f"预览文件失败: {e}"))

    def 开始处理(self):
        \"\"\"开始处理\"\"\"
        if self.处理中:
            self.安全调用(lambda: messagebox.showwarning("警告", "处理正在进行中"))
            return

        文件列表 = self.文件列表框.get(0, tk.END)
        if not 文件列表:
            self.安全调用(lambda: messagebox.showwarning("警告", "请先添加文件"))
            return

        self.处理中 = True
        self.进度值.set(0)
        self.安全调用(self.状态标签.config, text="开始处理...")

        线程 = threading.Thread(target=self.执行处理, daemon=True)
        线程.start()

    def 执行处理(self):
        \"\"\"执行处理\"\"\"
        try:
            文件路径列表 = self.文件列表框.get(0, tk.END)
            json数据列表 = []

            for i, 文件路径 in enumerate(文件路径列表):
                if not self.处理中:
                    break

                self.安全调用(self.进度值.set, (i / len(文件路径列表)) * 100)
                self.安全调用(self.状态标签.config, text=f"处理文件 {i+1}/{len(文件路径列表)}")

                try:
                    if 文件路径.endswith('.json'):
                        json数据 = self.处理器.读取JSON文件(文件路径)
                    elif 文件路径.endswith(('.yaml', '.yml')):
                        with open(文件路径, 'r', encoding='utf-8') as 文件:
                            yaml内容 = 文件.read()
                        json数据 = self.处理器.YAML转JSON(yaml内容)
                    elif 文件路径.endswith('.txt'):
                        with open(文件路径, 'r', encoding='utf-8') as 文件:
                            txt内容 = 文件.read()
                        json数据 = self.处理器.TXT转JSON(txt内容)
                    else:
                        json数据 = self.处理器.读取JSON文件(文件路径)

                    if self.OpenAPI修复Var.get() and ('openapi' in json数据 or 'swagger' in json数据):
                        json数据 = self.处理器.修复OpenAPI参数错误(json数据)
                    json数据列表.append(json数据)
                except Exception as e:
                    logger.error(f"处理文件失败 {文件路径}: {e}")

            if json数据列表 and self.处理中:
                self.安全调用(self.状态标签.config, text="正在合并数据...")
                合并结果 = self.处理器.合并多个JSON文件(json数据列表)

                self.安全调用(self.状态标签.config, text="正在验证兼容性...")
                验证通过, 错误列表 = self.处理器.验证Coze兼容性(合并结果)

                self.当前数据 = 合并结果
                self.当前格式 = "json"

                if 验证通过:
                    self.安全调用(self.状态标签.config, text="处理完成")
                    self.安全调用(self.显示结果, json.dumps(合并结果, ensure_ascii=False, indent=2))
                else:
                    self.安全调用(self.状态标签.config, text="验证失败")
                    结果文本 = f"发现 {len(错误列表)} 个问题:\\n\\n" + "\\n".join([f"• {错误}" for 错误 in 错误列表])
                    self.安全调用(self.显示结果, 结果文本)

            self.安全调用(self.进度值.set, 100)

        except Exception as e:
            logger.error(f"处理过程出错: {e}")
            self.安全调用(lambda: messagebox.showerror("错误", f"处理失败: {e}"))
        finally:
            self.处理中 = False

    def 显示结果(self, 结果文本: str):
        \"\"\"显示结果\"\"\"
        try:
            self.结果文本框.delete(1.0, tk.END)
            self.结果文本框.insert(1.0, 结果文本)
        except Exception as e:
            logger.error(f"显示结果失败: {e}")

    # 格式转换操作方法（简要实现）
    def TXT转JSON操作(self):
        try:
            文本内容 = self.文本输入框.get(1.0, tk.END).strip()
            if not 文本内容:
                messagebox.showwarning("警告", "请输入TXT文本")
                return
            json数据 = self.处理器.TXT转JSON(文本内容)
            self.文本输入框.delete(1.0, tk.END)
            self.文本输入框.insert(1.0, json.dumps(json数据, ensure_ascii=False, indent=2))
            self.安全调用(self.状态标签.config, text="TXT转JSON完成")
        except Exception as e:
            logger.error(f"TXT转JSON失败: {e}")
            messagebox.showerror("错误", f"转换失败: {e}")

    def TXT转YAML操作(self):
        try:
            文本内容 = self.文本输入框.get(1.0, tk.END).strip()
            if not 文本内容:
                messagebox.showwarning("警告", "请输入TXT文本")
                return
            yaml内容 = self.处理器.TXT转YAML(文本内容)
            self.文本输入框.delete(1.0, tk.END)
            self.文本输入框.insert(1.0, yaml内容)
            self.安全调用(self.状态标签.config, text="TXT转YAML完成")
        except Exception as e:
            logger.error(f"TXT转YAML失败: {e}")
            messagebox.showerror("错误", f"转换失败: {e}")

    def JSON转TXT操作(self):
        try:
            文本内容 = self.文本输入框.get(1.0, tk.END).strip()
            if not 文本内容:
                messagebox.showwarning("警告", "请输入JSON文本")
                return
            try:
                json数据 = json.loads(文本内容)
            except:
                messagebox.showerror("错误", "请输入有效的JSON文本")
                return
            txt内容 = self.处理器.JSON转TXT(json数据)
            self.文本输入框.delete(1.0, tk.END)
            self.文本输入框.insert(1.0, txt内容)
            self.安全调用(self.状态标签.config, text="JSON转TXT完成")
        except Exception as e:
            logger.error(f"JSON转TXT失败: {e}")
            messagebox.showerror("错误", f"转换失败: {e}")

    def JSON转YAML操作(self):
        try:
            文本内容 = self.文本输入框.get(1.0, tk.END).strip()
            if not 文本内容:
                messagebox.showwarning("警告", "请输入JSON文本")
                return
            try:
                json数据 = json.loads(文本内容)
            except:
                messagebox.showerror("错误", "请输入有效的JSON文本")
                return
            yaml内容 = self.处理器.JSON转YAML(json数据)
            self.文本输入框.delete(1.0, tk.END)
            self.文本输入框.insert(1.0, yaml内容)
            self.安全调用(self.状态标签.config, text="JSON转YAML完成")
        except Exception as e:
            logger.error(f"JSON转YAML失败: {e}")
            messagebox.showerror("错误", f"转换失败: {e}")

    def YAML转TXT操作(self):
        try:
            文本内容 = self.文本输入框.get(1.0, tk.END).strip()
            if not 文本内容:
                messagebox.showwarning("警告", "请输入YAML文本")
                return
            txt内容 = self.处理器.YAML转TXT(文本内容)
            self.文本输入框.delete(1.0, tk.END)
            self.文本输入框.insert(1.0, txt内容)
            self.安全调用(self.状态标签.config, text="YAML转TXT完成")
        except Exception as e:
            logger.error(f"YAML转TXT失败: {e}")
            messagebox.showerror("错误", f"转换失败: {e}")

    def YAML转JSON操作(self):
        try:
            文本内容 = self.文本输入框.get(1.0, tk.END).strip()
            if not 文本内容:
                messagebox.showwarning("警告", "请输入YAML文本")
                return
            json数据 = self.处理器.YAML转JSON(文本内容)
            self.文本输入框.delete(1.0, tk.END)
            self.文本输入框.insert(1.0, json.dumps(json数据, ensure_ascii=False, indent=2))
            self.安全调用(self.状态标签.config, text="YAML转JSON完成")
        except Exception as e:
            logger.error(f"YAML转JSON失败: {e}")
            messagebox.showerror("错误", f"转换失败: {e}")

    def 验证格式(self):
        try:
            文本内容 = self.文本输入框.get(1.0, tk.END).strip()
            if not 文本内容:
                messagebox.showwarning("警告", "请输入要验证的文本")
                return
            json数据 = None
            try:
                json数据 = json.loads(文本内容)
            except:
                try:
                    json数据 = yaml.safe_load(文本内容)
                except:
                    try:
                        json数据 = self.处理器.TXT转JSON(文本内容)
                    except:
                        messagebox.showerror("错误", "无法识别文本格式")
                        return
            if json数据 is not None:
                验证通过, 问题列表 = self.处理器.验证Coze兼容性(json数据)
                if 验证通过:
                    messagebox.showinfo("验证结果", "✅ 数据符合Coze导入标准！")
                else:
                    问题文本 = "\\n".join([f"• {问题}" for 问题 in 问题列表])
                    messagebox.showwarning("验证结果", f"❌ 发现 {len(问题列表)} 个问题：\\n\\n{问题文本}")
            else:
                messagebox.showerror("错误", "无法解析文本")
        except Exception as e:
            logger.error(f"验证格式失败: {e}")
            messagebox.showerror("错误", f"验证失败: {e}")

    def 提取JSON片段(self):
        try:
            文本内容 = self.文本输入框.get(1.0, tk.END).strip()
            if not 文本内容:
                messagebox.showwarning("警告", "请输入包含JSON片段的文本")
                return
            json片段列表 = re.findall(r'\\{[^{}]*\\{[^{}]*\\}[^{}]*\\}|\\{[^{}]*\\}', 文本内容, re.DOTALL)
            if not json片段列表:
                messagebox.showinfo("信息", "未找到JSON片段")
                return
            结果文本 = f"找到 {len(json片段列表)} 个JSON片段:\\n\\n"
            for i, 片段 in enumerate(json片段列表, 1):
                结果文本 += f"片段 {i}:\\n{片段}\\n{'-'*50}\\n"
            self.文本输入框.delete(1.0, tk.END)
            self.文本输入框.insert(1.0, 结果文本)
            self.安全调用(self.状态标签.config, text=f"提取到 {len(json片段列表)} 个JSON片段")
        except Exception as e:
            logger.error(f"提取JSON片段失败: {e}")
            messagebox.showerror("错误", f"提取失败: {e}")

    def 清空文本(self):
        try:
            self.文本输入框.delete(1.0, tk.END)
        except Exception as e:
            logger.error(f"清空文本失败: {e}")

    def 导出结果(self, 格式: str):
        if not self.当前数据:
            messagebox.showwarning("警告", "没有可导出的数据")
            return
        try:
            文件路径 = filedialog.asksaveasfilename(
                title=f"导出{格式.upper()}文件",
                defaultextension=f".{格式}",
                filetypes=[(f"{格式.upper()}文件", f"*.{格式}")]
            )
            if 文件路径:
                if 格式 == "json":
                    self.处理器.导出JSON文件(self.当前数据, 文件路径)
                elif 格式 == "yaml":
                    yaml内容 = self.处理器.JSON转YAML(self.当前数据)
                    self.处理器.导出YAML文件(yaml内容, 文件路径)
                elif 格式 == "txt":
                    txt内容 = self.处理器.JSON转TXT(self.当前数据)
                    self.处理器.导出TXT文件(txt内容, 文件路径)
                messagebox.showinfo("成功", f"文件已导出到:\\n{文件路径}")
                self.安全调用(self.状态标签.config, text=f"已导出: {os.path.basename(文件路径)}")
        except Exception as e:
            logger.error(f"导出失败: {e}")
            messagebox.showerror("错误", f"导出失败: {e}")

    def 查看日志(self):
        try:
            日志窗口 = tk.Toplevel(self.主窗口)
            日志窗口.title("处理日志")
            日志窗口.geometry("800x600")
            日志文本框 = scrolledtext.ScrolledText(日志窗口, wrap=tk.WORD)
            日志文本框.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            日志内容 = "处理日志:\\n\\n"
            for 日志条目 in self.处理器.处理日志:
                if 日志条目:
                    日志内容 += f"时间: {日志条目.get('时间戳', '未知')}\\n"
                    日志内容 += f"类型: {日志条目.get('类型', '未知')}\\n"
                    日志内容 += f"位置: {日志条目.get('位置', '未知')}\\n"
                    日志内容 += f"操作: {日志条目.get('修复方式', '未知')}\\n"
                    if 日志条目.get('修复前'):
                        日志内容 += f"修复前: {日志条目['修复前']}\\n"
                    if 日志条目.get('修复后'):
                        日志内容 += f"修复后: {日志条目['修复后']}\\n"
                    日志内容 += "-" * 50 + "\\n"
            日志文本框.insert(1.0, 日志内容)
            日志文本框.config(state=tk.DISABLED)
        except Exception as e:
            logger.error(f"查看日志失败: {e}")
            messagebox.showerror("错误", f"无法显示日志: {e}")

def 主函数():
    \"\"\"安全的主函数\"\"\"
    try:
        root = tk.Tk()
        if os.name == 'nt':
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        app = CozeProcessorGUI(root)
        root.mainloop()
    except Exception as e:
        logger.critical(f"程序运行失败: {e}")
        messagebox.showerror("致命错误", f"程序启动失败:\\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("启动Coze JSON/OpenAPI/TXT/YAML处理工具...")
    print("如果遇到问题，请查看 logs 目录下的日志文件")
    主函数()
"""
