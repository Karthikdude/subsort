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
import time

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
        
        self.timeout = self.config.get('timeout', 5)
        self.retries = self.config.get('retries', 3)
        self.follow_redirects = self.config.get('follow_redirects', True)
        self.ignore_ssl = self.config.get('ignore_ssl', False)
        self.threads = self.config.get('threads', 50)

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
        
    async def _create_session(self):
        """Internal method to create session"""
        ssl_context = ssl.create_default_context()
        if self.ignore_ssl:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(
            ssl=ssl_context,
            limit=self.threads * 2,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
            enable_cleanup_closed=True
        )

        self.session = ClientSession(
            connector=connector,
            timeout=ClientTimeout(total=self.timeout),
            headers=self.default_headers,
            raise_for_status=False,
            auto_decompress=True
        )

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

    async def make_request(self, url: str, method: str = 'GET', custom_headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retries and error handling"""

        start_time = time.time()

        for attempt in range(self.retries + 1):
            try:
                # Use more conservative timeouts
                timeout = aiohttp.ClientTimeout(
                    total=self.timeout,
                    connect=min(self.timeout // 2, 10),
                    sock_read=self.timeout
                )

                # Ensure session is available
                if not self.session or self.session.closed:
                    await self._create_session()

                headers = custom_headers or self.get_random_headers()

                async with self.session.request(
                    method=method,
                    url=url,
                    timeout=timeout,
                    allow_redirects=self.follow_redirects,
                    ssl=not self.ignore_ssl,
                    headers=headers
                ) as response:

                    # Read response content with size limit
                    content = await response.read()

                    # Limit content size to prevent memory issues
                    if len(content) > 10 * 1024 * 1024:  # 10MB limit
                        content = content[:10 * 1024 * 1024]

                    try:
                        text_content = content.decode('utf-8', errors='ignore')
                    except Exception:
                        text_content = str(content)

                    result = {
                        'url': str(response.url),
                        'status_code': response.status,
                        'status_message': response.reason or '',
                        'headers': dict(response.headers),
                        'content': text_content,
                        'content_length': len(content),
                        'response_time': time.time() - start_time,
                        'attempt': attempt + 1
                    }

                    return result

            except asyncio.TimeoutError:
                self.logger.warning(f"Request timeout for {url} (attempt {attempt + 1})")
                if attempt == self.retries:
                    return {
                        'error': 'timeout', 
                        'url': url, 
                        'attempts': attempt + 1,
                        'response_time': time.time() - start_time
                    }

            except aiohttp.ClientError as e:
                self.logger.warning(f"Client error for {url}: {e} (attempt {attempt + 1})")
                if attempt == self.retries:
                    return {
                        'error': f'client_error: {str(e)}', 
                        'url': url, 
                        'attempts': attempt + 1,
                        'response_time': time.time() - start_time
                    }

            except Exception as e:
                self.logger.warning(f"Request failed for {url}: {e} (attempt {attempt + 1})")
                if attempt == self.retries:
                    return {
                        'error': str(e), 
                        'url': url, 
                        'attempts': attempt + 1,
                        'response_time': time.time() - start_time
                    }

            # Wait before retry with exponential backoff
            if attempt < self.retries:
                await asyncio.sleep(min(0.5 * (2 ** attempt), 5))

        return None

    async def get(self, url: str, **kwargs) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Make GET request"""
        result = await self.make_request(url, 'GET', **kwargs)
        if result and 'status_code' in result:
            return result, result.get('content', '')
        return None, None

    async def head(self, url: str, **kwargs) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Make HEAD request"""
        result = await self.make_request(url, 'HEAD', **kwargs)
        if result and 'status_code' in result:
            return result, result.get('content', '')
        return None, None

    def format_url(self, subdomain: str, scheme: str = 'https') -> str:
        """Format subdomain to full URL"""
        if not subdomain.startswith(('http://', 'https://')):
            return f"{scheme}://{subdomain}"
        return subdomain

    async def check_both_schemes(self, subdomain: str) -> Tuple[Optional[Dict[str, Any]], Optional[str], str]:
        """Check both HTTP and HTTPS schemes, return the working one"""
        schemes = ['https', 'http']

        for scheme in schemes:
            url = self.format_url(subdomain, scheme)
            response, content = await self.get(url)

            if response is not None and response.get('status_code'):
                self.logger.debug(f"Successfully connected to {url}")
                return response, content, url

        self.logger.debug(f"No working scheme found for {subdomain}")
        return None, None, ""