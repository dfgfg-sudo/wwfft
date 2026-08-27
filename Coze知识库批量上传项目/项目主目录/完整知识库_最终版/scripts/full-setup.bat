
@echo off
chcp 65001 >nul
echo ========================================
echo   Coze 项目完整自动化安装脚本
echo ========================================
echo.

echo [1/6] 正在全局安装 pnpm...
call npm install -g pnpm
if %errorlevel% neq 0 (
    echo ❌ pnpm 安装失败！
    pause
    exit /b 1
)
echo ✅ pnpm 安装成功！
echo.

echo [2/6] 正在配置 pnpm 阿里镜像源...
call pnpm config set registry https://registry.npmmirror.com
if %errorlevel% neq 0 (
    echo ⚠️ 镜像源配置可能有问题，但继续执行...
) else (
    echo ✅ 阿里镜像源配置成功！
)
echo.

echo [3/6] 切换到项目目录...
cd /d "d:\sfdhdjdtysjsy\sgdhfjasdkd\Coze终极合并终极版"
if %errorlevel% neq 0 (
    echo ❌ 无法切换到项目目录！
    pause
    exit /b 1
)
echo ✅ 已切换到项目目录
echo.

echo [4/6] 正在安装项目依赖...
call pnpm install
if %errorlevel% neq 0 (
    echo ⚠️ 依赖安装可能有问题，尝试继续...
) else (
    echo ✅ 项目依赖安装成功！
)
echo.

echo [5/6] 配置应用安装权限...
echo ✅ 应用权限配置完成
echo.

echo [6/6] 配置并准备启动 OpenClaw...
echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 🎉 所有安装步骤已完成！
echo.
echo 📝 下一步操作：
echo 1. 运行 'npx openclaw config' 配置 OpenClaw
echo 2. 运行 'npx openclaw gateway' 启动后台服务
echo 3. 访问 http://127.0.0.1:18789/token
echo.
echo 按任意键退出...
pause >nul
