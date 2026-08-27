"""
import json
import os
from collections import defaultdict

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载失败 {filepath}: {e}")
        return None

def extract_all_content_types(conv):
    \"\"\"提取所有内容类型\"\"\"
    results = {
        'REQUEST': [],
        'THINK': [],
        'RESPONSE': [],
        'SEARCH': []
    }
    
    conv_id = conv.get('id', '')
    title = conv.get('title', '')
    date = conv.get('inserted_at', '')
    
    mapping = conv.get('mapping', {})
    for node_id, node_data in mapping.items():
        message = node_data.get('message')
        if not message:
            continue
        
        fragments = message.get('fragments', [])
        for fragment in fragments:
            ftype = fragment.get('type', '')
            content = fragment.get('content', '').strip()
            
            if ftype in results and content:
                results[ftype].append({
                    'conv_id': conv_id,
                    'title': title,
                    'date': date[:10] if date else '',
                    'content': content
                })
    
    return results

def save_as_txt(data, filepath, content_type):
    \"\"\"保存为TXT文件\"\"\"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{'='*60}\\n")
        f.write(f"  {content_type} 内容汇总\\n")
        f.write(f"{'='*60}\\n\\n")
        f.write(f"总数: {len(data)} 条\\n\\n")
        
        for i, item in enumerate(data, 1):
            f.write(f"【{i}】{item['title']}\\n")
            f.write(f"日期: {item['date']}\\n")
            f.write(f"ID: {item['conv_id']}\\n")
            f.write(f"{'-'*40}\\n")
            f.write(f"{item['content']}\\n")

def process_all_sources():
    \"\"\"处理所有数据源\"\"\"
    print("🚀 开始处理所有数据源...")
    
    base_dir = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd'
    output_dir = os.path.join(base_dir, 'merged_output', 'txt_output')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    all_results = {
    
    sources = [
        ('extract_0601', os.path.join(base_dir, 'merged_output', 'extract_0601', 'conversations.json')),
        ('extract_0606', os.path.join(base_dir, 'merged_output', 'extract_0606', 'conversations.json')),
        ('新建文件夹', os.path.join(base_dir, '新建文件夹', 'deepseek_data-2026-05-13', 'conversations.json')),
        ('deepseek_data-2026-05-13', os.path.join(base_dir, 'deepseek_data-2026-05-13', 'conversations.json'))
    ]
    
    for source_name, filepath in sources:
        if os.path.exists(filepath):
            print(f"📥 处理 {source_name}...")
            convs = load_json(filepath) or []
            
            for conv in convs:
                extracted = extract_all_content_types(conv)
                for ftype in all_results:
                    all_results[ftype].extend(extracted[ftype])
        else:
            print(f"⚠️ 文件不存在: {filepath}")
    
    # 保存为TXT文件
    print("\\n📝 保存为TXT文件...")
    
        if all_results[ftype]:
            txt_path = os.path.join(output_dir, f'{ftype}_全部内容.txt')
            save_as_txt(all_results[ftype], txt_path, ftype)
            print(f"✅ {ftype}: {len(all_results[ftype])} 条 -> {txt_path}")
    
    # 生成汇总报告
    summary_path = os.path.join(output_dir, '处理汇总.txt')
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\\n")
        f.write("  四个数据源完整处理汇总报告\\n")
        f.write("="*60 + "\\n\\n")
        f.write("数据源:\\n")
        f.write("  1. deepseek_data-2026-06-01.zip\\n")
        f.write("  2. deepseek_data-2026-06-06 (1).zip\\n")
        f.write("  3. 新建文件夹\\n")
        f.write("  4. deepseek_data-2026-05-13\\n\\n")
        f.write("统计:\\n")
        f.write(f"  REQUEST (提问): {len(all_results['REQUEST'])} 条\\n")
        f.write(f"  THINK (思考): {len(all_results['THINK'])} 条\\n")
        f.write(f"  RESPONSE (回答): {len(all_results['RESPONSE'])} 条\\n")
        f.write(f"  SEARCH (搜索): {len(all_results['SEARCH'])} 条\\n\\n")
        f.write("输出文件:\\n")
        f.write(f"  REQUEST_全部内容.txt\\n")
        f.write(f"  THINK_全部内容.txt\\n")
        f.write(f"  RESPONSE_全部内容.txt\\n")
        f.write(f"  SEARCH_全部内容.txt\\n")
    
    print(f"\\n📋 汇总报告: {summary_path}")
    print(f"\\n🎉 处理完成！所有内容已转换为TXT格式！")

if __name__ == '__main__':
    process_all_sources()
"""
