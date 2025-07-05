@echo off
cd /d "%~dp0"
title Dobby AI Rephraser PyQt6
echo =====================================
echo    DOBBY AI REPHRASER PYQT6 VERSION   
echo =====================================
echo.
echo Current directory: %CD%
echo.
echo Installing PyQt6 (may take a few minutes first time)...
pip install PyQt6 >nul 2>&1
echo Installing other requirements...
pip install requests pyperclip pyautogui pynput >nul 2>&1
echo.
echo Features:
echo   Modern Native Windows Interface
echo   Exact React Component Design  
echo   Real Dobby Dog Image Support
echo   Powered by Fireworks AI
echo   Native Windows Look and Feel
echo.
echo Starting PyQt6 version...
echo.
python "%~dp0dobby_qt.py"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start PyQt6 version!
    echo Make sure all dependencies are installed.
    pause
)