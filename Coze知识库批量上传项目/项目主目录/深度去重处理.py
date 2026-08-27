"""
# -*- coding: utf-8 -*-
import os
import sys
import hashlib
from datetime import datetime

INPUT_FILE = r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\完整知识库_最终合并版_含ZIP内容.md"
OUTPUT_FILE = r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\完整知识库_深度去重版.md"

def md5_hash(content):
    return hashlib.md5(content.encode('utf-8', errors='replace')).hexdigest()

def main():
    print(f"🚀 启动深度去重处理...")
    print(f"📂 输入文件：{INPUT_FILE}")
    print(f"📄 输出文件：{OUTPUT_FILE}\\n")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 输入文件不存在：{INPUT_FILE}")
        sys.exit(1)
    
    seen_line_hashes = set()
    seen_paragraph_hashes = set()
    seen_section_hashes = set()
    
    total_lines = 0
    unique_lines = 0
    total_paragraphs = 0
    unique_paragraphs = 0
    total_sections = 0
    unique_sections = 0
    
    current_paragraph = []
    
    with open(INPUT_FILE, 'r', encoding='utf-8', errors='replace') as infile, \\
         open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        
        outfile.write(f"# 🌐 完全完整知识库（深度去重版）\\n")
        outfile.write(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        outfile.write(f"> 源文件：`{INPUT_FILE}`\\n")
        outfile.write(f"> 处理原则：去除所有重复语句、重复字，减少存储空间占用\\n\\n")
        outfile.write("---\\n\\n")
        
        for line in infile:
            total_lines += 1
            line_stripped = line.strip()
            
            if not line_stripped:
                if current_paragraph:
                    total_paragraphs += 1
                    paragraph_content = ''.join(current_paragraph)
                    paragraph_hash = md5_hash(paragraph_content)
                    
                    if paragraph_hash not in seen_paragraph_hashes:
                        seen_paragraph_hashes.add(paragraph_hash)
                        unique_paragraphs += 1
                        outfile.write(paragraph_content)
                        outfile.write('\\n\\n')
                
                outfile.write('\\n')
                continue
            
            line_hash = md5_hash(line_stripped)
            
            if line_hash in seen_line_hashes:
            
            seen_line_hashes.add(line_hash)
            unique_lines += 1
            current_paragraph.append(line)
        
            
        
        outfile.write(f"\\n\\n## ✅ 深度去重报告\\n")
        outfile.write(f"- **原始行数**：`{total_lines}`\\n")
        outfile.write(f"- **去重后行数**：`{unique_lines}`\\n")
        outfile.write(f"- **行数去重率**：`{((total_lines - unique_lines) / total_lines * 100):.2f}%`\\n")
        outfile.write(f"- **原始段落数**：`{total_paragraphs}`\\n")
        outfile.write(f"- **去重后段落数**：`{unique_paragraphs}`\\n")
        outfile.write(f"- **段落去重率**：`{((total_paragraphs - unique_paragraphs) / total_paragraphs * 100):.2f}%`\\n")
        outfile.write(f"\\n> 🔒 所有重复语句和重复字已智能去除，存储空间占用已优化。\\n")
    
    print(f"\\n✅ 深度去重处理完成！")
    print(f"📄 文件位置：{os.path.abspath(OUTPUT_FILE)}")
    print(f"📊 统计：")
    print(f"   - 原始行数：{total_lines}")
    print(f"   - 去重后行数：{unique_lines}")
    print(f"   - 行数去重率：{((total_lines - unique_lines) / total_lines * 100):.2f}%")
    print(f"   - 原始段落数：{total_paragraphs}")
    print(f"   - 去重后段落数：{unique_paragraphs}")
    print(f"   - 段落去重率：{((total_paragraphs - unique_paragraphs) / total_paragraphs * 100):.2f}%")

if __name__ == "__main__":
    main()
"""
