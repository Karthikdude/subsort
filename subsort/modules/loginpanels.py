
"""
Login Panels Detection Module
Detects and lists login portals and authentication forms across subdomains
"""

import re
from typing import Dict, Any, List
from .base import BaseModule

class LoginpanelsModule(BaseModule):
    """Module for detecting login panels and authentication interfaces"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Common admin panel paths
        self.admin_paths = [
            '/admin', '/admin/', '/admin/login', '/admin/login.php',
            '/wp-admin', '/wp-login.php', '/administrator',
            '/login', '/login.php', '/signin', '/auth',
            '/panel', '/cpanel', '/control', '/dashboard'
        ]
        
        # Login panel indicators
        self.login_indicators = [
            'login', 'signin', 'sign in', 'log in', 'authentication',
            'admin panel', 'administrator', 'control panel', 'dashboard',
            'password', 'username', 'email'
        ]
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """Detect login panels on subdomain"""
        result = {
            'login_panels': [],
            'admin_paths_found': [],
            'form_count': 0,
            'panel_types': []
        }
        
        try:
            # Check main page first
            main_panel = await self._check_main_page(subdomain)
            if main_panel:
                result['login_panels'].append(main_panel)
            
            # Check common admin paths
            admin_panels = await self._check_admin_paths(subdomain)
            result['admin_paths_found'] = admin_panels
            result['login_panels'].extend(admin_panels)
            
            # Analyze panel types
            panel_types = list(set([panel.get('type', 'unknown') for panel in result['login_panels']]))
            result['panel_types'] = panel_types
            result['form_count'] = len(result['login_panels'])
        
        except Exception as e:
            self.log_error(f"Login panel detection failed: {e}", subdomain)
        
        return result
    
    async def _check_main_page(self, subdomain: str) -> Dict[str, Any]:
        """Check main page for login forms"""
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
                        if response.status == 200:
                            content = await response.text()
                            panel_info = await self._analyze_login_content(content, url)
                            if panel_info:
                                return panel_info
                except Exception as e:
                    self.log_debug(f"Failed to fetch main page {url}: {e}", subdomain)
                    continue
        
        except Exception as e:
            self.log_error(f"Error checking main page: {e}", subdomain)
        
        return None
    
    async def _check_admin_paths(self, subdomain: str) -> List[Dict[str, Any]]:
        """Check common admin paths for login panels"""
        found_panels = []
        
        for protocol in ['https', 'http']:
            base_url = f"{protocol}://{subdomain}"
            
            for path in self.admin_paths:
                try:
                    url = base_url + path
                    
                    async with self.http_client.session.get(
                        url, 
                        timeout=self.http_client.timeout,
                        ssl=False if self.http_client.config.get('ignore_ssl') else None,
                        allow_redirects=True
                    ) as response:
                        if response.status in [200, 401, 403]:
                            content = await response.text()
                            panel_info = await self._analyze_login_content(content, str(response.url))
                            
                            if panel_info:
                                panel_info['discovered_path'] = path
                                panel_info['status_code'] = response.status
                                found_panels.append(panel_info)
                            elif response.status == 401:
                                # HTTP Basic Auth detected
                                found_panels.append({
                                    'url': str(response.url),
                                    'type': 'HTTP Basic Auth',
                                    'title': 'Authentication Required',
                                    'discovered_path': path,
                                    'status_code': 401,
                                    'requires_auth': True
                                })
                
                except Exception as e:
                    self.log_debug(f"Error checking {path}: {e}", subdomain)
                    continue
            
            # If we found panels with HTTPS, don't check HTTP
            if found_panels:
                break
        
        return found_panels
    
    async def _analyze_login_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """Analyze HTML content for login panel indicators"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Get page title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else 'No Title'
            
            # Check if page contains login indicators
            content_text = soup.get_text().lower()
            has_login_content = any(indicator in content_text for indicator in self.login_indicators)
            
            if not has_login_content:
                return None
            
            # Find login forms
            forms = soup.find_all('form')
            login_forms = []
            
            for form in forms:
                if self._is_login_form(form):
                    form_info = self._extract_form_info(form)
                    login_forms.append(form_info)
            
            if not login_forms and not has_login_content:
                return None
            
            # Determine panel type
            panel_type = self._determine_panel_type(title, content_text, url)
            
            return {
                'url': url,
                'type': panel_type,
                'title': title,
                'forms': login_forms,
                'form_count': len(login_forms),
                'requires_auth': False
            }
        
        except Exception as e:
            self.log_error(f"Error analyzing login content: {e}")
            return None
    
    def _is_login_form(self, form) -> bool:
        """Check if a form is likely a login form"""
        # Look for password fields
        password_inputs = form.find_all('input', {'type': 'password'})
        if not password_inputs:
            return False
        
        # Look for username/email fields
        username_patterns = ['username', 'email', 'login', 'user', 'userid']
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
        
        return has_username
    
    def _extract_form_info(self, form) -> Dict[str, Any]:
        """Extract information from a login form"""
        form_info = {
            'action': form.get('action', ''),
            'method': form.get('method', 'GET').upper(),
            'fields': []
        }
        
        inputs = form.find_all('input')
        for inp in inputs:
            input_type = inp.get('type', 'text')
            input_name = inp.get('name', '')
            input_placeholder = inp.get('placeholder', '')
            
            if input_type in ['text', 'email', 'password', 'hidden']:
                form_info['fields'].append({
                    'type': input_type,
                    'name': input_name,
                    'placeholder': input_placeholder
                })
        
        return form_info
    
    def _determine_panel_type(self, title: str, content: str, url: str) -> str:
        """Determine the type of login panel based on content and URL"""
        title_lower = title.lower()
        content_lower = content.lower()
        url_lower = url.lower()
        
        # WordPress
        if any(indicator in title_lower or indicator in url_lower 
               for indicator in ['wordpress', 'wp-admin', 'wp-login']):
            return 'WordPress Admin'
        
        # Generic admin panels
        if any(indicator in title_lower or indicator in content_lower 
               for indicator in ['admin panel', 'administrator', 'control panel']):
            return 'Admin Panel'
        
        # CPanel/WHM
        if any(indicator in title_lower or indicator in url_lower 
               for indicator in ['cpanel', 'whm', 'webhost']):
            return 'Hosting Panel'
        
        # Database admin
        if any(indicator in title_lower 
               for indicator in ['phpmyadmin', 'adminer', 'database']):
            return 'Database Admin'
        
        # Generic login
        if any(indicator in title_lower 
               for indicator in ['login', 'sign in', 'authentication']):
            return 'Login Page'
        
        return 'Unknown Panel'
