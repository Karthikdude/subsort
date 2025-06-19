# SubSort - Enhanced CLI Recon Tool

## Overview

SubSort is a high-performance Python-based CLI reconnaissance tool designed for comprehensive subdomain analysis. The application follows a modular architecture that enables extensible scanning capabilities with async processing, making it suitable for security researchers, penetration testers, and DevOps professionals conducting domain reconnaissance.

## System Architecture

### Core Architecture Pattern
- **Modular Design**: Plugin-based architecture allowing easy addition of new scanning modules
- **Async Processing**: Built on asyncio for high-performance concurrent operations
- **CLI-First Approach**: Command-line interface with rich terminal output using Click and Rich libraries
- **Layered Structure**: Clear separation between CLI, core engine, modules, and utilities

### Directory Structure
```
subsort/
├── cli.py              # CLI interface and argument parsing
├── core/               # Core scanning engine
│   ├── scanner.py      # Main scanning orchestrator
│   └── http_client.py  # Async HTTP client with anti-detection
├── modules/            # Scanning modules (pluggable)
│   ├── base.py         # Base module interface
│   ├── status.py       # HTTP status checking
│   ├── server.py       # Server information extraction
│   └── title.py        # Page title and content analysis
└── utils/              # Utility functions
    ├── helpers.py      # Common helper functions
    ├── logger.py       # Logging configuration
    └── output.py       # Result formatting and export
```

## Key Components

### 1. CLI Interface (`cli.py`)
- **Purpose**: Command-line argument parsing and user interaction
- **Framework**: Click for robust CLI handling
- **Features**: Rich banner display, parameter validation, help system
- **Design Decision**: Chosen Click over argparse for better extensibility and built-in validation

### 2. Core Scanner (`core/scanner.py`)
- **Purpose**: Main orchestration engine for subdomain scanning
- **Features**: Module management, concurrent processing, progress tracking
- **Architecture**: Uses async/await pattern for high concurrency
- **Integration**: Coordinates between HTTP client and scanning modules

### 3. HTTP Client (`core/http_client.py`)
- **Purpose**: Async HTTP operations with anti-detection features
- **Technology**: aiohttp for async HTTP requests
- **Features**: User-agent rotation, connection pooling, SSL handling
- **Anti-Detection**: Multiple user agents, request timing variation

### 4. Module System (`modules/`)
- **Pattern**: Plugin architecture with base class inheritance
- **Modules Available**:
  - Status Module: HTTP status code checking
  - Server Module: Server technology identification
  - Title Module: Page title and metadata extraction
- **Extensibility**: New modules can be added by extending BaseModule

### 5. Utilities (`utils/`)
- **Logger**: Structured logging with different verbosity levels
- **Output Manager**: Multiple output formats (JSON, CSV, TXT)
- **Helpers**: Common validation and parsing functions

## Data Flow

1. **Input Processing**: CLI reads subdomains from file or command line
2. **Module Initialization**: Selected scanning modules are instantiated
3. **Concurrent Scanning**: Async scanner processes multiple subdomains simultaneously
4. **Data Collection**: Each module extracts specific information (status, server, title)
5. **Result Aggregation**: Scanner collects and combines results from all modules
6. **Output Generation**: Results formatted and saved in specified format

## External Dependencies

### Core Libraries
- **aiohttp**: Async HTTP client for network requests
- **click**: CLI framework for command-line interface
- **rich**: Terminal formatting and progress displays
- **beautifulsoup4**: HTML parsing for content extraction
- **lxml**: Fast XML/HTML parsing backend

### Optional Enhancements (from specification)
- **aiodns**: Async DNS resolution for subdomain validation
- **redis/diskcache**: Caching layers for performance optimization
- **pandas/numpy**: Data analysis and manipulation
- **cryptography**: SSL/TLS certificate analysis

## Deployment Strategy

### Environment Setup
- **Python Version**: 3.11+ (configured in .replit)
- **Package Management**: pip with automatic dependency installation
- **Platform**: Cross-platform compatibility (Windows, macOS, Linux)

### Installation Process
1. Dependencies auto-installed via pip on first run
2. Entry point through main.py wrapper
3. Platform-specific event loop handling for Windows compatibility

### Execution Model
- **Single Binary**: Self-contained Python application
- **CLI Tool**: Direct command-line execution
- **Async Runtime**: Event loop management for concurrent operations

## Recent Changes

- June 19, 2025: Complete implementation of SubSort CLI tool with all core modules
  - Implemented modular architecture with Status, Server, and Title modules
  - Added async HTTP client with anti-detection features
  - Created comprehensive CLI interface with Click framework
  - Added support for multiple output formats (TXT, JSON, CSV)
  - Implemented rich terminal output with progress bars
  - Added proper error handling and logging system
  - Successfully tested with real-world subdomains
  - Created comprehensive documentation and examples

## Changelog

- June 19, 2025: Initial setup and complete implementation

## User Preferences

Preferred communication style: Simple, everyday language.