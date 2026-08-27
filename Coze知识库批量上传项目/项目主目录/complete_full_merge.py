"""
import os
import json
from datetime import datetime

ROOT_DIR = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd'
OUTPUT_DIR = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\COMPLETE_FINAL_OUTPUT'

EXCLUDE_DIRS = [
    'COMPLETE_FINAL_OUTPUT',
    '.git',
    '__pycache__',
    'node_modules',
]

EXCLUDE_FILES = [
    'complete_full_merge.py',
    'deepseek_data-2026-07-03.zip',

EXCLUDE_EXTENSIONS = [
    '.pyc', '.pyo', '.exe', '.dll', '.zip', '.rar', '.7z', '.gz', '.tar',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv',
    '.dat', '.log', '.tmp', '.temp',

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_all_files(root_dir):
    all_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        
        for filename in filenames:
            if filename in EXCLUDE_FILES:
                continue
            
            ext = os.path.splitext(filename)[1].lower()
            if ext in EXCLUDE_EXTENSIONS:
            
            all_files.append(os.path.join(dirpath, filename))
    return sorted(all_files)

def extract_conversation_text(conv):
    lines = []
    lines.append("=" * 120)
    lines.append(f"# 对话标题: {conv.get('title', '')}")
    lines.append(f"# 对话ID: {conv.get('id', '')}")
    lines.append(f"# 创建时间: {conv.get('inserted_at', '')}")
    lines.append(f"# 更新时间: {conv.get('updated_at', '')}")
    
    mapping = conv.get('mapping', {})
    for key, value in mapping.items():
        if key == 'root':
        msg = value.get('message')
        if not msg:
        
        fragments = msg.get('fragments', [])
        for frag in fragments:
            content = frag.get('content', '')
            frag_type = frag.get('type', '')
            if content:
                if frag_type == 'REQUEST':
                    lines.append("\\n" + "-" * 120)
                    lines.append("## 📝 用户提问 (蓝色框内容)")
                    lines.append("-" * 120)
                    lines.append(content)
                elif frag_type == 'THINK':
                    lines.append("## 💭 已思考 (AI思考过程)")
                elif frag_type == 'RESPONSE':
                    lines.append("## 🤖 AI回答")
                else:
                    lines.append(f"## {frag_type}")
    
    lines.append("\\n" + "=" * 120 + "\\n")
    return "\\n".join(lines)

def process_json_file(filepath, out_f):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            first_key = list(data[0].keys())[0] if data[0] else ''
            if 'title' in data[0] and 'mapping' in data[0] and 'id' in data[0]:
                out_f.write(f"# 类型: DeepSeek对话数据 (共{len(data)}条)\\n\\n")
                for i, conv in enumerate(data, 1):
                    if i % 100 == 0:
                        print(f"    处理对话 {i}/{len(data)}")
                    out_f.write(extract_conversation_text(conv))
                out_f.write(json.dumps(data, ensure_ascii=False, indent=2))
        return True
    except Exception:
        return False

def main():
    print("=" * 80)
    print("🤖 终极完整合并工具")
    print("📅", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    ensure_output_dir()
    
    all_files = get_all_files(ROOT_DIR)
    print(f"\\n📁 发现 {len(all_files)} 个文件")
    
    main_output = os.path.join(OUTPUT_DIR, '终极完整合并文档_包含全部内容.txt')
    
    with open(main_output, 'w', encoding='utf-8') as out_f:
        out_f.write("#" * 120 + "\\n")
        out_f.write("# 终极完整合并文档 - ULTIMATE COMPREHENSIVE MERGED DOCUMENT\\n")
        out_f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        out_f.write(f"# 文件总数: {len(all_files)}\\n")
        out_f.write(f"# 源目录: {ROOT_DIR}\\n")
        out_f.write("#" * 120 + "\\n\\n")
        
        for i, filepath in enumerate(all_files, 1):
            rel_path = os.path.relpath(filepath, ROOT_DIR)
            filename = os.path.basename(filepath)
            
                file_size = os.path.getsize(filepath)
            except:
                file_size = 0
            
            print(f"  [{i}/{len(all_files)}] {rel_path} ({file_size:,} 字节)")
            
            out_f.write("\\n" + "=" * 120 + "\\n")
            out_f.write(f"# FILE: {filepath}\\n")
            out_f.write(f"# PATH: {rel_path}\\n")
            out_f.write(f"# SIZE: {file_size:,} 字节\\n")
            out_f.write(f"# TYPE: {ext.upper()[1:] if ext else 'TEXT'}\\n")
            out_f.write("=" * 120 + "\\n")
            
                if ext == '.json':
                    if not process_json_file(filepath, out_f):
                        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                            out_f.write(f.read())
            except Exception as e:
                out_f.write(f"⚠️ 文件读取错误: {str(e)}\\n")
            
            out_f.write("\\n" + "=" * 120 + "\\n\\n")
    
    output_size = os.path.getsize(main_output)
    print(f"\\n✅ 终极合并文档: {main_output}")
    print(f"📦 文件大小: {output_size / 1024 / 1024:.2f} MB")
    
    stats_output = os.path.join(OUTPUT_DIR, '文件清单统计.txt')
    with open(stats_output, 'w', encoding='utf-8') as f:
        f.write("# 文件清单统计\\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        f.write(f"总文件数: {len(all_files)}\\n")
        f.write(f"输出文件大小: {output_size / 1024 / 1024:.2f} MB\\n")
        f.write("\\n文件列表:\\n")
        f.write("-" * 100 + "\\n")
        f.write(f"{'序号':<5} {'路径':<100} {'大小(KB)':<15} {'类型':<10}\\n")
            ext = os.path.splitext(filepath)[1].lower()
                size_kb = os.path.getsize(filepath) / 1024
                size_kb = 0
            f.write(f"{i:<5} {rel_path[:95]:<100} {size_kb:<15.2f} {ext[1:]:<10}\\n")
    
    print(f"\\n✅ 文件清单统计: {stats_output}")
    
    print("\\n" + "=" * 80)
    print("🎉 终极合并完成!")
    print(f"📁 输出目录: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

"""
