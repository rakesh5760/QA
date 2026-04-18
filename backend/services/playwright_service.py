import os
import uuid
import asyncio
from playwright.async_api import async_playwright
from backend.services.seo_service import analyze_seo
from backend.services.bug_service import detect_bugs
from backend.services.ai_service import get_ai_insights

SCREENSHOT_DIR = "screenshots"

# Ensure screenshots directory exists
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

async def analyze_website(url: str):
    """
    Launches a browser, navigates to the URL, extracts basic data, 
    and captures a screenshot.
    """
    results = {
        "url": url,
        "page_title": "",
        "links": [],
        "console_errors": [],
        "screenshot_path": "",
        "seo_analysis": {},
        "bug_report": {},
        "ai_insights": {}
    }

    async with async_playwright() as p:
        # Launch Chromium (headless by default)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Capture console errors
        page.on("console", lambda msg: results["console_errors"].append(msg.text) if msg.type == "error" else None)

        try:
            # Navigate to the URL
            await page.goto(url, wait_until="networkidle", timeout=60000)

            # Extract Page Title
            results["page_title"] = await page.title()

            # Extract All Links
            links = await page.query_selector_all("a")
            for link in links:
                href = await link.get_attribute("href")
                if href:
                    # Resolve relative URLs to absolute
                    from urllib.parse import urljoin
                    absolute_url = urljoin(url, href)
                    results["links"].append(absolute_url)

            # Extract full HTML for SEO Analysis
            html_content = await page.content()
            results["seo_analysis"] = analyze_seo(html_content)

            # Bug Detection (Broken links check)
            results["bug_report"] = await asyncio.to_thread(detect_bugs, results["links"])

            # AI Insights
            results["ai_insights"] = await asyncio.to_thread(get_ai_insights, results["seo_analysis"], results["bug_report"])

            # Capture Full Page Screenshot
            screenshot_name = f"screenshot_{uuid.uuid4().hex[:8]}.png"
            screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_name)
            await page.screenshot(path=screenshot_path, full_page=True)
            results["screenshot_path"] = screenshot_path

        except Exception as e:
            # If navigation fails, we still want to close the browser
            # but we'll re-raise or handle the specific error information
            raise Exception(f"Failed to analyze website: {str(e)}")

        finally:
            # Ensure the browser is closed even if an error occurs
            await browser.close()

    return results
