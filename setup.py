"""
Setup script for the API documentation MCP server.
"""

from setuptools import setup, find_packages

setup(
    name="api-docs-mcp-server",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mcp-server>=0.1.0",
        "httpx>=0.24.0",
        "beautifulsoup4>=4.12.0",
        "aiohttp>=3.9.0",
        "lxml>=4.9.0",
    ],
    python_requires=">=3.8",
) 