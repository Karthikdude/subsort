#!/usr/bin/env python3
"""
SubSort - Enhanced CLI Recon Tool
A high-performance Python-based CLI reconnaissance tool for subdomain analysis
Developed by Karthik S Sathyan
"""

import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from subsort.cli import main

if __name__ == "__main__":
    # Set the event loop policy for Windows compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    main()
