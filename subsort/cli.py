"""
CLI interface for SubSort
Handles command-line argument parsing and main application flow
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .core.scanner import SubdomainScanner
from .utils.logger import setup_logger
from .utils.output import OutputManager
from .utils.helpers import validate_file, read_subdomains_from_file

console = Console()

def print_banner():
    """Print the SubSort banner"""
    banner = """
 ____        _     ____             _   
/ ___| _   _| |__ / ___|  ___  _ __| |_ 
\___ \| | | | '_ \\___ \ / _ \| '__| __|
 ___) | |_| | |_) |___) | (_) | |  | |_ 
|____/ \__,_|_.__/|____/ \___/|_|   \__|
                                        
Enhanced CLI Recon Tool v1.0.0
Developed by Karthik S Sathyan
    """
    console.print(Panel(Text(banner, style="cyan bold"), border_style="blue"))

@click.command()
@click.option('-i', '--input', 'input_file', 
              help='Input file containing subdomains (one per line)')
@click.option('-o', '--output', 'output_file',
              help='Output file to save results')
@click.option('--status', is_flag=True, default=False,
              help='Check HTTP status codes')
@click.option('--server', is_flag=True, default=False,
              help='Extract server information from headers')
@click.option('--title', is_flag=True, default=False,
              help='Extract page titles')
@click.option('--threads', default=50, type=int,
              help='Number of concurrent threads (default: 50, max: 200)')
@click.option('--timeout', default=5, type=int,
              help='Request timeout in seconds (default: 5)')
@click.option('--retries', default=3, type=int,
              help='Number of retry attempts (default: 3)')
@click.option('--delay', default=0, type=float,
              help='Delay between requests in seconds (default: 0)')
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='Enable verbose logging')
@click.option('--log-file', 
              help='Custom log file path')
@click.option('--output-format', 
              type=click.Choice(['txt', 'json', 'csv'], case_sensitive=False),
              default='txt',
              help='Output format (default: txt)')
@click.option('--no-color', is_flag=True, default=False,
              help='Disable colored output')
@click.option('--progress-bar', is_flag=True, default=True,
              help='Show progress bar (default: enabled)')
@click.option('--silent', is_flag=True, default=False,
              help='Suppress banner and non-essential output')
@click.option('--user-agent',
              default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
              help='Custom User-Agent string')
@click.option('--follow-redirects', is_flag=True, default=True,
              help='Follow HTTP redirects (default: enabled)')
@click.option('--ignore-ssl', is_flag=True, default=False,
              help='Ignore SSL certificate errors')
def main(input_file: Optional[str], output_file: Optional[str], status: bool,
         server: bool, title: bool, threads: int, timeout: int, retries: int,
         delay: float, verbose: bool, log_file: Optional[str], 
         output_format: str, no_color: bool, progress_bar: bool, 
         silent: bool, user_agent: str, follow_redirects: bool, 
         ignore_ssl: bool):
    """
    SubSort - Enhanced CLI Recon Tool for subdomain analysis
    
    Examples:
    
    \b
    # Basic status check from file
    subsort -i subdomains.txt --status
    
    \b
    # Comprehensive scan with all modules
    subsort -i subs.txt --status --server --title -v
    
    \b
    # High performance scan with custom settings
    subsort -i targets.txt --status --threads 100 --timeout 10
    """
    
    # Validate thread count
    if threads > 200:
        console.print("[red]Warning: Thread count limited to 200 for stability[/red]")
        threads = 200
    elif threads < 1:
        console.print("[red]Error: Thread count must be at least 1[/red]")
        sys.exit(1)
    
    # Show banner unless silent mode is enabled
    if not silent:
        print_banner()
    
    # Setup logging
    logger = setup_logger(verbose, log_file)
    
    # Disable color if requested
    if no_color:
        console._color_system = None
    
    # Get subdomains from input
    subdomains: List[str] = []
    
    if input_file:
        # Read from file
        if not validate_file(input_file):
            console.print(f"[red]Error: Cannot access input file: {input_file}[/red]")
            sys.exit(1)
        
        try:
            subdomains = read_subdomains_from_file(input_file)
            if not subdomains:
                console.print(f"[red]Error: No valid subdomains found in {input_file}[/red]")
                sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error reading input file: {e}[/red]")
            sys.exit(1)
    else:
        # Read from stdin
        if not silent:
            console.print("[yellow]Reading subdomains from stdin (Ctrl+D to finish)...[/yellow]")
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if line and not line.startswith('#'):
                    subdomains.append(line)
        except KeyboardInterrupt:
            console.print("\n[yellow]Input interrupted by user[/yellow]")
            sys.exit(0)
        
        if not subdomains:
            console.print("[red]Error: No subdomains provided[/red]")
            sys.exit(1)
    
    # Ensure at least one module is enabled
    if not any([status, server, title]):
        if not silent:
            console.print("[yellow]No modules specified, enabling status check by default[/yellow]")
        status = True
    
    # Create scanner configuration
    config = {
        'threads': threads,
        'timeout': timeout,
        'retries': retries,
        'delay': delay,
        'user_agent': user_agent,
        'follow_redirects': follow_redirects,
        'ignore_ssl': ignore_ssl,
        'verbose': verbose
    }
    
    # Initialize output manager
    output_manager = OutputManager(output_file, output_format)
    
    # Create and configure scanner
    scanner = SubdomainScanner(config, logger)
    
    # Add enabled modules
    if status:
        scanner.enable_module('status')
    if server:
        scanner.enable_module('server')
    if title:
        scanner.enable_module('title')
    
    # Run the scan
    try:
        if not silent:
            console.print(f"\n[green]Starting scan of {len(subdomains)} subdomains...[/green]")
            console.print(f"[blue]Modules: {', '.join(scanner.get_enabled_modules())}[/blue]")
            console.print(f"[blue]Threads: {threads}, Timeout: {timeout}s[/blue]\n")
        
        # Run async scan with proper cleanup
        async def run_scan():
            async with scanner:
                return await scanner.scan_subdomains(subdomains, show_progress=progress_bar)
        
        results = asyncio.run(run_scan())
        
        # Process and save results
        output_manager.save_results(results, scanner.get_enabled_modules())
        
        if not silent:
            console.print(f"\n[green]Scan completed successfully![/green]")
            console.print(f"[blue]Total subdomains: {len(subdomains)}[/blue]")
            console.print(f"[blue]Successful responses: {len([r for r in results if r.get('status_code')])}/{len(subdomains)}[/blue]")
            
            if output_file:
                console.print(f"[blue]Results saved to: {output_file}[/blue]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Scan interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Scan failed: {e}[/red]")
        logger.error(f"Scan failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
