# Creates neuroscan_data.zip and checks image counts before Colab upload.
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$normal = Join-Path $root "data\raw\normal"
$abnormal = Join-Path $root "data\raw\abnormal"
$out = Join-Path $PSScriptRoot "neuroscan_data.zip"

function Count-Images($dir) {
    if (-not (Test-Path $dir)) { return 0 }
    return (Get-ChildItem -Path $dir -Recurse -Include *.jpg,*.jpeg,*.png,*.bmp -File).Count
}

$n = Count-Images $normal
$a = Count-Images $abnormal

Write-Host ""
Write-Host "=== NeuroScan Colab upload check ===" -ForegroundColor Cyan
Write-Host "Normal folder:   $normal"
Write-Host "Abnormal folder: $abnormal"
Write-Host "Normal images:   $n"
Write-Host "Abnormal images: $a"
Write-Host ""

if ($n -eq 0 -or $a -eq 0) {
    Write-Host "ERROR: MRI images missing on this PC." -ForegroundColor Red
    Write-Host "Colab cannot train without images. Find your dataset and copy to:"
    Write-Host "  data\raw\normal\"
    Write-Host "  data\raw\abnormal\"
    Write-Host ""
    Write-Host "If you already trained locally, you may NOT need Colab — use START_NEUROSCAN.bat for demo."
    exit 1
}

if (Test-Path $out) { Remove-Item $out -Force }

Compress-Archive -Path $normal, $abnormal -DestinationPath $out -CompressionLevel Optimal
$sizeMb = [math]::Round((Get-Item $out).Length / 1MB, 1)

Write-Host "Created: $out ($sizeMb MB)" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT — upload this ONE file to Google Drive:" -ForegroundColor Yellow
Write-Host "  1. Open https://drive.google.com"
Write-Host "  2. Open folder: final year project / NeuroScan_Nepal"
Write-Host "  3. Upload: neuroscan_data.zip  (from scripts folder)"
Write-Host "  4. In Colab, run the short notebook cell (see docs/COLAB_KAGGLE_TRAINING.md)"
Write-Host ""
