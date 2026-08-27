"""
import json
import os
from collections import defaultdict

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载文件失败 {filepath}: {e}")
        return None

def process_conversation(conv):
    \"\"\"处理单条对话，提取问答对\"\"\"
    qa_pairs = []
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
            if ftype == 'REQUEST' and content:
                qa_pairs.append({
                    'type': 'question',
                    'content': content
                })
            elif ftype == 'RESPONSE' and content:
                    'type': 'answer',
    
    return {
        'id': conv_id,
        'title': title,
        'date': date[:10] if date else '',
        'qa_pairs': qa_pairs
    }

def main():
    print("🚀 开始按主题处理DeepSeek对话...")
    
    base_dir = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\merged_output'
    
    conv1 = load_json(os.path.join(base_dir, 'extract_0601', 'conversations.json')) or []
    conv2 = load_json(os.path.join(base_dir, 'extract_0606', 'conversations.json')) or []
    
    all_conversations = conv1 + conv2
    print(f"📥 已加载 {len(all_conversations)} 条对话")
    
    processed = []
    for i, conv in enumerate(all_conversations, 1):
        if i % 100 == 0:
            print(f"⏳ 已处理 {i}/{len(all_conversations)} 条对话")
        
        processed_conv = process_conversation(conv)
        if processed_conv['qa_pairs']:
            processed.append(processed_conv)
    
    print(f"✨ 提取到 {len(processed)} 条有效对话")
    
    output_data = {
        'total_conversations': len(all_conversations),
        'valid_conversations': len(processed),
        'data': processed
    
    json_path = os.path.join(base_dir, '主题处理结果.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"📊 JSON数据已保存: {json_path}")
    
    md_path = os.path.join(base_dir, '主题处理报告.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# 📚 主题对话处理报告\\n\\n")
        f.write(f"## 统计\\n")
        f.write(f"- 总对话数: {len(all_conversations)}\\n")
        f.write(f"- 有效对话数: {len(processed)}\\n\\n")
        f.write("## 对话内容\\n\\n")
        
        for conv in processed[:50]:
            f.write(f"### {conv['title']}\\n")
            f.write(f"**日期**: {conv['date']}\\n\\n")
            
            for qa in conv['qa_pairs']:
                if qa['type'] == 'question':
                    f.write(f"**提问**: {qa['content'][:200]}...\\n\\n")
                else:
                    f.write(f"**回答**: {qa['content'][:500]}...\\n\\n")
            f.write("---\\n\\n")
    
    print(f"📄 报告已保存: {md_path}")
    print(f"\\n🎉 处理完成！")

if __name__ == '__main__':
    main()
"""
