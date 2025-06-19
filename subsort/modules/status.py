"""
Status module for SubSort
Checks HTTP status codes and basic connectivity
"""

import time
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
        return await self.analyze(subdomain, self.http_client)

    def categorize_status(self, status_code: int) -> str:
        """Categorize status code."""
        if status_code is None:
            return 'unreachable'
        if 200 <= status_code < 300:
            return 'success'
        if 300 <= status_code < 400:
            return 'redirect'
        if 400 <= status_code < 500:
            return 'client_error'
        if 500 <= status_code < 600:
            return 'server_error'
        return 'unknown'

    def _get_status_text(self, status_code: int) -> str:
        """Get status text."""
        status_map = {
            200: "OK",
            301: "Moved Permanently",
            302: "Found",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error",
        }
        return status_map.get(status_code, "Unknown Status")

    async def analyze(self, subdomain: str, http_client) -> Dict[str, Any]:
        """Analyze subdomain status"""
        result = {
            'accessible': False,
            'status_code': None,
            'status_text': '',
            'status_category': 'unknown',
            'response_time': None,
            'content_length': None,
            'redirect_url': None,
            'error': None
        }

        try:
            response, content, final_url = await http_client.check_both_schemes(subdomain)

            if response is None:
                result.update({
                    'accessible': False,
                    'status_code': None,
                    'status_category': 'unreachable',
                    'final_url': None
                })
            else:
                if isinstance(response, dict):
                    status_code = response.get('status_code', response.get('status', 0))
                    response_time = response.get('response_time', 0)
                else:
                    status_code = getattr(response, 'status', getattr(response, 'status_code', 0))
                    response_time = getattr(response, 'response_time', 0)

                result.update({
                    'accessible': True,
                    'status_code': status_code,
                    'status_text': self._get_status_text(status_code),
                    'status_category': self.categorize_status(status_code),
                    'response_time': round(response_time, 2),
                    'content_length': len(content) if content else 0,
                    'final_url': final_url,
                    'protocol': final_url.split('://')[0] if final_url else None
                })

        except Exception as e:
            result['error'] = str(e)
            result['status_category'] = 'error'
            self.log_error(f"Status check failed for {subdomain}: {e}", subdomain)

        return result