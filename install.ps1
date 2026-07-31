# Minecraft CLI Launcher Windows Installer
$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Setting up Minecraft CLI Launcher for Windows  " -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

function Get-ValidPythonExecutable {
    # 1. Check 'py' launcher
    try {
        $pyPath = & py -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $pyPath -and (Test-Path $pyPath)) {
            return $pyPath
        }
    } catch {}

    # 2. Check 'python' command (excluding WindowsApps store redirector)
    try {
        $pyPath = & python -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $pyPath -and (Test-Path $pyPath) -and $pyPath -notmatch "WindowsApps") {
            return $pyPath
        }
    } catch {}

    # 3. Check standard Windows installation paths
    $candidatePaths = @(
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe",
        "$env:ProgramFiles\Python310\python.exe",
        "$env:LocalAppData\Programs\Python\Python312\python.exe",
        "$env:LocalAppData\Programs\Python\Python311\python.exe",
        "$env:LocalAppData\Programs\Python\Python310\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe"
    )
    foreach ($p in $candidatePaths) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

# Find or Install Python
$pythonExe = Get-ValidPythonExecutable

if (-not $pythonExe) {
    Write-Host "[INFO] Valid Python installation not detected. Installing Python automatically..." -ForegroundColor Yellow
    
    $installerUrl = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
    $installerPath = Join-Path $env:TEMP "python-3.12.8-amd64.exe"
    
    Write-Host "[INFO] Downloading Python 3.12 installer..." -ForegroundColor Cyan
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
    
    Write-Host "[INFO] Installing Python 3.12 (silent mode)..." -ForegroundColor Cyan
    Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait
    Remove-Item -Path $installerPath -ErrorAction SilentlyContinue

    # Update PATH environment variable in current session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    # Re-check Python executable
    $pythonExe = Get-ValidPythonExecutable
}

if (-not $pythonExe) {
    Write-Host "[ERROR] Could not locate Python executable. Please restart PowerShell and re-run installation." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[OK] Using Python at: $pythonExe" -ForegroundColor Green

# Install dependencies (portablemc)
Write-Host "[INFO] Installing required package 'portablemc'..." -ForegroundColor Cyan
& $pythonExe -m pip install --quiet --upgrade portablemc

# Create Desktop Shortcut
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