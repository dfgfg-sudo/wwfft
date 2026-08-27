"""
import json
import os
from datetime import datetime

INPUT_JSON = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\deepseek_data-2026-07-03\\conversations.json'
OUTPUT_DIR = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\final_comprehensive'

FILES_TO_MERGE = [
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\新建文本文档 - 副本.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\新建文本文档 (2).txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\新建文本文档 (3).txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\新建文本文档 (4).txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\新建文本文档 (5).txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\新建文本文档 (6).txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\新建文本文档.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\reyjcukfjhb.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\sfghgfrhsdtf.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\zdxfkaredtrddfcg - 副本.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\zdxfkaredtrddfcg.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\抖音存储.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\新建文本文档 - 副本.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\新建文本文档 (2).txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\新建文本文档 (3).txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\新建文本文档 (4).txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\新建文本文档 (5).txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\新建文本文档 (6).txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\新建文本文档.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\赚钱、创业与财富认知相关.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\dsfdgfhgjh.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\fgdhfggtfk.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\reyjcukfjhb - 副本.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\reyjcukfjhb.txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\wertyfkuyfd (2).txt',
    r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\wertyfkuyfd.txt'
]

CATEGORIES = {
    'ai_training': {
        'name': 'AI模型与训练相关',
        'keywords': ['AI', '人工智能', '模型训练', '训练模型', 'LoRA', 'QLoRA', '微调', 
                     'fine-tuning', 'finetune', '数据集', '数据处理', 'Transformer', 
                     '大语言模型', 'LLM', 'GPT', 'DeepSeek', '模型', '训练', '推理', 
                     'embedding', '向量数据库', 'Pinecone', 'Weaviate', '知识蒸馏', 
                     '强化学习', 'RLHF', '自监督学习', '预训练', '量化', '压缩', 
                     '模型部署', '推理优化', 'CUDA', 'GPU', 'PyTorch', 'TensorFlow',
                     'Cherry Studio', '代码训练', '数据投喂', '模型架构', '超智能']
    },
    'coze': {
        'name': 'Coze相关',
        'keywords': ['Coze', 'coze', '插件', '工作流', '节点', 'OpenAPI', '工作流自动化',
                     '插件开发', 'Coze平台', 'Coze IDE', 'MCP', 'Modular Control Plane',
                     '节点配置', '工作流配置', '插件代码', '工作流引擎', '自动化修复',
                     'API集成', '插件生成', '工作流设计', '代码生成器', '智能诊断',
                     'JSON修复', 'Invalid params', 'coze-cli', '代码验证', '缓存策略',
                     '并发处理', '错误诊断', '监控告警', '性能优化']
    'finance': {
        'name': '金融赚钱自媒体抖音相关',
        'keywords': ['金融', '赚钱', '自媒体', '抖音', '视频', '制作', '理财', '基金',
                     '经济', '商业', '创业', '财富', '投资', '股票', '股市', '财经',
                     '现金', '收入', '副业', '电商', '直播', '带货', '短视频',
                     '流量', '变现', '运营', '自媒体运营', '抖音运营', '视频制作',
                     '内容创作', '网红', 'IP打造', '品牌', '营销', '私域', '社群',
                     '商业思维', '商业模式', '现金流', '资产', '负债', '财务自由',
                     '经济周期', '趋势', '风口', '红利', '机会']
    }

def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def contains_keywords(text, keywords):
    text_lower = text.lower()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            return True
    return False

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
            continue
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

def main():
    print("=" * 80)
    print("🤖 最终综合合并工具")
    print("📅", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    ensure_output_dir()
    
    main_output = os.path.join(OUTPUT_DIR, '最终完整合并文档.txt')
    
    print("\\n📝 开始生成最终合并文档...")
    
    with open(main_output, 'w', encoding='utf-8') as out_f:
        out_f.write("#" * 120 + "\\n")
        out_f.write("# 最终完整合并文档 - COMPREHENSIVE MERGED DOCUMENT\\n")
        out_f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        out_f.write("# 内容包含: conversations.json + 26个TXT文件\\n")
        out_f.write("#" * 120 + "\\n\\n")
        
        print("\\n📂 第一部分: conversations.json (含REQUEST/THINK/RESPONSE)")
        with open(INPUT_JSON, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
        
        print(f"  共 {len(conversations)} 条对话")
        out_f.write("# 第一部分: conversations.json\\n")
        out_f.write(f"# 对话数量: {len(conversations)}\\n")
        
        for i, conv in enumerate(conversations, 1):
            if i % 50 == 0:
                print(f"  处理对话 {i}/{len(conversations)}")
            conv_text = extract_conversation_text(conv)
            out_f.write(conv_text)
        
        print("\\n📂 第二部分: 26个TXT文件")
        out_f.write("\\n" + "#" * 120 + "\\n")
        out_f.write("# 第二部分: TXT文件内容\\n")
        out_f.write(f"# 文件数量: {len(FILES_TO_MERGE)}\\n")
        
        for i, filepath in enumerate(FILES_TO_MERGE, 1):
            filename = os.path.basename(filepath)
            
            if not os.path.exists(filepath):
                print(f"  ❌ [{i}] 文件不存在: {filename}")
                out_f.write("\\n" + "=" * 120 + "\\n")
                out_f.write(f"# FILE: {filename} (文件不存在)\\n")
                out_f.write("=" * 120 + "\\n")
                out_f.write("⚠️ 文件不存在\\n")
                out_f.write("\\n" + "=" * 120 + "\\n\\n")
            
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            if not content.strip():
                print(f"  ⚠️ [{i}] 空文件: {filename}")
            
            print(f"  ✅ [{i}] {filename} ({len(content):,} 字符)")
            
            out_f.write(f"# FILE: {filepath}\\n")
            out_f.write(f"# SIZE: {len(content):,} 字符\\n")
            out_f.write(content)
    
    output_size = os.path.getsize(main_output)
    print(f"\\n✅ 最终合并文档: {main_output} ({output_size / 1024 / 1024:.2f} MB)")
    
    print("\\n📊 生成分类文档...")
    
    cat_files = {}
    cat_counts = {key: 0 for key in CATEGORIES}
    
    for cat_key, cat_config in CATEGORIES.items():
        cat_file = os.path.join(OUTPUT_DIR, f"{cat_config['name']}.txt")
        f = open(cat_file, 'w', encoding='utf-8')
        f.write("#" * 120 + "\\n")
        f.write(f"# {cat_config['name']}\\n")
        f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        f.write("#" * 120 + "\\n\\n")
        cat_files[cat_key] = f
    
    for i, conv in enumerate(conversations):
        
            if contains_keywords(conv_text, cat_config['keywords']):
                cat_counts[cat_key] += 1
                cat_files[cat_key].write(conv_text)
    
    for cat_key, f in cat_files.items():
        f.close()
        cat_file = os.path.join(OUTPUT_DIR, f"{CATEGORIES[cat_key]['name']}.txt")
        file_size = os.path.getsize(cat_file)
        print(f"  ✅ {CATEGORIES[cat_key]['name']}.txt ({file_size / 1024 / 1024:.2f} MB) - {cat_counts[cat_key]} 条")
    
    print("\\n" + "=" * 80)
    print("🎉 全部处理完成!")
    print(f"📁 输出目录: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

"""
