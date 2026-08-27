"""
import os
import shutil

def main():
    root_dir = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd'
    
    dirs = {
        'plugins': [],
        'scripts': [],
        'reports': [],
        'data': [],
        'config': [],
        'backup': [],
        'unmatched': []
    }
    
    files = [
        '11_FILES_FULL_MERGE_COMPLETE.txt',
        '11_FILES_ULTIMATE_COMPLETE.txt',
        'ALL_MERGED_PROCESSORS.py',
        'ALL_MERGED_SYSTEM.py',
        'bunny_ai_system.py',
        'COMPLETE_FULL_MERGE_ALL_CONTENTS.txt',
        'config.yaml',
        'Coze_Full_Automation_Super_Hub_Complete_Edition_v6.0_20260603.txt',
        'create_ultimate_complete_merge.py',
        'deepseek_ai_factory.py',
        'deepseek_ultimate_plugin.js',
        'drfgjgkvhcx.txt',
        'extract_topics.ps1',
        'FINAL_MERGED_COMPLETE_ALL.txt',
        'MERGED_ALL_MD_FILES.md',
        'MERGED_ALL_TXT_FILES.txt',
        'process_large_file.ps1',
        'sdfgfhjhdfgh1_备份.txt',
        'sdfgfhjhdfgh2.txt',
        'sdgfghgfhghhhj.txt',
        'verify_merge.py',
        '主题提取_自媒体抖音.txt',
        '主题提取_金融赚钱创业.txt',
        '全面合并脚本.py',
        '合并整理脚本.py',
        '多版本智能体协作系统设计 - DeepSeek.html',
        '完整整理脚本.ps1',
        '整理后的文档.md',
        '用户兴趣内容合集_20260601.md'
    ]
    
    for filename in files:
        filepath = os.path.join(root_dir, filename)
        if not os.path.exists(filepath):
            continue
        
        if filename.endswith('.js') and ('deepseek' in filename.lower() or 'plugin' in filename.lower()):
            dirs['plugins'].append(filename)
        elif filename.endswith('.py'):
            dirs['scripts'].append(filename)
        elif filename.endswith('.ps1'):
        elif filename.endswith('.md'):
            dirs['reports'].append(filename)
        elif filename.endswith('.html'):
        elif filename.endswith('.txt'):
            if '_备份' in filename or 'drfgjgkvhcx' in filename or 'sdfgfhjhdfgh' in filename or 'sdgfghgfhghhhj' in filename:
                dirs['backup'].append(filename)
            else:
        elif filename.endswith('.yaml') or filename.endswith('.yml'):
            dirs['config'].append(filename)
            dirs['unmatched'].append(filename)
    
    for dir_name, file_list in dirs.items():
        dir_path = os.path.join(root_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        for filename in file_list:
            src = os.path.join(root_dir, filename)
            dst = os.path.join(dir_path, filename)
            if os.path.exists(src):
                shutil.move(src, dst)
                print(f'移动: {filename} -> {dir_name}/')
    
    print(f'\\n整理完成！')
        print(f'  {dir_name}/: {len(file_list)} 个文件')

if __name__ == '__main__':
    main()
"""
