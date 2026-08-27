"""
﻿import os
import json

base_dir = r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd\\新建文件夹"
txt_dir = os.path.join(base_dir, "FINAL_OUTPUT")
json_dir = os.path.join(base_dir, "merged_output")

topic_mapping = {
    "AI人工智能": "AI人工智能",
    "医疗健康": "医疗健康", 
    "国学文化": "国学文化",
    "地理知识": "地理知识",
    "情商为人处世": "情商为人处世",
    "新闻时事": "新闻时事",
    "时代社会热点": "时代社会热点",
    "法律法规": "法律法规",
    "科技前沿": "科技前沿",
    "自媒体抖音视频": "自媒体抖音视频",
    "认知提升": "认知提升",
    "识人读心": "识人读心",
    "金融赚钱": "金融赚钱创业"
}

for txt_topic, json_topic in topic_mapping.items():
    txt_path = os.path.join(txt_dir, f"兴趣_{txt_topic}.txt")
    json_path = os.path.join(json_dir, f"{json_topic}.json")
    
    if os.path.exists(txt_path):
        try:
            with open(txt_path, 'r', encoding='gbk', errors='ignore') as f:
                content = f.read()
            
            lines = content.strip().split('\\n')
            items = []
            current_item = {}
            for line in lines:
                line = line.strip()
                if line.startswith('===='):
                    if current_item:
                        items.append(current_item)
                elif line and not line.startswith('='):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        current_item[key.strip()] = value.strip()
                    else:
                        if 'content' in current_item:
                            current_item['content'] += '\\n' + line
                            current_item['content'] = line
            
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            
            print(f"已处理: {json_topic}.json ({len(items)} 条)")
        except Exception as e:
            print(f"处理 {txt_topic} 时出错: {e}")

print("\\\\n处理完成！")

"""
