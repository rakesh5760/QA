import os
import uuid
import datetime
from urllib.parse import urlparse, urljoin

def normalize_url(base_url, href):
    """Resolves relative links to absolute URLs."""
    return urljoin(base_url, href)

def is_internal_url(base_url, target_url):
    """Checks if a URL belongs to the same domain as the base URL."""
    base_netloc = urlparse(base_url).netloc
    target_netloc = urlparse(target_url).netloc
    return base_netloc == target_netloc

def create_screenshot_path(output_dir="reports/screenshots"):
    """Creates a unique path for a screenshot."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
    return os.path.join(output_dir, filename)

def setup_directories(config):
    """Ensures output directories exist."""
    output_dir = config.get("report", {}).get("output_dir", "reports")
    screenshots_dir = os.path.join(output_dir, "screenshots")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(screenshots_dir, exist_ok=True)
    return output_dir, screenshots_dir
