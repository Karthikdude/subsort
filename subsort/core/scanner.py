"""
Main scanning engine for SubSort
Handles subdomain scanning with async processing and module management
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import time

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn

from .http_client import AsyncHttpClient
from ..modules import get_module

console = Console()

class SubdomainScanner:
    """Main scanner class that orchestrates subdomain analysis"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.enabled_modules = []
        self.http_client = AsyncHttpClient(config, logger)
        
    def enable_module(self, module_name: str):
        """Enable a scanning module"""
        try:
            module_class = get_module(module_name)
            if module_class:
                self.enabled_modules.append({
                    'name': module_name,
                    'class': module_class,
                    'instance': module_class(self.http_client, self.logger)
                })
                self.logger.info(f"Enabled module: {module_name}")
            else:
                self.logger.warning(f"Unknown module: {module_name}")
        except Exception as e:
            self.logger.error(f"Failed to enable module {module_name}: {e}")
    
    def get_enabled_modules(self) -> List[str]:
        """Get list of enabled module names"""
        return [module['name'] for module in self.enabled_modules]
    
    async def scan_subdomain(self, subdomain: str) -> Dict[str, Any]:
        """Scan a single subdomain with all enabled modules"""
        result = {
            'subdomain': subdomain,
            'timestamp': int(time.time())
        }
        
        self.logger.debug(f"Starting scan for: {subdomain}")
        
        try:
            # Run each enabled module with proper error handling
            for module_info in self.enabled_modules:
                module_name = module_info['name']
                module_instance = module_info['instance']
                
                try:
                    self.logger.debug(f"Running module {module_name} for {subdomain}")
                    
                    # Create a timeout for each module to prevent hanging
                    if hasattr(module_instance, 'safe_scan'):
                        module_result = await asyncio.wait_for(
                            module_instance.safe_scan(subdomain),
                            timeout=self.config.get('timeout', 5) * 2
                        )
                    else:
                        module_result = await asyncio.wait_for(
                            module_instance.scan(subdomain),
                            timeout=self.config.get('timeout', 5) * 2
                        )
                    
                    if module_result:
                        result.update(module_result)
                    
                except asyncio.TimeoutError:
                    self.logger.error(f"Module {module_name} timed out for {subdomain}")
                    result[f'{module_name}_timeout'] = True
                except Exception as e:
                    self.logger.error(f"Module {module_name} failed for {subdomain}: {e}")
                    result[f'{module_name}_error'] = str(e)
            
            # Add delay if configured
            if self.config.get('delay', 0) > 0:
                await asyncio.sleep(self.config['delay'])
                
        except Exception as e:
            self.logger.error(f"Scan failed for {subdomain}: {e}")
            result['scan_error'] = str(e)
        
        self.logger.debug(f"Completed scan for: {subdomain}")
        return result
    
    async def scan_batch(self, subdomains: List[str]) -> List[Dict[str, Any]]:
        """Scan a batch of subdomains concurrently"""
        semaphore = asyncio.Semaphore(self.config.get('threads', 50))
        
        async def scan_with_semaphore(subdomain: str):
            async with semaphore:
                return await self.scan_subdomain(subdomain)
        
        tasks = [scan_with_semaphore(subdomain) for subdomain in subdomains]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Batch scan failed for {subdomains[i]}: {result}")
                processed_results.append({
                    'subdomain': subdomains[i],
                    'batch_error': str(result),
                    'timestamp': int(time.time())
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def scan_subdomains(self, subdomains: List[str], show_progress: bool = True) -> List[Dict[str, Any]]:
        """Scan all subdomains with progress tracking"""
        all_results = []
        batch_size = min(self.config.get('threads', 50), len(subdomains))
        
        if show_progress:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=console
            )
            
            with progress:
                task = progress.add_task("Scanning subdomains...", total=len(subdomains))
                
                # Process in batches
                for i in range(0, len(subdomains), batch_size):
                    batch = subdomains[i:i + batch_size]
                    
                    self.logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} subdomains")
                    
                    try:
                        batch_results = await self.scan_batch(batch)
                        all_results.extend(batch_results)
                        
                        progress.update(task, advance=len(batch))
                        
                    except Exception as e:
                        self.logger.error(f"Batch processing failed: {e}")
                        # Add error results for failed batch
                        for subdomain in batch:
                            all_results.append({
                                'subdomain': subdomain,
                                'batch_processing_error': str(e),
                                'timestamp': int(time.time())
                            })
                        progress.update(task, advance=len(batch))
        else:
            # Process without progress bar
            for i in range(0, len(subdomains), batch_size):
                batch = subdomains[i:i + batch_size]
                
                self.logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} subdomains")
                
                try:
                    batch_results = await self.scan_batch(batch)
                    all_results.extend(batch_results)
                    
                except Exception as e:
                    self.logger.error(f"Batch processing failed: {e}")
                    # Add error results for failed batch
                    for subdomain in batch:
                        all_results.append({
                            'subdomain': subdomain,
                            'batch_processing_error': str(e),
                            'timestamp': int(time.time())
                        })
        
        self.logger.info(f"Scan completed. Processed {len(all_results)} results")
        return all_results
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.http_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.http_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def cleanup(self):
        """Clean up resources"""
        if hasattr(self.http_client, 'session') and self.http_client.session:
            await self.http_client.session.close()
