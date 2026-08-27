"""
import os
import json
import hashlib
import shutil
from datetime import datetime

SOURCE_DIRS = [
    r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd\\多版本智能体协作系统设计 - DeepSeek_files",
    r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd\\数据文件",
    r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd\\新建文件夹",
    r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd\\Coze终极插件套件"
]

OUTPUT_DIR = r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd\\MERGED_KNOWLEDGE_BASE"
LARGE_FILES_DIR = os.path.join(OUTPUT_DIR, "LARGE_FILES")
CHUNK_SIZE = 1024 * 1024 * 50

SKILL_CATEGORIES = {
    "AI人工智能": ["AI", "artificial", "intelligence", "机器学习", "深度学习", "模型", "神经网络"],
    "金融理财": ["金融", "理财", "投资", "股票", "基金", "财富", "经济"],
    "自媒体运营": ["自媒体", "抖音", "视频", "直播", "变现", "内容创作"],
    "科技前沿": ["科技", "技术", "前沿", "互联网", "区块链", "元宇宙"],
    "医疗健康": ["医疗", "健康", "养生", "疾病", "医学"],
    "国学文化": ["国学", "文化", "历史", "哲学", "传统"],
    "地理知识": ["地理", "旅游", "地图", "城市"],
    "新闻时事": ["新闻", "时事", "热点", "资讯"],
    "法律法规": ["法律", "法规", "政策", "合规"],
    "个人提升": ["认知", "情商", "职场", "为人处世", "识人", "沟通"]
}

def get_file_hash(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except:
        return None

def categorize_file(filename):
    lower_name = filename.lower()
    for category, keywords in SKILL_CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in lower_name:
                return category
    return "其他"

def read_file_content(filepath):
        file_size = os.path.getsize(filepath)
        if file_size > CHUNK_SIZE:
            return {"type": "large_file", "size_mb": round(file_size / (1024 * 1024), 2)}
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if len(content) > 100000:
                return {"type": "large_content", "preview": content[:5000], "size_chars": len(content)}
            return {"type": "full_content", "content": content}
    except Exception as e:
        return {"type": "error", "error": str(e)}

def collect_all_files():
    all_files = []
    hash_set = set()
    duplicate_count = 0
    
    for source_dir in SOURCE_DIRS:
        if not os.path.exists(source_dir):
            print(f"警告: 目录不存在 {source_dir}")
            continue
            
        for root, dirs, files in os.walk(source_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                    file_hash = get_file_hash(filepath)
                    if file_hash in hash_set:
                        duplicate_count += 1
                    hash_set.add(file_hash)
                    
                    rel_path = os.path.relpath(filepath, r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd")
                    category = categorize_file(filename)
                    
                    all_files.append({
                        "filename": filename,
                        "filepath": filepath,
                        "rel_path": rel_path,
                        "size_bytes": file_size,
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "category": category,
                        "hash": file_hash,
                        "modified_time": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                    })
                    print(f"处理文件失败 {filepath}: {e}")
    
    return all_files, duplicate_count

def create_knowledge_base(files_data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(LARGE_FILES_DIR, exist_ok=True)
    
    category_stats = {}
    for file_info in files_data:
        cat = file_info["category"]
        if cat not in category_stats:
            category_stats[cat] = {"count": 0, "total_size_mb": 0}
        category_stats[cat]["count"] += 1
        category_stats[cat]["total_size_mb"] += file_info["size_mb"]
    
    large_files = [f for f in files_data if f["size_mb"] > 50]
    
    for large_file in large_files:
            new_name = f"{large_file['hash']}_{large_file['filename']}"
            dest_path = os.path.join(LARGE_FILES_DIR, new_name)
            shutil.copy2(large_file["filepath"], dest_path)
            large_file["large_file_path"] = f"LARGE_FILES/{new_name}"
            print(f"复制大文件失败 {large_file['filepath']}: {e}")
    
    knowledge_base = {
        "schema_version": "6.0",
        "name": "Coze全场景智能自动化超级中枢 - 综合技能版",
        "name_en": "Coze Omni Automation Hub - Comprehensive Skill Edition",
        "version": "25.0.0",
        "created_at": datetime.now().isoformat(),
        "description": "按照comprehensive-ai-dev.md技能体系整理的完整知识库",
        
        "source_directories": SOURCE_DIRS,
        "total_files": len(files_data),
        "total_size_mb": round(sum(f["size_mb"] for f in files_data), 2),
        "large_files_count": len(large_files),
        
        "category_statistics": category_stats,
        
        "skill_framework": {
            "core_concept": "Harness操作系统",
            "modules": [
                {"id": "universal", "name": "统一入口", "description": "智能路由统一入口"},
                {"id": "workflow", "name": "工作流自动化", "description": "支持工作流生成、修复、执行"},
                {"id": "plugin", "name": "插件开发", "description": "支持插件自动生成、参数修复、测试"},
                {"id": "json_fix", "name": "JSON修复", "description": "修复JSON格式错误、参数验证"},
                {"id": "ai_training", "name": "AI训练", "description": "支持模型训练、LoRA微调"},
                {"id": "multimedia", "name": "多媒体制作", "description": "视频生成、图像生成"},
                {"id": "data_processing", "name": "数据处理", "description": "数据收集、清洗、去重"}
            ],
            "error_codes": {
                "101001": {"code": "INVALID_PARAMS", "message": "参数重复或不合法"},
                "101002": {"code": "INCONSISTENT_API_PREFIX", "message": "API URL前缀不一致"},
                "101003": {"code": "INVALID_SCHEMA", "message": "Schema验证错误"},
                "101004": {"code": "MISSING_REQUIRED_FIELD", "message": "缺少必需字段"}
        },
        
        "files": files_data,
        
        "api_specification": {
            "openapi": "3.0.0",
            "base_url": "https://api.coze.cn",
            "api_url_prefix": "/api/v1/automation",
            "endpoints": [
                {"method": "POST", "path": "/v1/automation/execute", "description": "插件执行"},
                {"method": "POST", "path": "/v1/automation/validate", "description": "YAML/JSON格式验证"},
                {"method": "POST", "path": "/v1/automation/fix", "description": "错误修复"},
                {"method": "GET", "path": "/v1/automation/modules", "description": "模块列表"}
            "validation_rules": {
                "required_fields": ["action", "user_input"],
                "param_types": {"action": "string", "user_input": "string", "options": "object"},
                "url_prefix": "/api/v1"
        
        "security_features": {
            "input_sanitization": True,
            "parameter_validation": True,
            "environment_variable_protection": True,
            "injection_prevention": True,
            "rate_limiting": True,
            "audit_logging": True
    
    output_path = os.path.join(OUTPUT_DIR, "KNOWLEDGE_BASE_COMPLETE.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    
    summary_md = f\"\"\"# 知识库整理报告

## 统计概览

| 项目 | 数值 |
|------|------|
| 源目录数 | {len(SOURCE_DIRS)} |
| 处理文件数 | {len(files_data)} |
| 总大小 | {round(sum(f["size_mb"] for f in files_data), 2)} MB |
| 大文件数 (>50MB) | {len(large_files)} |

## 分类统计

\"\"\"
    
    for cat, stats in category_stats.items():
        summary_md += f"### {cat}\\n- 文件数: {stats['count']}\\n- 大小: {round(stats['total_size_mb'], 2)} MB\\n\\n"
    
    summary_md += \"\"\"## 大文件列表

| 文件名 | 大小 | 存储路径 |
|--------|------|----------|
    
        summary_md += f"| {large_file['filename']} | {large_file['size_mb']} MB | {large_file.get('large_file_path', '未复制')} |\\n"
    
    summary_md += f\"\"\"

## 输出文件

- `{OUTPUT_DIR}\\\\KNOWLEDGE_BASE_COMPLETE.json` - 完整知识库索引
- `{OUTPUT_DIR}\\\\LARGE_FILES\\\\` - 大文件存储目录

## 生成时间

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    summary_path = os.path.join(OUTPUT_DIR, "KNOWLEDGE_BASE_SUMMARY.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_md)
    
    return knowledge_base, summary_md

if __name__ == "__main__":
    print("开始收集所有文件...")
    files_data, duplicate_count = collect_all_files()
    print(f"收集完成: {len(files_data)} 个文件, 跳过 {duplicate_count} 个重复文件")
    
    print("创建知识库...")
    kb, summary = create_knowledge_base(files_data)
    
    print("\\n" + "="*60)
    print("整理完成!")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"总文件数: {kb['total_files']}")
    print(f"总大小: {kb['total_size_mb']} MB")
    print("="*60)
"""
