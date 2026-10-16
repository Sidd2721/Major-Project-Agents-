@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo  SMARTOPS AI -- Automated Setup for Windows
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
    echo.
    echo Please install Python 3.10 or 3.11 from:
    echo   https://www.python.org/downloads/
    echo.
    echo CRITICAL: Ensure you check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Using Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

:: Run setup script
%PYTHON_CMD% setup.py %*
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Setup encountered an issue. See log messages above.
    pause
    exit /b %errorlevel%
)

echo.
echo =====================================================================
echo  Setup completed successfully!
echo  To start all services, run:  run_all.bat  (or python run_all.py)
echo =====================================================================
pause
