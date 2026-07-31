@echo off
title Minecraft Launcher Setup
cls
echo ==================================================
echo   Installing Minecraft CLI Launcher for Windows
echo ==================================================
echo.

set SCRIPT_DIR=%~dp0
set TARGET_DIR=%LOCALAPPDATA%\mcl-launcher

if not "%SCRIPT_DIR:~0,-1%"=="%TARGET_DIR%" (
    echo [INFO] Installing launcher files to %TARGET_DIR%...
    if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"
    xcopy "%SCRIPT_DIR%*" "%TARGET_DIR%\" /E /Y /Q >nul
)

set VBS_SCRIPT=%TEMP%\SetupMclGlobal.vbs

echo Set WshShell = CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo Set UserEnv = WshShell.Environment("User") >> "%VBS_SCRIPT%"
echo UserPath = UserEnv("PATH") >> "%VBS_SCRIPT%"
echo TargetDir = "%TARGET_DIR%" >> "%VBS_SCRIPT%"
echo If InStr(1, UserPath, TargetDir, 1) = 0 Then >> "%VBS_SCRIPT%"
echo     If Right(UserPath, 1) ^<\^> ";" And UserPath ^<\^> "" Then UserPath = UserPath ^& ";" >> "%VBS_SCRIPT%"
echo     UserEnv("PATH") = UserPath ^& TargetDir >> "%VBS_SCRIPT%"
echo End If >> "%VBS_SCRIPT%"
echo DesktopPath = WshShell.SpecialFolders("Desktop") >> "%VBS_SCRIPT%"
echo Set Shortcut = WshShell.CreateShortcut(DesktopPath ^& "\Minecraft Launcher.lnk") >> "%VBS_SCRIPT%"
echo Shortcut.TargetPath = TargetDir ^& "\mcl.bat" >> "%VBS_SCRIPT%"
echo Shortcut.WorkingDirectory = TargetDir >> "%VBS_SCRIPT%"
echo Shortcut.Description = "Minecraft Launcher" >> "%VBS_SCRIPT%"
echo Shortcut.IconLocation = "%%SystemRoot%%\System32\shell32.dll, 13" >> "%VBS_SCRIPT%"
echo Shortcut.Save >> "%VBS_SCRIPT%"

cscript //nologo "%VBS_SCRIPT%"
if exist "%VBS_SCRIPT%" del "%VBS_SCRIPT%"

echo [SUCCESS] Installed launcher to %TARGET_DIR%!
echo [SUCCESS] Added 'mcl' command to global PATH! (You can type 'mcl' in any terminal)
echo [SUCCESS] Created 'Minecraft Launcher' shortcut on Desktop!
echo.
echo Launching Minecraft Launcher...
echo.
call "%TARGET_DIR%\mcl.bat"