"""
Dashboard Components Package
Executive dashboard components for the Real Estate Decision Tool

This package provides professional dashboard layouts and widgets:
- Results summary dashboard with key metrics
- Decision recommendation cards with confidence indicators
- Mobile-responsive executive presentation layouts
- Interactive metric widgets and status indicators

All components follow professional styling and executive presentation standards.
"""

from .results_dashboard import (
    render_executive_summary_dashboard,
    create_results_summary_section,
    create_decision_recommendation_card,
    create_key_metrics_grid,
    create_investment_comparison_section,
    render_analysis_results_tab
)

from .metric_widgets import (
    create_metric_widget,
    create_status_indicator,
    create_confidence_badge,
    create_progress_indicator,
    create_kpi_card,
    create_comparison_metric_pair
)

__all__ = [
    # Dashboard layouts
    'render_executive_summary_dashboard',
    'create_results_summary_section',
    'create_decision_recommendation_card', 
    'create_key_metrics_grid',
    'create_investment_comparison_section',
    'render_analysis_results_tab',
    
    # Metric widgets
    'create_metric_widget',
    'create_status_indicator',
    'create_confidence_badge',
    'create_progress_indicator',
    'create_kpi_card',
    'create_comparison_metric_pair'
]