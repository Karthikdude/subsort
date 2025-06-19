"""
Enhanced UI components for SubSort
Professional styling and display functions
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.layout import Layout
from rich.live import Live
from typing import List, Dict, Any

console = Console()

def print_enhanced_banner():
    """Print the professional SubSort banner"""
    
    # Modern ASCII art with gradient colors
    banner_lines = [
        ("███████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗ ████████╗", "bold bright_blue"),
        ("██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝", "bold bright_cyan"),
        ("███████╗██║   ██║██████╔╝███████╗██║   ██║██████╔╝   ██║   ", "bold bright_green"),
        ("╚════██║██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗   ██║   ", "bold bright_yellow"),
        ("███████║╚██████╔╝██████╔╝███████║╚██████╔╝██║  ██║   ██║   ", "bold bright_magenta"),
        ("╚══════╝ ╚═════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ", "bold bright_red")
    ]
    
    # Create banner text with colors
    banner_text = Text()
    for line, style in banner_lines:
        banner_text.append(line + "\n", style=style)
    
    # Add tool information
    banner_text.append("\n")
    banner_text.append("🚀 Enhanced CLI Reconnaissance Tool ", style="bold bright_white")
    banner_text.append("• ", style="dim white")
    banner_text.append("v1.0.0", style="bold green")
    banner_text.append(" • ", style="dim white")
    banner_text.append("by Karthik S Sathyan", style="italic bright_cyan")
    banner_text.append("\n\n")
    
    # Feature highlights with icons
    features = [
        ("🔍", "Advanced Subdomain Analysis", "bright_white"),
        ("⚡", "High-Performance Async Processing", "bright_yellow"),
        ("🛡️", "Anti-Detection Technology", "bright_red"),
        ("📊", "Multi-Format Output Support", "bright_green"),
        ("🌐", "Global CLI Access", "bright_blue"),
        ("🎯", "Professional Reconnaissance", "bright_magenta")
    ]
    
    for icon, text, color in features:
        banner_text.append(f"{icon} {text}  ", style=color)
    
    banner_text.append("\n")
    
    # Create panel with enhanced styling
    console.print(Panel(
        Align.center(banner_text),
        border_style="bright_blue",
        padding=(1, 2),
        title="[bold bright_white on blue] SubSort Reconnaissance Framework [/]",
        title_align="center",
        subtitle="[dim bright_cyan]Professional Subdomain Intelligence Gathering[/]",
        subtitle_align="center"
    ))

def create_enhanced_progress():
    """Create enhanced progress bar with professional styling"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold bright_white]{task.description}"),
        BarColumn(
            bar_width=40,
            complete_style="bright_green",
            finished_style="bold green"
        ),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False
    )

def create_results_table(results: List[Dict[str, Any]], enabled_modules: List[str]) -> Table:
    """Create enhanced results table with professional styling"""
    
    # Create table with modern styling
    table = Table(
        show_header=True,
        header_style="bold bright_white on blue",
        border_style="bright_blue",
        row_styles=["", "dim"]
    )
    
    # Add columns based on enabled modules
    table.add_column("🌐 Subdomain", style="bold bright_cyan", no_wrap=True, width=25)
    
    if 'status' in enabled_modules:
        table.add_column("📊 Status", justify="center", width=8)
        table.add_column("🔗 URL", style="dim", max_width=30)
    
    if 'server' in enabled_modules:
        table.add_column("🖥️ Server", style="bright_green", width=15)
        table.add_column("🛡️ Security", style="bright_yellow", width=10)
    
    if 'title' in enabled_modules:
        table.add_column("📝 Title", style="bright_white", max_width=40)
    
    # Add performance column
    table.add_column("⚡ Response", style="dim", width=10)
    
    # Add rows with enhanced styling
    for result in results:
        row = []
        
        # Subdomain with icon based on status
        subdomain = result.get('subdomain', 'Unknown')
        if result.get('accessible', False):
            row.append(f"✅ {subdomain}")
        else:
            row.append(f"❌ {subdomain}")
        
        if 'status' in enabled_modules:
            status_code = result.get('status_code')
            if status_code:
                if 200 <= status_code < 300:
                    status_text = Text(str(status_code), style="bold green")
                elif 300 <= status_code < 400:
                    status_text = Text(str(status_code), style="bold yellow")
                elif 400 <= status_code < 500:
                    status_text = Text(str(status_code), style="bold orange3")
                else:
                    status_text = Text(str(status_code), style="bold red")
            else:
                status_text = Text("N/A", style="dim red")
            
            row.append(status_text)
            
            # URL with truncation
            url = result.get('url', 'N/A')
            if len(url) > 30:
                url = url[:27] + "..."
            row.append(url)
        
        if 'server' in enabled_modules:
            server = result.get('server', 'Unknown')
            if server == 'Not disclosed':
                server = "🔒 Hidden"
            elif 'cloudflare' in server.lower():
                server = f"☁️ {server}"
            elif any(x in server.lower() for x in ['nginx', 'apache']):
                server = f"🗄️ {server}"
            row.append(server[:15])
            
            # Security indicators
            security_headers = result.get('security_headers', {})
            if security_headers:
                security_count = len(security_headers)
                if security_count >= 4:
                    row.append("🛡️ High")
                elif security_count >= 2:
                    row.append("🔒 Medium")
                else:
                    row.append("⚠️ Low")
            else:
                row.append("❌ None")
        
        if 'title' in enabled_modules:
            title = result.get('title', 'N/A')
            if title == 'No title found':
                title = "📄 No Title"
            elif title == 'Unable to retrieve content':
                title = "❌ No Content"
            else:
                title = f"📝 {title}"
            
            if len(title) > 40:
                title = title[:37] + "..."
            row.append(title)
        
        # Response time (simulated for now)
        if result.get('accessible', False):
            row.append("⚡ Fast")
        else:
            row.append("⏱️ Timeout")
        
        table.add_row(*row)
    
    return table

def print_scan_summary(results: List[Dict[str, Any]], enabled_modules: List[str]):
    """Print enhanced scan summary with statistics"""
    
    total = len(results)
    accessible = len([r for r in results if r.get('accessible', False)])
    success_rate = (accessible / total * 100) if total > 0 else 0
    
    # Create summary panel
    summary_text = Text()
    summary_text.append("📊 Scan Summary\n\n", style="bold bright_white")
    
    summary_text.append(f"🎯 Total Subdomains: ", style="bright_white")
    summary_text.append(f"{total}\n", style="bold bright_cyan")
    
    summary_text.append(f"✅ Accessible: ", style="bright_white")
    summary_text.append(f"{accessible}\n", style="bold green")
    
    summary_text.append(f"❌ Unreachable: ", style="bright_white")
    summary_text.append(f"{total - accessible}\n", style="bold red")
    
    summary_text.append(f"📈 Success Rate: ", style="bright_white")
    if success_rate >= 80:
        summary_text.append(f"{success_rate:.1f}%\n", style="bold green")
    elif success_rate >= 50:
        summary_text.append(f"{success_rate:.1f}%\n", style="bold yellow")
    else:
        summary_text.append(f"{success_rate:.1f}%\n", style="bold red")
    
    summary_text.append(f"🔧 Modules Used: ", style="bright_white")
    summary_text.append(f"{', '.join(enabled_modules)}\n", style="bold bright_cyan")
    
    # Security analysis
    if 'server' in enabled_modules:
        high_security = len([r for r in results if len(r.get('security_headers', {})) >= 4])
        summary_text.append(f"🛡️ High Security: ", style="bright_white")
        summary_text.append(f"{high_security} domains\n", style="bold green")
    
    console.print(Panel(
        summary_text,
        border_style="bright_green",
        padding=(1, 2),
        title="[bold bright_white on green] Scan Results [/]",
        title_align="center"
    ))

def print_help_enhancement():
    """Print enhanced help information"""
    help_text = Text()
    help_text.append("🚀 SubSort Quick Start Guide\n\n", style="bold bright_white")
    
    examples = [
        ("Basic scan", "subsort -i domains.txt --status"),
        ("Full analysis", "subsort -i domains.txt --status --server --title -v"),
        ("JSON output", "subsort -i domains.txt --status -o results.json --output-format json"),
        ("Silent mode", "subsort -i domains.txt --status --silent"),
        ("High performance", "subsort -i domains.txt --status --threads 100")
    ]
    
    for description, command in examples:
        help_text.append(f"📌 {description}:\n", style="bright_cyan")
        help_text.append(f"   {command}\n\n", style="dim white")
    
    console.print(Panel(
        help_text,
        border_style="bright_blue",
        padding=(1, 2),
        title="[bold bright_white on blue] Usage Examples [/]",
        title_align="center"
    ))