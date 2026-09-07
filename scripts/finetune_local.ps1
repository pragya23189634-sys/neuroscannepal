# Fine-tune CNN locally (CPU). Slower than Colab GPU but reliable — no Drive upload.
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "Fine-tuning cnn_baseline.pth on local data (CPU, ~20-45 min)..." -ForegroundColor Cyan
py -3.11 notebooks/colab/neuroscan_colab_train.py `
  --data-root data/raw `
  --out-dir models `
  --pretrained models/cnn_baseline.pth `
  --epochs 15 `
  --batch-size 32 `
  --lr 0.0001 `
  --patience 5

Write-Host "Done. Restart the app to use the updated model." -ForegroundColor Green
