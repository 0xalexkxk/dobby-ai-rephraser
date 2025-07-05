@echo off
title Building Dobby AI Rephraser EXE
echo =====================================
echo    DOBBY AI REPHRASER - EXE BUILDER
echo =====================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo Installing build requirements...
pip install pyinstaller >nul 2>&1

echo.
echo Building EXE file...
python build_exe.py

if %errorlevel% equ 0 (
    echo.
    echo =====================================
    echo    BUILD SUCCESSFUL!
    echo =====================================
    echo.
    echo Your EXE file is ready: DobbyAI-Rephraser.exe
    echo.
) else (
    echo.
    echo =====================================
    echo    BUILD FAILED!
    echo =====================================
    echo.
    echo Check the error messages above.
    echo.
)

pause