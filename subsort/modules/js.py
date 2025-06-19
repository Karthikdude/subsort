
"""
JavaScript File Extraction Module
Extracts and analyzes linked JavaScript files from web pages
"""

import re
import aiofiles
import os
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, List
from .base import BaseModule

class JsModule(BaseModule):
    """Module for extracting and analyzing JavaScript files"""
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """Extract JavaScript files from subdomain"""
        result = {
            'js_files': [],
            'inline_js_count': 0,
            'external_js_count': 0,
            'js_libraries': []
        }
        
        try:
            # Try both HTTP and HTTPS
            for protocol in ['https', 'http']:
                url = f"{protocol}://{subdomain}"
                
                try:
                    async with self.http_client.session.get(
                        url, 
                        timeout=self.http_client.timeout,
                        ssl=False if self.http_client.config.get('ignore_ssl') else None
                    ) as response:
                        if response.status == 200:
                            content = await response.text()
                            result.update(await self._extract_js_files(content, url))
                            break
                except Exception as e:
                    self.log_debug(f"Failed to fetch {url}: {e}", subdomain)
                    continue
        
        except Exception as e:
            self.log_error(f"JavaScript extraction failed: {e}", subdomain)
        
        return result
    
    async def _extract_js_files(self, html_content: str, base_url: str) -> Dict[str, Any]:
        """Extract JavaScript files from HTML content"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            js_files = []
            inline_js_count = 0
            js_libraries = []
            
            # Find all script tags
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                if script.get('src'):
                    # External JavaScript file
                    src = script['src']
                    if not src.startswith(('http://', 'https://')):
                        src = urljoin(base_url, src)
                    
                    js_files.append({
                        'url': src,
                        'type': 'external',
                        'async': script.get('async') is not None,
                        'defer': script.get('defer') is not None
                    })
                    
                    # Detect common libraries
                    if any(lib in src.lower() for lib in ['jquery', 'angular', 'react', 'vue', 'bootstrap']):
                        js_libraries.append(self._extract_library_info(src))
                
                elif script.string:
                    # Inline JavaScript
                    inline_js_count += 1
            
            return {
                'js_files': js_files,
                'inline_js_count': inline_js_count,
                'external_js_count': len(js_files),
                'js_libraries': js_libraries
            }
        
        except Exception as e:
            self.log_error(f"Error parsing JavaScript: {e}")
            return {
                'js_files': [],
                'inline_js_count': 0,
                'external_js_count': 0,
                'js_libraries': []
            }
    
    def _extract_library_info(self, js_url: str) -> Dict[str, str]:
        """Extract library information from JavaScript URL"""
        filename = os.path.basename(urlparse(js_url).path)
        
        # Common library patterns
        library_patterns = {
            'jquery': r'jquery[.-]?(\d+(?:\.\d+)*)',
            'angular': r'angular[.-]?(\d+(?:\.\d+)*)',
            'react': r'react[.-]?(\d+(?:\.\d+)*)',
            'vue': r'vue[.-]?(\d+(?:\.\d+)*)',
            'bootstrap': r'bootstrap[.-]?(\d+(?:\.\d+)*)'
        }
        
        for lib_name, pattern in library_patterns.items():
            match = re.search(pattern, filename.lower())
            if match:
                return {
                    'library': lib_name,
                    'version': match.group(1) if match.groups() else 'unknown',
                    'url': js_url
                }
        
        return {
            'library': 'unknown',
            'version': 'unknown',
            'url': js_url
        }
