"""
Comparison Views
Professional side-by-side comparison layouts for rent vs buy analysis

This module provides comprehensive comparison views including:
- Side-by-side rent vs buy comparisons
- Financial metrics comparison grids  
- Investment timeline comparisons
- Detailed tabular presentations
- Visual indicators for better/worse outcomes
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..charts.core_charts import format_currency, get_professional_color_scheme
from ..dashboard.metric_widgets import create_kpi_card, create_comparison_metric_pair
from .comparison_tables import (
    create_annual_costs_table,
    create_cash_flow_comparison_table,
    format_comparison_table
)


def render_side_by_side_comparison(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> None:
    """
    Render complete side-by-side comparison of rent vs buy scenarios
    
    Args:
        analysis_results: Complete analysis results
        ownership_flows: Ownership cash flow data
        rental_flows: Rental cash flow data
    """
    st.subheader("🔄 Side-by-Side Comparison")
    
    # High-level comparison
    create_high_level_comparison(analysis_results)
    
    st.markdown("---")
    
    # Financial metrics comparison
    create_financial_metrics_comparison(analysis_results, ownership_flows, rental_flows)
    
    st.markdown("---")
    
    # Cost comparison
    create_cost_comparison_table(ownership_flows, rental_flows)
    
    st.markdown("---")
    
    # Investment timeline comparison
    create_investment_timeline_comparison(analysis_results, ownership_flows, rental_flows)


def create_high_level_comparison(analysis_results: Dict[str, Any]) -> None:
    """
    Create high-level comparison overview
    
    Args:
        analysis_results: Analysis results dictionary
    """
    st.markdown("#### 📊 High-Level Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### 🏠 **Ownership Scenario**")
        ownership_npv = analysis_results.get('ownership_npv', 0)
        ownership_investment = analysis_results.get('ownership_initial_investment', 0)
        
        st.markdown(f"""
        <div style="background: #F0F2F6; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #FF6B6B;">
            <div style="margin-bottom: 0.5rem;"><strong>Total NPV:</strong> {format_currency(ownership_npv)}</div>
            <div style="margin-bottom: 0.5rem;"><strong>Initial Investment:</strong> {format_currency(ownership_investment)}</div>
            <div><strong>Strategy:</strong> Build long-term equity</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("##### 🏢 **Rental Scenario**")
        rental_npv = analysis_results.get('rental_npv', 0)
        rental_investment = analysis_results.get('rental_initial_investment', 0)
        
        st.markdown(f"""
        <div style="background: #F0F2F6; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #4ECDC4;">
            <div style="margin-bottom: 0.5rem;"><strong>Total NPV:</strong> {format_currency(rental_npv)}</div>
            <div style="margin-bottom: 0.5rem;"><strong>Initial Investment:</strong> {format_currency(rental_investment)}</div>
            <div><strong>Strategy:</strong> Preserve capital flexibility</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("##### ⚖️ **Net Advantage**")
        npv_difference = analysis_results.get('npv_difference', 0)
        recommendation = analysis_results.get('recommendation', 'UNKNOWN')
        confidence = analysis_results.get('confidence', 'Low')
        
        advantage_color = "#96CEB4" if npv_difference > 0 else "#FECA57" if npv_difference < 0 else "#F0F2F6"
        winner = "Ownership" if npv_difference > 0 else "Rental" if npv_difference < 0 else "Tie"
        
        st.markdown(f"""
        <div style="background: {advantage_color}; padding: 1rem; border-radius: 0.5rem; text-align: center;">
            <div style="margin-bottom: 0.5rem; color: #262730;"><strong>{winner} Advantage</strong></div>
            <div style="margin-bottom: 0.5rem; font-size: 1.2rem; font-weight: bold; color: #262730;">{format_currency(abs(npv_difference))}</div>
            <div style="color: #262730;"><strong>{recommendation}</strong> ({confidence})</div>
        </div>
        """, unsafe_allow_html=True)


def create_financial_metrics_comparison(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> None:
    """
    Create detailed financial metrics comparison
    
    Args:
        analysis_results: Analysis results
        ownership_flows: Ownership cash flows
        rental_flows: Rental cash flows
    """
    st.markdown("#### 💰 Financial Metrics Comparison")
    
    # Create comparison metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### NPV Analysis")
        create_comparison_metric_pair(
            "Net Present Value",
            format_currency(analysis_results.get('ownership_npv', 0)),
            "Ownership",
            format_currency(analysis_results.get('rental_npv', 0)),
            "Rental",
            "first" if analysis_results.get('npv_difference', 0) > 0 else "second"
        )
    
    with col2:
        st.markdown("##### Initial Investment")
        create_comparison_metric_pair(
            "Upfront Capital Required",
            format_currency(analysis_results.get('ownership_initial_investment', 0)),
            "Ownership",
            format_currency(analysis_results.get('rental_initial_investment', 0)),
            "Rental",
            "second"  # Lower initial investment is better
        )
    
    # Terminal values comparison
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("##### Terminal Value")
        create_comparison_metric_pair(
            "End-of-Period Value (PV)",
            format_currency(analysis_results.get('ownership_terminal_value', 0)),
            "Ownership",
            format_currency(analysis_results.get('rental_terminal_value', 0)), 
            "Rental",
            "first" if analysis_results.get('ownership_terminal_value', 0) > analysis_results.get('rental_terminal_value', 0) else "second"
        )
    
    with col4:
        # Calculate average annual costs
        if ownership_flows and rental_flows:
            avg_ownership_cost = sum(abs(f['net_cash_flow']) for f in ownership_flows) / len(ownership_flows)
            avg_rental_cost = sum(abs(f['net_cash_flow']) for f in rental_flows) / len(rental_flows)
            
            st.markdown("##### Average Annual Cost")
            create_comparison_metric_pair(
                "Average Yearly Outflow",
                format_currency(avg_ownership_cost),
                "Ownership",
                format_currency(avg_rental_cost),
                "Rental", 
                "second" if avg_ownership_cost > avg_rental_cost else "first"
            )


def create_cost_comparison_table(
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> None:
    """
    Create detailed cost comparison table
    
    Args:
        ownership_flows: Ownership cash flow data
        rental_flows: Rental cash flow data
    """
    st.markdown("#### 📋 Annual Cost Comparison")
    
    if not ownership_flows or not rental_flows:
        st.warning("Cost comparison data not available")
        return
    
    # Create comparison dataframe for all analysis years
    max_years = min(len(ownership_flows), len(rental_flows))
    years = [f"Year {f['year']}" for f in ownership_flows[:max_years]]
    
    comparison_data = []
    for i in range(max_years):
        ownership_cost = abs(ownership_flows[i]['net_cash_flow'])
        rental_cost = abs(rental_flows[i]['net_cash_flow'])
        difference = ownership_cost - rental_cost
        
        comparison_data.append({
            'Year': years[i],
            'Ownership Cost': f"${ownership_cost:,.0f}",
            'Rental Cost': f"${rental_cost:,.0f}",
            'Difference': f"${difference:+,.0f}",
            'Better Option': "Rental" if difference > 0 else "Ownership"
        })
    
    df = pd.DataFrame(comparison_data)
    
    # Display table with styling
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Year": st.column_config.TextColumn("Year", width="small"),
            "Ownership Cost": st.column_config.TextColumn("Ownership Cost", width="medium"),
            "Rental Cost": st.column_config.TextColumn("Rental Cost", width="medium"),
            "Difference": st.column_config.TextColumn("Difference", width="medium"),
            "Better Option": st.column_config.TextColumn("Better Option", width="small")
        }
    )
    
    # Add summary statistics for full analysis period
    total_ownership = sum(abs(f['net_cash_flow']) for f in ownership_flows[:max_years])
    total_rental = sum(abs(f['net_cash_flow']) for f in rental_flows[:max_years])
    
    st.markdown(f"""
    **{max_years}-Year Analysis Period Summary:**
    - Total Ownership Costs: {format_currency(total_ownership)}
    - Total Rental Costs: {format_currency(total_rental)}
    - Net Difference: {format_currency(total_ownership - total_rental)} ({'Ownership costs more' if total_ownership > total_rental else 'Rental costs more'})
    """)


def create_investment_timeline_comparison(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> None:
    """
    Create investment timeline comparison chart
    
    Args:
        analysis_results: Analysis results
        ownership_flows: Ownership flows
        rental_flows: Rental flows
    """
    st.markdown("#### 📈 Investment Timeline Comparison")
    
    if not ownership_flows or not rental_flows:
        st.warning("Timeline comparison data not available")
        return
    
    colors = get_professional_color_scheme()
    
    years = [flow['year'] for flow in ownership_flows]
    
    # Calculate cumulative investments
    ownership_initial = analysis_results.get('ownership_initial_investment', 0)
    rental_initial = analysis_results.get('rental_initial_investment', 0)
    
    cumulative_ownership = [ownership_initial]
    cumulative_rental = [rental_initial]
    
    running_ownership = ownership_initial
    running_rental = rental_initial
    
    for i in range(len(ownership_flows)):
        running_ownership += abs(ownership_flows[i]['net_cash_flow'])
        running_rental += abs(rental_flows[i]['net_cash_flow'])
        cumulative_ownership.append(running_ownership)
        cumulative_rental.append(running_rental)
    
    # Create timeline chart
    fig = go.Figure()
    
    # Add ownership timeline
    fig.add_trace(go.Scatter(
        x=[0] + years,
        y=cumulative_ownership,
        mode='lines+markers',
        name='Cumulative Ownership Investment',
        line=dict(color=colors['ownership'], width=3),
        marker=dict(size=6),
        fill='tonexty' if len(fig.data) == 0 else None,
        fillcolor=f'rgba(255, 107, 107, 0.1)',
        hovertemplate='<b>Year %{x}</b><br>Cumulative Investment: %{text}<extra></extra>',
        text=[format_currency(val) for val in cumulative_ownership]
    ))
    
    # Add rental timeline
    fig.add_trace(go.Scatter(
        x=[0] + years,
        y=cumulative_rental,
        mode='lines+markers',
        name='Cumulative Rental Investment', 
        line=dict(color=colors['rental'], width=3),
        marker=dict(size=6),
        hovertemplate='<b>Year %{x}</b><br>Cumulative Investment: %{text}<extra></extra>',
        text=[format_currency(val) for val in cumulative_rental]
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': '<b>Cumulative Investment Timeline</b><br><span style="font-size:14px;">Total Capital Deployed Over Time</span>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='Year',
        yaxis_title='Cumulative Investment ($)',
        yaxis={'tickformat': ',.0f'},
        height=400,
        hovermode='x unified',
        font={'family': 'Arial, sans-serif', 'size': 12},
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add breakeven analysis
    final_ownership = cumulative_ownership[-1]
    final_rental = cumulative_rental[-1]
    total_difference = final_ownership - final_rental
    
    if total_difference > 0:
        st.markdown(f"📊 **Over {len(years)} years, ownership requires {format_currency(total_difference)} more total investment than rental.**")
    else:
        st.markdown(f"📊 **Over {len(years)} years, rental requires {format_currency(abs(total_difference))} more total investment than ownership.**")


def create_scenario_summary_table(
    analysis_results: Dict[str, Any]
) -> None:
    """
    Create summary table of scenario comparison
    
    Args:
        analysis_results: Analysis results dictionary
    """
    st.markdown("#### 📊 Scenario Summary")
    
    # Prepare summary data
    summary_data = {
        'Metric': [
            'Initial Investment Required',
            'Net Present Value',
            'Terminal Value (Present Value)',
            'Analysis Period', 
            'Cost of Capital Used',
            'Recommendation',
            'Confidence Level'
        ],
        'Ownership Scenario': [
            format_currency(analysis_results.get('ownership_initial_investment', 0)),
            format_currency(analysis_results.get('ownership_npv', 0)),
            format_currency(analysis_results.get('ownership_terminal_value', 0)),
            f"{analysis_results.get('analysis_period', 25)} years",
            f"{analysis_results.get('cost_of_capital', 8.0):.1f}%",
            analysis_results.get('recommendation', 'UNKNOWN'),
            analysis_results.get('confidence', 'Low')
        ],
        'Rental Scenario': [
            format_currency(analysis_results.get('rental_initial_investment', 0)),
            format_currency(analysis_results.get('rental_npv', 0)),
            format_currency(analysis_results.get('rental_terminal_value', 0)),
            f"{analysis_results.get('analysis_period', 25)} years",
            f"{analysis_results.get('cost_of_capital', 8.0):.1f}%",
            'Continue Renting',
            analysis_results.get('confidence', 'Low')
        ]
    }
    
    df = pd.DataFrame(summary_data)
    
    # Display styled table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Metric": st.column_config.TextColumn("Metric", width="medium"),
            "Ownership Scenario": st.column_config.TextColumn("🏠 Ownership", width="medium"),
            "Rental Scenario": st.column_config.TextColumn("🏢 Rental", width="medium")
        }
    )
    
    # Add advantage summary
    npv_advantage = analysis_results.get('npv_difference', 0)
    winner = "Ownership" if npv_advantage > 0 else "Rental"
    advantage_pct = abs(npv_advantage / max(abs(analysis_results.get('ownership_npv', 1)), abs(analysis_results.get('rental_npv', 1))) * 100)
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%); 
                padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; color: white; text-align: center;">
        <strong>Summary: {winner} provides {format_currency(abs(npv_advantage))} advantage ({advantage_pct:.1f}% better NPV)</strong>
    </div>
    """, unsafe_allow_html=True)


def render_detailed_comparison_tab(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> None:
    """
    Main function to render the complete detailed comparison tab
    
    Args:
        analysis_results: Complete analysis results
        ownership_flows: Ownership cash flow data
        rental_flows: Rental cash flow data
    """
    if not analysis_results:
        st.warning("⚠️ No analysis results available for comparison. Please complete the input sections and run the analysis.")
        return
    
    # Main comparison sections
    render_side_by_side_comparison(analysis_results, ownership_flows, rental_flows)
    
    st.markdown("---")
    
    # Scenario summary table
    create_scenario_summary_table(analysis_results)