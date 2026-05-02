import logging

logger = logging.getLogger(__name__)

async def run_seo_audit(page, url):
    """
    Checks basic technical SEO elements.
    """
    logger.info("Running SEO audit")
    try:
        title = await page.title()
        meta_desc = await page.get_attribute("meta[name='description']", "content")
        h1_elements = await page.query_selector_all("h1")
        canonical = await page.get_attribute("link[rel='canonical']", "href")
        
        passed = True
        issues = []
        
        if not title:
            passed = False
            issues.append("Missing <title> tag.")
        elif len(title) < 10 or len(title) > 60:
            issues.append(f"Title length is {len(title)} (recommended 10-60 characters).")
            
        if not meta_desc:
            passed = False
            issues.append("Missing meta description.")
        elif len(meta_desc) < 50 or len(meta_desc) > 160:
            issues.append(f"Meta description length is {len(meta_desc)} (recommended 50-160 characters).")
            
        if len(h1_elements) == 0:
            passed = False
            issues.append("Missing <h1> tag.")
        elif len(h1_elements) > 1:
            passed = False
            issues.append("Multiple <h1> tags found. Only one recommended.")
            
        return {
            "passed": passed,
            "title": title,
            "meta_description": meta_desc,
            "h1_count": len(h1_elements),
            "canonical": canonical,
            "issues": issues
        }
    except Exception as e:
        logger.error(f"Failed to run SEO audit: {e}")
        return {"passed": False, "error": str(e)}
