"""
Executive Results Dashboard
Professional dashboard layout for displaying analysis results

This module provides the main dashboard components for executive-level
presentation of the real estate analysis results including:
- Executive summary dashboard layout
- Decision recommendation cards
- Key metrics display grids
- Investment comparison sections
- Professional styling and mobile responsiveness
"""

import streamlit as st
from typing import Dict, List, Optional, Any
import plotly.graph_objects as go
from datetime import datetime

from .metric_widgets import (
    create_metric_widget,
    create_status_indicator, 
    create_confidence_badge,
    create_kpi_card,
    create_comparison_metric_pair
)
from ..charts.core_charts import (
    create_npv_comparison_chart,
    create_cash_flow_timeline_chart,
    create_cost_breakdown_chart,
    create_terminal_value_chart,
    create_annual_costs_comparison_chart,
    format_currency
)
from ..charts.advanced_charts import (
    create_sensitivity_tornado_chart,
    create_break_even_chart,
    create_roi_progression_chart
)


def render_executive_summary_dashboard(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]],
    session_manager: Any
) -> None:
    """
    Render the complete executive summary dashboard
    
    Args:
        analysis_results: Complete NPV analysis results
        ownership_flows: Ownership cash flow data
        rental_flows: Rental cash flow data
        session_manager: Session management instance
    """
    # Page header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%); 
                padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 2rem; 
                color: white; text-align: center;">
        <h1 style="color: white; margin: 0;">📊 Executive Analysis Dashboard</h1>
        <p style="color: white; margin: 0; font-size: 1.1rem;">Real Estate Investment Decision Summary</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main decision recommendation
    create_decision_recommendation_card(analysis_results)
    
    st.markdown("---")
    
    # Key metrics grid
    create_key_metrics_grid(analysis_results, ownership_flows, rental_flows)
    
    st.markdown("---")
    
    # Investment comparison section
    create_investment_comparison_section(analysis_results)
    
    st.markdown("---")
    
    # Chart sections
    render_chart_sections(analysis_results, ownership_flows, rental_flows)


def create_decision_recommendation_card(analysis_results: Dict[str, Any]) -> None:
    """
    Create the main decision recommendation card
    
    Args:
        analysis_results: Analysis results with recommendation data
    """
    recommendation = analysis_results.get('recommendation', 'UNKNOWN')
    confidence = analysis_results.get('confidence', 'Low')
    npv_difference = analysis_results.get('npv_difference', 0)
    
    # Determine colors and styling based on recommendation
    if recommendation == 'BUY':
        card_color = "#96CEB4"  # Success green
        icon = "🏠"
        title = "RECOMMENDED: BUY THE PROPERTY"
    elif recommendation == 'RENT':
        card_color = "#FECA57"  # Warning yellow
        icon = "🏢"
        title = "RECOMMENDED: RENT THE PROPERTY"
    else:  # MARGINAL
        card_color = "#FF9FF3"  # Info purple
        icon = "⚖️"
        title = "MARGINAL DECISION - FURTHER ANALYSIS NEEDED"
    
    # Create recommendation card
    st.markdown(f"""
    <div style="background-color: {card_color}; padding: 2rem; border-radius: 1rem; 
                margin-bottom: 1rem; text-align: center; border: 2px solid #FFFFFF;">
        <h2 style="margin: 0; color: #262730; font-size: 1.8rem;">
            {icon} {title}
        </h2>
        <div style="margin: 1rem 0; font-size: 1.2rem; color: #262730;">
            <strong>NPV Advantage: {format_currency(abs(npv_difference))}</strong>
        </div>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.8); padding: 0.5rem 1rem; 
                        border-radius: 0.5rem; font-weight: bold;">
                Confidence: {confidence}
            </div>
            <div style="background: rgba(255,255,255,0.8); padding: 0.5rem 1rem; 
                        border-radius: 0.5rem; font-weight: bold;">
                Analysis Date: {datetime.now().strftime('%B %d, %Y')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_key_metrics_grid(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> None:
    """
    Create grid of key financial metrics
    
    Args:
        analysis_results: Analysis results
        ownership_flows: Ownership cash flows
        rental_flows: Rental cash flows
    """
    st.subheader("📈 Key Financial Metrics")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_kpi_card(
            "NPV Difference",
            format_currency(analysis_results.get('npv_difference', 0)),
            "Net advantage of recommended option",
            "positive" if analysis_results.get('npv_difference', 0) > 0 else "negative"
        )
    
    with col2:
        initial_investment = analysis_results.get('ownership_initial_investment', 0)
        create_kpi_card(
            "Initial Investment",
            format_currency(initial_investment),
            "Required upfront capital for purchase",
            "neutral"
        )
    
    with col3:
        if ownership_flows:
            annual_ownership_cost = abs(ownership_flows[0]['net_cash_flow'])
            create_kpi_card(
                "Year 1 Ownership Cost",
                format_currency(annual_ownership_cost),
                "First year total ownership costs",
                "neutral"
            )
        else:
            st.empty()
    
    with col4:
        if rental_flows:
            annual_rental_cost = abs(rental_flows[0]['net_cash_flow'])
            create_kpi_card(
                "Year 1 Rental Cost", 
                format_currency(annual_rental_cost),
                "First year rental costs",
                "neutral"
            )
        else:
            st.empty()
    
    # Second row of metrics
    st.markdown("<br>", unsafe_allow_html=True)
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        terminal_value = analysis_results.get('ownership_terminal_value', 0)
        create_kpi_card(
            "Terminal Value (PV)",
            format_currency(terminal_value),
            "Present value of terminal property equity",
            "positive" if terminal_value > 0 else "neutral"
        )
    
    with col6:
        analysis_period = analysis_results.get('analysis_period', 25)
        create_kpi_card(
            "Analysis Period",
            f"{analysis_period} Years",
            "Investment analysis time horizon",
            "neutral"
        )
    
    with col7:
        cost_of_capital = analysis_results.get('cost_of_capital', 8.0)
        create_kpi_card(
            "Cost of Capital",
            f"{cost_of_capital:.1f}%",
            "Discount rate used for NPV analysis",
            "neutral"
        )
    
    with col8:
        if ownership_flows and rental_flows:
            # Calculate average annual difference
            total_ownership = sum(abs(f['net_cash_flow']) for f in ownership_flows)
            total_rental = sum(abs(f['net_cash_flow']) for f in rental_flows) 
            avg_annual_diff = (total_ownership - total_rental) / len(ownership_flows)
            
            create_kpi_card(
                "Avg Annual Difference",
                format_currency(avg_annual_diff),
                "Average yearly cost difference",
                "positive" if avg_annual_diff < 0 else "negative"
            )
        else:
            st.empty()


def create_investment_comparison_section(analysis_results: Dict[str, Any]) -> None:
    """
    Create investment comparison section
    
    Args:
        analysis_results: Analysis results with investment data
    """
    st.subheader("💰 Investment Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏠 Ownership Scenario")
        ownership_npv = analysis_results.get('ownership_npv', 0)
        ownership_investment = analysis_results.get('ownership_initial_investment', 0)
        ownership_terminal = analysis_results.get('ownership_terminal_value', 0)
        
        st.markdown(f"""
        <div style="background: #F0F2F6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span><strong>Initial Investment:</strong></span>
                <span>{format_currency(ownership_investment)}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span><strong>Terminal Value (PV):</strong></span>
                <span>{format_currency(ownership_terminal)}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding-top: 0.5rem; 
                        border-top: 1px solid #ccc; font-weight: bold; font-size: 1.1rem;">
                <span>Total NPV:</span>
                <span style="color: #FF6B6B;">{format_currency(ownership_npv)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🏢 Rental Scenario")
        rental_npv = analysis_results.get('rental_npv', 0)
        rental_investment = analysis_results.get('rental_initial_investment', 0)
        rental_terminal = analysis_results.get('rental_terminal_value', 0)
        
        st.markdown(f"""
        <div style="background: #F0F2F6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span><strong>Initial Investment:</strong></span>
                <span>{format_currency(rental_investment)}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span><strong>Terminal Value (PV):</strong></span>
                <span>{format_currency(rental_terminal)}</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding-top: 0.5rem; 
                        border-top: 1px solid #ccc; font-weight: bold; font-size: 1.1rem;">
                <span>Total NPV:</span>
                <span style="color: #4ECDC4;">{format_currency(rental_npv)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add comparison summary
    npv_advantage = analysis_results.get('npv_difference', 0)
    better_option = "Ownership" if npv_advantage > 0 else "Rental"
    advantage_pct = abs(npv_advantage / max(abs(ownership_npv), abs(rental_npv)) * 100) if max(abs(ownership_npv), abs(rental_npv)) > 0 else 0
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%); 
                padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; color: white; text-align: center;">
        <strong>{better_option} has a {format_currency(abs(npv_advantage))} advantage ({advantage_pct:.1f}% better NPV)</strong>
    </div>
    """, unsafe_allow_html=True)


def render_chart_sections(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> None:
    """
    Render all chart sections
    
    Args:
        analysis_results: Analysis results
        ownership_flows: Ownership cash flows
        rental_flows: Rental cash flows
    """
    # Create tabs for different chart categories
    chart_tab1, chart_tab2, chart_tab3 = st.tabs([
        "📊 Core Analysis", 
        "📈 Advanced Analysis", 
        "📋 Detailed Comparisons"
    ])
    
    with chart_tab1:
        render_core_charts_section(analysis_results, ownership_flows, rental_flows)
    
    with chart_tab2:
        render_advanced_charts_section(analysis_results, ownership_flows, rental_flows)
    
    with chart_tab3:
        render_comparison_charts_section(analysis_results, ownership_flows, rental_flows)


def render_core_charts_section(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> None:
    """Render core analysis charts"""
    st.subheader("📊 Core Financial Analysis")
    
    # NPV Comparison Chart
    if analysis_results:
        try:
            npv_chart = create_npv_comparison_chart(analysis_results, show_confidence=True)
            st.plotly_chart(npv_chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating NPV comparison chart: {str(e)}")
            st.info("Please check your analysis data and try again.")
    
    # Cash Flow Timeline
    if ownership_flows and rental_flows:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📈 Cash Flow Timeline")
            try:
                cash_flow_chart = create_cash_flow_timeline_chart(ownership_flows, rental_flows)
                st.plotly_chart(cash_flow_chart, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating cash flow chart: {str(e)}")
        
        with col2:
            st.markdown("#### 🥧 Cost Breakdown")
            try:
                cost_breakdown_chart = create_cost_breakdown_chart(ownership_flows, "year1")
                st.plotly_chart(cost_breakdown_chart, use_container_width=True)
            except Exception as e:
                st.error(f"Error creating cost breakdown chart: {str(e)}")


def render_advanced_charts_section(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> None:
    """Render advanced analysis charts"""
    st.subheader("📈 Advanced Financial Analysis")
    
    # Terminal Value Progression
    if analysis_results and ownership_flows:
        try:
            terminal_chart = create_terminal_value_chart(analysis_results, ownership_flows)
            st.plotly_chart(terminal_chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating terminal value chart: {str(e)}")
    
    # ROI Progression
    if analysis_results and ownership_flows:
        try:
            roi_chart = create_roi_progression_chart(analysis_results, ownership_flows)
            st.plotly_chart(roi_chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating ROI progression chart: {str(e)}")
            st.info("ROI chart requires valid ownership cash flows and analysis results.")


def render_comparison_charts_section(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> None:
    """Render detailed comparison charts"""
    st.subheader("📋 Detailed Comparisons")
    
    # Annual Costs Comparison
    if ownership_flows and rental_flows:
        try:
            annual_costs_chart = create_annual_costs_comparison_chart(ownership_flows, rental_flows)
            st.plotly_chart(annual_costs_chart, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating annual costs comparison chart: {str(e)}")
    
    # Break-even Analysis (if data available)
    st.info("🚧 Break-even analysis and sensitivity charts will be displayed when calculation data is available")


def create_results_summary_section(analysis_results: Dict[str, Any]) -> None:
    """
    Create a concise results summary section
    
    Args:
        analysis_results: Analysis results dictionary
    """
    st.markdown("### 📋 Analysis Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        recommendation = analysis_results.get('recommendation', 'UNKNOWN')
        color = "#96CEB4" if recommendation == 'BUY' else "#FECA57" if recommendation == 'RENT' else "#FF9FF3"
        st.markdown(f"""
        <div style="background: {color}; padding: 1rem; border-radius: 0.5rem; text-align: center;">
            <h4 style="margin: 0; color: #262730;">Recommendation</h4>
            <h3 style="margin: 0.5rem 0 0 0; color: #262730;">{recommendation}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        npv_diff = analysis_results.get('npv_difference', 0)
        st.markdown(f"""
        <div style="background: #F0F2F6; padding: 1rem; border-radius: 0.5rem; text-align: center;">
            <h4 style="margin: 0; color: #262730;">NPV Advantage</h4>
            <h3 style="margin: 0.5rem 0 0 0; color: #262730;">{format_currency(abs(npv_diff))}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        confidence = analysis_results.get('confidence', 'Low')
        st.markdown(f"""
        <div style="background: #F0F2F6; padding: 1rem; border-radius: 0.5rem; text-align: center;">
            <h4 style="margin: 0; color: #262730;">Confidence Level</h4>
            <h3 style="margin: 0.5rem 0 0 0; color: #262730;">{confidence}</h3>
        </div>
        """, unsafe_allow_html=True)


def render_analysis_results_tab(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]],
    session_manager: Any
) -> None:
    """
    Main function to render the complete analysis results tab
    
    Args:
        analysis_results: Complete analysis results
        ownership_flows: Ownership cash flow data
        rental_flows: Rental cash flow data
        session_manager: Session manager instance
    """
    if not analysis_results:
        st.warning("⚠️ No analysis results available. Please complete the input sections and run the analysis.")
        return
        
    render_executive_summary_dashboard(
        analysis_results, ownership_flows, rental_flows, session_manager
    )