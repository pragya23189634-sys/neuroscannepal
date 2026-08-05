# Fast CNN training for NeuroScan Nepal
# Uses Python 3.11 (PyTorch is not available on the project's 32-bit Python 3.13 venv)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $ProjectRoot "src")

Write-Host "Starting fast CNN training (cached data + preprocessed PNGs)..." -ForegroundColor Cyan
py -3.11 cnn_baseline.py --epochs 10 --batch-size 32 @args
