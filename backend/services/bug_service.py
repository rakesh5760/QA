import requests
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

def check_special_link(url):
    """
    Validates mailto: and tel: formats.
    """
    if url.lower().startswith('mailto:'):
        import re
        parts = url.split(':')
        if len(parts) < 2: return "Invalid Format"
        email = parts[1].split('?')[0]
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(regex, email):
            return "Invalid Email Format"
        return "Valid"
    elif url.lower().startswith('tel:'):
        import re
        parts = url.split(':')
        if len(parts) < 2: return "Invalid Format"
        phone = parts[1]
        # Basic regex for phone numbers
        regex = r'^\+?[\d\s\-\(\)]{7,15}$'
        if not re.match(regex, phone):
            return "Invalid Phone Format"
        return "Valid"
    return "Unknown"

def is_valid_url(url):
    """
    Checks if a URL is valid for checking.
    """
    if not url or not isinstance(url, str):
        return False
        
    url = url.split('#')[0]
    if not url or url.startswith(('#')):
        return False
        
    # Return true for special links so they can be processed by detect_bugs
    if url.lower().startswith(('mailto:', 'tel:')):
        return True
        
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False

def check_link(url):
    """
    Sends a HEAD request with GET fallback to check if a link is valid.
    Handles mailto: and tel: separately.
    """
    if url.lower().startswith(('mailto:', 'tel:')):
        status = check_special_link(url)
        if status == "Valid":
            return url, 200
        else:
            return url, 400 # Treat as broken if format is wrong
            
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
