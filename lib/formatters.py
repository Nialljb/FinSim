"""
Number and currency formatting utilities
"""

from typing import Optional
from lib.constants import CURRENCY_INFO


def format_currency(
    amount: float,
    currency_code: str = "GBP",
    decimals: int = 0,
    include_symbol: bool = True
) -> str:
    """
    Format a number as currency
    
    Args:
        amount: The amount to format
        currency_code: Currency code (GBP, USD, etc.)
        decimals: Number of decimal places
        include_symbol: Whether to include currency symbol
    
    Returns:
        Formatted currency string
    
    Examples:
        >>> format_currency(1000, "GBP")
        "£1,000"
        >>> format_currency(1234.56, "USD", decimals=2)
        "$1,234.56"
    """
    # Get currency info
    currency = CURRENCY_INFO.get(currency_code, CURRENCY_INFO["GBP"])
    symbol = currency["symbol"]
    
    # Format number with commas
    if decimals == 0:
        formatted = f"{amount:,.0f}"
    else:
        formatted = f"{amount:,.{decimals}f}"
    
    # Add symbol if requested
    if include_symbol:
        return f"{symbol}{formatted}"
    return formatted


def format_percentage(
    value: float,
    decimals: int = 1,
    include_symbol: bool = True
) -> str:
    """
    Format a decimal as a percentage
    
    Args:
        value: Decimal value (e.g., 0.15 for 15%)
        decimals: Number of decimal places
        include_symbol: Whether to include % symbol
    
    Returns:
        Formatted percentage string
    
    Examples:
        >>> format_percentage(0.15)
        "15.0%"
        >>> format_percentage(0.0725, decimals=2)
        "7.25%"
    """
    percentage = value * 100
    formatted = f"{percentage:.{decimals}f}"
    
    if include_symbol:
        return f"{formatted}%"
    return formatted


def format_large_number(
    value: float,
    decimals: int = 1,
    include_suffix: bool = True
) -> str:
    """
    Format large numbers with K/M/B suffixes
    
    Args:
        value: The number to format
        decimals: Decimal places for formatted value
        include_suffix: Whether to include K/M/B suffix
    
    Returns:
        Formatted number string
    
    Examples:
        >>> format_large_number(1500)
        "1.5K"
        >>> format_large_number(2500000)
        "2.5M"
        >>> format_large_number(1200000000)
        "1.2B"
    """
    if not include_suffix:
        return f"{value:,.{decimals}f}"
    
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1_000_000_000:
        return f"{sign}{abs_value/1_000_000_000:.{decimals}f}B"
    elif abs_value >= 1_000_000:
        return f"{sign}{abs_value/1_000_000:.{decimals}f}M"
    elif abs_value >= 1_000:
        return f"{sign}{abs_value/1_000:.{decimals}f}K"
    else:
        return f"{sign}{abs_value:.{decimals}f}"


def format_number(
    value: float,
    decimals: int = 0,
    use_commas: bool = True
) -> str:
    """
    Format a number with optional commas and decimals
    
    Args:
        value: The number to format
        decimals: Number of decimal places
        use_commas: Whether to include thousand separators
    
    Returns:
        Formatted number string
    """
    if use_commas:
        return f"{value:,.{decimals}f}"
    else:
        return f"{value:.{decimals}f}"


def parse_currency_input(input_str: str) -> Optional[float]:
    """
    Parse currency input string to float
    Removes currency symbols, commas, and whitespace
    
    Args:
        input_str: Input string (e.g., "£1,000.50" or "$1000")
    
    Returns:
        Float value or None if invalid
    
    Examples:
        >>> parse_currency_input("£1,000.50")
        1000.5
        >>> parse_currency_input("$1,234,567")
        1234567.0
    """
    if not input_str:
        return None
    
    # Remove currency symbols and whitespace
    cleaned = input_str.strip()
    for symbol in ['£', '$', '€', '¥', 'C$', 'A$', 'NZ$', 'CHF', 'kr']:
        cleaned = cleaned.replace(symbol, '')
    
    # Remove commas
    cleaned = cleaned.replace(',', '')
    
    try:
        return float(cleaned)
    except ValueError:
        return None


# ============================================================================
# Export
# ============================================================================

__all__ = [
    'format_currency',
    'format_percentage',
    'format_large_number',
    'format_number',
    'parse_currency_input',
]
