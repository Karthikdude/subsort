#!/usr/bin/env python3
"""
SubSort - Enhanced CLI Recon Tool
A high-performance Python-based CLI reconnaissance tool for subdomain analysis
Developed by Karthik S Sathyan
"""

import sys
import signal
import asyncio
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from subsort.cli import main

def signal_handler(signum, frame):
    """Handle interruption signals gracefully"""
    print("\n🛑 Received interrupt signal. Cleaning up...")
    sys.exit(0)

if __name__ == "__main__":
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Set the event loop policy for Windows compatibility
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Configure logging to reduce noise
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
        logging.getLogger('asyncio').setLevel(logging.WARNING)
        
        main()
        
    except KeyboardInterrupt:
        print("\n🛑 Scan interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
