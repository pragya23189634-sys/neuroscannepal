# Start NeuroScan Nepal dashboard (backend + frontend)
# Backend uses Python 3.11 for PyTorch pipeline support.

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$FrontendDir = Join-Path $ProjectRoot "frontend"

Write-Host "Starting NeuroScan backend on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$ProjectRoot'; `$env:NEUROSCAN_LOG_LEVEL='INFO'; py -3.11 -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload"
) | Out-Null

Start-Sleep -Seconds 3

Write-Host "Starting NeuroScan frontend on http://127.0.0.1:3000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$FrontendDir'; npm run dev -- --host 127.0.0.1"
) | Out-Null

Write-Host ""
Write-Host "Dashboard starting." -ForegroundColor Green
Write-Host "Frontend : http://127.0.0.1:3000/" -ForegroundColor Yellow
Write-Host "Backend  : http://127.0.0.1:8000/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "Watch the BACKEND terminal for full pipeline logs:" -ForegroundColor Cyan
Write-Host "  upload -> preprocessing -> detection -> gradcam -> rag -> chatbot -> hospitals -> report"
Write-Host ""
Write-Host "Log file : $ProjectRoot\neuroscan.log" -ForegroundColor Gray
Write-Host "Keep both PowerShell windows open while testing." -ForegroundColor Gray

Write-Host ""
Write-Host "Opening the login page in your browser..." -ForegroundColor Green
Start-Sleep -Seconds 4
Start-Process "http://127.0.0.1:3000/login"
