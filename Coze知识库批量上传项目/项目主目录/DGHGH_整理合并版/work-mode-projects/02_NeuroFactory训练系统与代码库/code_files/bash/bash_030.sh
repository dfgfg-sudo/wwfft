# 交互式模式（推荐）
python unified_automation_tool.py --interactive

# 处理单个内容
python unified_automation_tool.py --process '{"plugin_name": "测试插件"}' --mode coze_json_repair

# 批量处理目录
python unified_automation_tool.py --batch ./data --mode auto_detect

# 查看系统状态
python unified_automation_tool.py --status

# 生成报告
python unified_automation_tool.py --report daily