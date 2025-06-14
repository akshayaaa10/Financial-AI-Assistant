@echo off
echo ========================================
echo   Financial AI Assistant - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating it now...
    echo.
    
    REM Create virtual environment
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    
    echo Virtual environment created successfully!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

if not defined VIRTUAL_ENV (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated: %VIRTUAL_ENV%
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install core dependencies
echo Installing core dependencies...
pip install --quiet yfinance requests beautifulsoup4 feedparser newspaper3k pandas numpy python-dotenv flask

REM Install AI dependencies
echo Installing AI dependencies...
pip install --quiet transformers torch sentence-transformers chromadb scikit-learn

REM Install additional dependencies
echo Installing additional dependencies...
pip install --quiet nltk matplotlib plotly

REM Download NLTK data
echo Downloading NLTK data...
python -c "import nltk; import ssl; ssl._create_default_https_context = ssl._create_unverified_context; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('vader_lexicon', quiet=True)"

REM Create necessary directories
echo Creating directories...
if not exist "cache" mkdir cache
if not exist "vector_db" mkdir vector_db
if not exist "logs" mkdir logs

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    echo # Optional API Keys for enhanced functionality > .env
    echo NEWS_API_KEY=your_newsapi_key_here >> .env
    echo ALPHA_VANTAGE_API_KEY=your_alphavantage_key_here >> .env
    echo. >> .env
    echo # Flask settings >> .env
    echo SECRET_KEY=your_secret_key_here >> .env
    echo. >> .env
    echo # Created by quick_start.bat >> .env
)

echo.
echo ========================================
echo   Starting Financial AI Assistant
echo ========================================
echo.
echo IMPORTANT NOTES:
echo - First startup may take 2-5 minutes to download AI models
echo - The application will run on: http://localhost:8888
echo - Press Ctrl+C to stop the server
echo.
echo Starting application...
echo.

REM Start the application
python app.py

echo.
echo Application stopped.
pause