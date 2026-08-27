@echo off

:: 抖音视频字幕工具启动脚本

echo 抖音视频字幕工具启动中...
echo =============================

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python安装
    echo 请先安装Python 3.11或更高版本
    pause
    exit /b 1
)

echo Python已安装

:: 检查pip是否可用
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: pip不可用
    pause
    exit /b 1
)

echo pip已可用

:: 安装依赖包
echo 正在安装依赖包...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo 错误: 依赖包安装失败
    pause
    exit /b 1
)

echo 依赖包安装成功

:: 启动应用程序
echo 正在启动抖音视频字幕工具...
python main.py

pause
