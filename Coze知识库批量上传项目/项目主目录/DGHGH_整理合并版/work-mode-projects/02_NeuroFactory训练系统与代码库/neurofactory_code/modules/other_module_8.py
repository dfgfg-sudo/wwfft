def monthly_resource_maintenance():
    actions = [
        {"task": "扫描30天未更新的工作流", "action": "标记为'待归档'", "notify": "admin@team.com"},
        {"task": "检测URL链接有效性", "action": "测试所有工作流中硬编码的URL", "invalid_handler": "自动替换为最新有效链接"},
        {"task": "合并功能重复的工作流", "action": "生成合并建议报告", "threshold": "相似度>85%"},
        {"task": "版本清理", "action": "保留最近5个版本，删除更早版本", "exclude": ["production", "stable"]}
    ]
    execute_maintenance(actions)