@echo off
setlocal
set VERSION=%~1
if "%VERSION%"=="" set VERSION=1.2.0
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_portmaster.ps1" -Version "%VERSION%"
if errorlevel 1 (
  echo PortMaster build failed.
  exit /b 1
)
echo.
echo PortMaster ZIP created in the outputs folder.
pause
