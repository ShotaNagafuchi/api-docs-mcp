#!/usr/bin/env python3
"""
Main module for the API documentation MCP server.
"""

import argparse
import asyncio
import logging

from mcp.server.fastmcp import FastMCP

from src.crawler.crawler import ApiDocCrawler
from src.mcp.resources import register_resources
from src.storage.repository import ApiRepository

logger = logging.getLogger(__name__)


async def main():
    """Main entry point for the API documentation MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='API documentation MCP server')
    parser.add_argument('--url', required=True, help='URL of the API documentation to crawl')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the MCP server on')
    parser.add_argument('--uds-perms', type=str, default='0o660', help='Unix Domain Socket permissions (default: 0o660)')
    args = parser.parse_args()
    
    # Initialize the repository
    repository = ApiRepository()
    
    # Initialize the crawler
    crawler = ApiDocCrawler(repository)
    
    # Crawl the API documentation
    logger.info(f"Crawling API documentation from {args.url}")
    await crawler.crawl(args.url)
    
    # Initialize the MCP server with secure Unix Domain Socket permissions
    mcp = FastMCP(
        port=args.port,
        uds_perms=int(args.uds_perms, 8)  # Convert octal string to int
    )
    
    # Register resources
    register_resources(mcp, repository)
    
    # Start the server
    logger.info(f"Starting MCP server on port {args.port}")
    await mcp.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
