"""
# -*- coding: utf-8 -*-
\"\"\"
批量去重处理脚本 - 安全版
功能：删除全部文件夹中的重复内容（行级+文件级）
作者：AI Assistant
日期：2026-07-16

import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict

# 配置
ROOT_DIR = r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd"
REPORT_FILE = os.path.join(ROOT_DIR, "去重处理报告_完整版.txt")
DUPLICATES_DIR = os.path.join(ROOT_DIR, "已删除的重复文件_备份")

# 要处理的文件类型
TEXT_EXTENSIONS = {'.txt', '.md', '.js', '.ts', '.json', '.yaml', '.yml', '.py'}

# 统计数据
stats = {
    'total_files': 0,
    'processed_files': 0,
    'duplicate_files': 0,
    'duplicate_lines_removed': 0,
    'bytes_saved': 0,
    'errors': [],
    'file_hashes': defaultdict(list),  # 文件哈希 -> 文件路径列表
    'line_duplicates': {}
}

def get_file_hash(filepath):
    \"\"\"计算文件哈希值\"\"\"
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        stats['errors'].append(f"计算哈希失败: {filepath} - {str(e)}")
        return None

def remove_duplicate_lines(filepath):
    \"\"\"去除文件内的重复行\"\"\"
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        original_count = len(lines)
        seen = set()
        unique_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            # 保留空行和特殊格式行
            if not line_stripped or line_stripped.startswith(('#', '//', '/*', '*', '```')):
                unique_lines.append(line)
            elif line_stripped not in seen:
                seen.add(line_stripped)
        
        duplicate_count = original_count - len(unique_lines)
        
        if duplicate_count > 0:
            with open(filepath, 'w', encoding='utf-8', newline='\\n') as f:
                f.writelines(unique_lines)
            stats['duplicate_lines_removed'] += duplicate_count
            return duplicate_count
        return 0
        stats['errors'].append(f"去重失败: {filepath} - {str(e)}")

def process_json_file(filepath):
    \"\"\"处理JSON文件，去除重复元素\"\"\"
            content = f.read()
        
        # 尝试修复常见JSON错误
        content = content.replace(',]', ']').replace(',}', '}')
        content = content.replace('\\"\\"', '\\"')
        
            data = json.loads(content)
        except:
        
        # 处理数组类型JSON
        if isinstance(data, list):
            original_count = len(data)
            unique_data = []
            for item in data:
                item_str = json.dumps(item, sort_keys=True, ensure_ascii=False)
                if item_str not in seen:
                    seen.add(item_str)
                    unique_data.append(item)
            
            if len(unique_data) < original_count:
                    json.dump(unique_data, f, ensure_ascii=False, indent=2)
                return original_count - len(unique_data)
        stats['errors'].append(f"JSON去重失败: {filepath} - {str(e)}")

def find_and_remove_duplicate_files():
    \"\"\"查找并删除完全相同的重复文件\"\"\"
    duplicates_found = 0
    
    # 按文件大小分组
    size_groups = defaultdict(list)
    for root, dirs, files in os.walk(ROOT_DIR):
        # 跳过备份目录和node_modules
        if '已删除的重复文件' in root or 'node_modules' in root:
            continue
        for file in files:
            filepath = os.path.join(root, file)
                size = os.path.getsize(filepath)
                size_groups[size].append(filepath)
    
    # 对相同大小的文件进行哈希比较
    for size, files in size_groups.items():
        if len(files) > 1:
            hashes = {}
            for filepath in files:
                file_hash = get_file_hash(filepath)
                if file_hash:
                    if file_hash in hashes:
                        # 发现重复文件
                        original = hashes[file_hash]
                        duplicate = filepath
                        
                        # 创建备份目录
                        os.makedirs(DUPLICATES_DIR, exist_ok=True)
                        
                        # 移动重复文件到备份目录
                            backup_name = f"{os.path.basename(duplicate)}_{hashlib.md5(duplicate.encode()).hexdigest()[:8]}"
                            backup_path = os.path.join(DUPLICATES_DIR, backup_name)
                            os.rename(duplicate, backup_path)
                            
                            stats['file_hashes'][file_hash].append(duplicate)
                            stats['bytes_saved'] += size
                            duplicates_found += 1
                            stats['errors'].append(f"移动重复文件失败: {duplicate} - {str(e)}")
                    else:
                        hashes[file_hash] = filepath
                        stats['file_hashes'][file_hash].append(filepath)
    
    return duplicates_found

def main():
    print("=" * 60)
    print("批量去重处理脚本 - 安全版")
    print(f"处理目录: {ROOT_DIR}")
    print()
    
    # 创建备份目录
    
    # 第一步：去除文件内重复行
    print("第一步：去除文件内的重复行...")
        # 跳过特殊目录
        if '已删除的重复文件' in root or 'node_modules' in root or '.git' in root:
        
            ext = os.path.splitext(file)[1].lower()
            
            if ext in TEXT_EXTENSIONS:
                stats['total_files'] += 1
                
                # JSON文件特殊处理
                if ext == '.json':
                    removed = process_json_file(filepath)
                    if removed > 0:
                        print(f"  JSON去重: {file} (移除 {removed} 个重复项)")
                    removed = remove_duplicate_lines(filepath)
                        print(f"  行去重: {file} (移除 {removed} 行)")
                
                stats['processed_files'] += 1
    
    print(f"已处理文件: {stats['processed_files']}")
    print(f"移除重复行: {stats['duplicate_lines_removed']}")
    
    # 第二步：查找并删除完全相同的重复文件
    print("第二步：查找并删除完全相同的重复文件...")
    duplicate_files = find_and_remove_duplicate_files()
    print(f"发现重复文件: {duplicate_files}")
    
    # 生成报告
    print("生成去重报告...")
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\\n")
        f.write("批量去重处理报告\\n")
        f.write("=" * 60 + "\\n\\n")
        
        f.write("处理统计:\\n")
        f.write(f"  - 处理文件总数: {stats['total_files']}\\n")
        f.write(f"  - 成功处理文件: {stats['processed_files']}\\n")
        f.write(f"  - 移除重复行数: {stats['duplicate_lines_removed']}\\n")
        f.write(f"  - 删除重复文件: {duplicate_files}\\n")
        f.write(f"  - 节省空间: {stats['bytes_saved'] / 1024:.2f} KB\\n")
        f.write(f"  - 备份目录: {DUPLICATES_DIR}\\n\\n")
        
        if stats['errors']:
            f.write("错误信息:\\n")
            for error in stats['errors'][:50]:  # 只显示前50条错误
                f.write(f"  - {error}\\n")
        
        f.write("\\n" + "=" * 60 + "\\n")
        f.write("处理完成\\n")
    
    print(f"报告已保存: {REPORT_FILE}")
    print("去重处理完成!")

if __name__ == "__main__":
    main()
"""
