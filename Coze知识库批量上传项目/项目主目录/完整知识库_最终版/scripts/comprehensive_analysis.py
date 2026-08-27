"""
import json
import os
from datetime import datetime
from collections import defaultdict

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def analyze_conversations(conv_list, source_name):
    stats = {
        'source': source_name,
        'total_conversations': len(conv_list),
        'total_requests': 0,
        'total_thinks': 0,
        'total_responses': 0,
        'total_searches': 0,
        'content_chars': 0,
        'titles': [],
        'dates': [],
        'keywords': []
    }
    
    for conv in conv_list:
        if 'title' in conv:
            stats['titles'].append(conv['title'])
        
        if 'inserted_at' in conv:
            stats['dates'].append(conv['inserted_at'])
        
        mapping = conv.get('mapping', {})
        for node_id, node_data in mapping.items():
            message = node_data.get('message')
            if message is None:
                continue
            fragments = message.get('fragments', [])
            
            for fragment in fragments:
                content = fragment.get('content', '')
                stats['content_chars'] += len(content)
                
                fragment_type = fragment.get('type', '')
                if fragment_type == 'REQUEST':
                    stats['total_requests'] += 1
                elif fragment_type == 'THINK':
                    stats['total_thinks'] += 1
                elif fragment_type == 'RESPONSE':
                    stats['total_responses'] += 1
                elif fragment_type == 'SEARCH':
                    stats['total_searches'] += 1
    
    if stats['dates']:
        stats['earliest_date'] = min(stats['dates'])
        stats['latest_date'] = max(stats['dates'])
    else:
        stats['earliest_date'] = None
        stats['latest_date'] = None
    
    return stats

def compare_conversations(conv1, conv2):
    ids1 = {conv.get('id', str(i)) for i, conv in enumerate(conv1)}
    ids2 = {conv.get('id', str(i)) for i, conv in enumerate(conv2)}
    
    unique_to_0601 = ids1 - ids2
    unique_to_0606 = ids2 - ids1
    common = ids1 & ids2
    
    return {
        'unique_to_0601': len(unique_to_0601),
        'unique_to_0606': len(unique_to_0606),
        'common': len(common),
        'total_unique': len(ids1 | ids2)

def extract_key_topics(conversations, keywords_list):
    extracted = defaultdict(list)
    
    for conv in conversations:
        content = ""
            content += str(conv['title']) + " "
        
        for node_data in mapping.values():
                content += str(fragment.get('content', '')) + " "
        
        matched_topics = []
        for topic, keywords in keywords_list.items():
            for kw in keywords:
                if kw in content:
                    matched_topics.append(topic)
                    break
        
        if matched_topics:
            for topic in matched_topics:
                extracted[topic].append({
                    'id': conv.get('id'),
                    'title': conv.get('title'),
                    'date': conv.get('inserted_at')
                })
            extracted['其他'].append({
    
    return extracted

def generate_comprehensive_report(stats_0601, stats_0606, comparison, extracted_topics):
    report = "# 📊 DeepSeek数据综合分析报告\\n\\n"
    report += "## 📋 概览\\n"
    report += "本报告对两个DeepSeek数据文件进行了完整的统计分析、内容对比和主题提取。\\n\\n"
    
    report += "## 📈 数据统计\\n\\n"
    report += "### 按来源统计\\n\\n"
    report += "| 指标 | 2026-06-01 | 2026-06-06 | 总计 |\\n"
    report += "|------|------------|------------|------|\\n"
    report += f"| 对话总数 | {stats_0601['total_conversations']} | {stats_0606['total_conversations']} | {stats_0601['total_conversations'] + stats_0606['total_conversations']} |\\n"
    report += f"| 提问数 | {stats_0601['total_requests']} | {stats_0606['total_requests']} | {stats_0601['total_requests'] + stats_0606['total_requests']} |\\n"
    report += f"| 思考数 | {stats_0601['total_thinks']} | {stats_0606['total_thinks']} | {stats_0601['total_thinks'] + stats_0606['total_thinks']} |\\n"
    report += f"| 回复数 | {stats_0601['total_responses']} | {stats_0606['total_responses']} | {stats_0601['total_responses'] + stats_0606['total_responses']} |\\n"
    report += f"| 搜索数 | {stats_0601['total_searches']} | {stats_0606['total_searches']} | {stats_0601['total_searches'] + stats_0606['total_searches']} |\\n"
    report += f"| 内容字符数 | {stats_0601['content_chars']:,} | {stats_0606['content_chars']:,} | {(stats_0601['content_chars'] + stats_0606['content_chars']):,} |\\n\\n"
    
    report += "### 时间范围\\n\\n"
    report += f"- **最早日期**: {stats_0601['earliest_date'] or stats_0606['earliest_date']}\\n"
    report += f"- **最晚日期**: {stats_0601['latest_date'] or stats_0606['latest_date']}\\n\\n"
    
    report += "## 🔍 内容对比分析\\n\\n"
    report += "### 两个文件内容差异\\n\\n"
    report += "| 类别 | 数量 |\\n"
    report += "|------|------|\\n"
    report += f"| 仅在06-01中存在 | {comparison['unique_to_0601']}条 |\\n"
    report += f"| 仅在06-06中存在 | {comparison['unique_to_0606']}条 |\\n"
    report += f"| 两个文件共有 | {comparison['common']}条 |\\n"
    report += f"| 去重后总数 | {comparison['total_unique']}条 |\\n\\n"
    
    report += "## 🎯 主题分类提取\\n\\n"
    report += "根据您关注的领域，提取以下主题内容：\\n\\n"
    
    for topic, items in extracted_topics.items():
        if items and topic != '其他':
            report += f"### {topic} ({len(items)}条)\\n\\n"
            for item in items[:10]:
                report += f"- **{item['title']}** ({item['date'][:10]})\\n"
            if len(items) > 10:
                report += f"- ... 还有 {len(items) - 10} 条\\n"
            report += "\\n"
    
    report += "## 💡 用户兴趣领域匹配\\n\\n"
    report += "根据您的兴趣偏好，以下主题最相关：\\n\\n"
    report += "### 金融与赚钱\\n"
    report += "- 实时赚钱信息获取系统\\n"
    report += "- AI辅助赚钱路径解析\\n"
    report += "- 外贸赚钱信息指南\\n\\n"
    
    report += "### 自媒体与抖音\\n"
    report += "- 全能AI创作助手\\n"
    report += "- 短视频脚本生成\\n"
    report += "- 抖音视频内容提取\\n\\n"
    
    report += "### AI与科技\\n"
    report += "- 本地AI模型训练方案\\n"
    report += "- AI编程工具与趋势\\n"
    report += "- 人工智能技术集成\\n\\n"
    
    report += "### 认知与提升\\n"
    report += "- AI时代个人发展指南\\n"
    report += "- 情商提升与为人处世\\n"
    report += "- 思维格局与财商培养\\n\\n"
    
    return report

def main():
    base_dir = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\merged_output'
    
    conv1 = load_json(os.path.join(base_dir, 'extract_0601', 'conversations.json')) or []
    conv2 = load_json(os.path.join(base_dir, 'extract_0606', 'conversations.json')) or []
    
    stats_0601 = analyze_conversations(conv1, '2026-06-01')
    stats_0606 = analyze_conversations(conv2, '2026-06-06')
    
    comparison = compare_conversations(conv1, conv2)
    
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
    
    all_conversations = conv1 + conv2
    extracted_topics = extract_key_topics(all_conversations, keywords_list)
    
    report = generate_comprehensive_report(stats_0601, stats_0606, comparison, extracted_topics)
    
    report_path = os.path.join(base_dir, '综合分析报告_完整版.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"综合分析报告已生成: {report_path}")
    print(f"\\n📊 统计摘要:")
    print(f"  总对话数: {stats_0601['total_conversations'] + stats_0606['total_conversations']}")
    print(f"  总提问数: {stats_0601['total_requests'] + stats_0606['total_requests']}")
    print(f"  总思考数: {stats_0601['total_thinks'] + stats_0606['total_thinks']}")
    print(f"  总回复数: {stats_0601['total_responses'] + stats_0606['total_responses']}")
    print(f"  时间范围: {stats_0601['earliest_date'] or stats_0606['earliest_date']} 至 {stats_0601['latest_date'] or stats_0606['latest_date']}")

if __name__ == '__main__':
    main()
"""
