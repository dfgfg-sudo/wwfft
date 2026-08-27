def monthly_resource_maintenance():
    actions = [
        {"task": "扫描30天未更新", "action": "标记'待归档'"},
        {"task": "检测URL链接有效性", "action": "自动替换失效链接"},
        {"task": "合并功能重复工作流", "threshold": "相似度>85%"},
        {"task": "版本清理", "action": "保留最近5个版本"}
    ]
    execute_maintenance(actions)