@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo  SMARTOPS AI -- Multi-Agent Platform Orchestrator
echo =====================================================================
echo.

:: Detect Python
set PYTHON_CMD=
where py.exe >nul 2>&1
if %errorlevel% equ 0 (
    py -3.11 -V >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_CMD=py -3.11
    ) else (
        set PYTHON_CMD=py
    )
) else (
    where python.exe >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python was not found on your system!
    echo Please install Python 3.10 or 3.11 from https://www.python.org/downloads/
    pause
    exit /b 1
)

%PYTHON_CMD% run_all.py %*
