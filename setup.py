#!/usr/bin/env python3
"""
Setup script for SubSort CLI tool
Enables global installation as 'subsort' command
"""

from setuptools import setup, find_packages
import pathlib

# Read the contents of README file
this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="subsort-cli",
    version="1.0.0",
    author="Karthik S Sathyan",
    author_email="karthik@subsort.dev",
    description="Enhanced CLI reconnaissance tool for subdomain analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/karthiksathyan/subsort",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "subsort=subsort.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="subdomain reconnaissance security pentest cybersecurity cli",
    project_urls={
        "Bug Reports": "https://github.com/karthiksathyan/subsort/issues",
        "Source": "https://github.com/karthiksathyan/subsort",
        "Documentation": "https://github.com/karthiksathyan/subsort/wiki",
    },
)