@echo off
REM Lyftr AI - Website Scraper Run Script for Windows

echo 🚀 Starting Lyftr AI Website Scraper...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Install Playwright browsers
echo 🌐 Installing Playwright browsers...
playwright install chromium

REM Start the server
echo ✨ Starting server on http://localhost:8000
echo 📝 Open http://localhost:8000 in your browser
echo.

uvicorn app:app --host 0.0.0.0 --port 8000

pause

