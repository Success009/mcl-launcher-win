# Minecraft CLI Launcher Windows Installer
$ErrorActionPreference = "Continue"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Setting up Minecraft CLI Launcher for Windows  " -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

function Write-Log($msg, $color="Cyan") {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $msg" -ForegroundColor $color
}

# 1. Target Installation Directory
$TargetDir = "$env:USERPROFILE\.mcl-launcher"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) { $ScriptDir = Get-Location }

if ($ScriptDir -ne $TargetDir) {
    Write-Log "Copying launcher files to $TargetDir..." "Cyan"
    if (-not (Test-Path $TargetDir)) { New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null }
    Copy-Item -Path "$ScriptDir\*" -Destination $TargetDir -Recurse -Force | Out-Null
}

# 2. Add to Global User PATH
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$TargetDir*") {
    Write-Log "Adding 'mcl' to global User PATH..." "Cyan"
    $NewUserPath = "$UserPath;$TargetDir"
    [Environment]::SetEnvironmentVariable("Path", $NewUserPath, "User")
    $env:Path = "$env:Path;$TargetDir"
}

# 3. Create Desktop Shortcut
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Minecraft Launcher.lnk"
$TargetBat = Join-Path $TargetDir "mcl.bat"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetBat
$Shortcut.WorkingDirectory = $TargetDir
$Shortcut.Description = "Minecraft CLI Launcher for Windows"
$Shortcut.IconLocation = "%SystemRoot%\System32\shell32.dll, 13"
$Shortcut.Save()

Write-Log "[SUCCESS] Created Desktop Shortcut!" "Green"
Write-Log "[SUCCESS] 'mcl' is now globally accessible from any CMD or PowerShell terminal!" "Green"
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   INSTALLATION COMPLETE - TYPE 'mcl' ANYWHERE!    " -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan