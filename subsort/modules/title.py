"""
Title module for SubSort
Extracts page titles and basic content information
"""

import re
from typing import Dict, Any
from .base import BaseModule

class TitleModule(BaseModule):
    """Module for extracting page titles and basic content information"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Regex patterns for title extraction
        self.title_patterns = [
            re.compile(r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL),
            re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)', re.IGNORECASE),
            re.compile(r'<meta[^>]+name=["\']twitter:title["\'][^>]+content=["\']([^"\']+)', re.IGNORECASE)
        ]
        
        # Regex patterns for description extraction
        self.description_patterns = [
            re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', re.IGNORECASE),
            re.compile(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)', re.IGNORECASE),
            re.compile(r'<meta[^>]+name=["\']twitter:description["\'][^>]+content=["\']([^"\']+)', re.IGNORECASE)
        ]
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Decode HTML entities
        import html
        text = html.unescape(text)
        
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        
        # Trim to reasonable length
        if len(text) > 200:
            text = text[:197] + "..."
        
        return text.strip()
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """
        Extract page title and basic content information
        
        Args:
            subdomain: The subdomain to analyze
            
        Returns:
            Dictionary containing title and content information
        """
        result = {}
        
        try:
            self.log_debug(f"Extracting title for {subdomain}")
            
            # Try both HTTPS and HTTP
            response, content, final_url = await self.http_client.check_both_schemes(subdomain)
            
            if response is not None and content:
                
                # Extract title
                title = self.extract_title(content)
                if title:
                    result['title'] = title
                else:
                    result['title'] = 'No title found'
                
                # Extract description
                description = self.extract_description(content)
                if description:
                    result['description'] = description
                
                # Basic content analysis
                result['content_type'] = response.headers.get('Content-Type', '').split(';')[0].strip()
                result['content_size'] = len(content)
                
                # Detect content language
                content_language = response.headers.get('Content-Language', '').strip()
                if content_language:
                    result['content_language'] = content_language
                else:
                    # Try to extract from HTML lang attribute
                    lang_match = re.search(r'<html[^>]+lang=["\']([^"\']+)', content, re.IGNORECASE)
                    if lang_match:
                        result['content_language'] = lang_match.group(1)
                
                # Check for common frameworks/platforms in content
                framework_indicators = {
                    'wordpress': ['wp-content', 'wp-includes', '/wp-json/'],
                    'drupal': ['drupal', 'sites/default/files'],
                    'joomla': ['/joomla/', 'joomla!'],
                    'react': ['react', '__REACT_DEVTOOLS'],
                    'angular': ['ng-', 'angular'],
                    'vue': ['vue.js', '__vue__'],
                    'bootstrap': ['bootstrap', 'btn-'],
                    'jquery': ['jquery', '$.']
                }
                
                detected_frameworks = []
                content_lower = content.lower()
                
                for framework, indicators in framework_indicators.items():
                    for indicator in indicators:
                        if indicator in content_lower:
                            detected_frameworks.append(framework)
                            break
                
                if detected_frameworks:
                    result['frameworks'] = detected_frameworks
                
                # Check for common security indicators
                security_indicators = {
                    'login_form': ['type="password"', 'login', 'signin'],
                    'admin_panel': ['/admin', '/administrator', 'admin panel'],
                    'database_error': ['mysql error', 'sql error', 'database error'],
                    'debug_info': ['debug', 'traceback', 'stack trace']
                }
                
                security_findings = []
                for indicator, patterns in security_indicators.items():
                    for pattern in patterns:
                        if pattern in content_lower:
                            security_findings.append(indicator)
                            break
                
                if security_findings:
                    result['security_indicators'] = security_findings
                
                self.log_debug(f"Title: {title[:50]}{'...' if len(title) > 50 else ''}", subdomain)
                
            else:
                result['title'] = 'Unable to retrieve content'
                self.log_debug(f"Unable to retrieve content for title extraction", subdomain)
        
        except Exception as e:
            result['title_error'] = str(e)
            self.log_error(f"Title extraction failed: {e}", subdomain)
        
        return result
    
    def extract_title(self, content: str) -> str:
        """Extract title from HTML content"""
        for pattern in self.title_patterns:
            match = pattern.search(content)
            if match:
                title = self.clean_text(match.group(1))
                if title:
                    return title
        return ""
    
    def extract_description(self, content: str) -> str:
        """Extract description from HTML content"""
        for pattern in self.description_patterns:
            match = pattern.search(content)
            if match:
                description = self.clean_text(match.group(1))
                if description:
                    return description
        return ""
