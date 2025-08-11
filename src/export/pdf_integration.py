"""
PDF Integration Layer
Integration between PDF report generation and Streamlit application

This module provides:
- Functions to generate PDF reports from analysis data
- Integration with Streamlit download system
- Template selection and customization interface
- Progress tracking and error handling for PDF generation
- Unified interface for PDF export functionality

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime
import io

# Streamlit integration
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    logging.warning("Streamlit not available - some features will be limited")

# PDF generation imports
try:
    from .pdf.pdf_generator import PDFGenerator
    from .pdf.chart_renderer import PDFChartRenderer
    from .pdf.layout_engine import LayoutEngine
    from .pdf.executive_templates import ExecutiveTemplateBuilder, TemplateConfig, TemplateType
    PDF_SYSTEM_AVAILABLE = True
except ImportError:
    PDF_SYSTEM_AVAILABLE = False
    logging.warning("PDF system not available - PDF generation will be disabled")

logger = logging.getLogger(__name__)


class PDFExportManager:
    """
    Manager class for PDF export operations
    
    Provides high-level interface for generating PDF reports with different templates,
    managing chart rendering, and integrating with Streamlit UI components.
    """
    
    def __init__(self):
        """Initialize PDF export manager"""
        if not PDF_SYSTEM_AVAILABLE:
            raise ImportError("PDF system components are required")
        
        self.pdf_generator = PDFGenerator()
        self.chart_renderer = PDFChartRenderer(output_resolution=300)
        
        # Template configurations
        self.template_configs = {
            'executive': TemplateConfig(
                template_type=TemplateType.EXECUTIVE,
                page_size='letter',
                margin_preset='executive',
                color_scheme='corporate'
            ),
            'detailed': TemplateConfig(
                template_type=TemplateType.DETAILED,
                page_size='letter',
                margin_preset='standard',
                color_scheme='professional'
            ),
            'investor': TemplateConfig(
                template_type=TemplateType.INVESTOR,
                page_size='letter',
                margin_preset='executive',
                color_scheme='investor'
            )
        }
        
        logger.info("PDF Export Manager initialized")
    
    async def generate_pdf_report(
        self,
        export_data: Dict[str, Any],
        template_type: str = 'executive',
        custom_config: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable] = None
    ) -> Tuple[Path, Dict[str, Any]]:
        """
        Generate complete PDF report with charts
        
        Args:
            export_data: Complete export data from analysis
            template_type: Template type ('executive', 'detailed', 'investor')
            custom_config: Custom configuration overrides
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple of (pdf_path, generation_info)
        """
        logger.info(f"Generating PDF report: {template_type}")
        
        generation_info = {
            'start_time': datetime.now(),
            'template_type': template_type,
            'success': False,
            'charts_rendered': 0,
            'pages_generated': 0,
            'file_size': 0,
            'errors': []
        }
        
        try:
            # Update progress
            if progress_callback:
                progress_callback("Initializing PDF generation...", 0.1)
            
            # Validate export data
            validation = self.pdf_generator.validate_export_data(export_data)
            if not validation['is_valid']:
                raise ValueError(f"Invalid export data: {validation}")
            
            # Set up temporary directory for charts
            temp_dir = Path(tempfile.mkdtemp()) / "pdf_generation"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Update progress
            if progress_callback:
                progress_callback("Rendering charts for PDF...", 0.3)
            
            # Render charts optimized for PDF
            if template_type == 'executive':
                chart_images = await self.chart_renderer.render_executive_summary_charts(
                    export_data, temp_dir
                )
            elif template_type == 'detailed':
                chart_images = await self.chart_renderer.render_detailed_analysis_charts(
                    export_data, temp_dir
                )
            elif template_type == 'investor':
                chart_images = await self.chart_renderer.render_investor_presentation_charts(
                    export_data, temp_dir
                )
            else:
                raise ValueError(f"Unknown template type: {template_type}")
            
            generation_info['charts_rendered'] = len(chart_images)
            
            # Update progress
            if progress_callback:
                progress_callback("Generating PDF document...", 0.7)
            
            # Generate PDF with template
            template_config = self.template_configs[template_type]
            if custom_config:
                # Apply custom configuration
                for key, value in custom_config.items():
                    if hasattr(template_config, key):
                        setattr(template_config, key, value)
            
            template_builder = ExecutiveTemplateBuilder(template_config)
            
            # Build content based on template type
            if template_type == 'executive':
                story = template_builder.build_executive_summary(export_data, chart_images)
            elif template_type == 'detailed':
                story = template_builder.build_detailed_analysis(export_data, chart_images)
            elif template_type == 'investor':
                story = template_builder.build_investor_presentation(export_data, chart_images)
            
            # Generate final PDF using template builder's layout engine
            pdf_path = Path(tempfile.mktemp(suffix='.pdf'))
            
            # Use the template builder's document creation instead of the basic generator
            from reportlab.platypus import SimpleDocTemplate
            
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=template_builder.layout.page_size,
                topMargin=template_builder.layout.margins['top'],
                bottomMargin=template_builder.layout.margins['bottom'],
                leftMargin=template_builder.layout.margins['left'],
                rightMargin=template_builder.layout.margins['right'],
                title="Real Estate Investment Analysis",
                subject="Investment Analysis and Recommendation",
                author="Real Estate Decision Tool"
            )
            
            doc.build(story)
            
            # Update generation info
            generation_info['success'] = True
            generation_info['file_size'] = pdf_path.stat().st_size
            generation_info['end_time'] = datetime.now()
            generation_info['duration'] = (generation_info['end_time'] - generation_info['start_time']).total_seconds()
            
            # Update progress
            if progress_callback:
                progress_callback("PDF generation complete!", 1.0)
            
            # Clean up temporary charts
            self.chart_renderer.cleanup_temp_charts(chart_images)
            
            logger.info(f"PDF report generated successfully: {pdf_path}")
            
        except Exception as e:
            generation_info['errors'].append(str(e))
            logger.error(f"Error generating PDF report: {str(e)}")
            raise
        
        return pdf_path, generation_info
    
    def create_streamlit_download_button(
        self,
        export_data: Dict[str, Any],
        template_type: str = 'executive',
        button_label: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create Streamlit download button for PDF report
        
        Args:
            export_data: Export data for report generation
            template_type: Template type to generate
            button_label: Custom button label
            custom_config: Custom configuration
            
        Returns:
            True if button was clicked and download initiated
        """
        if not STREAMLIT_AVAILABLE:
            logger.error("Streamlit not available for download button")
            return False
        
        if button_label is None:
            button_label = f"Download {template_type.title()} PDF Report"
        
        # Create download button
        if st.button(button_label, key=f"pdf_download_{template_type}"):
            try:
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(message: str, progress: float):
                    progress_bar.progress(progress)
                    status_text.text(message)
                
                # Generate PDF asynchronously
                with st.spinner("Generating PDF report..."):
                    pdf_path, generation_info = asyncio.run(
                        self.generate_pdf_report(
                            export_data=export_data,
                            template_type=template_type,
                            custom_config=custom_config,
                            progress_callback=update_progress
                        )
                    )
                
                # Read PDF for download
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_bytes = pdf_file.read()
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"real_estate_analysis_{template_type}_{timestamp}.pdf"
                
                # Create download button
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    key=f"pdf_download_final_{template_type}"
                )
                
                # Show generation info
                st.success(f"✅ PDF report generated successfully!")
                
                with st.expander("Generation Details"):
                    st.write(f"**Template:** {generation_info['template_type'].title()}")
                    st.write(f"**Charts Rendered:** {generation_info['charts_rendered']}")
                    st.write(f"**File Size:** {generation_info['file_size']:,} bytes")
                    st.write(f"**Generation Time:** {generation_info.get('duration', 0):.2f} seconds")
                
                # Clean up
                try:
                    pdf_path.unlink()
                except:
                    pass
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                return True
                
            except Exception as e:
                st.error(f"❌ Error generating PDF report: {str(e)}")
                logger.error(f"Error in Streamlit PDF download: {str(e)}")
                
                # Clear progress indicators
                try:
                    progress_bar.empty()
                    status_text.empty()
                except:
                    pass
        
        return False
    
    def create_template_selector(self, key_suffix: str = "") -> str:
        """
        Create Streamlit template selector widget
        
        Args:
            key_suffix: Suffix for widget key uniqueness
            
        Returns:
            Selected template type
        """
        if not STREAMLIT_AVAILABLE:
            return 'executive'
        
        template_options = {
            'executive': {
                'name': '📊 Executive Summary',
                'description': '2-3 pages with key metrics and recommendation',
                'audience': 'Executives, Decision Makers'
            },
            'detailed': {
                'name': '📈 Detailed Analysis',
                'description': '8-12 pages with comprehensive analysis and charts',
                'audience': 'Analysts, Finance Teams'
            },
            'investor': {
                'name': '💼 Investor Presentation',
                'description': '6-8 pages focused on investment thesis and returns',
                'audience': 'Investors, Stakeholders'
            }
        }
        
        st.subheader("📄 PDF Report Templates")
        
        selected_template = st.radio(
            "Select Report Template:",
            options=list(template_options.keys()),
            format_func=lambda x: template_options[x]['name'],
            key=f"template_selector{key_suffix}"
        )
        
        # Show template details
        template_info = template_options[selected_template]
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Description:** {template_info['description']}")
        with col2:
            st.write(f"**Target Audience:** {template_info['audience']}")
        
        return selected_template
    
    def create_customization_options(self, key_suffix: str = "") -> Dict[str, Any]:
        """
        Create Streamlit customization options interface
        
        Args:
            key_suffix: Suffix for widget key uniqueness
            
        Returns:
            Dictionary of customization options
        """
        if not STREAMLIT_AVAILABLE:
            return {}
        
        st.subheader("🎨 Customization Options")
        
        customization = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Page size options
            customization['page_size'] = st.selectbox(
                "Page Size:",
                options=['letter', 'A4'],
                index=0,
                key=f"page_size{key_suffix}"
            )
            
            # Color scheme options
            customization['color_scheme'] = st.selectbox(
                "Color Scheme:",
                options=['corporate', 'professional', 'investor'],
                index=0,
                key=f"color_scheme{key_suffix}"
            )
        
        with col2:
            # Margin options
            customization['margin_preset'] = st.selectbox(
                "Margins:",
                options=['executive', 'standard', 'narrow', 'wide'],
                index=0,
                key=f"margins{key_suffix}"
            )
            
            # Additional options
            customization['include_toc'] = st.checkbox(
                "Include Table of Contents",
                value=False,
                key=f"toc{key_suffix}"
            )
        
        return customization
    
    def create_export_interface(self, export_data: Dict[str, Any], key_suffix: str = "") -> None:
        """
        Create complete PDF export interface for Streamlit
        
        Args:
            export_data: Export data for report generation
            key_suffix: Suffix for widget key uniqueness
        """
        if not STREAMLIT_AVAILABLE:
            logger.error("Streamlit not available for export interface")
            return
        
        st.header("📄 PDF Report Export")
        
        # Validate data first
        validation = self.pdf_generator.validate_export_data(export_data)
        
        if not validation['is_valid']:
            st.error("❌ Export data is not ready for PDF generation")
            
            missing_items = []
            if not validation['has_analysis_results']:
                missing_items.append("Analysis results")
            if not validation['has_recommendation']:
                missing_items.append("Investment recommendation")
            if not validation['reportlab_available']:
                missing_items.append("ReportLab library")
            
            st.write("**Missing components:**")
            for item in missing_items:
                st.write(f"• {item}")
            
            return
        
        # Show validation success
        st.success("✅ Analysis data ready for PDF export")
        
        # Template selection
        selected_template = self.create_template_selector(key_suffix)
        
        # Customization options
        with st.expander("🎨 Customization Options", expanded=False):
            custom_config = self.create_customization_options(key_suffix)
        
        # Export buttons
        st.subheader("📥 Download Reports")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self.create_streamlit_download_button(
                export_data=export_data,
                template_type='executive',
                button_label="📊 Executive Summary",
                custom_config=custom_config if selected_template == 'executive' else None
            )
        
        with col2:
            self.create_streamlit_download_button(
                export_data=export_data,
                template_type='detailed',
                button_label="📈 Detailed Analysis",
                custom_config=custom_config if selected_template == 'detailed' else None
            )
        
        with col3:
            self.create_streamlit_download_button(
                export_data=export_data,
                template_type='investor',
                button_label="💼 Investor Report",
                custom_config=custom_config if selected_template == 'investor' else None
            )
        
        # Additional information
        with st.expander("ℹ️ About PDF Reports", expanded=False):
            st.markdown("""
            **PDF Report Features:**
            - Professional layouts with corporate branding
            - High-resolution charts optimized for printing
            - Comprehensive financial analysis and recommendations
            - Multiple templates for different audiences
            - Print-ready quality (300 DPI)
            
            **Template Comparison:**
            - **Executive Summary:** Quick overview for decision makers
            - **Detailed Analysis:** Complete analysis with all charts and tables
            - **Investor Presentation:** Investment-focused with risk analysis
            """)
    
    def get_export_capabilities(self) -> Dict[str, Any]:
        """
        Get information about PDF export capabilities
        
        Returns:
            Dictionary with export capabilities and system status
        """
        return {
            'pdf_system_available': PDF_SYSTEM_AVAILABLE,
            'streamlit_available': STREAMLIT_AVAILABLE,
            'templates': list(self.template_configs.keys()) if PDF_SYSTEM_AVAILABLE else [],
            'supported_templates': list(self.template_configs.keys()) if PDF_SYSTEM_AVAILABLE else [],
            'chart_rendering_available': hasattr(self, 'chart_renderer'),
            'template_configurations': {
                template_type: {
                    'page_size': config.page_size,
                    'margin_preset': config.margin_preset,
                    'color_scheme': config.color_scheme
                }
                for template_type, config in (self.template_configs.items() if PDF_SYSTEM_AVAILABLE else {}.items())
            },
            'system_requirements': {
                'reportlab': 'Required for PDF generation',
                'pillow': 'Required for image optimization',
                'plotly': 'Required for chart rendering',
                'streamlit': 'Required for UI integration'
            }
        }


# Convenience functions for direct use
async def generate_executive_summary_pdf(export_data: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
    """
    Generate executive summary PDF report
    
    Args:
        export_data: Complete export data
        output_path: Output path for PDF
        
    Returns:
        Path to generated PDF
    """
    manager = PDFExportManager()
    pdf_path, _ = await manager.generate_pdf_report(export_data, 'executive')
    
    if output_path:
        import shutil
        shutil.move(pdf_path, output_path)
        return output_path
    
    return pdf_path


async def generate_detailed_analysis_pdf(export_data: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
    """
    Generate detailed analysis PDF report
    
    Args:
        export_data: Complete export data
        output_path: Output path for PDF
        
    Returns:
        Path to generated PDF
    """
    manager = PDFExportManager()
    pdf_path, _ = await manager.generate_pdf_report(export_data, 'detailed')
    
    if output_path:
        import shutil
        shutil.move(pdf_path, output_path)
        return output_path
    
    return pdf_path


async def generate_investor_presentation_pdf(export_data: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
    """
    Generate investor presentation PDF report
    
    Args:
        export_data: Complete export data
        output_path: Output path for PDF
        
    Returns:
        Path to generated PDF
    """
    manager = PDFExportManager()
    pdf_path, _ = await manager.generate_pdf_report(export_data, 'investor')
    
    if output_path:
        import shutil
        shutil.move(pdf_path, output_path)
        return output_path
    
    return pdf_path


def create_streamlit_pdf_export_section(export_data: Dict[str, Any]) -> None:
    """
    Create complete PDF export section for Streamlit app
    
    Args:
        export_data: Export data for report generation
    """
    try:
        manager = PDFExportManager()
        manager.create_export_interface(export_data)
    except ImportError:
        if STREAMLIT_AVAILABLE:
            st.error("❌ PDF generation system not available. Please install required dependencies.")
            st.code("pip install reportlab Pillow pypdf")
        else:
            logger.error("Neither PDF system nor Streamlit available for export section")