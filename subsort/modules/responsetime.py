"""
Response Time module for SubSort
Measures response times and sorts subdomains based on latency
"""

import time
import asyncio
from typing import Dict, Any
from .base import BaseModule


class ResponsetimeModule(BaseModule):
    """Module for measuring and analyzing response times"""
    
    async def scan(self, subdomain: str) -> Dict[str, Any]:
        """
        Measure response times for subdomain
        
        Args:
            subdomain: The subdomain to analyze
            
        Returns:
            Dictionary containing response time information
        """
        result = {
            'subdomain': subdomain,
            'response_time': None,
            'response_times': [],
            'average_response_time': None,
            'min_response_time': None,
            'max_response_time': None,
            'latency_category': None,
            'connection_time': None,
            'ttfb': None  # Time to first byte
        }
        
        try:
            response_times = []
            
            # Perform multiple measurements for accuracy
            for i in range(3):
                start_time = time.time()
                response, content, scheme = await self.http_client.check_both_schemes(subdomain)
                end_time = time.time()
                
                if response:
                    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    response_times.append(response_time)
                
                # Small delay between requests
                if i < 2:
                    await asyncio.sleep(0.1)
            
            if response_times:
                result['response_times'] = response_times
                result['response_time'] = response_times[0]  # First measurement
                result['average_response_time'] = sum(response_times) / len(response_times)
                result['min_response_time'] = min(response_times)
                result['max_response_time'] = max(response_times)
                
                # Categorize latency
                avg_time = result['average_response_time']
                if avg_time < 100:
                    result['latency_category'] = 'excellent'
                elif avg_time < 300:
                    result['latency_category'] = 'good'
                elif avg_time < 1000:
                    result['latency_category'] = 'fair'
                elif avg_time < 3000:
                    result['latency_category'] = 'slow'
                else:
                    result['latency_category'] = 'very_slow'
                
                self.log_debug(f"Average response time: {avg_time:.2f}ms", subdomain)
            else:
                self.log_warning(f"No successful response received", subdomain)
            
        except Exception as e:
            self.log_error(f"Response time measurement failed: {e}", subdomain)
        
        return result