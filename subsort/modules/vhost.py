"""
Virtual Host module for SubSort
Performs virtual host-based detection and saves accordingly
"""

from typing import Dict, Any, List, Tuple
from .base import BaseModule


class VhostModule(BaseModule):
    """Module for virtual host detection and analysis"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Common virtual host headers to check
        self.vhost_headers = [
            'Host',
            'X-Forwarded-Host',
            'X-Host',
            'X-Original-Host',
            'X-Real-Host'
        ]
        
        # Virtual host detection patterns
        self.vhost_patterns = [
            'virtual host',
            'vhost',
            'shared hosting',
            'multiple domains',
            'domain parking'
        ]
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """
        Perform virtual host detection
        
        Args:
            subdomain: The subdomain to analyze
            
        Returns:
            Dictionary containing virtual host information
        """
        result = {
            'subdomain': subdomain,
            'is_vhost': False,
            'vhost_type': None,
            'shared_ip': None,
            'host_headers': {},
            'vhost_indicators': [],
            'alternative_hosts': []
        }
        
        try:
            # Test with original subdomain
            response, content, scheme = await self.http_client.check_both_schemes(subdomain)
            
            if not response:
                self.log_warning(f"No response received", subdomain)
                return result
            
            # Store original response details
            original_status = response.status
            original_content_length = len(content) if content else 0
            original_title = self._extract_title(content or "")
            
            # Test with different Host headers
            test_hosts = [
                'example.com',
                'test.local',
                'nonexistent.domain.com',
                subdomain.replace('.', '-') + '.test'
            ]
            
            vhost_detected = False
            alternative_responses = []
            
            for test_host in test_hosts:
                try:
                    # Make request with custom Host header
                    custom_headers = {'Host': test_host}
                    test_response, test_content = await self.http_client.make_request(
                        f"https://{subdomain}",
                        custom_headers=custom_headers
                    )
                    
                    if test_response:
                        test_title = self._extract_title(test_content or "")
                        test_content_length = len(test_content) if test_content else 0
                        
                        # Check if response differs significantly
                        if (test_response.status != original_status or
                            abs(test_content_length - original_content_length) > 100 or
                            test_title != original_title):
                            
                            vhost_detected = True
                            alternative_responses.append({
                                'host': test_host,
                                'status': test_response.status,
                                'title': test_title,
                                'content_length': test_content_length
                            })
                
                except Exception as e:
                    self.log_debug(f"Virtual host test failed for {test_host}: {e}", subdomain)
                    continue
            
            result['is_vhost'] = vhost_detected
            result['alternative_hosts'] = alternative_responses
            
            # Analyze headers for virtual host indicators
            result['host_headers'] = self._analyze_host_headers(dict(response.headers))
            
            # Check content for virtual host indicators
            if content:
                result['vhost_indicators'] = self._find_vhost_indicators(content)
            
            # Determine virtual host type
            if vhost_detected:
                result['vhost_type'] = self._determine_vhost_type(
                    response, content or "", alternative_responses
                )
            
            self.log_debug(f"Virtual host detection: {vhost_detected}", subdomain)
            
        except Exception as e:
            self.log_error(f"Virtual host detection failed: {e}", subdomain)
        
        return result
    
    def _analyze_host_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Analyze headers for virtual host related information"""
        host_info = {}
        
        for header_name in self.vhost_headers:
            if header_name.lower() in [h.lower() for h in headers.keys()]:
                # Find the actual header name (case-insensitive)
                actual_header = next(h for h in headers.keys() if h.lower() == header_name.lower())
                host_info[header_name] = headers[actual_header]
        
        return host_info
    
    def _find_vhost_indicators(self, content: str) -> List[str]:
        """Find virtual host indicators in content"""
        indicators = []
        content_lower = content.lower()
        
        for pattern in self.vhost_patterns:
            if pattern in content_lower:
                indicators.append(pattern)
        
        # Look for multiple domain references
        import re
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        domains = re.findall(domain_pattern, content)
        
        if len(set(domains)) > 3:  # Multiple different domains found
            indicators.append('multiple_domains_in_content')
        
        return indicators
    
    def _determine_vhost_type(self, response, content: str, alternatives: List[Dict]) -> str:
        """Determine the type of virtual hosting"""
        
        # Check if it's a wildcard DNS setup
        if len(alternatives) > 2:
            return 'wildcard_vhost'
        
        # Check for shared hosting indicators
        if content and any(indicator in content.lower() for indicator in 
                          ['cpanel', 'plesk', 'shared hosting', 'hosting provider']):
            return 'shared_hosting'
        
        # Check for CDN/Proxy
        server_header = response.headers.get('Server', '').lower()
        if any(cdn in server_header for cdn in ['cloudflare', 'nginx-proxy', 'haproxy']):
            return 'cdn_proxy_vhost'
        
        # Default virtual host type
        return 'name_based_vhost'
    
    def _extract_title(self, content: str) -> str:
        """Extract title from HTML content"""
        import re
        if not content:
            return ""
        
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            return title_match.group(1).strip()[:100]  # Limit title length
        
        return ""