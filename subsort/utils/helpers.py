"""
Helper utility functions for SubSort
Contains common functions used across the application
"""

import re
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

def validate_file(file_path: str) -> bool:
    """
    Validate if a file exists and is readable
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if file is valid and readable, False otherwise
    """
    try:
        path = Path(file_path)
        return path.exists() and path.is_file() and path.stat().st_size > 0
    except Exception:
        return False

def read_subdomains_from_file(file_path: str) -> List[str]:
    """
    Read subdomains from a file, one per line
    
    Args:
        file_path: Path to the file containing subdomains
        
    Returns:
        List of clean subdomains
    """
    subdomains = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Clean and validate subdomain
                subdomain = clean_subdomain(line)
                if subdomain and is_valid_subdomain(subdomain):
                    subdomains.append(subdomain)
                else:
                    # Log invalid subdomain but continue processing
                    pass
    
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")
    
    return subdomains

def clean_subdomain(subdomain: str) -> str:
    """
    Clean and normalize a subdomain string
    
    Args:
        subdomain: Raw subdomain string
        
    Returns:
        Cleaned subdomain string
    """
    if not subdomain:
        return ""
    
    # Remove protocol if present
    if subdomain.startswith(('http://', 'https://')):
        try:
            parsed = urlparse(subdomain)
            subdomain = parsed.netloc or parsed.path
        except Exception:
            pass
    
    # Remove path, query, and fragment
    subdomain = subdomain.split('/')[0].split('?')[0].split('#')[0]
    
    # Remove port if present
    if ':' in subdomain and not subdomain.count(':') > 1:  # Avoid IPv6 addresses
        subdomain = subdomain.split(':')[0]
    
    # Convert to lowercase
    subdomain = subdomain.lower().strip()
    
    # Remove trailing dots
    subdomain = subdomain.rstrip('.')
    
    return subdomain

def is_valid_subdomain(subdomain: str) -> bool:
    """
    Validate if a string is a valid subdomain format
    
    Args:
        subdomain: Subdomain string to validate
        
    Returns:
        True if valid subdomain format, False otherwise
    """
    if not subdomain:
        return False
    
    # Basic length check
    if len(subdomain) > 253:
        return False
    
    # Check for valid characters and format
    # Allow letters, numbers, hyphens, and dots
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$'
    
    if not re.match(pattern, subdomain):
        return False
    
    # Check each label (part between dots)
    labels = subdomain.split('.')
    
    for label in labels:
        # Each label must be 1-63 characters
        if not label or len(label) > 63:
            return False
        
        # Labels cannot start or end with hyphens
        if label.startswith('-') or label.endswith('-'):
            return False
        
        # Labels must contain at least one letter or number
        if not re.search(r'[a-zA-Z0-9]', label):
            return False
    
    # Must have at least one dot (be a subdomain, not just a domain)
    if '.' not in subdomain:
        return False
    
    return True

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to specified length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated string
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from URL
    
    Args:
        url: URL string
        
    Returns:
        Domain string or None if extraction fails
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None

def generate_output_filename(base_name: str, extension: str = 'txt') -> str:
    """
    Generate timestamped output filename
    
    Args:
        base_name: Base name for the file
        extension: File extension
        
    Returns:
        Generated filename with timestamp
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return f"{base_name}_{timestamp}.{extension}"
