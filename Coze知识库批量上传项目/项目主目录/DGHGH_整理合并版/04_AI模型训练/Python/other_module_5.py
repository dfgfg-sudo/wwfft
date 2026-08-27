import json
from deepdiff import DeepDiff

def compare_plugin_versions(old_file, new_file):
    with open(old_file) as f1, open(new_file) as f2:
        old_data = json.load(f1)
        new_data = json.load(f2)
    diff = DeepDiff(old_data, new_data, ignore_order=True)
    return diff

# 使用示例
diff_result = compare_plugin_versions("plugins_v1.json", "plugins_v2.json")
with open("version_diff.json", "w") as f:
    json.dump(diff_result, f, indent=2, default=str)
print("版本差异已保存至 version_diff.json")