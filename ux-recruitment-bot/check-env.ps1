$ErrorActionPreference = "Continue"

Write-Host "=== 公众号招募工作台环境检查 ===" -ForegroundColor Green

Write-Host "`n[1] 当前目录"
Write-Host (Get-Location)

Write-Host "`n[2] Python"
try {
    python --version
} catch {
    Write-Host "未找到 python。请安装 Python 3.11 或 3.12，并勾选 Add Python to PATH。" -ForegroundColor Red
}

Write-Host "`n[3] 配置文件"
if (Test-Path ".env") {
    Write-Host ".env 已存在" -ForegroundColor Green
} else {
    Write-Host ".env 不存在。请复制 .env.example 并重命名为 .env。" -ForegroundColor Yellow
}

if (Test-Path ".env.example") {
    Write-Host ".env.example 已存在" -ForegroundColor Green
} else {
    Write-Host ".env.example 缺失" -ForegroundColor Red
}

Write-Host "`n[4] 海报 HTML"
$posterPath = "..\poster-generator\player-recruitment-poster-standalone.html"
if (Test-Path $posterPath) {
    Write-Host "海报 HTML 已找到：$posterPath" -ForegroundColor Green
} else {
    Write-Host "海报 HTML 未找到：$posterPath" -ForegroundColor Red
    Write-Host "请确认 ux-recruitment-bot 和 poster-generator 是相邻目录。"
}

Write-Host "`n[5] 依赖清单"
if (Test-Path "requirements.deploy.txt") {
    Write-Host "requirements.deploy.txt 已存在" -ForegroundColor Green
} else {
    Write-Host "requirements.deploy.txt 缺失" -ForegroundColor Red
}

Write-Host "`n检查完成。"
