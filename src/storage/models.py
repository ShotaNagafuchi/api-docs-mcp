"""
Data models for storing API documentation information.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class ApiEndpoint:
    """Represents an API endpoint."""
    path: str
    method: str
    description: str
    parameters: List[Dict]
    responses: List[Dict]
    url: str


@dataclass
class ApiSchema:
    """Represents a data schema."""
    name: str
    description: str
    properties: List[Dict]
    url: str


@dataclass
class ApiPage:
    """Represents an API documentation page."""
    title: str
    url: str
    endpoints: List[ApiEndpoint]
    schemas: List[ApiSchema]
    content: str
    last_crawled: Optional[datetime] = None 