$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

Write-Host ""
Write-Host "正在启动公众号招募工作台..." -ForegroundColor Green
Write-Host "项目目录：$PSScriptRoot"
Write-Host ""

$venvActivate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
$setupMarker = Join-Path $PSScriptRoot ".setup-ok"
$url = "http://127.0.0.1:8000/workbench"

$existingServer = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($existingServer) {
    Write-Host "检测到工作台已经在运行，直接打开网页。" -ForegroundColor Green
    Start-Process $url
    Write-Host ""
    Write-Host "如果网页不能正常使用，请先关闭旧的 PowerShell 后端窗口，再重新双击启动。" -ForegroundColor Yellow
    Read-Host "按回车关闭这个窗口"
    exit 0
}

if (-not (Test-Path -LiteralPath $venvActivate)) {
    Write-Host "首次运行：正在创建 Python 虚拟环境..."
    python -m venv .venv
    if (Test-Path -LiteralPath $setupMarker) {
        Remove-Item -LiteralPath $setupMarker -Force
    }
}

. $venvActivate

if (-not (Test-Path -LiteralPath $setupMarker)) {
    Write-Host "首次运行：正在安装依赖和 Chromium，可能需要几分钟..."
    python -m pip install --upgrade pip
    pip install -r requirements.deploy.txt
    playwright install chromium
    New-Item -ItemType File -Path $setupMarker -Force | Out-Null
} else {
    Write-Host "依赖已初始化，直接启动服务。"
}

Start-Job -ScriptBlock {
    param($targetUrl)
    Start-Sleep -Seconds 4
    Start-Process $targetUrl
} -ArgumentList $url | Out-Null

Write-Host ""
Write-Host "启动完成后会自动打开：" -ForegroundColor Green
Write-Host $url -ForegroundColor Cyan
Write-Host ""
Write-Host "使用期间请不要关闭这个窗口。要停止服务，请按 Ctrl + C。" -ForegroundColor Yellow
Write-Host ""

python run.py
