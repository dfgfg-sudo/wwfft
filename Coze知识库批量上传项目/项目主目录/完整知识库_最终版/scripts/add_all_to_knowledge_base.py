"""
import os
import json
import hashlib
from datetime import datetime

TARGET_DIRS = [
    r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd\\reports",
    r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd\\scripts",
    r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd\\backup"
]

OUTPUT_FILE = r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd\\KNOWLEDGE_BASE_COMPLETE\\COMPLETE_KNOWLEDGE_BASE_ALL.json"

def get_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"计算哈希失败 {filepath}: {e}")
        return None

def read_file_content(filepath):
        file_size = os.path.getsize(filepath)
        if file_size > 50 * 1024 * 1024:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                preview = f.read(5000)
            return {
                "type": "large_file",
                "size_mb": round(file_size / (1024 * 1024), 2),
                "preview": preview,
                "full_path": filepath
            }
        
            content = f.read()
        
        if len(content) > 500000:
                "type": "large_content",
                "size_chars": len(content),
                "preview": content[:5000],
        
            "type": "full_content",
            "content": content,
            "size_mb": round(file_size / (1024 * 1024), 2)
        return {"type": "error", "error": str(e), "full_path": filepath}

def collect_all_content():
    all_content = {
        "schema_version": "7.0",
        "name": "Coze全场景智能自动化超级中枢 - 终极完整版",
        "name_en": "Coze Omni Automation Hub - Ultimate Complete Edition",
        "version": "30.0.0",
        "created_at": datetime.now().isoformat(),
        "description": "整合reports、scripts、backup目录下所有文件内容的终极知识库",
        "total_files": 0,
        "total_size_mb": 0,
        "content": {}
    
    total_files = 0
    total_size = 0
    
    for target_dir in TARGET_DIRS:
        dir_name = os.path.basename(target_dir)
        all_content["content"][dir_name] = {}
        
        if not os.path.exists(target_dir):
            print(f"警告: 目录不存在 {target_dir}")
            continue
            
        for filename in os.listdir(target_dir):
            filepath = os.path.join(target_dir, filename)
            
            if not os.path.isfile(filepath):
                
                file_hash = get_file_hash(filepath)
                file_content = read_file_content(filepath)
                
                all_content["content"][dir_name][filename] = {
                    "filename": filename,
                    "filepath": filepath,
                    "hash": file_hash,
                    "size_bytes": file_size,
                    "modified_time": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                    "content": file_content
                
                total_files += 1
                total_size += file_size
                print(f"已处理: {filename} ({round(file_size / (1024 * 1024), 2)} MB)")
                
                print(f"处理文件失败 {filepath}: {e}")
    
    all_content["total_files"] = total_files
    all_content["total_size_mb"] = round(total_size / (1024 * 1024), 2)
    
    return all_content

if __name__ == "__main__":
    print("="*60)
    print("开始收集 reports、scripts、backup 目录下的所有文件内容")
    
    knowledge_base = collect_all_content()
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    
    print("\\n" + "="*60)
    print("知识库更新完成!")
    print(f"输出文件: {OUTPUT_FILE}")
    print(f"处理文件数: {knowledge_base['total_files']}")
    print(f"总大小: {knowledge_base['total_size_mb']} MB")
    
    print("\\n📋 目录统计:")
    for dir_name, files in knowledge_base["content"].items():
        dir_size = sum(f["size_mb"] for f in files.values())
        print(f"  - {dir_name}: {len(files)}个文件, {round(dir_size, 2)} MB")
"""
