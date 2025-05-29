from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.async_api import async_playwright
import asyncio

app = FastAPI()

 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class URLRequest(BaseModel):
    url: str

@app.post("/analyze")
async def analyze_url(req: URLRequest):
    url = req.url
    result = {
        "url": url,
        "trackers": 0,
        "cookies": 0,
        "warnings": []
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            external_requests = []

            
            page.on("request", lambda request: external_requests.append(request.url) if any(term in request.url.lower() for term in ["tracker", "ads", "analytics", "doubleclick", "facebook", "google"]) else None)

            await page.goto(url, timeout=15000)
            await asyncio.sleep(3)  

            cookies = await context.cookies()
            result["cookies"] = len(cookies)
            result["trackers"] = len(set(external_requests))

            await browser.close()

    except Exception as e:
        result["warnings"].append(str(e))

    return result
