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
    
    def __init__(self, output_file: Optional[str] = None, output_format: str = 'txt', 
                 individual: bool = False, match_code: Optional[int] = None, plain_text: bool = False):
        self.output_file = output_file
        self.output_format = output_format.lower()
        self.individual = individual
        self.match_code = match_code
        self.plain_text = plain_text
        
    def save_results(self, results: List[Dict[str, Any]], enabled_modules: List[str]):
        """
        Save scan results to file and/or console
        
        Args:
            results: List of scan results
            enabled_modules: List of enabled module names
        """
        
        # Filter results by status code if specified
        filtered_results = self._filter_by_status_code(results)
        
        if self.output_file:
            # Save to file
            output_path = Path(self.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.output_format == 'json':
                self._save_json(filtered_results, output_path)
            elif self.output_format == 'csv':
                self._save_csv(filtered_results, output_path, enabled_modules)
            else:  # txt format
                self._save_txt(filtered_results, output_path, enabled_modules)
                
                # Save individual module files only if requested
                if self.individual:
                    self._save_individual_module_files(filtered_results, output_path, enabled_modules)
        else:
            # Print to console
            if self.plain_text:
                self._print_plain_text(filtered_results, enabled_modules)
            else:
                self._print_results(filtered_results, enabled_modules)
    
    def _filter_by_status_code(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter results by status code if match_code is specified"""
        if self.match_code is None:
            return results
        
        filtered = []
        for result in results:
            status_code = result.get('status_code')
            if status_code == self.match_code:
                filtered.append(result)
        
        return filtered
    
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
            if self.plain_text:
                # Plain text format - simple line by line
                for result in results:
                    line_parts = []
                    subdomain = result.get('subdomain', 'Unknown')
                    line_parts.append(subdomain)
                    
                    # Add status if enabled
                    if 'status' in enabled_modules and 'status_code' in result:
                        line_parts.append(str(result['status_code']))
                    
                    # Add server if enabled
                    if 'server' in enabled_modules and 'server' in result:
                        line_parts.append(result['server'])
                    
                    # Add title if enabled
                    if 'title' in enabled_modules and 'title' in result:
                        title = result['title'].replace('\n', ' ').replace('\r', ' ')
                        if len(title) > 50:
                            title = title[:47] + "..."
                        line_parts.append(f'"{title}"')
                    
                    # Add other module data
                    for module in enabled_modules:
                        if module in ['status', 'server', 'title']:
                            continue
                        
                        # Add specific fields for each module
                        if module == 'techstack' and 'technologies' in result:
                            techs = result['technologies']
                            if isinstance(techs, list) and techs:
                                line_parts.append(f"techs:{','.join(techs[:3])}")
                        elif module == 'responsetime' and 'response_time' in result:
                            rt = result['response_time']
                            if rt:
                                line_parts.append(f"time:{rt:.0f}ms")
                        elif module == 'vhost' and 'is_vhost' in result:
                            line_parts.append(f"vhost:{result['is_vhost']}")
                    
                    f.write(" | ".join(line_parts) + "\n")
            else:
                # Regular formatted output
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
        if self.match_code:
            console.print(f"[yellow]Filtered by status code: {self.match_code}[/yellow]")
    
    def _print_plain_text(self, results: List[Dict[str, Any]], enabled_modules: List[str]):
        """Print results in plain text format"""
        for result in results:
            line_parts = []
            subdomain = result.get('subdomain', 'Unknown')
            line_parts.append(subdomain)
            
            # Add status if enabled
            if 'status' in enabled_modules and 'status_code' in result:
                line_parts.append(str(result['status_code']))
            
            # Add server if enabled
            if 'server' in enabled_modules and 'server' in result:
                line_parts.append(result['server'])
            
            # Add title if enabled
            if 'title' in enabled_modules and 'title' in result:
                title = result['title'].replace('\n', ' ').replace('\r', ' ')
                if len(title) > 50:
                    title = title[:47] + "..."
                line_parts.append(f'"{title}"')
            
            # Add other module data
            for module in enabled_modules:
                if module in ['status', 'server', 'title']:
                    continue
                
                # Add specific fields for each module
                if module == 'techstack' and 'technologies' in result:
                    techs = result['technologies']
                    if isinstance(techs, list) and techs:
                        line_parts.append(f"techs:{','.join(techs[:3])}")
                elif module == 'responsetime' and 'response_time' in result:
                    rt = result['response_time']
                    if rt:
                        line_parts.append(f"time:{rt:.0f}ms")
                elif module == 'vhost' and 'is_vhost' in result:
                    line_parts.append(f"vhost:{result['is_vhost']}")
                elif module == 'faviconhash' and 'favicon_hash' in result:
                    fh = result['favicon_hash']
                    if fh:
                        line_parts.append(f"favicon:{fh[:10]}...")
                elif module == 'robots' and 'robots_accessible' in result:
                    line_parts.append(f"robots:{result['robots_accessible']}")
                elif module == 'js' and 'js_files' in result:
                    js_files = result['js_files']
                    if isinstance(js_files, list) and js_files:
                        line_parts.append(f"js_files:{len(js_files)}")
                elif module == 'auth' and 'requires_auth' in result:
                    line_parts.append(f"auth:{result['requires_auth']}")
                elif module == 'jsvuln' and 'vulnerable_js' in result:
                    vuln_js = result['vulnerable_js']
                    if isinstance(vuln_js, list) and vuln_js:
                        line_parts.append(f"js_vulns:{len(vuln_js)}")
                elif module == 'loginpanels' and 'login_panels' in result:
                    panels = result['login_panels']
                    if isinstance(panels, list) and panels:
                        line_parts.append(f"login_panels:{len(panels)}")
                elif module == 'jwt' and 'jwt_tokens' in result:
                    tokens = result['jwt_tokens']
                    if isinstance(tokens, list) and tokens:
                        line_parts.append(f"jwt_tokens:{len(tokens)}")
                elif module == 'cname' and 'cname_records' in result:
                    records = result['cname_records']
                    if isinstance(records, list) and records:
                        line_parts.append(f"cname:{len(records)}")
            
            print(" | ".join(line_parts))
        
        # Simple summary for plain text
        total = len(results)
        accessible = len([r for r in results if r.get('accessible', False)])
        print(f"\nTotal: {total} | Accessible: {accessible}")
        if self.match_code:
            print(f"Filtered by status code: {self.match_code}")
    
    def _save_individual_module_files(self, results: List[Dict[str, Any]], output_path: Path, enabled_modules: List[str]):
        """Save individual result files for each module"""
        try:
            # Create a directory for module results
            module_dir = output_path.parent / f"{output_path.stem}_modules"
            module_dir.mkdir(exist_ok=True)
            
            # Define module field mappings
            module_fields = {
                'status': ['status_code', 'status_message', 'url', 'accessible'],
                'server': ['server', 'security_headers'],
                'title': ['title', 'content_length'],
                'techstack': ['technologies', 'web_server', 'programming_language', 'framework', 'cms', 'cdn', 'security', 'analytics', 'frontend'],
                'vhost': ['is_vhost', 'vhost_type', 'shared_ip', 'host_headers', 'vhost_indicators', 'alternative_hosts'],
                'responsetime': ['response_time', 'response_times', 'average_response_time', 'min_response_time', 'max_response_time', 'latency_category', 'connection_time', 'ttfb'],
                'faviconhash': ['favicon_hash', 'favicon_mmh3', 'favicon_md5', 'technology_match', 'favicon_url', 'favicon_size', 'favicon_accessible'],
                'robots': ['robots_accessible', 'robots_content', 'disallowed_paths', 'allowed_paths', 'crawl_delay', 'sitemap_urls', 'sitemaps_found', 'interesting_paths', 'user_agents'],
                'js': ['js_files', 'js_technologies', 'js_frameworks', 'js_libraries', 'external_js', 'inline_js', 'js_errors'],
                'auth': ['requires_auth', 'auth_type', 'auth_headers', 'login_form', 'auth_endpoints'],
                'jsvuln': ['vulnerable_js', 'js_versions', 'vulnerability_details', 'severity_levels', 'cve_references'],
                'loginpanels': ['login_panels', 'form_fields', 'auth_methods', 'login_endpoints', 'panel_types'],
                'jwt': ['jwt_tokens', 'jwt_headers', 'jwt_payloads', 'jwt_algorithms', 'jwt_expiry'],
                'cname': ['cname_records', 'takeover_possible', 'provider_info', 'dns_status', 'vulnerability_risk']
            }
            
            for module in enabled_modules:
                if module in module_fields:
                    module_file = module_dir / f"{module}_results.txt"
                    
                    with open(module_file, 'w', encoding='utf-8') as f:
                        f.write(f"SubSort {module.title()} Module Results\n")
                        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Total Subdomains: {len(results)}\n")
                        if self.match_code:
                            f.write(f"Filtered by Status Code: {self.match_code}\n")
                        f.write("-" * 60 + "\n\n")
                        
                        for result in results:
                            subdomain = result.get('subdomain', 'Unknown')
                            f.write(f"Subdomain: {subdomain}\n")
                            
                            # Write module-specific fields
                            found_data = False
                            for field in module_fields[module]:
                                if field in result and result[field] is not None:
                                    found_data = True
                                    value = result[field]
                                    if isinstance(value, (list, dict)):
                                        f.write(f"  {field.replace('_', ' ').title()}: {json.dumps(value, indent=2)}\n")
                                    else:
                                        f.write(f"  {field.replace('_', ' ').title()}: {value}\n")
                            
                            if not found_data:
                                f.write(f"  No {module} data available\n")
                            
                            f.write("\n")
                    
                    print(f"Saved {module} results to: {module_file}")
                    
        except Exception as e:
            print(f"Error saving individual module files: {e}")
