"""
Crawler module for fetching API documentation websites.
"""

import asyncio
import logging
import re
import time
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from src.crawler.parser import ApiDocParser
from src.storage.repository import ApiRepository
from src.storage.models import ApiEndpoint, ApiPage, ApiSchema

logger = logging.getLogger(__name__)


class ApiDocCrawler:
    """Crawler for API documentation websites."""
    
    def __init__(self, repository: ApiRepository, concurrency: int = 5, delay: float = 0.5):
        """
        Initialize the API documentation crawler.
        
        Args:
            repository: Repository for storing crawled data
            concurrency: Maximum number of concurrent requests
            delay: Delay between requests to the same domain (in seconds)
        """
        self.repository = repository
        self.concurrency = concurrency
        self.delay = delay
        self.parser = ApiDocParser()
        
        self._visited_urls = set()
        self._domain_last_access = {}
        self._semaphore = asyncio.Semaphore(concurrency)
    
    async def crawl(self, base_url: str, max_pages: int = 500) -> None:
        """
        Crawl the API documentation website starting from the base URL.
        
        Args:
            base_url: The starting URL for crawling
            max_pages: Maximum number of pages to crawl
        """
        self._visited_urls = set()
        parsed_url = urlparse(base_url)
        self.base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Store site information
        site_info = {
            "base_url": base_url,
            "title": await self._get_site_title(base_url),
            "last_crawled": time.time()
        }
        self.repository.save_site_info(site_info)
        
        # Use a queue for BFS crawling
        queue = asyncio.Queue()
        await queue.put(base_url)
        
        tasks = []
        for _ in range(min(self.concurrency, max_pages)):
            task = asyncio.create_task(self._worker(queue, max_pages))
            tasks.append(task)
        
        # Wait for all workers to complete
        await queue.join()
        
        # Cancel any remaining tasks
        for task in tasks:
            task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"Crawling completed. Processed {len(self._visited_urls)} pages.")
    
    async def _worker(self, queue: asyncio.Queue, max_pages: int) -> None:
        """Worker for processing URLs from the queue."""
        while True:
            url = await queue.get()
            
            try:
                if url in self._visited_urls or len(self._visited_urls) >= max_pages:
                    queue.task_done()
                    continue
                
                self._visited_urls.add(url)
                
                # Respect the delay for the domain
                domain = urlparse(url).netloc
                if domain in self._domain_last_access:
                    last_access = self._domain_last_access[domain]
                    wait_time = max(0, self.delay - (time.time() - last_access))
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)
                
                # Process the page
                async with self._semaphore:
                    logger.info(f"Crawling: {url}")
                    self._domain_last_access[domain] = time.time()
                    
                    content = await self._fetch_url(url)
                    if not content:
                        queue.task_done()
                        continue
                    
                    # Parse the page content
                    soup = BeautifulSoup(content, "lxml")
                    
                    # Extract and store API information
                    await self._process_page(url, soup)
                    
                    # Find and enqueue links
                    links = self._extract_links(soup, url)
                    for link in links:
                        if link not in self._visited_urls:
                            await queue.put(link)
            
            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
            
            finally:
                queue.task_done()
    
    async def _get_site_title(self, url: str) -> str:
        """Get the title of the API documentation site."""
        content = await self._fetch_url(url)
        if not content:
            return "Unknown API Documentation"
        
        soup = BeautifulSoup(content, "lxml")
        title_tag = soup.find("title")
        
        if title_tag:
            return title_tag.text.strip()
        else:
            # Try to find another element that might contain the site title
            potential_title = soup.find("h1")
            if potential_title:
                return potential_title.text.strip()
            
            return "Unknown API Documentation"
    
    async def _fetch_url(self, url: str) -> str:
        """Fetch content from a URL."""
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(url, headers={
                    "User-Agent": "ApiDocsCrawler/1.0",
                    "Accept": "text/html,application/xhtml+xml"
                })
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
                    return ""
                
                # Check if the content is HTML
                content_type = response.headers.get("Content-Type", "")
                if not any(ct in content_type.lower() for ct in ["text/html", "application/xhtml+xml"]):
                    return ""
                
                return response.text
        
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return ""
    
    def _extract_links(self, soup: BeautifulSoup, current_url: str) -> list[str]:
        """Extract links from the page that should be crawled next."""
        links = []
        base_url = urlparse(current_url)
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            
            # Skip empty links, anchors, javascript, etc.
            if not href or href.startswith(("#", "javascript:", "mailto:")):
                continue
            
            # Convert relative URL to absolute
            absolute_url = urljoin(current_url, href)
            parsed_url = urlparse(absolute_url)
            
            # Only follow links on the same domain
            if parsed_url.netloc == base_url.netloc:
                # Remove fragments
                clean_url = absolute_url.split("#")[0]
                
                # Skip common non-documentation paths
                skip_patterns = [
                    r"/login", r"/signup", r"/register", r"/pricing",
                    r"/contact", r"/about", r"/terms", r"/privacy",
                ]
                
                if not any(re.search(pattern, clean_url, re.IGNORECASE) for pattern in skip_patterns):
                    links.append(clean_url)
        
        return links
    
    async def _process_page(self, url: str, soup: BeautifulSoup) -> None:
        """Process a page to extract API documentation information."""
        
        # Extract general page information
        title = soup.find("title")
        title_text = title.text.strip() if title else ""
        
        # Create a page object
        page = ApiPage(
            url=url,
            title=title_text,
            content=str(soup),
            last_crawled=time.time()
        )
        
        # Parse API endpoints
        endpoints = self.parser.extract_endpoints(soup, url)
        for endpoint in endpoints:
            endpoint_obj = ApiEndpoint(
                endpoint_id=self.repository.generate_id(),
                url=url,
                path=endpoint["path"],
                method=endpoint["method"],
                description=endpoint["description"],
                parameters=endpoint["parameters"],
                request_body=endpoint["request_body"],
                responses=endpoint["responses"],
                examples=endpoint["examples"]
            )
            self.repository.save_endpoint(endpoint_obj)
        
        # Parse API schemas
        schemas = self.parser.extract_schemas(soup, url)
        for schema in schemas:
            schema_obj = ApiSchema(
                schema_id=self.repository.generate_id(),
                url=url,
                name=schema["name"],
                description=schema["description"],
                properties=schema["properties"],
                examples=schema["examples"]
            )
            self.repository.save_schema(schema_obj)
        
        # Save the page
        self.repository.save_page(page)
