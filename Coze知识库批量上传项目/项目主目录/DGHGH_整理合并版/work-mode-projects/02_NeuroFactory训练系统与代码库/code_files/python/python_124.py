from unified_automation_tool import UnifiedAutomationTool

# 创建工具实例
tool = UnifiedAutomationTool()

# 处理内容
result = tool.process(
    content='{"plugin_name": "测试插件", "nodes": []}',
    operation_mode="coze_json_repair",
    automation_level="comprehensive"
)

print(result)

# 批量处理
result = tool.batch_process(
    directory="./plugins",
    operation_mode="auto_detect",
    automation_level="standard"
)

print(result)