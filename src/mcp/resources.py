"""
MCP resources for API documentation.
"""

from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from src.storage.repository import ApiRepository


def register_resources(mcp: FastMCP, repository: ApiRepository) -> None:
    """
    Register MCP resources for API documentation.
    
    Args:
        mcp: The MCP server instance
        repository: The API repository instance
    """
    @mcp.resource("api-docs/{query}")
    async def api_docs(query: str) -> Dict:
        """
        Search API documentation.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary containing search results
        """
        # List all pages
        pages = repository.list_pages()
        
        # Search for matching endpoints
        results = []
        for page_url in pages:
            page = repository.get_page(page_url)
            if not page:
                continue
            
            for endpoint in page.endpoints:
                if query.lower() in endpoint.path.lower() or query.lower() in endpoint.description.lower():
                    results.append({
                        'url': endpoint.url,
                        'path': endpoint.path,
                        'method': endpoint.method,
                        'description': endpoint.description
                    })
        
        return {
            'results': results,
            'total': len(results)
        }
    
    @mcp.resource("api-endpoint/{url}")
    async def api_endpoint(url: str) -> Optional[Dict]:
        """
        Get detailed information about an API endpoint.
        
        Args:
            url: The URL of the endpoint
            
        Returns:
            Dictionary containing endpoint details
        """
        # Find the page containing the endpoint
        for page_url in repository.list_pages():
            page = repository.get_page(page_url)
            if not page:
                continue
            
            for endpoint in page.endpoints:
                if endpoint.url == url:
                    return {
                        'url': endpoint.url,
                        'path': endpoint.path,
                        'method': endpoint.method,
                        'description': endpoint.description,
                        'parameters': endpoint.parameters,
                        'responses': endpoint.responses
                    }
        
        return None
    
    @mcp.resource("api-schema/{url}")
    async def api_schema(url: str) -> Optional[Dict]:
        """
        Get detailed information about a data schema.
        
        Args:
            url: The URL of the schema
            
        Returns:
            Dictionary containing schema details
        """
        # Find the page containing the schema
        for page_url in repository.list_pages():
            page = repository.get_page(page_url)
            if not page:
                continue
            
            for schema in page.schemas:
                if schema.url == url:
                    return {
                        'url': schema.url,
                        'name': schema.name,
                        'description': schema.description,
                        'properties': schema.properties
                    }
        
        return None 