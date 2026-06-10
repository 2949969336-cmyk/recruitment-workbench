$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

$url = "http://127.0.0.1:8000/workbench"
$venvActivate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
$setupMarker = Join-Path $PSScriptRoot ".setup-ok"

Write-Host ""
Write-Host "Starting recruitment workbench..." -ForegroundColor Green
Write-Host "Project: $PSScriptRoot"
Write-Host ""

$existingServer = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($existingServer) {
    Write-Host "Port 8000 is already running. Opening workbench..." -ForegroundColor Green
    Start-Process $url
    Write-Host ""
    Write-Host "If the page is not correct, close the old backend window first, then run this launcher again." -ForegroundColor Yellow
    Read-Host "Press Enter to close this window"
    exit 0
}

if (-not (Test-Path -LiteralPath $venvActivate)) {
    Write-Host "First run: creating Python virtual environment..."
    python -m venv .venv
    if (Test-Path -LiteralPath $setupMarker) {
        Remove-Item -LiteralPath $setupMarker -Force
    }
}

. $venvActivate

if (-not (Test-Path -LiteralPath $setupMarker)) {
    Write-Host "First run: installing dependencies and Chromium. This may take a few minutes..."
    python -m pip install --upgrade pip
    pip install -r requirements.deploy.txt
    playwright install chromium
    New-Item -ItemType File -Path $setupMarker -Force | Out-Null
} else {
    Write-Host "Dependencies already initialized. Starting backend..."
}

Start-Job -ScriptBlock {
    param($targetUrl)
    Start-Sleep -Seconds 4
    Start-Process $targetUrl
} -ArgumentList $url | Out-Null

Write-Host ""
Write-Host "Workbench will open automatically:" -ForegroundColor Green
Write-Host $url -ForegroundColor Cyan
Write-Host ""
Write-Host "Keep this window open while using the tool. Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""

python run.py
