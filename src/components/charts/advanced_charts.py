"""
Advanced Chart Components
Interactive visualizations for sensitivity analysis and advanced financial metrics

This module provides sophisticated chart components for executive-level analysis:
- Tornado diagrams for sensitivity analysis
- Scenario comparison charts
- Break-even analysis visualizations
- Risk assessment gauge charts  
- ROI progression charts

All charts maintain professional styling and executive presentation quality.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import streamlit as st

from .core_charts import get_professional_color_scheme, get_chart_layout_config, format_currency


def validate_chart_inputs(
    data: Any, 
    required_keys: Optional[List[str]] = None, 
    data_type: str = "generic"
) -> Tuple[bool, str]:
    """
    Comprehensive input validation for chart functions
    
    Args:
        data: Input data to validate
        required_keys: List of required keys for dictionary data
        data_type: Type of data being validated for specific checks
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    try:
        # Basic existence check
        if data is None:
            return False, f"No {data_type} data provided"
        
        # Check for empty data structures
        if isinstance(data, (list, dict)) and len(data) == 0:
            return False, f"Empty {data_type} data provided"
        
        # Dictionary validation
        if isinstance(data, dict):
            if required_keys:
                missing_keys = [key for key in required_keys if key not in data]
                if missing_keys:
                    return False, f"Missing required keys in {data_type} data: {', '.join(missing_keys)}"
            
            # Check for all None/empty values
            if all(value is None or value == 0 for value in data.values()):
                return False, f"All values in {data_type} data are None or zero"
        
        # List validation
        elif isinstance(data, list):
            if all(item is None or (isinstance(item, dict) and not item) for item in data):
                return False, f"All items in {data_type} data are None or empty"
            
            # Check for consistent data structure in list items
            if data and isinstance(data[0], dict):
                first_keys = set(data[0].keys())
                for i, item in enumerate(data[1:], 1):
                    if not isinstance(item, dict):
                        return False, f"Inconsistent data types in {data_type} data at index {i}"
                    if set(item.keys()) != first_keys:
                        return False, f"Inconsistent dictionary structure in {data_type} data at index {i}"
        
        # Specific validations based on data type
        if data_type == "sensitivity_results":
            return validate_sensitivity_data(data)
        elif data_type == "cash_flows":
            return validate_cash_flow_data(data)
        elif data_type == "analysis_results":
            return validate_analysis_results_data(data)
        
        return True, "Valid"
        
    except Exception as e:
        return False, f"Validation error for {data_type} data: {str(e)}"


def validate_sensitivity_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate sensitivity analysis data structure"""
    if not isinstance(data, dict):
        return False, "Sensitivity results must be a dictionary"
    
    for param, results in data.items():
        if not isinstance(results, dict):
            return False, f"Sensitivity results for {param} must be a dictionary"
        if len(results) < 2:
            return False, f"Sensitivity results for {param} must have at least 2 scenarios"
    
    return True, "Valid sensitivity data"


def validate_cash_flow_data(data: List[Dict[str, float]]) -> Tuple[bool, str]:
    """Validate cash flow data structure"""
    if not isinstance(data, list):
        return False, "Cash flow data must be a list"
    
    required_keys = ['year', 'net_cash_flow']
    for i, flow in enumerate(data):
        if not isinstance(flow, dict):
            return False, f"Cash flow item {i} must be a dictionary"
        
        missing_keys = [key for key in required_keys if key not in flow]
        if missing_keys:
            return False, f"Cash flow item {i} missing keys: {', '.join(missing_keys)}"
        
        # Check for valid year values
        if not isinstance(flow['year'], (int, float)) or flow['year'] <= 0:
            return False, f"Invalid year value in cash flow item {i}: {flow['year']}"
    
    return True, "Valid cash flow data"


def validate_analysis_results_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate analysis results data structure"""
    if not isinstance(data, dict):
        return False, "Analysis results must be a dictionary"
    
    # Check for key financial metrics
    numeric_keys = ['ownership_npv', 'rental_npv', 'npv_difference']
    for key in numeric_keys:
        if key in data and not isinstance(data[key], (int, float)):
            return False, f"Analysis result {key} must be a number"
    
    return True, "Valid analysis results data"


def extract_npv_impact(sensitivity_result: Any) -> float:
    """
    Safely extract NPV impact from various sensitivity result formats
    
    Args:
        sensitivity_result: Result from sensitivity analysis (various formats)
        
    Returns:
        NPV impact value, 0 if extraction fails
    """
    try:
        # Handle dictionary format
        if isinstance(sensitivity_result, dict):
            # Try common keys for NPV difference
            for key in ['npv_difference', 'npv_impact', 'npv_delta', 'ownership_npv', 'total_npv']:
                if key in sensitivity_result:
                    value = sensitivity_result[key]
                    return float(value) if value is not None else 0.0
            
            # If no direct NPV key, try to compute from ownership and rental NPVs
            if 'ownership_npv' in sensitivity_result and 'rental_npv' in sensitivity_result:
                ownership_npv = sensitivity_result['ownership_npv'] or 0
                rental_npv = sensitivity_result['rental_npv'] or 0
                return float(ownership_npv - rental_npv)
            
            # Return first numeric value found
            for value in sensitivity_result.values():
                if isinstance(value, (int, float)) and value != 0:
                    return float(value)
        
        # Handle direct numeric value
        elif isinstance(sensitivity_result, (int, float)):
            return float(sensitivity_result)
        
        # Handle string that might be numeric
        elif isinstance(sensitivity_result, str):
            # Try to parse as number
            clean_str = sensitivity_result.replace('$', '').replace(',', '').strip()
            try:
                return float(clean_str)
            except ValueError:
                pass
        
        # Safe fallback
        return 0.0
        
    except Exception:
        # If all else fails, return 0
        return 0.0


def create_sensitivity_tornado_chart(
    sensitivity_results: Dict[str, Dict[str, float]],
    base_npv: float
) -> go.Figure:
    """
    Create tornado diagram showing sensitivity analysis results
    
    Args:
        sensitivity_results: Dictionary with sensitivity test results
        base_npv: Base case NPV for comparison
        
    Returns:
        Plotly figure object
    """
    # Input validation
    is_valid, error_msg = validate_chart_inputs(sensitivity_results, data_type="sensitivity_results")
    if not is_valid:
        fig = go.Figure()
        fig.update_layout(
            title="Sensitivity Analysis - Data Error",
            annotations=[dict(text=f"Data validation failed: {error_msg}", 
                            x=0.5, y=0.5, showarrow=False)]
        )
        return fig
    
    if not isinstance(base_npv, (int, float)):
        fig = go.Figure()
        fig.update_layout(
            title="Sensitivity Analysis - Invalid Base NPV",
            annotations=[dict(text="Base NPV must be a number", 
                            x=0.5, y=0.5, showarrow=False)]
        )
        return fig
    
    colors = get_professional_color_scheme()
    layout = get_chart_layout_config()
    
    # Process sensitivity data
    parameters = []
    low_impacts = []
    high_impacts = []
    parameter_labels = []
    
    # Extract sensitivity data and calculate impacts with robust handling
    for param, results in sensitivity_results.items():
        if len(results) >= 2:  # Need at least low and high values
            values = list(results.values())
            npv_values = []
            
            # Robust NPV extraction for various data formats
            for result in values:
                npv_value = extract_npv_impact(result)
                npv_values.append(npv_value)
            
            if len(npv_values) >= 2 and any(v != 0 for v in npv_values):
                low_impact = min(npv_values) - base_npv
                high_impact = max(npv_values) - base_npv
                
                parameters.append(param)
                low_impacts.append(low_impact)
                high_impacts.append(high_impact)
                
                # Clean up parameter name for display
                clean_name = param.replace('_', ' ').title()
                parameter_labels.append(clean_name)
    
    if not parameters:
        # Return empty chart if no sensitivity data
        fig = go.Figure()
        fig.update_layout(
            title="Sensitivity Analysis - No Data Available",
            annotations=[dict(text="No sensitivity data available", 
                            x=0.5, y=0.5, showarrow=False)]
        )
        return fig
    
    # Sort by impact magnitude
    impact_magnitudes = [abs(high - low) for high, low in zip(high_impacts, low_impacts)]
    sorted_data = sorted(zip(parameter_labels, low_impacts, high_impacts, impact_magnitudes), 
                        key=lambda x: x[3], reverse=True)
    
    if sorted_data:
        parameter_labels, low_impacts, high_impacts, _ = zip(*sorted_data)
    
    # Create tornado chart
    fig = go.Figure()
    
    # Add bars for negative impacts (left side)
    fig.add_trace(go.Bar(
        name='Downside Impact',
        y=parameter_labels,
        x=low_impacts,
        orientation='h',
        marker_color=colors['warning'],
        hovertemplate='<b>%{y}</b><br>Downside: %{text}<extra></extra>',
        text=[format_currency(val) for val in low_impacts]
    ))
    
    # Add bars for positive impacts (right side)  
    fig.add_trace(go.Bar(
        name='Upside Impact',
        y=parameter_labels,
        x=high_impacts,
        orientation='h',
        marker_color=colors['success'],
        hovertemplate='<b>%{y}</b><br>Upside: %{text}<extra></extra>',
        text=[format_currency(val) for val in high_impacts]
    ))
    
    # Update layout
    fig.update_layout(
        **layout,
        title={
            'text': '<b>Sensitivity Analysis - Tornado Diagram</b><br><span style="font-size:14px;">Impact of Key Parameters on NPV</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title='NPV Impact ($)',
        yaxis_title='Parameter',
        xaxis={'tickformat': ',.0f'},
        barmode='overlay',
        height=max(400, len(parameter_labels) * 40 + 100)
    )
    
    # Add vertical line at zero
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.7)
    
    return fig


def create_scenario_comparison_chart(
    scenarios: List[Dict[str, Any]]
) -> go.Figure:
    """
    Create chart comparing multiple scenarios
    
    Args:
        scenarios: List of scenario dictionaries with analysis results
    
    Returns:
        Plotly figure object
    """
    colors = get_professional_color_scheme()
    layout = get_chart_layout_config()
    
    if not scenarios:
        fig = go.Figure()
        fig.update_layout(
            title="Scenario Comparison - No Data Available",
            annotations=[dict(text="No scenario data available", 
                            x=0.5, y=0.5, showarrow=False)]
        )
        return fig
    
    # Extract scenario data
    scenario_names = []
    ownership_npvs = []
    rental_npvs = []
    recommendations = []
    
    for i, scenario in enumerate(scenarios):
        scenario_names.append(scenario.get('name', f'Scenario {i+1}'))
        ownership_npvs.append(scenario.get('ownership_npv', 0))
        rental_npvs.append(scenario.get('rental_npv', 0))
        recommendations.append(scenario.get('recommendation', 'UNKNOWN'))
    
    # Create grouped bar chart
    fig = go.Figure()
    
    # Add ownership NPVs
    fig.add_trace(go.Bar(
        name='Ownership NPV',
        x=scenario_names,
        y=ownership_npvs,
        marker_color=colors['ownership'],
        text=[format_currency(val) for val in ownership_npvs],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Ownership NPV: %{text}<extra></extra>'
    ))
    
    # Add rental NPVs
    fig.add_trace(go.Bar(
        name='Rental NPV', 
        x=scenario_names,
        y=rental_npvs,
        marker_color=colors['rental'],
        text=[format_currency(val) for val in rental_npvs],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Rental NPV: %{text}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        **layout,
        title={
            'text': '<b>Scenario Comparison Analysis</b><br><span style="font-size:14px;">NPV Comparison Across Different Scenarios</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title='Scenario',
        yaxis_title='Net Present Value ($)',
        yaxis={'tickformat': ',.0f'},
        barmode='group',
        height=450
    )
    
    # Add recommendation annotations
    for i, rec in enumerate(recommendations):
        color = colors['success'] if rec == 'BUY' else colors['warning'] if rec == 'RENT' else colors['neutral']
        fig.add_annotation(
            x=i,
            y=max(ownership_npvs[i], rental_npvs[i]) * 1.1,
            text=f"<b>{rec}</b>",
            showarrow=False,
            font={'size': 12, 'color': color},
            bgcolor='white',
            bordercolor=color,
            borderwidth=1
        )
    
    return fig


def create_break_even_chart(
    break_even_data: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> go.Figure:
    """
    Create break-even analysis visualization
    
    Args:
        break_even_data: Dictionary with break-even analysis results
        ownership_flows: Ownership cash flow data
        rental_flows: Rental cash flow data
    
    Returns:
        Plotly figure object
    """
    colors = get_professional_color_scheme()
    layout = get_chart_layout_config(exclude_params=['hovermode'])
    
    years = [flow['year'] for flow in ownership_flows]
    
    # Calculate cumulative costs
    cumulative_ownership = []
    cumulative_rental = []
    cumulative_diff = []
    
    running_ownership = 0
    running_rental = 0
    
    for i in range(len(years)):
        running_ownership += abs(ownership_flows[i]['net_cash_flow'])
        running_rental += abs(rental_flows[i]['net_cash_flow'])
        
        cumulative_ownership.append(running_ownership)
        cumulative_rental.append(running_rental)
        cumulative_diff.append(running_ownership - running_rental)
    
    # Create subplot with two charts
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Cumulative Cost Comparison', 'Cost Difference Over Time'),
        vertical_spacing=0.15
    )
    
    # Top chart: Cumulative costs
    fig.add_trace(
        go.Scatter(
            x=years, y=cumulative_ownership,
            mode='lines+markers',
            name='Cumulative Ownership Cost',
            line=dict(color=colors['ownership'], width=3),
            hovertemplate='<b>Year %{x}</b><br>Cumulative Ownership: %{text}<extra></extra>',
            text=[format_currency(val) for val in cumulative_ownership]
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=years, y=cumulative_rental,
            mode='lines+markers',
            name='Cumulative Rental Cost',
            line=dict(color=colors['rental'], width=3),
            hovertemplate='<b>Year %{x}</b><br>Cumulative Rental: %{text}<extra></extra>',
            text=[format_currency(val) for val in cumulative_rental]
        ),
        row=1, col=1
    )
    
    # Bottom chart: Difference over time
    positive_diff = [max(0, diff) for diff in cumulative_diff]
    negative_diff = [min(0, diff) for diff in cumulative_diff]
    
    fig.add_trace(
        go.Scatter(
            x=years, y=positive_diff,
            fill='tozeroy',
            fillcolor=f'rgba(255, 107, 107, 0.3)',
            line=dict(color=colors['ownership']),
            name='Ownership Costs More',
            hovertemplate='<b>Year %{x}</b><br>Excess Ownership Cost: %{text}<extra></extra>',
            text=[format_currency(val) for val in positive_diff]
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=years, y=negative_diff,
            fill='tozeroy',
            fillcolor=f'rgba(78, 205, 196, 0.3)',
            line=dict(color=colors['rental']),
            name='Rental Costs More',
            hovertemplate='<b>Year %{x}</b><br>Excess Rental Cost: %{text}<extra></extra>',
            text=[format_currency(abs(val)) for val in negative_diff]
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        **layout,
        title={
            'text': '<b>Break-Even Analysis</b><br><span style="font-size:14px;">When Does Ownership Break Even?</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        height=600,
        hovermode='x unified'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Cumulative Cost ($)", tickformat=',.0f', row=1, col=1)
    fig.update_yaxes(title_text="Cost Difference ($)", tickformat=',.0f', row=2, col=1)
    
    # Add break-even annotation if available
    break_even_year = break_even_data.get('break_even_year')
    if break_even_year and break_even_year <= len(years):
        fig.add_vline(
            x=break_even_year,
            line_dash="dash",
            line_color=colors['success'],
            annotation_text=f"Break-Even: Year {break_even_year}",
            row=1, col=1
        )
    
    return fig


def create_risk_gauge_chart(
    risk_metrics: Dict[str, float]
) -> go.Figure:
    """
    Create risk assessment gauge chart
    
    Args:
        risk_metrics: Dictionary with risk assessment metrics
    
    Returns:
        Plotly figure object
    """
    colors = get_professional_color_scheme()
    
    # Extract risk score (0-100 scale)
    risk_score = risk_metrics.get('overall_risk_score', 50)
    market_risk = risk_metrics.get('market_risk', 50)
    financial_risk = risk_metrics.get('financial_risk', 50)
    operational_risk = risk_metrics.get('operational_risk', 50)
    
    # Determine risk level and color
    if risk_score <= 30:
        risk_level = "Low Risk"
        gauge_color = colors['success']
    elif risk_score <= 70:
        risk_level = "Moderate Risk" 
        gauge_color = colors['warning']
    else:
        risk_level = "High Risk"
        gauge_color = colors['primary']
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = risk_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>Overall Risk Assessment</b><br><span style='font-size:14px;'>{risk_level}</span>"},
        delta = {'reference': 50, 'position': "top"},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': gauge_color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': 'lightgreen'},
                {'range': [30, 70], 'color': 'yellow'},
                {'range': [70, 100], 'color': 'lightcoral'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    # Update layout
    fig.update_layout(
        font={'color': colors['text'], 'family': 'Arial, sans-serif'},
        height=400,
        margin={'l': 20, 'r': 20, 't': 60, 'b': 20}
    )
    
    # Add risk breakdown annotation
    breakdown_text = f"Market Risk: {market_risk:.0f}%<br>Financial Risk: {financial_risk:.0f}%<br>Operational Risk: {operational_risk:.0f}%"
    fig.add_annotation(
        x=0.5, y=0.1,
        text=breakdown_text,
        showarrow=False,
        font={'size': 12},
        bgcolor='white',
        bordercolor='gray',
        borderwidth=1
    )
    
    return fig


def create_roi_progression_chart(
    analysis_results: Dict[str, float],
    ownership_flows: List[Dict[str, float]]
) -> go.Figure:
    """
    Create ROI progression chart showing return on investment over time
    
    Args:
        analysis_results: Analysis results with investment data
        ownership_flows: Ownership cash flows for ROI calculation
    
    Returns:
        Plotly figure object
    """
    # Input validation
    is_valid_results, error_msg_results = validate_chart_inputs(analysis_results, data_type="analysis_results")
    if not is_valid_results:
        fig = go.Figure()
        fig.update_layout(
            title="ROI Progression - Analysis Data Error",
            annotations=[dict(text=f"Analysis data validation failed: {error_msg_results}", 
                            x=0.5, y=0.5, showarrow=False)]
        )
        return fig
    
    is_valid_flows, error_msg_flows = validate_chart_inputs(ownership_flows, data_type="cash_flows")
    if not is_valid_flows:
        fig = go.Figure()
        fig.update_layout(
            title="ROI Progression - Cash Flow Data Error",
            annotations=[dict(text=f"Cash flow data validation failed: {error_msg_flows}", 
                            x=0.5, y=0.5, showarrow=False)]
        )
        return fig
    
    colors = get_professional_color_scheme()
    layout = get_chart_layout_config(exclude_params=['hovermode'])
    
    # Calculate ROI progression
    initial_investment = analysis_results.get('ownership_initial_investment', 100000)
    years = [flow['year'] for flow in ownership_flows]
    
    # Calculate cumulative returns and ROI
    cumulative_cash_flows = []
    roi_percentages = []
    annualized_roi = []
    
    running_cash_flow = -initial_investment  # Start with negative investment
    
    for i, flow in enumerate(ownership_flows):
        # Add annual cash flow (negative = cost)
        running_cash_flow += flow['net_cash_flow']
        cumulative_cash_flows.append(running_cash_flow)
        
        # Calculate ROI percentage
        roi_pct = (running_cash_flow / initial_investment) * 100 if initial_investment > 0 else 0
        roi_percentages.append(roi_pct)
        
        # Calculate annualized ROI with proper handling for negative cash flows
        years_elapsed = i + 1
        if years_elapsed > 0 and initial_investment > 0:
            # For positive cumulative cash flows, use compound growth formula
            if running_cash_flow > 0:
                # Standard annualized return formula: ((FV/PV)^(1/n) - 1) * 100
                annualized = ((running_cash_flow / initial_investment) ** (1/years_elapsed) - 1) * 100
            else:
                # For negative cash flows, calculate average annual loss rate
                total_return_pct = (running_cash_flow / initial_investment) * 100
                annualized = total_return_pct / years_elapsed
        else:
            annualized = 0
        
        annualized_roi.append(annualized)
    
    # Create subplot
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Cumulative Cash Flow', 'ROI Progression'),
        vertical_spacing=0.15
    )
    
    # Top chart: Cumulative cash flow
    fig.add_trace(
        go.Scatter(
            x=years, y=cumulative_cash_flows,
            mode='lines+markers',
            name='Cumulative Cash Flow',
            line=dict(color=colors['primary'], width=3),
            fill='tozeroy',
            fillcolor=f'rgba(255, 107, 107, 0.2)',
            hovertemplate='<b>Year %{x}</b><br>Cumulative Flow: %{text}<extra></extra>',
            text=[format_currency(val) for val in cumulative_cash_flows]
        ),
        row=1, col=1
    )
    
    # Bottom chart: ROI percentages
    fig.add_trace(
        go.Scatter(
            x=years, y=roi_percentages,
            mode='lines+markers',
            name='Total ROI %',
            line=dict(color=colors['success'], width=3),
            hovertemplate='<b>Year %{x}</b><br>Total ROI: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=years, y=annualized_roi,
            mode='lines+markers',
            name='Annualized ROI %',
            line=dict(color=colors['secondary'], width=2, dash='dash'),
            hovertemplate='<b>Year %{x}</b><br>Annualized ROI: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        **layout,
        title={
            'text': '<b>Return on Investment Progression</b><br><span style="font-size:14px;">Investment Performance Over Time</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        height=600,
        hovermode='x unified'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Cumulative Cash Flow ($)", tickformat=',.0f', row=1, col=1)
    fig.update_yaxes(title_text="ROI (%)", row=2, col=1)
    
    # Add break-even line
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5, row=1, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5, row=2, col=1)
    
    return fig


def create_monte_carlo_distribution_chart(
    simulation_results: List[float],
    confidence_intervals: Dict[str, float]
) -> go.Figure:
    """
    Create Monte Carlo simulation results distribution chart
    
    Args:
        simulation_results: List of NPV results from Monte Carlo simulation
        confidence_intervals: Dictionary with confidence interval values
    
    Returns:
        Plotly figure object
    """
    colors = get_professional_color_scheme()
    
    if not simulation_results:
        fig = go.Figure()
        fig.update_layout(
            title="Monte Carlo Analysis - No Data Available",
            annotations=[dict(text="No simulation results available", 
                            x=0.5, y=0.5, showarrow=False)]
        )
        return fig
    
    # Create histogram
    fig = go.Figure(data=[
        go.Histogram(
            x=simulation_results,
            nbinsx=50,
            marker_color=colors['primary'],
            opacity=0.7,
            name='NPV Distribution'
        )
    ])
    
    # Add confidence interval lines
    ci_5 = confidence_intervals.get('ci_5', np.percentile(simulation_results, 5))
    ci_95 = confidence_intervals.get('ci_95', np.percentile(simulation_results, 95))
    median = confidence_intervals.get('median', np.median(simulation_results))
    
    fig.add_vline(
        x=ci_5, line_dash="dash", line_color=colors['warning'],
        annotation_text="5th Percentile"
    )
    fig.add_vline(
        x=ci_95, line_dash="dash", line_color=colors['warning'],
        annotation_text="95th Percentile"
    )
    fig.add_vline(
        x=median, line_dash="solid", line_color=colors['success'],
        annotation_text="Median"
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': '<b>Monte Carlo Simulation Results</b><br><span style="font-size:14px;">NPV Distribution with Confidence Intervals</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        xaxis_title='NPV Difference ($)',
        yaxis_title='Frequency',
        xaxis={'tickformat': ',.0f'},
        font={'family': 'Arial, sans-serif', 'size': 12},
        height=450,
        showlegend=False
    )
    
    return fig


# Example usage and testing
if __name__ == "__main__":
    # This would be used for testing the advanced chart components
    pass