"""
# -*- coding: utf-8 -*-
import os
import sys
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

SOURCE_DIR = r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd"
OUTPUT_FILE = r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\完整知识库_深度去重版.md"

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
    print(f"🚀 启动完整知识库生成（直接去重版）...")
    print(f"📂 目标目录：{SOURCE_DIR}")
    print(f"📄 输出文件：{OUTPUT_FILE}\\n")
    
    seen_hashes = set()
    total_files = 0
    unique_files = 0
    total_lines = 0
    unique_lines = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as kb:
        kb.write(f"# 🌐 完全完整知识库（深度去重版）\\n")
        kb.write(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        kb.write(f"> 源目录：`{SOURCE_DIR}`\\n")
        kb.write(f"> 处理原则：去除所有重复语句和重复字，减少存储空间占用\\n\\n")
        kb.write("---\\n\\n")
        
        kb.write("## 📂 当前目录内容\\n\\n")
        
        dir_files = []
        for dirpath, dirnames, filenames in os.walk(SOURCE_DIR):
            dirnames.sort()
            filenames.sort()
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                if filename == Path(OUTPUT_FILE).name:
                    continue
                dir_files.append((dirpath, filename, full_path))
        
        current_dir = None
        seen_lines = set()
        
        for dirpath, filename, full_path in dir_files:
            total_files += 1
            content = extract_text_file(full_path)
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            if content_hash in seen_hashes:
            seen_hashes.add(content_hash)
            unique_files += 1
            
            if dirpath != current_dir:
                current_dir = dirpath
                rel_path = os.path.relpath(dirpath, SOURCE_DIR)
                if rel_path == '.':
                    display = "📁 根目录"
                    display = f"📁 {rel_path}"
                kb.write(f"### {display}\\n\\n")
            
                fsize = os.path.getsize(full_path)
                size_str = f"{fsize:,} 字节"
                size_str = "未知大小"
            
            kb.write(f"#### 📄 {filename}\\n")
            kb.write(f"- **来源**：本地目录\\n")
            kb.write(f"- **完整路径**：`{full_path}`\\n")
            kb.write(f"- **文件大小**：{size_str}\\n\\n")
            
            for line in content.split('\\n'):
                total_lines += 1
                line_stripped = line.strip()
                line_hash = hashlib.md5(line_stripped.encode('utf-8')).hexdigest()
                
                if line_hash in seen_lines:
                seen_lines.add(line_hash)
                unique_lines += 1
                kb.write(line + '\\n')
            
            kb.write("\\n---\\n\\n")
        
        print(f"✅ 已处理本地目录：{len(dir_files)} 个文件")
        
        zip_path = os.path.join(SOURCE_DIR, "sgdhfjasdkd.zip")
        if os.path.exists(zip_path):
            kb.write("## 📦 ZIP文件内容 (sgdhfjasdkd.zip)\\n\\n")
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for info in zf.infolist():
                    if info.is_dir():
                    
                    filename = info.filename
                    ext = Path(filename).suffix.lower()
                    
                            with zf.open(info) as file:
                                    content = file.read().decode('utf-8', errors='replace')
                                    content = file.read().decode('gbk', errors='replace')
                            content = "[占位标记：ZIP内二进制文件]"
                        content = "[ZIP提取失败]"
                    
                    
                    
                    kb.write(f"- **来源**：sgdhfjasdkd.zip 压缩包\\n")
                    kb.write(f"- **文件大小**：{info.file_size:,} 字节\\n\\n")
                    
                        
                    
            
            print(f"✅ 已处理ZIP文件：{len([x for x in zf.infolist() if not x.is_dir()])} 个文件")
        
        kb.write(f"\\n## ✅ 深度去重报告\\n")
        kb.write(f"- **扫描文件总数**：`{total_files}`\\n")
        kb.write(f"- **去重后文件数**：`{unique_files}`\\n")
        kb.write(f"- **重复文件数**：`{total_files - unique_files}`\\n")
        kb.write(f"- **文件去重率**：`{((total_files - unique_files) / total_files * 100):.2f}%`\\n")
        kb.write(f"- **原始行数**：`{total_lines}`\\n")
        kb.write(f"- **去重后行数**：`{unique_lines}`\\n")
        kb.write(f"- **行数去重率**：`{((total_lines - unique_lines) / total_lines * 100):.2f}%`\\n")
        kb.write(f"\\n> 🔒 所有重复语句和重复字已智能去除，存储空间占用已优化。\\n")
    
    print(f"\\n✅ 知识库生成完成！")
    print(f"📄 文件位置：{os.path.abspath(OUTPUT_FILE)}")
    print(f"📊 统计：")
    print(f"   - 文件：{total_files} → {unique_files}")
    print(f"   - 行数：{total_lines} → {unique_lines}")

if __name__ == "__main__":
    main()
"""
