"""
import os
import json
import base64
from datetime import datetime
from pathlib import Path

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def read_file_content(filepath):
    \"\"\"读取文件内容，支持多种文件类型\"\"\"
    try:
        suffix = filepath.suffix.lower()
        file_size = filepath.stat().st_size
        
        # 如果文件太大，只返回占位符
        if file_size > MAX_FILE_SIZE:
            return f"[文件过大，已跳过完整内容，大小: {file_size} bytes]"
        
        if suffix == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                    return json.loads(content)
                except:
                    return content
        
        elif suffix in ['.txt', '.md', '.html', '.css', '.js', '.ts', '.py', '.yaml', '.yml', '.bat', '.ps1']:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        else:
            with open(filepath, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        return f"[读取错误: {str(e)}]"

def escape_content(content):
    \"\"\"转义内容中的特殊字符\"\"\"
    if isinstance(content, str):
        return content.replace('\\\\', '\\\\\\\\').replace('"', '\\\\"').replace('\\n', '\\\\n').replace('\\r', '\\\\r')
    elif isinstance(content, dict):
        return json.dumps(content, ensure_ascii=False).replace('\\\\', '\\\\\\\\').replace('"', '\\\\"')
    return str(content)

def get_file_category(suffix):
    \"\"\"根据文件后缀获取分类\"\"\"
    categories = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.html': 'html',
        '.md': 'markdown',
        '.json': 'json',
        '.txt': 'text',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.css': 'stylesheet',
        '.bat': 'batch',
        '.ps1': 'powershell'
    }
    return categories.get(suffix, 'other')

def write_knowledge_base_streaming(output_file, base_dir, target_dirs, root_files):
    \"\"\"使用流式写入创建知识库\"\"\"
    total_files = 0
    dir_count = 0
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('{\\n')
        f.write('  "metadata": {\\n')
        f.write(f'    "generated_at": "{datetime.now().isoformat()}",\\n')
        f.write(f'    "source_directory": "{str(base_dir)}",\\n')
        f.write('    "version": "1.0.0",\\n')
        f.write('    "description": "完整知识库 - 包含所有目录和文件的全部原始内容",\\n')
        f.write('    "max_file_size_bytes": ' + str(MAX_FILE_SIZE) + '\\n')
        f.write('  },\\n')
        
        # 根目录文件
        f.write('  "root_files": {\\n')
        first_root = True
        for filename in root_files:
            filepath = base_dir / filename
            if filepath.exists():
                content = read_file_content(filepath)
                escaped_content = escape_content(content)
                
                if not first_root:
                    f.write(',\\n')
                first_root = False
                
                f.write(f'    "{filename}": {{\\n')
                f.write(f'      "type": "file",\\n')
                f.write(f'      "category": "{get_file_category(filepath.suffix.lower())}",\\n')
                f.write(f'      "content": "{escaped_content}",\\n')
                f.write(f'      "size": {filepath.stat().st_size},\\n')
                f.write(f'      "modified": "{datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()}"\\n')
                f.write('    }')
                total_files += 1
                print(f"  已处理: {filename}")
        f.write('\\n  },\\n')
        
        # 目录内容
        f.write('  "directories": {\\n')
        first_dir = True
        for dir_name in target_dirs:
            dir_path = base_dir / dir_name
            if not dir_path.exists():
                continue
            
            if not first_dir:
            first_dir = False
            
            f.write(f'    "{dir_name}": ')
            _, file_count = write_directory_streaming(f, dir_path, 4)
            total_files += file_count
            dir_count += 1
            print(f"  已处理 {file_count} 个文件")
        
        f.write(f'  "file_count": {total_files},\\n')
        f.write(f'  "directory_count": {dir_count}\\n')
        f.write('}')
    
    return total_files, dir_count

def write_directory_streaming(f, dir_path, indent):
    \"\"\"递归写入目录内容\"\"\"
    indent_str = '  ' * indent
    inner_indent_str = '  ' * (indent + 1)
    
    first_item = True
    file_count = 0
    
        items = list(dir_path.iterdir())
        items.sort(key=lambda x: (x.is_file(), x.name.lower()))
        
        for item in items:
            item_name = item.name
            
            if not first_item:
            first_item = False
            
            if item.is_file():
                content = read_file_content(item)
                
                f.write(f'{inner_indent_str}"{item_name}": {{\\n')
                f.write(f'{inner_indent_str}  "type": "file",\\n')
                f.write(f'{inner_indent_str}  "category": "{get_file_category(item.suffix.lower())}",\\n')
                f.write(f'{inner_indent_str}  "content": "{escaped_content}",\\n')
                f.write(f'{inner_indent_str}  "size": {item.stat().st_size},\\n')
                f.write(f'{inner_indent_str}  "modified": "{datetime.fromtimestamp(item.stat().st_mtime).isoformat()}"\\n')
                f.write(f'{inner_indent_str}}}')
                file_count += 1
            
            elif item.is_dir():
                sub_path = dir_path / item_name
                f.write(f'{inner_indent_str}"{item_name}": ')
                _, sub_count = write_directory_streaming(f, sub_path, indent + 1)
                file_count += sub_count
    
    except PermissionError:
        f.write(f'{inner_indent_str}"error": "权限拒绝"')
    
    f.write(f'\\n{indent_str}}}')
    return None, file_count

def create_complete_knowledge_base():
    \"\"\"创建完整的知识库数据库\"\"\"
    base_dir = Path('d:/sfdhdjdtysjsy/sgdhfjasdkd')
    output_dir = base_dir / 'KNOWLEDGE_BASE_COMPLETE'
    output_dir.mkdir(exist_ok=True)
    
    # 包含所有指定的目录
    target_dirs = [
        '.trae/specs/content_extraction_20260601',
        '多版本智能体协作系统设计 - DeepSeek_files',
        '数据文件',
        '新建文件夹',
        '主题提取',
        'backup',
        'Coze终极插件套件',
        'config',
        'reports',
        'plugins',
        'scripts',
        'dhfdfghj'
    ]
    
    # 也包含根目录的文件
    root_files = [
        '整理根目录文件.py',
        'create_knowledge_base.py',
        'dhfdfghj_完整合并版.md',
        'generate_complete_knowledge_base.py'
    
    # 保存完整知识库（流式写入）
    output_file = output_dir / 'COMPLETE_KNOWLEDGE_BASE_FULL.json'
    print(f"保存知识库到: {output_file}")
    print("\\n处理根目录文件...")
    
    total_files, dir_count = write_knowledge_base_streaming(output_file, base_dir, target_dirs, root_files)
    
    print(f"\\n知识库创建完成！")
    print(f"总计: {total_files} 个文件, {dir_count} 个目录")
    
    # 创建索引文件
    index_file = output_dir / 'KNOWLEDGE_INDEX.json'
    create_index(base_dir, target_dirs, root_files, index_file)
    

def create_index(base_dir, target_dirs, root_files, index_file):
    \"\"\"创建索引文件\"\"\"
    index = {
        'generated_at': datetime.now().isoformat(),
        'files': []
    
            index['files'].append({
                'path': filename,
                'category': get_file_category(filepath.suffix.lower()),
                'size': filepath.stat().st_size
            })
    
        if dir_path.exists():
            scan_for_index(dir_path, dir_name, index['files'])
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"索引文件已创建: {index_file}")

def scan_for_index(dir_path, base_path, files_list):
    \"\"\"递归扫描目录创建索引\"\"\"
    for item in dir_path.iterdir():
        full_path = f"{base_path}/{item.name}"
            files_list.append({
                'path': full_path,
                'category': get_file_category(item.suffix.lower()),
                'size': item.stat().st_size
            scan_for_index(item, full_path, files_list)

if __name__ == '__main__':
    create_complete_knowledge_base()

"""
