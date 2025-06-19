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
from .ui import print_enhanced_banner, create_enhanced_progress, create_results_table, print_scan_summary, print_help_enhancement

console = Console()

def print_banner():
    """Print the SubSort banner"""
    banner = r"""
 ____        _     ____             _   
/ ___| _   _| |__ / ___|  ___  _ __| |_ 
\___ \| | | | '_ \\___ \ / _ \| '__| __|
 ___) | |_| | |_) |___) | (_) | |  | |_ 
|____/ \__,_|_.__/|____/ \___/|_|   \__|
"""
    print("Enhanced CLI Recon Tool v1.0.0")
    print("Developed by Karthik S Sathyan")
    """
    console.print(Panel(Text(banner, style="cyan bold"), border_style="blue"))

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-i', '--input', 'input_file', 
              help='📁 Input file containing subdomains (one per line)')
@click.option('-o', '--output', 'output_file',
              help='💾 Output file to save results')
@click.option('--status', is_flag=True, default=False,
              help='🔍 Check HTTP status codes and connectivity')
@click.option('--server', is_flag=True, default=False,
              help='🖥️ Extract server information and security headers')
@click.option('--title', is_flag=True, default=False,
              help='📝 Extract page titles and content analysis')
@click.option('--techstack', is_flag=True, default=False,
              help='🔧 Detect and sort subdomains based on their tech stack')
@click.option('--vhost', is_flag=True, default=False,
              help='🌐 Perform virtual host-based detection and save accordingly')
@click.option('--responsetime', is_flag=True, default=False,
              help='⏱️ Measure response times and sort subdomains based on latency')
@click.option('--faviconhash', is_flag=True, default=False,
              help='🎭 Generate favicon hashes to identify technologies or services')
@click.option('--robots', is_flag=True, default=False,
              help='🤖 Fetch and parse robots.txt and sitemap.xml for hidden endpoints')
@click.option('--js', is_flag=True, default=False,
              help='📜 Extract and download linked JavaScript files for analysis')
@click.option('--auth', is_flag=True, default=False,
              help='🔐 Detect presence of login portals or authentication-requiring endpoints')
@click.option('--jsvuln', is_flag=True, default=False,
              help='⚠️ Identify outdated/vulnerable JavaScript libraries and their versions')
@click.option('--loginpanels', is_flag=True, default=False,
              help='🚪 Detect and list login portals and auth forms across all subdomains')
@click.option('--jwt', is_flag=True, default=False,
              help='🔑 Extract and decode JWT tokens from headers or responses')
@click.option('--cname', is_flag=True, default=False,
              help='📋 Check CNAME records for possible subdomain takeover')
@click.option('--iphistory', is_flag=True, default=False,
              help='📊 Check historical IP records to track infrastructure changes')
@click.option('--httpmethods', is_flag=True, default=False,
              help='🔧 Discover supported HTTP methods like OPTIONS, PUT, DELETE')
@click.option('--port', is_flag=True, default=False,
              help='🔌 Perform port scanning and group based on open ports')
@click.option('--ssl', is_flag=True, default=False,
              help='🔒 Collect SSL certificate details (expiry, CN, issuer)')
@click.option('--headers', is_flag=True, default=False,
              help='📋 Analyze and store security-related headers like CSP, HSTS')
@click.option('--content', is_flag=True, default=False,
              help='📄 Sort based on Content-Type (text/html, application/json, etc.)')
@click.option('--cors', is_flag=True, default=False,
              help='🌍 Detect CORS configuration issues or wildcards')
@click.option('--cdn', is_flag=True, default=False,
              help='☁️ Identify and group based on CDN or hosting provider')
@click.option('--length', is_flag=True, default=False,
              help='📏 Sort subdomains based on Content-Length or response similarity')
@click.option('--geoip', is_flag=True, default=False,
              help='🌎 Sort based on country, ASN, or IP origin')
@click.option('--cms', is_flag=True, default=False,
              help='💻 Detect CMS (e.g., WordPress, Joomla) and organize results')
@click.option('--waf', is_flag=True, default=False,
              help='🛡️ Detect WAF and categorize accordingly (e.g., Cloudflare, Akamai)')
@click.option('--cloudassets', is_flag=True, default=False,
              help='☁️ Discover exposed S3 buckets, Azure blobs, or Google Cloud storage')
@click.option('--dirscan', is_flag=True, default=False,
              help='📁 Discover common endpoints/directories (/admin, /api, etc.)')
@click.option('--wappalyzer', is_flag=True, default=False,
              help='🔍 Use Wappalyzer to identify frontend/backend technologies')
@click.option('--vulnscan', is_flag=True, default=False,
              help='🚨 Run vulnerability fingerprints using custom signatures')
@click.option('--threads', default=50, type=int,
              help='⚡ Number of concurrent threads (default: 50, max: 200)')
@click.option('--timeout', default=5, type=int,
              help='⏱️ Request timeout in seconds (default: 5)')
@click.option('--retries', default=3, type=int,
              help='🔄 Number of retry attempts per request (default: 3)')
@click.option('--delay', default=0, type=float,
              help='⏳ Delay between requests in seconds (default: 0)')
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='📊 Enable detailed verbose logging')
@click.option('--log-file', 
              help='📋 Custom log file path for detailed logs')
@click.option('--output-format', 
              type=click.Choice(['txt', 'json', 'csv'], case_sensitive=False),
              default='txt',
              help='📄 Output format: txt, json, or csv (default: txt)')
@click.option('--no-color', is_flag=True, default=False,
              help='🎨 Disable colored terminal output')
@click.option('--progress-bar', is_flag=True, default=True,
              help='📈 Show enhanced progress bar (default: enabled)')
@click.option('--silent', is_flag=True, default=False,
              help='🔇 Suppress banner and non-essential output')
@click.option('--user-agent',
              default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
              help='🕵️ Custom User-Agent string for requests')
@click.option('--follow-redirects', is_flag=True, default=True,
              help='🔄 Follow HTTP redirects automatically (default: enabled)')
@click.option('--ignore-ssl', is_flag=True, default=False,
              help='🔓 Ignore SSL certificate verification errors')
@click.option('--individual', is_flag=True, default=False,
              help='📂 Save individual module results as separate txt files')
@click.option('-mc', '--match-code', type=int,
              help='🎯 Filter results by specific HTTP status code (e.g., 200, 404)')
@click.option('--plain-text', is_flag=True, default=False,
              help='📝 Display/save results in plain text format without styling (domain.com | 200)')
@click.option('--examples', is_flag=True, default=False,
              help='📚 Show usage examples and exit')
def main(input_file: Optional[str], output_file: Optional[str], status: bool,
         server: bool, title: bool, techstack: bool, vhost: bool, responsetime: bool,
         faviconhash: bool, robots: bool, js: bool, auth: bool, jsvuln: bool,
         loginpanels: bool, jwt: bool, cname: bool, iphistory: bool, httpmethods: bool,
         port: bool, ssl: bool, headers: bool, content: bool, cors: bool, cdn: bool,
         length: bool, geoip: bool, cms: bool, waf: bool, cloudassets: bool,
         dirscan: bool, wappalyzer: bool, vulnscan: bool, threads: int, timeout: int, 
         retries: int, delay: float, verbose: bool, log_file: Optional[str], 
         output_format: str, no_color: bool, progress_bar: bool, 
         silent: bool, user_agent: str, follow_redirects: bool, 
         ignore_ssl: bool, individual: bool, match_code: Optional[int], 
         plain_text: bool, examples: bool):
    """
    SubSort - Enhanced CLI Reconnaissance Tool for subdomain analysis
    
    A high-performance, async-powered subdomain analysis framework with
    professional-grade reconnaissance capabilities.
    
    \b
    🚀 QUICK START EXAMPLES:
    
    \b
    # Basic connectivity scan
    subsort -i subdomains.txt --status
    
    \b
    # Full reconnaissance scan
    subsort -i targets.txt --status --server --title -v
    
    \b
    # High-performance scanning
    subsort -i domains.txt --status --threads 100 --timeout 10
    
    \b
    # Professional JSON output
    subsort -i subs.txt --status --server --title -o results.json --output-format json
    
    \b
    # Silent operation for automation
    subsort -i domains.txt --status --silent
    
    \b
    # Save individual module results
    subsort -i domains.txt --status --server --individual
    
    \b
    # Filter by status code
    subsort -i domains.txt --status -mc 200
    
    \b
    # Plain text output (simple format)
    subsort -i domains.txt --status --plain-text
    
    \b
    📚 For more examples: subsort --examples
    """
    
    # Handle examples flag
    if examples:
        print_help_enhancement()
        return
    
    # Validate thread count
    if threads > 200:
        console.print("[red]Warning: Thread count limited to 200 for stability[/red]")
        threads = 200
    elif threads < 1:
        console.print("[red]Error: Thread count must be at least 1[/red]")
        sys.exit(1)
    
    # Show enhanced banner unless silent mode is enabled
    if not silent:
        print_enhanced_banner()
    
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
    enabled_modules = [status, server, title, techstack, vhost, responsetime, faviconhash, 
                      robots, js, auth, jsvuln, loginpanels, jwt, cname, iphistory, 
                      httpmethods, port, ssl, headers, content, cors, cdn, length, 
                      geoip, cms, waf, cloudassets, dirscan, wappalyzer, vulnscan]
    
    if not any(enabled_modules):
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
    output_manager = OutputManager(output_file, output_format, individual, match_code, plain_text)
    
    # Create and configure scanner
    scanner = SubdomainScanner(config, logger)
    
    # Add enabled modules
    if status:
        scanner.enable_module('status')
    if server:
        scanner.enable_module('server')
    if title:
        scanner.enable_module('title')
    if techstack:
        scanner.enable_module('techstack')
    if vhost:
        scanner.enable_module('vhost')
    if responsetime:
        scanner.enable_module('responsetime')
    if faviconhash:
        scanner.enable_module('faviconhash')
    if robots:
        scanner.enable_module('robots')
    if js:
        scanner.enable_module('js')
    if auth:
        scanner.enable_module('auth')
    if jsvuln:
        scanner.enable_module('jsvuln')
    if loginpanels:
        scanner.enable_module('loginpanels')
    if jwt:
        scanner.enable_module('jwt')
    if cname:
        scanner.enable_module('cname')
    if iphistory:
        scanner.enable_module('iphistory')
    if httpmethods:
        scanner.enable_module('httpmethods')
    if port:
        scanner.enable_module('port')
    if ssl:
        scanner.enable_module('ssl')
    if headers:
        scanner.enable_module('headers')
    if content:
        scanner.enable_module('content')
    if cors:
        scanner.enable_module('cors')
    if cdn:
        scanner.enable_module('cdn')
    if length:
        scanner.enable_module('length')
    if geoip:
        scanner.enable_module('geoip')
    if cms:
        scanner.enable_module('cms')
    if waf:
        scanner.enable_module('waf')
    if cloudassets:
        scanner.enable_module('cloudassets')
    if dirscan:
        scanner.enable_module('dirscan')
    if wappalyzer:
        scanner.enable_module('wappalyzer')
    if vulnscan:
        scanner.enable_module('vulnscan')
    
    # Run the scan
    try:
        if not silent:
            console.print(f"\n[green]Starting scan of {len(subdomains)} subdomains...[/green]")
            console.print(f"[blue]Modules: {', '.join(scanner.get_enabled_modules())}[/blue]")
            console.print(f"[blue]Threads: {threads}, Timeout: {timeout}s[/blue]\n")
        
        # Run async scan with enhanced progress tracking
        async def run_scan():
            async with scanner:
                if progress_bar and not silent:
                    progress = create_enhanced_progress()
                    with progress:
                        task = progress.add_task("🔍 Scanning subdomains...", total=len(subdomains))
                        results = await scanner.scan_subdomains(subdomains, show_progress=False)
                        progress.update(task, completed=len(subdomains))
                        return results
                else:
                    return await scanner.scan_subdomains(subdomains, show_progress=False)
        
        results = asyncio.run(run_scan())
        
        # Enhanced results display
        if not silent and not output_file:
            console.print("\n")
            results_table = create_results_table(results, scanner.get_enabled_modules())
            console.print(results_table)
            console.print("\n")
            print_scan_summary(results, scanner.get_enabled_modules())
        elif output_file:
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
