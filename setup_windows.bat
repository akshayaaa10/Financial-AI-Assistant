@echo off
echo Setting up Financial AI Assistant on Windows...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing Python packages...
pip install -r requirements.txt

REM Download NLTK data
echo Downloading NLTK data...
python -c "import nltk; import ssl; ssl._create_default_https_context = ssl._create_unverified_context; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

REM Create necessary directories
echo Creating directories...
if not exist "cache" mkdir cache
if not exist "vector_db" mkdir vector_db
if not exist "logs" mkdir logs

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    echo # Optional API Keys > .env
    echo NEWS_API_KEY=your_newsapi_key_here >> .env
    echo ALPHA_VANTAGE_API_KEY=your_alphavantage_key_here >> .env
    echo. >> .env
    echo # Flask settings >> .env
    echo SECRET_KEY=your_secret_key_here >> .env
)

echo.
echo Setup complete!
echo.
echo To start the application:
echo 1. venv\Scripts\activate.bat
echo 2. python app.py
echo.
echo Then open: http://localhost:8888
echo.
pause