"""
UI Components Package
Professional UI components for the Real Estate Decision Tool

This package provides all the UI components needed for the application:
- Layout and styling components
- Input form system with validation
- Session state management
- Individual section components
"""

from .layout import (
    initialize_professional_layout,
    setup_page_config,
    apply_custom_css,
    render_header,
    render_sidebar_navigation,
    create_metric_card,
    create_section_header,
    create_info_box,
    create_professional_columns,
    render_footer,
    apply_responsive_design
)

from .input_forms import (
    render_project_information_section,
    render_property_market_section,
    render_purchase_parameters_section,
    render_rental_parameters_section,
    render_operational_parameters_section,
    render_tax_accounting_section,
    render_input_summary,
    render_all_input_forms
)

from .validation import (
    ValidationResult,
    InputValidator,
    display_validation_messages,
    validate_and_display
)

from .session_management import (
    SessionManager,
    get_session_manager,
    initialize_session
)

__all__ = [
    # Layout components
    'initialize_professional_layout',
    'setup_page_config', 
    'apply_custom_css',
    'render_header',
    'render_sidebar_navigation',
    'create_metric_card',
    'create_section_header',
    'create_info_box',
    'create_professional_columns',
    'render_footer',
    'apply_responsive_design',
    
    # Input form components
    'render_project_information_section',
    'render_property_market_section', 
    'render_purchase_parameters_section',
    'render_rental_parameters_section',
    'render_operational_parameters_section',
    'render_tax_accounting_section',
    'render_input_summary',
    'render_all_input_forms',
    
    # Validation components
    'ValidationResult',
    'InputValidator',
    'display_validation_messages', 
    'validate_and_display',
    
    # Session management
    'SessionManager',
    'get_session_manager',
    'initialize_session'
]