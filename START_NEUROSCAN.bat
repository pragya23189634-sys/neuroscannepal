@echo off
title NeuroScan Nepal Launcher
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_dashboard.ps1"
