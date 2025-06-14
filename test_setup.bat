@echo off
echo Testing Financial AI Assistant Setup...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Test Python imports
echo Testing Python imports...

python -c "import yfinance; print('✓ yfinance works')" 2>nul || echo "✗ yfinance failed"
python -c "import requests; print('✓ requests works')" 2>nul || echo "✗ requests failed"
python -c "import transformers; print('✓ transformers works')" 2>nul || echo "✗ transformers failed"
python -c "import sentence_transformers; print('✓ sentence_transformers works')" 2>nul || echo "✗ sentence_transformers failed"
python -c "import chromadb; print('✓ chromadb works')" 2>nul || echo "✗ chromadb failed"
python -c "import flask; print('✓ flask works')" 2>nul || echo "✗ flask failed"

echo.
echo Testing basic functionality...

python -c "
try:
    import yfinance as yf
    ticker = yf.Ticker('AAPL')
    info = ticker.info
    print('✓ Yahoo Finance connection works')
except Exception as e:
    print('✗ Yahoo Finance test failed:', str(e))
"

echo.
echo Setup test complete!
pause