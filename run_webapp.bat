@echo off
chcp 65001 > nul
set VENV_DIR=.venv

if not exist %VENV_DIR% (
    echo Creating virtual environment...
    py -m venv %VENV_DIR%
)
call %VENV_DIR%\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt > nul

if not exist .env (
    echo ERROR: .env file not found. Please set your API key.
    pause
    exit /b 1
)

echo Starting Web Application...
streamlit run app.py

pause
