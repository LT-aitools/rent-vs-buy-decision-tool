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
import logging
from typing import Dict, List, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

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
    
    # Import new 2D sensitivity analysis
    from calculations.two_dimensional_sensitivity import (
        calculate_2d_sensitivity_analysis,
        format_2d_sensitivity_for_streamlit,
        get_available_sensitivity_metrics
    )
    
except ImportError as e:
    st.error(f"Error importing components: {e}")
    st.stop()


def _safe_get_rent_increase_rate(priority_manager, inputs):
    """
    Safely extract rent_increase_rate with extensive error handling
    """
    try:
        # Method 1: Try priority manager first
        if priority_manager:
            try:
                rent_rate = priority_manager.get_value_only('rent_increase_rate', None)
                if rent_rate is not None and isinstance(rent_rate, (int, float)) and rent_rate >= 0:
                    return rent_rate
            except Exception as e:
                logger.warning(f"Priority manager failed for rent_increase_rate: {e}")
        
        # Method 2: Try direct session input
        rent_rate = inputs.get('rent_increase_rate', None)
        if rent_rate is not None and isinstance(rent_rate, (int, float)) and rent_rate >= 0:
            return rent_rate
        
        # Method 3: Try string conversion (in case it's stored as string)
        rent_rate_str = inputs.get('rent_increase_rate', '3.0')
        if isinstance(rent_rate_str, str) and rent_rate_str.strip():
            try:
                rent_rate = float(rent_rate_str.strip())
                if rent_rate >= 0:
                    return rent_rate
            except (ValueError, TypeError):
                pass
        
        # Method 4: Final fallback
        logger.warning("All rent_increase_rate extraction methods failed, using default: 3.0")
        return 3.0
        
    except Exception as e:
        logger.error(f"Critical error in _safe_get_rent_increase_rate: {e}")
        return 3.0


def run_financial_analysis(session_manager) -> tuple[Optional[Dict], Optional[List], Optional[List]]:
    """
    Run the complete financial analysis using session data with data priority management
    
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
        
        # Initialize data priority manager with user inputs, API data, and defaults
        from data.data_priority_manager import get_data_priority_manager
        priority_manager = get_data_priority_manager()
        
        # Update with user inputs (highest priority)
        priority_manager.bulk_update_from_session(session_data)
        
        # Fetch and apply API data (if available) - will not override user inputs
        try:
            from data.interest_rate_feeds import create_interest_rate_feeds
            import asyncio
            
            # Get current rates from API
            rate_feeds = create_interest_rate_feeds()
            current_rates = asyncio.run(rate_feeds.get_current_rates(['30_year_fixed', '15_year_fixed', 'federal_funds_rate']))
            priority_manager.apply_api_rates(current_rates)
            
        except Exception as e:
            logger.warning(f"Could not fetch API rates: {e}")
            # API failure - will fall back to defaults via priority manager
        
        # Extract all required parameters using priority manager (User > API > Default)
        inputs = session_data.get('inputs', {})
        
        analysis_params = {
            # Purchase scenario parameters - use user inputs directly for main parameters
            'purchase_price': inputs.get('purchase_price'),
            'down_payment_pct': inputs.get('down_payment_percent', 30.0),
            'interest_rate': priority_manager.get_value_only('interest_rate', inputs.get('interest_rate', 7.0)),
            'loan_term': inputs.get('loan_term', 20),
            'transaction_costs': inputs.get('transaction_costs_percent', 5.0) * inputs.get('purchase_price', 0) / 100,
            
            # Rental scenario parameters  
            'current_annual_rent': inputs.get('current_annual_rent'),
            'rent_increase_rate': _safe_get_rent_increase_rate(priority_manager, inputs),
            'moving_costs': inputs.get('moving_costs', 0.0),
            
            # Common parameters
            'analysis_period': inputs.get('analysis_period', 25),
            'cost_of_capital': priority_manager.get_value_only('cost_of_capital', inputs.get('cost_of_capital', 8.0)),
            
            # Property parameters
            'property_tax_rate': priority_manager.get_value_only('property_tax_rate', inputs.get('property_tax_rate', 1.2)),
            'property_tax_escalation': inputs.get('property_tax_escalation_rate', 2.0),
            'insurance_cost': inputs.get('insurance_cost', 5000),
            'annual_maintenance': inputs.get('annual_maintenance_percent', 2.0) * inputs.get('purchase_price', 0) / 100,
            'property_management': inputs.get('property_management', 0),
            
            # Advanced parameters
            'capex_reserve_rate': inputs.get('longterm_capex_reserve', 1.5),
            'obsolescence_risk_rate': inputs.get('obsolescence_risk_factor', 0.5),
            'inflation_rate': priority_manager.get_value_only('inflation_rate', inputs.get('inflation_rate', 3.0)),
            'land_value_pct': inputs.get('land_value_percent', 25.0),
            'market_appreciation_rate': priority_manager.get_value_only('market_appreciation_rate', inputs.get('market_appreciation_rate', 3.0)),
            'depreciation_period': inputs.get('depreciation_period', 39),
            
            # Tax parameters
            'corporate_tax_rate': inputs.get('corporate_tax_rate', 25.0),
            'interest_deductible': inputs.get('interest_deductible', True),
            'property_tax_deductible': inputs.get('property_tax_deductible', True),
            
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
        
        # Validate critical parameters before analysis
        critical_params = ['purchase_price', 'current_annual_rent', 'rent_increase_rate']
        for param in critical_params:
            value = analysis_params.get(param)
            if value is None or (isinstance(value, (int, float)) and value < 0):
                # Provide specific fallbacks for mobile compatibility
                if param == 'rent_increase_rate':
                    analysis_params[param] = 3.0
                    logger.warning(f"Parameter '{param}' was invalid ({value}), using default: 3.0")
                    # Also show user-friendly message in production
                    st.info(f"ℹ️ Using default {param.replace('_', ' ').title()}: 3.0%")
                else:
                    raise ValueError(f"Critical parameter '{param}' is missing or zero. Please complete all required inputs.")
        
        # Debug info for production troubleshooting
        if st.checkbox("🔧 Show Debug Info", value=False):
            st.write("**Analysis Parameters Debug:**")
            debug_params = {k: v for k, v in analysis_params.items() if k in critical_params}
            st.json(debug_params)
        
        # Run NPV analysis with comprehensive error handling
        try:
            # Debug: Show what we're about to pass to NPV function
            if 'rent_increase_rate' not in analysis_params:
                st.error("🚨 CRITICAL: rent_increase_rate missing from analysis_params!")
                st.json(analysis_params)
                return None, None, None
            
            st.info(f"🔍 Running NPV analysis with rent_increase_rate: {analysis_params['rent_increase_rate']}")
            
            analysis_results = calculate_npv_comparison(**analysis_params)
            
            st.success("✅ NPV analysis completed successfully")
            
        except NameError as ne:
            st.error(f"🚨 NameError in NPV analysis: {ne}")
            if "rent_increase_rate" in str(ne):
                st.error("This is the rent_increase_rate error! Parameters passed:")
                st.json({k: v for k, v in analysis_params.items() if 'rent' in k.lower()})
            raise ne
        except Exception as e:
            st.error(f"🚨 Unexpected error in NPV analysis: {e}")
            raise e
        
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
            transaction_costs=analysis_params['transaction_costs'],
            # New expansion and subletting parameters
            future_expansion_year=analysis_params['future_expansion_year'],
            additional_space_needed=analysis_params['additional_space_needed'],
            current_space_needed=analysis_params['current_space_needed'],
            ownership_property_size=analysis_params['ownership_property_size'],
            subletting_potential=analysis_params['subletting_potential'],
            subletting_rate=analysis_params['subletting_rate'],
            subletting_space_sqm=analysis_params['subletting_space_sqm'],
            # Rental rate parameters for subletting calculations
            rent_increase_rate=analysis_params['rent_increase_rate'],
            # Property upgrade parameters
            property_upgrade_cycle=analysis_params['property_upgrade_cycle']
        )
        
        rental_flows = calculate_rental_cash_flows(
            current_annual_rent=analysis_params['current_annual_rent'],
            rent_increase_rate=analysis_params['rent_increase_rate'],
            analysis_period=analysis_params['analysis_period'],
            corporate_tax_rate=analysis_params['corporate_tax_rate'],
            # New expansion parameters for rental
            future_expansion_year=analysis_params['future_expansion_year'],
            additional_space_needed=analysis_params['additional_space_needed'],
            current_space_needed=analysis_params['current_space_needed'],
            rental_property_size=analysis_params['rental_property_size']
        )
        
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
        
        # Check for input changes and clear stale analysis
        session_manager.clear_stale_analysis()
        
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
                        # Analysis completed with real data
                        # Mark that analysis has been run with current inputs
                        session_manager.mark_analysis_run()
                        st.success("✅ Analysis completed successfully!")
                        st.rerun()
        
        # Show analysis results if available
        if 'analysis_results' in st.session_state:
            st.markdown("---")
            st.markdown("### 📈 Analysis Results Preview")
            create_results_summary_section(st.session_state['analysis_results'])
            
            st.info("📊 **Go to the 'Analysis Results' tab to view detailed visualizations and charts.**")
        
        # Show notification if inputs have changed since last analysis
        elif session_manager.has_analysis_results() and session_manager.analysis_is_stale():
            st.markdown("---")
            st.warning("⚠️ **Your inputs have changed since the last analysis.** Click 'Run Financial Analysis' above to see updated results.")
        elif st.session_state.get("inputs_changed", False) and not session_manager.has_analysis_results():
            st.markdown("---")
            st.info("💡 **Ready for analysis!** Click 'Run Financial Analysis' above to generate results based on your inputs.")
        
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
    
    # Check for input changes and clear stale analysis
    cleared_stale = session_manager.clear_stale_analysis()
    
    # Show notification if stale results were just cleared
    if cleared_stale:
        st.info("🔄 **Analysis results have been refreshed** because your inputs have changed. Please re-run the analysis to see updated results.")
    
    # Check if we have real analysis results
    if 'analysis_results' not in st.session_state:
        st.warning("⚠️ **No analysis results available.** Please complete the input sections in the Dashboard tab and run the analysis.")
        
        # Check if inputs are ready for analysis
        if session_manager.is_ready_for_analysis():
            st.info("✅ **All inputs are complete!** Go to the Dashboard tab and click 'Run Financial Analysis' to generate real results.")
        else:
            completion = session_manager.get_completion_percentage()
            st.info(f"📝 **Input Progress: {completion:.0f}%** - Complete all required sections to enable analysis.")
        return
    
    # Analysis results available - show visualizations
    st.success("✅ **Displaying Analysis Results** based on your input data.")
    
    # Render full analysis results dashboard
    render_analysis_results_tab(
        st.session_state['analysis_results'],
        st.session_state['ownership_flows'],
        st.session_state['rental_flows'],
        session_manager
    )


def render_comparison_tab():
    """Render detailed comparison views"""
    session_manager = get_session_manager()
    
    # Check for input changes and clear stale analysis
    cleared_stale = session_manager.clear_stale_analysis()
    
    # Show notification if stale results were just cleared
    if cleared_stale:
        st.info("🔄 **Analysis results have been refreshed** because your inputs have changed. Please re-run the analysis to see updated results.")
    
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
    
    # Check for input changes and clear stale analysis
    cleared_stale = session_manager.clear_stale_analysis()
    
    # Show notification if stale results were just cleared
    if cleared_stale:
        st.warning("🔄 **Analysis results have been refreshed** because your inputs have changed. Please re-run the analysis to see updated results.")
    
    if not session_manager.is_ready_for_analysis():
        create_info_box(
            "Complete all required input sections to enable export functionality.",
            "warning"
        )
        return
    
    # Check if we have analysis results for professional exports
    has_analysis_results = ('analysis_results' in st.session_state and 
                            'ownership_flows' in st.session_state and 
                            'rental_flows' in st.session_state)
    
    if has_analysis_results:
        # Check if analysis results are current (not stale)
        if session_manager.analysis_is_stale():
            st.error("❌ **Export Not Available - Analysis Results Are Outdated**")
            st.markdown("Your input parameters have changed since the last analysis was run. The current analysis results may not reflect your latest inputs.")
            st.markdown("**Please re-run the financial analysis to ensure your export contains the latest data.**")
            return
        
        # Professional Export Section
        st.markdown("### 📊 Professional Reports")
        st.markdown("Generate executive-ready Excel reports with charts and comprehensive analysis.")
        
        
        # Try to initialize export system
        try:
            # PDF features hidden - will be re-enabled later if needed
            # from export.pdf_integration import PDFExportManager, PDF_SYSTEM_AVAILABLE
            from export.streamlit_integration import ExcelExportManager, EXCEL_SYSTEM_AVAILABLE
            
            # Prepare export data with real user data and metadata
            from datetime import datetime
            export_data = {
                'analysis_results': st.session_state['analysis_results'],
                'ownership_flows': st.session_state['ownership_flows'],
                'rental_flows': st.session_state['rental_flows'],
                'inputs': session_manager.export_session_data(),
                'export_metadata': {
                    'export_timestamp': datetime.now().isoformat(),
                    'analysis_hash': st.session_state.get("analysis_input_hash", "unknown"),
                    'data_freshness': 'current' if not session_manager.analysis_is_stale() else 'stale'
                }
            }
            
            # Validate export data
            validation_errors = []
            if not export_data['analysis_results']:
                validation_errors.append("Analysis results are empty")
            if not export_data['ownership_flows']:
                validation_errors.append("Ownership cash flows are missing")
            if not export_data['rental_flows']:
                validation_errors.append("Rental cash flows are missing")
            if not export_data['inputs'].get('inputs'):
                validation_errors.append("Input parameters are missing")
            
            # Additional validation for data consistency
            analysis_hash = st.session_state.get("analysis_input_hash", "")
            current_hash = session_manager.get_analysis_input_hash()
            if analysis_hash != current_hash:
                validation_errors.append("Data synchronization issue detected - input hash mismatch")
            
            if validation_errors:
                st.error("❌ **Export Data Validation Failed**")
                st.markdown("**Issues found:**")
                for error in validation_errors:
                    st.markdown(f"• {error}")
                st.markdown("**Please run the analysis again to generate complete data.**")
                return
            
            # PDF features hidden - will be re-enabled later if needed
            # col1, col2 = st.columns(2)
            
            # Excel Reports section (full width)
            st.markdown("#### 📊 Excel Reports")
            if EXCEL_SYSTEM_AVAILABLE:
                try:
                    excel_manager = ExcelExportManager()
                    
                    # Excel options
                    include_charts = st.checkbox("Include Charts", value=True, help="Embed analysis charts in Excel")
                    professional_format = st.checkbox("Professional Formatting", value=True, help="Apply corporate styling")
                    
                    # Call the Excel manager directly (no button wrapper)
                    excel_manager.create_streamlit_download_button(
                        export_data=export_data,
                        template_type='detailed',  # Use supported template
                        include_charts=include_charts,
                        professional_formatting=professional_format
                    )
                    
                except Exception as e:
                    st.error(f"Excel system error: {str(e)}")
                    logger.error(f"Excel system error in export tab: {str(e)}", exc_info=True)
            else:
                st.error("Excel generation not available. Missing dependencies.")
                st.code("pip install openpyxl kaleido plotly")
                    
        except ImportError:
            st.warning("⚠️ Professional export system not available. Showing basic export options.")
            
            # Fallback to basic JSON exports
            _render_basic_export_options(session_manager)
    
    else:
        create_info_box(
            "Run the financial analysis first to enable professional PDF and Excel report generation.",
            "info"
        )
        
        # Show basic export options even without analysis
        _render_basic_export_options(session_manager)
    
    # Session management section
    st.markdown("---")
    st.markdown("### 🔄 Session Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
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
    
    with col2:
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


def _render_basic_export_options(session_manager):
    """Render basic JSON export options when professional exports aren't available"""
    
    st.markdown("### 📄 Basic Export Options")
    
    # Export session data as JSON
    export_data = session_manager.export_session_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📄 Download Input Data (JSON)",
            data=str(export_data),
            file_name=f"real_estate_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="Download all input parameters for backup or sharing"
        )
    
    with col2:
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


def render_data_integration_tab():
    """Render data integration and API status"""
    try:
        from components.api_status_dashboard import render_api_status_dashboard
        render_api_status_dashboard()
    except ImportError:
        st.error("❌ **API Status Dashboard not available**")
        st.info("The data integration dashboard requires additional components.")


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
    
    # Apply professional styling and force light mode
    st.markdown("""
    <style>
    /* Force light mode */
    .stApp {
        background-color: #FFFFFF !important;
        color: #262730 !important;
    }
    
    /* Main content styling */
    .main .block-container {
        padding-top: 2rem;
        background-color: #FFFFFF !important;
        color: #262730 !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F0F2F6 !important;
    }
    
    /* Text elements */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {
        color: #262730 !important;
    }
    
    /* Input widgets */
    .stSelectbox, .stNumberInput, .stSlider, .stCheckbox {
        color: #262730 !important;
    }
    
    /* Custom styling for charts and visualizations */
    .js-plotly-plot .plotly .modebar {
        right: 10px !important;
    }
    
    /* Enhanced metric cards */
    div[data-testid="metric-container"] {
        background-color: #f0f2f6 !important;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #262730 !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #FFFFFF !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #262730 !important;
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
        <p style="color: white; margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">Executive Dashboard • Interactive Charts • Enhanced Tooltips • v2.1.4</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Tab navigation with new analysis tab and API status
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Analysis Dashboard", 
        "📈 Analysis Results", 
        "📋 Detailed Comparison",
        "📤 Export & Share", 
        "🌐 Data Integration",
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
        render_data_integration_tab()
    
    with tab6:
        render_help_tab()
    
    # Professional footer
    render_footer()


if __name__ == "__main__":
    main()