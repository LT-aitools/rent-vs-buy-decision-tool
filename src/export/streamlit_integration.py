"""
Streamlit Integration for Excel Export
Simplified interface for generating Excel reports from Streamlit app

This module provides easy-to-use functions that can be called directly
from the Streamlit application to generate professional Excel reports.
"""

import asyncio
import logging
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

import streamlit as st

try:
    from .excel.excel_generator import ExcelGenerator
    from .excel.template_manager import ExcelTemplateManager, TemplateType
    from .validation import validate_export_data
    EXCEL_SYSTEM_AVAILABLE = True
except ImportError:
    EXCEL_SYSTEM_AVAILABLE = False
    logging.warning("Excel export system not fully available - some dependencies missing")

logger = logging.getLogger(__name__)


class ExcelExportManager:
    """
    Excel Export Manager for Streamlit Integration
    
    Provides comprehensive Excel report generation with template support,
    chart embedding, and progress tracking for Streamlit applications.
    """
    
    def __init__(self):
        """Initialize Excel export manager"""
        
        if not EXCEL_SYSTEM_AVAILABLE:
            raise ImportError("Excel system dependencies not available")
        
        # Initialize Excel system components
        self.excel_generator = ExcelGenerator()
        self.template_manager = ExcelTemplateManager()
        
        # Available templates
        self.available_templates = ['comprehensive', 'executive', 'detailed']
        
        logger.info("Excel Export Manager initialized")
    
    async def generate_excel_report(
        self,
        export_data: Dict[str, Any],
        template_type: str = 'comprehensive',
        output_path: Optional[Path] = None,
        include_charts: bool = True
    ) -> Tuple[Path, Dict[str, Any]]:
        """
        Generate Excel report with progress tracking
        
        Args:
            export_data: Complete analysis data
            template_type: Excel template type
            output_path: Output file path (temp file if None)
            include_charts: Whether to include charts
            
        Returns:
            Tuple of (excel_path, export_info)
        """
        
        start_time = time.time()
        logger.info(f"Starting Excel generation - template: {template_type}")
        
        try:
            # Validate export data
            validation = validate_export_data(export_data)
            if not validation['is_valid']:
                raise ValueError("Export data validation failed")
            
            # Set up output path
            if output_path is None:
                output_path = Path(tempfile.mktemp(suffix='.xlsx'))
            
            # Generate Excel file
            excel_path = await self._generate_with_template(
                export_data=export_data,
                template_type=template_type,
                output_path=output_path,
                include_charts=include_charts
            )
            
            # Prepare export information
            generation_time = time.time() - start_time
            export_info = {
                'template_type': template_type,
                'include_charts': include_charts,
                'generation_time': generation_time,
                'file_size': excel_path.stat().st_size if excel_path.exists() else 0,
                'worksheets': self._count_worksheets(template_type),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Excel generation completed in {generation_time:.1f}s")
            return excel_path, export_info
            
        except Exception as e:
            logger.error(f"Excel generation failed: {str(e)}")
            raise
    
    async def _generate_with_template(
        self,
        export_data: Dict[str, Any],
        template_type: str,
        output_path: Path,
        include_charts: bool
    ) -> Path:
        """Generate Excel using template manager"""
        
        # Handle both list and dict formats for cash flows
        ownership_flows = export_data.get('ownership_flows', [])
        rental_flows = export_data.get('rental_flows', [])
        
        # Convert list format to expected format for Excel generation
        if isinstance(ownership_flows, list):
            ownership_flows_processed = ownership_flows
        else:
            # Already in dict format, extract the list
            ownership_flows_processed = ownership_flows.get('annual_cash_flows', [])
            # Convert back to list of dicts if needed
            if isinstance(ownership_flows_processed, list) and ownership_flows_processed:
                if not isinstance(ownership_flows_processed[0], dict):
                    # Convert from simple array to list of dicts
                    ownership_flows_processed = [
                        {'year': i+1, 'net_cash_flow': flow} 
                        for i, flow in enumerate(ownership_flows_processed)
                    ]
        
        if isinstance(rental_flows, list):
            rental_flows_processed = rental_flows
        else:
            # Already in dict format, extract the list
            rental_flows_processed = rental_flows.get('annual_cash_flows', [])
            # Convert back to list of dicts if needed
            if isinstance(rental_flows_processed, list) and rental_flows_processed:
                if not isinstance(rental_flows_processed[0], dict):
                    # Convert from simple array to list of dicts
                    rental_flows_processed = [
                        {'year': i+1, 'net_cash_flow': flow}
                        for i, flow in enumerate(rental_flows_processed)
                    ]
        
        # Use the existing generate_excel_report function
        result_path = await asyncio.to_thread(
            generate_excel_report,
            analysis_results=export_data.get('analysis_results', {}),
            ownership_flows=ownership_flows_processed,
            rental_flows=rental_flows_processed,
            session_data=export_data.get('inputs', {}) or export_data.get('session_data', {}),
            template_type=template_type
        )
        
        # If a result path was returned, copy it to our desired location
        if result_path and isinstance(result_path, Path) and result_path.exists():
            import shutil
            # Create parent directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file instead of moving to avoid cleanup issues
            shutil.copy2(str(result_path), str(output_path))
            logger.info(f"Copied Excel file from {result_path} to {output_path}")
            
            return output_path
        elif result_path and isinstance(result_path, Path) and result_path == output_path:
            # File was already created at the desired path
            return result_path
        else:
            raise RuntimeError(f"Excel generation failed - no file created at {result_path}")
    
    def _count_worksheets(self, template_type: str) -> int:
        """Estimate worksheet count for template type"""
        
        worksheet_counts = {
            'comprehensive': 5,  # Summary, Ownership, Rental, Charts, Assumptions
            'executive': 3,      # Summary, Key Metrics, Charts
            'detailed': 6        # All worksheets plus additional analysis
        }
        
        return worksheet_counts.get(template_type, 5)
    
    def create_streamlit_download_button(
        self,
        export_data: Dict[str, Any],
        template_type: str = 'comprehensive',
        button_label: Optional[str] = None,
        include_charts: bool = True,
        professional_formatting: bool = True
    ) -> bool:
        """
        Create Streamlit download button for Excel report
        
        Args:
            export_data: Export data for report generation
            template_type: Template type to generate
            button_label: Custom button label
            include_charts: Whether to include charts
            professional_formatting: Whether to apply professional formatting
            
        Returns:
            True if button was clicked and download initiated
        """
        if button_label is None:
            button_label = f"Generate {template_type.title()} Excel Report"
        
        # Create download button
        if st.button(button_label, key=f"excel_download_{template_type}"):
            logger.info(f"Excel export button clicked: {template_type}")
            
            try:
                # Validate critical data exists
                if 'analysis_results' not in export_data:
                    st.error("❌ Missing analysis results data for export")
                    return False
                if not export_data.get('analysis_results'):
                    st.error("❌ Empty analysis results data for export")
                    return False
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔄 Initializing Excel export...")
                progress_bar.progress(10)
                logger.info("Excel export progress: Initializing...")
                
                # Generate Excel file
                with st.spinner("Generating Excel report..."):
                    status_text.text("🔄 Generating Excel file...")
                    progress_bar.progress(50)
                    logger.info("Excel export progress: Starting async generation...")
                    
                    # Use synchronous Excel generation for Streamlit compatibility
                    logger.info(f"Starting Excel generation with data: ownership_flows={len(export_data['ownership_flows']) if export_data['ownership_flows'] else 0} items, rental_flows={len(export_data['rental_flows']) if export_data['rental_flows'] else 0} items")
                    excel_path = generate_excel_report(
                        analysis_results=export_data['analysis_results'],
                        ownership_flows=export_data['ownership_flows'],
                        rental_flows=export_data['rental_flows'],
                        session_data=export_data.get('inputs', {}) or export_data.get('session_data', {}),
                        template_type=template_type
                    )
                    logger.info(f"Excel generation returned: {excel_path}")
                    generation_info = {
                        'template_type': template_type,
                        'include_charts': include_charts,
                        'generation_time': 0,
                        'file_size': excel_path.stat().st_size if excel_path and excel_path.exists() else 0,
                        'worksheets': 5,
                        'timestamp': datetime.now().isoformat()
                    }
                    logger.info(f"Excel generation completed: {excel_path}")
                
                status_text.text("✅ Excel report generated successfully!")
                progress_bar.progress(100)
                
                # Verify file exists
                if not excel_path or not excel_path.exists():
                    st.error("❌ Excel file generation failed - file not found")
                    logger.error(f"Excel file missing: {excel_path}")
                    return False
                
                file_size = excel_path.stat().st_size
                logger.info(f"Excel file verified, size: {file_size:,} bytes")
                
                # Read Excel for download
                with open(excel_path, 'rb') as excel_file:
                    excel_bytes = excel_file.read()
                
                logger.info(f"Excel file read into memory: {len(excel_bytes):,} bytes")
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"real_estate_analysis_{template_type}_{timestamp}.xlsx"
                
                # Create download button
                st.download_button(
                    label="📊 Download Excel Report",
                    data=excel_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"excel_download_final_{template_type}"
                )
                
                logger.info("Excel download button created successfully")
                
                # Show generation info
                st.success(f"✅ Excel report generated successfully!")
                
                with st.expander("Generation Details"):
                    st.write(f"**Template:** {generation_info['template_type'].title()}")
                    st.write(f"**Worksheets:** {generation_info['worksheets']}")
                    st.write(f"**File Size:** {generation_info['file_size']:,} bytes")
                    st.write(f"**Generation Time:** {generation_info.get('generation_time', 0):.2f} seconds")
                
                # Clean up
                try:
                    excel_path.unlink()
                    logger.info("Temporary Excel file cleaned up")
                except Exception as cleanup_e:
                    logger.warning(f"Failed to cleanup Excel file: {cleanup_e}")
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                return True
                
            except Exception as e:
                error_msg = f"Error generating Excel report: {str(e)}"
                st.error(f"❌ {error_msg}")
                logger.error(f"Excel export error: {str(e)}", exc_info=True)
                
                # Clear progress indicators
                try:
                    progress_bar.empty()
                    status_text.empty()
                except:
                    pass
        
        return False
    
    def get_export_capabilities(self) -> Dict[str, Any]:
        """Get Excel export capabilities"""
        
        capabilities = {
            'excel_system_available': EXCEL_SYSTEM_AVAILABLE,
            'templates': self.available_templates,
            'features': {
                'professional_formatting': True,
                'chart_embedding': True,
                'multiple_worksheets': True,
                'data_validation': True,
                'conditional_formatting': True
            },
            'formats': ['xlsx'],
            'chart_types': [
                'npv_comparison',
                'annual_cash_flows',
                'cumulative_cash_flows',
                'financial_metrics',
                'sensitivity_analysis'
            ]
        }
        
        return capabilities


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
        logger.info(f"generate_excel_report called with ownership_flows={type(ownership_flows)}, rental_flows={type(rental_flows)}")
        # Check if we're in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an event loop, need to use different approach
            import concurrent.futures
            import threading
            
            def run_in_thread():
                # Run the async function in a new event loop on a separate thread
                result = asyncio.run(_generate_excel_async(
                    analysis_results, ownership_flows, rental_flows, session_data,
                    template_type, company_name, report_title
                ))
                logger.info(f"Thread result: {result}")
                return result
            
            # Use ThreadPoolExecutor to run in separate thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result(timeout=60)  # 60 second timeout
                
        except RuntimeError:
            # No event loop running, we can use asyncio.run
            result = asyncio.run(_generate_excel_async(
                analysis_results, ownership_flows, rental_flows, session_data,
                template_type, company_name, report_title
            ))
            logger.info(f"AsyncIO result: {result}")
            return result
            
    except Exception as e:
        logger.error(f"Excel report generation failed: {str(e)}", exc_info=True)
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
        'ownership_flows': ownership_flows,  # Keep original format
        'rental_flows': rental_flows,        # Keep original format
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
        return None
    
    # Initialize Excel generator
    excel_generator = ExcelGenerator()
    
    try:
        # Validate export data
        data_validation = await excel_generator.validate_data(export_data)
        if not data_validation['is_valid']:
            error_msg = "; ".join(data_validation['errors'])
            logger.error(f"Excel data validation failed: {error_msg}")
            return None
        
        # Log warnings if any
        if data_validation['warnings']:
            for warning in data_validation['warnings']:
                logger.warning(f"Data warning: {warning}")
        
        # Prepare data for Excel generation
        excel_data = await excel_generator.prepare_data(export_data)
        
        # Generate workbook
        output_path = await excel_generator.generate_workbook(excel_data, template_type)
        
        logger.info(f"Excel report generated successfully: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Excel generation error: {str(e)}")
        return None
    # Note: We're NOT cleaning up automatically anymore - let files persist for copying


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