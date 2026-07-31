# Minecraft CLI Launcher Windows Installer
$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Setting up Minecraft CLI Launcher for Windows  " -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python was not found in PATH! Please install Python from https://www.python.org/ or Microsoft Store." -ForegroundColor Red
    pause
    exit 1
}

# 2. Install dependencies (portablemc)
Write-Host "[INFO] Installing / updating required package 'portablemc'..." -ForegroundColor Cyan
python -m pip install --quiet --upgrade portablemc

# 3. Create Desktop Shortcut
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) {
    $ScriptDir = Get-Location
}

$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Minecraft Launcher.lnk"
$TargetBat = Join-Path $ScriptDir "mcl.bat"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetBat
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.Description = "Minecraft CLI Launcher for Windows"
$Shortcut.IconLocation = "%SystemRoot%\System32\shell32.dll, 13" # Game icon style
$Shortcut.Save()

Write-Host "[SUCCESS] Created 'Minecraft Launcher' shortcut on your Desktop!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan