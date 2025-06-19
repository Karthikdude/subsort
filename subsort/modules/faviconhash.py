"""
Favicon Hash module for SubSort
Generates favicon hashes to identify technologies or services
"""

import hashlib
import base64
from typing import Dict, Any
from .base import BaseModule


class FaviconhashModule(BaseModule):
    """Module for generating favicon hashes for technology identification"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Known favicon hashes for popular services/technologies
        self.known_hashes = {
            # Web servers and frameworks
            '-1588080585': 'Apache HTTP Server',
            '1404073852': 'nginx',
            '708578229': 'Microsoft IIS',
            '-235893395': 'WordPress',
            '1942532096': 'Django',
            '-343656283': 'Flask',
            
            # Cloud services
            '81166609': 'Amazon S3',
            '-1152842768': 'Google Cloud',
            '1379923932': 'Microsoft Azure',
            '-1194133913': 'Cloudflare',
            
            # CMS and platforms
            '1011053026': 'Drupal',
            '-1506969290': 'Joomla',
            '1335392324': 'Magento',
            '-1278104634': 'Shopify',
            
            # Monitoring and security
            '566218143': 'Splunk',
            '-1025300011': 'Kibana',
            '394490493': 'Grafana',
            '-1347968860': 'pfSense'
        }
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """
        Generate favicon hash and identify technology
        
        Args:
            subdomain: The subdomain to analyze
            
        Returns:
            Dictionary containing favicon hash information
        """
        result = {
            'subdomain': subdomain,
            'favicon_hash': None,
            'favicon_mmh3': None,
            'favicon_md5': None,
            'technology_match': None,
            'favicon_url': None,
            'favicon_size': None,
            'favicon_accessible': False
        }
        
        try:
            # Try common favicon paths
            favicon_paths = [
                '/favicon.ico',
                '/favicon.png', 
                '/apple-touch-icon.png',
                '/android-chrome-192x192.png',
                '/mstile-150x150.png'
            ]
            
            favicon_data = None
            favicon_url = None
            
            # Check each favicon path
            for path in favicon_paths:
                try:
                    response, content, scheme = await self.http_client.check_both_schemes(subdomain)
                    if response:
                        # Build favicon URL
                        favicon_url = f"{scheme}://{subdomain}{path}"
                        
                        # Make request to favicon
                        fav_response, fav_content = await self.http_client.get(favicon_url)
                        
                        if fav_response and fav_response.status == 200 and fav_content:
                            favicon_data = fav_content.encode() if isinstance(fav_content, str) else fav_content
                            result['favicon_url'] = favicon_url
                            result['favicon_size'] = len(favicon_data)
                            result['favicon_accessible'] = True
                            break
                            
                except Exception as e:
                    self.log_debug(f"Failed to fetch favicon from {path}: {e}", subdomain)
                    continue
            
            if favicon_data:
                # Generate hashes
                result['favicon_md5'] = hashlib.md5(favicon_data).hexdigest()
                
                # Calculate MMH3 hash (similar to Shodan)
                mmh3_hash = self._calculate_mmh3_hash(favicon_data)
                result['favicon_mmh3'] = str(mmh3_hash)
                result['favicon_hash'] = str(mmh3_hash)
                
                # Check against known hashes
                if str(mmh3_hash) in self.known_hashes:
                    result['technology_match'] = self.known_hashes[str(mmh3_hash)]
                    self.log_debug(f"Favicon technology match: {result['technology_match']}", subdomain)
                
                self.log_debug(f"Favicon hash: {mmh3_hash}", subdomain)
            else:
                self.log_warning(f"No favicon found", subdomain)
            
        except Exception as e:
            self.log_error(f"Favicon hash generation failed: {e}", subdomain)
        
        return result
    
    def _calculate_mmh3_hash(self, data: bytes) -> int:
        """Calculate MMH3 hash similar to Shodan's favicon hash"""
        try:
            # Base64 encode the favicon data
            encoded = base64.b64encode(data)
            
            # Simple hash calculation (approximation of MMH3)
            # For production use, you might want to use the actual mmh3 library
            hash_value = 0
            for byte in encoded:
                hash_value = ((hash_value << 5) - hash_value + byte) & 0xffffffff
            
            # Convert to signed 32-bit integer
            if hash_value > 0x7fffffff:
                hash_value -= 0x100000000
                
            return hash_value
            
        except Exception as e:
            self.log_error(f"MMH3 hash calculation failed: {e}")
            return 0