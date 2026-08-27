"""
import json
import os
import re

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_text(content, filepath):
        f.write(content)

def merge_conversations(file1, file2):
    conv1 = load_json(file1)
    conv2 = load_json(file2)
    
    if not conv1:
        conv1 = []
    if not conv2:
        conv2 = []
    
    merged = []
    seen_ids = set()
    
    for conv in conv1:
        conv_id = conv.get('id', str(len(merged)))
        if conv_id not in seen_ids:
            seen_ids.add(conv_id)
            merged.append(conv)
    
    for conv in conv2:
    
    print(f"Merged {len(conv1)} + {len(conv2)} = {len(merged)} conversations")
    return merged

def extract_topics(conversations):
    keywords = {
        '金融赚钱创业': ['金融', '赚钱', '创业', '投资', '理财', '股票', '基金', '财富', '经济', '商业'],
        '自媒体抖音视频': ['自媒体', '抖音', '视频', '创作', '运营', '流量', '变现', '直播', '短视频'],
        'AI人工智能': ['AI', '人工智能', '模型', '机器人', '机器学习', '深度学习', '大模型'],
        '时代社会热点': ['时代', '社会', '热点', '趋势', '科技', '发展', '变革'],
        '情商为人处世': ['情商', '为人处世', '沟通', '职场', '人际关系', '说话', '表达'],
        '国学文化': ['国学', '文化', '传统', '经典', '历史', '哲学'],
        '新闻时事': ['新闻', '时事', '政治', '国际', '局势', '热点事件'],
        '地理知识': ['地理', '地图', '旅行', '城市', '自然', '环境'],
        '法律法规': ['法律', '法规', '合同', '权益', '维权', '合规'],
        '识人读心': ['识人', '读心', '心理学', '性格', '心理效应', '微表情'],
        '认知提升': ['认知', '思维', '格局', '眼界', '学习', '成长'],
        '医疗健康': ['医疗', '健康', '养生', '疾病', '体检', '保健'],
        '科技前沿': ['科技', '前沿', '技术', '创新', '互联网', '数字化']
    }
    
    extracted = {topic: [] for topic in keywords}
    extracted['其他'] = []
    
    for conv in conversations:
        content = ""
        if 'content' in conv:
            content += str(conv['content'])
        if 'summary' in conv:
            content += str(conv.get('summary', ''))
        if 'title' in conv:
            content += str(conv.get('title', ''))
        
        matched = False
        for topic, kw_list in keywords.items():
            for kw in kw_list:
                if kw in content:
                    extracted[topic].append(conv)
                    matched = True
                    break
        
        if not matched:
            extracted['其他'].append(conv)
    
    return extracted

def generate_report(extracted, output_dir):
    report = "# 完整内容合并与主题提取报告\\n\\n"
    report += "## 概述\\n"
    report += "本报告对两个DeepSeek数据文件进行了完整合并，并按照用户兴趣主题进行了分类提取。\\n\\n"
    
    total_count = sum(len(items) for items in extracted.values())
    report += f"### 数据统计\\n"
    report += f"- 合并后总对话数: {total_count}\\n\\n"
    
    report += "## 主题分类详情\\n\\n"
    
    for topic, items in extracted.items():
        if items:
            report += f"### {topic} ({len(items)}条)\\n\\n"
            for i, item in enumerate(items[:5], 1):
                title = item.get('title', '无标题')
                summary = item.get('summary', '')[:200]
                report += f"{i}. **{title}**\\n"
                if summary:
                    report += f"   {summary}...\\n\\n"
            if len(items) > 5:
                report += f"   ... 还有 {len(items) - 5} 条内容\\n\\n"
    
    save_text(report, os.path.join(output_dir, '主题提取报告.md'))
    return report

def main():
    base_dir = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\merged_output'
    conv1_path = os.path.join(base_dir, 'extract_0601', 'conversations.json')
    conv2_path = os.path.join(base_dir, 'extract_0606', 'conversations.json')
    
    print("正在合并对话数据...")
    merged = merge_conversations(conv1_path, conv2_path)
    
    merged_path = os.path.join(base_dir, 'merged_conversations.json')
    save_json(merged, merged_path)
    print(f"合并后的对话已保存到: {merged_path}")
    
    print("正在提取主题内容...")
    extracted = extract_topics(merged)
    
        topic_path = os.path.join(base_dir, f'{topic}.json')
        save_json(items, topic_path)
        print(f"{topic}: {len(items)} 条，已保存到: {topic_path}")
    
    print("正在生成报告...")
    report = generate_report(extracted, base_dir)
    print("报告已生成完成！")
    

if __name__ == '__main__':
    main()
"""
