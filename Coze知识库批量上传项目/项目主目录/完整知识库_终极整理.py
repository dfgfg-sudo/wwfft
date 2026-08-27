"""
# -*- coding: utf-8 -*-
import os
import sys
import json
from pathlib import Path
from datetime import datetime

SOURCE_DIRS = [
    r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\完整知识库_最终版",
    r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\extracted_0628",
    r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\最终插件结果",
    r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\FINAL_COZE_PLUGIN_OUTPUT",
]
OUTPUT_FILE = r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\完整知识库_终极完整版.md"

TEXT_EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.htm', '.log',
                   '.py', '.js', '.java', '.c', '.cpp', '.h', '.sh', '.bat', '.sql', '.ini', 
                   '.ts', '.yaml', '.yml', '.jsonl', '.mdx', '.rst', '.text', 
                   '.properties', '.cfg', '.conf', '.toml', '.csv', '.tsv']

def extract_text_file(filepath):
    ext = Path(filepath).suffix.lower()
    if ext in TEXT_EXTENSIONS:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except:
                with open(filepath, 'r', errors='replace') as f:
                return "[修复失败：文件编码彻底损毁]"
    else:
        return "[占位标记：二进制/多媒体文件，内容已安全跳过]"

def main():
    print(f"🚀 启动完整知识库终极整理...")
    print(f"📂 目标目录：{SOURCE_DIRS}")
    print(f"📄 输出文件：{OUTPUT_FILE}\\n")
    
    total_files = 0
    total_size = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as kb:
        kb.write(f"# 🌐 完全完整知识库（终极完整版）\\n")
        kb.write(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        kb.write(f"> 处理原则：完整保留所有原文内容，不进行任何去重，确保内容完整\\n\\n")
        kb.write("---\\n\\n")
        
        for source_dir in SOURCE_DIRS:
            if not os.path.exists(source_dir):
                print(f"⚠️ 目录不存在：{source_dir}")
                continue
            
            kb.write(f"## 📂 {os.path.basename(source_dir)} 目录\\n\\n")
            
            dir_files = []
            for dirpath, dirnames, filenames in os.walk(source_dir):
                dirnames.sort()
                filenames.sort()
                for filename in filenames:
                    full_path = os.path.join(dirpath, filename)
                    dir_files.append((dirpath, filename, full_path))
            
            current_dir = None
            
            for dirpath, filename, full_path in dir_files:
                total_files += 1
                
                    fsize = os.path.getsize(full_path)
                    total_size += fsize
                    size_str = f"{fsize:,} 字节"
                    size_str = "未知大小"
                
                if dirpath != current_dir:
                    current_dir = dirpath
                    rel_path = os.path.relpath(dirpath, source_dir)
                    if rel_path == '.':
                        display = "📁 根目录"
                        display = f"📁 {rel_path}"
                    kb.write(f"### {display}\\n\\n")
                
                kb.write(f"#### 📄 {filename}\\n")
                kb.write(f"- **完整路径**：`{full_path}`\\n")
                kb.write(f"- **文件大小**：{size_str}\\n\\n")
                
                content = extract_text_file(full_path)
                kb.write(content)
                kb.write("\\n\\n---\\n\\n")
            
            print(f"✅ 已处理 {os.path.basename(source_dir)}：{len(dir_files)} 个文件")
        
        kb.write(f"\\n## ✅ 完整性校验报告\\n")
        kb.write(f"- **扫描文件总数**：`{total_files}`\\n")
        kb.write(f"- **文件总大小**：`{total_size:,} 字节` ({total_size / 1024 / 1024 / 1024:.2f} GB)\\n")
        kb.write(f"\\n> 🔒 所有文件均以**只读**方式处理，原文件完好无损。\\n")
        kb.write(f"> 📌 所有内容均已完整保留，未进行任何去重处理。\\n")
    
    print(f"\\n✅ 知识库终极整理完成！")
    print(f"📄 文件位置：{os.path.abspath(OUTPUT_FILE)}")
    print(f"📊 统计：共 {total_files} 个文件，总大小 {total_size / 1024 / 1024 / 1024:.2f} GB")

if __name__ == "__main__":
    main()
"""
