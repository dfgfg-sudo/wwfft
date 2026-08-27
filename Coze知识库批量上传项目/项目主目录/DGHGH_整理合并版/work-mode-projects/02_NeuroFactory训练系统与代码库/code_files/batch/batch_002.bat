@echo off
chcp 65001
echo ====================================
echo    AI训练工厂 v3.0 - 启动脚本
echo ====================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo 正在创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo ❌ 虚拟环境创建失败
    pause
    exit /b 1
)

echo 正在激活虚拟环境...
call venv\Scripts\activate.bat

echo 正在安装依赖包...
pip install torch transformers peft pandas pillow python-docx PyPDF2 openpyxl

echo.
echo ✅ 环境准备完成！
echo 🚀 启动AI训练工厂...
echo.

python auto_trainer.py

pause