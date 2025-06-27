"""
Base scraper class for all web scrapers
"""
import time
import random
import requests
import warnings
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from typing import Optional, Dict, Any
import logging

# Suppress SSL warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

logger = logging.getLogger(__name__)


class BaseScraper:
    """Base class for all web scrapers with common functionality"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        self.session.headers.update(self.headers)
        self.min_delay = 1.0  # Minimum delay between requests (seconds)
        self.max_delay = 3.0  # Maximum delay between requests (seconds)
        self.max_retries = 3
        self.last_request_time = 0
        self.robot_parsers: Dict[str, RobotFileParser] = {}
    
    def _wait_if_needed(self):
        """Ensure random delay between requests (1-3 seconds)"""
        # Calculate random delay between min and max
        delay = random.uniform(self.min_delay, self.max_delay)
        
        # Check time since last request
        elapsed = time.time() - self.last_request_time
        if elapsed < delay:
            sleep_time = delay - elapsed
            logger.debug(f"Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_robot_parser(self, url: str) -> RobotFileParser:
        """Get or create robot parser for the domain"""
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        if domain not in self.robot_parsers:
            robot_parser = RobotFileParser()
            robot_url = urljoin(domain, '/robots.txt')
            robot_parser.set_url(robot_url)
            try:
                # Try to read robots.txt
                robot_parser.read()
                self.robot_parsers[domain] = robot_parser
            except Exception as e:
                logger.warning(f"Failed to read robots.txt from {robot_url}: {e}")
                # Create a permissive parser if robots.txt cannot be read
                # This allows the scraper to continue even if robots.txt is inaccessible
                robot_parser = RobotFileParser()
                # Set can_fetch to always return True for this parser
                robot_parser.parse("")  # Parse empty content to initialize
                self.robot_parsers[domain] = robot_parser
        
        return self.robot_parsers[domain]
    
    def respect_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        try:
            robot_parser = self._get_robot_parser(url)
            # If the parser has no rules (empty), allow access
            if not robot_parser.entries:
                return True
            return robot_parser.can_fetch(self.headers['User-Agent'], url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            # If there's an error, assume it's allowed
            return True
    
    def get_soup(self, url: str, **kwargs) -> Optional[BeautifulSoup]:
        """
        Fetch URL and return BeautifulSoup object
        
        Args:
            url: URL to fetch
            **kwargs: Additional arguments for requests.get()
            
        Returns:
            BeautifulSoup object or None if failed
        """
        # Check robots.txt
        if not self.respect_robots_txt(url):
            logger.warning(f"URL blocked by robots.txt: {url}")
            return None
        
        # Retry logic
        for attempt in range(self.max_retries):
            try:
                # Wait before request
                self._wait_if_needed()
                
                # Make request
                response = self.session.get(url, timeout=10, verify=False, **kwargs)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'lxml')
                return soup
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}")
                return None
    
    def get_json(self, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Fetch URL and return JSON response
        
        Args:
            url: URL to fetch
            **kwargs: Additional arguments for requests.get()
            
        Returns:
            JSON response as dictionary or None if failed
        """
        # Check robots.txt
        if not self.respect_robots_txt(url):
            logger.warning(f"URL blocked by robots.txt: {url}")
            return None
        
        # Retry logic
        for attempt in range(self.max_retries):
            try:
                # Wait before request
                self._wait_if_needed()
                
                # Make request
                response = self.session.get(url, timeout=10, verify=False, **kwargs)
                response.raise_for_status()
                
                # Parse JSON
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}")
                return None 