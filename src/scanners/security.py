import logging
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def run_security_audit(url):
    """
    Checks HTTP response headers for security best practices.
    """
    logger.info("Running Security headers audit")
    try:
        parsed_url = urlparse(url)
        is_https = parsed_url.scheme == "https"
        
        response = requests.get(url, timeout=10, verify=True)
        headers = {k.lower(): v for k, v in response.headers.items()}
        
        required_headers = [
            "strict-transport-security",
            "content-security-policy",
            "x-frame-options",
            "x-content-type-options"
        ]
        
        missing = [h for h in required_headers if h not in headers]
        
        passed = len(missing) == 0 and is_https
        issues = []
        if not is_https:
            issues.append("Site is not using HTTPS.")
        if missing:
            issues.append(f"Missing headers: {', '.join(missing)}")
            
        return {
            "passed": passed,
            "is_https": is_https,
            "missing_headers": missing,
            "issues": issues
        }
    except Exception as e:
        logger.error(f"Failed to run security audit: {e}")
        return {"passed": False, "error": str(e)}
