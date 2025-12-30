# Universal Website Scraper

A full-stack web scraping application that extracts structured content from websites, handling both static HTML and JavaScript-rendered content.

## Features

- **Static Scraping**: Fast HTML parsing using `requests` and `beautifulsoup4`
- **JS Rendering Fallback**: Automatic fallback to Playwright for JavaScript-heavy sites
- **Interactive Scraping**: Handles tabs, "Load more" buttons, and pagination
- **Scroll & Pagination**: Supports infinite scroll and pagination to depth ≥ 3
- **Section-Aware Extraction**: Intelligently groups content into semantic sections
- **JSON API**: RESTful API with structured JSON responses
- **Web UI**: Beautiful frontend for testing and viewing results

## Setup & Run

### Prerequisites

- Python 3.10 or higher
- pip

### Quick Start

**On Linux/Mac:**
1. Make the run script executable:
```bash
chmod +x run.sh
```

2. Run the application:
```bash
./run.sh
```

**On Windows:**
1. Run the batch file:
```cmd
run.bat
```

Or double-click `run.bat` in Windows Explorer.

The script will:
- Create a virtual environment (if it doesn't exist)
- Install all dependencies
- Install Playwright browsers (optional, for JS rendering)
- Start the server on `http://localhost:8000`

### Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (optional, for JS rendering)
playwright install chromium

# Run the server
uvicorn app:app --host 0.0.0.0 --port 8000
```

**Note:** If you don't have C++ build tools installed (common on Windows), the server will still work for static scraping. Playwright installation may require additional setup, but it's optional - the scraper will fall back to static scraping if Playwright is not available.

## Usage

### Web Interface

1. Open `http://localhost:8000` in your browser
2. Enter a URL in the input field
3. Click "Scrape" to start scraping
4. View sections in the expandable accordion
5. Download the full JSON result using the "Download JSON" button

### API Endpoints

#### GET /healthz

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

#### POST /scrape

Scrape a website and return structured JSON.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
See the assignment specification for the complete response schema.

## Test URLs

The following URLs were used for testing:

1. **https://en.wikipedia.org/wiki/Artificial_intelligence**
   - Static page with rich content
   - Good for testing section extraction and meta data

2. **https://vercel.com/**
   - JavaScript-heavy marketing page
   - Tests JS rendering fallback and interactive elements

3. **https://news.ycombinator.com/**
   - Pagination-based content
   - Tests pagination handling and depth ≥ 3 requirement

## Project Structure

```
.
├── app.py                 # FastAPI application
├── scraper.py             # Core scraping logic
├── requirements.txt       # Python dependencies
├── run.sh                 # Run script
├── README.md             # This file
├── design_notes.md       # Design decisions and strategies
├── capabilities.json     # Feature capabilities
└── templates/
    └── index.html        # Frontend UI
```

## Known Limitations

1. **Same-Origin Limitation**: The scraper primarily focuses on the initial domain. Cross-origin navigation is limited.

2. **Timeout Handling**: Some sites may block automation or have aggressive rate limiting. Errors are captured in the `errors` array.

3. **Content Filtering**: Noise filtering (cookie banners, modals) uses heuristics and may not catch all cases.

4. **Playwright Browser**: Requires Chromium to be installed. The run script handles this automatically.

5. **Large Pages**: Very large pages may have truncated content in `rawHtml` fields.

## Dependencies

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `requests`: HTTP client for static scraping
- `selectolax`: Fast HTML parser
- `playwright`: Browser automation for JS rendering
- `jinja2`: Template engine for frontend

## License

This project is created for the Lyftr AI full-stack assignment.


