import asyncio
import logging
from urllib.parse import urlparse
from src.utils import normalize_url, is_internal_url
from src.extractor import extract_links

logger = logging.getLogger(__name__)

class AsyncCrawler:
    def __init__(self, base_url, max_depth=3, max_pages=100, respect_robots=True):
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.respect_robots = respect_robots
        self.visited = set()
        self.to_visit = [(base_url, 0)]  # (url, depth)
        self.discovered_urls = []
        
    async def crawl(self, context):
        """
        Crawls the website starting from base_url.
        Returns a list of visited internal URLs.
        """
        logger.info(f"Starting crawl for {self.base_url} (max_depth={self.max_depth})")
        
        # NOTE: For simplicity, basic robots.txt check could be implemented here via urllib.robotparser
        # We will assume all are allowed if respect_robots is true for now.
        
        while self.to_visit and len(self.visited) < self.max_pages:
            current_url, depth = self.to_visit.pop(0)
            
            if current_url in self.visited:
                continue
                
            self.visited.add(current_url)
            self.discovered_urls.append(current_url)
            logger.info(f"Crawling ({len(self.visited)}/{self.max_pages}): {current_url} at depth {depth}")
            
            if depth >= self.max_depth:
                continue
                
            try:
                page = await context.new_page()
                response = await page.goto(current_url, wait_until="domcontentloaded", timeout=30000)
                
                if response and response.status < 400:
                    links = await extract_links(page)
                    for link in links:
                        full_url = normalize_url(self.base_url, link)
                        # Remove fragments
                        full_url = full_url.split("#")[0]
                        
                        if is_internal_url(self.base_url, full_url) and full_url not in self.visited:
                            # Avoid adding duplicates to the queue if they are already in the queue
                            if not any(url == full_url for url, _ in self.to_visit):
                                self.to_visit.append((full_url, depth + 1))
                
                await page.close()
            except Exception as e:
                logger.error(f"Failed to crawl {current_url}: {e}")
                
        return self.discovered_urls
