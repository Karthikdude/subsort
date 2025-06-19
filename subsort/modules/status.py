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
        Check HTTP status code and basic connectivity.

        Args:
            subdomain: The subdomain to check.

        Returns:
            A dictionary containing status information.
        """
        try:
            response, content, final_url = await self.http_client.check_both_schemes(subdomain)

            if response and isinstance(response, dict) and 'error' in response:
                self.log_error(f"Status check failed for {subdomain}: {response['error']}", subdomain)
                return {
                    'accessible': False,
                    'status_code': None,
                    'status_category': 'error',
                    'final_url': None,
                    'status_error': response['error']
                }

            if response is None:
                return {
                    'accessible': False,
                    'status_code': None,
                    'status_category': 'unreachable',
                    'final_url': None
                }

            status_code = getattr(response, 'status', 0)
            return {
                'accessible': True,
                'status_code': status_code,
                'status_text': self._get_status_text(status_code),
                'status_category': self.categorize_status(status_code),
                'final_url': str(final_url),
                'response_size': len(content) if content else 0,
                'protocol': final_url.split('://')[0] if final_url else None
            }

        except Exception as e:
            self.log_error(f"An unexpected error occurred in StatusModule for {subdomain}: {e}", subdomain)
            return {
                'accessible': False,
                'status_error': str(e),
                'status_category': 'exception'
            }

    def categorize_status(self, status_code: int) -> str:
        """Categorizes the HTTP status code."""
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
        """Returns a descriptive text for common HTTP status codes."""
        status_map = {
            200: "OK",
            301: "Moved Permanently",
            302: "Found",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
        }
        return status_map.get(status_code, "Unknown Status")