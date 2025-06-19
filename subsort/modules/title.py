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
            response, content, final_url = await self.http_client.check_both_schemes(subdomain)

            if response is None or not content:
                return {
                    'title': 'No title found',
                    'title_length': 0,
                    'has_title': False
                }

            # Handle both response object and dictionary
            if isinstance(response, dict):
                headers = response.get('headers', {})
            else:
                headers = getattr(response, 'headers', {})

            # Convert headers to dict if needed
            if hasattr(headers, 'items'):
                headers = dict(headers)

            # Only process HTML content
            content_type = headers.get('content-type', headers.get('Content-Type', '')).lower()
            if 'text/html' not in content_type:
                return {
                    'title': 'Non-HTML content',
                    'content_type': content_type,
                    'title_length': 0,
                    'has_title': False
                }

            # Extract title from HTML
            title = self._extract_title_from_html(content)

            return {
                'title': title,
                'title_length': len(title) if title else 0,
                'has_title': bool(title and title != 'No title found'),
                'description': self._extract_meta_description(content)
            }

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

    def _extract_title_from_html(self, content: str) -> str:
        """Extract title from HTML content using patterns"""
        for pattern in self.title_patterns:
            match = pattern.search(content)
            if match:
                title = self.clean_text(match.group(1))
                if title:
                    return title
        return "No title found"

    def _extract_meta_description(self, content: str) -> str:
        """Extract meta description from HTML content"""
        for pattern in self.description_patterns:
            match = pattern.search(content)
            if match:
                description = self.clean_text(match.group(1))
                if description:
                    return description
        return ""