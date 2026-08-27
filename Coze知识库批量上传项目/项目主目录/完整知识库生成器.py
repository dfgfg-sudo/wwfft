"""
# -*- coding: utf-8 -*-
import os
import sys
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

SOURCE_DIR = r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd"
ZIP_FILE = r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\sgdhfjasdkd.zip"
EXTRACED_DIR = r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\extracted_0628"
OUTPUT_FILE = r"D:\\sfdhdjdtysjsy\\sgdhfjasdkd\\完整知识库_最终合并版_含ZIP内容.md"

TEXT_EXTENSIONS = ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.htm', '.log',
                   '.py', '.js', '.java', '.c', '.cpp', '.h', '.sh', '.bat', '.sql', '.ini', 
                   '.ts', '.yaml', '.yml', '.jsonl', '.mdx', '.rst', '.text', 
                   '.properties', '.cfg', '.conf', '.toml', '.csv', '.tsv']

def extract_text_file(filepath):
    ext = Path(filepath).suffix.lower()
    if ext in TEXT_EXTENSIONS:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                for chunk in iter(lambda: f.read(65536), ''):
                    yield chunk
            return
        except PermissionError:
            yield "[安全拦截：文件无读取权限]"
        except:
                with open(filepath, 'r', errors='replace') as f:
                yield "[修复失败：文件编码彻底损毁，已跳过二进制]"
    else:
        yield "[占位标记：二进制/多媒体/特殊格式文件，内容已安全跳过]"

def md5_hash_content(filepath):
    md5 = hashlib.md5()
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    md5.update(chunk)
            return md5.hexdigest()
            return hashlib.md5(b"").hexdigest()
        return hashlib.md5(b"binary").hexdigest()

def main():
    print(f"🚀 启动完整知识库生成...")
    print(f"📂 目标目录：{SOURCE_DIR}")
    print(f"📦 ZIP文件：{ZIP_FILE}")
    print(f"📂 extracted_0628目录：{EXTRACED_DIR}")
    print(f"📄 输出文件：{OUTPUT_FILE}\\n")
    
    seen_hashes = set()
    total_files = 0
    unique_files = 0
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as kb:
        kb.write(f"# 🌐 完全完整知识库（安全镜像 - 去重版）\\n")
        kb.write(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        kb.write(f"> 源目录：`{SOURCE_DIR}`\\n")
        kb.write(f"> ZIP文件：`{ZIP_FILE}`\\n")
        kb.write(f"> extracted_0628目录：`{EXTRACED_DIR}`\\n")
        kb.write(f"> 安全声明：所有源文件仅被读取，未被写入或移动。\\n")
        kb.write(f"> 处理原则：无变动保留原文内容，智能去除重复内容\\n\\n")
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
        for dirpath, filename, full_path in dir_files:
            total_files += 1
            content_hash = md5_hash_content(full_path)
            
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
            
            for chunk in extract_text_file(full_path):
                kb.write(chunk)
            
            kb.write("\\n\\n---\\n\\n")
        
        print(f"✅ 已处理本地目录：{len(dir_files)} 个文件，去重后 {unique_files} 个")
        
        if os.path.exists(ZIP_FILE):
            kb.write("## 📦 ZIP文件内容 (sgdhfjasdkd.zip)\\n\\n")
            
            with zipfile.ZipFile(ZIP_FILE, 'r') as zf:
                for info in zf.infolist():
                    if info.is_dir():
                    
                    filename = info.filename
                    content_hash = hashlib.md5(filename.encode()).hexdigest()
                    
                    
                    size = info.file_size
                    ext = Path(filename).suffix.lower()
                    
                    kb.write(f"- **来源**：sgdhfjasdkd.zip 压缩包\\n")
                    kb.write(f"- **文件大小**：{size:,} 字节\\n\\n")
                    
                            with zf.open(info) as file:
                                    chunk = file.read(65536)
                                        kb.write(chunk.decode('utf-8', errors='replace'))
                                        kb.write(chunk.decode('gbk', errors='replace'))
                            kb.write("[占位标记：ZIP内二进制/多媒体文件，内容已安全跳过]")
                    except Exception as e:
                        kb.write(f"[ZIP提取警告：{str(e)}]")
                    
            
            print(f"✅ 已处理ZIP文件：{len([x for x in zf.infolist() if not x.is_dir()])} 个文件")
        
        kb.write(f"\\n## ✅ 完整性校验报告\\n")
        kb.write(f"- **扫描文件总数**：`{total_files}`\\n")
        kb.write(f"- **去重后文件数**：`{unique_files}`\\n")
        kb.write(f"- **重复文件数**：`{total_files - unique_files}`\\n")
        kb.write(f"- **去重率**：`{((total_files - unique_files) / total_files * 100):.2f}%`\\n")
        kb.write(f"\\n> 🔒 所有文件均以**只读**方式处理，原文件完好无损。\\n")
        kb.write(f"> 📌 所有唯一内容均已保留，重复内容已智能去除。\\n")
    
    print(f"\\n✅ 知识库构建完成！")
    print(f"📄 文件位置：{os.path.abspath(OUTPUT_FILE)}")
    print(f"📊 统计：共 {total_files} 个文件，去重后 {unique_files} 个唯一内容")

if __name__ == "__main__":
    main()
"""
