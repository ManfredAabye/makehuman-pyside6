@echo off
REM MakeHuman Build Automation Script

REM Set working directory
set WORK_DIR=%~dp0
cd /d "%WORK_DIR%"

REM Define paths
set USER_FOLDER=%WORK_DIR%\mhuser
set LOG_FILE=%USER_FOLDER%\log

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    exit /b 1
)

REM Create user folder if it does not exist
if not exist "%USER_FOLDER%" (
    mkdir "%USER_FOLDER%"
)

REM Install required Python packages
echo Installing required Python packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python packages.
    exit /b 1
)

REM Run MakeHuman to initialize user workspace
echo Initializing MakeHuman user workspace...
python makehuman.py --help >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to initialize MakeHuman user workspace.
    exit /b 1
)

REM Set preferences in MakeHuman
echo Setting user preferences...
python makehuman.py -A --nomultisampling
if errorlevel 1 (
    echo [ERROR] Failed to set preferences.
    exit /b 1
)

REM Download assets
echo Downloading assets...
python getpackages.py
if errorlevel 1 (
    echo [ERROR] Failed to download assets.
    exit /b 1
)

REM Compile targets
echo Compiling targets...
python compile_targets.py
if errorlevel 1 (
    echo [ERROR] Failed to compile targets.
    exit /b 1
)

REM Compile meshes
echo Compiling meshes...
python compile_meshes.py
if errorlevel 1 (
    echo [ERROR] Failed to compile meshes.
    exit /b 1
)

REM Completion message
echo [SUCCESS] MakeHuman build process completed successfully.
pause
