"""
import os
import json
import re
from datetime import datetime
from pathlib import Path

def read_file_content(filepath):
    try:
        if filepath.suffix == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif filepath.suffix in ['.txt', '.md']:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        else:
            return None
    except Exception as e:
        print(f"读取文件失败 {filepath}: {e}")

def extract_conversations_from_topics(topics_data):
    conversations = []
    for topic in topics_data:
        if 'messages' in topic:
            conversation = {
                'id': topic.get('id', ''),
                'title': topic.get('title', ''),
                'inserted_at': topic.get('inserted_at', ''),
                'updated_at': topic.get('updated_at', ''),
                'message_count': topic.get('message_count', 0),
                'messages': topic['messages']
            }
            conversations.append(conversation)
    return conversations

def merge_requests_responses_thinks(requests, responses, thinks):
    all_messages = {}
    
    for msg in requests:
        key = f"{msg['conversation_id']}_{msg['node_id']}"
        all_messages[key] = msg
    
    for msg in responses:
    
    for msg in thinks:
    
    return list(all_messages.values())

def process_large_txt_files(txt_files):
    categorized_content = {}
    for filepath in txt_files:
        category = filepath.stem.replace('兴趣_', '')
        content = read_file_content(filepath)
        if content:
            categorized_content[category] = content
    return categorized_content

def main():
    base_dir = Path('d:/sfdhdjdtysjsy/sgdhfjasdkd')
    output_dir = base_dir / 'KNOWLEDGE_BASE_OUTPUT'
    output_dir.mkdir(exist_ok=True)
    
    knowledge_base = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'source_directory': str(base_dir),
            'version': '1.0.0'
        },
        'conversations': [],
        'messages': [],
        'categorized_content': {},
        'reports': [],
        'plugins': [],
        'code_snippets': [],
        'statistics': {}
    
    data_dir = base_dir / '数据文件'
    if data_dir.exists():
        print("读取数据文件目录...")
        
        topics_file = data_dir / 'ALL_TOPICS_COMPLETE.json'
        if topics_file.exists():
            topics_data = read_file_content(topics_file)
            if topics_data:
                knowledge_base['conversations'] = extract_conversations_from_topics(topics_data)
                print(f"已读取 {len(knowledge_base['conversations'])} 个对话")
        
        requests_file = data_dir / 'ALL_REQUESTS_COMPLETE.json'
        responses_file = data_dir / 'ALL_RESPONSES_COMPLETE.json'
        thinks_file = data_dir / 'ALL_THINKS_COMPLETE.json'
        
        requests_data = read_file_content(requests_file) if requests_file.exists() else []
        responses_data = read_file_content(responses_file) if responses_file.exists() else []
        thinks_data = read_file_content(thinks_file) if thinks_file.exists() else []
        
        knowledge_base['messages'] = merge_requests_responses_thinks(requests_data, responses_data, thinks_data)
        print(f"已合并 {len(knowledge_base['messages'])} 条消息")
        
        final_content_file = data_dir / 'FINAL_COMPLETE_CONTENT.txt'
        if final_content_file.exists():
            knowledge_base['full_text_content'] = read_file_content(final_content_file)
        
        statistics_file = data_dir / 'STATISTICS_REPORT.json'
        if statistics_file.exists():
            knowledge_base['statistics'] = read_file_content(statistics_file)
    
    final_output_dir = base_dir / '新建文件夹' / 'FINAL_OUTPUT'
    if final_output_dir.exists():
        print("读取FINAL_OUTPUT目录...")
        txt_files = list(final_output_dir.glob('兴趣_*.txt'))
        knowledge_base['categorized_content'] = process_large_txt_files(txt_files)
        print(f"已读取 {len(knowledge_base['categorized_content'])} 个分类内容")
    
    merged_output_dir = base_dir / '新建文件夹' / 'merged_output'
    if merged_output_dir.exists():
        print("读取merged_output目录...")
        json_files = list(merged_output_dir.glob('*.json'))
        for json_file in json_files:
            content = read_file_content(json_file)
                category = json_file.stem
                knowledge_base['categorized_content'][category] = content
        
        md_files = list(merged_output_dir.glob('*.md'))
        for md_file in md_files:
            content = read_file_content(md_file)
                knowledge_base['reports'].append({
                    'filename': md_file.name,
                    'content': content
                })
    
    plugins_dir = base_dir / '新建文件夹' / 'plugins'
    if plugins_dir.exists():
        print("读取plugins目录...")
        plugin_files = list(plugins_dir.glob('*.js'))
        for plugin_file in plugin_files:
            content = read_file_content(plugin_file)
                knowledge_base['plugins'].append({
                    'filename': plugin_file.name,
    
    source_data_dir = base_dir / '新建文件夹' / 'source_data'
    if source_data_dir.exists():
        print("读取source_data目录...")
        txt_files = list(source_data_dir.rglob('*.txt'))
        for txt_file in txt_files:
            content = read_file_content(txt_file)
                knowledge_base['code_snippets'].append({
                    'filename': txt_file.name,
    
    unified_dir = base_dir / '新建文件夹' / 'UNIFIED_MERGED_DATA'
    if unified_dir.exists():
        print("读取UNIFIED_MERGED_DATA目录...")
        conversations_file = unified_dir / 'all_conversations.json'
        if conversations_file.exists():
            content = read_file_content(conversations_file)
                knowledge_base['unified_conversations'] = content
    
    output_file = output_dir / 'COMPLETE_KNOWLEDGE_BASE.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    
    output_txt_file = output_dir / 'COMPLETE_KNOWLEDGE_BASE.txt'
    with open(output_txt_file, 'w', encoding='utf-8') as f:
        f.write(f"====================================================================================================\\n")
        f.write(f"              DeepSeek 完整知识库 - 生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        f.write(f"\\n【元数据统计】\\n")
        f.write(f"- 对话总数: {len(knowledge_base['conversations'])}\\n")
        f.write(f"- 消息总数: {len(knowledge_base['messages'])}\\n")
        f.write(f"- 分类内容数: {len(knowledge_base['categorized_content'])}\\n")
        f.write(f"- 报告数: {len(knowledge_base['reports'])}\\n")
        f.write(f"- 插件数: {len(knowledge_base['plugins'])}\\n")
        f.write(f"\\n====================================================================================================\\n")
        f.write(f"\\n【分类内容列表】\\n")
        for category in knowledge_base['categorized_content'].keys():
            f.write(f"- {category}\\n")
    
    print(f"\\n知识库生成完成！")
    print(f"- JSON格式: {output_file}")
    print(f"- TXT格式: {output_txt_file}")
    print(f"- 对话数: {len(knowledge_base['conversations'])}")
    print(f"- 消息数: {len(knowledge_base['messages'])}")
    print(f"- 分类内容: {len(knowledge_base['categorized_content'])}")
    print(f"- 报告数: {len(knowledge_base['reports'])}")
    print(f"- 插件数: {len(knowledge_base['plugins'])}")

if __name__ == '__main__':
    main()
"""
