# Blueprint XPU · PowerShell Launcher
# 우선순위: LM Studio(:1234, 주력) → Ollama(:11434, 폴백) → serve.py(:8080) → Minimal.html
# 사용법: .\start.ps1
#         .\start.ps1 -Port 9090 -WithOllama

param(
    [int]$Port = 8080,
    [string]$OllamaExe = "C:\Ollama-IPEX\ollama.exe",
    [string]$LmsExe = "$env:USERPROFILE\.lmstudio\bin\lms.exe",
    [string]$PreferredModel = "openai-gpt-oss-20b-abliterated-uncensored-neo-imatrix",
    [switch]$WithOllama
)

$Host.UI.RawUI.WindowTitle = "Blueprint XPU · Launcher"
$lmUrl     = "http://127.0.0.1:1234"
$ollamaUrl = "http://127.0.0.1:11434"
$appUrl    = "http://127.0.0.1:$Port"

Write-Host ""
Write-Host "  ============================================================" -ForegroundColor Cyan
Write-Host "   Blueprint XPU  |  LM Studio primary (Ollama: -WithOllama)" -ForegroundColor Cyan
Write-Host "  ============================================================" -ForegroundColor Cyan
Write-Host ""

function Test-Endpoint($url) {
    try {
        $r = Invoke-WebRequest $url -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        return $r.StatusCode -eq 200
    } catch { return $false }
}

# ── 1. LM Studio (주력) ────────────────────────────────────────
if (Test-Endpoint "$lmUrl/v1/models") {
    Write-Host "  [OK]  LM Studio already running at :1234" -ForegroundColor Green
} elseif (Test-Path $LmsExe) {
    Write-Host "  [..] Starting LM Studio server..." -ForegroundColor Yellow
    & $LmsExe server start | Out-Null
    $ok = $false
    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep 1
        if (Test-Endpoint "$lmUrl/v1/models") { $ok = $true; break }
    }
    if ($ok) { Write-Host "  [OK]  LM Studio online at :1234" -ForegroundColor Green }
    else     { Write-Host "  [WARN] LM Studio did not respond in 15s — UI will use Ollama fallback" -ForegroundColor Yellow }
} else {
    Write-Host "  [WARN] lms.exe not found ($LmsExe) — UI will use Ollama fallback" -ForegroundColor Yellow
}

# 선호 모델 로드 (이미 로드돼 있으면 lms가 알아서 스킵)
if (Test-Endpoint "$lmUrl/v1/models") {
    try {
        $loaded = (Invoke-RestMethod "$lmUrl/v1/models" -UseBasicParsing).data.id
        if ($loaded -contains $PreferredModel) {
            Write-Host "  [OK]  Model ready: $PreferredModel" -ForegroundColor Green
        } else {
            Write-Host "  [..] Loading $PreferredModel (수 분 걸릴 수 있음)..." -ForegroundColor Yellow
            & $LmsExe load $PreferredModel -y 2>$null | Out-Null
            Write-Host "  [OK]  Model load requested" -ForegroundColor Green
        }
    } catch {}
}

Write-Host ""

# ── 2. Ollama (폴백 — 기본 끔 — -WithOllama 줄 때만 기동, 떠 있으면 감지만) ──
if (Test-Endpoint "$ollamaUrl/api/tags") {
    Write-Host "  [OK]  Ollama fallback running at :11434" -ForegroundColor Green
} elseif ($WithOllama -and (Test-Path $OllamaExe)) {
    Write-Host "  [..] Starting Ollama fallback..." -ForegroundColor Yellow
    Start-Process $OllamaExe -ArgumentList "serve" -WindowStyle Minimized
    $ok = $false
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep 1
        if (Test-Endpoint "$ollamaUrl/api/tags") { $ok = $true; break }
    }
    if ($ok) { Write-Host "  [OK]  Ollama fallback online at :11434" -ForegroundColor Green }
    else     { Write-Host "  [WARN] Ollama did not respond — LM Studio only" -ForegroundColor Yellow }
} else {
    Write-Host "  [--]  Ollama off by default (start with -WithOllama to enable fallback)" -ForegroundColor DarkGray
}

Write-Host ""

# ── 3. Python HTTP 서버 (serve.py: 정적 UI + /packs/ + LM Studio 프록시) ──
$projectRoot = $PSScriptRoot
$servePy     = Join-Path $projectRoot "10_execution\server\serve.py"
$serverJob   = $null

if (Test-Endpoint "$appUrl/schema") {
    Write-Host "  [OK]  HTTP server already running at :$Port" -ForegroundColor Green
} elseif ((Get-Command python -ErrorAction SilentlyContinue) -and (Test-Path $servePy)) {
    Write-Host "  [..] Starting HTTP server on :$Port..." -ForegroundColor Yellow
    $serverJob = Start-Process python -ArgumentList "`"$servePy`" $Port --no-browser" `
                     -WorkingDirectory $projectRoot -WindowStyle Minimized -PassThru
    Start-Sleep 2
    Write-Host "  [OK]  HTTP server at $appUrl" -ForegroundColor Green
} else {
    Write-Host "  [ERR] Python or serve.py missing — UI를 띄울 수 없습니다." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# ── 4. 설계 UI 직행 ────────────────────────────────────────────
Start-Process "$appUrl/Minimal.html"

Write-Host ""
Write-Host "  ── 실행 중 ─────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host "   LM Studio (주력) : $lmUrl" -ForegroundColor White
Write-Host "   Ollama (폴백)    : $ollamaUrl" -ForegroundColor White
Write-Host "   Design UI        : $appUrl/Minimal.html" -ForegroundColor White
Write-Host "   Dashboard        : $appUrl" -ForegroundColor White
Write-Host ""
Write-Host "  종료: 이 창 닫기 (LM Studio/Ollama는 별도 종료)" -ForegroundColor DarkGray
Write-Host ""

if ($serverJob) {
    try { $serverJob | Wait-Process } catch {}
}
