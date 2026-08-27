import json
from collections import defaultdict

with open("plugins_full_dump.json", "r", encoding="utf-8") as f:
    all_plugins = json.load(f)

groups = defaultdict(list)
for pid, plugin in all_plugins.items():
    base_url = plugin.get("data", {}).get("base_url", "")
    for tool in plugin.get("data", {}).get("tools", []):
        groups[base_url].append({
            "plugin_id": pid,
            "tool_name": tool.get("name"),
            "description": tool.get("description"),
            "method": tool.get("method", "GET"),
            "path": tool.get("path", ""),
            "input_params": tool.get("input_params", {}),
            "output_params": tool.get("output_params", {})
        })

# 生成合并清单（Markdown）
for base, tools in groups.items():
    print(f"## 域名: {base}\n")
    print("| 工具名称 | 方法 | 路径 | 原插件ID |")
    print("|----------|------|------|----------|")
    for t in tools:
        print(f"| {t['tool_name']} | {t['method']} | {t['path']} | {t['plugin_id']} |")
    print("\n")