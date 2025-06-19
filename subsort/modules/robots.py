"""
Robots module for SubSort
Fetches and parses robots.txt and sitemap.xml for hidden/disallowed endpoints
"""

import re
from typing import Dict, Any, List
from .base import BaseModule


class RobotsModule(BaseModule):
    """Module for analyzing robots.txt and sitemap.xml files"""
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """
        Fetch and parse robots.txt and sitemap.xml
        
        Args:
            subdomain: The subdomain to analyze
            
        Returns:
            Dictionary containing robots and sitemap information
        """
        result = {
            'subdomain': subdomain,
            'robots_accessible': False,
            'robots_content': None,
            'disallowed_paths': [],
            'allowed_paths': [],
            'crawl_delay': None,
            'sitemap_urls': [],
            'sitemaps_found': [],
            'interesting_paths': [],
            'user_agents': []
        }
        
        try:
            # Fetch robots.txt
            response, content, scheme = await self.http_client.check_both_schemes(subdomain)
            if response:
                robots_url = f"{scheme}://{subdomain}/robots.txt"
                robots_response, robots_content = await self.http_client.get(robots_url)
                
                if robots_response and robots_response.status == 200 and robots_content:
                    result['robots_accessible'] = True
                    result['robots_content'] = robots_content
                    
                    # Parse robots.txt
                    self._parse_robots_txt(robots_content, result)
                    
                    # Find interesting paths
                    result['interesting_paths'] = self._find_interesting_paths(robots_content)
                    
                    self.log_debug(f"Found {len(result['disallowed_paths'])} disallowed paths", subdomain)
                
                # Check for sitemaps
                await self._check_sitemaps(subdomain, scheme, result)
                
        except Exception as e:
            self.log_error(f"Robots.txt analysis failed: {e}", subdomain)
        
        return result
    
    def _parse_robots_txt(self, content: str, result: Dict[str, Any]):
        """Parse robots.txt content"""
        lines = content.split('\n')
        current_user_agent = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.lower().startswith('user-agent:'):
                user_agent = line.split(':', 1)[1].strip()
                current_user_agent = user_agent
                if user_agent not in result['user_agents']:
                    result['user_agents'].append(user_agent)
            
            elif line.lower().startswith('disallow:'):
                path = line.split(':', 1)[1].strip()
                if path and path not in result['disallowed_paths']:
                    result['disallowed_paths'].append(path)
            
            elif line.lower().startswith('allow:'):
                path = line.split(':', 1)[1].strip()
                if path and path not in result['allowed_paths']:
                    result['allowed_paths'].append(path)
            
            elif line.lower().startswith('crawl-delay:'):
                delay = line.split(':', 1)[1].strip()
                try:
                    result['crawl_delay'] = int(delay)
                except ValueError:
                    pass
            
            elif line.lower().startswith('sitemap:'):
                sitemap_url = line.split(':', 1)[1].strip()
                if sitemap_url and sitemap_url not in result['sitemap_urls']:
                    result['sitemap_urls'].append(sitemap_url)
    
    def _find_interesting_paths(self, content: str) -> List[str]:
        """Find potentially interesting paths in robots.txt"""
        interesting_keywords = [
            'admin', 'login', 'api', 'private', 'internal', 'backup',
            'config', 'test', 'dev', 'staging', 'tmp', 'temp',
            'secret', 'hidden', 'upload', 'download', 'logs',
            'phpMyAdmin', 'wp-admin', 'wp-content', 'database'
        ]
        
        interesting_paths = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip().lower()
            if line.startswith('disallow:') or line.startswith('allow:'):
                path = line.split(':', 1)[1].strip()
                for keyword in interesting_keywords:
                    if keyword.lower() in path.lower():
                        if path not in interesting_paths:
                            interesting_paths.append(path)
                        break
        
        return interesting_paths
    
    async def _check_sitemaps(self, subdomain: str, scheme: str, result: Dict[str, Any]):
        """Check for common sitemap locations"""
        sitemap_paths = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemaps.xml',
            '/sitemap1.xml',
            '/sitemap.txt'
        ]
        
        for path in sitemap_paths:
            try:
                sitemap_url = f"{scheme}://{subdomain}{path}"
                response, content = await self.http_client.get(sitemap_url)
                
                if response and response.status == 200 and content:
                    sitemap_info = {
                        'url': sitemap_url,
                        'size': len(content),
                        'type': 'xml' if path.endswith('.xml') else 'txt'
                    }
                    
                    # Parse XML sitemap for URL count
                    if path.endswith('.xml'):
                        url_count = content.count('<url>')
                        sitemap_count = content.count('<sitemap>')
                        sitemap_info['url_count'] = url_count
                        sitemap_info['sitemap_count'] = sitemap_count
                    
                    result['sitemaps_found'].append(sitemap_info)
                    
            except Exception as e:
                self.log_debug(f"Failed to check sitemap {path}: {e}", subdomain)