# -*- coding: utf-8 -*-
"""
TXT文件自动化修复整合工具 - 最终增强版
功能：修复缺失内容、合并重复段落、检测完整性、去除所有重复内容
版本：v2.1 最终增强版
最后更新：2024年
"""

import os
import re
from collections import defaultdict, OrderedDict
from pathlib import Path
from difflib import SequenceMatcher
import hashlib

class AdvancedTXTRepairTool:
    def __init__(self, input_path):
        self.input_path = input_path
        self.output_path = os.path.splitext(input_path)[0] + "_cleaned.txt"
        self.report_path = os.path.splitext(input_path)[0] + "_report.txt"
        
        self.content_dict = defaultdict(list)
        self.missing_sections = []
        self.duplicate_records = []
        self.processing_stats = {
            'original_size': 0,
            'final_size': 0,
            'duplicates_removed': 0,
            'sections_fixed': 0
        }
        
        self.version_pattern = r'(全功能AI训练系统|全栈式AI工厂系统|版本)[\s\S]*?最后更新[:：]\s*\d{4}年?\d{1,2}月?'

    def _read_file(self):
        """安全读取文件内容"""
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(self.input_path, 'r', encoding='gbk') as f:
                    return f.read()
            except:
                with open(self.input_path, 'r', encoding='latin-1') as f:
                    return f.read()
        except Exception as e:
            print(f"文件读取失败: {str(e)}")
            return ""

    def remove_duplicate_lines(self, text):
        """移除重复行，保留首次出现"""
        lines = text.split('\n')
        seen = set()
        unique_lines = []
        duplicates_count = 0
        
        for line in lines:
            stripped = line.rstrip()
            if stripped and stripped not in seen:
                seen.add(stripped)
                unique_lines.append(line)
            elif stripped:
                duplicates_count += 1
                self.duplicate_records.append(f"重复行: {stripped[:50]}...")
        
        self.processing_stats['duplicates_removed'] += duplicates_count
        return '\n'.join(unique_lines)

    def remove_duplicate_paragraphs(self, text):
        """移除重复段落，保留首次出现"""
        paragraphs = re.split(r'\n\s*\n', text)
        seen = set()
        unique_paragraphs = []
        duplicates_count = 0
        
        for para in paragraphs:
            stripped = para.strip()
            if stripped and stripped not in seen:
                seen.add(stripped)
                unique_paragraphs.append(para)
            elif stripped:
                duplicates_count += 1
                self.duplicate_records.append(f"重复段落: {stripped[:100]}...")
        
        self.processing_stats['duplicates_removed'] += duplicates_count
        return '\n\n'.join(unique_paragraphs)

    def remove_similar_content(self, text, threshold=0.85):
        """移除相似段落，阈值控制相似度"""
        paragraphs = re.split(r'\n\s*\n', text)
        result = []
        duplicates_count = 0
        
        for para in paragraphs:
            stripped = para.strip()
            if not stripped:
                continue
                
            is_similar = False
            for saved in result:
                saved_stripped = saved.strip()
                if (SequenceMatcher(None, saved_stripped, stripped).ratio() >= threshold and 
                    abs(len(saved_stripped) - len(stripped)) / max(len(saved_stripped), len(stripped)) < 0.3):
                    is_similar = True
                    duplicates_count += 1
                    self.duplicate_records.append(f"相似内容: {stripped[:100]}...")
                    break
            
            if not is_similar:
                result.append(para)
        
        self.processing_stats['duplicates_removed'] += duplicates_count
        return '\n\n'.join(result)

    def remove_duplicate_versions(self, text):
        """智能移除重复版本块，保留最新版本"""
        blocks = re.split(r'\n{2,}', text)
        version_blocks = [b for b in blocks if re.search(self.version_pattern, b, re.IGNORECASE)]
        non_version_blocks = [b for b in blocks if b not in version_blocks]
        
        if not version_blocks:
            return text
        
        def parse_timestamp(block):
            patterns = [
                r'最后更新[:：]\s*(\d{4}年\d{1,2}月)',
                r'最后更新[:：]\s*(\d{4}-\d{1,2})',
                r'最后更新[:：]\s*(\d{4})',
                r'(\d{4}年\d{1,2}月)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, block)
                if match:
                    return match.group(1)
            return '2000年01月'
        
        version_blocks.sort(key=lambda x: parse_timestamp(x), reverse=True)
        
        seen = set()
        unique_versions = []
        duplicates_count = 0
        
        for block in version_blocks:
            content_hash = hash(re.sub(r'\s+', '', block))
            if content_hash not in seen:
                seen.add(content_hash)
                unique_versions.append(block)
            else:
                duplicates_count += 1
                self.duplicate_records.append(f"重复版本块: {block[:100]}...")
        
        self.processing_stats['duplicates_removed'] += duplicates_count
        return '\n\n'.join(unique_versions + non_version_blocks)

    def clean_code_duplicates(self, text):
        """清理代码重复（保留导入和注释）"""
        lines = text.splitlines()
        seen = set()
        imports = []
        comments = []
        logic_lines = []
        duplicates_count = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                imports.append(line)
            elif stripped.startswith('#') or '#' in line:
                comments.append(line)
            else:
                cleaned = re.sub(r'#.*$', '', stripped)
                if cleaned and cleaned not in seen:
                    seen.add(cleaned)
                    logic_lines.append(line)
                elif cleaned:
                    duplicates_count += 1
                    self.duplicate_records.append(f"重复代码: {cleaned[:50]}...")
        
        result = []
        if imports:
            result.extend(list(OrderedDict.fromkeys(imports)))
        if comments:
            result.extend(comments)
        if logic_lines:
            result.extend(logic_lines)
            
        self.processing_stats['duplicates_removed'] += duplicates_count
        return '\n'.join(result)

    def _detect_missing_sections(self, content):
        """检测缺失的内容章节（基于编号模式）"""
        lines = content.split('\n')
        section_pattern = re.compile(r'^(\d+(?:\.\d+)*)\.?\s+(.*)$')
        
        sections = []
        for line in lines:
            match = section_pattern.match(line.strip())
            if match:
                sections.append(match.groups())
        
        if len(sections) >= 2:
            current_num = sections[0][0].split('.')
            for i in range(1, len(sections)):
                next_num = sections[i][0].split('.')
                if len(current_num) == len(next_num):
                    expected = [str(int(current_num[j]) + 1) for j in range(len(current_num))]
                    if next_num != expected:
                        missing_num = '.'.join(expected)
                        self.missing_sections.append({
                            'missing_number': missing_num,
                            'before_section': sections[i-1][1][:30],
                            'after_section': sections[i][1][:30]
                        })
                        self.processing_stats['sections_fixed'] += 1
                current_num = next_num

    def _fix_document_structure(self, content):
        """修复文档结构"""
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'\n +', '\n', content)
        return content

    def _generate_report(self):
        """生成处理报告"""
        report = []
        report.append("=" * 50)
        report.append("TXT文件修复处理报告")
        report.append("=" * 50)
        report.append(f"处理文件: {self.input_path}")
        report.append(f"输出文件: {self.output_path}")
        report.append(f"原始大小: {self.processing_stats['original_size']} 字符")
        report.append(f"最终大小: {self.processing_stats['final_size']} 字符")
        
        reduction = ((self.processing_stats['original_size'] - self.processing_stats['final_size']) / 
                    self.processing_stats['original_size'] * 100) if self.processing_stats['original_size'] > 0 else 0
        
        report.append(f"去重率: {reduction:.2f}%")
        report.append(f"移除重复: {self.processing_stats['duplicates_removed']} 处")
        report.append(f"修复章节: {self.processing_stats['sections_fixed']} 处")
        
        if self.missing_sections:
            report.append("\n缺失章节检测:")
            for i, missing in enumerate(self.missing_sections[:3], 1):
                report.append(f"{i}. 缺失编号: {missing['missing_number']}")
                report.append(f"   前节: {missing['before_section']}...")
                report.append(f"   后节: {missing['after_section']}...")
        
        if self.duplicate_records:
            report.append(f"\n重复内容示例 (共{len(self.duplicate_records)}处):")
            for i, dup in enumerate(self.duplicate_records[:3], 1):
                report.append(f"{i}. {dup}")
        
        report.append("\n" + "=" * 50)
        return '\n'.join(report)

    def repair_process(self, mode='auto', threshold=0.85, keep_versions=True):
        """完整修复流程"""
        content = self._read_file()
        
        if not content:
            print("文件内容为空，修复终止")
            return False
        
        self.processing_stats['original_size'] = len(content)
        print(f"原始文件大小: {self.processing_stats['original_size']} 字符")
        
        print("1. 移除重复行...")
        content = self.remove_duplicate_lines(content)
        
        print("2. 移除重复段落...")
        content = self.remove_duplicate_paragraphs(content)
        
        if mode == 'similar' or mode == 'auto':
            print("3. 移除相似内容...")
            content = self.remove_similar_content(content, threshold)
        elif mode == 'code':
            print("3. 代码去重处理...")
            content = self.clean_code_duplicates(content)
        
        if keep_versions:
            print("4. 处理版本块重复...")
            content = self.remove_duplicate_versions(content)
        
        print("5. 检测缺失内容...")
        self._detect_missing_sections(content)
        
        print("6. 修复文档结构...")
        content = self._fix_document_structure(content)
        
        self.processing_stats['final_size'] = len(content)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        report_content = self._generate_report()
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        reduction = ((self.processing_stats['original_size'] - self.processing_stats['final_size']) / 
                    self.processing_stats['original_size'] * 100) if self.processing_stats['original_size'] > 0 else 0
        
        print(f"\n✅ 修复完成！")
        print(f"输出路径：{self.output_path}")
        print(f"报告文件：{self.report_path}")
        print(f"大小变化：{self.processing_stats['original_size']} → {self.processing_stats['final_size']} 字符")
        print(f"去重率：{reduction:.2f}%")
        print(f"检测到缺失部分：{len(self.missing_sections)} 处")
        print(f"合并重复项：{self.processing_stats['duplicates_removed']} 处")
        
        if self.missing_sections:
            print("\n缺失内容提示：")
            for missing in self.missing_sections[:3]:
                print(f"  - 缺失章节: {missing['missing_number']}")
        
        if self.duplicate_records and len(self.duplicate_records) <= 5:
            print("\n重复内容示例：")
            for dup in self.duplicate_records[:3]:
                print(f"  - {dup}")
        
        return True