@echo off
REM Zip dataset for Google Colab / Kaggle upload
REM Creates neuroscan_data.zip in this folder (normal + abnormal only)

cd /d "%~dp0.."
set OUT=%~dp0neuroscan_data.zip

if not exist "data\raw\normal" (
  echo ERROR: data\raw\normal not found
  pause
  exit /b 1
)

powershell -NoProfile -Command ^
  "Compress-Archive -Path 'data\raw\normal','data\raw\abnormal' -DestinationPath '%OUT%' -Force"

echo.
echo Created: %OUT%
echo Upload this zip to Google Drive or Kaggle Dataset.
echo.
pause
