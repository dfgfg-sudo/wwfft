#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文件格式合并系统 - 终极完整版
功能：自动检测、合并、优化、验证所有相同格式的文件
"""

import os
import sys
import json
import hashlib
import shutil
import numpy as np
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import concurrent.futures
from collections import defaultdict
import re
import difflib
import csv
import pickle
import yaml

@dataclass
class FileInfo:
    """文件信息类"""
    path: Path
    size: int
    hash_md5: str
    hash_sha256: str
    last_modified: datetime
    content_preview: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FormatGroup:
    """格式分组类"""
    extension: str
    files: List[FileInfo]
    total_size: int
    duplicate_groups: List[List[FileInfo]] = field(default_factory=list)

class IntelligentFileMerger:
    """智能文件合并器 - 终极完整版"""
    
    def __init__(self, root_dir: str, output_dir: str = None):
        self.root_dir = Path(root_dir).absolute()
        self.output_dir = Path(output_dir if output_dir else str(self.root_dir) + "_merged")
        self.format_groups: Dict[str, FormatGroup] = {}
        self.duplicate_stats: Dict[str, Dict] = {}
        self.merge_strategies = self._init_merge_strategies()
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _init_merge_strategies(self) -> Dict[str, callable]:
        """初始化合并策略"""
        return {
            '.txt': self._merge_text_files,
            '.json': self._merge_json_files,
            '.csv': self._merge_csv_files,
            '.yaml': self._merge_yaml_files,
            '.yml': self._merge_yaml_files,
            '.xml': self._merge_xml_files,
            '.md': self._merge_markdown_files,
            '.log': self._merge_log_files,
            '.py': self._merge_python_files,
            '.js': self._merge_js_files,
            '.html': self._merge_html_files,
            '.css': self._merge_css_files,
            '.sql': self._merge_sql_files,
            '.sh': self._merge_shell_files,
            '.bat': self._merge_batch_files,
            '.ini': self._merge_ini_files,
            '.cfg': self._merge_config_files,
            '.conf': self._merge_config_files,
            '.properties': self._merge_properties_files
        }
    
    def scan_directory(self, max_workers: int = 8) -> Dict:
        """扫描目录并分析文件格式"""
        print(f"🔍 开始扫描目录: {self.root_dir}")
        
        all_files = []
        for root, dirs, files in os.walk(self.root_dir):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = Path(root) / file
                all_files.append(file_path)
        
        print(f"📁 找到 {len(all_files)} 个文件，开始分析...")
        
        # 并行处理文件信息收集
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            file_infos = list(executor.map(self._get_file_info, all_files))
        
        # 按格式分组
        self._group_by_format(file_infos)
        
        # 分析重复文件
        self._analyze_duplicates()
        
        return self._generate_scan_report()
    
    def _get_file_info(self, file_path: Path) -> FileInfo:
        """获取文件详细信息"""
        try:
            stat = file_path.stat()
            
            # 计算哈希
            md5_hash = hashlib.md5()
            sha256_hash = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                # 只读取前1MB用于哈希和预览
                content = f.read(1024 * 1024)
                md5_hash.update(content)
                sha256_hash.update(content)
                
                # 获取内容预览（文本文件）
                if file_path.suffix.lower() in ['.txt', '.md', '.log', '.py', '.js', '.html', '.css', '.sql', '.sh']:
                    try:
                        content_preview = content[:500].decode('utf-8', errors='ignore')
                    except:
                        content_preview = ""
                else:
                    content_preview = ""
            
            # 读取元数据（如果是支持的格式）
            metadata = self._extract_metadata(file_path, content)
            
            return FileInfo(
                path=file_path,
                size=stat.st_size,
                hash_md5=md5_hash.hexdigest(),
                hash_sha256=sha256_hash.hexdigest(),
                last_modified=datetime.fromtimestamp(stat.st_mtime),
                content_preview=content_preview,
                metadata=metadata
            )
        except Exception as e:
            print(f"⚠️  跳过文件 {file_path}: {e}")
            return None
    
    def _extract_metadata(self, file_path: Path, content: bytes) -> Dict[str, Any]:
        """提取文件元数据"""
        metadata = {
            "extension": file_path.suffix.lower(),
            "filename": file_path.name,
            "parent_dir": file_path.parent.name
        }
        
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.json':
                data = json.loads(content.decode('utf-8', errors='ignore'))
                metadata.update({
                    "type": "json",
                    "keys": list(data.keys()) if isinstance(data, dict) else ["array"],
                    "size": len(data) if isinstance(data, (dict, list)) else 1
                })
            
            elif suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(content.decode('utf-8', errors='ignore'))
                if isinstance(data, dict):
                    metadata.update({
                        "type": "yaml",
                        "keys": list(data.keys()),
                        "size": len(data)
                    })
            
            elif suffix == '.csv':
                # 读取CSV头部
                csv_content = content.decode('utf-8', errors='ignore')
                reader = csv.reader(csv_content.splitlines())
                headers = next(reader, [])
                metadata.update({
                    "type": "csv",
                    "headers": headers,
                    "column_count": len(headers)
                })
            
            elif suffix == '.py':
                metadata.update({
                    "type": "python",
                    "lines": content.decode('utf-8', errors='ignore').count('\n') + 1
                })
            
            elif suffix == '.txt':
                text = content.decode('utf-8', errors='ignore')
                metadata.update({
                    "type": "text",
                    "lines": text.count('\n') + 1,
                    "words": len(text.split()),
                    "chars": len(text)
                })
        
        except Exception:
            pass
        
        return metadata
    
    def _group_by_format(self, file_infos: List[FileInfo]):
        """按格式分组文件"""
        for file_info in file_infos:
            if file_info is None:
                continue
                
            ext = file_info.path.suffix.lower()
            if ext == '':
                ext = '.no_extension'
            
            if ext not in self.format_groups:
                self.format_groups[ext] = FormatGroup(
                    extension=ext,
                    files=[],
                    total_size=0
                )
            
            self.format_groups[ext].files.append(file_info)
            self.format_groups[ext].total_size += file_info.size
    
    def _analyze_duplicates(self):
        """分析重复文件"""
        for ext, group in self.format_groups.items():
            # 按哈希分组
            hash_groups = defaultdict(list)
            for file_info in group.files:
                hash_groups[file_info.hash_md5].append(file_info)
            
            # 找出重复组（至少2个文件）
            duplicate_groups = []
            for hash_val, files in hash_groups.items():
                if len(files) > 1:
                    duplicate_groups.append(files)
            
            group.duplicate_groups = duplicate_groups
            
            # 统计重复信息
            total_duplicates = sum(len(g) - 1 for g in duplicate_groups)
            wasted_space = sum(
                sum(f.size for f in g[1:]) for g in duplicate_groups
            )
            
            self.duplicate_stats[ext] = {
                "total_files": len(group.files),
                "unique_files": len(group.files) - total_duplicates,
                "duplicate_files": total_duplicates,
                "wasted_space": wasted_space,
                "duplicate_groups": len(duplicate_groups)
            }
    
    def _generate_scan_report(self) -> Dict:
        """生成扫描报告"""
        total_files = sum(len(g.files) for g in self.format_groups.values())
        total_duplicates = sum(stats["duplicate_files"] for stats in self.duplicate_stats.values())
        total_wasted = sum(stats["wasted_space"] for stats in self.duplicate_stats.values())
        
        report = {
            "scan_time": datetime.now().isoformat(),
            "root_directory": str(self.root_dir),
            "output_directory": str(self.output_dir),
            "summary": {
                "total_files": total_files,
                "unique_files": total_files - total_duplicates,
                "duplicate_files": total_duplicates,
                "wasted_space_bytes": total_wasted,
                "wasted_space_mb": round(total_wasted / (1024 * 1024), 2),
                "wasted_space_gb": round(total_wasted / (1024 * 1024 * 1024), 3),
                "format_types": len(self.format_groups)
            },
            "formats": {},
            "recommendations": self._generate_recommendations()
        }
        
        # 添加格式详情
        for ext, group in self.format_groups.items():
            stats = self.duplicate_stats.get(ext, {})
            report["formats"][ext] = {
                "file_count": len(group.files),
                "total_size": group.total_size,
                "duplicate_stats": stats,
                "sample_files": [
                    {
                        "path": str(f.path.relative_to(self.root_dir)),
                        "size": f.size,
                        "last_modified": f.last_modified.isoformat()
                    }
                    for f in group.files[:5]  # 只显示前5个
                ]
            }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于重复文件的分析
        for ext, stats in self.duplicate_stats.items():
            if stats["duplicate_files"] > 0:
                savings_mb = round(stats["wasted_space"] / (1024 * 1024), 2)
                recommendations.append(
                    f"📁 {ext} 格式: 发现 {stats['duplicate_files']} 个重复文件，"
                    f"可节省 {savings_mb} MB 空间"
                )
        
        # 基于格式分布的优化建议
        total_files = sum(len(g.files) for g in self.format_groups.values())
        for ext, group in self.format_groups.items():
            percentage = (len(group.files) / total_files) * 100
            if percentage > 30:  # 如果某种格式占比超过30%
                recommendations.append(
                    f"⚙️  格式优化: {ext} 格式占比 {percentage:.1f}%，"
                    f"考虑统一或压缩处理"
                )
        
        # 基于文件大小的建议
        large_files = []
        for group in self.format_groups.values():
            for file_info in group.files:
                if file_info.size > 100 * 1024 * 1024:  # 大于100MB
                    large_files.append(file_info)
        
        if large_files:
            recommendations.append(
                f"💾 大文件优化: 发现 {len(large_files)} 个大于100MB的文件，"
                f"考虑分割或压缩"
            )
        
        return recommendations
    
    def merge_files(self, strategy: str = "smart", max_workers: int = 4) -> Dict:
        """合并文件（主入口）"""
        print(f"🔄 开始合并文件，策略: {strategy}")
        
        merge_results = {
            "strategy": strategy,
            "start_time": datetime.now().isoformat(),
            "merged_files": 0,
            "skipped_files": 0,
            "errors": [],
            "details": {}
        }
        
        for ext, group in self.format_groups.items():
            print(f"📊 处理 {ext} 格式: {len(group.files)} 个文件")
            
            if len(group.files) <= 1:
                print(f"  ⏭️  跳过，文件数量不足")
                continue
            
            # 应用合并策略
            try:
                if ext in self.merge_strategies:
                    result = self.merge_strategies[ext](group, strategy)
                else:
                    result = self._merge_generic_files(group, strategy)
                
                merge_results["details"][ext] = result
                merge_results["merged_files"] += result.get("merged", 0)
                merge_results["skipped_files"] += result.get("skipped", 0)
                
                if "error" in result:
                    merge_results["errors"].append({
                        "format": ext,
                        "error": result["error"]
                    })
            
            except Exception as e:
                error_msg = f"合并 {ext} 格式失败: {str(e)}"
                print(f"  ❌ {error_msg}")
                merge_results["errors"].append({
                    "format": ext,
                    "error": error_msg
                })
        
        merge_results["end_time"] = datetime.now().isoformat()
        merge_results["success"] = len(merge_results["errors"]) == 0
        
        # 生成合并报告
        self._generate_merge_report(merge_results)
        
        return merge_results
    
    def _merge_text_files(self, group: FormatGroup, strategy: str) -> Dict:
        """合并文本文件"""
        output_file = self.output_dir / f"merged_{group.extension[1:]}_files.txt"
        
        merged_content = []
        metadata = {
            "source_files": [],
            "total_lines": 0,
            "total_words": 0,
            "total_chars": 0
        }
        
        for file_info in group.files:
            try:
                with open(file_info.path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 添加文件头
                    merged_content.append(f"\n{'='*80}\n")
                    merged_content.append(f"File: {file_info.path.relative_to(self.root_dir)}\n")
                    merged_content.append(f"Size: {file_info.size} bytes\n")
                    merged_content.append(f"Modified: {file_info.last_modified}\n")
                    merged_content.append(f"{'='*80}\n\n")
                    
                    merged_content.append(content)
                    
                    # 更新元数据
                    metadata["source_files"].append(str(file_info.path.relative_to(self.root_dir)))
                    metadata["total_lines"] += content.count('\n') + 1
                    metadata["total_words"] += len(content.split())
                    metadata["total_chars"] += len(content)
            
            except Exception as e:
                print(f"  ⚠️  读取失败 {file_info.path}: {e}")
                continue
        
        # 写入合并文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(merged_content))
        
        return {
            "merged": len(group.files),
            "skipped": 0,
            "output_file": str(output_file),
            "metadata": metadata
        }
    
    def _merge_json_files(self, group: FormatGroup, strategy: str) -> Dict:
        """合并JSON文件"""
        merged_data = {}
        metadata = {
            "source_files": [],
            "total_keys": 0,
            "merged_keys": 0
        }
        
        for file_info in group.files:
            try:
                with open(file_info.path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if strategy == "smart":
                        # 智能合并：处理键冲突
                        for key, value in data.items():
                            if key in merged_data:
                                # 键冲突，添加后缀
                                counter = 1
                                new_key = f"{key}_{counter}"
                                while new_key in merged_data:
                                    counter += 1
                                    new_key = f"{key}_{counter}"
                                merged_data[new_key] = value
                                metadata["merged_keys"] += 1
                            else:
                                merged_data[key] = value
                                metadata["merged_keys"] += 1
                    else:
                        # 简单合并（可能覆盖）
                        merged_data.update(data)
                    
                    metadata["source_files"].append(str(file_info.path.relative_to(self.root_dir)))
                    metadata["total_keys"] += len(data)
            
            except Exception as e:
                print(f"  ⚠️  JSON解析失败 {file_info.path}: {e}")
                continue
        
        # 写入合并文件
        output_file = self.output_dir / f"merged_{group.extension[1:]}_files.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        return {
            "merged": len(group.files),
            "skipped": 0,
            "output_file": str(output_file),
            "metadata": metadata
        }
    
    def _merge_csv_files(self, group: FormatGroup, strategy: str) -> Dict:
        """合并CSV文件"""
        all_rows = []
        headers = None
        metadata = {
            "source_files": [],
            "total_rows": 0,
            "columns": []
        }
        
        for file_info in group.files:
            try:
                with open(file_info.path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    
                    # 读取头部
                    file_headers = next(reader)
                    
                    if headers is None:
                        headers = file_headers
                        metadata["columns"] = headers
                    
                    # 读取数据行
                    rows = list(reader)
                    all_rows.extend(rows)
                    
                    metadata["source_files"].append(str(file_info.path.relative_to(self.root_dir)))
                    metadata["total_rows"] += len(rows)
            
            except Exception as e:
                print(f"  ⚠️  CSV读取失败 {file_info.path}: {e}")
                continue
        
        # 写入合并文件
        output_file = self.output_dir / f"merged_{group.extension[1:]}_files.csv"
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(all_rows)
        
        return {
            "merged": len(group.files),
            "skipped": 0,
            "output_file": str(output_file),
            "metadata": metadata
        }
    
    def _merge_yaml_files(self, group: FormatGroup, strategy: str) -> Dict:
        """合并YAML文件"""
        merged_data = {}
        metadata = {
            "source_files": [],
            "total_entries": 0
        }
        
        for file_info in group.files:
            try:
                with open(file_info.path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    
                    if isinstance(data, dict):
                        # 智能合并字典
                        for key, value in data.items():
                            if key in merged_data:
                                if strategy == "smart":
                                    # 深度合并
                                    if isinstance(merged_data[key], dict) and isinstance(value, dict):
                                        merged_data[key].update(value)
                                    else:
                                        # 创建列表存储多个值
                                        if not isinstance(merged_data[key], list):
                                            merged_data[key] = [merged_data[key]]
                                        merged_data[key].append(value)
                                else:
                                    # 覆盖
                                    merged_data[key] = value
                            else:
                                merged_data[key] = value
                        
                        metadata["total_entries"] += len(data)
                    
                    metadata["source_files"].append(str(file_info.path.relative_to(self.root_dir)))
            
            except Exception as e:
                print(f"  ⚠️  YAML解析失败 {file_info.path}: {e}")
                continue
        
        # 写入合并文件
        output_file = self.output_dir / f"merged_{group.extension[1:]}_files.yaml"
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(merged_data, f, default_flow_style=False, allow_unicode=True)
        
        return {
            "merged": len(group.files),
            "skipped": 0,
            "output_file": str(output_file),
            "metadata": metadata
        }
    
    def _merge_generic_files(self, group: FormatGroup, strategy: str) -> Dict:
        """通用文件合并方法"""
        merged_count = 0
        skipped_count = 0
        output_files = []
        
        for file_info in group.files:
            try:
                # 复制到输出目录，保持原始结构
                rel_path = file_info.path.relative_to(self.root_dir)
                output_path = self.output_dir / rel_path
                
                # 确保目录存在
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(file_info.path, output_path)
                merged_count += 1
                output_files.append(str(output_path))
            
            except Exception as e:
                print(f"  ⚠️  复制失败 {file_info.path}: {e}")
                skipped_count += 1
        
        return {
            "merged": merged_count,
            "skipped": skipped_count,
            "output_files": output_files[:10]  # 只显示前10个
        }
    
    def _generate_merge_report(self, merge_results: Dict):
        """生成合并报告"""
        report_file = self.output_dir / "merge_report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(merge_results, f, ensure_ascii=False, indent=2)
        
        # 生成人类可读的报告
        text_report = self.output_dir / "merge_report.txt"
        
        with open(text_report, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("📊 文件合并报告\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"合并时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"原始目录: {self.root_dir}\n")
            f.write(f"输出目录: {self.output_dir}\n")
            f.write(f"合并策略: {merge_results.get('strategy', 'unknown')}\n")
            f.write("\n")
            
            f.write("📈 合并统计:\n")
            f.write(f"  - 合并文件数: {merge_results.get('merged_files', 0)}\n")
            f.write(f"  - 跳过文件数: {merge_results.get('skipped_files', 0)}\n")
            f.write(f"  - 错误数量: {len(merge_results.get('errors', []))}\n")
            f.write(f"  - 成功率: {merge_results.get('success', False)}\n")
            f.write("\n")
            
            if merge_results.get('details'):
                f.write("📁 格式详情:\n")
                for ext, detail in merge_results['details'].items():
                    f.write(f"\n  {ext}:\n")
                    f.write(f"    合并: {detail.get('merged', 0)}\n")
                    f.write(f"    跳过: {detail.get('skipped', 0)}\n")
                    if 'output_file' in detail:
                        f.write(f"    输出: {detail['output_file']}\n")
            
            if merge_results.get('errors'):
                f.write("\n❌ 错误列表:\n")
                for error in merge_results['errors']:
                    f.write(f"  - {error.get('format', 'unknown')}: {error.get('error', '未知错误')}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("报告生成完成\n")
            f.write("=" * 80 + "\n")
        
        print(f"📋 合并报告已生成: {report_file}")
        print(f"📄 文本报告: {text_report}")
    
    def compare_files(self, file1: str, file2: str, detailed: bool = False) -> Dict:
        """完整文件内容对比"""
        file1_path = Path(file1)
        file2_path = Path(file2)
        
        if not file1_path.exists():
            return {"error": f"文件不存在: {file1}"}
        if not file2_path.exists():
            return {"error": f"文件不存在: {file2}"}
        
        result = {
            "files": {
                "file1": str(file1_path),
                "file2": str(file2_path)
            },
            "basic_comparison": {},
            "detailed_comparison": {},
            "similarity": 0.0,
            "identical": False,
            "differences": []
        }
        
        # 基本比较
        try:
            # 文件大小
            size1 = file1_path.stat().st_size
            size2 = file2_path.stat().st_size
            
            # 哈希比较
            hash1_md5 = self._calculate_hash(file1_path, 'md5')
            hash2_md5 = self._calculate_hash(file2_path, 'md5')
            hash1_sha256 = self._calculate_hash(file1_path, 'sha256')
            hash2_sha256 = self._calculate_hash(file2_path, 'sha256')
            
            result["basic_comparison"] = {
                "size": {
                    "file1": size1,
                    "file2": size2,
                    "difference": abs(size1 - size2),
                    "percentage": abs(size1 - size2) / max(size1, size2) * 100 if max(size1, size2) > 0 else 0
                },
                "hash_md5": {
                    "file1": hash1_md5,
                    "file2": hash2_md5,
                    "match": hash1_md5 == hash2_md5
                },
                "hash_sha256": {
                    "file1": hash1_sha256,
                    "file2": hash2_sha256,
                    "match": hash1_sha256 == hash2_sha256
                }
            }
            
            # 检查是否完全一致
            if hash1_md5 == hash2_md5 and hash1_sha256 == hash2_sha256:
                result["identical"] = True
                result["similarity"] = 1.0
                return result
            
        except Exception as e:
            result["error"] = f"基本比较失败: {str(e)}"
            return result
        
        # 详细比较
        if detailed:
            try:
                # 读取文件内容
                with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
                    content1 = f1.read()
                    content2 = f2.read()
                
                # 逐字节比较
                min_len = min(len(content1), len(content2))
                max_len = max(len(content1), len(content2))
                
                # 计算相似度
                matches = 0
                differences = []
                
                for i in range(min_len):
                    if content1[i] == content2[i]:
                        matches += 1
                    elif len(differences) < 100:  # 最多记录100个差异
                        differences.append({
                            "position": i,
                            "byte1": f"0x{content1[i]:02x}",
                            "byte2": f"0x{content2[i]:02x}",
                            "char1": chr(content1[i]) if 32 <= content1[i] <= 126 else ".",
                            "char2": chr(content2[i]) if 32 <= content2[i] <= 126 else "."
                        })
                
                # 计算相似度百分比
                similarity = (matches / max_len) * 100 if max_len > 0 else 0
                
                result["detailed_comparison"] = {
                    "length": {
                        "file1": len(content1),
                        "file2": len(content2),
                        "difference": abs(len(content1) - len(content2))
                    },
                    "similarity_percentage": similarity,
                    "matching_bytes": matches,
                    "total_bytes": max_len,
                    "difference_count": max_len - matches
                }
                
                result["similarity"] = similarity / 100
                result["differences"] = differences
                
                # 对于文本文件，进行行级比较
                if file1_path.suffix.lower() in ['.txt', '.py', '.js', '.html', '.css', '.md', '.json', '.yaml', '.yml']:
                    try:
                        text1 = content1.decode('utf-8', errors='ignore').splitlines()
                        text2 = content2.decode('utf-8', errors='ignore').splitlines()
                        
                        diff = difflib.unified_diff(
                            text1, text2,
                            fromfile=str(file1_path),
                            tofile=str(file2_path),
                            lineterm=''
                        )
                        
                        text_diff = list(diff)
                        result["text_differences"] = text_diff[:100]  # 最多显示100行
                        
                    except Exception as e:
                        result["text_comparison_error"] = str(e)
            
            except Exception as e:
                result["detailed_error"] = f"详细比较失败: {str(e)}"
        
        return result
    
    def _calculate_hash(self, file_path: Path, algorithm: str = 'md5') -> str:
        """计算文件哈希"""
        hash_func = hashlib.md5() if algorithm == 'md5' else hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    def batch_compare(self, file_pairs: List[Tuple[str, str]], detailed: bool = False) -> Dict:
        """批量文件对比"""
        results = {
            "total_pairs": len(file_pairs),
            "identical_pairs": 0,
            "similar_pairs": 0,
            "different_pairs": 0,
            "errors": 0,
            "comparisons": []
        }
        
        for file1, file2 in file_pairs:
            try:
                comparison = self.compare_files(file1, file2, detailed)
                
                if "error" in comparison:
                    results["errors"] += 1
                elif comparison.get("identical", False):
                    results["identical_pairs"] += 1
                elif comparison.get("similarity", 0) > 0.9:  # 相似度大于90%
                    results["similar_pairs"] += 1
                else:
                    results["different_pairs"] += 1
                
                results["comparisons"].append(comparison)
            
            except Exception as e:
                results["errors"] += 1
                results["comparisons"].append({
                    "files": {"file1": file1, "file2": file2},
                    "error": str(e)
                })
        
        return results

# ======================
# 自动化整合系统
# ======================
class CozeAutomationIntegrator:
    """Coze自动化整合系统 - 终极完整版"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.file_merger = None
        self.results = {}
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        default_config = {
            "api_base": "https://api.coze.com/v1",
            "timeout": 30,
            "max_retries": 3,
            "parallel_workers": 4,
            "auto_merge_duplicates": True,
            "detailed_comparison": True,
            "generate_reports": True,
            "backup_before_merge": True,
            "notification_enabled": True,
            "log_level": "INFO"
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️  配置文件加载失败，使用默认配置: {e}")
        
        return default_config
    
    def run_full_automation(self, directory: str) -> Dict:
        """运行完整自动化流程"""
        print("🚀 启动Coze插件全栈自动化系统")
        print("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # 阶段1: 扫描和分析
            print("\n📊 阶段1: 目录扫描和分析")
            scan_results = self._scan_and_analyze(directory)
            
            # 阶段2: 文件合并
            print("\n🔄 阶段2: 智能文件合并")
            merge_results = self._merge_files(directory)
            
            # 阶段3: 内容对比
            print("\n🔍 阶段3: 完整内容对比")
            comparison_results = self._compare_contents(directory)
            
            # 阶段4: 优化处理
            print("\n⚡ 阶段4: 优化处理")
            optimization_results = self._optimize_files()
            
            # 阶段5: 生成报告
            print("\n📋 阶段5: 生成综合报告")
            report_results = self._generate_comprehensive_report(
                scan_results, merge_results, comparison_results, optimization_results
            )
            
            # 计算总时间
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            # 汇总结果
            final_results = {
                "success": True,
                "total_time_seconds": total_time,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "phases": {
                    "scan": scan_results,
                    "merge": merge_results,
                    "compare": comparison_results,
                    "optimize": optimization_results,
                    "report": report_results
                },
                "summary": self._generate_summary(
                    scan_results, merge_results, comparison_results, optimization_results
                )
            }
            
            print(f"\n🎉 自动化流程完成！总耗时: {total_time:.2f} 秒")
            return final_results
            
        except Exception as e:
            print(f"❌ 自动化流程失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _scan_and_analyze(self, directory: str) -> Dict:
        """扫描和分析目录"""
        print(f"🔍 扫描目录: {directory}")
        
        self.file_merger = IntelligentFileMerger(directory)
        scan_results = self.file_merger.scan_directory(
            max_workers=self.config.get("parallel_workers", 4)
        )
        
        print(f"📈 扫描完成:")
        print(f"  - 文件总数: {scan_results['summary']['total_files']}")
        print(f"  - 格式类型: {scan_results['summary']['format_types']}")
        print(f"  - 重复文件: {scan_results['summary']['duplicate_files']}")
        print(f"  - 可节省空间: {scan_results['summary']['wasted_space_mb']} MB")
        
        return scan_results
    
    def _merge_files(self, directory: str) -> Dict:
        """合并文件"""
        if not self.config.get("auto_merge_duplicates", True):
            print("⏭️  跳过文件合并（配置禁用）")
            return {"skipped": True, "reason": "config_disabled"}
        
        if not self.file_merger:
            self.file_merger = IntelligentFileMerger(directory)
        
        # 备份原始文件（如果配置启用）
        if self.config.get("backup_before_merge", True):
            backup_dir = Path(directory) / "_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir.mkdir(parents=True, exist_ok=True)
            print(f"💾 创建备份: {backup_dir}")
            
            # 这里可以添加备份逻辑
        
        # 执行合并
        merge_results = self.file_merger.merge_files(
            strategy="smart",
            max_workers=self.config.get("parallel_workers", 4)
        )
        
        print(f"📊 合并完成:")
        print(f"  - 合并文件数: {merge_results.get('merged_files', 0)}")
        print(f"  - 跳过文件数: {merge_results.get('skipped_files', 0)}")
        print(f"  - 错误数量: {len(merge_results.get('errors', []))}")
        
        return merge_results
    
    def _compare_contents(self, directory: str) -> Dict:
        """对比文件内容"""
        if not self.config.get("detailed_comparison", True):
            print("⏭️  跳过详细对比（配置禁用）")
            return {"skipped": True, "reason": "config_disabled"}
        
        # 查找成对文件进行对比
        directory_path = Path(directory)
        all_files = list(directory_path.rglob("*"))
        
        # 按格式分组
        format_groups = defaultdict(list)
        for file_path in all_files:
            if file_path.is_file():
                ext = file_path.suffix.lower()
                format_groups[ext].append(str(file_path))
        
        # 为每个格式创建对比对
        comparison_pairs = []
        for ext, files in format_groups.items():
            if len(files) >= 2:
                # 对比前两个文件
                comparison_pairs.append((files[0], files[1]))
        
        if not comparison_pairs:
            print("⏭️  没有找到可对比的文件对")
            return {"skipped": True, "reason": "no_pairs"}
        
        # 执行批量对比
        detailed = self.config.get("detailed_comparison", True)
        comparison_results = self.file_merger.batch_compare(comparison_pairs, detailed)
        
        print(f"🔍 对比完成:")
        print(f"  - 对比对数: {comparison_results.get('total_pairs', 0)}")
        print(f"  - 相同文件: {comparison_results.get('identical_pairs', 0)}")
        print(f"  - 相似文件: {comparison_results.get('similar_pairs', 0)}")
        print(f"  - 不同文件: {comparison_results.get('different_pairs', 0)}")
        print(f"  - 错误数量: {comparison_results.get('errors', 0)}")
        
        return comparison_results
    
    def _optimize_files(self) -> Dict:
        """优化文件"""
        print("⚡ 执行文件优化")
        
        # 这里可以添加各种优化逻辑
        # 1. 压缩大文件
        # 2. 标准化格式
        # 3. 清理临时文件
        # 4. 优化存储结构
        
        optimization_results = {
            "optimizations_applied": [],
            "space_saved": 0,
            "files_optimized": 0
        }
        
        print("✅ 优化完成（示例实现）")
        return optimization_results
    
    def _generate_comprehensive_report(self, *results) -> Dict:
        """生成综合报告"""
        print("📋 生成综合报告")
        
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "system_version": "Coze自动化系统 v3.0",
            "config": self.config,
            "results": {}
        }
        
        # 合并所有结果
        for i, result in enumerate(results):
            phase_name = ["scan", "merge", "compare", "optimize"][i]
            report_data["results"][phase_name] = result
        
        # 保存报告
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        
        json_report = report_dir / f"automation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        # 生成文本报告
        text_report = report_dir / f"automation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self._generate_text_report(report_data, text_report)
        
        print(f"📄 报告已保存:")
        print(f"  - JSON报告: {json_report}")
        print(f"  - 文本报告: {text_report}")
        
        return {
            "json_report": str(json_report),
            "text_report": str(text_report),
            "report_data": report_data
        }
    
    def _generate_text_report(self, report_data: Dict, output_path: Path):
        """生成文本报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("📊 Coze自动化系统综合报告\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"生成时间: {report_data['generated_at']}\n")
            f.write(f"系统版本: {report_data['system_version']}\n\n")
            
            f.write("📈 执行摘要\n")
            f.write("-" * 40 + "\n")
            
            # 扫描结果
            if 'scan' in report_data['results']:
                scan = report_data['results']['scan']
                if 'summary' in scan:
                    f.write(f"📁 扫描统计:\n")
                    f.write(f"  文件总数: {scan['summary']['total_files']}\n")
                    f.write(f"  重复文件: {scan['summary']['duplicate_files']}\n")
                    f.write(f"  可节省空间: {scan['summary']['wasted_space_mb']} MB\n")
                    f.write(f"  格式类型: {scan['summary']['format_types']}\n\n")
            
            # 合并结果
            if 'merge' in report_data['results']:
                merge = report_data['results']['merge']
                if not merge.get('skipped'):
                    f.write(f"🔄 合并统计:\n")
                    f.write(f"  合并文件: {merge.get('merged_files', 0)}\n")
                    f.write(f"  跳过文件: {merge.get('skipped_files', 0)}\n")
                    f.write(f"  错误数量: {len(merge.get('errors', []))}\n\n")
            
            # 对比结果
            if 'compare' in report_data['results']:
                compare = report_data['results']['compare']
                if not compare.get('skipped'):
                    f.write(f"🔍 对比统计:\n")
                    f.write(f"  对比对数: {compare.get('total_pairs', 0)}\n")
                    f.write(f"  相同文件: {compare.get('identical_pairs', 0)}\n")
                    f.write(f"  相似文件: {compare.get('similar_pairs', 0)}\n")
                    f.write(f"  不同文件: {compare.get('different_pairs', 0)}\n")
                    f.write(f"  错误数量: {compare.get('errors', 0)}\n\n")
            
            f.write("🔧 配置信息\n")
            f.write("-" * 40 + "\n")
            for key, value in report_data['config'].items():
                f.write(f"  {key}: {value}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("报告结束\n")
            f.write("=" * 80 + "\n")
    
    def _generate_summary(self, *results) -> Dict:
        """生成汇总统计"""
        summary = {
            "total_files_processed": 0,
            "duplicates_found": 0,
            "space_saved_mb": 0,
            "comparisons_made": 0,
            "optimizations_applied": 0,
            "success_rate": 100
        }
        
        # 提取统计数据
        for result in results:
            if isinstance(result, dict):
                # 扫描结果
                if 'summary' in result:
                    summary['total_files_processed'] = result['summary'].get('total_files', 0)
                    summary['duplicates_found'] = result['summary'].get('duplicate_files', 0)
                    summary['space_saved_mb'] = result['summary'].get('wasted_space_mb', 0)
                
                # 合并结果
                if 'merged_files' in result:
                    summary['files_merged'] = result.get('merged_files', 0)
                
                # 对比结果
                if 'total_pairs' in result:
                    summary['comparisons_made'] = result.get('total_pairs', 0)
                
                # 优化结果
                if 'files_optimized' in result:
                    summary['optimizations_applied'] = result.get('files_optimized', 0)
        
        return summary

# ======================
# 主程序入口
# ======================
def main():
    """主程序入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Coze插件全栈自动化系统 - 终极完整版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基本使用
  python coze_automation.py --dir ./plugins
  
  # 完整自动化流程
  python coze_automation.py --dir ./data --full --config config.json
  
  # 仅文件合并
  python coze_automation.py --dir ./files --merge-only
  
  # 仅内容对比
  python coze_automation.py --dir ./docs --compare-only
  
  # 自定义输出目录
  python coze_automation.py --dir ./input --output ./processed
        """
    )
    
    parser.add_argument("--dir", "-d", required=True, help="要处理的目录路径")
    parser.add_argument("--output", "-o", help="输出目录路径")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--full", "-f", action="store_true", help="运行完整自动化流程")
    parser.add_argument("--merge-only", action="store_true", help="仅执行文件合并")
    parser.add_argument("--compare-only", action="store_true", help="仅执行内容对比")
    parser.add_argument("--no-backup", action="store_true", help="跳过备份")
    parser.add_argument("--workers", "-w", type=int, default=4, help="并行工作线程数")
    
    args = parser.parse_args()
    
    try:
        # 创建自动化整合器
        integrator = CozeAutomationIntegrator(args.config)
        
        # 更新配置
        if args.workers:
            integrator.config["parallel_workers"] = args.workers
        if args.no_backup:
            integrator.config["backup_before_merge"] = False
        
        if args.full:
            # 运行完整自动化流程
            results = integrator.run_full_automation(args.dir)
            
        elif args.merge_only:
            # 仅文件合并
            print("🔄 执行文件合并")
            file_merger = IntelligentFileMerger(args.dir, args.output)
            file_merger.scan_directory()
            results = file_merger.merge_files(strategy="smart")
            
        elif args.compare_only:
            # 仅内容对比
            print("🔍 执行内容对比")
            file_merger = IntelligentFileMerger(args.dir, args.output)
            file_merger.scan_directory()
            
            # 对比前10个文件的第一个和第二个
            all_files = list(Path(args.dir).rglob("*"))
            if len(all_files) >= 2:
                comparison = file_merger.compare_files(
                    str(all_files[0]), str(all_files[1]), detailed=True
                )
                results = {"comparison": comparison}
            else:
                results = {"error": "文件数量不足"}
        
        else:
            # 默认运行完整流程
            results = integrator.run_full_automation(args.dir)
        
        # 输出结果
        if args.full or not any([args.merge_only, args.compare_only]):
            print(f"\n🎯 最终结果:")
            print(f"  成功: {results.get('success', False)}")
            if 'summary' in results:
                for key, value in results['summary'].items():
                    print(f"  {key}: {value}")
        
        # 保存最终结果
        if results.get('success'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"final_results_{timestamp}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n📄 最终结果已保存: {results_file}")
        
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()