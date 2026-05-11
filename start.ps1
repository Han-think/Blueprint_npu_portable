# Blueprint NPU · PowerShell Launcher
# 사용법: .\start.ps1
#         .\start.ps1 -Port 9090

param(
    [int]$Port = 8080,
    [string]$OllamaExe = "C:\Ollama-IPEX\ollama.exe"
)

$Host.UI.RawUI.WindowTitle = "Blueprint NPU · Launcher"
$ollamaUrl = "http://127.0.0.1:11434"
$appUrl    = "http://127.0.0.1:$Port"

Write-Host ""
Write-Host "  ============================================================" -ForegroundColor Cyan
Write-Host "   Blueprint NPU  |  PowerShell Launcher" -ForegroundColor Cyan
Write-Host "  ============================================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Ollama 상태 확인 ────────────────────────────────────────
function Test-Ollama {
    try {
        $r = Invoke-WebRequest "$ollamaUrl/api/tags" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        return $r.StatusCode -eq 200
    } catch { return $false }
}

if (Test-Ollama) {
    Write-Host "  [OK]  Ollama already running at :11434" -ForegroundColor Green
} else {
    # ── 2. Ollama 실행 ─────────────────────────────────────────
    if (-not (Test-Path $OllamaExe)) {
        Write-Host "  [ERR] Not found: $OllamaExe" -ForegroundColor Red
        Write-Host "        -OllamaExe 파라미터로 경로를 지정하세요." -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Host "  [..] Starting Ollama IPEX..." -ForegroundColor Yellow
    Start-Process $OllamaExe -ArgumentList "serve" -WindowStyle Minimized

    # ── 3. 준비 대기 (최대 20초) ───────────────────────────────
    $ok = $false
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep 1
        if (Test-Ollama) { $ok = $true; break }
        Write-Host "  [..] Waiting... ($($i+1)s)" -ForegroundColor DarkGray
    }

    if (-not $ok) {
        Write-Host "  [ERR] Ollama did not respond within 20s." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Host "  [OK]  Ollama online at :11434" -ForegroundColor Green

    # 모델 목록 표시
    try {
        $tags = Invoke-RestMethod "$ollamaUrl/api/tags" -UseBasicParsing
        $names = $tags.models | ForEach-Object { $_.name }
        if ($names) {
            Write-Host "  [OK]  Models: $($names -join ', ')" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] No models installed — run: .\ollama.exe pull qwen2.5:7b" -ForegroundColor Yellow
        }
    } catch {}
}

Write-Host ""

# ── 4. Python HTTP 서버 ────────────────────────────────────────
$projectRoot = Split-Path $MyInvocation.MyCommand.Path -Parent
$servePy     = Join-Path $projectRoot "server\serve.py"

$pythonOk = $null -ne (Get-Command python -ErrorAction SilentlyContinue)

if ($pythonOk -and (Test-Path $servePy)) {
    Write-Host "  [..] Starting HTTP server on :$Port..." -ForegroundColor Yellow
    $serverJob = Start-Process python -ArgumentList "`"$servePy`" $Port" `
                     -WorkingDirectory $projectRoot -WindowStyle Minimized -PassThru
    Start-Sleep 2
    Write-Host "  [OK]  HTTP server at $appUrl" -ForegroundColor Green
    Start-Process $appUrl
} elseif ($pythonOk) {
    Write-Host "  [..] Starting python -m http.server $Port..." -ForegroundColor Yellow
    $serverJob = Start-Process python -ArgumentList "-m http.server $Port" `
                     -WorkingDirectory $projectRoot -WindowStyle Minimized -PassThru
    Start-Sleep 2
    Write-Host "  [OK]  HTTP server at $appUrl" -ForegroundColor Green
    Start-Process $appUrl
} else {
    Write-Host "  [WARN] Python not found — opening index.html directly" -ForegroundColor Yellow
    Write-Host "         CORS 오류 발생 시 Python을 설치하세요." -ForegroundColor DarkGray
    Start-Process (Join-Path $projectRoot "index.html")
    $serverJob = $null
}

Write-Host ""
Write-Host "  ── 실행 중 ─────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host "   Ollama  : $ollamaUrl" -ForegroundColor White
Write-Host "   Browser : $appUrl" -ForegroundColor White
Write-Host ""
Write-Host "  종료하려면 Ctrl+C 또는 이 창을 닫으세요." -ForegroundColor DarkGray
Write-Host "  (Ollama 프로세스는 별도로 종료해야 합니다)" -ForegroundColor DarkGray
Write-Host ""

# 서버 프로세스 감시 (선택적)
if ($serverJob) {
    try { $serverJob | Wait-Process } catch {}
}
