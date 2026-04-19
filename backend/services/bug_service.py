import requests
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

def is_valid_url(url):
    """
    Checks if a URL is valid for HTTP/HTTPS checking.
    Strips fragments and ignores non-HTTP schemes.
    """
    if not url or not isinstance(url, str):
        return False
        
    # Remove fragments client-side anchors
    url = url.split('#')[0]
    
    # Ignore empty after stripping or simple anchors
    if not url or url.startswith(('#')):
        return False
        
    # Explicitly ignore common non-http schemes
    if url.lower().startswith(('javascript:', 'mailto:', 'tel:')):
        return False
        
    try:
        result = urlparse(url)
        # Must have scheme and domain
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False

def check_link(url):
    """
    Sends a HEAD request with GET fallback to check if a link is valid.
    Treats 403 and 999 (LinkedIn bot blocking) as valid.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Strip fragment before check
    url_to_check = url.split('#')[0]
    
    try:
        # Try HEAD first for efficiency
        response = requests.head(url_to_check, timeout=5, headers=headers, allow_redirects=True)
        
        # Fallback to GET if HEAD is not allowed or fails with anything other than 404
        if response.status_code == 405 or (400 <= response.status_code < 500 and response.status_code != 404):
            response = requests.get(url_to_check, timeout=5, headers=headers, stream=True, allow_redirects=True)
            
        # Treat 403/999 as valid (some sites block automated tools aggressively)
        if response.status_code in [403, 999]:
            return url, 200
            
        return url, response.status_code
    except requests.exceptions.RequestException:
        # Final fallback check with GET in case HEAD specifically failed connection
        try:
            response = requests.get(url_to_check, timeout=5, headers=headers, stream=True, allow_redirects=True)
            if response.status_code in [403, 999]:
                return url, 200
            return url, response.status_code
        except:
            return url, -1

def detect_bugs(links: list):
    """
    Iterates through links, checks their status, and returns a structured report.
    Deduplicates and cleans links before checking.
    """
    # 1. Clean and deduplicate links
    cleaned_links = []
    for link in links:
        if is_valid_url(link):
            # Resolve URL and strip fragments for deduplication
            clean = link.split('#')[0]
            if clean not in cleaned_links:
                cleaned_links.append(clean)
    
    report = {
        "total_links_checked": len(cleaned_links),
        "valid_links": 0,
        "broken_links": [],
        "server_errors": []
    }

    if not cleaned_links:
        return report

    # Use ThreadPoolExecutor for efficiency
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_link, cleaned_links))

    for url, status_code in results:
        if 200 <= status_code < 400:
            report["valid_links"] += 1
        elif status_code in [400, 404, 410]:
            report["broken_links"].append({"url": url, "status_code": status_code})
        elif status_code >= 500:
            report["server_errors"].append({"url": url, "status_code": status_code})
        elif status_code == -1:
            report["broken_links"].append({"url": url, "status_code": "Connection Failed"})
        else:
            # Other 4xx errors
            report["broken_links"].append({"url": url, "status_code": status_code})

    return report
