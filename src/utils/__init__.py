"""
Utilities Package
Common utilities for the Real Estate Decision Tool

This package provides utility functions for:
- Default values and validation ranges
- Professional formatting functions
- Helper functions for UI operations
"""

from .defaults import (
    DEFAULT_VALUES,
    VALIDATION_RANGES,
    FIELD_DESCRIPTIONS,
    CURRENCY_OPTIONS,
    PROPERTY_TYPE_OPTIONS,
    get_default_value,
    get_validation_range,
    get_field_description,
    get_expansion_year_options
)

from .formatting import (
    CURRENCY_SYMBOLS,
    format_currency,
    format_number,
    format_percentage,
    format_square_meters,
    format_date,
    format_years,
    format_months,
    format_rate_per_area,
    format_large_number,
    format_input_placeholder,
    validate_currency_input,
    format_comparison_value
)

from .helpers import (
    show_tooltip,
    create_info_card,
    format_validation_message,
    safe_divide,
    calculate_percentage_change,
    format_section_completion_status,
    get_field_value_with_fallback,
    update_session_field,
    calculate_loan_payment,
    calculate_annual_loan_payment,
    get_currency_formatting_info,
    create_download_link,
    display_comparison_metrics,
    create_expandable_help_section,
    validate_positive_number,
    validate_percentage,
    create_styled_metric_card,
    display_progress_indicator,
    create_two_column_comparison,
    format_business_number,
    create_status_badge,
    export_session_to_url,
    import_session_from_url
)

__all__ = [
    # Defaults and configuration
    'DEFAULT_VALUES',
    'VALIDATION_RANGES', 
    'FIELD_DESCRIPTIONS',
    'CURRENCY_OPTIONS',
    'PROPERTY_TYPE_OPTIONS',
    'get_default_value',
    'get_validation_range',
    'get_field_description',
    'get_expansion_year_options',
    
    # Formatting functions
    'CURRENCY_SYMBOLS',
    'format_currency',
    'format_number',
    'format_percentage',
    'format_square_meters',
    'format_date',
    'format_years',
    'format_months',
    'format_rate_per_area',
    'format_large_number',
    'format_input_placeholder',
    'validate_currency_input',
    'format_comparison_value',
    
    # Helper functions
    'show_tooltip',
    'create_info_card',
    'format_validation_message',
    'safe_divide',
    'calculate_percentage_change',
    'format_section_completion_status',
    'get_field_value_with_fallback',
    'update_session_field',
    'calculate_loan_payment',
    'calculate_annual_loan_payment',
    'get_currency_formatting_info',
    'create_download_link',
    'display_comparison_metrics',
    'create_expandable_help_section',
    'validate_positive_number',
    'validate_percentage',
    'create_styled_metric_card',
    'display_progress_indicator',
    'create_two_column_comparison',
    'format_business_number',
    'create_status_badge',
    'export_session_to_url',
    'import_session_from_url'
]