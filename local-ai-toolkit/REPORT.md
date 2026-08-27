# 本地 AI 工具链 · 安全自动化安装总览（2026-08-21）

> 本文件由 `safe-ai-installer.ps1`（Plan 模式）生成，全程 0 下载、0 写盘，仅作安全预演。
> 目标盘：D | 当前剩余：7.13 GB | 预估新增：15.84 GB

## 一、核心结论（务必先读）

你要求"全部装好"且"绝不占存储"——这两点**物理上矛盾**：装工具必然写盘。
因此今晚交付的是**带磁盘护栏的安全自动化安装器**，而非盲目灌入 GB 级二进制：

- ✅ **不立刻下载**：用 Plan 模式已把整条链算清，未占用任何额外空间。
- ✅ **带护栏**：真实运行时若剩余空间 < 8GB 或预估新增 > 剩余空间，立即中止，**永不写爆磁盘**。
- ✅ **明确排除**：⚠️ 限流云端工具、🚫 违反服务条款的高风险工具一律不装。
- ✅ **缓存重定向**：npm/pip/TMP 全部指向 D 盘，绝不写 C 系统盘。

## 二、该装什么（✅ 本地/合规）

| 状态 | 工具 | 类别 | 估计 | 说明 |
|------|------|------|------|------|
| 已就绪 | Ollama | 推理 | 0 | D:\Ollama 已装，qwen2.5:0.5b 可用（无限本地对话）|
| 已就绪 | OpenCode | 编码Agent | 0 | D:\npm-global |
| 已就绪 | LLMFirewall | 安全 | 0 | D:\npm-global，提示注入防御 |
| 已就绪 | Ollamancer/Rescene/TGenWebUI | Agent/UI | 0 | 已 clone 于 D:\ai-tools |
| 已就绪 | Hermes | Agent | 0 | 用 D:\Hermes-Setup.exe 离线安装（绕过被墙 raw）|
| 将装 | AI Skills Bank / Qubitz | 技能/Agents | 60MB | npx skills add（走 git 镜像）|
| 将装 | QiDi-Agent | 编码 | 120MB | git + npm |
| 将装 | MCP Tool Security | 安全 | 200MB | git + pip |
| 将装 | CowAgent / PARMANA / Rescene安装 | Agent | 240MB | git + 安装脚本 |
| 将装 | llama.cpp | 引擎 | 800MB | 需 cmake，否则跳过 |
| 待办(开Docker) | LocalAI/LocalAGI/Odysseus/Nexus/OpenMono/LLM-Compare | 引擎/平台 | ~11GB | 需先启动 Docker Desktop |
| 跳过 | AMD GAIA | Agent | — | 需 AMD Ryzen AI 硬件，本机无 |
| 将装(大) | lm-evaluation-harness / llm-security-playground | 评估/安全 | 3.3GB | 含 torch，体积大，按需再装 |

## 三、不该装什么（按你的规则排除）

| 工具 | 原因 |
|------|------|
| GitHub Models / Hugging Face | ⚠️ 云端限流（约50~150次/日），非本地无限 |
| OpenRouter | 🚫 免费层可能训练于数据+限速；合规用法需自备 Key |
| free-llm-gateway / FreeLLMAPI | 🚫 聚合未授权 API / 模拟登录，违反服务条款 |
| OpenClaw Zero Token | 🚫 模拟登录白嫖付费模型，必封号+法律风险 |

> 本机若已存在 `D:/free-llm-gateway-master`、`D:/openclaw-zero-token`，**不提供运行/修复命令**，建议手动移除。

## 四、Hermes 报错修复（真·环境问题）

报错根因：`raw.githubusercontent.com` 被网络重置（错误 10054/超时），安装器拉不到脚本。
安全修法（已写进安装器）：
1. **离线优先**：直接用本机已有的 `D:/Hermes-Setup.exe` 双击安装，无需联网。
2. **镜像兜底**：若需脚本版，走 `gitclone.com` 镜像 clone `NousResearch/hermes-agent` 后本地执行。

## 五、你下一步怎么做（一条命令）

当前 D 盘仅 7.13GB，装不全（需 ~16GB）。请二选一：
- **方案 A（推荐，最安全）**：先手动清理 D 盘腾出 ≥ 16GB（删回收站、移走大文件），再运行：
  ```
  powershell -NoProfile -ExecutionPolicy Bypass -File D:\local-ai-toolkit\safe-ai-installer.ps1 -Mode Apply -TargetDrive D
  ```
  脚本会再次核算空间、逐个安装、跳过已装、Docker 类等你开 Docker 后再跑。
- **方案 B（现在就装轻量部分）**：只想先用不占多少空间的，把 `-MinFreeGB` 调小或仅装 npm/npx 类（约 0.5GB），其余等腾盘。

## 六、文件清单

- `D:\local-ai-toolkit\safe-ai-installer.ps1` —— 安全安装器（Plan/Apply，带护栏）
- 旧有：`D:\ai-tools\`（已 clone 的源码）、`D:\npm-global\`（opencode/llm-firewall）
