#!/usr/bin/env python3
"""
Main entry point for the API Documentation MCP Server.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from src.crawler.crawler import ApiDocCrawler
from src.mcp.resources import register_resources
from src.mcp.tools import register_tools
from src.mcp.prompts import register_prompts
from src.storage.repository import ApiRepository

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


async def setup_server(args):
    """Initialize and set up the MCP server with all components."""
    # Create data directory if it doesn't exist
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize the repository
    repository = ApiRepository(data_dir)
    
    # Initialize the crawler with the repository
    crawler = ApiDocCrawler(repository)
    
    # If a URL is provided, crawl it first
    if args.url:
        logger.info(f"Starting initial crawl of {args.url}")
        await crawler.crawl(args.url)
    
    # Initialize the MCP server
    mcp_server = FastMCP("api-docs")
    
    # Register MCP components
    register_resources(mcp_server, repository)
    register_tools(mcp_server, repository, crawler)
    register_prompts(mcp_server, repository)
    
    return mcp_server


def main():
    """Parse arguments and start the MCP server."""
    parser = argparse.ArgumentParser(description="API Documentation MCP Server")
    parser.add_argument(
        "--url", 
        type=str, 
        help="URL of the API documentation to crawl"
    )
    parser.add_argument(
        "--data-dir", 
        type=str, 
        default="./data", 
        help="Directory to store crawled data"
    )
    parser.add_argument(
        "--transport", 
        type=str, 
        choices=["stdio", "http"], 
        default="stdio",
        help="Transport method for the MCP server"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port for HTTP transport (if selected)"
    )
    
    args = parser.parse_args()
    
    # Set up the server asynchronously
    loop = asyncio.new_event_loop()
    mcp_server = loop.run_until_complete(setup_server(args))
    
    # Run the server with the specified transport
    if args.transport == "stdio":
        mcp_server.run(transport="stdio")
    else:
        mcp_server.run(transport="http", port=args.port)


if __name__ == "__main__":
    main()
