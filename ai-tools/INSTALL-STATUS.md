# 安装进度与阻塞状态（实时记录）

> 生成：2026-08-19 ｜ 此文件在 D 盘，因为 C 盘已 100% 满、无法写入。

## ✅ 已完成
- 环境配置：npm 全局前缀 → `D:/npm-global`；Python venv → `D:/ai-tools-venv`；npm 缓存 → `D:/npm-cache`；git 走 `gitclone.com` 镜像（绕开被墙的 raw.githubusercontent.com）
- npm 安装成功：**OpenCode**、**LLMFirewall**（位于 `D:/npm-global`）
- git clone 成功：**ResceneAgent**（`D:/ai-tools/ResceneAgent`）
- 已验证：Ollama + `qwen2.5:0.5b-instruct` 本地对话可用

## ⚠️ 当前硬阻塞（必须解决才能继续）
1. **C 盘 100% 满（0 字节可用）**：装 `lm-eval` 时 pip 把 655M 缓存写进 `C:/Users/Administrator/AppData/Local/pip/Cache`。本环境有 safe-delete 拦截层，回收站不可用时**拒绝任何删除**，所以我无法在这里清掉它。结果：bash 工具自身 cwd 在 C 盘，已无法写入（ENOSPC），后续命令全失败。
2. **D 盘 91%（剩约 3.7G，且部分克隆/安装已占用）**：继续装大模型或 Docker 镜像会爆。
3. **Docker 守护进程未运行**：所有 Docker 类工具需你先开 Docker Desktop。
4. **ghproxy.net 镜像失效**（开始要求认证），已切到 `gitclone.com`（可用）。

## ❌ 需要你来做（我无法在此环境删除文件）
请在 WorkBuddy 环境之外（文件管理器 / CMD / 磁盘清理）释放 C 盘，至少腾出 2~3GB：
- 删除 `C:/Users/Administrator/AppData/Local/pip/Cache`（655M，纯 pip 缓存，可安全删除）
- 清空回收站、运行 Windows「磁盘清理」
- 若仍不够：把 D 盘已装的大模型/镜像迁走，或扩容

> 腾出空间后，bash 工具即可恢复工作，我再用 `TMPDIR=D:/tmp` 把所有安装都导向 D 盘继续。

## 📋 腾出空间后待装（全部走 D 盘，TMPDIR=D:/tmp）
- npm：AI-Agent-Qubitz（npx skills，上次失败需重试）、QiDi-Agent（clone 后 npm i）
- pip(venv)：lm-eval(=lm-evaluation-harness)、MCP Tool Security Playground、llm-security-playground
- 源码续 clone：cowagent、LocalAGI、odysseus、nexus、OpenMonoAgent.ai、llama.cpp、mcp-tool-security-playground、llm-security-playground、QiDi-Agent、hermes-agent
- Docker 类（需先开 Docker Desktop）：LocalAI、LocalAGI、Odysseus、Nexus、Text Generation WebUI、OpenMonoAgent.ai、LLM-Compare
- Hermes：clone 后用仓库内本地脚本 / 离线 `D:/Hermes-Setup.exe` 修复
- **排除（按你要求 ⚠️）**：GitHub Models、Hugging Face
- **不碰（🚫 高风险）**：free-llm-gateway、OpenClaw Zero Token、FreeLLMAPI
