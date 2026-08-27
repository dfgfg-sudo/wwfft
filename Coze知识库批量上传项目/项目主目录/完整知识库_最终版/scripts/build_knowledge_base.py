"""
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(r"d:\\sfdhdjdtysjsy")
OUTPUT_FILE = BASE_DIR / "FINAL_KNOWLEDGE_BASE_COMPLETE.json"
 
def get_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except:
        return None

def read_file_content(filepath, max_size=50*1024*1024):
        file_size = filepath.stat().st_size
        if file_size > max_size:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return {"type": "large_file", "preview": f.read(5000), "size_bytes": file_size}
            content = f.read()
            return {"type": "full_content", "content": content, "size_bytes": file_size}
    except Exception as e:
        return {"type": "error", "error": str(e)}

print("=== 开始创建完整知识库 ===")

knowledge_base = {
    "schema_version": "8.0",
    "name": "DeepSeek AI Factory Ultimate - 完整知识库",
    "name_en": "DeepSeek AI Factory Ultimate - Complete Knowledge Base",
    "version": "8.0.0",
    "created_at": datetime.now().isoformat(),
    "description": "整合项目所有目录和文件的完整知识库",
    "source_directory": str(BASE_DIR),
    "total_files": 0,
    "total_size_bytes": 0,
    "total_size_mb": 0,
    "content": {}
}

hash_set = set()
total_files = 0
total_size = 0

print("扫描目录:", BASE_DIR.name)

for root, dirs, files in os.walk(BASE_DIR):
    rel_root = os.path.relpath(root, BASE_DIR)
    if rel_root == ".":
        rel_root = "root"
    
    knowledge_base["content"][rel_root] = {}
    
    for filename in files:
        filepath = Path(root) / filename
        
            file_hash = get_file_hash(filepath)
            if file_hash in hash_set:
                continue
            hash_set.add(file_hash)
            
            content = read_file_content(filepath)
            
            knowledge_base["content"][rel_root][filename] = {
                "filename": filename,
                "filepath": str(filepath),
                "rel_path": str(filepath.relative_to(BASE_DIR)),
                "hash": file_hash,
                "size_bytes": file_size,
                "modified_time": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                "content": content
            
            total_files += 1
            total_size += file_size
            
            if total_files % 50 == 0:
                print("已处理:", total_files, "个文件...")
                
            print("跳过文件", filename, ":", e)

knowledge_base["total_files"] = total_files
knowledge_base["total_size_bytes"] = total_size
knowledge_base["total_size_mb"] = round(total_size / (1024 * 1024), 2)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(knowledge_base, f, ensure_ascii=False, indent=2)

print()
print("=== 知识库创建完成 ===")
print("输出文件:", OUTPUT_FILE)
print("总文件数:", total_files)
print("总大小:", knowledge_base["total_size_mb"], "MB")
print("去重后文件数:", len(hash_set))
"""
