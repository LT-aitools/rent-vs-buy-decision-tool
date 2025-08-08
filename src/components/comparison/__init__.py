"""
Comparison Views Package
Professional comparison components for rent vs buy analysis

This package provides detailed comparison views and tables:
- Side-by-side rent vs buy comparison tables
- Visual indicators for better/worse financial outcomes  
- Detailed cost breakdown comparisons
- Professional tabular presentations
- Mobile-responsive comparison layouts

All components maintain executive presentation quality with consistent styling.
"""

from .comparison_views import (
    render_side_by_side_comparison,
    create_cost_comparison_table,
    create_financial_metrics_comparison,
    create_investment_timeline_comparison,
    render_detailed_comparison_tab,
    create_scenario_summary_table
)

from .comparison_tables import (
    create_annual_costs_table,
    create_cash_flow_comparison_table,
    create_investment_summary_table,
    format_comparison_table,
    add_visual_indicators
)

__all__ = [
    # Comparison views
    'render_side_by_side_comparison',
    'create_cost_comparison_table',
    'create_financial_metrics_comparison', 
    'create_investment_timeline_comparison',
    'render_detailed_comparison_tab',
    'create_scenario_summary_table',
    
    # Comparison tables
    'create_annual_costs_table',
    'create_cash_flow_comparison_table', 
    'create_investment_summary_table',
    'format_comparison_table',
    'add_visual_indicators'
]