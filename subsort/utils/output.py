"""
Output management utility for SubSort
Handles saving results in different formats
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class OutputManager:
    """Manages output formatting and saving for scan results"""
    
    def __init__(self, output_file: Optional[str] = None, output_format: str = 'txt'):
        self.output_file = output_file
        self.output_format = output_format.lower()
        
    def save_results(self, results: List[Dict[str, Any]], enabled_modules: List[str]):
        """
        Save scan results to file and/or console
        
        Args:
            results: List of scan results
            enabled_modules: List of enabled module names
        """
        
        if self.output_file:
            # Save to file
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.output_format == 'json':
                self._save_json(results, output_path)
            elif self.output_format == 'csv':
                self._save_csv(results, output_path, enabled_modules)
            else:  # txt format
                self._save_txt(results, output_path, enabled_modules)
        else:
            # Print to console
            self._print_results(results, enabled_modules)
    
    def _save_json(self, results: List[Dict[str, Any]], output_path: Path):
        """Save results in JSON format"""
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'total_subdomains': len(results),
            'results': results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    def _save_csv(self, results: List[Dict[str, Any]], output_path: Path, enabled_modules: List[str]):
        """Save results in CSV format"""
        if not results:
            return
        
        # Determine all possible field names
        all_fields = set()
        for result in results:
            all_fields.update(result.keys())
        
        # Sort fields for consistent output
        sorted_fields = sorted(all_fields)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted_fields)
            writer.writeheader()
            
            for result in results:
                # Convert complex values to strings
                row = {}
                for field in sorted_fields:
                    value = result.get(field, '')
                    if isinstance(value, (list, dict)):
                        row[field] = json.dumps(value)
                    else:
                        row[field] = value
                writer.writerow(row)
    
    def _save_txt(self, results: List[Dict[str, Any]], output_path: Path, enabled_modules: List[str]):
        """Save results in text format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"SubSort Scan Results\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Subdomains: {len(results)}\n")
            f.write(f"Enabled Modules: {', '.join(enabled_modules)}\n")
            f.write("-" * 80 + "\n\n")
            
            for result in results:
                subdomain = result.get('subdomain', 'Unknown')
                f.write(f"Subdomain: {subdomain}\n")
                
                # Status information
                if 'status_code' in result:
                    status = result['status_code']
                    message = result.get('status_message', '')
                    url = result.get('url', '')
                    f.write(f"  Status: {status} {message} ({url})\n")
                
                # Server information
                if 'server' in result:
                    f.write(f"  Server: {result['server']}\n")
                
                # Title information
                if 'title' in result:
                    f.write(f"  Title: {result['title']}\n")
                
                # Additional information
                for key, value in result.items():
                    if key not in ['subdomain', 'status_code', 'status_message', 'url', 'server', 'title', 'timestamp']:
                        if isinstance(value, (list, dict)):
                            f.write(f"  {key.replace('_', ' ').title()}: {json.dumps(value)}\n")
                        else:
                            f.write(f"  {key.replace('_', ' ').title()}: {value}\n")
                
                f.write("\n")
    
    def _print_results(self, results: List[Dict[str, Any]], enabled_modules: List[str]):
        """Print results to console"""
        from rich.console import Console
        from rich.table import Table
        from rich.text import Text
        
        console = Console()
        
        # Create table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Subdomain", style="cyan", no_wrap=True)
        
        if 'status' in enabled_modules:
            table.add_column("Status", justify="center")
            table.add_column("URL", style="dim")
        
        if 'server' in enabled_modules:
            table.add_column("Server", style="green")
        
        if 'title' in enabled_modules:
            table.add_column("Title", style="yellow", max_width=40)
        
        # Add rows
        for result in results:
            row = [result.get('subdomain', 'Unknown')]
            
            if 'status' in enabled_modules:
                status_code = result.get('status_code')
                if status_code:
                    if 200 <= status_code < 300:
                        status_text = Text(str(status_code), style="green")
                    elif 300 <= status_code < 400:
                        status_text = Text(str(status_code), style="yellow")
                    else:
                        status_text = Text(str(status_code), style="red")
                else:
                    status_text = Text("N/A", style="dim")
                
                row.append(status_text)
                row.append(result.get('url', 'N/A'))
            
            if 'server' in enabled_modules:
                row.append(result.get('server', 'N/A'))
            
            if 'title' in enabled_modules:
                title = result.get('title', 'N/A')
                if len(title) > 37:
                    title = title[:37] + "..."
                row.append(title)
            
            table.add_row(*row)
        
        console.print(table)
        console.print(f"\n[blue]Total: {len(results)} subdomains processed[/blue]")
