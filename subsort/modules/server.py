"""
Server module for SubSort
Extracts server information from HTTP headers
"""

from typing import Dict, Any
from .base import BaseModule

class ServerModule(BaseModule):
    """Module for extracting server information from HTTP headers"""
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """
        Extract server information from HTTP headers
        
        Args:
            subdomain: The subdomain to analyze
            
        Returns:
            Dictionary containing server information
        """
        result = {}
        
        try:
            self.log_debug(f"Extracting server info for {subdomain}")
            
            # Try both HTTPS and HTTP
            response, content, final_url = await self.http_client.check_both_schemes(subdomain)
            
            if response is not None:
                headers = response.headers
                
                # Extract server information
                server = headers.get('Server', '').strip()
                if server:
                    result['server'] = server
                    
                    # Parse server details
                    server_lower = server.lower()
                    if 'nginx' in server_lower:
                        result['server_type'] = 'nginx'
                    elif 'apache' in server_lower:
                        result['server_type'] = 'apache'
                    elif 'iis' in server_lower:
                        result['server_type'] = 'iis'
                    elif 'cloudflare' in server_lower:
                        result['server_type'] = 'cloudflare'
                    elif 'lightspeed' in server_lower:
                        result['server_type'] = 'litespeed'
                    else:
                        result['server_type'] = 'unknown'
                else:
                    result['server'] = 'Not disclosed'
                    result['server_type'] = 'hidden'
                
                # Extract powered-by information
                powered_by = headers.get('X-Powered-By', '').strip()
                if powered_by:
                    result['powered_by'] = powered_by
                
                # Extract additional server-related headers
                additional_headers = {
                    'x-server': 'X-Server',
                    'x-cache': 'X-Cache',
                    'x-cache-status': 'X-Cache-Status',
                    'x-served-by': 'X-Served-By',
                    'x-varnish': 'X-Varnish',
                    'x-proxy-cache': 'X-Proxy-Cache',
                    'x-fastly-request-id': 'X-Fastly-Request-ID',
                    'cf-ray': 'CF-Ray',
                    'cf-cache-status': 'CF-Cache-Status'
                }
                
                for key, header_name in additional_headers.items():
                    value = headers.get(header_name, '').strip()
                    if value:
                        result[key] = value
                
                # Detect CDN/Proxy services
                cdn_indicators = {
                    'cloudflare': ['cf-ray', 'cf-cache-status', 'cloudflare'],
                    'fastly': ['x-fastly-request-id', 'fastly'],
                    'varnish': ['x-varnish', 'varnish'],
                    'akamai': ['akamai'],
                    'maxcdn': ['maxcdn'],
                    'keycdn': ['keycdn']
                }
                
                detected_cdns = []
                all_headers_str = ' '.join([f"{k}:{v}" for k, v in headers.items()]).lower()
                
                for cdn, indicators in cdn_indicators.items():
                    for indicator in indicators:
                        if indicator in all_headers_str:
                            detected_cdns.append(cdn)
                            break
                
                if detected_cdns:
                    result['cdn_services'] = detected_cdns
                
                # Security headers analysis
                security_headers = {
                    'strict_transport_security': 'Strict-Transport-Security',
                    'content_security_policy': 'Content-Security-Policy',
                    'x_frame_options': 'X-Frame-Options',
                    'x_content_type_options': 'X-Content-Type-Options',
                    'x_xss_protection': 'X-XSS-Protection',
                    'referrer_policy': 'Referrer-Policy'
                }
                
                security_info = {}
                for key, header_name in security_headers.items():
                    value = headers.get(header_name, '').strip()
                    if value:
                        security_info[key] = value
                
                if security_info:
                    result['security_headers'] = security_info
                
                self.log_debug(f"Server: {result.get('server', 'Unknown')}", subdomain)
                
            else:
                result['server_error'] = 'Unable to connect'
                self.log_debug(f"Unable to connect for server detection", subdomain)
        
        except Exception as e:
            result['server_error'] = str(e)
            self.log_error(f"Server detection failed: {e}", subdomain)
        
        return result
