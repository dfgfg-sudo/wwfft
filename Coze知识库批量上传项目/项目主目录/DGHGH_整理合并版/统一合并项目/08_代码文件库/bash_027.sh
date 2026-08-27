# 方式1: 完整自动化（推荐）
python coze_automation.py --dir ./your_plugins --full --config config.json

# 方式2: 分步执行
# 第一步: 扫描分析
python coze_automation.py --dir ./data --scan-only

# 第二步: 文件合并
python coze_automation.py --dir ./data --merge-only

# 第三步: 内容对比
python coze_automation.py --dir ./data --compare-only

# 第四步: 生成报告
python coze_automation.py --dir ./data --report-only