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
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.calculation_tooltips import (
    add_metric_with_tooltip,
    create_detailed_calculation_expander,
    display_calculation_tooltip,
    get_npv_analysis_tooltips
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
    
    # Calculation details section
    create_calculation_details_section(analysis_results, ownership_flows, rental_flows)
    
    st.markdown("---")
    
    # Investment comparison section
    create_investment_comparison_section(analysis_results)
    
    st.markdown("---")
    
    # Chart sections
    render_chart_sections(analysis_results, ownership_flows, rental_flows, session_manager)


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
    
    # Create metrics columns with calculation tooltips
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        npv_difference = analysis_results.get('npv_difference', 0)
        st.metric(
            label="NPV Difference",
            value=format_currency(npv_difference),
            delta="Recommended Option Advantage" if npv_difference != 0 else None,
            help=display_calculation_tooltip("npv_difference")
        )
    
    with col2:
        initial_investment = analysis_results.get('ownership_initial_investment', 0)
        st.metric(
            label="Initial Investment",
            value=format_currency(initial_investment),
            help=display_calculation_tooltip("initial_investment")
        )
    
    with col3:
        if ownership_flows:
            annual_ownership_cost = abs(ownership_flows[0]['net_cash_flow'])
            st.metric(
                label="Year 1 Ownership Cost",
                value=format_currency(annual_ownership_cost),
                help=display_calculation_tooltip("ownership_npv", "First year total ownership costs including mortgage, taxes, insurance, and maintenance")
            )
        else:
            st.empty()
    
    with col4:
        if rental_flows:
            # Use annual_rent to show gross rental cost, not net after tax benefits
            annual_rental_cost = rental_flows[0]['annual_rent']
            st.metric(
                label="Year 1 Rental Cost", 
                value=format_currency(annual_rental_cost),
                help=display_calculation_tooltip("annual_rent", "First year rental costs")
            )
        else:
            st.empty()
    
    # Second row of metrics
    st.markdown("<br>", unsafe_allow_html=True)
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        terminal_value = analysis_results.get('ownership_terminal_value', 0)
        st.metric(
            label="Terminal Value (PV)",
            value=format_currency(terminal_value),
            help=display_calculation_tooltip("terminal_value")
        )
    
    with col6:
        analysis_period = analysis_results.get('analysis_period', 25)
        st.metric(
            label="Analysis Period",
            value=f"{analysis_period} Years",
            help="Investment analysis time horizon. All cash flows and terminal values are calculated over this period."
        )
    
    with col7:
        cost_of_capital = analysis_results.get('cost_of_capital', 8.0)
        st.metric(
            label="Cost of Capital",
            value=f"{cost_of_capital:.1f}%",
            help=display_calculation_tooltip("present_value", "Discount rate used to calculate present value of future cash flows")
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


def create_calculation_details_section(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> None:
    """
    Create expandable section with detailed calculation explanations
    
    Args:
        analysis_results: Analysis results
        ownership_flows: Ownership cash flows
        rental_flows: Rental cash flows
    """
    # Main NPV Analysis Details
    create_detailed_calculation_expander(
        "NPV Analysis Breakdown",
        ["npv_difference", "ownership_npv", "rental_npv", "initial_investment", "terminal_value"],
        {
            "npv_difference": format_currency(analysis_results.get('npv_difference', 0)),
            "ownership_npv": format_currency(analysis_results.get('ownership_npv', 0)),
            "rental_npv": format_currency(analysis_results.get('rental_npv', 0)),
            "initial_investment": format_currency(analysis_results.get('ownership_initial_investment', 0)),
            "terminal_value": format_currency(analysis_results.get('ownership_terminal_value', 0))
        }
    )
    
    # Annual Costs Details
    if ownership_flows and rental_flows:
        first_year_ownership = ownership_flows[0]
        first_year_rental = rental_flows[0]
        
        with st.expander("📊 Annual Costs Breakdown - Calculation Details", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏠 Ownership Costs (Year 1)")
                
                mortgage_payment = first_year_ownership.get('mortgage_payment', 0)
                st.markdown(f"**Mortgage Payment**: {format_currency(mortgage_payment)}")
                st.markdown(display_calculation_tooltip("mortgage_payment"))
                
                property_taxes = first_year_ownership.get('property_taxes', 0)
                st.markdown(f"**Property Taxes**: {format_currency(property_taxes)}")
                st.markdown(display_calculation_tooltip("property_taxes"))
                
                insurance = first_year_ownership.get('insurance', 0)
                st.markdown(f"**Insurance**: {format_currency(insurance)}")
                st.markdown(display_calculation_tooltip("insurance_cost"))
                
                maintenance = first_year_ownership.get('maintenance', 0)
                st.markdown(f"**Maintenance**: {format_currency(maintenance)}")
                st.markdown(display_calculation_tooltip("maintenance_cost"))
                
                tax_benefits = first_year_ownership.get('tax_benefits', 0)
                st.markdown(f"**Tax Benefits**: {format_currency(tax_benefits)}")
                st.markdown(display_calculation_tooltip("tax_benefits"))
            
            with col2:
                st.markdown("### 🏢 Rental Costs (Year 1)")
                
                annual_rent = first_year_rental.get('annual_rent', abs(first_year_rental.get('net_cash_flow', 0)))
                st.markdown(f"**Annual Rent**: {format_currency(annual_rent)}")
                st.markdown(display_calculation_tooltip("annual_rent"))
                
                st.markdown("**Additional Costs**: Security deposit, moving costs, and rental commission are included in initial investment calculations.")


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
    rental_flows: List[Dict[str, float]],
    session_manager: Any = None
) -> None:
    """
    Render all chart sections
    
    Args:
        analysis_results: Analysis results
        ownership_flows: Ownership cash flows
        rental_flows: Rental cash flows
        session_manager: Session manager for accessing original input parameters
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
        render_advanced_charts_section(analysis_results, ownership_flows, rental_flows, session_manager)
    
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
    rental_flows: List[Dict[str, float]],
    session_manager: Any = None
) -> None:
    """Render advanced analysis charts including sensitivity analysis"""
    st.subheader("📈 Advanced Financial Analysis")
    
    # Sensitivity Analysis Section
    render_sensitivity_analysis_section(analysis_results, session_manager)
    
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


def render_sensitivity_analysis_section(analysis_results: Dict[str, Any], session_manager: Any = None) -> None:
    """
    Render two-dimensional sensitivity analysis with interactive metric selection
    
    Args:
        analysis_results: Analysis results containing input parameters
        session_manager: Session manager to access original input parameters
    """
    st.markdown("#### ⚡ Two-Dimensional Sensitivity Analysis")
    st.markdown("*Interactive analysis of how two key parameters simultaneously affect NPV*")
    
    try:
        # Import the new 2D sensitivity analysis functions
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        from calculations.two_dimensional_sensitivity import (
            calculate_2d_sensitivity_analysis,
            format_2d_sensitivity_for_streamlit,
            get_available_sensitivity_metrics
        )
        
        # Extract base parameters - use same logic as main analysis to ensure consistency
        if session_manager and session_manager.is_ready_for_analysis():
            # Use session manager to get the exact same parameters used for main analysis
            session_data = session_manager.export_session_data()
            inputs = session_data.get('inputs', {})
            
            # Use same parameter extraction logic as run_financial_analysis()
            try:
                from data.data_priority_manager import get_data_priority_manager
                priority_manager = get_data_priority_manager()
                priority_manager.bulk_update_from_session(session_data)
            except:
                priority_manager = None
            
            def get_priority_value(key, default):
                if priority_manager:
                    return priority_manager.get_value_only(key, inputs.get(key, default))
                return inputs.get(key, default)
            
            base_params = {
                # Purchase scenario parameters
                'purchase_price': inputs.get('purchase_price', 500000),
                'down_payment_pct': inputs.get('down_payment_percent', 30.0),
                'interest_rate': get_priority_value('interest_rate', 7.0),
                'loan_term': inputs.get('loan_term', 20),
                'transaction_costs': inputs.get('transaction_costs_percent', 5.0) * inputs.get('purchase_price', 0) / 100,
                
                # Rental scenario parameters  
                'current_annual_rent': inputs.get('current_annual_rent', 24000),
                'rent_increase_rate': get_priority_value('rent_increase_rate', 3.0),
                'moving_costs': inputs.get('moving_costs', 0.0),
                
                # Common parameters
                'analysis_period': inputs.get('analysis_period', 25),
                'cost_of_capital': get_priority_value('cost_of_capital', 8.0),
                
                # Property parameters
                'property_tax_rate': get_priority_value('property_tax_rate', 1.2),
                'property_tax_escalation': inputs.get('property_tax_escalation_rate', 2.0),
                'insurance_cost': inputs.get('insurance_cost', 5000),
                'annual_maintenance': inputs.get('annual_maintenance_percent', 2.0) * inputs.get('purchase_price', 0) / 100,
                'property_management': inputs.get('property_management', 0),
                
                # Advanced parameters
                'capex_reserve_rate': inputs.get('longterm_capex_reserve', 1.5),
                'obsolescence_risk_rate': inputs.get('obsolescence_risk_factor', 0.5),
                'inflation_rate': get_priority_value('inflation_rate', 3.0),
                'land_value_pct': inputs.get('land_value_percent', 25.0),
                'market_appreciation_rate': get_priority_value('market_appreciation_rate', 3.0),
                'depreciation_period': inputs.get('depreciation_period', 39),
                
                # Tax parameters
                'corporate_tax_rate': inputs.get('corporate_tax_rate', 25.0),
                'interest_deductible': inputs.get('interest_deductible', True),
                'property_tax_deductible': inputs.get('property_tax_deductible', True),
                'rent_deductible': inputs.get('rent_deductible', True),
                
                # Space improvement costs
                'space_improvement_cost': inputs.get('space_improvement_cost', 0.0),
                
                # Expansion parameters
                'future_expansion_year': inputs.get('future_expansion_year', 'Never'),
                'additional_space_needed': inputs.get('additional_space_needed', 0),
                'current_space_needed': inputs.get('current_space_needed', 0),
                'ownership_property_size': inputs.get('ownership_property_size', 0),
                'rental_property_size': inputs.get('rental_property_size', 0),
                
                # Subletting parameters
                'subletting_potential': inputs.get('subletting_potential', False),
                'subletting_rate': inputs.get('subletting_rate', 0),
                'subletting_space_sqm': inputs.get('subletting_space_sqm', 0),
                
                # Property upgrade parameters
                'property_upgrade_cycle': inputs.get('property_upgrade_cycle', 30)
            }
        else:
            # Fallback to analysis_results if session manager not available
            base_params = {
                'purchase_price': analysis_results.get('purchase_price', 500000),
                'current_annual_rent': analysis_results.get('current_annual_rent', 24000),
                'down_payment_pct': analysis_results.get('down_payment_pct', 30.0),
                'interest_rate': analysis_results.get('interest_rate', 5.0),
                'loan_term': analysis_results.get('loan_term', 20),
                'transaction_costs': analysis_results.get('transaction_costs', 25000),
                'rent_increase_rate': analysis_results.get('rent_increase_rate', 3.0),
                'analysis_period': analysis_results.get('analysis_period', 25),
                'cost_of_capital': analysis_results.get('cost_of_capital', 8.0),
                'property_tax_rate': analysis_results.get('property_tax_rate', 1.2),
                'property_tax_escalation': analysis_results.get('property_tax_escalation', 2.0),
                'insurance_cost': analysis_results.get('insurance_cost', 5000),
                'annual_maintenance': analysis_results.get('annual_maintenance', 10000),
                'property_management': analysis_results.get('property_management', 0),
                'capex_reserve_rate': analysis_results.get('capex_reserve_rate', 1.5),
                'obsolescence_risk_rate': analysis_results.get('obsolescence_risk_rate', 0.5),
                'inflation_rate': analysis_results.get('inflation_rate', 3.0),
                'land_value_pct': analysis_results.get('land_value_pct', 25.0),
                'market_appreciation_rate': analysis_results.get('market_appreciation_rate', 3.0),
                'depreciation_period': analysis_results.get('depreciation_period', 39),
                'corporate_tax_rate': analysis_results.get('corporate_tax_rate', 25.0),
                'interest_deductible': analysis_results.get('interest_deductible', True),
                'property_tax_deductible': analysis_results.get('property_tax_deductible', True),
                'rent_deductible': analysis_results.get('rent_deductible', True),
                'moving_costs': analysis_results.get('moving_costs', 0.0),
                'space_improvement_cost': analysis_results.get('space_improvement_cost', 0.0),
                'future_expansion_year': analysis_results.get('future_expansion_year', 'Never'),
                'additional_space_needed': analysis_results.get('additional_space_needed', 0),
                'current_space_needed': analysis_results.get('current_space_needed', 0),
                'ownership_property_size': analysis_results.get('ownership_property_size', 0),
                'rental_property_size': analysis_results.get('rental_property_size', 0),
                'subletting_potential': analysis_results.get('subletting_potential', False),
                'subletting_rate': analysis_results.get('subletting_rate', 0),
                'subletting_space_sqm': analysis_results.get('subletting_space_sqm', 0),
                'property_upgrade_cycle': analysis_results.get('property_upgrade_cycle', 30)
            }
        
        # Check if we have minimum required parameters
        if not all(base_params[key] for key in ['purchase_price', 'current_annual_rent']):
            st.warning("⚠️ Sensitivity analysis requires purchase price and annual rent to be set.")
            return
        
        # Get available metrics for selection
        available_metrics = get_available_sensitivity_metrics()
        metric_options = list(available_metrics.values())
        metric_keys = list(available_metrics.keys())
        
        # Interactive controls for 2D sensitivity analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # X-axis metric selection
            x_metric_display = st.selectbox(
                "X-Axis (Column Headers)",
                options=metric_options,
                index=1,  # Default to Interest Rate
                key="x_metric_selection",
                help="Choose the metric to vary along the table columns"
            )
            x_metric = metric_keys[metric_options.index(x_metric_display)]
        
        with col2:
            # Y-axis metric selection
            y_metric_display = st.selectbox(
                "Y-Axis (Row Headers)",
                options=metric_options,
                index=3,  # Default to Market Appreciation Rate
                key="y_metric_selection",
                help="Choose the metric to vary along the table rows"
            )
            y_metric = metric_keys[metric_options.index(y_metric_display)]
        
        # Validate metric selection
        if x_metric == y_metric:
            st.error("❌ Please select different metrics for X and Y axes")
            return
        
        # Range configuration
        st.markdown("**Analysis Ranges**")
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown(f"*{x_metric_display} range: -1.5% to +1.5%*")
            
        with col4:
            st.markdown(f"*{y_metric_display} range: -1.5% to +1.5%*")
        
        # Run 2D sensitivity analysis
        if st.button("🔍 Run 2D Sensitivity Analysis", type="primary", key="run_2d_sensitivity"):
            with st.spinner("Calculating two-dimensional sensitivity table..."):
                try:
                    # Calculate 2D sensitivity analysis
                    sensitivity_result = calculate_2d_sensitivity_analysis(
                        base_params=base_params,
                        x_metric=x_metric,
                        y_metric=y_metric,
                        x_range=[-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5],
                        y_range=[-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
                    )
                    
                    if sensitivity_result:
                        # Format for Streamlit display
                        formatted_result = format_2d_sensitivity_for_streamlit(sensitivity_result)
                        
                        # Display the table
                        st.markdown("### 📊 NPV Sensitivity Table")
                        st.markdown(f"**{formatted_result['y_metric_display']} vs {formatted_result['x_metric_display']}**")
                        
                        # Create column configuration
                        column_config = {'y_label': f"{formatted_result['y_metric_display']}", 'y_change': 'Change'}
                        for i in range(formatted_result['num_columns']):
                            column_config[f'col_{i}'] = formatted_result['x_headers'][i]
                        
                        # Prepare dataframe for display
                        import pandas as pd
                        display_data = []
                        
                        for row in formatted_result['table_data']:
                            display_row = {
                                f"{formatted_result['y_metric_display']}": f"{row['y_label']} {row['y_change']}",
                            }
                            for i in range(formatted_result['num_columns']):
                                header = f"{formatted_result['x_headers'][i]}"
                                if i < len(formatted_result['x_change_indicators']):
                                    header += f" {formatted_result['x_change_indicators'][i]}"
                                display_row[header] = row[f'col_{i}']
                            display_data.append(display_row)
                        
                        df = pd.DataFrame(display_data)
                        
                        # Create styling function for color coding based on NPV values
                        def style_npv_values(val, raw_values, col_name):
                            """Apply color styling based on NPV values"""
                            if col_name in raw_values:
                                raw_val = raw_values[col_name]
                                if raw_val > 0:
                                    # Positive NPV (ownership advantage) - green background
                                    return 'background-color: #D5F4E6; color: #00B894; font-weight: bold;'
                                elif raw_val < 0:
                                    # Negative NPV (rental advantage) - light red background  
                                    return 'background-color: #FADBD8; color: #E74C3C; font-weight: bold;'
                                else:
                                    # Zero NPV - neutral
                                    return 'color: #2D3436; font-weight: bold;'
                            return ''
                        
                        # Create a styled dataframe
                        styled_df = df.copy()
                        
                        # Apply styling using st.dataframe with custom CSS
                        try:
                            # Create styling for each row based on raw NPV values
                            def highlight_cells(row):
                                styles = [''] * len(row)
                                
                                # Find the corresponding raw data for this row
                                row_index = styled_df.index[styled_df[f"{formatted_result['y_metric_display']}"] == row[f"{formatted_result['y_metric_display']}"]].tolist()
                                if row_index:
                                    raw_row_data = formatted_result['table_data'][row_index[0]]
                                    
                                    # Style NPV value columns
                                    for i in range(formatted_result['num_columns']):
                                        col_header = f"{formatted_result['x_headers'][i]}"
                                        if i < len(formatted_result['x_change_indicators']):
                                            col_header += f" {formatted_result['x_change_indicators'][i]}"
                                        
                                        if col_header in row.index:
                                            col_idx = row.index.get_loc(col_header)
                                            raw_val = raw_row_data[f'col_{i}_raw']
                                            
                                            if raw_val > 0:
                                                # Positive NPV (ownership advantage) - green
                                                styles[col_idx] = 'background-color: #D5F4E6; color: #00B894; font-weight: bold;'
                                            elif raw_val < 0:
                                                # Negative NPV (rental advantage) - light red
                                                styles[col_idx] = 'background-color: #FADBD8; color: #E74C3C; font-weight: bold;'
                                            else:
                                                # Zero NPV - neutral
                                                styles[col_idx] = 'color: #2D3436; font-weight: bold;'
                                
                                return styles
                            
                            # Apply the styling
                            styled_dataframe = styled_df.style.apply(highlight_cells, axis=1)
                            
                            # Display the styled table
                            st.dataframe(
                                styled_dataframe,
                                use_container_width=True,
                                hide_index=True
                            )
                            
                        except Exception as e:
                            # Fallback to regular table if styling fails
                            st.dataframe(
                                df,
                                use_container_width=True,
                                hide_index=True
                            )
                            st.info("💡 **Color Legend**: Green values favor ownership, red values favor rental")
                        
                        # Color legend
                        st.markdown("### 🎨 Color Legend")
                        col_legend1, col_legend2 = st.columns(2)
                        
                        with col_legend1:
                            st.markdown("""
                            <div style="background-color: #D5F4E6; color: #00B894; padding: 8px; border-radius: 4px; text-align: center; font-weight: bold; margin-bottom: 8px;">
                                🟢 Positive NPV - Ownership Advantage
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_legend2:
                            st.markdown("""
                            <div style="background-color: #FADBD8; color: #E74C3C; padding: 8px; border-radius: 4px; text-align: center; font-weight: bold; margin-bottom: 8px;">
                                🔴 Negative NPV - Rental Advantage
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Analysis insights
                        st.markdown("### 🎯 Sensitivity Insights")
                        
                        col5, col6, col7 = st.columns(3)
                        
                        with col5:
                            st.metric(
                                "Base Case NPV",
                                formatted_result['base_npv'],
                                help="NPV difference with current parameter values"
                            )
                        
                        with col6:
                            st.metric(
                                "Table Size",
                                formatted_result['table_size'],
                                help="Number of parameter combinations analyzed"
                            )
                        
                        with col7:
                            st.metric(
                                "Calculation Time",
                                formatted_result['calculation_time'],
                                help="Time taken to compute all combinations"
                            )
                        
                        # Interpretation guide
                        with st.expander("📖 How to Read This Table", expanded=False):
                            st.markdown(f"""
                            **Understanding the Sensitivity Table:**
                            
                            • **0% Column/Row**: Shows actual parameter values used in your analysis
                            • **Positive Changes**: Parameter increases (e.g., +1% = 1 percentage point higher)
                            • **Negative Changes**: Parameter decreases (e.g., -1% = 1 percentage point lower)
                            • **Values in Table**: Show how NPV difference changes from the base case
                            • **Green Values**: Favorable changes that improve the recommended option
                            • **Red Values**: Unfavorable changes that worsen the recommended option
                            
                            **Example Interpretation:**
                            If your base case recommends "BUY" and you see a value of "+$50K" at the intersection 
                            of "+1% {y_metric_display}" and "+1% {x_metric_display}", this means that if both 
                            parameters increase by 1 percentage point, the NPV advantage of buying increases by $50K.
                            """)
                        
                        # Store results in session state for potential export
                        st.session_state['sensitivity_2d_results'] = {
                            'raw_result': sensitivity_result,
                            'formatted_result': formatted_result,
                            'x_metric': x_metric,
                            'y_metric': y_metric
                        }
                        
                        st.success("✅ Two-dimensional sensitivity analysis completed successfully!")
                    
                    else:
                        st.error("❌ Failed to calculate sensitivity analysis. Please check your parameters.")
                        
                except Exception as e:
                    st.error(f"❌ Error calculating sensitivity analysis: {str(e)}")
                    st.info("Please check your input parameters and try again.")
        
        # Show current selection summary
        st.markdown("---")
        st.markdown("**Current Selection:**")
        col8, col9 = st.columns(2)
        
        with col8:
            st.info(f"**X-Axis**: {x_metric_display}")
            if x_metric in base_params:
                current_x_value = base_params[x_metric]
                if x_metric in ['interest_rate', 'rent_increase_rate', 'market_appreciation_rate', 'inflation_rate']:
                    st.write(f"Current value: {current_x_value:.1f}%")
                else:
                    st.write(f"Current value: ${current_x_value:,.0f}")
        
        with col9:
            st.info(f"**Y-Axis**: {y_metric_display}")
            if y_metric in base_params:
                current_y_value = base_params[y_metric]
                if y_metric in ['interest_rate', 'rent_increase_rate', 'market_appreciation_rate', 'inflation_rate']:
                    st.write(f"Current value: {current_y_value:.1f}%")
                else:
                    st.write(f"Current value: ${current_y_value:,.0f}")
        
        # Show previously calculated results if available
        if 'sensitivity_2d_results' in st.session_state:
            prev_results = st.session_state['sensitivity_2d_results']
            if (prev_results['x_metric'] == x_metric and prev_results['y_metric'] == y_metric):
                st.info("📊 Results shown above are current. Click 'Run 2D Sensitivity Analysis' to recalculate if you've changed inputs.")
            else:
                st.info("📊 Results from a previous analysis are stored. Click 'Run 2D Sensitivity Analysis' to analyze the newly selected metrics.")
        
    except ImportError as e:
        st.error(f"❌ Two-dimensional sensitivity analysis not available: {str(e)}")
        st.info("🚧 2D sensitivity analysis requires the updated calculation modules.")
    except Exception as e:
        st.error(f"❌ Error loading sensitivity analysis: {str(e)}")
        st.info("Please check your analysis parameters and try again.")


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