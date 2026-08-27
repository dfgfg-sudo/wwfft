@echo off
setlocal enabledelayedexpansion

chcp 65001 >nul
echo ==================================================
echo           NeuroForge-AI 训练系统启动器
echo ==================================================

:: 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未检测到Python环境，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 正在检查系统环境...
python -c "import torch, transformers" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装必要依赖包...
    pip install torch transformers datasets pandas pyyaml cryptography >nul 2>&1
    if %errorlevel% neq 0 (
        echo 依赖安装失败，请手动运行：pip install torch transformers datasets pandas pyyaml cryptography
        pause
        exit /b 1
    )
)

echo 环境检查通过，启动训练系统...
python main.py

if %errorlevel% equ 0 (
    echo.
    echo ==================================================
    echo   训练完成！结果已保存至 models\deployed 目录
    echo ==================================================
) else (
    echo.
    echo ==================================================
    echo   训练过程出现错误，请查看 logs/training.log
    echo ==================================================
)

pause