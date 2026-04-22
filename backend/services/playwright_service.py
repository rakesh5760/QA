import os
import uuid
import asyncio
import time
import requests
from playwright.async_api import async_playwright
from backend.services.seo_service import analyze_seo, calculate_seo_score
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
        "console_warnings": [],
        "screenshot_path": "",
        "seo_analysis": {},
        "seo_score_data": {},
        "qa_checks": {},
        "bug_report": {},
        "ai_insights": {}
    }

    async with async_playwright() as p:
        # Launch Chromium (headless by default)
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Capture console logs (errors and warnings)
        def handle_console(msg):
            if msg.type == "error":
                results["console_errors"].append(msg.text)
            elif msg.type == "warning":
                results["console_warnings"].append(msg.text)

        page.on("console", handle_console)

        try:
            # Navigate to the URL and measure load time
            start_time = time.time()
            response = await page.goto(url, wait_until="networkidle", timeout=60000)
            load_time = time.time() - start_time
            
            page_status = response.status if response else 0

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

            # --- QA Enhancement Module Checks ---
            # 1. UI Elements Counts
            buttons = await page.query_selector_all("button, input[type='button'], input[type='submit']")
            inputs = await page.query_selector_all("input:not([type='button']):not([type='submit']), select, textarea")
            forms = await page.query_selector_all("form")
            
            # Accessibility: Button text/label check
            buttons_missing_label = 0
            for btn in buttons:
                text = await btn.inner_text()
                label = await btn.get_attribute("aria-label")
                title = await btn.get_attribute("title")
                if not text.strip() and not label and not title:
                    buttons_missing_label += 1

            qa_issues = []
            if load_time > 3:
                qa_issues.append(f"Slow page load: {load_time:.2f}s (Target: < 3s)")
            if page_status != 200:
                qa_issues.append(f"Main page returned non-200 status: {page_status}")
            if len(buttons) == 0:
                qa_issues.append("No buttons found on the page")
            if len(forms) == 0:
                qa_issues.append("No forms found on the page")
            if buttons_missing_label > 0:
                qa_issues.append(f"{buttons_missing_label} button(s) missing text or aria-label")

            results["qa_checks"] = {
                "console_errors": results["console_errors"],
                "console_warnings": results["console_warnings"],
                "load_time": round(load_time, 2),
                "page_status": page_status,
                "ui_elements": {
                    "buttons_count": len(buttons),
                    "inputs_count": len(inputs),
                    "forms_count": len(forms),
                    "buttons_missing_label": buttons_missing_label
                },
                "issues": qa_issues
            }

            # Extract visible text for AI Content Analysis
            page_text = await page.inner_text("body")
            # Truncate to avoid exceeding LLM context limits (10k chars is usually safe)
            results["page_text"] = page_text[:10000]

            # Extract full HTML for SEO Analysis
            html_content = await page.content()
            results["seo_analysis"] = analyze_seo(html_content)

            # --- Technical & Performance Metrics for Scoring ---
            from urllib.parse import urlparse
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            
            def check_file(url_to_check):
                try:
                    r = requests.get(url_to_check, timeout=5)
                    return r.status_code == 200
                except:
                    return False

            has_sitemap = await asyncio.to_thread(check_file, f"{base_url}/sitemap.xml")
            has_robots = await asyncio.to_thread(check_file, f"{base_url}/robots.txt")
            
            tech_data = {
                "is_https": url.startswith("https://"),
                "has_sitemap": has_sitemap,
                "has_robots": has_robots,
                "load_time": load_time,
                "html_size_kb": len(html_content) / 1024
            }
            
            # Calculate SEO Score
            results["seo_score_data"] = calculate_seo_score(results["seo_analysis"], tech_data)

            # Bug Detection (Broken links check)
            results["bug_report"] = await asyncio.to_thread(detect_bugs, results["links"])

            # AI Insights
            results["ai_insights"] = await asyncio.to_thread(get_ai_insights, results["seo_analysis"], results["bug_report"], results.get("page_text", ""))

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
