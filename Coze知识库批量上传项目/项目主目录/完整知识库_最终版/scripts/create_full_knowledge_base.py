"""
import os
import json
import base64
from datetime import datetime

BASE_DIR = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\新建文件夹'
OUTPUT_FILE = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\KNOWLEDGE_BASE_COMPLETE\\COMPLETE_KNOWLEDGE_BASE_ALL.json'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def escape_content(content):
    if isinstance(content, str):
        return content.replace('\\\\', '\\\\\\\\').replace('"', '\\\\"').replace('\\n', '\\\\n').replace('\\r', '\\\\r')
    return content

def read_file_content(filepath):
    try:
        file_size = os.path.getsize(filepath)
        if file_size > MAX_FILE_SIZE:
            return {
                "status": "skipped",
                "reason": f"File too large ({file_size} bytes)",
                "size_bytes": file_size
            }
        
        _, ext = os.path.splitext(filepath)
        
        if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico']:
            with open(filepath, 'rb') as f:
                    "status": "base64",
                    "content": base64.b64encode(f.read()).decode('utf-8'),
        
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                    "status": "success",
                    "content": content,
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='gbk', errors='replace') as f:
                    "status": "success_gbk",
    except Exception as e:
            "status": "error",
            "reason": str(e)

def process_directory(directory, base_path):
    result = {}
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        rel_path = os.path.relpath(item_path, base_path)
        
        if os.path.isdir(item_path):
            result[item] = process_directory(item_path, base_path)
        else:
            result[item] = read_file_content(item_path)
    
    return result

def main():
    ensure_dir(os.path.dirname(OUTPUT_FILE))
    
    knowledge_base = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "source_directory": BASE_DIR,
            "version": "1.0.0",
            "description": "完整知识库 - 包含新建文件夹下所有目录和文件的全部原始内容",
            "max_file_size_bytes": MAX_FILE_SIZE,
            "total_directories": 0,
            "total_files": 0
        },
        "content": {}
    
    directories_to_process = [
        "backup_temp",
        "data",
        "deepseek_data-2026-05-13",
        "FINAL_OUTPUT",
        "MERGED_ALL_DATA",
        "merged_output",
        "plugins",
        "source_data",
        "UNIFIED_MERGED_DATA"
    ]
    
    file_count = 0
    
    for dir_name in directories_to_process:
        dir_path = os.path.join(BASE_DIR, dir_name)
        if os.path.exists(dir_path):
            print(f"Processing {dir_name}...")
            knowledge_base["content"][dir_name] = process_directory(dir_path, BASE_DIR)
            file_count += sum(1 for _, item in knowledge_base["content"][dir_name].items() 
                           if isinstance(item, dict) and "status" in item)
    
    knowledge_base["metadata"]["total_files"] = file_count
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    
    print(f"Knowledge base created: {OUTPUT_FILE}")
    print(f"Total files processed: {file_count}")

if __name__ == "__main__":
    main()
"""
