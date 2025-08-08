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

from .export_coordinator import ExportCoordinator, ExportOptions
from .file_manager import FileManager, ExportFile
from .validation import validate_export_data, ExportValidationError

__version__ = "1.0.0"
__all__ = [
    # Main coordinator
    'ExportCoordinator',
    'ExportOptions', 
    
    # File management
    'FileManager',
    'ExportFile',
    
    # Validation
    'validate_export_data',
    'ExportValidationError'
]