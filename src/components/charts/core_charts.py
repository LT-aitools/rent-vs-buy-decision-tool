"""
Core Chart Components
Professional executive-ready charts for financial analysis results

This module provides the fundamental chart components for the Real Estate Decision Tool:
- NPV comparison bar charts
- Cash flow timeline visualizations  
- Cost breakdown pie charts
- Terminal value progression charts
- Annual costs comparison charts

All charts use Plotly with professional styling and mobile-responsive design.
Executive presentation quality with consistent branding.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional, Tuple
import streamlit as st


def get_professional_color_scheme() -> Dict[str, str]:
    """
    Get the professional color scheme matching the Streamlit theme
    
    Returns:
        Dictionary of color definitions for consistent branding
    """
    return {
        'primary': '#FF6B6B',        # Primary brand color from Streamlit config
        'secondary': '#4ECDC4',      # Secondary accent color
        'tertiary': '#45B7D1',       # Third accent color
        'success': '#96CEB4',        # Success/positive color
        'warning': '#FECA57',        # Warning/attention color
        'info': '#FF9FF3',           # Information color
        'background': '#FFFFFF',     # Background color
        'text': '#262730',           # Text color
        'grid': '#F0F2F6',           # Grid/secondary background
        'ownership': '#FF6B6B',      # Ownership scenarios
        'rental': '#4ECDC4',         # Rental scenarios
        'neutral': '#95A5A6'         # Neutral/comparison color
    }


def get_chart_layout_config(exclude_params: List[str] = None) -> Dict:
    """
    Get standard chart layout configuration for consistency
    
    Args:
        exclude_params: List of parameter names to exclude from the base config
    
    Returns:
        Plotly layout configuration dictionary
    """
    colors = get_professional_color_scheme()
    exclude_params = exclude_params or []
    
    config = {
        'font': {
            'family': 'Arial, sans-serif',
            'size': 12,
            'color': colors['text']
        },
        'plot_bgcolor': colors['background'],
        'paper_bgcolor': colors['background'],
        'margin': {'l': 60, 'r': 60, 't': 80, 'b': 60},
        'showlegend': True,
        'legend': {
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.2,
            'xanchor': 'center',
            'x': 0.5,
            'font': {'size': 10}
        },
        'hovermode': 'closest',
        'hoverlabel': {
            'bgcolor': colors['background'],
            'bordercolor': colors['primary'],
            'font': {'size': 11}
        }
    }
    
    # Remove excluded parameters
    for param in exclude_params:
        config.pop(param, None)
    
    return config


def format_currency(amount: float, include_k_notation: bool = True) -> str:
    """
    Format currency amounts for chart display
    
    Args:
        amount: Dollar amount to format
        include_k_notation: Whether to use K/M notation for large amounts
    
    Returns:
        Formatted currency string
    """
    if include_k_notation:
        if abs(amount) >= 1_000_000:
            return f"${amount/1_000_000:.1f}M"
        elif abs(amount) >= 1_000:
            return f"${amount/1_000:.0f}K"
    
    return f"${amount:,.0f}"


def create_npv_comparison_chart(
    analysis_results: Dict[str, float],
    show_confidence: bool = True
) -> go.Figure:
    """
    Create NPV comparison bar chart showing buy vs rent analysis
    
    Args:
        analysis_results: Dictionary with NPV analysis results including:
            - ownership_npv: NPV of ownership scenario
            - rental_npv: NPV of rental scenario
            - npv_difference: Difference between scenarios
            - recommendation: BUY, RENT, or MARGINAL
            - confidence: High, Medium, Low
        show_confidence: Whether to display confidence indicators
    
    Returns:
        Plotly figure object
    """
    try:
        # Validate input data
        if not analysis_results or not isinstance(analysis_results, dict):
            raise ValueError("analysis_results must be a valid dictionary")
        
        colors = get_professional_color_scheme()
        layout = get_chart_layout_config()
    
    # Extract data
    ownership_npv = analysis_results.get('ownership_npv', 0)
    rental_npv = analysis_results.get('rental_npv', 0)
    recommendation = analysis_results.get('recommendation', 'UNKNOWN')
    confidence = analysis_results.get('confidence', 'Low')
    
    # Prepare data for chart
    scenarios = ['Ownership (Buy)', 'Rental (Rent)']
    npv_values = [ownership_npv, rental_npv]
    colors_list = [colors['ownership'], colors['rental']]
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=scenarios,
            y=npv_values,
            marker_color=colors_list,
            text=[format_currency(val) for val in npv_values],
            textposition='auto',
            textfont={'size': 14, 'color': 'white', 'family': 'Arial Black'},
            hovertemplate='<b>%{x}</b><br>NPV: %{text}<extra></extra>',
            showlegend=False
        )
    ])
    
    # Update layout
    fig.update_layout(
        **layout,
        title={
            'text': f'<b>NPV Comparison Analysis</b><br><span style="font-size:14px;">Recommendation: {recommendation}' + 
                   (f' ({confidence} Confidence)' if show_confidence else '') + '</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title='Scenario',
        yaxis_title='Net Present Value ($)',
        yaxis={'tickformat': ',.0f'},
        height=450
    )
    
    # Add difference annotation
    npv_diff = ownership_npv - rental_npv
    better_scenario = "Ownership" if npv_diff > 0 else "Rental"
    
    fig.add_annotation(
        x=0.5,
        y=max(npv_values) * 0.8,
        text=f'<b>{better_scenario} Advantage:</b><br>{format_currency(abs(npv_diff))}',
        showarrow=False,
        font={'size': 14, 'color': colors['text']},
        bgcolor=colors['grid'],
        bordercolor=colors['primary'],
        borderwidth=2,
        xanchor='center'
    )
    
    return fig
    
    except Exception as e:
        # Return an error chart if something goes wrong
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text=f"Chart Error: {str(e)}",
            showarrow=False,
            font={'size': 16, 'color': 'red'},
            xanchor='center',
            yanchor='middle'
        )
        fig.update_layout(
            title="NPV Comparison Chart - Error",
            xaxis={'visible': False},
            yaxis={'visible': False},
            height=450
        )
        return fig


def create_cash_flow_timeline_chart(
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> go.Figure:
    """
    Create timeline chart showing year-by-year cash flows
    
    Args:
        ownership_flows: List of ownership cash flow data by year
        rental_flows: List of rental cash flow data by year
    
    Returns:
        Plotly figure object
    """
    try:
        # Validate input data
        if not ownership_flows or not rental_flows:
            raise ValueError("Both ownership_flows and rental_flows must be provided")
        if not isinstance(ownership_flows, list) or not isinstance(rental_flows, list):
            raise ValueError("Flow data must be lists")
        
        colors = get_professional_color_scheme()
        layout = get_chart_layout_config(exclude_params=['hovermode'])
    
    # Extract years and cash flows with proper cost/return distinction
    years = [flow['year'] for flow in ownership_flows]
    
    # For ownership: distinguish between operational costs and investment returns/terminal value
    ownership_cash_flows = []
    for i, flow in enumerate(ownership_flows):
        cash_flow = flow['net_cash_flow']
        # If this is the final year and there's significant positive cash flow, it likely includes terminal value
        if i == len(ownership_flows) - 1 and cash_flow > 0:
            # Final year with positive return (terminal value realization)
            ownership_cash_flows.append(cash_flow)
        else:
            # Regular operational costs (show as negative for costs)
            ownership_cash_flows.append(cash_flow if cash_flow < 0 else -cash_flow)
    
    # For rental: these are typically all costs, so show as negative
    rental_cash_flows = []
    for flow in rental_flows:
        cash_flow = flow['net_cash_flow']
        rental_cash_flows.append(cash_flow if cash_flow < 0 else -cash_flow)
    
    # Create figure
    fig = go.Figure()
    
    # Add ownership line with dynamic labeling for costs vs returns
    ownership_text_labels = []
    for i, val in enumerate(ownership_cash_flows):
        if val > 0:
            ownership_text_labels.append(f'Terminal Return: {format_currency(val)}')
        else:
            ownership_text_labels.append(f'Cost: {format_currency(abs(val))}')
    
    fig.add_trace(go.Scatter(
        x=years,
        y=ownership_cash_flows,
        mode='lines+markers',
        name='Ownership Cash Flow',
        line=dict(color=colors['ownership'], width=3),
        marker=dict(size=6),
        hovertemplate='<b>Year %{x}</b><br>%{text}<extra></extra>',
        text=ownership_text_labels
    ))
    
    # Add rental line  
    fig.add_trace(go.Scatter(
        x=years,
        y=rental_cash_flows,
        mode='lines+markers',
        name='Rental Costs',
        line=dict(color=colors['rental'], width=3),
        marker=dict(size=6),
        hovertemplate='<b>Year %{x}</b><br>Rental Cost: %{text}<extra></extra>',
        text=[format_currency(abs(val)) for val in rental_cash_flows]
    ))
    
    # Update layout
    fig.update_layout(
        **layout,
        title={
            'text': '<b>Annual Cash Flow Timeline</b><br><span style="font-size:14px;">Year-by-Year Cost Comparison</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title='Year',
        yaxis_title='Annual Cash Flow ($)',
        yaxis={'tickformat': ',.0f'},
        height=450,
        hovermode='x unified'
    )
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
    
    return fig
    
    except Exception as e:
        # Return an error chart if something goes wrong
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text=f"Chart Error: {str(e)}",
            showarrow=False,
            font={'size': 16, 'color': 'red'},
            xanchor='center',
            yanchor='middle'
        )
        fig.update_layout(
            title="Cash Flow Timeline Chart - Error",
            xaxis={'visible': False},
            yaxis={'visible': False},
            height=450
        )
        return fig


def create_cost_breakdown_chart(
    ownership_flows: List[Dict[str, float]],
    analysis_type: str = "year1"
) -> go.Figure:
    """
    Create pie chart showing cost breakdown for ownership scenario
    
    Args:
        ownership_flows: List of ownership cash flow data
        analysis_type: "year1" for first year, "average" for average across period
    
    Returns:
        Plotly figure object
    """
    colors = get_professional_color_scheme()
    
    if analysis_type == "year1" and ownership_flows:
        flow = ownership_flows[0]
    else:
        # Calculate averages
        flow = {
            'mortgage_payment': sum(f['mortgage_payment'] for f in ownership_flows) / len(ownership_flows),
            'property_taxes': sum(f['property_taxes'] for f in ownership_flows) / len(ownership_flows),
            'insurance': sum(f['insurance'] for f in ownership_flows) / len(ownership_flows),
            'maintenance': sum(f['maintenance'] for f in ownership_flows) / len(ownership_flows),
            'property_management': sum(f['property_management'] for f in ownership_flows) / len(ownership_flows),
            'capex_reserve': sum(f['capex_reserve'] for f in ownership_flows) / len(ownership_flows),
            'obsolescence_cost': sum(f['obsolescence_cost'] for f in ownership_flows) / len(ownership_flows)
        }
    
    # Prepare data
    labels = ['Mortgage Payment', 'Property Taxes', 'Insurance', 'Maintenance', 
              'Property Management', 'CapEx Reserve', 'Obsolescence Risk']
    values = [flow['mortgage_payment'], flow['property_taxes'], flow['insurance'], 
              flow['maintenance'], flow['property_management'], flow['capex_reserve'], 
              flow['obsolescence_cost']]
    
    # Filter out zero values
    filtered_data = [(label, value) for label, value in zip(labels, values) if value > 0]
    if filtered_data:
        labels, values = zip(*filtered_data)
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,  # Donut style
        textinfo='label+percent',
        textposition='outside',
        marker=dict(
            colors=[colors['primary'], colors['secondary'], colors['tertiary'], 
                   colors['success'], colors['warning'], colors['info'], colors['neutral']][:len(labels)]
        ),
        hovertemplate='<b>%{label}</b><br>Amount: %{text}<br>Percentage: %{percent}<extra></extra>',
        text=[format_currency(val) for val in values]
    )])
    
    # Update layout
    title_text = "First Year Cost Breakdown" if analysis_type == "year1" else "Average Annual Cost Breakdown"
    fig.update_layout(
        title={
            'text': f'<b>{title_text}</b><br><span style="font-size:14px;">Ownership Scenario</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        font={'family': 'Arial, sans-serif', 'size': 12},
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        ),
        height=450,
        margin={'l': 20, 'r': 150, 't': 80, 'b': 20}
    )
    
    return fig


def create_terminal_value_chart(
    analysis_results: Dict[str, float],
    ownership_flows: List[Dict[str, float]]
) -> go.Figure:
    """
    Create chart showing terminal value progression over time
    
    Args:
        analysis_results: Analysis results with terminal value data
        ownership_flows: Ownership cash flows for loan balance tracking
    
    Returns:
        Plotly figure object
    """
    colors = get_professional_color_scheme()
    layout = get_chart_layout_config(exclude_params=['hovermode'])
    
    # Extract terminal values
    ownership_terminal = analysis_results.get('ownership_terminal_value', 0)
    rental_terminal = analysis_results.get('rental_terminal_value', 0)
    
    # Extract actual data from ownership flows
    years = [flow['year'] for flow in ownership_flows]
    
    # Get property details from analysis results for calculations
    purchase_price = analysis_results.get('purchase_price', 500000)  # fallback if not in results
    land_value_pct = analysis_results.get('land_value_pct', 25.0)
    market_appreciation_rate = analysis_results.get('market_appreciation_rate', 3.0)
    
    # Calculate actual property value progression using terminal value functions
    property_values = []
    loan_balances = []
    net_equity_values = []
    
    # Import terminal value calculation function
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'calculations'))
        from terminal_value import calculate_property_appreciation
        
        for i, flow in enumerate(ownership_flows):
            year = i + 1
            
            # Calculate actual property appreciation for this year
            appreciated_value = calculate_property_appreciation(
                purchase_price, 
                market_appreciation_rate, 
                year
            )
            
            loan_balance = flow.get('remaining_loan_balance', 0)
            net_equity = max(0, appreciated_value - loan_balance)  # Cannot be negative
            
            property_values.append(appreciated_value)
            loan_balances.append(loan_balance)
            net_equity_values.append(net_equity)
            
    except ImportError:
        # Fallback to estimated calculation if import fails
        analysis_period = len(years)
        for i, flow in enumerate(ownership_flows):
            # Compound appreciation calculation as fallback
            year = i + 1
            appreciation_factor = (1 + market_appreciation_rate / 100) ** year
            estimated_property_value = purchase_price * appreciation_factor
            
            loan_balance = flow.get('remaining_loan_balance', 0)
            net_equity = max(0, estimated_property_value - loan_balance)
            
            property_values.append(estimated_property_value)
            loan_balances.append(loan_balance)
            net_equity_values.append(net_equity)
    
    # Create subplot
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Property Value & Loan Balance', 'Net Equity Progression'),
        vertical_spacing=0.15
    )
    
    # Add property value
    fig.add_trace(
        go.Scatter(
            x=years, y=property_values,
            mode='lines+markers',
            name='Property Value',
            line=dict(color=colors['success'], width=3),
            hovertemplate='<b>Year %{x}</b><br>Property Value: %{text}<extra></extra>',
            text=[format_currency(val) for val in property_values]
        ),
        row=1, col=1
    )
    
    # Add loan balance
    fig.add_trace(
        go.Scatter(
            x=years, y=loan_balances,
            mode='lines+markers',
            name='Loan Balance',
            line=dict(color=colors['warning'], width=3),
            fill='tonexty',
            fillcolor='rgba(254, 202, 87, 0.2)',
            hovertemplate='<b>Year %{x}</b><br>Loan Balance: %{text}<extra></extra>',
            text=[format_currency(val) for val in loan_balances]
        ),
        row=1, col=1
    )
    
    # Add net equity
    fig.add_trace(
        go.Scatter(
            x=years, y=net_equity_values,
            mode='lines+markers',
            name='Net Equity',
            line=dict(color=colors['primary'], width=4),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.2)',
            hovertemplate='<b>Year %{x}</b><br>Net Equity: %{text}<extra></extra>',
            text=[format_currency(val) for val in net_equity_values]
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        **layout,
        title={
            'text': '<b>Terminal Value Progression</b><br><span style="font-size:14px;">Property Value Build-Up Over Time</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        height=600,
        hovermode='x unified'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Value ($)", tickformat=',.0f')
    
    return fig


def create_annual_costs_comparison_chart(
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> go.Figure:
    """
    Create stacked bar chart comparing annual costs between scenarios
    
    Args:
        ownership_flows: Ownership cost flows by year
        rental_flows: Rental cost flows by year
    
    Returns:
        Plotly figure object
    """
    colors = get_professional_color_scheme()
    layout = get_chart_layout_config(exclude_params=['hovermode'])
    
    years = [flow['year'] for flow in ownership_flows]
    
    # Create figure
    fig = go.Figure()
    
    # Add ownership costs breakdown
    mortgage_payments = [flow['mortgage_payment'] for flow in ownership_flows]
    property_taxes = [flow['property_taxes'] for flow in ownership_flows]
    other_costs = [flow['insurance'] + flow['maintenance'] + flow['property_management'] + 
                   flow['capex_reserve'] + flow['obsolescence_cost'] for flow in ownership_flows]
    
    fig.add_trace(go.Bar(
        name='Mortgage Payment',
        x=years,
        y=mortgage_payments,
        marker_color=colors['primary'],
        hovertemplate='<b>Year %{x}</b><br>Mortgage: %{text}<extra></extra>',
        text=[format_currency(val) for val in mortgage_payments]
    ))
    
    fig.add_trace(go.Bar(
        name='Property Taxes',
        x=years,
        y=property_taxes,
        marker_color=colors['secondary'],
        hovertemplate='<b>Year %{x}</b><br>Property Taxes: %{text}<extra></extra>',
        text=[format_currency(val) for val in property_taxes]
    ))
    
    fig.add_trace(go.Bar(
        name='Other Costs',
        x=years,
        y=other_costs,
        marker_color=colors['tertiary'],
        hovertemplate='<b>Year %{x}</b><br>Other Costs: %{text}<extra></extra>',
        text=[format_currency(val) for val in other_costs]
    ))
    
    # Add rental costs as line
    rental_costs = [abs(flow['net_cash_flow']) for flow in rental_flows]
    fig.add_trace(go.Scatter(
        x=years,
        y=rental_costs,
        mode='lines+markers',
        name='Rental Costs',
        line=dict(color=colors['rental'], width=4),
        marker=dict(size=8),
        hovertemplate='<b>Year %{x}</b><br>Rental Cost: %{text}<extra></extra>',
        text=[format_currency(val) for val in rental_costs]
    ))
    
    # Update layout
    fig.update_layout(
        **layout,
        title={
            'text': '<b>Annual Costs Comparison</b><br><span style="font-size:14px;">Ownership Breakdown vs Rental Costs</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title='Year',
        yaxis_title='Annual Cost ($)',
        yaxis={'tickformat': ',.0f'},
        barmode='stack',
        height=450,
        hovermode='x unified'
    )
    
    return fig


def display_chart_with_options(
    fig: go.Figure,
    chart_title: str = "",
    export_filename: str = "chart"
) -> None:
    """
    Display a chart with export and interaction options
    
    Args:
        fig: Plotly figure to display
        chart_title: Title for the chart container
        export_filename: Base filename for exports
    """
    if chart_title:
        st.subheader(chart_title)
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Add export options in an expander
    with st.expander("📤 Export Options"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # PNG export
            if st.button("📊 PNG", key=f"png_{export_filename}"):
                fig.write_image(f"{export_filename}.png", width=1200, height=600, scale=2)
                st.success("PNG saved!")
        
        with col2:
            # PDF export
            if st.button("📋 PDF", key=f"pdf_{export_filename}"):
                fig.write_image(f"{export_filename}.pdf", width=1200, height=600)
                st.success("PDF saved!")
                
        with col3:
            # HTML export
            if st.button("🌐 HTML", key=f"html_{export_filename}"):
                fig.write_html(f"{export_filename}.html")
                st.success("HTML saved!")


# Example usage and testing functions
if __name__ == "__main__":
    # This would be used for testing the chart components
    pass