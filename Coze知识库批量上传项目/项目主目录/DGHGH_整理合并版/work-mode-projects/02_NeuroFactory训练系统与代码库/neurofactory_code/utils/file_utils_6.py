name_map = {}
for base, tools in groups.items():
    for t in tools:
        name = t['tool_name']
        if name in name_map:
            print(f"冲突：工具名 '{name}' 同时存在于插件 {name_map[name]['plugin_id']} 和 {t['plugin_id']}，请手动选择。")
        else:
            name_map[name] = t