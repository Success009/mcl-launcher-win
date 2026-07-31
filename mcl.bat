@echo off
title Minecraft Launcher
cls

:: 1. Try 'py' launcher
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -m mcl_launcher.cli %*
    goto end
)

:: 2. Try 'python' if not Microsoft Store alias
where python >nul 2>nul
if %errorlevel% equ 0 (
    python -c "import sys; sys.exit(0 if 'WindowsApps' not in sys.executable else 1)" >nul 2>nul
    if %errorlevel% equ 0 (
        python -m mcl_launcher.cli %*
        goto end
    )
)

:: 3. Try standard installation paths on disk
if exist "%ProgramFiles%\Python312\python.exe" (
    "%ProgramFiles%\Python312\python.exe" -m mcl_launcher.cli %*
    goto end
)
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    "%LocalAppData%\Programs\Python\Python312\python.exe" -m mcl_launcher.cli %*
    goto end
)
if exist "C:\Python312\python.exe" (
    "C:\Python312\python.exe" -m mcl_launcher.cli %*
    goto end
)

echo [ERROR] Python not found. Please run install.bat or install.ps1 first.
pause

:end
if %errorlevel% neq 0 (
    echo.
    echo Press any key to close...
    pause >nul
)