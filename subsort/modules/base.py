"""
Adding error handling to the base module class for SubSort scanning modules.
"""
"""
Base module class for SubSort scanning modules
Provides common interface and functionality for all modules
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from ..core.http_client import AsyncHttpClient

class BaseModule(ABC):
    """Base class for all scanning modules"""

    def __init__(self, http_client: AsyncHttpClient, logger: logging.Logger):
        self.http_client = http_client
        self.logger = logger
        self.module_name = self.__class__.__name__.replace('Module', '').lower()

    @abstractmethod
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """
        Scan a subdomain and return results

        Args:
            subdomain: The subdomain to scan

        Returns:
            Dictionary containing scan results
        """
        pass

    def log_debug(self, message: str, subdomain: str = ""):
        """Log debug message with module context"""
        if subdomain:
            self.logger.debug(f"[{self.module_name.upper()}] {subdomain}: {message}")
        else:
            self.logger.debug(f"[{self.module_name.upper()}] {message}")

    def log_error(self, message: str, subdomain: str = ""):
        """Log error message with module context"""
        if subdomain:
            self.logger.error(f"[{self.module_name.upper()}] {subdomain}: {message}")
        else:
            self.logger.error(f"[{self.module_name.upper()}] {message}")

    def log_warning(self, message: str, subdomain: str = ""):
        """Log warning message with module context"""
        if subdomain:
            self.logger.warning(f"[{self.module_name.upper()}] {subdomain}: {message}")
        else:
            self.logger.warning(f"[{self.module_name.upper()}] {message}")

    async def safe_scan(self, subdomain: str) -> Dict[str, Any]:
        """Safe wrapper for scan method with error handling"""
        try:
            return await self.scan(subdomain)
        except Exception as e:
            self.log_error(f"Module scan failed: {e}", subdomain)
            return {}