from axe_playwright_python.sync_playwright import Axe
import logging

logger = logging.getLogger(__name__)

async def run_axe_audit(page):
    """
    Injects and runs axe-core on the page to find accessibility violations.
    """
    logger.info("Running Axe accessibility audit")
    try:
        # Load axe-core script manually and evaluate
        axe_script_url = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js"
        import requests
        axe_script = requests.get(axe_script_url, timeout=5).text
        await page.add_script_tag(content=axe_script)
        
        axe_results = await page.evaluate("async () => await axe.run()")
        violations = axe_results.get("violations", [])
        
        # Filter for critical or serious
        critical_violations = [v for v in violations if v.get("impact") in ["critical", "serious"]]
        
        return {
            "passed": len(critical_violations) == 0,
            "total_violations": len(violations),
            "critical_violations": critical_violations
        }
    except Exception as e:
        logger.error(f"Failed to run axe audit: {e}")
        return {"passed": False, "error": str(e)}
