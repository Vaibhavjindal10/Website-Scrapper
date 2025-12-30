#!/bin/bash

# Lyftr AI - Website Scraper Run Script

set -e

echo "🚀 Starting Lyftr AI Website Scraper..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Start the server
echo "✨ Starting server on http://localhost:8000"
echo "📝 Open http://localhost:8000 in your browser"
echo ""

uvicorn app:app --host 0.0.0.0 --port 8000

