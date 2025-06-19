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
            response, content, final_url = await self.http_client.check_both_schemes(subdomain)

            if response is None:
                result.update({
                    'accessible': False,
                    'status_code': None,
                    'status_category': 'unreachable',
                    'final_url': None
                })
            else:
                # Handle both response object and dictionary
                if isinstance(response, dict):
                    status_code = response.get('status_code', response.get('status', 0))
                else:
                    status_code = getattr(response, 'status', getattr(response, 'status_code', 0))

                result.update({
                    'accessible': True,
                    'status_code': status_code,
                    'status_category': self.categorize_status(status_code),
                    'final_url': final_url,
                    'response_size': len(content) if content else 0
                })

        except Exception as e:
            result.update({
                'accessible': False,
                'status_error': str(e),
                'status_category': 'error'
            })
            self.log_error(f"Status check failed: {e}", subdomain)

        return result