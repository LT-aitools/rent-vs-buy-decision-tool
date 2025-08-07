"""
Visualization Charts Package
Professional charts and visualizations for the Real Estate Decision Tool

This package provides all chart components for displaying financial analysis results:
- Core charts for NPV comparison, cash flows, cost breakdowns
- Advanced charts for sensitivity analysis and scenario comparison
- Interactive dashboard components with executive presentation quality
- Mobile-responsive design for all screen sizes

All charts use Plotly for interactivity with professional styling
consistent with the application theme.
"""

from .core_charts import (
    create_npv_comparison_chart,
    create_cash_flow_timeline_chart,
    create_cost_breakdown_chart,
    create_terminal_value_chart,
    create_annual_costs_comparison_chart
)

from .advanced_charts import (
    create_sensitivity_tornado_chart,
    create_scenario_comparison_chart,
    create_break_even_chart,
    create_risk_gauge_chart,
    create_roi_progression_chart
)

__all__ = [
    # Core charts
    'create_npv_comparison_chart',
    'create_cash_flow_timeline_chart', 
    'create_cost_breakdown_chart',
    'create_terminal_value_chart',
    'create_annual_costs_comparison_chart',
    
    # Advanced charts
    'create_sensitivity_tornado_chart',
    'create_scenario_comparison_chart',
    'create_break_even_chart',
    'create_risk_gauge_chart',
    'create_roi_progression_chart'
]