
"""
JavaScript Vulnerability Detection Module
Identifies outdated/vulnerable JavaScript libraries and their versions
"""

import re
import json
from typing import Dict, Any, List
from .base import BaseModule

class JsvulnModule(BaseModule):
    """Module for detecting vulnerable JavaScript libraries"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Known vulnerable library patterns
        self.vuln_patterns = {
            'jquery': {
                'versions': ['1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7', '1.8', '1.9', '2.0', '2.1'],
                'vulnerabilities': ['XSS', 'DOM manipulation']
            },
            'angular': {
                'versions': ['1.0', '1.1', '1.2', '1.3', '1.4', '1.5'],
                'vulnerabilities': ['XSS', 'Template injection']
            },
            'bootstrap': {
                'versions': ['2.0', '2.1', '2.2', '2.3', '3.0', '3.1', '3.2'],
                'vulnerabilities': ['XSS in tooltip/popover']
            }
        }
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """Scan for vulnerable JavaScript libraries"""
        result = {
            'vulnerable_libraries': [],
            'total_vulnerabilities': 0,
            'risk_score': 0
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
                        if response.status == 200:
                            content = await response.text()
                            result.update(await self._analyze_js_vulnerabilities(content, url))
                            break
                except Exception as e:
                    self.log_debug(f"Failed to fetch {url}: {e}", subdomain)
                    continue
        
        except Exception as e:
            self.log_error(f"JavaScript vulnerability scan failed: {e}", subdomain)
        
        return result
    
    async def _analyze_js_vulnerabilities(self, html_content: str, base_url: str) -> Dict[str, Any]:
        """Analyze HTML content for vulnerable JavaScript libraries"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            vulnerable_libraries = []
            total_vulnerabilities = 0
            
            # Find all script tags
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                src = script.get('src', '')
                if src:
                    vuln_info = self._check_library_vulnerabilities(src)
                    if vuln_info:
                        vulnerable_libraries.append(vuln_info)
                        total_vulnerabilities += len(vuln_info.get('vulnerabilities', []))
                
                # Check inline scripts for library usage indicators
                if script.string:
                    inline_vulns = self._check_inline_js_vulnerabilities(script.string)
                    if inline_vulns:
                        vulnerable_libraries.extend(inline_vulns)
                        total_vulnerabilities += sum(len(v.get('vulnerabilities', [])) for v in inline_vulns)
            
            # Calculate risk score (0-100)
            risk_score = min(total_vulnerabilities * 10, 100)
            
            return {
                'vulnerable_libraries': vulnerable_libraries,
                'total_vulnerabilities': total_vulnerabilities,
                'risk_score': risk_score
            }
        
        except Exception as e:
            self.log_error(f"Error analyzing JavaScript vulnerabilities: {e}")
            return {
                'vulnerable_libraries': [],
                'total_vulnerabilities': 0,
                'risk_score': 0
            }
    
    def _check_library_vulnerabilities(self, js_url: str) -> Dict[str, Any]:
        """Check if a JavaScript library URL contains known vulnerable versions"""
        js_url_lower = js_url.lower()
        
        for lib_name, lib_info in self.vuln_patterns.items():
            if lib_name in js_url_lower:
                # Extract version using regex
                version_patterns = [
                    rf'{lib_name}[.-]?(\d+(?:\.\d+)*)',
                    rf'{lib_name}[/-]v?(\d+(?:\.\d+)*)',
                    rf'(\d+(?:\.\d+)*)[.-]{lib_name}'
                ]
                
                for pattern in version_patterns:
                    match = re.search(pattern, js_url_lower)
                    if match:
                        version = match.group(1)
                        
                        # Check if version is vulnerable
                        if any(version.startswith(vuln_ver) for vuln_ver in lib_info['versions']):
                            return {
                                'library': lib_name,
                                'version': version,
                                'url': js_url,
                                'vulnerabilities': lib_info['vulnerabilities'],
                                'severity': 'high' if len(lib_info['vulnerabilities']) > 1 else 'medium'
                            }
        
        return None
    
    def _check_inline_js_vulnerabilities(self, js_content: str) -> List[Dict[str, Any]]:
        """Check inline JavaScript for vulnerable library usage patterns"""
        vulnerabilities = []
        
        # Check for jQuery version declarations
        jquery_version_match = re.search(r'jQuery\s*[vV]?(\d+(?:\.\d+)*)', js_content)
        if jquery_version_match:
            version = jquery_version_match.group(1)
            if any(version.startswith(vuln_ver) for vuln_ver in self.vuln_patterns['jquery']['versions']):
                vulnerabilities.append({
                    'library': 'jquery',
                    'version': version,
                    'url': 'inline',
                    'vulnerabilities': self.vuln_patterns['jquery']['vulnerabilities'],
                    'severity': 'high'
                })
        
        # Check for other library patterns
        angular_pattern = re.search(r'angular\.version\s*[=:]\s*["\'](\d+(?:\.\d+)*)["\']', js_content)
        if angular_pattern:
            version = angular_pattern.group(1)
            if any(version.startswith(vuln_ver) for vuln_ver in self.vuln_patterns['angular']['versions']):
                vulnerabilities.append({
                    'library': 'angular',
                    'version': version,
                    'url': 'inline',
                    'vulnerabilities': self.vuln_patterns['angular']['vulnerabilities'],
                    'severity': 'high'
                })
        
        return vulnerabilities
