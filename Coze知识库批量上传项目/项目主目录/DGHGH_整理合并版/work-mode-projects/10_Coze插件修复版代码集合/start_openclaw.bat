@echo off
REM ============================================================
REM OpenClaw Gateway 启动脚本
REM 使用 Node.js v22.23.1 (OpenClaw 要求 >=22.22.3)
REM Gateway 端口: 18790
REM 健康检查: http://127.0.0.1:18790/health
REM ============================================================

set "PATH=C:\nodejs-v22\node-v22.23.1-win-x64;%PATH%"
set "PATH=C:\Users\Administrator\AppData\Local\pnpm\bin;%PATH%"

echo ============================================================
echo OpenClaw Gateway 启动中...
echo Node.js 版本:
node --version
echo pnpm 版本:
pnpm --version
echo ============================================================
echo.
echo Gateway 端口: ws://127.0.0.1:18790
echo 健康检查: http://127.0.0.1:18790/health
echo Canvas: http://127.0.0.1:18790/__openclaw__/canvas/
echo ============================================================
echo.

openclaw gateway run --verbose
pause