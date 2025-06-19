# SubSort - Enhanced CLI Reconnaissance Tool

A high-performance Python-based CLI reconnaissance tool for comprehensive subdomain analysis with async processing, professional UI, and modular architecture.

**Developed by Karthik S Sathyan**

## Features

- **High Performance**: Async processing with configurable threading (up to 200 concurrent threads)
- **Professional UI**: Modern terminal interface with enhanced styling and progress bars
- **Global CLI Access**: Install once, use anywhere as `subsort` command
- **Modular Architecture**: Extensible plugin system for different scan types
- **Multiple Output Formats**: Support for TXT, JSON, and CSV output with enhanced formatting
- **Anti-Detection**: User-agent rotation and request randomization
- **Comprehensive Analysis**: Status codes, server information, page titles, security headers, and more
- **Flexible Input**: Read from files or stdin
- **Enhanced Help System**: Rich help with examples and emojis

## Available Modules

- **Status Module** (`--status`): HTTP status codes and connectivity checking with visual indicators
- **Server Module** (`--server`): Server technology identification, security headers, and CDN detection
- **Title Module** (`--title`): Page title extraction, content analysis, and framework detection

## Global Installation

### Method 1: Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/karthiksathyan/subsort.git
cd subsort

# Run the installation script
chmod +x install.sh
./install.sh
```

### Method 2: Manual Installation

```bash
# Install from source
git clone https://github.com/karthiksathyan/subsort.git
cd subsort
pip install -e .

# Or install from PyPI (when published)
pip install subsort-cli
```

### Method 3: Development Setup

```bash
# For development
git clone https://github.com/karthiksathyan/subsort.git
cd subsort
pip install -e .
```

After installation, the tool is available globally as `subsort` command.

## Verification

```bash
# Verify installation
subsort --help

# Show examples
subsort --examples

# Quick test
echo "google.com" | subsort --status --silent
```

## Usage Examples

### Basic Usage

```bash
# Basic status check from file
subsort -i subdomains.txt --status

# Comprehensive scan with all modules
subsort -i subdomains.txt --status --server --title -v

# High performance scan
subsort -i subdomains.txt --status --threads 100 --timeout 10
```

### Output Formats

```bash
# JSON output with professional formatting
subsort -i subdomains.txt --status --server --title -o results.json --output-format json

# CSV output for data analysis
subsort -i subdomains.txt --status --server --title -o report.csv --output-format csv

# Silent mode for automation
subsort -i subdomains.txt --status --server --title --silent
```

### Advanced Options

```bash
# Verbose logging with custom user agent
subsort -i subdomains.txt --status --server --title -v --user-agent "CustomBot/1.0"

# Anti-detection with delays and SSL bypass
subsort -i subdomains.txt --status --delay 1 --ignore-ssl

# Pipeline input from other tools
echo -e "google.com\ngithub.com" | subsort --status --server

# High-performance batch processing
subsort -i large_list.txt --status --threads 150 --timeout 3 --output-format json
```

## Enhanced Command Line Interface

The new SubSort CLI features a modern, professional interface with enhanced help system:

```bash
# Enhanced help with emojis and detailed descriptions
subsort --help        # or -h for short

# Interactive examples
subsort --examples     # Show comprehensive usage examples
```

### Core Options

| Option | Description | Default |
|--------|-------------|---------|
| `-i, --input` | 📁 Input file containing subdomains (one per line) | - |
| `-o, --output` | 💾 Output file to save results | stdout |
| `--status` | 🔍 Check HTTP status codes and connectivity | disabled |
| `--server` | 🖥️ Extract server information and security headers | disabled |
| `--title` | 📝 Extract page titles and content analysis | disabled |

### Performance Options

| Option | Description | Default |
|--------|-------------|---------|
| `--threads` | ⚡ Number of concurrent threads (max: 200) | 50 |
| `--timeout` | ⏱️ Request timeout in seconds | 5 |
| `--retries` | 🔄 Number of retry attempts per request | 3 |
| `--delay` | ⏳ Delay between requests in seconds | 0 |

### Output & Logging

| Option | Description | Default |
|--------|-------------|---------|
| `-v, --verbose` | 📊 Enable detailed verbose logging | disabled |
| `--log-file` | 📋 Custom log file path for detailed logs | auto-generated |
| `--output-format` | 📄 Output format: txt, json, or csv | txt |
| `--silent` | 🔇 Suppress banner and non-essential output | disabled |
| `--no-color` | 🎨 Disable colored terminal output | disabled |

### Advanced Options

| Option | Description | Default |
|--------|-------------|---------|
| `--user-agent` | 🕵️ Custom User-Agent string for requests | Mozilla/5.0... |
| `--follow-redirects` | 🔄 Follow HTTP redirects automatically | enabled |
| `--ignore-ssl` | 🔓 Ignore SSL certificate verification errors | disabled |

## Professional Output Display

### Enhanced Terminal Interface

SubSort now features a modern, professional terminal interface with:

- **Gradient ASCII Banner**: Eye-catching rainbow-colored SubSort logo
- **Rich Progress Bars**: Real-time scanning progress with spinners
- **Professional Tables**: Clean, formatted results with status indicators
- **Security Analysis**: Visual security header assessment
- **Performance Metrics**: Response time and success rate statistics

### Sample Console Output
```
╭─────────────────────  SubSort Reconnaissance Framework  ─────────────────────╮
│                                                                              │
│  ███████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗ ████████╗                 │
│  ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝                 │
│  ███████╗██║   ██║██████╔╝███████╗██║   ██║██████╔╝   ██║                    │
│  ╚════██║██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗   ██║                    │
│  ███████║╚██████╔╝██████╔╝███████║╚██████╔╝██║  ██║   ██║                    │
│  ╚══════╝ ╚═════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝                    │
│                                                                              │
│  🚀 Enhanced CLI Reconnaissance Tool • v1.0.0 • by Karthik S Sathyan         │
│                                                                              │
╰─────────────── Professional Subdomain Intelligence Gathering ────────────────╯

  🔍 Scanning subdomains... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:02

┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ 🌐 Subdomain             ┃ 📊 Status ┃ 🖥️ Server       ┃ 🛡️ Security ┃ ⚡ Response ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ ✅ google.com            │   200   │ gws            │ 🔒 Medium │ ⚡ Fast   │
│ ✅ github.com            │   200   │ github.com     │ 🛡️ High   │ ⚡ Fast   │
│ ✅ stackoverflow.com     │   200   │ ☁️ cloudflare   │ 🔒 Medium │ ⚡ Fast   │
└──────────────────────────┴─────────┴────────────────┴──────────┴───────────┘

╭───────────────────────────────  Scan Results  ───────────────────────────────╮
│  📊 Scan Summary                                                             │
│  🎯 Total Subdomains: 3                                                      │
│  ✅ Accessible: 3                                                            │
│  📈 Success Rate: 100.0%                                                     │
│  🛡️ High Security: 1 domains                                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
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

## Global Installation Guide

### Quick Install

```bash
# Download and install in one command
curl -sSL https://raw.githubusercontent.com/karthiksathyan/subsort/main/install.sh | bash
```

### Manual Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/karthiksathyan/subsort.git
   cd subsort
   ```

2. **Install globally using pip**
   ```bash
   pip install -e .
   ```

3. **Verify installation**
   ```bash
   subsort --version
   subsort --help
   ```

### Development Installation

For developers who want to contribute:

```bash
# Clone and install in development mode
git clone https://github.com/karthiksathyan/subsort.git
cd subsort
pip install -e .

# Install development dependencies
pip install pytest black flake8
```

### Uninstallation

```bash
pip uninstall subsort-cli
```

## Requirements

- Python 3.8 or higher
- pip package manager
- Internet connection for reconnaissance tasks

## Features Overview

### Core Capabilities
- **Multi-threaded scanning** up to 200 concurrent connections
- **Intelligent rate limiting** and retry mechanisms
- **Anti-detection features** with user-agent rotation
- **Professional UI** with rich terminal formatting
- **Comprehensive logging** with multiple verbosity levels

### Analysis Modules
- **Status Analysis**: HTTP response codes, redirects, SSL detection
- **Server Intelligence**: Technology stack, security headers, CDN detection
- **Content Analysis**: Title extraction, framework detection, security indicators

### Output Formats
- **Terminal Display**: Rich tables with color coding and icons
- **JSON Export**: Machine-readable structured data
- **CSV Export**: Spreadsheet-compatible format for analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

This project is developed by Karthik S Sathyan for educational and professional reconnaissance purposes.