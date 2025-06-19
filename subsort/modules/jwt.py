
"""
JWT Token Analysis Module
Extracts and decodes JWT tokens for security analysis
"""

import re
import json
import base64
from typing import Dict, Any, List
from .base import BaseModule

class JwtModule(BaseModule):
    """Module for analyzing JWT tokens"""
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """Extract and analyze JWT tokens from subdomain"""
        result = {
            'jwt_tokens': [],
            'token_count': 0,
            'insecure_configs': [],
            'algorithms_detected': []
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
                            headers = dict(response.headers)
                            result.update(await self._analyze_jwt_tokens(content, headers))
                            break
                except Exception as e:
                    self.log_debug(f"Failed to fetch {url}: {e}", subdomain)
                    continue
        
        except Exception as e:
            self.log_error(f"JWT analysis failed: {e}", subdomain)
        
        return result
    
    async def _analyze_jwt_tokens(self, html_content: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Analyze content and headers for JWT tokens"""
        jwt_tokens = []
        algorithms_detected = []
        insecure_configs = []
        
        try:
            # JWT pattern (three base64url encoded parts separated by dots)
            jwt_pattern = r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'
            
            # Search in headers
            for header_name, header_value in headers.items():
                if 'authorization' in header_name.lower() or 'token' in header_name.lower():
                    tokens = re.findall(jwt_pattern, header_value)
                    for token in tokens:
                        jwt_info = self._decode_jwt(token, f'header:{header_name}')
                        if jwt_info:
                            jwt_tokens.append(jwt_info)
            
            # Search in HTML content
            content_tokens = re.findall(jwt_pattern, html_content)
            for token in content_tokens:
                jwt_info = self._decode_jwt(token, 'html_content')
                if jwt_info:
                    jwt_tokens.append(jwt_info)
            
            # Analyze algorithms and security issues
            for jwt_token in jwt_tokens:
                algorithm = jwt_token.get('header', {}).get('alg', 'unknown')
                if algorithm not in algorithms_detected:
                    algorithms_detected.append(algorithm)
                
                # Check for insecure configurations
                security_issues = self._check_jwt_security(jwt_token)
                insecure_configs.extend(security_issues)
            
            return {
                'jwt_tokens': jwt_tokens,
                'token_count': len(jwt_tokens),
                'insecure_configs': list(set(insecure_configs)),
                'algorithms_detected': algorithms_detected
            }
        
        except Exception as e:
            self.log_error(f"Error analyzing JWT tokens: {e}")
            return {
                'jwt_tokens': [],
                'token_count': 0,
                'insecure_configs': [],
                'algorithms_detected': []
            }
    
    def _decode_jwt(self, token: str, source: str) -> Dict[str, Any]:
        """Decode JWT token and extract information"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            
            # Decode header
            header_data = self._decode_base64url(parts[0])
            header = json.loads(header_data) if header_data else {}
            
            # Decode payload
            payload_data = self._decode_base64url(parts[1])
            payload = json.loads(payload_data) if payload_data else {}
            
            return {
                'token': token[:50] + '...' if len(token) > 50 else token,
                'source': source,
                'header': header,
                'payload': payload,
                'signature': parts[2][:20] + '...' if len(parts[2]) > 20 else parts[2]
            }
        
        except Exception as e:
            self.log_debug(f"Error decoding JWT: {e}")
            return None
    
    def _decode_base64url(self, data: str) -> str:
        """Decode base64url encoded data"""
        try:
            # Add padding if necessary
            missing_padding = len(data) % 4
            if missing_padding:
                data += '=' * (4 - missing_padding)
            
            # Replace URL-safe characters
            data = data.replace('-', '+').replace('_', '/')
            
            return base64.b64decode(data).decode('utf-8')
        
        except Exception:
            return None
    
    def _check_jwt_security(self, jwt_token: Dict[str, Any]) -> List[str]:
        """Check JWT token for security issues"""
        issues = []
        
        header = jwt_token.get('header', {})
        payload = jwt_token.get('payload', {})
        
        # Check algorithm
        algorithm = header.get('alg', '').upper()
        if algorithm == 'NONE':
            issues.append('No signature algorithm (alg: none)')
        elif algorithm in ['HS256', 'HS384', 'HS512']:
            issues.append('HMAC algorithm detected (shared secret)')
        
        # Check expiration
        exp = payload.get('exp')
        if not exp:
            issues.append('No expiration time (exp) claim')
        
        # Check issued at
        iat = payload.get('iat')
        if not iat:
            issues.append('No issued at (iat) claim')
        
        # Check audience
        aud = payload.get('aud')
        if not aud:
            issues.append('No audience (aud) claim')
        
        # Check issuer
        iss = payload.get('iss')
        if not iss:
            issues.append('No issuer (iss) claim')
        
        return issues
