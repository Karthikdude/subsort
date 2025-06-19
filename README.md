# SubSort - Enhanced CLI Recon Tool

A high-performance Python-based CLI reconnaissance tool for comprehensive subdomain analysis with async processing and modular architecture.

**Developed by Karthik S Sathyan**

## Features

- **High Performance**: Async processing with configurable threading (up to 200 concurrent threads)
- **Modular Architecture**: Extensible plugin system for different scan types
- **Multiple Output Formats**: Support for TXT, JSON, and CSV output
- **Anti-Detection**: User-agent rotation and request randomization
- **Comprehensive Analysis**: Status codes, server information, page titles, and more
- **Flexible Input**: Read from files or stdin
- **Rich Terminal Output**: Beautiful progress bars and colored output

## Available Modules

- **Status Module** (`--status`): HTTP status codes and connectivity checking
- **Server Module** (`--server`): Server technology identification and security headers
- **Title Module** (`--title`): Page title extraction and content analysis

## Installation

The tool automatically installs required dependencies on first run:

```bash
# Install dependencies
pip install aiohttp click rich beautifulsoup4 lxml

# Run the tool
python main.py --help
```

## Usage Examples

### Basic Usage

```bash
# Basic status check from file
python main.py -i subdomains.txt --status

# Comprehensive scan with all modules
python main.py -i subdomains.txt --status --server --title -v

# High performance scan
python main.py -i subdomains.txt --status --threads 100 --timeout 10
```

### Output Formats

```bash
# JSON output
python main.py -i subdomains.txt --status --server --title -o results.json --output-format json

# CSV output
python main.py -i subdomains.txt --status --server --title -o report.csv --output-format csv

# Silent mode (no banner)
python main.py -i subdomains.txt --status --server --title --silent
```

### Advanced Options

```bash
# Custom user agent and verbose logging
python main.py -i subdomains.txt --status --server --title -v --user-agent "CustomBot/1.0"

# With delays and SSL bypass
python main.py -i subdomains.txt --status --delay 1 --ignore-ssl

# Read from stdin
echo -e "google.com\ngithub.com" | python main.py --status --server
```

## Command Line Options

```
-i, --input TEXT                Input file containing subdomains (one per line)
-o, --output TEXT               Output file to save results
--status                        Check HTTP status codes
--server                        Extract server information from headers
--title                         Extract page titles
--threads INTEGER               Number of concurrent threads (default: 50, max: 200)
--timeout INTEGER               Request timeout in seconds (default: 5)
--retries INTEGER               Number of retry attempts (default: 3)
--delay FLOAT                   Delay between requests in seconds (default: 0)
-v, --verbose                   Enable verbose logging
--log-file TEXT                 Custom log file path
--output-format [txt|json|csv]  Output format (default: txt)
--no-color                      Disable colored output
--progress-bar                  Show progress bar (default: enabled)
--silent                        Suppress banner and non-essential output
--user-agent TEXT               Custom User-Agent string
--follow-redirects              Follow HTTP redirects (default: enabled)
--ignore-ssl                    Ignore SSL certificate errors
```

## Sample Output

### Console Output
```
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Subdomain         ┃ Status ┃ URL            ┃ Server        ┃ Title          ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ google.com        │  200   │ https://googl… │ gws           │ Google         │
│ github.com        │  200   │ https://githu… │ github.com    │ GitHub Website │
│ stackoverflow.com │  200   │ https://stack… │ cloudflare    │ Stack Overflow │
└───────────────────┴────────┴────────────────┴───────────────┴────────────────┘
```

### JSON Output
```json
{
  "timestamp": "2025-06-19T07:08:15.006897",
  "total_subdomains": 3,
  "results": [
    {
      "subdomain": "google.com",
      "status_code": 200,
      "url": "https://google.com",
      "accessible": true,
      "status_category": "success",
      "status_message": "OK",
      "scheme": "https",
      "ssl_enabled": true,
      "server": "gws",
      "server_type": "unknown",
      "security_headers": {
        "strict_transport_security": "max-age=31536000",
        "x_frame_options": "SAMEORIGIN"
      },
      "title": "Google",
      "content_type": "text/html",
      "content_size": 178490,
      "frameworks": ["angular"]
    }
  ]
}
```

## Architecture

SubSort follows a modular architecture with:

- **CLI Interface**: Command-line argument parsing and user interaction
- **Core Scanner**: Async orchestration engine for subdomain scanning
- **HTTP Client**: Async HTTP operations with anti-detection features
- **Module System**: Plugin architecture for extensible scanning capabilities
- **Utilities**: Logging, output management, and helper functions

## Performance Features

- **Async Processing**: Built on asyncio for high concurrency
- **Connection Pooling**: Efficient HTTP connection reuse
- **Smart Batching**: Adaptive batch sizing based on performance
- **Anti-Detection**: User-agent rotation and request timing variation
- **Error Handling**: Robust retry logic with exponential backoff

## Logging

Verbose logging provides detailed information about:
- HTTP request/response details
- DNS resolution timing
- Module execution status
- Performance metrics
- Error tracking

Log files are automatically created in the `logs/` directory with timestamps.

## License

This project is developed by Karthik S Sathyan for educational and professional reconnaissance purposes.