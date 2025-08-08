"""
UI Components Package
Professional UI components for the Real Estate Decision Tool

This package provides all the UI components needed for the application:
- Layout and styling components
- Input form system with validation
- Session state management
- Interactive charts and visualizations
- Executive dashboard components
- Comparison views and tables
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

# Chart components
from .charts import (
    create_npv_comparison_chart,
    create_cash_flow_timeline_chart,
    create_cost_breakdown_chart,
    create_terminal_value_chart,
    create_annual_costs_comparison_chart,
    create_sensitivity_tornado_chart,
    create_scenario_comparison_chart,
    create_break_even_chart,
    create_risk_gauge_chart,
    create_roi_progression_chart
)

# Dashboard components
from .dashboard import (
    render_executive_summary_dashboard,
    create_results_summary_section,
    create_decision_recommendation_card,
    create_key_metrics_grid,
    render_analysis_results_tab,
    create_metric_widget,
    create_status_indicator,
    create_confidence_badge,
    create_kpi_card
)

# Comparison components
from .comparison import (
    render_side_by_side_comparison,
    create_cost_comparison_table,
    create_financial_metrics_comparison,
    render_detailed_comparison_tab,
    create_annual_costs_table,
    create_cash_flow_comparison_table,
    create_investment_summary_table
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
    'initialize_session',
    
    # Chart components
    'create_npv_comparison_chart',
    'create_cash_flow_timeline_chart',
    'create_cost_breakdown_chart',
    'create_terminal_value_chart',
    'create_annual_costs_comparison_chart',
    'create_sensitivity_tornado_chart',
    'create_scenario_comparison_chart',
    'create_break_even_chart',
    'create_risk_gauge_chart',
    'create_roi_progression_chart',
    
    # Dashboard components
    'render_executive_summary_dashboard',
    'create_results_summary_section',
    'create_decision_recommendation_card',
    'create_key_metrics_grid',
    'render_analysis_results_tab',
    'create_metric_widget',
    'create_status_indicator',
    'create_confidence_badge',
    'create_kpi_card',
    
    # Comparison components
    'render_side_by_side_comparison',
    'create_cost_comparison_table',
    'create_financial_metrics_comparison',
    'render_detailed_comparison_tab',
    'create_annual_costs_table',
    'create_cash_flow_comparison_table',
    'create_investment_summary_table'
]