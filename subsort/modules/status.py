"""
Status module for SubSort
Checks HTTP status codes and basic connectivity
"""

from typing import Dict, Any
from .base import BaseModule

class StatusModule(BaseModule):
    """Module for checking HTTP status codes and basic connectivity"""
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """
        Check HTTP status code and basic connectivity
        
        Args:
            subdomain: The subdomain to check
            
        Returns:
            Dictionary containing status information
        """
        result = {}
        
        try:
            self.log_debug(f"Checking status for {subdomain}")
            
            # Try both HTTPS and HTTP
            response, content, final_url = await self.http_client.check_both_schemes(subdomain)
            
            if response is not None:
                result['status_code'] = response.status
                result['url'] = final_url
                result['content_length'] = len(content) if content else 0
                result['accessible'] = True
                
                # Additional status information
                if response.status >= 200 and response.status < 300:
                    result['status_category'] = 'success'
                elif response.status >= 300 and response.status < 400:
                    result['status_category'] = 'redirect'
                    # Get redirect location if available
                    if 'Location' in response.headers:
                        result['redirect_location'] = response.headers['Location']
                elif response.status >= 400 and response.status < 500:
                    result['status_category'] = 'client_error'
                elif response.status >= 500:
                    result['status_category'] = 'server_error'
                
                # Check for common status codes
                status_messages = {
                    200: 'OK',
                    301: 'Moved Permanently',
                    302: 'Found',
                    403: 'Forbidden',
                    404: 'Not Found',
                    500: 'Internal Server Error',
                    502: 'Bad Gateway',
                    503: 'Service Unavailable'
                }
                
                result['status_message'] = status_messages.get(
                    response.status, 
                    f'HTTP {response.status}'
                )
                
                # Extract scheme from final URL
                if final_url.startswith('https://'):
                    result['scheme'] = 'https'
                    result['ssl_enabled'] = True
                else:
                    result['scheme'] = 'http'
                    result['ssl_enabled'] = False
                
                self.log_debug(f"Status {response.status} ({result['status_message']})", subdomain)
                
            else:
                result['accessible'] = False
                result['status_code'] = None
                result['status_category'] = 'unreachable'
                result['status_message'] = 'Unreachable'
                result['ssl_enabled'] = False
                
                self.log_debug(f"Subdomain unreachable", subdomain)
        
        except Exception as e:
            result['accessible'] = False
            result['status_error'] = str(e)
            result['status_category'] = 'error'
            result['status_message'] = 'Error'
            self.log_error(f"Status check failed: {e}", subdomain)
        
        return result
