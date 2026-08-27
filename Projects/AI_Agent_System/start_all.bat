@echo off

:: OpenClaw 安全配置与技能管理解决方案启动脚本
:: 一劳永逸的自动配置

echo ================================================
echo OpenClaw 安全配置与技能管理解决方案
echo ================================================
echo 正在启动自动配置...

:: 安装依赖
echo 安装必要依赖...
python -m pip install flask requests

:: 启动集成服务
echo 启动集成服务...
python d:\Projects\AI_Agent_System\auto_integration.py

:: 保持窗口打开
echo 按任意键退出...
pause > nul