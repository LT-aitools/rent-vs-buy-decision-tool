"""
Streamlit Application Example - Excel Export Integration
Example of how to integrate Excel export functionality into the main Streamlit app

This module shows how to add Excel export capabilities to the existing 
Real Estate Decision Tool Streamlit application.
"""

import streamlit as st
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import the excel export integration functions
from .streamlit_integration import (
    generate_excel_report,
    create_download_button,
    create_export_ui,
    show_export_status,
    get_available_templates,
    recommend_template,
    quick_excel_export
)


def add_excel_export_section(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, Any]],
    rental_flows: List[Dict[str, Any]],
    session_data: Dict[str, Any]
) -> None:
    """
    Add Excel export section to Streamlit app
    
    This function should be called in the main app after analysis results are generated.
    It creates a complete Excel export interface with configuration options.
    
    Args:
        analysis_results: Results from calculate_npv_comparison()
        ownership_flows: Results from calculate_ownership_cash_flows()
        rental_flows: Results from calculate_rental_cash_flows()
        session_data: Complete session state data
    """
    
    st.markdown("---")
    st.header("📊 Export Analysis Report")
    
    # Create tabs for different export options
    tab1, tab2 = st.tabs(["📋 Quick Export", "⚙️ Custom Export"])
    
    with tab1:
        st.subheader("Quick Excel Export")
        st.write("Generate a professional Excel report with default settings.")
        
        # Quick export button
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if st.button("🚀 Generate Excel Report", type="primary"):
                with st.spinner("Generating Excel report..."):
                    excel_file = quick_excel_export(
                        analysis_results, ownership_flows, rental_flows, session_data
                    )
                    
                    if excel_file:
                        st.success("✅ Excel report generated successfully!")
                        st.session_state['excel_file'] = excel_file
                    else:
                        st.error("❌ Failed to generate Excel report")
        
        with col2:
            # Show download button if file was generated
            if 'excel_file' in st.session_state and st.session_state['excel_file']:
                create_download_button(
                    st.session_state['excel_file'],
                    "📥 Download Excel Report",
                    "real_estate_analysis.xlsx"
                )
    
    with tab2:
        st.subheader("Custom Excel Export")
        st.write("Customize your Excel report with advanced options.")
        
        # Export configuration UI
        export_config = create_export_ui()
        
        # Show export estimates
        st.subheader("Export Preview")
        analysis_period = session_data.get('analysis_period', 25)
        show_export_status(export_config, analysis_period)
        
        # Generate custom report
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎯 Generate Custom Report", type="primary"):
                with st.spinner("Generating custom Excel report..."):
                    excel_file = generate_excel_report(
                        analysis_results=analysis_results,
                        ownership_flows=ownership_flows,
                        rental_flows=rental_flows,
                        session_data=session_data,
                        template_type=export_config['template_type'],
                        company_name=export_config['company_name'],
                        report_title=export_config['report_title']
                    )
                    
                    if excel_file:
                        st.success("✅ Custom Excel report generated successfully!")
                        st.session_state['custom_excel_file'] = excel_file
                    else:
                        st.error("❌ Failed to generate custom Excel report")
        
        with col2:
            # Show download button for custom report
            if 'custom_excel_file' in st.session_state and st.session_state['custom_excel_file']:
                create_download_button(
                    st.session_state['custom_excel_file'],
                    "📥 Download Custom Report"
                )


def add_simple_export_button(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, Any]],
    rental_flows: List[Dict[str, Any]],
    session_data: Dict[str, Any]
) -> None:
    """
    Add simple Excel export button to sidebar or main area
    
    Minimal integration - just adds a button that generates and downloads an Excel report.
    
    Args:
        analysis_results: Results from NPV analysis
        ownership_flows: Ownership cash flows
        rental_flows: Rental cash flows
        session_data: Session state data
    """
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("📊 Export to Excel", type="secondary", use_container_width=True):
            with st.spinner("Generating Excel report..."):
                excel_file = quick_excel_export(
                    analysis_results, ownership_flows, rental_flows, session_data
                )
                
                if excel_file:
                    # Create download button immediately
                    with open(excel_file, 'rb') as f:
                        excel_data = f.read()
                    
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=excel_data,
                        file_name=f"real_estate_analysis_{analysis_results.get('recommendation', 'analysis')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )
                else:
                    st.error("Failed to generate Excel report")


def show_template_selector_in_sidebar() -> str:
    """
    Add template selector to Streamlit sidebar
    
    Returns:
        Selected template type
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Excel Export")
    
    # Get available templates
    templates = get_available_templates()
    template_options = {t['name']: t['id'] for t in templates}
    
    selected_template_name = st.sidebar.selectbox(
        "Report Template",
        options=list(template_options.keys()),
        help="Choose Excel report template"
    )
    
    return template_options[selected_template_name]


def add_export_info_box() -> None:
    """Add informational box about Excel export capabilities"""
    
    with st.expander("ℹ️ About Excel Export"):
        st.markdown("""
        ### Excel Report Features
        
        **Professional Formatting**
        - Multiple worksheets with analysis data
        - Interactive charts and visualizations  
        - Professional styling and branding
        - Currency and percentage formatting
        
        **Available Templates**
        - **Executive**: High-level summary for decision makers
        - **Detailed**: Comprehensive analysis for analysts
        - **Investor**: Investment-focused metrics
        - **Full Analysis**: Complete data export
        
        **Export Contents**
        - Executive summary with recommendations
        - Detailed cash flow analysis
        - NPV calculations and assumptions
        - Terminal value calculations
        - Interactive charts and graphs
        - All input parameters and assumptions
        
        Reports are generated in `.xlsx` format compatible with Microsoft Excel,
        Google Sheets, and other spreadsheet applications.
        """)


# Example integration code for adding to main app
INTEGRATION_EXAMPLE = '''
# Add this to your main Streamlit app after analysis results are calculated:

from src.export.streamlit_example import add_excel_export_section

# In your main app function, after calculating analysis results:
if analysis_results and ownership_flows and rental_flows:
    # Add the Excel export section
    add_excel_export_section(
        analysis_results=analysis_results,
        ownership_flows=ownership_flows, 
        rental_flows=rental_flows,
        session_data=st.session_state
    )

# Or for a simpler integration, just add a button:
from src.export.streamlit_example import add_simple_export_button

add_simple_export_button(
    analysis_results, ownership_flows, rental_flows, st.session_state
)
'''


def show_integration_guide():
    """Show integration guide in Streamlit"""
    
    st.markdown("---")
    st.subheader("🔧 Integration Guide")
    
    st.markdown("""
    To add Excel export functionality to your main Streamlit app, 
    follow these steps:
    """)
    
    st.code(INTEGRATION_EXAMPLE, language="python")
    
    st.markdown("""
    ### Integration Options
    
    1. **Full Export Section** (`add_excel_export_section`): 
       Complete export interface with tabs and configuration options
    
    2. **Simple Export Button** (`add_simple_export_button`): 
       Just a button that generates and downloads a report
       
    3. **Sidebar Template Selector** (`show_template_selector_in_sidebar`):
       Adds template selection to the sidebar
       
    4. **Information Box** (`add_export_info_box`):
       Shows export capabilities and features
    """)