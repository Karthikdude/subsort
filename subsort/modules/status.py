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

            response, content, final_url = await self.http_client.check_both_schemes(subdomain)

            if response is None:
                return {
                    'accessible': False,
                    'status_code': None,
                    'status_message': 'Connection failed',
                    'status_category': 'error',
                    'final_url': None,
                    'scheme': None
                }

            # Extract scheme from final URL
            scheme = 'https' if final_url.startswith('https') else 'http'

            # Categorize status code
            status_code = response.get('status_code')
            category = self._categorize_status_code(status_code)

            return {
                'accessible': True,
                'status_code': status_code,
                'status_message': response.get('status_message', ''),
                'status_category': category,
                'final_url': final_url,
                'scheme': scheme,
                'redirect_chain': []
            }

        except Exception as e:
            result['accessible'] = False
            result['status_error'] = str(e)
            result['status_category'] = 'error'
            result['status_message'] = 'Error'
            self.log_error(f"Status check failed: {e}", subdomain)

        return result