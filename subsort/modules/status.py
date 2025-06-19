Fixes the status module to correctly handle HTTP responses and retrieve status codes.
```

```python
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
```Fixes the status module to correctly handle HTTP responses and retrieve status codes.
```

```python
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
            # Build URL with protocol detection
            for protocol in ['https://', 'http://']:
                url = f"{protocol}{subdomain}"

                try:
                    start_time = time.time()
                    response = await http_client.get(url)
                    response_time = (time.time() - start_time) * 1000

                    # Handle response object properly
                    if hasattr(response, 'status_code') and response.status_code > 0:
                        result.update({
                            'accessible': True,
                            'status_code': response.status_code,
                            'status_text': self._get_status_text(response.status_code),
                            'status_category': self._categorize_status(response.status_code),
                            'response_time': round(response_time, 2),
                            'content_length': len(response.content) if hasattr(response, 'content') and response.content else 0,
                            'protocol': protocol.rstrip('://')
                        })
                        break

                except Exception as e:
                    continue

            if not result['accessible']:
                result['error'] = "No accessible protocol found"
                result['status_category'] = 'error'

        except Exception as e:
            result['error'] = str(e)
            result['status_category'] = 'error'

        return result