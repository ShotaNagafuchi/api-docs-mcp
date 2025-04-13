"""
Parser module for extracting structured information from API documentation.
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional

from src.storage.models import ApiEndpoint, ApiSchema


class ApiDocParser:
    """Parser for API documentation HTML content."""
    
    def __init__(self):
        """Initialize the API documentation parser."""
        pass
    
    def parse_page(self, html: str, url: str) -> Dict:
        """
        Parse an API documentation page.
        
        Args:
            html: The HTML content of the page
            url: The URL of the page
            
        Returns:
            Dictionary containing parsed information
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract page title
        title = self._extract_title(soup)
        
        # Extract endpoints
        endpoints = self._extract_endpoints(soup)
        
        # Extract schemas
        schemas = self._extract_schemas(soup)
        
        return {
            'title': title,
            'endpoints': endpoints,
            'schemas': schemas,
            'url': url
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the page title."""
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else ''
    
    def _extract_endpoints(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract API endpoints from the page."""
        endpoints = []
        
        # Look for common endpoint documentation patterns
        endpoint_sections = soup.find_all(['div', 'section'], class_=lambda x: x and any(
            cls in x.lower() for cls in ['endpoint', 'api', 'method', 'operation']
        ))
        
        for section in endpoint_sections:
            endpoint = {
                'path': self._extract_endpoint_path(section),
                'method': self._extract_endpoint_method(section),
                'description': self._extract_endpoint_description(section),
                'parameters': self._extract_endpoint_parameters(section),
                'responses': self._extract_endpoint_responses(section)
            }
            if endpoint['path']:
                endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_schemas(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract data schemas from the page."""
        schemas = []
        
        # Look for common schema documentation patterns
        schema_sections = soup.find_all(['div', 'section'], class_=lambda x: x and any(
            cls in x.lower() for cls in ['schema', 'model', 'type', 'object']
        ))
        
        for section in schema_sections:
            schema = {
                'name': self._extract_schema_name(section),
                'description': self._extract_schema_description(section),
                'properties': self._extract_schema_properties(section)
            }
            if schema['name']:
                schemas.append(schema)
        
        return schemas
    
    def _extract_endpoint_path(self, section: BeautifulSoup) -> str:
        """Extract the endpoint path."""
        path_elem = section.find(['code', 'pre'], string=lambda x: x and '/' in x)
        return path_elem.text.strip() if path_elem else ''
    
    def _extract_endpoint_method(self, section: BeautifulSoup) -> str:
        """Extract the HTTP method."""
        method_elem = section.find(['code', 'span'], string=lambda x: x and x.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
        return method_elem.text.strip().upper() if method_elem else ''
    
    def _extract_endpoint_description(self, section: BeautifulSoup) -> str:
        """Extract the endpoint description."""
        desc_elem = section.find(['p', 'div'], class_=lambda x: x and 'description' in x.lower())
        return desc_elem.text.strip() if desc_elem else ''
    
    def _extract_endpoint_parameters(self, section: BeautifulSoup) -> List[Dict]:
        """Extract endpoint parameters."""
        parameters = []
        param_sections = section.find_all(['div', 'table'], class_=lambda x: x and 'parameter' in x.lower())
        
        for param_section in param_sections:
            param = {
                'name': self._extract_parameter_name(param_section),
                'type': self._extract_parameter_type(param_section),
                'required': self._extract_parameter_required(param_section),
                'description': self._extract_parameter_description(param_section)
            }
            if param['name']:
                parameters.append(param)
        
        return parameters
    
    def _extract_endpoint_responses(self, section: BeautifulSoup) -> List[Dict]:
        """Extract endpoint responses."""
        responses = []
        response_sections = section.find_all(['div', 'table'], class_=lambda x: x and 'response' in x.lower())
        
        for response_section in response_sections:
            response = {
                'code': self._extract_response_code(response_section),
                'description': self._extract_response_description(response_section),
                'schema': self._extract_response_schema(response_section)
            }
            if response['code']:
                responses.append(response)
        
        return responses
    
    def _extract_schema_name(self, section: BeautifulSoup) -> str:
        """Extract the schema name."""
        name_elem = section.find(['h2', 'h3', 'h4', 'code'], string=lambda x: x and not x.isspace())
        return name_elem.text.strip() if name_elem else ''
    
    def _extract_schema_description(self, section: BeautifulSoup) -> str:
        """Extract the schema description."""
        desc_elem = section.find(['p', 'div'], class_=lambda x: x and 'description' in x.lower())
        return desc_elem.text.strip() if desc_elem else ''
    
    def _extract_schema_properties(self, section: BeautifulSoup) -> List[Dict]:
        """Extract schema properties."""
        properties = []
        prop_sections = section.find_all(['div', 'table'], class_=lambda x: x and 'property' in x.lower())
        
        for prop_section in prop_sections:
            prop = {
                'name': self._extract_property_name(prop_section),
                'type': self._extract_property_type(prop_section),
                'required': self._extract_property_required(prop_section),
                'description': self._extract_property_description(prop_section)
            }
            if prop['name']:
                properties.append(prop)
        
        return properties
    
    def _extract_parameter_name(self, section: BeautifulSoup) -> str:
        """Extract parameter name."""
        name_elem = section.find(['code', 'td'], string=lambda x: x and not x.isspace())
        return name_elem.text.strip() if name_elem else ''
    
    def _extract_parameter_type(self, section: BeautifulSoup) -> str:
        """Extract parameter type."""
        type_elem = section.find(['code', 'td'], string=lambda x: x and any(t in x.lower() for t in ['string', 'integer', 'boolean', 'array', 'object']))
        return type_elem.text.strip() if type_elem else ''
    
    def _extract_parameter_required(self, section: BeautifulSoup) -> bool:
        """Extract whether parameter is required."""
        required_elem = section.find(string=lambda x: x and 'required' in x.lower())
        return bool(required_elem)
    
    def _extract_parameter_description(self, section: BeautifulSoup) -> str:
        """Extract parameter description."""
        desc_elem = section.find(['p', 'td'], class_=lambda x: x and 'description' in x.lower())
        return desc_elem.text.strip() if desc_elem else ''
    
    def _extract_response_code(self, section: BeautifulSoup) -> str:
        """Extract response code."""
        code_elem = section.find(['code', 'td'], string=lambda x: x and x.isdigit())
        return code_elem.text.strip() if code_elem else ''
    
    def _extract_response_description(self, section: BeautifulSoup) -> str:
        """Extract response description."""
        desc_elem = section.find(['p', 'td'], class_=lambda x: x and 'description' in x.lower())
        return desc_elem.text.strip() if desc_elem else ''
    
    def _extract_response_schema(self, section: BeautifulSoup) -> Dict:
        """Extract response schema."""
        schema_elem = section.find(['div', 'pre'], class_=lambda x: x and 'schema' in x.lower())
        if not schema_elem:
            return {}
        
        return {
            'type': self._extract_schema_type(schema_elem),
            'properties': self._extract_schema_properties(schema_elem)
        }
    
    def _extract_property_name(self, section: BeautifulSoup) -> str:
        """Extract property name."""
        name_elem = section.find(['code', 'td'], string=lambda x: x and not x.isspace())
        return name_elem.text.strip() if name_elem else ''
    
    def _extract_property_type(self, section: BeautifulSoup) -> str:
        """Extract property type."""
        type_elem = section.find(['code', 'td'], string=lambda x: x and any(t in x.lower() for t in ['string', 'integer', 'boolean', 'array', 'object']))
        return type_elem.text.strip() if type_elem else ''
    
    def _extract_property_required(self, section: BeautifulSoup) -> bool:
        """Extract whether property is required."""
        required_elem = section.find(string=lambda x: x and 'required' in x.lower())
        return bool(required_elem)
    
    def _extract_property_description(self, section: BeautifulSoup) -> str:
        """Extract property description."""
        desc_elem = section.find(['p', 'td'], class_=lambda x: x and 'description' in x.lower())
        return desc_elem.text.strip() if desc_elem else ''
    
    def _extract_schema_type(self, section: BeautifulSoup) -> str:
        """Extract schema type."""
        type_elem = section.find(['code', 'td'], string=lambda x: x and any(t in x.lower() for t in ['object', 'array', 'string', 'integer', 'boolean']))
        return type_elem.text.strip() if type_elem else 'object' 