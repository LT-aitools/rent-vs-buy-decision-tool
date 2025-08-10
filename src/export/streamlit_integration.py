"""
Streamlit Integration for Excel Export
Simplified interface for generating Excel reports from Streamlit app

This module provides easy-to-use functions that can be called directly
from the Streamlit application to generate professional Excel reports.
"""

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

import streamlit as st

from .excel.excel_generator import ExcelGenerator
from .excel.template_manager import ExcelTemplateManager, TemplateType
from .validation import validate_export_data

logger = logging.getLogger(__name__)


def generate_excel_report(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, Any]],
    rental_flows: List[Dict[str, Any]],
    session_data: Dict[str, Any],
    template_type: str = "detailed",
    company_name: Optional[str] = None,
    report_title: Optional[str] = None
) -> Optional[Path]:
    """
    Generate Excel report from analysis results
    
    Args:
        analysis_results: NPV analysis results from calculate_npv_comparison()
        ownership_flows: Ownership cash flows from calculate_ownership_cash_flows()
        rental_flows: Rental cash flows from calculate_rental_cash_flows() 
        session_data: Complete session state data
        template_type: Template type ("executive", "detailed", "investor", "full_analysis")
        company_name: Optional company name for branding
        report_title: Optional custom report title
        
    Returns:
        Path to generated Excel file or None if generation failed
    """
    try:
        # Run async generation in sync context
        return asyncio.run(_generate_excel_async(
            analysis_results, ownership_flows, rental_flows, session_data,
            template_type, company_name, report_title
        ))
    except Exception as e:
        logger.error(f"Excel report generation failed: {str(e)}")
        st.error(f"Failed to generate Excel report: {str(e)}")
        return None


async def _generate_excel_async(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, Any]],
    rental_flows: List[Dict[str, Any]],
    session_data: Dict[str, Any],
    template_type: str,
    company_name: Optional[str],
    report_title: Optional[str]
) -> Optional[Path]:
    """Async implementation of Excel generation"""
    
    # Prepare export data package
    export_data = {
        'analysis_results': analysis_results,
        'ownership_flows': {'annual_cash_flows': [flow.get('net_cash_flow', 0) for flow in ownership_flows]},
        'rental_flows': {'annual_cash_flows': [flow.get('net_cash_flow', 0) for flow in rental_flows]},
        'session_data': session_data,
        'export_options': {
            'template_type': template_type,
            'company_name': company_name or "Real Estate Decision Analytics",
            'report_title': report_title or f"Investment Analysis Report - {datetime.now().strftime('%B %d, %Y')}"
        }
    }
    
    # Validate data
    validation_result = validate_export_data(export_data)
    if not validation_result['is_valid']:
        error_msg = "; ".join(validation_result['errors'])
        logger.error(f"Data validation failed: {error_msg}")
        st.error(f"Export data validation failed: {error_msg}")
        return None
    
    # Initialize Excel generator
    excel_generator = ExcelGenerator()
    
    try:
        # Validate export data
        data_validation = await excel_generator.validate_data(export_data)
        if not data_validation['is_valid']:
            error_msg = "; ".join(data_validation['errors'])
            logger.error(f"Excel data validation failed: {error_msg}")
            st.error(f"Excel data validation failed: {error_msg}")
            return None
        
        # Show warnings if any
        if data_validation['warnings']:
            for warning in data_validation['warnings']:
                st.warning(f"Data warning: {warning}")
        
        # Prepare data for Excel generation
        excel_data = await excel_generator.prepare_data(export_data)
        
        # Generate workbook
        output_path = await excel_generator.generate_workbook(excel_data, template_type)
        
        logger.info(f"Excel report generated successfully: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Excel generation error: {str(e)}")
        st.error(f"Excel generation error: {str(e)}")
        return None
    finally:
        # Cleanup
        excel_generator.cleanup()


def create_download_button(
    excel_file_path: Path,
    button_text: str = "📊 Download Excel Report",
    file_name: Optional[str] = None
) -> bool:
    """
    Create Streamlit download button for Excel file
    
    Args:
        excel_file_path: Path to generated Excel file
        button_text: Text for the download button
        file_name: Custom filename for download
        
    Returns:
        True if button was clicked and file downloaded
    """
    if not excel_file_path or not excel_file_path.exists():
        st.error("Excel file not found or invalid path")
        return False
    
    try:
        # Read Excel file content
        with open(excel_file_path, 'rb') as f:
            excel_data = f.read()
        
        # Generate filename if not provided
        if not file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"real_estate_analysis_{timestamp}.xlsx"
        
        # Create download button
        return st.download_button(
            label=button_text,
            data=excel_data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        logger.error(f"Download button creation failed: {str(e)}")
        st.error(f"Failed to create download button: {str(e)}")
        return False


def get_available_templates() -> List[Dict[str, str]]:
    """
    Get list of available Excel templates
    
    Returns:
        List of template information dictionaries
    """
    template_manager = ExcelTemplateManager()
    return template_manager.get_available_templates()


def get_template_preview(template_type: str) -> Dict[str, Any]:
    """
    Get preview information for a template
    
    Args:
        template_type: Template type to preview
        
    Returns:
        Template preview information
    """
    template_manager = ExcelTemplateManager()
    return template_manager.get_template_preview(template_type)


def recommend_template(session_data: Dict[str, Any]) -> str:
    """
    Get recommended template based on session data
    
    Args:
        session_data: Complete session state data
        
    Returns:
        Recommended template type
    """
    template_manager = ExcelTemplateManager()
    
    # Create export context from session data
    export_context = {
        'analysis_period': session_data.get('analysis_period', 25),
        'presentation_mode': session_data.get('export_preferences', {}).get('presentation_mode', 'detailed'),
        'audience': session_data.get('export_preferences', {}).get('audience', 'analysts'),
        'include_sensitivity': session_data.get('export_preferences', {}).get('include_sensitivity', True),
        'include_raw_data': session_data.get('export_preferences', {}).get('include_raw_data', False)
    }
    
    return template_manager.get_recommended_template(export_context)


def create_export_ui() -> Dict[str, Any]:
    """
    Create Streamlit UI for Excel export configuration
    
    Returns:
        Export configuration dictionary
    """
    st.subheader("📊 Excel Export Configuration")
    
    # Template selection
    available_templates = get_available_templates()
    template_options = {t['name']: t['id'] for t in available_templates}
    
    selected_template_name = st.selectbox(
        "Select Report Template",
        options=list(template_options.keys()),
        help="Choose the type of Excel report to generate"
    )
    
    selected_template_id = template_options[selected_template_name]
    
    # Show template preview
    with st.expander("Template Preview"):
        preview = get_template_preview(selected_template_id)
        st.write(f"**{preview['name']}**")
        st.write(preview['description'])
        st.write(f"Worksheets: {preview['worksheet_count']}")
        
        # Show worksheet details
        for ws in preview['worksheets']:
            st.write(f"• {ws['name']} ({'with charts' if ws['includes_charts'] else 'data only'})")
    
    # Customization options
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input(
            "Company Name",
            value="Real Estate Decision Analytics",
            help="Company name for report branding"
        )
    
    with col2:
        report_title = st.text_input(
            "Report Title",
            value=f"Investment Analysis Report - {datetime.now().strftime('%B %d, %Y')}",
            help="Custom title for the report"
        )
    
    # Advanced options
    with st.expander("Advanced Options"):
        include_charts = st.checkbox("Include Charts", value=True, help="Embed charts as images in Excel")
        include_sensitivity = st.checkbox("Include Sensitivity Analysis", value=True)
        include_assumptions = st.checkbox("Include Input Assumptions", value=True)
    
    return {
        'template_type': selected_template_id,
        'company_name': company_name,
        'report_title': report_title,
        'include_charts': include_charts,
        'include_sensitivity': include_sensitivity,
        'include_assumptions': include_assumptions
    }


def show_export_status(export_config: Dict[str, Any], data_size: int = 25) -> None:
    """
    Show export status and size estimates
    
    Args:
        export_config: Export configuration from create_export_ui()
        data_size: Number of years/data points in analysis
    """
    template_manager = ExcelTemplateManager()
    
    try:
        size_estimate = template_manager.get_template_size_estimate(
            export_config['template_type'], 
            data_size
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Worksheets", size_estimate['worksheet_count'])
        
        with col2:
            st.metric("Estimated Size", f"{size_estimate['estimated_size_kb']} KB")
        
        with col3:
            st.metric("Complexity", size_estimate['complexity'])
        
        with col4:
            st.metric("Est. Generation Time", f"{size_estimate['generation_time_estimate_seconds']}s")
            
    except Exception as e:
        st.warning(f"Could not calculate size estimates: {str(e)}")


# Convenience function for simple Excel generation
def quick_excel_export(
    analysis_results: Dict[str, Any],
    ownership_flows: List[Dict[str, Any]],
    rental_flows: List[Dict[str, Any]],
    session_data: Dict[str, Any]
) -> Optional[Path]:
    """
    Quick Excel export with default settings
    
    Args:
        analysis_results: NPV analysis results
        ownership_flows: Ownership cash flows
        rental_flows: Rental cash flows
        session_data: Session state data
        
    Returns:
        Path to generated Excel file
    """
    return generate_excel_report(
        analysis_results=analysis_results,
        ownership_flows=ownership_flows,
        rental_flows=rental_flows,
        session_data=session_data,
        template_type="detailed",
        company_name="Real Estate Decision Analytics",
        report_title=f"Investment Analysis - {datetime.now().strftime('%B %d, %Y')}"
    )