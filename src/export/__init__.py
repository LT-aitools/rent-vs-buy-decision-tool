"""
Excel/PDF Export System
Professional export functionality for Real Estate Decision Tool

This module provides comprehensive export capabilities including:
- Excel workbooks with multiple worksheets and embedded charts
- PDF reports with executive summaries and detailed analysis  
- Template system for customized reporting
- High-resolution chart rendering and data formatting

Export Process Flow:
1. Data Collection: Gather analysis results and user inputs
2. Validation: Ensure data completeness and accuracy
3. Chart Rendering: Convert interactive charts to images
4. File Generation: Create Excel/PDF with professional formatting
5. Quality Assurance: Validate output before delivery

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

try:
    from .file_manager import FileManager, ExportFile
    FILE_MANAGER_AVAILABLE = True
except ImportError:
    FILE_MANAGER_AVAILABLE = False

try:
    from .validation import validate_export_data, ExportValidationError
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

try:
    from .pdf_integration import PDFExportManager
    PDF_INTEGRATION_AVAILABLE = True
except ImportError:
    PDF_INTEGRATION_AVAILABLE = False

try:
    from .streamlit_integration import ExcelExportManager
    EXCEL_INTEGRATION_AVAILABLE = True
except ImportError:
    EXCEL_INTEGRATION_AVAILABLE = False

__version__ = "1.0.0"
__all__ = []

# Add available components to __all__
if FILE_MANAGER_AVAILABLE:
    __all__.extend(['FileManager', 'ExportFile'])

if VALIDATION_AVAILABLE:
    __all__.extend(['validate_export_data', 'ExportValidationError'])

if PDF_INTEGRATION_AVAILABLE:
    __all__.append('PDFExportManager')

if EXCEL_INTEGRATION_AVAILABLE:
    __all__.append('ExcelExportManager')