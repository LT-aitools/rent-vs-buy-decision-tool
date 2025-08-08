"""
Excel Export System
Professional Excel workbook generation with multiple worksheets and embedded charts

This module creates comprehensive Excel workbooks containing:
- Executive summary with key metrics and recommendations
- Cash flow analysis with year-by-year breakdowns
- Interactive charts embedded as high-resolution images
- Detailed calculations with all intermediate values
- Input assumptions and parameter documentation
- Sensitivity analysis results (when available)

Technical Features:
- Professional styling with corporate color schemes
- Conditional formatting for financial data
- Print-ready layouts with proper page breaks
- Chart embedding with underlying data tables
- Formula preservation for user analysis

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

from .excel_generator import ExcelGenerator
from .chart_embedding import ChartEmbedder
from .data_formatting import ExcelFormatter
from .template_manager import ExcelTemplateManager

__all__ = [
    'ExcelGenerator',
    'ChartEmbedder', 
    'ExcelFormatter',
    'ExcelTemplateManager'
]