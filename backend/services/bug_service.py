import requests
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

def is_valid_url(url):
    """
    Checks if a URL is valid and has a scheme (http/https).
    Skips empty links, tel, mailto, etc.
    """
    if not url or url.startswith(('javascript:', 'mailto:', 'tel:', '#')):
        return False
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def check_link(url):
    """
    Sends a GET request to a URL and returns the status code.
    Handles timeouts and exceptions.
    """
    try:
        # Using a small timeout to avoid blocking too long
        response = requests.get(url, timeout=5, stream=True)
        # Using stream=True and not reading content to save time/bandwidth
        return url, response.status_code
    except requests.exceptions.RequestException:
        return url, -1  # Indicates an exception occurred (invalid URL or timeout)

def detect_bugs(links: list):
    """
    Iterates through links, checks their status, and returns a structured report.
    """
    # Filter valid links first
    valid_format_links = [link for link in list(set(links)) if is_valid_url(link)]
    
    report = {
        "total_links_checked": len(valid_format_links),
        "valid_links": 0,
        "broken_links": [],
        "server_errors": []
    }

    # Use ThreadPoolExecutor for efficiency
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_link, valid_format_links))

    for url, status_code in results:
        if 200 <= status_code < 300:
            report["valid_links"] += 1
        elif status_code in [400, 404]:
            report["broken_links"].append({"url": url, "status_code": status_code})
        elif status_code >= 500:
            report["server_errors"].append({"url": url, "status_code": status_code})
        elif status_code == -1:
            # Treating timeouts or connection errors as server/broken contextually
            # but strictly following the 400/404/500 classification requested.
            # We'll put them in broken links if status_code is -1 for now.
            report["broken_links"].append({"url": url, "status_code": "Timeout/Error"})

    return report
