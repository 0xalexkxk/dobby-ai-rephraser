@echo off
title Установка Dobby AI Text Rephraser
echo ================================
echo 🔥 УСТАНОВКА DOBBY AI 🔥
echo ================================
echo.
echo Устанавливаем зависимости...
echo.

pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ✅ Все зависимости установлены успешно!
    echo.
    echo Теперь можете запускать программу через start.bat
    echo или командой: python text_rephrase_ai.py
    echo.
    echo 📝 Не забудьте настроить API ключ в config.py
) else (
    echo.
    echo ❌ Ошибка установки зависимостей!
    echo.
    echo Возможные причины:
    echo - Python не установлен
    echo - Нет доступа к интернету
    echo - Проблемы с pip
)

echo.
pause