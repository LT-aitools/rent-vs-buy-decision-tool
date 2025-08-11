"""
PDF Export System
Professional PDF report generation for Real Estate Decision Tool

This module provides PDF export capabilities including:
- Executive summary reports with key metrics and recommendations
- Detailed analysis reports with embedded charts and data tables
- Professional formatting with corporate branding
- High-resolution chart rendering and data visualization

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

try:
    from .pdf_generator import PDFGenerator
    from .layout_engine import LayoutEngine, LayoutDimensions, ContentType
    from .chart_renderer import PDFChartRenderer
    from .executive_templates import ExecutiveTemplateBuilder, TemplateConfig, TemplateType
    
    __all__ = [
        'PDFGenerator',
        'LayoutEngine',
        'LayoutDimensions', 
        'ContentType',
        'PDFChartRenderer',
        'ExecutiveTemplateBuilder',
        'TemplateConfig',
        'TemplateType'
    ]
    
    PDF_SYSTEM_AVAILABLE = True
    
except ImportError as e:
    # Graceful degradation if dependencies not available
    __all__ = []
    PDF_SYSTEM_AVAILABLE = False
    import logging
    logging.warning(f"PDF system not fully available: {e}")

__version__ = "1.0.0"