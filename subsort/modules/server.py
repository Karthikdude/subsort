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
        Extract server information and security headers

        Args:
            subdomain: The subdomain to analyze

        Returns:
            Dictionary containing server and security information
        """
        result = {}

        try:
            response, content, final_url = await self.http_client.check_both_schemes(subdomain)

            if response is None:
                return {'server_info': 'Not accessible'}

            # Handle both response object and dictionary
            if isinstance(response, dict):
                headers = response.get('headers', {})
            else:
                headers = getattr(response, 'headers', {})

            # Convert headers to dict if needed
            if hasattr(headers, 'items'):
                headers = dict(headers)

            # Extract server information
            server = headers.get('server', headers.get('Server', 'Not disclosed'))
            result['server_info'] = server

            # Extract security headers
            security_headers = {}
            for header_name in self.security_headers:
                header_value = headers.get(header_name) or headers.get(header_name.lower())
                if header_value:
                    security_headers[header_name] = header_value

            result['security_headers'] = security_headers
            result['server_fingerprint'] = self.fingerprint_server(server, headers)
            result['security_score'] = self.calculate_security_score(security_headers)

        except Exception as e:
            result['server_error'] = str(e)
            self.log_error(f"Server analysis failed: {e}", subdomain)

        return result