from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.async_api import async_playwright
import asyncio

app = FastAPI()

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
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=15000)
            cookies = await page.context.cookies()
            result["cookies"] = len(cookies)
            external_requests = []

            def log_request(route):
                if any(domain in route.request.url for domain in ["tracker", "ads", "analytics"]):
                    external_requests.append(route.request.url)

            page.on("request", log_request)
            await asyncio.sleep(3)
            result["trackers"] = len(set(external_requests))
            await browser.close()

    except Exception as e:
        result["warnings"].append(str(e))

    return result
