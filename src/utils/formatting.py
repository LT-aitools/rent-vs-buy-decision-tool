"""
Formatting Utilities
Professional number and currency formatting for the UI

Provides consistent formatting across all components:
- Currency formatting with proper symbols
- Number formatting with thousands separators
- Percentage formatting
- Date formatting
"""

from typing import Union, Optional
import locale
from datetime import datetime, date

# Currency symbols mapping
CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€", 
    "GBP": "£",
    "CAD": "C$",
    "AUD": "A$",
    "ILS": "₪",
    "LEI": "lei",
    "PLN": "zł"
}

def format_currency(amount: Union[float, int], currency: str = "USD", 
                   include_cents: bool = True) -> str:
    """
    Format currency values with proper symbols and thousands separators
    
    Args:
        amount: The monetary amount to format
        currency: Currency code (USD, EUR, etc.)
        include_cents: Whether to include cents/decimals
        
    Returns:
        Formatted currency string
    """
    if amount is None:
        return "N/A"
    
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    
    if include_cents:
        formatted = f"{amount:,.2f}"
    else:
        formatted = f"{amount:,.0f}"
    
    # Handle special currency placement
    if currency in ["EUR"]:
        return f"{formatted} {symbol}"
    else:
        return f"{symbol}{formatted}"

def format_number(value: Union[float, int], decimals: int = 2) -> str:
    """
    Format numbers with thousands separators
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted number string
    """
    if value is None:
        return "N/A"
    
    if decimals == 0:
        return f"{value:,.0f}"
    else:
        return f"{value:,.{decimals}f}"

def format_percentage(value: Union[float, int], decimals: int = 1) -> str:
    """
    Format percentage values
    
    Args:
        value: Percentage value (e.g., 5.0 for 5%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"
    
    return f"{value:.{decimals}f}%"

def format_square_meters(value: Union[float, int]) -> str:
    """
    Format square meter values
    
    Args:
        value: Square meter amount
        
    Returns:
        Formatted area string
    """
    if value is None:
        return "N/A"
    
    return f"{value:,.0f} m²"

def format_date(date_value: Union[datetime, date, str]) -> str:
    """
    Format date values consistently
    
    Args:
        date_value: Date to format
        
    Returns:
        Formatted date string
    """
    if date_value is None:
        return "N/A"
    
    if isinstance(date_value, str):
        return date_value
    
    if isinstance(date_value, datetime):
        return date_value.strftime("%Y-%m-%d")
    
    if isinstance(date_value, date):
        return date_value.strftime("%Y-%m-%d")
    
    return str(date_value)

def format_years(years: Union[float, int]) -> str:
    """
    Format year values
    
    Args:
        years: Number of years
        
    Returns:
        Formatted years string
    """
    if years is None:
        return "N/A"
    
    if years == 1:
        return "1 year"
    else:
        return f"{years:,.0f} years"

def format_months(months: Union[float, int]) -> str:
    """
    Format month values
    
    Args:
        months: Number of months
        
    Returns:
        Formatted months string
    """
    if months is None:
        return "N/A"
    
    if months == 1:
        return "1 month"
    else:
        return f"{months:,.0f} months"

def format_rate_per_area(rate: Union[float, int], currency: str = "USD") -> str:
    """
    Format rate per square meter
    
    Args:
        rate: Rate amount per square meter
        currency: Currency code
        
    Returns:
        Formatted rate string
    """
    if rate is None or rate == 0:
        return "N/A"
    
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    return f"{symbol}{rate:,.2f} per m²"

def format_large_number(value: Union[float, int]) -> str:
    """
    Format large numbers with K, M, B suffixes
    
    Args:
        value: Number to format
        
    Returns:
        Formatted number string with suffix
    """
    if value is None:
        return "N/A"
    
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    elif abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return f"{value:.0f}"

def format_input_placeholder(field_name: str, currency: str = "USD") -> str:
    """
    Generate helpful placeholder text for input fields
    
    Args:
        field_name: Name of the input field
        currency: Currency for monetary fields
        
    Returns:
        Placeholder text
    """
    currency_symbol = CURRENCY_SYMBOLS.get(currency, currency)
    
    placeholders = {
        "purchase_price": f"e.g., {currency_symbol}500,000",
        "current_annual_rent": f"e.g., {currency_symbol}25,000",
        "insurance_cost": f"e.g., {currency_symbol}5,000",
        "property_management": f"e.g., {currency_symbol}2,000",
        "moving_costs": f"e.g., {currency_symbol}10,000",
        "total_property_size": "e.g., 5,000 m²",
        "current_space_needed": "e.g., 3,000 m²",
        "additional_space_needed": "e.g., 1,000 m²",
        "space_improvement_cost": f"e.g., {currency_symbol}25,000",
        "subletting_rate": f"e.g., {currency_symbol}15 per m²",
        "project_name": "e.g., Warehouse Project 2025",
        "location": "e.g., 123 Industrial Blvd, City",
        "analyst_name": "e.g., John Smith"
    }
    
    return placeholders.get(field_name, "")

def validate_currency_input(value_str: str) -> Optional[float]:
    """
    Parse and validate currency input strings
    
    Args:
        value_str: String input from user
        
    Returns:
        Parsed float value or None if invalid
    """
    if not value_str or value_str.strip() == "":
        return None
    
    # Remove common currency symbols and separators
    cleaned = value_str.replace("$", "").replace("€", "").replace("£", "") \
                      .replace("₪", "").replace("lei", "").replace("zł", "") \
                      .replace("C$", "").replace("A$", "") \
                      .replace(",", "").strip()
    
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def format_comparison_value(value: Union[float, int], is_positive_good: bool = True,
                          format_as_currency: bool = False, currency: str = "USD") -> str:
    """
    Format values for comparison with color coding context
    
    Args:
        value: Value to format
        is_positive_good: Whether positive values are good (True) or bad (False)
        format_as_currency: Whether to format as currency
        currency: Currency code for formatting
        
    Returns:
        Formatted value with appropriate indicators
    """
    if value is None:
        return "N/A"
    
    if format_as_currency:
        formatted = format_currency(abs(value), currency, include_cents=True)
        prefix = "+" if value >= 0 else "-"
    else:
        formatted = format_number(abs(value), decimals=0)
        prefix = "+" if value >= 0 else "-"
    
    return f"{prefix}{formatted}"