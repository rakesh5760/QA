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
    and captures screenshots at multiple breakpoints.
    """
    results = {
        "url": url,
        "page_title": "",
        "links": [],
        "console_errors": [],
        "console_warnings": [],
        "resource_errors": [],
        "screenshots": {},
        "seo_analysis": {},
        "seo_score_data": {},
        "qa_checks": {},
        "accessibility_audit": {},
        "performance_metrics": {},
        "security_check": {},
        "bug_report": {},
        "ai_insights": {}
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Start with a desktop context
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        # 1. Error Tracking
        def handle_console(msg):
            if msg.type == "error":
                results["console_errors"].append(msg.text)
            elif msg.type == "warning":
                results["console_warnings"].append(msg.text)

        def handle_request_failed(request):
            results["resource_errors"].append({
                "url": request.url,
                "error": request.failure,
                "resource_type": request.resource_type
            })

        page.on("console", handle_console)
        page.on("requestfailed", handle_request_failed)

        try:
            # 2. Performance & Navigation
            start_time = time.time()
            response = await page.goto(url, wait_until="networkidle", timeout=60000)
            load_time = time.time() - start_time
            
            page_status = response.status if response else 0

            # 3. Capture Core Web Vitals (Simple)
            vitals = await page.evaluate("""() => {
                const nav = performance.getEntriesByType('navigation')[0];
                const paint = performance.getEntriesByType('paint');
                const fcp = paint.find(entry => entry.name === 'first-contentful-paint');
                
                return {
                    ttfb: nav ? nav.responseStart - nav.requestStart : 0,
                    fcp: fcp ? fcp.startTime : 0,
                    dom_ready: nav ? nav.domContentLoadedEventEnd - nav.fetchStart : 0,
                    window_load: nav ? nav.loadEventEnd - nav.fetchStart : 0
                };
            }""")
            results["performance_metrics"] = {
                "load_time_s": round(load_time, 2),
                "ttfb_ms": round(vitals["ttfb"], 2),
                "fcp_ms": round(vitals["fcp"], 2),
                "dom_ready_ms": round(vitals["dom_ready"], 2),
                "window_load_ms": round(vitals["window_load"], 2)
            }

            # 4. Accessibility Audit (Axe-Core)
            # Fetch axe-core from CDN for injection
            try:
                axe_script_url = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js"
                axe_script = requests.get(axe_script_url, timeout=5).text
                await page.add_script_tag(content=axe_script)
                axe_results = await page.evaluate("async () => await axe.run()")
                results["accessibility_audit"] = {
                    "score": 100 - (len(axe_results.get("violations", [])) * 5), # Simple heuristic
                    "violations": [
                        {
                            "id": v["id"],
                            "impact": v["impact"],
                            "description": v["description"],
                            "nodes_count": len(v["nodes"])
                        } for v in axe_results.get("violations", [])
                    ],
                    "passes_count": len(axe_results.get("passes", []))
                }
            except Exception as axe_err:
                results["accessibility_audit"] = {"error": f"Failed to run axe audit: {str(axe_err)}"}

            # 5. Security Header Check
            try:
                sec_res = requests.get(url, timeout=10, verify=True)
                headers = sec_res.headers
                results["security_check"] = {
                    "is_https": url.startswith("https://"),
                    "headers": {
                        "HSTS": "Strict-Transport-Security" in headers,
                        "CSP": "Content-Security-Policy" in headers,
                        "X-Frame-Options": "X-Frame-Options" in headers,
                        "X-Content-Type": "X-Content-Type-Options" in headers,
                        "Referrer-Policy": "Referrer-Policy" in headers
                    },
                    "missing_headers": [h for h in ["Strict-Transport-Security", "Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options"] if h not in headers]
                }
            except Exception as sec_err:
                results["security_check"] = {"error": f"Security check failed: {str(sec_err)}"}

            # 6. Basic Data Extraction
            results["page_title"] = await page.title()
            links = await page.query_selector_all("a")
            for link in links:
                href = await link.get_attribute("href")
                if href:
                    from urllib.parse import urljoin
                    results["links"].append(urljoin(url, href))

            # UI Elements Counts & Basic QA
            buttons = await page.query_selector_all("button, input[type='button'], input[type='submit']")
            inputs = await page.query_selector_all("input:not([type='button']):not([type='submit']), select, textarea")
            forms = await page.query_selector_all("form")
            
            qa_issues = []
            if load_time > 3: qa_issues.append(f"Slow page load: {load_time:.2f}s")
            if page_status != 200: qa_issues.append(f"Status {page_status}")
            
            results["qa_checks"] = {
                "console_errors": results["console_errors"],
                "resource_errors": results["resource_errors"],
                "ui_elements": {"buttons": len(buttons), "inputs": len(inputs), "forms": len(forms)},
                "issues": qa_issues
            }

            # 7. Multi-Breakpoint Screenshots
            breakpoints = {
                "desktop": (1920, 1080),
                "tablet": (768, 1024),
                "mobile": (375, 812)
            }
            
            for bp_name, (width, height) in breakpoints.items():
                await page.set_viewport_size({"width": width, "height": height})
                await asyncio.sleep(0.5) # Allow for layout shifts
                shot_name = f"{bp_name}_{uuid.uuid4().hex[:6]}.png"
                shot_path = os.path.join(SCREENSHOT_DIR, shot_name)
                await page.screenshot(path=shot_path, full_page=True)
                results["screenshots"][bp_name] = shot_path

            # SEO & AI Integration
            html_content = await page.content()
            results["seo_analysis"] = analyze_seo(html_content)
            
            from urllib.parse import urlparse
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            tech_data = {
                "is_https": results["security_check"].get("is_https", False),
                "has_sitemap": await asyncio.to_thread(lambda: requests.get(f"{base_url}/sitemap.xml", timeout=5).status_code == 200),
                "has_robots": await asyncio.to_thread(lambda: requests.get(f"{base_url}/robots.txt", timeout=5).status_code == 200),
                "load_time": load_time,
                "html_size_kb": len(html_content) / 1024
            }
            results["seo_score_data"] = calculate_seo_score(results["seo_analysis"], tech_data)
            results["bug_report"] = await asyncio.to_thread(detect_bugs, results["links"])
            results["ai_insights"] = await asyncio.to_thread(get_ai_insights, results["seo_analysis"], results["bug_report"], (await page.inner_text("body"))[:10000])

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise Exception(f"Analysis failed: {str(e)}")
        finally:
            await browser.close()

    return results
