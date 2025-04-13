"""
Repository for storing and retrieving API documentation data.
"""

import json
import os
from typing import Dict, List, Optional

from src.storage.models import ApiEndpoint, ApiPage, ApiSchema


class ApiRepository:
    """Repository for storing and retrieving API documentation data."""
    
    def __init__(self, storage_dir: str = "storage"):
        """
        Initialize the API repository.
        
        Args:
            storage_dir: Directory to store the data
        """
        self.storage_dir = storage_dir
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self) -> None:
        """Ensure the storage directory exists."""
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def save_site_info(self, site_info: Dict) -> None:
        """
        Save site information.
        
        Args:
            site_info: Dictionary containing site information
        """
        filepath = os.path.join(self.storage_dir, "site_info.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(site_info, f, ensure_ascii=False, indent=2)
    
    def get_site_info(self) -> Optional[Dict]:
        """
        Get site information.
        
        Returns:
            Dictionary containing site information if found, None otherwise
        """
        filepath = os.path.join(self.storage_dir, "site_info.json")
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_page(self, page: ApiPage) -> None:
        """
        Save an API documentation page.
        
        Args:
            page: The page to save
        """
        page_data = {
            'title': page.title,
            'url': page.url,
            'endpoints': [
                {
                    'path': endpoint.path,
                    'method': endpoint.method,
                    'description': endpoint.description,
                    'parameters': endpoint.parameters,
                    'responses': endpoint.responses,
                    'url': endpoint.url
                }
                for endpoint in page.endpoints
            ],
            'schemas': [
                {
                    'name': schema.name,
                    'description': schema.description,
                    'properties': schema.properties,
                    'url': schema.url
                }
                for schema in page.schemas
            ],
            'content': page.content
        }
        
        # Create a filename from the URL
        filename = self._url_to_filename(page.url)
        filepath = os.path.join(self.storage_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, ensure_ascii=False, indent=2)
    
    def get_page(self, url: str) -> Optional[ApiPage]:
        """
        Get an API documentation page by URL.
        
        Args:
            url: The URL of the page
            
        Returns:
            The page if found, None otherwise
        """
        filename = self._url_to_filename(url)
        filepath = os.path.join(self.storage_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            page_data = json.load(f)
        
        return ApiPage(
            title=page_data['title'],
            url=page_data['url'],
            endpoints=[
                ApiEndpoint(
                    path=endpoint['path'],
                    method=endpoint['method'],
                    description=endpoint['description'],
                    parameters=endpoint['parameters'],
                    responses=endpoint['responses'],
                    url=endpoint['url']
                )
                for endpoint in page_data['endpoints']
            ],
            schemas=[
                ApiSchema(
                    name=schema['name'],
                    description=schema['description'],
                    properties=schema['properties'],
                    url=schema['url']
                )
                for schema in page_data['schemas']
            ],
            content=page_data['content']
        )
    
    def list_pages(self) -> List[str]:
        """
        List all stored page URLs.
        
        Returns:
            List of page URLs
        """
        return [
            self._filename_to_url(filename)
            for filename in os.listdir(self.storage_dir)
            if filename.endswith('.json') and filename != 'site_info.json'
        ]
    
    def _url_to_filename(self, url: str) -> str:
        """Convert a URL to a filename."""
        # Remove protocol and special characters
        filename = url.replace('https://', '').replace('http://', '')
        filename = ''.join(c if c.isalnum() else '_' for c in filename)
        return f"{filename}.json"
    
    def _filename_to_url(self, filename: str) -> str:
        """Convert a filename to a URL."""
        # Remove .json extension and restore URL format
        url = filename[:-5]  # Remove .json
        url = url.replace('_', '/')
        return f"https://{url}" 