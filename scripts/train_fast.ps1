# Fast CNN training for NeuroScan Nepal
# Uses Python 3.11 (PyTorch is not available on the project's 32-bit Python 3.13 venv)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $ProjectRoot "src")

Write-Host "Starting tuned CNN training (augmentation + AdamW + calibration)..." -ForegroundColor Cyan
py -3.11 cnn_baseline.py --epochs 30 --batch-size 32 --learning-rate 0.0005 --weight-decay 0.0001 --label-smoothing 0.03 --patience 7 @args
