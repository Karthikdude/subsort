"""
Async HTTP client for SubSort
Handles HTTP requests with proper error handling, retries, and anti-detection features
"""

import asyncio
import logging
import ssl
from typing import Dict, Any, Optional, Tuple
import aiohttp
from aiohttp import ClientSession, ClientTimeout, ClientError
import random

class AsyncHttpClient:
    """Async HTTP client with advanced features for reconnaissance"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.session: Optional[ClientSession] = None
        
        # Default headers
        self.default_headers = {
            'User-Agent': config.get('user_agent', 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Additional user agents for rotation (basic anti-detection)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def create_session(self):
        """Create aiohttp session with proper configuration"""
        timeout = ClientTimeout(total=self.config.get('timeout', 5))
        
        # SSL context configuration
        ssl_context = ssl.create_default_context()
        if self.config.get('ignore_ssl', False):
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        # Connector configuration
        connector = aiohttp.TCPConnector(
            ssl=ssl_context,
            limit=self.config.get('threads', 50) * 2,  # Connection pool
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
            enable_cleanup_closed=True
        )
        
        self.session = ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self.default_headers,
            raise_for_status=False,
            auto_decompress=True
        )
        
        self.logger.debug("HTTP session created successfully")
    
    def get_random_headers(self) -> Dict[str, str]:
        """Get randomized headers for anti-detection"""
        headers = self.default_headers.copy()
        
        # Rotate user agent
        headers['User-Agent'] = random.choice(self.user_agents)
        
        # Add some randomization to other headers
        accept_languages = [
            'en-US,en;q=0.9',
            'en-GB,en;q=0.9',
            'en-US,en;q=0.8,es;q=0.6'
        ]
        headers['Accept-Language'] = random.choice(accept_languages)
        
        return headers
    
    async def make_request(self, url: str, method: str = 'GET', 
                          custom_headers: Optional[Dict[str, str]] = None) -> Tuple[Optional[aiohttp.ClientResponse], Optional[str]]:
        """Make HTTP request with retry logic"""
        if not self.session:
            await self.create_session()
        
        headers = custom_headers or self.get_random_headers()
        retries = self.config.get('retries', 3)
        
        for attempt in range(retries + 1):
            try:
                self.logger.debug(f"Attempting {method} {url} (attempt {attempt + 1})")
                
                async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    allow_redirects=self.config.get('follow_redirects', True),
                    ssl=False if self.config.get('ignore_ssl', False) else None
                ) as response:
                    
                    # Read response content
                    try:
                        content = await response.text(encoding='utf-8', errors='ignore')
                    except UnicodeDecodeError:
                        content = await response.text(encoding='latin1', errors='ignore')
                    except Exception as e:
                        self.logger.warning(f"Failed to read response content for {url}: {e}")
                        content = ""
                    
                    self.logger.debug(f"Response {response.status} for {url}")
                    return response, content
                    
            except asyncio.TimeoutError:
                self.logger.warning(f"Timeout for {url} (attempt {attempt + 1})")
                if attempt == retries:
                    self.logger.error(f"Max retries exceeded for {url} due to timeout")
                    return None, None
                    
            except ClientError as e:
                self.logger.warning(f"Client error for {url}: {e} (attempt {attempt + 1})")
                if attempt == retries:
                    self.logger.error(f"Max retries exceeded for {url} due to client error: {e}")
                    return None, None
                    
            except Exception as e:
                self.logger.warning(f"Unexpected error for {url}: {e} (attempt {attempt + 1})")
                if attempt == retries:
                    self.logger.error(f"Max retries exceeded for {url} due to unexpected error: {e}")
                    return None, None
            
            # Exponential backoff
            if attempt < retries:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                self.logger.debug(f"Waiting {wait_time:.2f}s before retry")
                await asyncio.sleep(wait_time)
        
        return None, None
    
    async def get(self, url: str, **kwargs) -> Tuple[Optional[aiohttp.ClientResponse], Optional[str]]:
        """Make GET request"""
        return await self.make_request(url, 'GET', **kwargs)
    
    async def head(self, url: str, **kwargs) -> Tuple[Optional[aiohttp.ClientResponse], Optional[str]]:
        """Make HEAD request"""
        return await self.make_request(url, 'HEAD', **kwargs)
    
    def format_url(self, subdomain: str, scheme: str = 'https') -> str:
        """Format subdomain to full URL"""
        if not subdomain.startswith(('http://', 'https://')):
            return f"{scheme}://{subdomain}"
        return subdomain
    
    async def check_both_schemes(self, subdomain: str) -> Tuple[Optional[aiohttp.ClientResponse], Optional[str], str]:
        """Check both HTTP and HTTPS schemes, return the working one"""
        schemes = ['https', 'http']
        
        for scheme in schemes:
            url = self.format_url(subdomain, scheme)
            response, content = await self.get(url)
            
            if response is not None:
                self.logger.debug(f"Successfully connected to {url}")
                return response, content, url
        
        self.logger.debug(f"No working scheme found for {subdomain}")
        return None, None, ""
