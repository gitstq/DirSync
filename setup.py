#!/usr/bin/env python3
"""
DirSync - 轻量级智能目录对比与同步引擎
Lightweight Intelligent Directory Comparison & Synchronization Engine
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="dirsync-cli",
    version="1.0.0",
    author="DirSync Team",
    author_email="dirsync@example.com",
    description="轻量级智能目录对比与同步引擎 / Lightweight Intelligent Directory Comparison & Synchronization Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/DirSync",
    py_modules=["dirsync"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "dirsync=dirsync:main",
        ],
    },
    keywords="directory sync backup compare diff mirror synchronization",
    project_urls={
        "Bug Reports": "https://github.com/gitstq/DirSync/issues",
        "Source": "https://github.com/gitstq/DirSync",
    },
)
