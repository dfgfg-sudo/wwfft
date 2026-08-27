"""
import json
import os
from datetime import datetime

INPUT_JSON = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\DGHGH\\szedgxjfchgvjhkjgf\\deepseek_data-2026-07-03\\conversations.json'
ROOT_DIR = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd'
OUTPUT_DIR = r'd:\\sfdhdjdtysjsy\\sgdhfjasdkd\\FINAL_COZE_CONTENT_OUTPUT'

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

def get_all_js_files(root_dir):
    js_files = []
    exclude_dirs = ['COMPLETE_FINAL_OUTPUT', '.git', '__pycache__']
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for filename in filenames:
            if filename.endswith('.js') and not filename.startswith('.'):
                js_files.append(os.path.join(dirpath, filename))
    return sorted(js_files)

def main():
    print("=" * 80)
    print("🤖 最终Coze内容整合工具")
    print("📅", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    ensure_output_dir()
    
    print("\\n📂 读取conversations.json...")
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    print(f"  ✅ 共 {len(conversations)} 条对话")
    
    print("\\n📝 生成完整对话文档...")
    full_doc = os.path.join(OUTPUT_DIR, '完整对话内容_含全部提问和思考.txt')
    with open(full_doc, 'w', encoding='utf-8') as f:
        f.write("#" * 120 + "\\n")
        f.write("# 完整对话内容 - conversations.json\\n")
        f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        f.write(f"# 对话数量: {len(conversations)}\\n")
        f.write("#" * 120 + "\\n\\n")
        
        for i, conv in enumerate(conversations, 1):
            if i % 50 == 0:
                print(f"  处理对话 {i}/{len(conversations)}")
            f.write(extract_conversation_text(conv))
    print(f"  ✅ {full_doc}")
    
    print("\\n📊 生成分类文档...")
    cat_files = {}
    cat_counts = {key: 0 for key in CATEGORIES}
    
    for cat_key, cat_config in CATEGORIES.items():
        cat_file = os.path.join(OUTPUT_DIR, f"{cat_config['name']}.txt")
        cat_files[cat_key] = open(cat_file, 'w', encoding='utf-8')
        cat_files[cat_key].write("#" * 120 + "\\n")
        cat_files[cat_key].write(f"# {cat_config['name']}\\n")
        cat_files[cat_key].write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        cat_files[cat_key].write("#" * 120 + "\\n\\n")
    
    for conv in conversations:
        conv_text = extract_conversation_text(conv)
            if contains_keywords(conv_text, cat_config['keywords']):
                cat_counts[cat_key] += 1
                cat_files[cat_key].write(conv_text)
    
    for cat_key, f in cat_files.items():
        f.close()
        cat_file = os.path.join(OUTPUT_DIR, f"{CATEGORIES[cat_key]['name']}.txt")
        print(f"  ✅ {CATEGORIES[cat_key]['name']}.txt - {cat_counts[cat_key]} 条")
    
    print("\\n🔧 生成Coze IDE完整插件...")
    js_files = get_all_js_files(ROOT_DIR)
    print(f"  发现 {len(js_files)} 个JS文件")
    
    coze_plugin = os.path.join(OUTPUT_DIR, 'COZE_IDE_FULL_PLUGIN.js')
    with open(coze_plugin, 'w', encoding='utf-8') as f:
        f.write("// ============================================================\\n")
        f.write("// Coze IDE 完整插件 - Ultimate All-in-One Plugin\\n")
        f.write("// 版本: 1.0.0\\n")
        f.write(f"// 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
        f.write(f"// 合并文件数: {len(js_files)}\\n")
        f.write("// ============================================================\\n\\n")
        f.write("// ===== 包含的源文件 =====\\n")
        for i, js_file in enumerate(js_files, 1):
            f.write(f"// {i}. {os.path.relpath(js_file, ROOT_DIR)}\\n")
        f.write("// ===== 插件代码开始 =====\\n\\n")
        
            f.write("\\n" + "//" + "=" * 118 + "\\n")
            f.write(f"// FILE {i}: {os.path.relpath(js_file, ROOT_DIR)}\\n")
            f.write("//" + "=" * 118 + "\\n")
            try:
                with open(js_file, 'r', encoding='utf-8', errors='replace') as jf:
                    f.write(jf.read())
            except:
                f.write(f"// ⚠️ 文件读取错误\\n")
            f.write("\\n")
    
    print(f"  ✅ Coze IDE完整插件: {coze_plugin}")
    
    print("\\n" + "=" * 80)
    print("🎉 全部处理完成!")
    print(f"📁 输出目录: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

"""
