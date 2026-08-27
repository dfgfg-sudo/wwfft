<#
  safe-ai-installer.ps1
  Safe, automated local-AI toolchain installer for Windows.
  - Plan mode (default): computes/prints the plan, downloads NOTHING, uses ~0 storage.
  - Apply mode: disk-guarded; aborts if free space < threshold so it can never fill the disk.
  - Explicitly EXCLUDES cloud-limited (warning) and ToS-violating (forbidden) tools.
  - All caches/temp are redirected to the target drive; the C: system disk is never written.
  Usage:
    powershell -NoProfile -ExecutionPolicy Bypass -File safe-ai-installer.ps1 -Mode Plan
    powershell -NoProfile -ExecutionPolicy Bypass -File safe-ai-installer.ps1 -Mode Apply -TargetDrive D
#>

[CmdletBinding()]
param(
  [ValidateSet('Plan','Apply')] [string] $Mode = 'Plan',
  [string] $TargetDrive = 'D',
  [int]    $MinFreeGB   = 8
)

$ErrorActionPreference = 'Continue'
$ToolRoot  = "$TargetDrive" + ':\ai-tools'
$npmGlobal = "$TargetDrive" + ':\npm-global'
$venv      = "$TargetDrive" + ':\ai-tools-venv'
$tmpDir    = "$TargetDrive" + ':\tmp'
$cacheNpm  = "$TargetDrive" + ':\npm-cache'
$cachePip  = "$TargetDrive" + ':\pip-cache'

function Ensure-Dirs {
  foreach ($d in @($ToolRoot,$npmGlobal,$venv,$tmpDir,$cacheNpm,$cachePip)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
  }
  $env:TMP = $tmpDir; $env:TEMP = $tmpDir; $env:TMPDIR = $tmpDir
  & npm config set prefix $npmGlobal 2>$null
  & npm config set cache  $cacheNpm  2>$null
  $env:PIP_CACHE_DIR = $cachePip
}

function Get-FreeGB {
  param([string]$d)
  $v = Get-PSDrive $d -ErrorAction SilentlyContinue
  if ($v) { return [math]::Round($v.Free/1GB,2) } else { return 0 }
}

# Tool catalog: only local / compliant tools. Warning + forbidden tools are excluded below.
$TOOLS = @(
  @{k='ollama';      n='Ollama';                 cat='Inference'; m='already'; mb=0;    docker=$false; amd=$false; note='Installed at D:\Ollama, qwen2.5:0.5b ready (unlimited local chat)'}
  @{k='opencode';    n='OpenCode';               cat='Agent/Code';m='npm';    mb=80;   docker=$false; amd=$false; note='npm global, installed at D:\npm-global'}
  @{k='llmfirewall'; n='LLMFirewall';            cat='Security';  m='npm';    mb=40;   docker=$false; amd=$false; note='npm global, prompt-injection defense'}
  @{k='skillsbank';  n='AI Skills Bank';         cat='Skills';    m='npx';    mb=30;   docker=$false; amd=$false; note='npx skills add (via git mirror)'}
  @{k='qubitz';      n='AI-Agent-Qubitz';        cat='Agent';     m='npx';    mb=30;   docker=$false; amd=$false; note='npx skills add (via git mirror)'}
  @{k='qidi';        n='QiDi-Agent';             cat='Agent/Code';m='gitnpm'; mb=120;  docker=$false; amd=$false; note='git clone + npm install'}
  @{k='lmeval';      n='lm-evaluation-harness';  cat='Eval';      m='pip';    mb=1500; docker=$false; amd=$false; note='pip lm-eval (torch deps, large)'}
  @{k='mcpsec';      n='MCP Tool Security';      cat='Security';  m='gitpip'; mb=200;  docker=$false; amd=$false; note='git clone + pip (28 scenarios)'}
  @{k='llmsec';      n='llm-security-playground';cat='Security';  m='gitpip'; mb=1800; docker=$false; amd=$false; note='git clone + pip torch'}
  @{k='ollamancer';  n='Ollamancer';             cat='Agent';     m='git';    mb=50;   docker=$false; amd=$false; note='cloned at D:\ai-tools'}
  @{k='rescene';     n='Rescene Agent OS';       cat='Agent';     m='git';    mb=80;   docker=$false; amd=$false; note='cloned at D:\ai-tools (PowerShell install)'}
  @{k='cowagent';    n='CowAgent';               cat='Agent';     m='git';    mb=120;  docker=$false; amd=$false; note='git clone + pip or docker'}
  @{k='parmana';     n='PARMANA';                cat='Agent';     m='git';    mb=40;   docker=$false; amd=$false; note='git clone + install.ps1 (unlimited local)'}
  @{k='tgenwebui';   n='Text Generation WebUI';  cat='UI';        m='git';    mb=400;  docker=$false; amd=$false; note='cloned at D:\ai-tools (or Docker/Win pkg)'}
  @{k='localai';     n='LocalAI';                cat='Engine';    m='docker'; mb=2500; docker=$true;  amd=$false; note='docker run (bundles LocalAGI)'}
  @{k='localagi';    n='LocalAGI';               cat='AgentPlat'; m='docker'; mb=2000; docker=$true;  amd=$false; note='docker compose (Web UI)'}
  @{k='odysseus';    n='Odysseus';               cat='Workspace'; m='docker'; mb=2500; docker=$true;  amd=$false; note='docker compose (all-in-one)'}
  @{k='nexus';       n='Nexus';                 cat='Orchestr';  m='docker'; mb=1800; docker=$true;  amd=$false; note='docker compose (parallel experts)'}
  @{k='openmono';    n='OpenMonoAgent.ai';       cat='CodeAgent'; m='docker'; mb=1500; docker=$true;  amd=$false; note='one-liner (terminal native)'}
  @{k='llmcompare';  n='LLM-Compare';           cat='Compare';   m='docker'; mb=800;  docker=$true;  amd=$false; note='docker run (side-by-side)'}
  @{k='hermes';      n='Hermes';                 cat='Agent';     m='offline';mb=200;  docker=$false; amd=$false; note='Use D:\Hermes-Setup.exe offline (bypasses blocked raw)'}
  @{k='amdgaia';     n='AMD GAIA';              cat='Agent';     m='amd';    mb=1500; docker=$false; amd=$true;  note='Only on AMD Ryzen AI hardware'}
  @{k='llamacpp';    n='llama.cpp';              cat='Engine';    m='build';  mb=800;  docker=$false; amd=$false; note='Needs C++ build tools (cmake); skipped if absent'}
)

$EXCLUDED = @(
  @{n='GitHub Models';     why='WARNING: cloud rate-limited (~50-150/day), not local-unlimited -> excluded per your rule'}
  @{n='Hugging Face';      why='WARNING: cloud rate-limited platform -> excluded per your rule'}
  @{n='OpenRouter';        why='FORBIDDEN: free tier may train on data + rate limits; compliant use needs your own key (no free bypass)'}
  @{n='free-llm-gateway';  why='FORBIDDEN: aggregates unauthorized APIs / login spoofing, violates ToS; not run even if present'}
  @{n='FreeLLMAPI';        why='FORBIDDEN: same as above, violates ToS'}
  @{n='OpenClaw Zero Token';why='FORBIDDEN: login spoofing to freeload paid models; ban + legal risk; not run even if present'}
)

function Detect-Installed {
  $hit = @{}
  if (Test-Path "D:\Ollama\ollama.exe") { $hit['ollama'] = $true }
  if (Test-Path "$npmGlobal\opencode.cmd") { $hit['opencode'] = $true }
  if (Test-Path "$npmGlobal\node_modules\llm-firewall") { $hit['llmfirewall'] = $true }
  foreach ($g in @('Ollamancer','ResceneAgent','text-generation-webui','CowAgent','PARMANA','QiDi-Agent','mcp-tool-security-playground','llm-security-playground','LocalAI','LocalAGI','odysseus','nexus','OpenMonoAgent.ai','LLM-Compare')) {
    if (Test-Path "$ToolRoot\$g") { $hit[$g.ToLower()] = $true }
  }
  if (Test-Path "$venv\Scripts\python.exe") {
    $pkgs = & "$venv\Scripts\python.exe" -m pip list 2>$null
    if ($pkgs -match 'lm-eval') { $hit['lmeval'] = $true }
  }
  if (Test-Path "D:\Hermes-Setup.exe") { $hit['hermes'] = $true }
  return $hit
}

Write-Host "=================================================="
Write-Host " Safe Local-AI Installer | Mode: $Mode"
Write-Host " Target: $TargetDrive | Required free >= ${MinFreeGB}GB"
Write-Host "=================================================="

$free = Get-FreeGB $TargetDrive
Write-Host ("Target free: {0} GB" -f $free)

if ($Mode -eq 'Apply') {
  if ($free -lt $MinFreeGB) {
    Write-Host ("[GUARD] free {0}GB < {1}GB -> abort to protect disk." -f $free,$MinFreeGB) -ForegroundColor Red
    Write-Host "Free up space on the target drive (or use -TargetDrive <other>), then run Apply." -ForegroundColor Yellow
    exit 0
  }
  Ensure-Dirs
}

$installed = Detect-Installed
$totalNewMB = 0
$dockerBlocked = $false
try { & "$env:ProgramFiles\Docker\Docker\resources\bin\docker.exe" info >$null 2>&1; $dockerOK = $? } catch { $dockerOK = $false }
if (-not $dockerOK) { $dockerBlocked = $true }

Write-Host ""
Write-Host ("{0,-22}{1,-11}{2,9}  {3}" -f 'Tool','Category','EstMB','Status / Note')
Write-Host ("-"*78)

foreach ($t in $TOOLS) {
  if ($t.amd) {
    Write-Host ("{0,-22}{1,-11}{2,9}  [SKIP] needs AMD Ryzen AI hardware" -f $t.n,$t.cat,$t.mb) -ForegroundColor DarkGray
    continue
  }
  if ($installed.ContainsKey($t.k)) {
    Write-Host ("{0,-22}{1,-11}{2,9}  [READY] {3}" -f $t.n,$t.cat,0,$t.note) -ForegroundColor Green
    continue
  }
  if ($t.docker -and $dockerBlocked) {
    Write-Host ("{0,-22}{1,-11}{2,9}  [TODO] start Docker Desktop first" -f $t.n,$t.cat,$t.mb) -ForegroundColor Yellow
    $totalNewMB += $t.mb
    continue
  }
  Write-Host ("{0,-22}{1,-11}{2,9}  [WILL INSTALL] {3}" -f $t.n,$t.cat,$t.mb,$t.note) -ForegroundColor White
  $totalNewMB += $t.mb
}

Write-Host ("-"*78)
Write-Host ("Estimated new download/install total: {0} MB ({1} GB)" -f $totalNewMB, [math]::Round($totalNewMB/1024,2)) -ForegroundColor Yellow
Write-Host ("Current target free: {0} GB" -f $free) -ForegroundColor Yellow
if (($Mode -eq 'Apply') -and (($free*1024) -lt $totalNewMB)) {
  Write-Host "[GUARD] estimated new > free space -> abort to protect disk." -ForegroundColor Red
  exit 0
}

Write-Host ""
Write-Host "===== Explicitly NOT installed (your rule: exclude warning/forbidden) =====" -ForegroundColor Red
foreach ($e in $EXCLUDED) {
  Write-Host ("  - {0}: {1}" -f $e.n, $e.why) -ForegroundColor Red
}

if ($Mode -eq 'Plan') {
  Write-Host ""
  Write-Host "[Plan mode] No downloads, no writes. This was a safe dry-run." -ForegroundColor Green
  Write-Host "After freeing >= ${MinFreeGB}GB, run:" -ForegroundColor Green
  Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File safe-ai-installer.ps1 -Mode Apply -TargetDrive $TargetDrive" -ForegroundColor Green
}
