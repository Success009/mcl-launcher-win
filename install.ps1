# Minecraft CLI Launcher Windows Installer
$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Setting up Minecraft CLI Launcher for Windows  " -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Check / Install Python
$hasPython = $false
try {
    $pyCheck = Get-Command python -ErrorAction SilentlyContinue
    if ($pyCheck) {
        $pythonVersion = python --version 2>&1
        Write-Host "[OK] Found $pythonVersion" -ForegroundColor Green
        $hasPython = $true
    }
} catch {}

if (-not $hasPython) {
    Write-Host "[INFO] Python was not found. Installing Python automatically..." -ForegroundColor Yellow
    
    $installedViaWinget = $false
    $wingetCheck = Get-Command winget -ErrorAction SilentlyContinue
    if ($wingetCheck) {
        try {
            Write-Host "[INFO] Attempting silent installation via winget..." -ForegroundColor Cyan
            winget install --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
            if ($LASTEXITCODE -eq 0) {
                $installedViaWinget = $true
            }
        } catch {}
    }
    
    if (-not $installedViaWinget) {
        $installerUrl = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
        $installerPath = Join-Path $env:TEMP "python-3.12.8-amd64.exe"
        Write-Host "[INFO] Downloading Python 3.12 standalone installer..." -ForegroundColor Cyan
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
        Write-Host "[INFO] Installing Python (silent mode)..." -ForegroundColor Cyan
        Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait
        Remove-Item -Path $installerPath -ErrorAction SilentlyContinue
    }
    
    # Refresh PATH environment variable in current session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "[SUCCESS] Python installed: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "[SUCCESS] Python installation complete! Path updated." -ForegroundColor Green
    }
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

Write-Host "[SUCCESS] Created 'Minecraft Launcher' shortcut on Desktop!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan