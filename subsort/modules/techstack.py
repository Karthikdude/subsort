"""
Technology Stack module for SubSort
Detects and sorts subdomains based on their tech stack
"""

import re
from typing import Dict, Any, List
from .base import BaseModule


class TechstackModule(BaseModule):
    """Module for detecting technology stack from HTTP headers and content"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Technology stack signatures
        self.tech_signatures = {
            # Web Servers
            'apache': ['Apache', 'apache'],
            'nginx': ['nginx', 'Nginx'],
            'iis': ['Microsoft-IIS', 'IIS'],
            'tomcat': ['Apache-Coyote', 'Tomcat'],
            'jetty': ['Jetty'],
            'lighttpd': ['lighttpd'],
            
            # Programming Languages/Frameworks
            'php': ['PHP', r'X-Powered-By.*PHP'],
            'nodejs': ['Express', 'Node.js', r'X-Powered-By.*Express'],
            'aspnet': ['X-AspNet-Version', r'X-Powered-By.*ASP\.NET'],
            'django': ['django', 'Django'],
            'flask': ['Flask', 'Werkzeug'],
            'rails': ['Ruby', 'Rails', r'X-Powered-By.*Rails'],
            'laravel': ['laravel', 'Laravel'],
            'spring': ['Spring', 'X-Application-Context'],
            
            # CMS/Platforms
            'wordpress': ['wp-content', 'wp-includes', 'WordPress'],
            'drupal': ['Drupal', 'X-Drupal'],
            'joomla': ['Joomla', '/components/com_'],
            'magento': ['Magento', 'X-Magento'],
            'shopify': ['Shopify', 'myshopify.com'],
            
            # CDN/Cloud
            'cloudflare': ['cloudflare', 'CF-RAY'],
            'aws': ['AmazonS3', 'X-Amz-', 'amazonaws.com'],
            'azure': ['X-Azure', 'windows.net'],
            'googlecloud': ['Google', 'X-Cloud-Trace-Context'],
            
            # Security/WAF
            'modsecurity': ['mod_security', 'ModSecurity'],
            'sucuri': ['X-Sucuri-ID', 'sucuri'],
            'incapsula': ['X-Iinfo', 'incap_ses'],
            
            # Analytics/Tracking
            'googleanalytics': ['google-analytics', 'gtag', r'ga\('],
            'gtm': ['googletagmanager', 'GTM-'],
            'hotjar': ['hotjar.com', 'hjid'],
            
            # JavaScript Frameworks
            'react': ['react', 'React', '__REACT_DEVTOOLS'],
            'angular': ['angular', 'ng-version'],
            'vue': ['vue.js', 'Vue.js', '__VUE__'],
            'jquery': ['jquery', 'jQuery'],
            'bootstrap': ['bootstrap', 'Bootstrap']
        }
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """
        Detect technology stack from headers and content
        
        Args:
            subdomain: The subdomain to analyze
            
        Returns:
            Dictionary containing technology stack information
        """
        result = {
            'subdomain': subdomain,
            'technologies': [],
            'web_server': None,
            'programming_language': None,
            'framework': None,
            'cms': None,
            'cdn': None,
            'security': [],
            'analytics': [],
            'frontend': []
        }
        
        try:
            # Make HTTP request
            response, content, scheme = await self.http_client.check_both_schemes(subdomain)
            
            if not response:
                self.log_warning(f"No response received", subdomain)
                return result
            
            # Analyze headers
            headers_text = ' '.join([f"{k}: {v}" for k, v in response.headers.items()])
            
            # Analyze content if available
            content_text = content or ""
            
            # Combined text for analysis
            full_text = f"{headers_text} {content_text}"
            
            detected_techs = []
            
            # Check for technology signatures
            for tech_name, signatures in self.tech_signatures.items():
                for signature in signatures:
                    if re.search(signature, full_text, re.IGNORECASE):
                        detected_techs.append(tech_name)
                        break
            
            # Remove duplicates while preserving order
            detected_techs = list(dict.fromkeys(detected_techs))
            result['technologies'] = detected_techs
            
            # Categorize technologies
            self._categorize_technologies(result, detected_techs, dict(response.headers))
            
            self.log_debug(f"Detected technologies: {', '.join(detected_techs)}", subdomain)
            
        except Exception as e:
            self.log_error(f"Technology stack detection failed: {e}", subdomain)
        
        return result
    
    def _categorize_technologies(self, result: Dict[str, Any], techs: List[str], headers: Dict[str, str]):
        """Categorize detected technologies into specific types"""
        
        # Web servers
        web_servers = ['apache', 'nginx', 'iis', 'tomcat', 'jetty', 'lighttpd']
        for tech in techs:
            if tech in web_servers:
                result['web_server'] = tech
                break
        
        # Programming languages
        languages = ['php', 'nodejs', 'aspnet', 'python', 'ruby', 'java']
        for tech in techs:
            if tech in languages:
                result['programming_language'] = tech
                break
        
        # Frameworks
        frameworks = ['django', 'flask', 'rails', 'laravel', 'spring', 'express']
        for tech in techs:
            if tech in frameworks:
                result['framework'] = tech
                break
        
        # CMS
        cms_list = ['wordpress', 'drupal', 'joomla', 'magento', 'shopify']
        for tech in techs:
            if tech in cms_list:
                result['cms'] = tech
                break
        
        # CDN
        cdn_list = ['cloudflare', 'aws', 'azure', 'googlecloud']
        for tech in techs:
            if tech in cdn_list:
                result['cdn'] = tech
                break
        
        # Security
        security_list = ['modsecurity', 'sucuri', 'incapsula', 'cloudflare']
        result['security'] = [tech for tech in techs if tech in security_list]
        
        # Analytics
        analytics_list = ['googleanalytics', 'gtm', 'hotjar']
        result['analytics'] = [tech for tech in techs if tech in analytics_list]
        
        # Frontend
        frontend_list = ['react', 'angular', 'vue', 'jquery', 'bootstrap']
        result['frontend'] = [tech for tech in techs if tech in frontend_list]