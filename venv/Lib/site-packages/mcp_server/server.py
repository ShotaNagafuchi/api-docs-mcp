from mcp.server.fastmcp import FastMCP, Context

# Create an MCP server specifically for basic math operations
mcp = FastMCP(
    "Basic Math Calculator",
    dependencies=[]  # No external dependencies needed for basic math
)

# Basic mathematical operations

@mcp.tool()
def add(a: float, b: float) -> float:
    """
    Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The sum of a and b
    """
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """
    Subtract the second number from the first.
    
    Args:
        a: Number to subtract from
        b: Number to subtract
        
    Returns:
        The result of a - b
    """
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        The product of a and b
    """
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> str:
    """
    Divide the first number by the second.
    
    Args:
        a: Numerator
        b: Denominator
        
    Returns:
        The result of a / b
    """
    if b == 0:
        return "Error: Division by zero is not allowed"
    return str(a / b)

# A resource with basic calculator instructions
@mcp.resource("calculator://help")
def calculator_help() -> str:
    """Basic calculator help information."""
    return """
    # Basic Math Calculator
    
    This calculator provides the following operations:
    
    - Addition: Use the `add` tool with two numbers
    - Subtraction: Use the `subtract` tool with two numbers
    - Multiplication: Use the `multiply` tool with two numbers
    - Division: Use the `divide` tool with two numbers
    
    Example:
    - To add 5 and 3, use: `add(5, 3)`
    """