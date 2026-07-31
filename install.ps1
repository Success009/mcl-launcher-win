# Minecraft CLI Launcher Windows Installer
$ErrorActionPreference = "Continue"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   Setting up Minecraft CLI Launcher for Windows  " -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

function Write-Log($msg, $color="Cyan") {
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $msg" -ForegroundColor $color
}

Write-Log "Step 1/3: Checking Python Environment..." "Yellow"

function Find-PythonExecutable {
    # 1. Check 'py' launcher
    Write-Log "[Search] Checking 'py' launcher..."
    $pyCheck = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCheck) {
        $path = & py -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $path -and (Test-Path $path)) {
            Write-Log "[Found] Python via 'py' launcher: $path" "Green"
            return $path
        }
    }

    # 2. Check standard disk installation locations
    Write-Log "[Search] Checking standard disk installation paths..."
    $candidatePaths = @(
        "$env:LocalAppData\Programs\Python\Python312\python.exe",
        "$env:LocalAppData\Programs\Python\Python311\python.exe",
        "$env:LocalAppData\Programs\Python\Python310\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe",
        "$env:ProgramFiles\Python310\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe"
    )
    foreach ($p in $candidatePaths) {
        if (Test-Path $p) {
            Write-Log "[Found] Disk binary: $p" "Green"
            return $p
        }
    }

    # 3. Check 'python' command in PATH (ignoring WindowsApps store redirector)
    Write-Log "[Search] Checking 'python' in system PATH..."
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd -and $pythonCmd.Source -notmatch "WindowsApps") {
        try {
            $path = & python -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $path -and (Test-Path $path)) {
                Write-Log "[Found] PATH binary: $path" "Green"
                return $path
            }
        } catch {}
    }

    Write-Log "[Status] No valid Python installation found." "Yellow"
    return $null
}

$pythonExe = Find-PythonExecutable

if (-not $pythonExe) {
    Write-Log "[Install] Initiating automatic Python 3.12 download & installation..." "Yellow"
    
    $installerUrl = "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
    $installerPath = Join-Path $env:TEMP "python-3.12.8-amd64.exe"
    
    Write-Log "[Download] Fetching $installerUrl ..." "Cyan"
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
    
    $fileSize = (Get-Item $installerPath).Length
    Write-Log "[Download] Download complete ($fileSize bytes)." "Green"
    Write-Log "[Exec] Installing Python 3.12 (User Mode)..." "Cyan"
    
    $targetDir = "$env:LocalAppData\Programs\Python\Python312"
    $proc = Start-Process -FilePath $installerPath -ArgumentList "/quiet PrependPath=1 Include_pip=1 TargetDir=`"$targetDir`"" -PassThru -Wait
    
    $exitColor = "Green"
    if ($proc.ExitCode -ne 0) { $exitColor = "Red" }
    Write-Log "[Exec] Installer process exit code: $($proc.ExitCode)" $exitColor
    Remove-Item -Path $installerPath -ErrorAction SilentlyContinue

    # Refresh PATH session variables
    $userPath = [System.Environment]::GetEnvironmentVariable("Path","User")
    $systemPath = [System.Environment]::GetEnvironmentVariable("Path","Machine")
    $pyUserPath = "$targetDir;$targetDir\Scripts"
    $env:Path = "$pyUserPath;$userPath;$systemPath"
    
    $pythonExe = Find-PythonExecutable
}

if (-not $pythonExe) {
    Write-Log "[ERROR] Could not locate Python executable after installation!" "Red"
    Write-Log "[ERROR] Please verify antivirus settings or manually install Python 3.12." "Red"
    pause
    exit 1
}

Write-Log "[OK] Active Python Executable: $pythonExe" "Green"

Write-Log "Step 2/3: Installing / Updating 'portablemc' dependency..." "Yellow"
& $pythonExe -m pip install --upgrade portablemc

if ($LASTEXITCODE -eq 0) {
    Write-Log "[OK] Dependencies installed successfully." "Green"
} else {
    Write-Log "[WARNING] Pip finished with exit code $LASTEXITCODE." "Yellow"
}

Write-Log "Step 3/3: Creating Desktop Shortcut..." "Yellow"
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
$Shortcut.IconLocation = "%SystemRoot%\System32\shell32.dll, 13"
$Shortcut.Save()

Write-Log "[OK] Desktop Shortcut Created at: $ShortcutPath" "Green"
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   INSTALLATION COMPLETE - READY TO PLAY!         " -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan