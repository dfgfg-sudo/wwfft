"""
import json
import os
from collections import defaultdict

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def extract_conversation_data(conversations):
    \"\"\"提取所有对话中的提问、思考和回答\"\"\"
    all_data = []
    
    for conv in conversations:
        conv_id = conv.get('id', '')
        title = conv.get('title', '')
        date = conv.get('inserted_at', '')
        
        mapping = conv.get('mapping', {})
        conversation_flow = []
        
        for node_id, node_data in mapping.items():
            message = node_data.get('message')
            if message is None:
                continue
            
            fragments = message.get('fragments', [])
            for fragment in fragments:
                fragment_type = fragment.get('type', '')
                content = fragment.get('content', '')
                
                if content.strip():
                    conversation_flow.append({
                        'type': fragment_type,
                        'content': content
                    })
        
        if conversation_flow:
            all_data.append({
                'id': conv_id,
                'title': title,
                'date': date,
                'flow': conversation_flow
    
    return all_data

def generate_qa_pairs(conversation_data):
    \"\"\"生成问答对\"\"\"
    qa_pairs = []
    
    for conv in conversation_data:
        questions = []
        answers = []
        thinks = []
        
        for item in conv['flow']:
            if item['type'] == 'REQUEST':
                questions.append(item['content'])
            elif item['type'] == 'RESPONSE':
                answers.append(item['content'])
            elif item['type'] == 'THINK':
                thinks.append(item['content'])
        
        if questions:
            for i, question in enumerate(questions):
                answer = answers[i] if i < len(answers) else ""
                think = thinks[i] if i < len(thinks) else ""
                
                qa_pairs.append({
                    'id': conv['id'],
                    'title': conv['title'],
                    'date': conv['date'],
                    'question': question.strip(),
                    'think': think.strip(),
                    'answer': answer.strip()
    
    return qa_pairs

def categorize_qa_pairs(qa_pairs, keywords_list):
    \"\"\"按主题分类问答对\"\"\"
    categorized = defaultdict(list)
    
    for qa in qa_pairs:
        content = qa['question'] + ' ' + qa['answer'] + ' ' + qa['title']
        matched_topics = []
        
        for topic, keywords in keywords_list.items():
            for kw in keywords:
                if kw in content:
                    matched_topics.append(topic)
                    break
        
        if matched_topics:
            for topic in matched_topics:
                categorized[topic].append(qa)
        else:
            categorized['其他'].append(qa)
    
    return categorized

def generate_final_report(categorized_qa, keywords_list):
    \"\"\"生成完整的最终报告\"\"\"
    report = "# 📚 DeepSeek对话内容完整整理报告\\n\\n"
    report += "## 概述\\n"
    report += "本报告对两个DeepSeek数据文件中的所有对话进行了完整整理，提取了所有提问和回答，并按照主题进行分类。\\n\\n"
    
    total_qa = sum(len(items) for items in categorized_qa.values())
    report += f"### 统计概览\\n"
    report += f"- 总问答对数: {total_qa}\\n"
    report += f"- 主题分类数: {len(categorized_qa)}\\n\\n"
    
    report += "## 🎯 主题分类内容\\n\\n"
    
    for topic in keywords_list.keys():
        if topic in categorized_qa and categorized_qa[topic]:
            qa_list = categorized_qa[topic]
            report += f"### {topic} ({len(qa_list)}条)\\n\\n"
            
            for i, qa in enumerate(qa_list, 1):
                report += f"#### {i}. {qa['title'] or '无标题'}\\n"
                report += f"**提问:** {qa['question'][:500]}...\\n\\n"
                
                if qa['answer']:
                    report += f"**回答:** {qa['answer'][:1000]}...\\n\\n"
                    report += f"**回答:** （自动生成中）\\n\\n"
                
                if qa['think']:
                    report += f"**思考:** {qa['think'][:500]}...\\n\\n"
                
                report += "---\\n\\n"
    
    return report

def main():
    base_dir = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\merged_output'
    
    conv1 = load_json(os.path.join(base_dir, 'extract_0601', 'conversations.json')) or []
    conv2 = load_json(os.path.join(base_dir, 'extract_0606', 'conversations.json')) or []
    
    all_conversations = conv1 + conv2
    
    conversation_data = extract_conversation_data(all_conversations)
    
    qa_pairs = generate_qa_pairs(conversation_data)
    
    keywords_list = {
        '金融赚钱创业': ['金融', '赚钱', '创业', '投资', '理财', '股票', '基金', '财富', '经济', '商业'],
        '自媒体抖音视频': ['自媒体', '抖音', '视频', '创作', '运营', '流量', '变现', '直播', '短视频'],
        'AI人工智能': ['AI', '人工智能', '模型', '机器人', '机器学习', '深度学习', '大模型'],
        '时代社会热点': ['时代', '社会', '热点', '趋势', '科技', '发展', '变革'],
        '情商为人处世': ['情商', '为人处世', '沟通', '职场', '人际关系', '说话', '表达'],
        '国学文化': ['国学', '文化', '传统', '经典', '历史', '哲学'],
        '新闻时事': ['新闻', '时事', '政治', '国际', '局势'],
        '地理知识': ['地理', '地图', '旅行', '城市', '自然'],
        '法律法规': ['法律', '法规', '合同', '权益', '维权'],
        '识人读心': ['识人', '读心', '心理学', '性格', '心理效应'],
        '认知提升': ['认知', '思维', '格局', '眼界', '学习', '成长'],
        '医疗健康': ['医疗', '健康', '养生', '疾病'],
        '科技前沿': ['科技', '前沿', '技术', '创新', '互联网']
    }
    
    categorized_qa = categorize_qa_pairs(qa_pairs, keywords_list)
    
    report = generate_final_report(categorized_qa, keywords_list)
    
    report_path = os.path.join(base_dir, '完整问答整理报告.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    qa_json_path = os.path.join(base_dir, '问答对集合.json')
    with open(qa_json_path, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完整问答整理报告已生成: {report_path}")
    print(f"✅ 问答对集合已保存: {qa_json_path}")
    print(f"✅ 共处理 {len(qa_pairs)} 个问答对")

if __name__ == '__main__':
    main()
"""
