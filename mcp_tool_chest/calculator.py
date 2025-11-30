from mcp.server.fastmcp import FastMCP
import math

mcp = FastMCP("calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """
    Add two numbers.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of the two numbers.
    """
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """
    Subtract the second number from the first.

    Args:
        a: The number to be subtracted from.
        b: The number to subtract.

    Returns:
        The difference between the two numbers.
    """
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The product of the two numbers.
    """
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """
    Divide the first number by the second.

    Args:
        a: The numerator.
        b: The denominator.

    Returns:
        The quotient of the division.

    Raises:
        ValueError: If the denominator is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@mcp.tool()
def power(a: float, b: float) -> float:
    """
    Raise a number to a power.

    Args:
        a: The base number.
        b: The exponent.

    Returns:
        The result of raising the base to the exponent.
    """
    return math.pow(a, b)

@mcp.tool()
def sqrt(a: float) -> float:
    """
    Calculate the square root of a number.

    Args:
        a: The number to calculate the square root of.

    Returns:
        The square root of the number.

    Raises:
        ValueError: If the number is negative.
    """
    if a < 0:
        raise ValueError("Cannot calculate square root of a negative number")
    return math.sqrt(a)

if __name__ == "__main__":
    mcp.run(transport='stdio')
