@echo off
setlocal
set VERSION=%~1
if "%VERSION%"=="" set VERSION=1.2.0
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_muxapp.ps1" -Version "%VERSION%"
if errorlevel 1 (
  echo Build failed.
  exit /b 1
)
pause
