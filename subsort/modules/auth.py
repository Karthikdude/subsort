
"""
Authentication Detection Module
Detects login portals and authentication-requiring endpoints
"""

import re
from typing import Dict, Any, List
from .base import BaseModule

class AuthModule(BaseModule):
    """Module for detecting authentication mechanisms"""
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """Detect authentication mechanisms on subdomain"""
        result = {
            'has_auth': False,
            'auth_types': [],
            'login_forms': 0,
            'auth_headers': [],
            'requires_auth': False
        }
        
        try:
            # Try both HTTP and HTTPS
            for protocol in ['https', 'http']:
                url = f"{protocol}://{subdomain}"
                
                try:
                    async with self.http_client.session.get(
                        url, 
                        timeout=self.http_client.timeout,
                        ssl=False if self.http_client.config.get('ignore_ssl') else None
                    ) as response:
                        if response.status in [200, 401, 403]:
                            content = await response.text()
                            headers = dict(response.headers)
                            result.update(await self._detect_auth(content, headers, response.status))
                            break
                except Exception as e:
                    self.log_debug(f"Failed to fetch {url}: {e}", subdomain)
                    continue
        
        except Exception as e:
            self.log_error(f"Authentication detection failed: {e}", subdomain)
        
        return result
    
    async def _detect_auth(self, html_content: str, headers: Dict[str, str], status_code: int) -> Dict[str, Any]:
        """Detect authentication mechanisms from content and headers"""
        try:
            from bs4 import BeautifulSoup
            
            auth_types = []
            login_forms = 0
            auth_headers = []
            has_auth = False
            requires_auth = False
            
            # Check HTTP status for auth requirements
            if status_code == 401:
                requires_auth = True
                has_auth = True
            
            # Check headers for authentication
            auth_header_patterns = {
                'www-authenticate': 'HTTP Basic/Digest',
                'authorization': 'Bearer/API Key',
                'x-auth-token': 'Token Authentication',
                'set-cookie': 'Session Authentication'
            }
            
            for header, auth_type in auth_header_patterns.items():
                if header in headers.keys() or header.lower() in [h.lower() for h in headers.keys()]:
                    auth_headers.append(header)
                    auth_types.append(auth_type)
                    has_auth = True
            
            # Parse HTML for login forms
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find login forms
            forms = soup.find_all('form')
            for form in forms:
                if self._is_login_form(form):
                    login_forms += 1
                    has_auth = True
                    if 'Form Authentication' not in auth_types:
                        auth_types.append('Form Authentication')
            
            # Check for OAuth/SAML patterns
            oauth_patterns = [
                r'oauth',
                r'saml',
                r'sso',
                r'login.*google',
                r'login.*facebook',
                r'login.*microsoft'
            ]
            
            content_lower = html_content.lower()
            for pattern in oauth_patterns:
                if re.search(pattern, content_lower):
                    auth_types.append('OAuth/SSO')
                    has_auth = True
                    break
            
            return {
                'has_auth': has_auth,
                'auth_types': list(set(auth_types)),
                'login_forms': login_forms,
                'auth_headers': auth_headers,
                'requires_auth': requires_auth
            }
        
        except Exception as e:
            self.log_error(f"Error analyzing authentication: {e}")
            return {
                'has_auth': False,
                'auth_types': [],
                'login_forms': 0,
                'auth_headers': [],
                'requires_auth': False
            }
    
    def _is_login_form(self, form) -> bool:
        """Check if a form is likely a login form"""
        # Look for password fields
        password_inputs = form.find_all('input', {'type': 'password'})
        if not password_inputs:
            return False
        
        # Look for username/email fields
        username_patterns = ['username', 'email', 'login', 'user']
        inputs = form.find_all('input')
        
        has_username = False
        for inp in inputs:
            name = inp.get('name', '').lower()
            placeholder = inp.get('placeholder', '').lower()
            id_attr = inp.get('id', '').lower()
            
            if any(pattern in name or pattern in placeholder or pattern in id_attr 
                   for pattern in username_patterns):
                has_username = True
                break
        
        return has_username and len(password_inputs) > 0
