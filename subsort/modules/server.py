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

            if response is None:
                return {
                    'server': None,
                    'server_version': None,
                    'powered_by': None,
                    'security_headers': {},
                    'server_signature': None
                }

            headers = response.get('headers', {})

            # Extract server information
            server_info = self._extract_server_info(headers)

            # Analyze security headers
            security_headers = self._analyze_security_headers(headers)

            return {
                'server': server_info.get('server'),
                'server_version': server_info.get('version'),
                'powered_by': headers.get('X-Powered-By'),
                'security_headers': security_headers,
                'server_signature': self._get_server_signature(headers),
                'all_headers': headers
            }

        except Exception as e:
            result['server_error'] = str(e)
            self.log_error(f"Server detection failed: {e}", subdomain)

        return result