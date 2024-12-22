@echo off
REM MakeHuman Build Automation Script

REM Set working directory
set "WORK_DIR=%~dp0"
cd /d "%WORK_DIR%"

REM Define paths
set "USER_FOLDER=%WORK_DIR%mhuser"
set "LOG_FILE=%USER_FOLDER%\log"

REM Create user folder if it does not exist
if not exist "%USER_FOLDER%" (
    mkdir "%USER_FOLDER%"
)

REM Install required Python packages
echo Installing required Python packages...
python.exe -m pip install PySide6>=6.5.0
if errorlevel 1 (
    echo [ERROR] Failed to install PySide6.
    exit /b 1
)
python.exe -m pip install PyOpenGL>=3.1.0
if errorlevel 1 (
    echo [ERROR] Failed to install PyOpenGL.
    exit /b 1
)
::python.exe -m pip install numpy>=1.17.4
python.exe -m pip install numpy>=1.21.0
if errorlevel 1 (
    echo [ERROR] Failed to install numpy.
    exit /b 1
)
python.exe -m pip install psutil>=5.9.0
if errorlevel 1 (
    echo [ERROR] Failed to install psutil.
    exit /b 1
)

REM Run MakeHuman to initialize user workspace
echo Initializing MakeHuman user workspace...
python.exe makehuman.py --help >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to initialize MakeHuman user workspace.
    exit /b 1
)


REM Set preferences in MakeHuman
echo Setting user preferences...
python.exe makehuman.py -A --nomultisampling >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to set preferences.
    pause
    exit /b 1
)

REM Download assets
echo Downloading assets...
python.exe getpackages.py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to download assets.
    exit /b 1
)

REM Compile targets
echo Compiling targets...
python.exe compile_targets.py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to compile targets.
    exit /b 1
)

REM Compile meshes
echo Compiling meshes...
python.exe compile_meshes.py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to compile meshes.
    exit /b 1
)

REM Completion message
echo [SUCCESS] MakeHuman build process completed successfully.
pause


