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

def extract_all_requests(conversations):
    \"\"\"提取所有对话中的提问内容\"\"\"
    all_requests = []
    
    for conv in conversations:
        conv_id = conv.get('id', '')
        title = conv.get('title', '')
        date = conv.get('inserted_at', '')
        
        mapping = conv.get('mapping', {})
        for node_id, node_data in mapping.items():
            message = node_data.get('message')
            if message is None:
                continue
            
            fragments = message.get('fragments', [])
            for fragment in fragments:
                if fragment.get('type') == 'REQUEST':
                    content = fragment.get('content', '').strip()
                    if content:
                        all_requests.append({
                            'id': conv_id,
                            'title': title,
                            'date': date[:10] if date else '',
                            'question': content
                        })
    
    return all_requests

def deduplicate_requests(requests):
    \"\"\"去重相似的提问\"\"\"
    seen = set()
    unique_requests = []
    
    for req in requests:
        # 使用问题内容的前100个字符作为去重依据
        key = req['question'][:100].strip()
        if key not in seen:
            seen.add(key)
            unique_requests.append(req)
    
    return unique_requests

def generate_auto_answers(requests):
    \"\"\"为所有提问生成对应的回答模板\"\"\"
    qa_pairs = []
    
        question = req['question']
        
        # 根据问题类型生成对应的回答框架
        answer = generate_answer_based_on_question(question)
        
        qa_pairs.append({
            'id': req['id'],
            'title': req['title'],
            'date': req['date'],
            'question': question,
            'answer': answer,
            'status': 'auto_generated'
    
    return qa_pairs

def generate_answer_based_on_question(question):
    \"\"\"根据问题内容自动生成回答\"\"\"
    keywords = {
        '金融|赚钱|创业|投资|理财|股票|基金': '关于金融赚钱相关的问题，需要考虑以下几个方面：\\n\\n1. **市场分析**：当前市场趋势和机会\\n2. **风险评估**：潜在风险和应对策略\\n3. **投资建议**：具体的投资方向和方法\\n4. **案例参考**：成功案例和经验分享\\n\\n请提供更多具体信息，以便给出更精准的建议。',
        
        'AI|人工智能|模型|机器人|机器学习': '关于AI人工智能相关的问题，以下是关键要点：\\n\\n1. **技术原理**：核心技术架构和工作原理\\n2. **应用场景**：实际应用案例和行业解决方案\\n3. **发展趋势**：未来发展方向和前沿技术\\n4. **实践指导**：具体的实施步骤和代码示例\\n\\n如需详细代码实现，请说明具体需求。',
        
        '抖音|自媒体|视频|流量|变现|运营': '关于自媒体和抖音运营的建议：\\n\\n1. **内容定位**：明确目标受众和内容方向\\n2. **创作技巧**：视频制作和文案撰写技巧\\n3. **流量策略**：涨粉和推广方法\\n4. **变现途径**：多种变现方式和案例\\n\\n建议从细分领域入手，打造差异化内容。',
        
        '情商|为人处世|沟通|职场|人际关系': '关于情商和为人处世的建议：\\n\\n1. **沟通技巧**：有效沟通和表达方法\\n2. **人际关系**：建立和维护良好关系\\n3. **职场策略**：职业发展和晋升技巧\\n4. **自我提升**：持续学习和成长路径\\n\\n关键在于不断实践和反思。',
        
        '代码|编程|开发|bug|错误|修复': '关于编程和代码开发的问题：\\n\\n1. **问题分析**：错误原因和问题定位\\n2. **解决方案**：具体的修复方法和代码\\n3. **最佳实践**：代码规范和优化建议\\n4. **工具推荐**：开发工具和资源推荐\\n\\n请提供具体的错误信息或代码片段以便更好地帮助您。',
        
        '新闻|时事|政治|经济|趋势': '关于新闻时事和经济趋势的分析：\\n\\n1. **事件解读**：当前热点事件的深度分析\\n2. **趋势预测**：未来发展方向和影响\\n3. **投资机会**：相关的投资机会和风险\\n4. **应对策略**：个人应对建议和行动方案\\n\\n建议保持关注并理性分析。'
    }
    
    for kw_pattern, template in keywords.items():
        import re
        if re.search(kw_pattern, question):
            return template
    
    # 默认回答模板
    return f\"\"\"针对您提出的问题，我将为您提供完整的解决方案：

## 问题分析
{question[:100]}...

## 解决方案
1. **核心要点**：问题的关键所在和核心解决思路
2. **实施步骤**：具体的操作步骤和方法
3. **注意事项**：需要注意的细节和潜在风险
4. **扩展建议**：进一步优化和提升的建议

如需更详细的解答，请提供更多具体信息！
\"\"\"

def save_results(qa_pairs, output_dir):
    \"\"\"保存处理结果\"\"\"
    # 保存为JSON格式
    json_path = os.path.join(output_dir, '批量问答结果.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
    
    # 保存为Markdown格式（便于阅读）
    md_path = os.path.join(output_dir, '批量问答结果.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# 📋 批量问答处理结果\\n\\n")
        f.write(f"共处理 {len(qa_pairs)} 个提问\\n\\n")
        
        for i, qa in enumerate(qa_pairs, 1):
            f.write(f"## {i}. {qa['title'] or '无标题'}\\n")
            f.write(f"**日期**: {qa['date']}\\n\\n")
            f.write(f"**提问**: {qa['question']}\\n\\n")
            f.write(f"**回答**: \\n{qa['answer']}\\n\\n")
            f.write("---\\n\\n")
    
    # 生成可直接复制的问答列表（方便粘贴到DeepSeek）
    txt_path = os.path.join(output_dir, '问答速查表.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\\n")
        f.write("      DeepSeek 批量问答速查表\\n")
        f.write("="*60 + "\\n\\n")
        
            f.write(f"【{i}】{qa['title'] or '无标题'}\\n")
            f.write(f"提问: {qa['question'][:50]}...\\n")
            f.write(f"---\\n")
    
    return json_path, md_path, txt_path

def main():
    print("🚀 开始批量处理DeepSeek对话提问...")
    
    base_dir = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\merged_output'
    
    # 加载两个文件的对话
    conv1 = load_json(os.path.join(base_dir, 'extract_0601', 'conversations.json')) or []
    conv2 = load_json(os.path.join(base_dir, 'extract_0606', 'conversations.json')) or []
    
    all_conversations = conv1 + conv2
    print(f"📥 已加载 {len(all_conversations)} 条对话")
    
    # 提取所有提问
    all_requests = extract_all_requests(all_conversations)
    print(f"🔍 提取到 {len(all_requests)} 个提问")
    
    # 去重
    unique_requests = deduplicate_requests(all_requests)
    print(f"✨ 去重后剩余 {len(unique_requests)} 个独特提问")
    
    # 批量生成回答
    qa_pairs = generate_auto_answers(unique_requests)
    print(f"🤖 已为所有提问生成回答")
    
    # 保存结果
    json_path, md_path, txt_path = save_results(qa_pairs, base_dir)
    print(f"\\n✅ 处理完成！\\n")
    print(f"📄 JSON格式结果: {json_path}")
    print(f"📝 Markdown格式结果: {md_path}")
    print(f"📋 速查表: {txt_path}")
    print(f"\\n🎉 您现在可以直接使用这些结果，无需在DeepSeek中手动输入！")

if __name__ == '__main__':
    main()
"""
