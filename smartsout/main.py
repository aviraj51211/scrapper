# app/main.py
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from scrapper.smartsocut.niche_finder import run_niche_finder_export

# Load environment variables
load_dotenv()

# Create limited thread pool (max 2 concurrent scrapers)
SCRAPER_EXECUTOR = ThreadPoolExecutor(max_workers=2)

# FastAPI app
app = FastAPI(title="SmartScout Scraper API")

class ScrapeRequest(BaseModel):
    search_text: str
    username: str 
    password: str

@app.get("/Samrtsouct/subcategory")
async def scrape_endpoint(request: ScrapeRequest):
    """
    Trigger SmartScout Niche Finder export.
    Uses thread pool to avoid blocking the async event loop.
    Max 2 concurrent scrapers allowed.
    """
    try:
        # Run blocking Selenium in a thread
        result = await asyncio.get_event_loop().run_in_executor(
            SCRAPER_EXECUTOR,
            run_niche_finder_export,
            request.search_text,
            request.username,
            request.password
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")
    
app.get("/Samrtsouct/labelranker    ")
async def scrape_endpoint(request: ScrapeRequest):
    """
    Trigger SmartScout Niche Finder export.
    Uses thread pool to avoid blocking the async event loop.
    Max 2 concurrent scrapers allowed.
    """
    try:
        # Run blocking Selenium in a thread
        result = await asyncio.get_event_loop().run_in_executor(
            SCRAPER_EXECUTOR,
            run_niche_finder_export,
            request.search_text,
            request.username,
            request.password
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")