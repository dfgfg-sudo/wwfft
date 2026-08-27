"""
import os
import json
import shutil
from collections import defaultdict

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

def load_txt(filepath):
            return f.read()
        return ""

def save_txt(content, filepath):
        f.write(content)

def merge_conversations(all_files):
    merged = []
    seen_ids = set()
    for filepath in all_files:
        data = load_json(filepath)
        if data:
            for item in data:
                if isinstance(item, dict):
                    item_id = item.get('id', item.get('conversation_id', item.get('uuid', str(item))))
                    if item_id not in seen_ids:
                        seen_ids.add(item_id)
                        merged.append(item)
                else:
                    item_str = json.dumps(item, ensure_ascii=False, sort_keys=True)
                    if item_str not in seen_ids:
                        seen_ids.add(item_str)
    return merged

def merge_users(all_files):
    merged = {}
            if isinstance(data, dict):
                merged.update(data)
            elif isinstance(data, list):
                for user in data:
                    if isinstance(user, dict):
                        user_id = user.get('id', user.get('user_id', str(user)))
                        merged[user_id] = user
    return list(merged.values())

def merge_txt_files(all_files):
    all_content = []
    seen_lines = set()
        content = load_txt(filepath)
        if content:
            for line in content.split('\\n'):
                line = line.strip()
                if line and line not in seen_lines:
                    seen_lines.add(line)
                    all_content.append(line)
    return '\\n'.join(all_content)

def main():
    base_dir = r"d:\\sfdhdjdtysjsy\\sgdhfjasdkd\\新建文件夹"
    output_dir = os.path.join(base_dir, "MERGED_FINAL")
    os.makedirs(output_dir, exist_ok=True)
    
    files_by_name = defaultdict(list)
    for root, dirs, files in os.walk(base_dir):
        if "MERGED_FINAL" in root:
            continue
        for filename in files:
            files_by_name[filename].append(os.path.join(root, filename))
    
    print("=== Found duplicate files ===")
    for name, paths in files_by_name.items():
        if len(paths) > 1:
            print(f"{name}: {len(paths)} copies")
    
    print("\\n=== Starting merge process ===")
    
    conversations_files = [p for p in files_by_name.get('conversations.json', [])]
    if conversations_files:
        print(f"Merging conversations.json: {len(conversations_files)} files")
        merged_convs = merge_conversations(conversations_files)
        save_json(merged_convs, os.path.join(output_dir, 'conversations.json'))
        print(f"Merged {len(merged_convs)} conversations")
    
    user_files = [p for p in files_by_name.get('user.json', [])]
    if user_files:
        print(f"Merging user.json: {len(user_files)} files")
        merged_users = merge_users(user_files)
        save_json(merged_users, os.path.join(output_dir, 'user.json'))
        print(f"Merged {len(merged_users)} users")
    
    print("\\n=== Merge complete ===")
    print(f"Results saved to: {output_dir}")

if __name__ == "__main__":
    main()
"""
