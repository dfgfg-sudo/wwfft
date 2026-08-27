"""
全自动知识库构建系统 - 完整版
功能：合并、对比、修复、排版，并生成Coze插件
原则：无变动保留原文内容
"""
import os
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ==================== 配置区 ====================
ROOT_DIR = Path(r"d:\sfdhdjdtysjsy\sgdhfjasdkd")
KNOWLEDGE_BASE_DIR = ROOT_DIR / "KNOWLEDGE_BASE_OUTPUT"  # 知识库输出目录
REPORTS_DIR = KNOWLEDGE_BASE_DIR / "reports"             # 对比报告目录
MERGED_DIR = KNOWLEDGE_BASE_DIR / "merged_by_type"       # 按类型合并目录
FIXED_DIR = KNOWLEDGE_BASE_DIR / "fixed_files"           # 修复后文件目录
PLUGIN_DIR = KNOWLEDGE_BASE_DIR / "coze_plugin"          # Coze插件输出目录

# ==================== 工具函数 ====================
def safe_read_file(file_path):
    """安全读取文件内容，自动处理编码问题"""
    encodings = ['utf-8', 'gbk', 'latin-1']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    # 若全部失败，以二进制方式读取
    with open(file_path, 'rb') as f:
        return f.read().decode('utf-8', errors='replace')

def get_all_files(root_dir, ignore_dirs=None):
    """递归获取目录下所有文件"""
    if ignore_dirs is None:
        ignore_dirs = [KNOWLEDGE_BASE_DIR.name, '__pycache__', '.git']
    files = []
    for item in root_dir.rglob('*'):
        if item.is_file():
            # 忽略输出目录自身
            if any(ignored in item.parts for ignored in ignore_dirs):
                continue
            files.append(item)
    return files

# ==================== T1: 按后缀名合并所有文件 ====================
def merge_by_extension(root_dir):
    """将相同后缀名的所有文件内容完整合并"""
    print("\n" + "="*60)
    print("T1: 按文件类型合并中...")
    
    files = get_all_files(root_dir)
    ext_groups = defaultdict(list)
    
    for f in files:
        ext = f.suffix.lower() if f.suffix else '.no_ext'
        ext_groups[ext].append(f)
    
    os.makedirs(MERGED_DIR, exist_ok=True)
    
    for ext, file_list in ext_groups.items():
        ext_name = ext.lstrip('.') if ext != '.no_ext' else 'no_extension'
        merged_file_path = MERGED_DIR / f"merged_all.{ext_name}"
        
        with open(merged_file_path, 'w', encoding='utf-8') as out_f:
            out_f.write(f"# 合并文件类型: {ext}\n")
            out_f.write(f"# 生成时间: {datetime.now()}\n")
            out_f.write(f"# 包含文件数: {len(file_list)}\n\n")
            
            for f in sorted(file_list, key=lambda x: str(x)):
                relative_path = f.relative_to(root_dir)
                content = safe_read_file(f)
                out_f.write(f"\n{'='*80}\n")
                out_f.write(f"# 来源文件: {relative_path}\n")
                out_f.write(f"# 原始大小: {f.stat().st_size} bytes\n")
                out_f.write(f"{'='*80}\n\n")
                out_f.write(content)
                out_f.write("\n\n")
        
        print(f"  ✓ {ext} -> {merged_file_path.name} ({len(file_list)} 个文件)")
    
    print("T1 完成！")
    return True

# ==================== T2: 完整内容对比 ====================
def compare_all_files(root_dir):
    """对所有同名文件进行逐行对比"""
    print("\n" + "="*60)
    print("T2: 完整内容对比中...")
    
    files = get_all_files(root_dir)
    name_groups = defaultdict(list)
    
    for f in files:
        name_groups[f.name].append(f)
    
    # 只保留有多个同名文件的组
    duplicate_groups = {name: paths for name, paths in name_groups.items() if len(paths) > 1}
    
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_path = REPORTS_DIR / f"diff_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_path, 'w', encoding='utf-8') as report:
        report.write("# 文件内容对比报告\n\n")
        report.write(f"**生成时间**: {datetime.now()}\n\n")
        report.write(f"**同名文件组数**: {len(duplicate_groups)}\n\n")
        report.write("---\n\n")
        
        for file_name, file_paths in sorted(duplicate_groups.items()):
            report.write(f"## 文件: {file_name}\n\n")
            report.write(f"**出现次数**: {len(file_paths)}\n\n")
            report.write("| 序号 | 路径 | 大小(bytes) | MD5 |\n")
            report.write("|:---|:---|:---|:---|\n")
            
            for idx, fp in enumerate(file_paths, 1):
                size = fp.stat().st_size
                md5 = hashlib.md5(fp.read_bytes()).hexdigest()
                rel_path = fp.relative_to(root_dir)
                report.write(f"| {idx} | {rel_path} | {size} | {md5} |\n")
            
            # 逐行对比前两个文件
            if len(file_paths) >= 2:
                content1 = safe_read_file(file_paths[0]).splitlines()
                content2 = safe_read_file(file_paths[1]).splitlines()
                max_lines = max(len(content1), len(content2))
                diff_count = 0
                for i in range(max_lines):
                    line1 = content1[i] if i < len(content1) else '(文件1无此行)'
                    line2 = content2[i] if i < len(content2) else '(文件2无此行)'
                    if line1 != line2:
                        diff_count += 1
                report.write(f"\n**差异行数**: {diff_count}\n\n")
            
            report.write("---\n\n")
    
    print(f"  ✓ 发现 {len(duplicate_groups)} 组同名文件")
    print(f"  ✓ 报告已保存至: {report_path}")
    print("T2 完成！")
    return True

# ==================== T3: 技术错误自动修复 ====================
def fix_technical_errors(root_dir):
    """修复常见技术错误"""
    print("\n" + "="*60)
    print("T3: 技术错误修复中...")
    
    files = get_all_files(root_dir)
    os.makedirs(FIXED_DIR, exist_ok=True)
    
    fixed_count = 0
    
    for f in files:
        content = safe_read_file(f)
        original_content = content
        relative_path = f.relative_to(root_dir)
        
        # 修复1: 移除行尾空格
        content = '\n'.join(line.rstrip() for line in content.splitlines())
        
        # 修复2: JSON格式验证与修复
        if f.suffix.lower() == '.json':
            try:
                parsed = json.loads(content)
                content = json.dumps(parsed, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                # JSON有误，保持原样
                pass
        
        # 修复3: 确保文件以换行符结尾
        if content and not content.endswith('\n'):
            content += '\n'
        
        # 保存修复后文件（保持目录结构）
        if content != original_content:
            target_path = FIXED_DIR / relative_path
            os.makedirs(target_path.parent, exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as out_f:
                out_f.write(content)
            fixed_count += 1
    
    print(f"  ✓ 修复文件数: {fixed_count}")
    print("T3 完成！")
    return True

# ==================== T4: 文档精致排版 ====================
def format_all_outputs():
    """对所有输出文件进行统一排版"""
    print("\n" + "="*60)
    print("T4: 文档精致排版中...")
    
    # 生成知识库索引文件
    index_path = KNOWLEDGE_BASE_DIR / "KNOWLEDGE_INDEX.md"
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# 全量知识库索引\n\n")
        f.write(f"**构建时间**: {datetime.now()}\n\n")
        f.write("---\n\n")
        f.write("## 目录结构\n\n")
        
        # 扫描并记录所有目录和文件
        for root, dirs, files in os.walk(ROOT_DIR):
            # 忽略输出目录
            dirs[:] = [d for d in dirs if d != KNOWLEDGE_BASE_DIR.name]
            level = root.replace(str(ROOT_DIR), '').count(os.sep)
            indent = '  ' * level
            folder_name = os.path.basename(root) or ROOT_DIR.name
            f.write(f"{indent}- 📁 **{folder_name}/**\n")
            sub_indent = '  ' * (level + 1)
            for file in sorted(files):
                file_path = Path(root) / file
                size = file_path.stat().st_size
                f.write(f"{sub_indent}- 📄 {file} ({size:,} bytes)\n")
    
    print(f"  ✓ 知识库索引已生成: {index_path}")
    print("T4 完成！")
    return True

# ==================== T5: Coze IDE 插件生成 ====================
def generate_coze_plugin():
    """生成完整的Coze IDE插件框架"""
    print("\n" + "="*60)
    print("T5: Coze IDE 插件生成中...")
    
    os.makedirs(PLUGIN_DIR, exist_ok=True)
    
    # 插件主文件
    plugin_main = {
        "name": "全量知识库检索插件",
        "version": "1.0.0",
        "description": "基于完整本地知识库的智能检索与上下文提供插件",
        "author": "自动生成系统",
        "functions": [
            {
                "name": "search_knowledge",
                "description": "在完整知识库中检索相关内容",
                "parameters": {
                    "query": "string - 检索关键词",
                    "file_type": "string (可选) - 限定文件类型，如 py, json, md"
                }
            },
            {
                "name": "get_file_content",
                "description": "获取知识库中指定文件的完整内容",
                "parameters": {
                    "file_path": "string - 文件在知识库中的相对路径"
                }
            },
            {
                "name": "list_directory",
                "description": "列出知识库指定目录下的所有文件",
                "parameters": {
                    "directory": "string - 目录路径，留空则列出根目录"
                }
            }
        ]
    }
    
    with open(PLUGIN_DIR / "plugin_manifest.json", 'w', encoding='utf-8') as f:
        json.dump(plugin_main, f, ensure_ascii=False, indent=2)
    
    # 插件Python实现
    plugin_code = '''"""
Coze IDE 知识库插件 - 完整实现
功能：加载本地知识库，提供智能检索接口
"""
import json
import os
from pathlib import Path

class KnowledgeBasePlugin:
    def __init__(self, knowledge_base_path):
        self.kb_path = Path(knowledge_base_path)
        self.index = self._load_index()
    
    def _load_index(self):
        """加载知识库索引"""
        index_file = self.kb_path / "KNOWLEDGE_INDEX.md"
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def search_knowledge(self, query: str, file_type: str = None):
        """全文检索"""
        results = []
        for f in self.kb_path.rglob("*"):
            if f.is_file() and f.suffix in ['.py', '.json', '.md', '.txt']:
                if file_type and f.suffix.lstrip('.') != file_type:
                    continue
                try:
                    content = f.read_text(encoding='utf-8')
                    if query.lower() in content.lower():
                        results.append({
                            "file": str(f.relative_to(self.kb_path)),
                            "size": len(content)
                        })
                except:
                    pass
        return results[:20]
    
    def get_file_content(self, file_path: str):
        """获取文件内容"""
        full_path = self.kb_path / file_path
        if full_path.exists() and full_path.is_file():
            return full_path.read_text(encoding='utf-8')
        return None
    
    def list_directory(self, directory: str = ""):
        """列出目录"""
        target = self.kb_path / directory if directory else self.kb_path
        if target.exists() and target.is_dir():
            return {
                "directories": [d.name for d in target.iterdir() if d.is_dir()],
                "files": [f.name for f in target.iterdir() if f.is_file()]
            }
        return None
'''
    
    with open(PLUGIN_DIR / "knowledge_base_plugin.py", 'w', encoding='utf-8') as f:
        f.write(plugin_code)
    
    # 使用说明
    readme = f"""# Coze IDE 全量知识库插件

## 安装方法
1. 将本文件夹复制到Coze IDE的插件目录
2. 在Coze IDE中启用插件

## 功能说明
- **search_knowledge**: 在全量知识库中检索
- **get_file_content**: 获取指定文件完整内容
- **list_directory**: 浏览知识库目录结构

## 知识库路径
`{KNOWLEDGE_BASE_DIR}`

## 生成时间
{datetime.now()}
"""
    with open(PLUGIN_DIR / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f"  ✓ Coze插件已生成至: {PLUGIN_DIR}")
    print("T5 完成！")
    return True

# ==================== 主执行流程 ====================
def main():
    print("="*60)
    print("全自动知识库构建系统 v3.0")
    print(f"根目录: {ROOT_DIR}")
    print(f"输出目录: {KNOWLEDGE_BASE_DIR}")
    print("="*60)
    
    # 创建输出根目录
    os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
    
    # 按顺序执行所有任务
    tasks = [
        ("T1-按类型合并", merge_by_extension),
        ("T2-内容对比", compare_all_files),
        ("T3-错误修复", fix_technical_errors),
        ("T4-精致排版", format_all_outputs),
        ("T5-插件生成", generate_coze_plugin),
    ]
    
    for task_name, task_func in tasks:
        try:
            task_func(ROOT_DIR if 'T1' in task_name or 'T2' in task_name or 'T3' in task_name else None)
        except Exception as e:
            print(f"  ✗ {task_name} 失败: {e}")
    
    print("\n" + "="*60)
    print("所有任务执行完毕！")
    print(f"完整知识库已生成至: {KNOWLEDGE_BASE_DIR}")
    print("="*60)

if __name__ == "__main__":
    main()