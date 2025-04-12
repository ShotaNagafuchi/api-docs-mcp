# API Docs MCP Server

An MCP server for crawling API documentation websites and exposing their content through the Model Context Protocol. This allows AI models to search, browse, and reference API specifications.

## Features

- Crawls API documentation websites to extract structured information
- Exposes API docs as resources through MCP
- Provides search tools for finding specific API endpoints
- Includes prompt templates for common API documentation tasks
- Stores crawled data for offline access

## Installation

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## Usage

### Starting the server

```bash
python -m src.main --url https://example-api-docs.com
```

### Connecting to the server

This MCP server can be connected to any MCP client, such as Claude for Desktop. Configure your client to use this server with:

```json
{
  "api-docs": {
    "command": "python",
    "args": ["-m", "src.main", "--url", "https://example-api-docs.com"]
  }
}
```

## MCP Capabilities

### Resources

- API endpoint specifications
- Data models and schemas
- API examples and code snippets

### Tools

- `search_api`: Search for API endpoints by name, path, or description
- `get_endpoint_details`: Get detailed information about a specific endpoint
- `list_endpoints`: List all available API endpoints
- `find_examples`: Find examples for a specific API endpoint

### Prompts

- `explain_endpoint`: Generate a natural language explanation of an API endpoint
- `compare_endpoints`: Compare two API endpoints
- `generate_code`: Generate sample code for using an API endpoint

## License

MIT
