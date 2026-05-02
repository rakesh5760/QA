import asyncio
import argparse
import yaml
import logging
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

from src.crawler import AsyncCrawler
from src.extractor import extract_images, extract_forms
from src.ai_generator import AIGenerator
from src.test_runner import TestRunner
from src.scanners.a11y import run_axe_audit
from src.scanners.seo import run_seo_audit
from src.scanners.security import run_security_audit
from src.scanners.performance import run_performance_audit
from src.scanners.spelling import run_spelling_audit
from src.reporter import Reporter
from src.utils import setup_directories

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

async def run_analysis(url, description, config):
    output_dir, screenshots_dir = setup_directories(config)
    
    crawler = AsyncCrawler(
        base_url=url, 
        max_depth=config.get("crawl", {}).get("max_depth", 3),
        max_pages=config.get("crawl", {}).get("max_pages", 100)
    )
    
    ai_gen = AIGenerator(
        model=config.get("ai", {}).get("groq_model", "llama-3.3-70b-versatile"),
        temperature=config.get("ai", {}).get("temperature", 0.3)
    )
    test_runner = TestRunner(ai_gen, output_dir)
    
    scanners_config = config.get("scanners", {})
    
    results = {
        "base_url": url,
        "description": description,
        "pages": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        # 1. Crawl to find all internal URLs
        logger.info("=== Phase 1: Crawling ===")
        discovered_urls = await crawler.crawl(context)
        
        # 2. Analyze each URL
        logger.info(f"=== Phase 2: Analyzing {len(discovered_urls)} Pages ===")
        for page_url in discovered_urls:
            page_data = {
                "url": page_url,
                "scanners": {},
                "form_tests": []
            }
            
            # Use Playwright for dynamic checks
            page = await context.new_page()
            try:
                await page.goto(page_url, wait_until="domcontentloaded", timeout=config.get("timeouts", {}).get("page_load", 30000))
                
                # A11y (Axe)
                if scanners_config.get("enable_accessibility", True):
                    page_data["scanners"]["a11y"] = await run_axe_audit(page)
                    
                # SEO
                if scanners_config.get("enable_seo", True):
                    page_data["scanners"]["seo"] = await run_seo_audit(page, page_url)
                    
                # Spelling
                if scanners_config.get("enable_spelling", False):
                    page_data["scanners"]["spelling"] = await run_spelling_audit(page)
                    
                # Forms (AI Gen & Execution)
                page_data["form_tests"] = await test_runner.run_form_tests(page, page_url)
                
            except Exception as e:
                logger.error(f"Error scanning {page_url}: {e}")
            finally:
                await page.close()
                
            # Static/Subprocess checks (can run outside playwright context)
            if scanners_config.get("enable_security", True):
                page_data["scanners"]["security"] = run_security_audit(page_url)
                
            if scanners_config.get("enable_performance", True):
                perf_threshold = config.get("thresholds", {}).get("lighthouse_performance", 0.7)
                page_data["scanners"]["performance"] = run_performance_audit(page_url, threshold=perf_threshold)
                
            results["pages"].append(page_data)
            
        await browser.close()
        
    # 3. Report Generation
    logger.info("=== Phase 3: Reporting ===")
    reporter = Reporter(output_dir)
    reporter.generate_report(results)
    
    logger.info("Automation Complete!")

def main():
    parser = argparse.ArgumentParser(description="Static QA Automator")
    parser.add_argument("--url", required=True, help="Base URL of the static website to scan")
    parser.add_argument("--desc", default="", help="Optional description of the website")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Load Environment
    load_dotenv()
    
    # Load Config
    config = {}
    if os.path.exists(args.config):
        with open(args.config, "r") as f:
            config = yaml.safe_load(f)
            
    asyncio.run(run_analysis(args.url, args.desc, config))

if __name__ == "__main__":
    main()
