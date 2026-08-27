"""
import os
import json
import base64
import hashlib
from datetime import datetime
from collections import defaultdict

BASE_DIR = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd'
OUTPUT_DIR = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\MERGED_KNOWLEDGE_BASE'

SOURCE_FOLDERS = [
    "多版本智能体协作系统设计 - DeepSeek_files",
    "数据文件",
    "新建文件夹",
    "Coze终极插件套件"
]

SKILL_CATEGORIES = {
    "harness": ["操作系统", "Harness", "状态持久化", "错误恢复", "自我修复"],
    "core_skills": ["GitHub Management", "Product Design", "Creative Production", 
                    "HyperFrames", "Remotion", "Browser/Web", "Presentations", 
                    "Skill Creator", "Browser Testing", "Figma"],
    "enhance_skills": ["UI/UX", "Superpowers", "Humanizer", "frontend-design", "Code Review"],
    "mcp_plugins": ["playwright", "filesystem", "sequential-thinking", "context7", "github", "memos"],
    "rag_knowledge": ["向量检索", "LLM重排", "知识库", "RAG", "文档分块"],
    "trading_agents": ["TradingAgents", "股票分析", "量化交易", "基本面分析", "技术分析"],
    "model_paradigm": ["Cola DLM", "ELF", "扩散语言模型", "DiT"],
    "tools": ["RTK", "ShipGate", "OpenHands", "Vibe Trading"]
}

LARGE_FILE_THRESHOLD = 50 * 1024 * 1024

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def calculate_file_hash(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def read_file_content(filepath):
    file_size = os.path.getsize(filepath)
    file_hash = calculate_file_hash(filepath)
    
    _, ext = os.path.splitext(filepath)
    
    if ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico']:
        if file_size > LARGE_FILE_THRESHOLD:
            return {
                "status": "external_large",
                "file_size_bytes": file_size,
                "hash": file_hash,
                "type": "image",
                "note": "Large file stored separately"
                "status": "success",
                "content": base64.b64encode(f.read()).decode('utf-8'),
                "size_bytes": file_size,
                "hash": file_hash
    
    try:
                "type": "text",
                "encoding": "utf-8",
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
                "content": content,
                "type": "text"
    except UnicodeDecodeError:
                    "encoding": "gbk",
            
            with open(filepath, 'r', encoding='gbk', errors='replace') as f:
        except:
                    "type": "binary",
            
    except Exception as e:
            "status": "error",
            "reason": str(e),
            "size_bytes": file_size

def save_large_file(filepath, output_dir):
    filename = os.path.basename(filepath)
    safe_name = f"{file_hash}_{filename}"
    output_path = os.path.join(output_dir, safe_name)
    
    with open(filepath, 'rb') as src:
        with open(output_path, 'wb') as dst:
            for chunk in iter(lambda: src.read(8192), b''):
                dst.write(chunk)
    
    return output_path

def categorize_file(file_name):
    file_name_lower = file_name.lower()
    for category, keywords in SKILL_CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in file_name_lower:
                return category
    return "other"

def process_directory(directory, base_path, file_hash_set, large_files_dir):
    result = {}
    file_count = 0
    
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        rel_path = os.path.relpath(item_path, base_path)
        
        if os.path.isdir(item_path):
            sub_result, sub_count = process_directory(item_path, base_path, file_hash_set, large_files_dir)
            if sub_result:
                result[item] = sub_result
                file_count += sub_count
        else:
            file_size = os.path.getsize(item_path)
            file_hash = calculate_file_hash(item_path)
            
            if file_hash in file_hash_set:
                content_info = {
                    "status": "duplicate",
                    "original_path": item_path,
                    "category": categorize_file(item),
                file_hash_set.add(file_hash)
                
                    external_path = save_large_file(item_path, large_files_dir)
                        "external_path": external_path,
                        "type": "text" if item.lower().endswith(('.txt', '.md', '.json', '.js', '.py')) else "binary"
                    content_info = read_file_content(item_path)
                    content_info["original_path"] = item_path
                    content_info["category"] = categorize_file(item)
                
                file_count += 1
            
            result[item] = content_info
    
    return result, file_count

def main():
    ensure_dir(OUTPUT_DIR)
    large_files_dir = os.path.join(OUTPUT_DIR, "LARGE_FILES")
    ensure_dir(large_files_dir)
    
    knowledge_base = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "source_folders": SOURCE_FOLDERS,
            "version": "4.0.0",
            "description": "综合AI开发知识库 - 合并四个文件夹的完整内容，超大文件单独存储",
            "total_files_processed": 0,
            "total_duplicates_found": 0,
            "total_large_files": 0,
            "total_errors": 0,
            "categories": list(SKILL_CATEGORIES.keys()),
            "harness_principle": "遵循Harness理念：状态持久化、错误恢复、自我修复",
            "large_file_threshold_bytes": LARGE_FILE_THRESHOLD
        },
        "content": {},
        "categorized_content": defaultdict(dict),
        "large_files": [],
        "errors": []
    
    file_hash_set = set()
    total_files = 0
    total_large = 0
    total_errors = 0
    
    print("开始处理所有源文件夹...")
    
    for folder_name in SOURCE_FOLDERS:
        folder_path = os.path.join(BASE_DIR, folder_name)
        if not os.path.exists(folder_path):
            print(f"警告：文件夹不存在 - {folder_path}")
            continue
        
        print(f"\\n处理文件夹: {folder_name}")
        folder_content, file_count = process_directory(folder_path, BASE_DIR, file_hash_set, large_files_dir)
        
        if folder_content:
            knowledge_base["content"][folder_name] = folder_content
            
            for file_name, file_info in folder_content.items():
                if isinstance(file_info, dict) and 'category' in file_info:
                    category = file_info['category']
                    knowledge_base["categorized_content"][category][file_name] = file_info
                    
                    if file_info.get('status') == 'external_large':
                        knowledge_base["large_files"].append({
                            "file": file_name,
                            "path": file_info.get('original_path'),
                            "external_path": file_info.get('external_path'),
                            "size_bytes": file_info.get('size_bytes')
                        })
                        total_large += 1
                    elif file_info.get('status') == 'error':
                        knowledge_base["errors"].append({
                            "error": file_info.get('reason')
                        total_errors += 1
        
        total_files += file_count
        print(f"  已处理文件: {file_count}")
    
    knowledge_base["metadata"]["total_files_processed"] = total_files
    knowledge_base["metadata"]["total_duplicates_found"] = len(file_hash_set) - total_files
    knowledge_base["metadata"]["total_large_files"] = total_large
    knowledge_base["metadata"]["total_errors"] = total_errors
    
    json_output = os.path.join(OUTPUT_DIR, "KNOWLEDGE_BASE_COMPLETE.json")
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    
    print(f"\\n完整知识库已生成: {json_output}")
    
    categorized_output = os.path.join(OUTPUT_DIR, "KNOWLEDGE_BASE_CATEGORIZED.json")
    with open(categorized_output, 'w', encoding='utf-8') as f:
        json.dump(dict(knowledge_base["categorized_content"]), f, ensure_ascii=False, indent=2)
    
    print(f"分类知识库已生成: {categorized_output}")
    
    summary_md = os.path.join(OUTPUT_DIR, "KNOWLEDGE_BASE_SUMMARY.md")
    with open(summary_md, 'w', encoding='utf-8') as f:
        f.write("# 综合AI知识库整理报告\\n\\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
        f.write(f"**源文件夹数量**: {len(SOURCE_FOLDERS)}\\n")
        f.write(f"**处理文件总数**: {total_files}\\n")
        f.write(f"**重复文件数**: {knowledge_base['metadata']['total_duplicates_found']}\\n")
        f.write(f"**超大文件数**: {total_large}\\n")
        f.write(f"**错误文件数**: {total_errors}\\n")
        f.write(f"**超大文件阈值**: {LARGE_FILE_THRESHOLD / (1024 * 1024):.0f} MB\\n\\n")
        f.write("## 分类统计\\n\\n")
        for category, items in knowledge_base["categorized_content"].items():
            f.write(f"- **{category}**: {len(items)} 个文件\\n")
        
        if knowledge_base["large_files"]:
            f.write("\\n## 超大文件列表\\n\\n")
            f.write("| 文件名 | 大小 | 原始路径 |\\n")
            f.write("|--------|------|----------|\\n")
            for lf in knowledge_base["large_files"]:
                size_mb = lf['size_bytes'] / (1024 * 1024)
                f.write(f"| {lf['file']} | {size_mb:.1f} MB | {lf['path']} |\\n")
    
    print(f"整理报告已生成: {summary_md}")
    print("\\n✅ 知识库整理完成！")
    
    return knowledge_base

if __name__ == "__main__":
    main()
"""
