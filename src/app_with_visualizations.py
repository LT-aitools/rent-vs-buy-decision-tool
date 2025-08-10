"""
Real Estate Rent vs. Buy Decision Tool
Enhanced Main Streamlit Application with Comprehensive Visualizations

Complete implementation with professional input forms, validation,
executive dashboard, interactive charts, and comprehensive analysis presentation.

This enhanced version includes:
- Executive summary dashboard with key metrics
- Interactive charts for NPV comparison, cash flows, and cost breakdowns
- Advanced visualizations for sensitivity analysis
- Professional comparison tables and views
- Mobile-responsive design for executive presentations

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

import streamlit as st
from datetime import datetime
import sys
import os
import pandas as pd
from typing import Dict, List, Any, Optional

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom UI components
try:
    from components import (
        initialize_professional_layout,
        render_all_input_forms,
        initialize_session,
        get_session_manager,
        create_info_box,
        render_footer,
        # Visualization components
        render_executive_summary_dashboard,
        render_analysis_results_tab,
        render_detailed_comparison_tab,
        create_decision_recommendation_card,
        create_results_summary_section
    )
    
    # Import calculation engine
    from calculations import (
        calculate_npv_comparison,
        calculate_ownership_cash_flows,
        calculate_rental_cash_flows,
        calculate_break_even_analysis,
        calculate_sensitivity_analysis
    )
    
except ImportError as e:
    st.error(f"Error importing components: {e}")
    st.stop()


def run_financial_analysis(session_manager) -> tuple[Optional[Dict], Optional[List], Optional[List]]:
    """
    Run the complete financial analysis using session data
    
    Args:
        session_manager: Session manager instance with input data
        
    Returns:
        Tuple of (analysis_results, ownership_flows, rental_flows)
    """
    try:
        # Extract parameters from session
        if not session_manager.is_ready_for_analysis():
            return None, None, None
        
        # Get all session data for analysis
        session_data = session_manager.export_session_data()
        
        # Extract all required parameters from session_data
        analysis_params = {
            # Purchase scenario parameters
            'purchase_price': session_data.get('purchase_price', session_data.get('inputs', {}).get('purchase_price')),
            'down_payment_pct': session_data.get('down_payment_percent', session_data.get('inputs', {}).get('down_payment_percent', 30.0)),
            'interest_rate': session_data.get('interest_rate', session_data.get('inputs', {}).get('interest_rate', 5.0)),
            'loan_term': session_data.get('loan_term', session_data.get('inputs', {}).get('loan_term', 20)),
            'transaction_costs': session_data.get('transaction_costs_percent', session_data.get('inputs', {}).get('transaction_costs_percent', 5.0)) * session_data.get('purchase_price', session_data.get('inputs', {}).get('purchase_price', 0)) / 100,
            
            # Rental scenario parameters  
            'current_annual_rent': session_data.get('current_annual_rent', session_data.get('inputs', {}).get('current_annual_rent')),
            'rent_increase_rate': session_data.get('rent_increase_rate', session_data.get('inputs', {}).get('rent_increase_rate', 3.0)),
            
            # Common parameters
            'analysis_period': session_data.get('analysis_period', session_data.get('inputs', {}).get('analysis_period', 25)),
            'cost_of_capital': session_data.get('cost_of_capital', session_data.get('inputs', {}).get('cost_of_capital', 8.0)),
            
            # Property parameters
            'property_tax_rate': session_data.get('property_tax_rate', session_data.get('inputs', {}).get('property_tax_rate', 1.2)),
            'property_tax_escalation': session_data.get('property_tax_escalation_rate', session_data.get('inputs', {}).get('property_tax_escalation_rate', 2.0)),
            'insurance_cost': session_data.get('insurance_cost', session_data.get('inputs', {}).get('insurance_cost', 5000)),
            'annual_maintenance': session_data.get('annual_maintenance_percent', session_data.get('inputs', {}).get('annual_maintenance_percent', 2.0)) * session_data.get('purchase_price', session_data.get('inputs', {}).get('purchase_price', 0)) / 100,
            'property_management': session_data.get('property_management', session_data.get('inputs', {}).get('property_management', 0)),
            
            # Advanced parameters
            'capex_reserve_rate': session_data.get('longterm_capex_reserve', session_data.get('inputs', {}).get('longterm_capex_reserve', 1.5)),
            'obsolescence_risk_rate': session_data.get('obsolescence_risk_factor', session_data.get('inputs', {}).get('obsolescence_risk_factor', 0.5)),
            'inflation_rate': session_data.get('inflation_rate', session_data.get('inputs', {}).get('inflation_rate', 3.0)),
            'land_value_pct': session_data.get('land_value_percent', session_data.get('inputs', {}).get('land_value_percent', 25.0)),
            'market_appreciation_rate': session_data.get('market_appreciation_rate', session_data.get('inputs', {}).get('market_appreciation_rate', 3.0)),
            'depreciation_period': session_data.get('depreciation_period', session_data.get('inputs', {}).get('depreciation_period', 39)),
            
            # Tax parameters
            'corporate_tax_rate': session_data.get('corporate_tax_rate', session_data.get('inputs', {}).get('corporate_tax_rate', 25.0)),
            'interest_deductible': session_data.get('interest_deductible', session_data.get('inputs', {}).get('interest_deductible', True)),
            'property_tax_deductible': session_data.get('property_tax_deductible', session_data.get('inputs', {}).get('property_tax_deductible', True))
        }
        
        # Validate critical parameters before analysis
        critical_params = ['purchase_price', 'current_annual_rent']
        for param in critical_params:
            if not analysis_params.get(param):
                raise ValueError(f"Critical parameter '{param}' is missing or zero. Please complete all required inputs.")
        
        # Run NPV analysis
        analysis_results = calculate_npv_comparison(**analysis_params)
        
        # Debug: Log analysis parameters
        st.write(f"Debug - Current Annual Rent Parameter: {analysis_params['current_annual_rent']}")
        
        # Calculate detailed cash flows
        ownership_flows = calculate_ownership_cash_flows(
            purchase_price=analysis_params['purchase_price'],
            down_payment_pct=analysis_params['down_payment_pct'],
            interest_rate=analysis_params['interest_rate'],
            loan_term=analysis_params['loan_term'],
            analysis_period=analysis_params['analysis_period'],
            property_tax_rate=analysis_params['property_tax_rate'],
            property_tax_escalation=analysis_params['property_tax_escalation'],
            insurance_cost=analysis_params['insurance_cost'],
            annual_maintenance=analysis_params['annual_maintenance'],
            property_management=analysis_params['property_management'],
            capex_reserve_rate=analysis_params['capex_reserve_rate'],
            obsolescence_risk_rate=analysis_params['obsolescence_risk_rate'],
            inflation_rate=analysis_params['inflation_rate'],
            land_value_pct=analysis_params['land_value_pct'],
            market_appreciation_rate=analysis_params['market_appreciation_rate'],
            depreciation_period=analysis_params['depreciation_period'],
            corporate_tax_rate=analysis_params['corporate_tax_rate'],
            interest_deductible=analysis_params['interest_deductible'],
            property_tax_deductible=analysis_params['property_tax_deductible'],
            transaction_costs=analysis_params['transaction_costs']
        )
        
        rental_flows = calculate_rental_cash_flows(
            current_annual_rent=analysis_params['current_annual_rent'],
            rent_increase_rate=analysis_params['rent_increase_rate'],
            analysis_period=analysis_params['analysis_period'],
            corporate_tax_rate=analysis_params['corporate_tax_rate']
        )
        
        # Debug: Log first year rental flow
        if rental_flows:
            st.write(f"Debug - Year 1 Rental Flow: {rental_flows[0]}")
        
        return analysis_results, ownership_flows, rental_flows
        
    except Exception as e:
        st.error(f"Error running financial analysis: {str(e)}")
        # Add debugging information
        st.error(f"Session data keys: {list(session_data.keys()) if session_data else 'No session data'}")
        st.error(f"Analysis params: {analysis_params}")
        return None, None, None


def render_dashboard_tab():
    """Render the main dashboard with input forms"""
    st.markdown("## 📊 Input Dashboard")
    st.markdown("*Complete all input sections below to enable financial analysis*")
    
    # Instructions for sidebar access
    st.info("👈 **Use the sidebar on the left** to input your property and financial data.")
    
    # Render input forms in sidebar
    with st.sidebar:
        try:
            inputs_valid = render_all_input_forms()
        except Exception as e:
            st.error("⚠️ **Loading Error** - Please refresh the page")
            inputs_valid = False
    
    # Main dashboard area
    try:
        session_manager = get_session_manager()
    except Exception as e:
        st.error(f"⚠️ **Session Error**: {str(e)}")
        st.info("🔄 Please refresh the page to continue")
        return
    
    if inputs_valid:
        st.success("✅ **All inputs are valid and ready for analysis!**")
        
        # Display input summary in main area
        st.markdown("### 📋 Analysis Summary")
        summary = session_manager.get_input_summary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            for section, data in list(summary.items())[:2]:
                st.markdown(f"**{section}**")
                for key, value in data.items():
                    st.write(f"• {key}: {value}")
                st.markdown("")
        
        with col2:
            for section, data in list(summary.items())[2:]:
                st.markdown(f"**{section}**")
                for key, value in data.items():
                    st.write(f"• {key}: {value}")
                st.markdown("")
        
        # Run Analysis Button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 **Run Financial Analysis**", type="primary", use_container_width=True):
                with st.spinner("Running comprehensive financial analysis..."):
                    # Store analysis results in session state
                    analysis_results, ownership_flows, rental_flows = run_financial_analysis(session_manager)
                    if analysis_results:
                        st.session_state['analysis_results'] = analysis_results
                        st.session_state['ownership_flows'] = ownership_flows
                        st.session_state['rental_flows'] = rental_flows
                        # Clear demo data flag to ensure we're showing real data
                        if 'using_demo_data' in st.session_state:
                            del st.session_state['using_demo_data']
                        st.success("✅ Analysis completed successfully!")
                        st.rerun()
        
        # Show analysis results if available
        if 'analysis_results' in st.session_state:
            st.markdown("---")
            st.markdown("### 📈 Analysis Results Preview")
            create_results_summary_section(st.session_state['analysis_results'])
            
            st.info("📊 **Go to the 'Analysis Results' tab to view detailed visualizations and charts.**")
        
        # Show completion status
        try:
            completion = session_manager.get_completion_percentage()
            st.progress(completion / 100, text=f"Setup Complete: {completion:.0f}%")
        except Exception:
            st.progress(0.0, text="Setup Complete: 0%")
        
    else:
        # Show what's needed
        st.markdown("### 📝 Getting Started")
        
        create_info_box(
            "Complete the input sections in the sidebar to begin your rent vs buy analysis. "
            "All required fields must be filled with valid data.",
            "info"
        )
        
        # Show completion progress
        try:
            completion = session_manager.get_completion_percentage()
            st.progress(completion / 100, text=f"Input Progress: {completion:.0f}%")
        except Exception:
            st.progress(0.0, text="Input Progress: 0%")
        
        # Development status
        st.markdown("### 🛠 Development Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Week 1", "UI Components", "✅ Complete")
        
        with col2:
            st.metric("Week 2", "Calculations", "✅ Complete")
        
        with col3:
            st.metric("Week 3", "Visualizations", "✅ Complete")


def render_analysis_tab():
    """Render comprehensive analysis results with visualizations"""
    session_manager = get_session_manager()
    
    # Check if we have real analysis results
    if 'analysis_results' not in st.session_state:
        st.warning("⚠️ **No analysis results available.** Please complete the input sections in the Dashboard tab and run the analysis.")
        
        # Check if inputs are ready for analysis
        if session_manager.is_ready_for_analysis():
            st.info("✅ **All inputs are complete!** Go to the Dashboard tab and click 'Run Financial Analysis' to generate real results.")
        else:
            completion = session_manager.get_completion_percentage()
            st.info(f"📝 **Input Progress: {completion:.0f}%** - Complete all required sections to enable analysis.")
        
        # Provide demo data option for visualization testing (less prominent)
        with st.expander("🧪 **Demo Data for Testing** (Click to expand)"):
            st.markdown("*This loads sample data for testing the visualization system only.*")
            if st.button("Load Demo Visualization Data", type="secondary", use_container_width=True):
                # Create demo analysis results
                demo_results = {
                    'ownership_npv': 450000,
                    'rental_npv': 325000,
                    'npv_difference': 125000,
                    'ownership_initial_investment': 175000,
                    'rental_initial_investment': 5000,
                    'ownership_terminal_value': 180000,
                    'rental_terminal_value': 5000,
                    'recommendation': 'BUY',
                    'confidence': 'High',
                    'analysis_period': 25,
                    'cost_of_capital': 8.0
                }
                
                # Create demo cash flows
                demo_ownership_flows = []
                demo_rental_flows = []
                
                for year in range(1, 26):
                    # Demo ownership flow
                    demo_ownership_flows.append({
                        'year': year,
                        'mortgage_payment': 35000 + (year * 100),
                        'property_taxes': 6000 + (year * 120),
                        'insurance': 5000 + (year * 150),
                        'maintenance': 10000 + (year * 300),
                        'property_management': 0,
                        'capex_reserve': 3000,
                        'obsolescence_cost': 1000,
                        'mortgage_interest': max(25000 - (year * 800), 5000),
                        'tax_benefits': 15000 - (year * 200),
                        'net_cash_flow': -(45000 + year * 500),
                        'remaining_loan_balance': max(350000 - (year * 15000), 0)
                    })
                    
                    # Demo rental flow
                    demo_rental_flows.append({
                        'year': year,
                        'annual_rent': 24000 * (1.03 ** (year-1)),
                        'tax_benefits': 6000,
                        'net_cash_flow': -(18000 * (1.03 ** (year-1)))
                    })
                
                st.session_state['analysis_results'] = demo_results
                st.session_state['ownership_flows'] = demo_ownership_flows
                st.session_state['rental_flows'] = demo_rental_flows
                st.session_state['using_demo_data'] = True
                
                st.success("✅ Demo data loaded! View the analysis below.")
                st.rerun()
        return
    
    # Check if we're using demo data and warn the user
    if st.session_state.get('using_demo_data', False):
        st.warning("⚠️ **Currently displaying demo data for testing.** To see real analysis results, complete your inputs in the Dashboard tab and run the analysis.")
        if st.button("🔄 Clear Demo Data and Use Real Analysis", type="primary"):
            # Clear demo data flags
            if 'using_demo_data' in st.session_state:
                del st.session_state['using_demo_data']
            if 'analysis_results' in st.session_state:
                del st.session_state['analysis_results']
            if 'ownership_flows' in st.session_state:
                del st.session_state['ownership_flows']
            if 'rental_flows' in st.session_state:
                del st.session_state['rental_flows']
            st.rerun()
    else:
        # Display marker for real data
        st.success("✅ **Displaying Real Analysis Results** based on your input data.")
    
    # Render full analysis results dashboard
    render_analysis_results_tab(
        st.session_state['analysis_results'],
        st.session_state['ownership_flows'],
        st.session_state['rental_flows'],
        session_manager
    )


def render_comparison_tab():
    """Render detailed comparison views"""
    if 'analysis_results' not in st.session_state:
        st.warning("⚠️ **No analysis results available for comparison.** Please run the analysis first in the Dashboard tab.")
        return
    
    render_detailed_comparison_tab(
        st.session_state['analysis_results'],
        st.session_state['ownership_flows'],
        st.session_state['rental_flows']
    )


def render_export_tab():
    """Render export and sharing functionality"""
    st.markdown("## 📤 Export & Sharing")
    
    session_manager = get_session_manager()
    
    if not session_manager.is_ready_for_analysis():
        create_info_box(
            "Complete all required input sections to enable export functionality.",
            "warning"
        )
        return
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Export Current Analysis")
        
        # Export session data as JSON
        export_data = session_manager.export_session_data()
        
        st.download_button(
            label="📄 Download Input Data (JSON)",
            data=str(export_data),
            file_name=f"real_estate_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="Download all input parameters for backup or sharing"
        )
        
        # Export analysis results if available
        if 'analysis_results' in st.session_state:
            results_data = {
                'analysis_results': st.session_state['analysis_results'],
                'input_parameters': export_data,
                'generated_date': datetime.now().isoformat()
            }
            
            st.download_button(
                label="📈 Export Analysis Results (JSON)",
                data=str(results_data),
                file_name=f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                help="Download complete analysis results and charts data"
            )
        else:
            st.button(
                label="📈 Export Analysis Report",
                disabled=True,
                help="Run analysis first to enable report export"
            )
    
    with col2:
        st.markdown("### 🔄 Session Management")
        
        if st.button("🔄 Reset All Inputs", type="secondary"):
            session_manager.reset_session()
            # Clear analysis results
            if 'analysis_results' in st.session_state:
                del st.session_state['analysis_results']
            if 'ownership_flows' in st.session_state:
                del st.session_state['ownership_flows']
            if 'rental_flows' in st.session_state:
                del st.session_state['rental_flows']
            st.success("✅ All inputs and results have been reset")
            st.rerun()
        
        st.markdown("**Import Analysis:**")
        uploaded_file = st.file_uploader(
            "Upload JSON file",
            type=['json'],
            help="Upload a previously exported analysis JSON file"
        )
        
        if uploaded_file is not None:
            try:
                import json
                data = json.load(uploaded_file)
                if session_manager.import_session_data(data):
                    st.success("✅ Analysis imported successfully!")
                    st.rerun()
                else:
                    st.error("❌ Error importing analysis data")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")


def render_help_tab():
    """Render help and documentation"""
    st.markdown("## ❓ Help & Documentation")
    
    # Quick start guide
    st.markdown("### 🚀 Quick Start Guide")
    
    with st.expander("📋 How to Use This Tool", expanded=True):
        st.markdown("""
        1. **Complete Input Sections**: Fill out all required fields in the sidebar sections
        2. **Review Validation**: Address any validation warnings or errors  
        3. **Run Analysis**: Click 'Run Financial Analysis' once inputs are complete
        4. **Review Results**: Examine charts and visualizations in the 'Analysis Results' tab
        5. **Compare Options**: Use 'Detailed Comparison' tab for side-by-side analysis
        6. **Export Report**: Download results and charts from the 'Export & Share' tab
        """)
    
    with st.expander("📊 Understanding the Visualizations"):
        st.markdown("""
        **Executive Dashboard**: Key metrics and decision recommendation with confidence levels
        
        **NPV Comparison Chart**: Side-by-side net present value comparison with clear winner
        
        **Cash Flow Timeline**: Year-by-year cost comparison showing when ownership breaks even
        
        **Cost Breakdown**: Detailed breakdown of ownership costs (mortgage, taxes, maintenance, etc.)
        
        **Terminal Value Chart**: Property value appreciation and equity building over time
        
        **Comparison Tables**: Detailed tabular analysis with visual indicators for better options
        """)
    
    with st.expander("💡 Input Field Explanations"):
        st.markdown("""
        **Project Information**: Basic details about your analysis project
        
        **Property & Market**: Property specifications and market assumptions
        
        **Purchase Parameters**: All costs and financing terms for buying the property
        
        **Rental Parameters**: Current rent and rental cost assumptions
        
        **Operational Parameters**: Business growth, expansion, and operational assumptions
        
        **Tax & Accounting**: Tax rates and deductibility assumptions
        """)
    
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Common Issues:**
        - *Validation errors*: Check that all required fields are filled with valid values
        - *Missing calculations*: Ensure all required sections are marked as complete
        - *Chart not displaying*: Try running the analysis again or refresh the page
        - *Performance issues*: Clear browser cache or refresh the page
        
        **Getting Help:**
        - Review field tooltips (❓ icons) for detailed explanations
        - Check validation messages for specific guidance
        - Use the demo data feature to test visualizations
        - Refer to the Business PRD for methodology details
        """)
    
    # Technical information
    st.markdown("### 📚 Technical Documentation")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Analysis Features:**")
        st.markdown("✅ NPV Analysis with Hold-Forever Strategy")
        st.markdown("✅ Interactive Charts and Visualizations") 
        st.markdown("✅ Executive Dashboard with Key Metrics")
        st.markdown("✅ Detailed Cost Breakdown Analysis")
        st.markdown("✅ Mobile-Responsive Design")
    
    with col2:
        st.markdown("**Visualization Features:**")
        st.markdown("📊 Professional Executive Charts")
        st.markdown("📈 Interactive Timeline Analysis")
        st.markdown("📋 Detailed Comparison Tables")
        st.markdown("💰 Terminal Value Progression")
        st.markdown("🎯 Decision Recommendation Cards")


def main():
    """Main application entry point with comprehensive visualization system"""
    
    # Initialize page config FIRST (must be first Streamlit command)
    st.set_page_config(
        page_title="Real Estate Decision Tool - with Visualizations",
        page_icon="🏢", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Then initialize other components
    initialize_session()
    
    # Apply professional styling
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
    }
    
    /* Custom styling for charts and visualizations */
    .js-plotly-plot .plotly .modebar {
        right: 10px !important;
    }
    
    /* Enhanced metric cards */
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Enhanced Header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%); 
                padding: 1.5rem 2rem; border-radius: 0.5rem; margin-bottom: 2rem; 
                color: white; text-align: center;">
        <h1 style="color: white; margin: 0;">🏢 Real Estate Decision Tool</h1>
        <p style="color: white; margin: 0; font-size: 1.1rem;">Professional Investment Strategy Analysis with Interactive Visualizations</p>
        <p style="color: white; margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">Executive Dashboard • Interactive Charts • Comprehensive Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Tab navigation with new analysis tab
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Analysis Dashboard", 
        "📈 Analysis Results", 
        "📋 Detailed Comparison",
        "📤 Export & Share", 
        "❓ Help & Documentation"
    ])
    
    with tab1:
        render_dashboard_tab()
    
    with tab2:
        render_analysis_tab()
    
    with tab3:
        render_comparison_tab()
    
    with tab4:
        render_export_tab()
    
    with tab5:
        render_help_tab()
    
    # Professional footer
    render_footer()


if __name__ == "__main__":
    main()