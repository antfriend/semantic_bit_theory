@echo off
REM Convenience script to start the Gradio app on Windows
REM Usage: start_gradio.bat

setlocal enabledelayedexpansion

echo.
echo 🚀 Starting Semantic Bit Theory Gradio App...
echo.

REM Get script directory (project root)
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found at: venv\
    echo.
    echo Please run setup first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install gradio graphviz
    echo   pip install -e ./semantic_bit
    exit /b 1
)

REM Check if semantic_bit package is installed
"%SCRIPT_DIR%venv\Scripts\python.exe" -c "import semantic_bit" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  semantic_bit package not installed
    echo.
    echo Installing now...
    "%SCRIPT_DIR%venv\Scripts\pip.exe" install -e ./semantic_bit
    echo.
)

REM Start the app
echo 📊 Opening Gradio at http://localhost:7860
echo    Press Ctrl+C to stop the server
echo.

"%SCRIPT_DIR%venv\Scripts\python.exe" "%SCRIPT_DIR%semantic_bit\demo\gradio_app.py"
