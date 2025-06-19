
"""
CNAME Takeover Detection Module
Checks CNAME records for possible subdomain takeover vulnerabilities
"""

import socket
from typing import Dict, Any, List
from .base import BaseModule

class CnameModule(BaseModule):
    """Module for detecting CNAME takeover vulnerabilities"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Known vulnerable CNAME targets
        self.vulnerable_services = {
            'amazonaws.com': 'AWS S3/ELB',
            'cloudfront.net': 'AWS CloudFront',
            'azurewebsites.net': 'Azure Websites',
            'herokuapp.com': 'Heroku',
            'github.io': 'GitHub Pages',
            'netlify.com': 'Netlify',
            'vercel.app': 'Vercel',
            'surge.sh': 'Surge.sh',
            'bitbucket.io': 'Bitbucket',
            'fastly.com': 'Fastly CDN',
            'cloudflare.net': 'Cloudflare',
            'unbounce.com': 'Unbounce',
            'helpjuice.com': 'HelpJuice',
            'desk.com': 'Salesforce Desk',
            'teamwork.com': 'Teamwork',
            'zendesk.com': 'Zendesk'
        }
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """Check subdomain for CNAME takeover vulnerabilities"""
        result = {
            'cname_records': [],
            'vulnerable': False,
            'takeover_possible': False,
            'service_identified': None,
            'risk_level': 'low'
        }
        
        try:
            # Resolve CNAME records
            cname_chain = await self._resolve_cname_chain(subdomain)
            result['cname_records'] = cname_chain
            
            if cname_chain:
                # Check for vulnerable services
                takeover_info = self._check_takeover_vulnerability(cname_chain)
                result.update(takeover_info)
        
        except Exception as e:
            self.log_error(f"CNAME analysis failed: {e}", subdomain)
        
        return result
    
    async def _resolve_cname_chain(self, subdomain: str) -> List[Dict[str, str]]:
        """Resolve CNAME chain for subdomain"""
        cname_chain = []
        current_domain = subdomain
        max_depth = 10  # Prevent infinite loops
        depth = 0
        
        try:
            while depth < max_depth:
                try:
                    # Try to resolve CNAME
                    import dns.resolver
                    resolver = dns.resolver.Resolver()
                    resolver.timeout = 5
                    resolver.lifetime = 5
                    
                    try:
                        cname_result = resolver.resolve(current_domain, 'CNAME')
                        for cname in cname_result:
                            cname_target = str(cname).rstrip('.')
                            cname_chain.append({
                                'domain': current_domain,
                                'cname': cname_target,
                                'depth': depth
                            })
                            current_domain = cname_target
                            depth += 1
                            break
                        else:
                            break
                    except dns.resolver.NoAnswer:
                        # No CNAME record, try A record
                        try:
                            a_result = resolver.resolve(current_domain, 'A')
                            ip_addresses = [str(ip) for ip in a_result]
                            if cname_chain:  # Only add if we have CNAME records
                                cname_chain[-1]['resolved_ips'] = ip_addresses
                        except Exception:
                            pass
                        break
                    except dns.resolver.NXDOMAIN:
                        # Domain doesn't exist - potential takeover
                        if cname_chain:
                            cname_chain[-1]['nxdomain'] = True
                        break
                
                except ImportError:
                    # Fallback to socket-based resolution
                    try:
                        ip = socket.gethostbyname(current_domain)
                        if cname_chain:
                            cname_chain[-1]['resolved_ips'] = [ip]
                    except socket.gaierror:
                        if cname_chain:
                            cname_chain[-1]['resolution_failed'] = True
                    break
                
                except Exception as e:
                    self.log_debug(f"Error resolving {current_domain}: {e}")
                    break
        
        except Exception as e:
            self.log_error(f"Error in CNAME chain resolution: {e}")
        
        return cname_chain
    
    def _check_takeover_vulnerability(self, cname_chain: List[Dict[str, str]]) -> Dict[str, Any]:
        """Check CNAME chain for takeover vulnerabilities"""
        vulnerable = False
        takeover_possible = False
        service_identified = None
        risk_level = 'low'
        
        try:
            for cname_record in cname_chain:
                cname_target = cname_record.get('cname', '')
                
                # Check against known vulnerable services
                for service_domain, service_name in self.vulnerable_services.items():
                    if service_domain in cname_target:
                        service_identified = service_name
                        vulnerable = True
                        
                        # Check if domain resolution fails (NXDOMAIN)
                        if cname_record.get('nxdomain') or cname_record.get('resolution_failed'):
                            takeover_possible = True
                            risk_level = 'high'
                        else:
                            risk_level = 'medium'
                        break
                
                # Additional checks for specific patterns
                if not vulnerable:
                    suspicious_patterns = [
                        '.s3.amazonaws.com',
                        '.s3-website',
                        '.cloudfront.net',
                        '.azurewebsites.net',
                        '.herokuapp.com'
                    ]
                    
                    for pattern in suspicious_patterns:
                        if pattern in cname_target:
                            vulnerable = True
                            service_identified = f'Suspicious pattern: {pattern}'
                            
                            if cname_record.get('nxdomain') or cname_record.get('resolution_failed'):
                                takeover_possible = True
                                risk_level = 'high'
                            else:
                                risk_level = 'medium'
                            break
        
        except Exception as e:
            self.log_error(f"Error checking takeover vulnerability: {e}")
        
        return {
            'vulnerable': vulnerable,
            'takeover_possible': takeover_possible,
            'service_identified': service_identified,
            'risk_level': risk_level
        }
