@echo off
title Minecraft Launcher
cls
python -m mcl_launcher.cli %*
if %errorlevel% neq 0 (
    echo.
    echo Press any key to close...
    pause >nul
)