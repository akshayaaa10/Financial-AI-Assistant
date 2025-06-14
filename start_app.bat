@echo off
echo Starting Financial AI Assistant...

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Virtual environment not found!
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

echo.
echo Starting the AI system...
echo This may take a few minutes on first run to download models...
echo.
echo Open your browser to: http://localhost:8888
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python app.py

pause