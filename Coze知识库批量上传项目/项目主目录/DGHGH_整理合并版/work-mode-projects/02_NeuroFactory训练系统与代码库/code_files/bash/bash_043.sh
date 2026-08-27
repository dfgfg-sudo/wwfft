# 开发者本地操作
git add .                    # 添加更改
git commit -m "功能说明"      # 提交代码
git push origin feature-branch # 推送到远程

# 触发CI的钩子配置
# .git/hooks/pre-push 示例
#!/bin/bash
echo "运行本地测试..."
npm test
if [ $? -ne 0 ]; then
    echo "测试失败，请修复后重试"
    exit 1
fi