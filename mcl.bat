@echo off
title Minecraft Launcher
cls
set SCRIPT_DIR=%~dp0
"%SCRIPT_DIR%python-embed\python.exe" -m mcl_launcher.cli %*
if %errorlevel% neq 0 (
    echo.
    echo Press any key to close...
    pause >nul
)