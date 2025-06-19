#!/bin/bash
# SubSort CLI Tool - Global Installation Script
# This script installs SubSort globally as 'subsort' command

set -e

echo "🚀 SubSort CLI Tool - Global Installation"
echo "========================================="
echo

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    echo "   Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ Error: Python 3.8+ required. Found Python $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"
echo

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is required but not installed."
    echo "   Please install pip3 and try again."
    exit 1
fi

echo "📦 Installing SubSort CLI tool..."
echo

# Install in development mode for local development
if [ -f "setup.py" ]; then
    echo "🔧 Installing from source (development mode)..."
    pip3 install -e .
else
    echo "🔧 Installing from PyPI..."
    pip3 install subsort-cli
fi

echo
echo "✅ Installation completed successfully!"
echo
echo "🎯 SubSort is now available globally as 'subsort' command"
echo
echo "📚 Quick start:"
echo "   subsort --help          # Show help"
echo "   subsort --examples      # Show usage examples"
echo "   subsort -i domains.txt --status  # Basic scan"
echo
echo "🔍 For more information, visit:"
echo "   https://github.com/karthiksathyan/subsort"
echo