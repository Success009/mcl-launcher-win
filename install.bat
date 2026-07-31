@echo off
title Minecraft Launcher Setup
cls
echo ==================================================
echo   Installing Minecraft CLI Launcher for Windows
echo ==================================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1"

echo.
echo ==================================================
echo Launching Minecraft Launcher...
echo ==================================================
echo.
call "%~dp0mcl.bat"