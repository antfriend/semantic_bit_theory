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

REM Check if required packages are installed
set MISSING_DEPS=

"%SCRIPT_DIR%venv\Scripts\python.exe" -c "import gradio" >nul 2>&1
if errorlevel 1 set MISSING_DEPS=%MISSING_DEPS% gradio

"%SCRIPT_DIR%venv\Scripts\python.exe" -c "import graphviz" >nul 2>&1
if errorlevel 1 set MISSING_DEPS=%MISSING_DEPS% graphviz

"%SCRIPT_DIR%venv\Scripts\python.exe" -c "import semantic_bit" >nul 2>&1
if errorlevel 1 set MISSING_DEPS=%MISSING_DEPS% semantic_bit

if not "%MISSING_DEPS%"=="" (
    echo ⚠️  Missing dependencies:%MISSING_DEPS%
    echo.
    echo Installing now...

    echo %MISSING_DEPS% | findstr /C:"gradio" >nul && (
        "%SCRIPT_DIR%venv\Scripts\pip.exe" install gradio graphviz
    )

    echo %MISSING_DEPS% | findstr /C:"semantic_bit" >nul && (
        "%SCRIPT_DIR%venv\Scripts\pip.exe" install -e ./semantic_bit
    )

    echo.
    echo ✅ Dependencies installed
    echo.
)

REM Start the app
echo 📊 Opening Gradio at http://localhost:7860
echo    Press Ctrl+C to stop the server
echo.

"%SCRIPT_DIR%venv\Scripts\python.exe" "%SCRIPT_DIR%semantic_bit\demo\gradio_app.py"
