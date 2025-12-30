"""
Lyftr AI - Universal Website Scraper
Main FastAPI application
"""

from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ValidationError

from scraper import WebsiteScraper

app = FastAPI(title="Lyftr AI Website Scraper")
templates = Jinja2Templates(directory="templates")


class ScrapeRequest(BaseModel):
    url: str


@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Frontend UI"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    """Main scraping endpoint"""
    try:
        # Validate URL
        parsed = urlparse(request.url)
        if parsed.scheme not in ("http", "https"):
            raise HTTPException(
                status_code=400,
                detail="Only http and https URLs are supported"
            )
        
        scraper = WebsiteScraper(request.url)
        result = await scraper.scrape()
        
        return {"result": result}
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

