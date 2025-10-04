#!/usr/bin/env python3
"""
Setup script for Florida Corporation Data Processing System
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="florida-corp-processor",
    version="1.0.0",
    author="Vladimir Belony",
    author_email="your.email@example.com",
    description="A comprehensive data processing pipeline for Florida corporation records",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/florida-corp-processor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "extract-officers=extract_officers_full:main",
            "match-documents=document_number_matcher:main",
            "format-corps=fill_officer_address_data:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.xlsx", "*.csv"],
    },
    keywords="data-processing, corporation, florida, matching, fuzzy-search, excel",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/florida-corp-processor/issues",
        "Source": "https://github.com/yourusername/florida-corp-processor",
        "Documentation": "https://github.com/yourusername/florida-corp-processor/blob/main/README.md",
    },
)

