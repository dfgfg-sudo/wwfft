"""
# -*- coding: utf-8 -*-
import os
import sys
import hashlib
from pathlib import Path
from datetime import datetime

INPUT_FILE = r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\完整知识库_最终合并版_含ZIP内容.md"
OUTPUT_FILE = r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\完整知识库_精细化整理版.md"

def md5_hash(content):
    return hashlib.md5(content.encode('utf-8', errors='replace')).hexdigest()

def main():
    print(f"🚀 启动知识库去重转移...")
    print(f"📂 输入文件：{INPUT_FILE}")
    print(f"📄 输出文件：{OUTPUT_FILE}\\n")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 输入文件不存在：{INPUT_FILE}")
        sys.exit(1)
    
    seen_hashes = set()
    total_sections = 0
    unique_sections = 0
    duplicate_sections = 0
    
    current_section = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8', errors='replace') as infile, \\
         open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        
        outfile.write(f"# 🌐 完全完整知识库（精细化整理版 - 去重后）\\n")
        outfile.write(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        outfile.write(f"> 源文件：`{INPUT_FILE}`\\n")
        outfile.write(f"> 处理原则：无变动保留原文内容，智能去除重复内容\\n\\n")
        outfile.write("---\\n\\n")
        
        for line in infile:
            if line.strip() == '---':
                if current_section:
                    total_sections += 1
                    content = ''.join(current_section)
                    content_hash = md5_hash(content)
                    
                    if content_hash in seen_hashes:
                        duplicate_sections += 1
                    else:
                        seen_hashes.add(content_hash)
                        unique_sections += 1
                        outfile.write(content)
                        outfile.write("\\n---\\n\\n")
                
                current_section.append(line)
        
            
            if content_hash not in seen_hashes:
        
        outfile.write(f"\\n## ✅ 去重报告\\n")
        outfile.write(f"- **原始章节总数**：`{total_sections}`\\n")
        outfile.write(f"- **重复章节数**：`{duplicate_sections}`\\n")
        outfile.write(f"- **去重后章节数**：`{unique_sections}`\\n")
        outfile.write(f"- **去重率**：`{((duplicate_sections / total_sections) * 100):.2f}%`\\n")
        outfile.write(f"\\n> 🔒 所有唯一内容均已保留，重复内容已智能去除。\\n")
    
    print(f"\\n✅ 知识库去重转移完成！")
    print(f"📄 文件位置：{os.path.abspath(OUTPUT_FILE)}")
    print(f"📊 统计：")
    print(f"   - 原始章节：{total_sections}")
    print(f"   - 重复章节：{duplicate_sections}")
    print(f"   - 去重后章节：{unique_sections}")

if __name__ == "__main__":
    main()
"""
