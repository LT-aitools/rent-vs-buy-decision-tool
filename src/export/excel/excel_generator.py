"""
Excel Generator
Main engine for creating comprehensive Excel workbooks with financial analysis

Creates professional Excel workbooks with multiple worksheets containing
analysis results, charts, calculations, and formatted data suitable for
executive review and stakeholder sharing.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import tempfile

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, Fill, Border, Side, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.drawing.image import Image

from .data_formatting import ExcelFormatter
from .chart_embedding import ChartEmbedder
from .template_manager import ExcelTemplateManager


# Configure logging
logger = logging.getLogger(__name__)


class ExcelGenerator:
    """
    Professional Excel workbook generator for real estate analysis
    
    Creates comprehensive workbooks with multiple worksheets, embedded charts,
    and professional formatting suitable for executive presentation.
    """
    
    def __init__(self, temp_dir: Optional[Path] = None):
        """
        Initialize Excel generator
        
        Args:
            temp_dir: Directory for temporary files during generation
        """
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "excel_generation"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.formatter = ExcelFormatter()
        self.chart_embedder = ChartEmbedder()
        self.template_manager = ExcelTemplateManager()
        
        # Workbook components
        self.workbook: Optional[Workbook] = None
        self.worksheets: Dict[str, Worksheet] = {}
        
        logger.info(f"ExcelGenerator initialized with temp_dir: {self.temp_dir}")
    
    async def prepare_data(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data for Excel generation
        
        Args:
            export_data: Complete export data package
            
        Returns:
            Excel-specific data package with formatted tables and calculations
        """
        logger.info("Preparing data for Excel generation")
        
        excel_data = {
            # Core data from export package
            'analysis_results': export_data['analysis_results'],
            'ownership_flows': export_data['ownership_flows'],
            'rental_flows': export_data['rental_flows'],
            'session_data': export_data['session_data'],
            'export_options': export_data['export_options'],
            
            # Excel-specific formatted data
            'formatted_tables': {},
            'summary_metrics': {},
            'chart_data': {},
            'worksheet_configs': {}
        }
        
        # Format data for different worksheets
        await self._prepare_summary_data(excel_data)
        await self._prepare_cash_flow_data(excel_data) 
        await self._prepare_calculations_data(excel_data)
        await self._prepare_assumptions_data(excel_data)
        
        logger.info("Excel data preparation completed")
        return excel_data
    
    async def render_charts(
        self, 
        export_data: Dict[str, Any], 
        resolution: int = 300
    ) -> Dict[str, Path]:
        """
        Render interactive charts as high-resolution images for Excel embedding
        
        Args:
            export_data: Export data with chart configurations
            resolution: Chart resolution in DPI
            
        Returns:
            Dictionary mapping chart names to image file paths
        """
        logger.info(f"Rendering charts for Excel at {resolution} DPI")
        
        chart_images = await self.chart_embedder.render_all_charts(
            export_data, resolution, self.temp_dir
        )
        
        logger.info(f"Rendered {len(chart_images)} charts for Excel")
        return chart_images
    
    async def generate_workbook(
        self,
        excel_data: Dict[str, Any],
        template_type: str = "detailed"
    ) -> Path:
        """
        Generate complete Excel workbook with all worksheets and formatting
        
        Args:
            excel_data: Prepared Excel data package
            template_type: Template type ("executive", "detailed", "investor")
            
        Returns:
            Path to generated Excel file
        """
        logger.info(f"Generating Excel workbook with template: {template_type}")
        
        try:
            # Initialize workbook
            self.workbook = Workbook()
            self.workbook.remove(self.workbook.active)  # Remove default sheet
            
            # Apply template configuration
            template_config = await self.template_manager.get_template_config(template_type)
            
            # Create worksheets based on template
            await self._create_worksheets(excel_data, template_config)
            
            # Apply professional styling
            await self._apply_workbook_styling(template_config)
            
            # Generate output file
            output_path = self.temp_dir / f"real_estate_analysis_{template_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Save workbook
            self.workbook.save(output_path)
            
            logger.info(f"Excel workbook generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Excel workbook generation failed: {str(e)}")
            raise RuntimeError(f"Excel generation failed: {str(e)}") from e
    
    async def _prepare_summary_data(self, excel_data: Dict[str, Any]) -> None:
        """Prepare executive summary data"""
        analysis = excel_data['analysis_results']
        
        summary_data = {
            'recommendation': analysis.get('recommendation', 'UNKNOWN'),
            'confidence': analysis.get('confidence', 'Low'),
            'npv_difference': analysis.get('npv_difference', 0),
            'ownership_npv': analysis.get('ownership_npv', 0),
            'rental_npv': analysis.get('rental_npv', 0),
            'ownership_initial_investment': analysis.get('ownership_initial_investment', 0),
            'rental_initial_investment': analysis.get('rental_initial_investment', 0),
            'analysis_period': analysis.get('analysis_period', 25),
            'cost_of_capital': analysis.get('cost_of_capital', 8.0)
        }
        
        excel_data['summary_metrics'] = summary_data
    
    async def _prepare_cash_flow_data(self, excel_data: Dict[str, Any]) -> None:
        """Prepare cash flow analysis data"""
        ownership_flows = excel_data['ownership_flows']
        rental_flows = excel_data['rental_flows']
        
        # Create formatted cash flow tables
        formatted_flows = {
            'ownership_table': await self.formatter.format_cash_flow_table(ownership_flows, "ownership"),
            'rental_table': await self.formatter.format_cash_flow_table(rental_flows, "rental"),
            'comparison_table': await self.formatter.create_comparison_table(ownership_flows, rental_flows)
        }
        
        excel_data['formatted_tables']['cash_flows'] = formatted_flows
    
    async def _prepare_calculations_data(self, excel_data: Dict[str, Any]) -> None:
        """Prepare detailed calculations data"""
        analysis = excel_data['analysis_results']
        
        # Extract calculation details
        calculations = {
            'npv_calculations': await self.formatter.format_npv_calculations(analysis),
            'mortgage_schedule': await self.formatter.format_mortgage_schedule(analysis),
            'tax_calculations': await self.formatter.format_tax_calculations(analysis),
            'terminal_value': await self.formatter.format_terminal_value(analysis)
        }
        
        excel_data['formatted_tables']['calculations'] = calculations
    
    async def _prepare_assumptions_data(self, excel_data: Dict[str, Any]) -> None:
        """Prepare input assumptions data"""
        session_data = excel_data['session_data']
        
        # Format assumptions by category
        assumptions = await self.formatter.format_assumptions_table(session_data)
        excel_data['formatted_tables']['assumptions'] = assumptions
    
    async def _create_worksheets(
        self, 
        excel_data: Dict[str, Any], 
        template_config: Dict[str, Any]
    ) -> None:
        """Create all worksheets based on template configuration"""
        
        worksheet_configs = template_config.get('worksheets', [])
        
        for config in worksheet_configs:
            worksheet_name = config['name']
            worksheet_type = config['type']
            
            # Create worksheet
            ws = self.workbook.create_sheet(title=worksheet_name)
            self.worksheets[worksheet_name] = ws
            
            # Populate worksheet based on type
            await self._populate_worksheet(ws, worksheet_type, excel_data, config)
    
    async def _populate_worksheet(
        self,
        ws: Worksheet,
        worksheet_type: str,
        excel_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Populate individual worksheet with data and formatting"""
        
        if worksheet_type == "executive_summary":
            await self._create_executive_summary_sheet(ws, excel_data, config)
        elif worksheet_type == "cash_flows":
            await self._create_cash_flows_sheet(ws, excel_data, config)
        elif worksheet_type == "charts":
            await self._create_charts_sheet(ws, excel_data, config)
        elif worksheet_type == "calculations":
            await self._create_calculations_sheet(ws, excel_data, config)
        elif worksheet_type == "assumptions":
            await self._create_assumptions_sheet(ws, excel_data, config)
        else:
            logger.warning(f"Unknown worksheet type: {worksheet_type}")
    
    async def _create_executive_summary_sheet(
        self,
        ws: Worksheet,
        excel_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Create executive summary worksheet"""
        summary = excel_data['summary_metrics']
        
        # Title section
        ws['A1'] = "Real Estate Investment Analysis"
        ws['A1'].font = Font(size=16, bold=True)
        
        ws['A2'] = f"Executive Summary - {datetime.now().strftime('%B %d, %Y')}"
        ws['A2'].font = Font(size=12, italic=True)
        
        # Recommendation section
        row = 4
        ws[f'A{row}'] = "RECOMMENDATION"
        ws[f'A{row}'].font = Font(size=14, bold=True)
        
        row += 1
        recommendation = summary['recommendation']
        ws[f'B{row}'] = recommendation
        ws[f'B{row}'].font = Font(size=12, bold=True)
        
        # Color code recommendation
        if recommendation == "BUY":
            ws[f'B{row}'].fill = PatternFill(start_color="96CEB4", end_color="96CEB4", fill_type="solid")
        elif recommendation == "RENT":
            ws[f'B{row}'].fill = PatternFill(start_color="FECA57", end_color="FECA57", fill_type="solid")
        
        # Key metrics section
        row += 3
        ws[f'A{row}'] = "KEY FINANCIAL METRICS"
        ws[f'A{row}'].font = Font(size=14, bold=True)
        
        row += 1
        metrics = [
            ("NPV Advantage", summary['npv_difference']),
            ("Ownership NPV", summary['ownership_npv']),
            ("Rental NPV", summary['rental_npv']),
            ("Initial Investment", summary['ownership_initial_investment']),
            ("Analysis Period", f"{summary['analysis_period']} years"),
            ("Cost of Capital", f"{summary['cost_of_capital']:.1f}%")
        ]
        
        for metric_name, metric_value in metrics:
            ws[f'A{row}'] = metric_name
            ws[f'B{row}'] = metric_value
            
            # Format currency values
            if isinstance(metric_value, (int, float)) and abs(metric_value) > 1000:
                ws[f'B{row}'].number_format = '$#,##0'
            
            row += 1
    
    async def _create_cash_flows_sheet(
        self,
        ws: Worksheet,
        excel_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Create cash flows analysis worksheet"""
        cash_flows = excel_data['formatted_tables']['cash_flows']
        
        # Title
        ws['A1'] = "Cash Flow Analysis"
        ws['A1'].font = Font(size=16, bold=True)
        
        # Ownership cash flows
        await self._insert_data_table(ws, cash_flows['ownership_table'], start_row=3, title="Ownership Cash Flows")
        
        # Rental cash flows  
        ownership_rows = len(cash_flows['ownership_table'].get('data', [])) + 5
        await self._insert_data_table(ws, cash_flows['rental_table'], start_row=ownership_rows, title="Rental Cash Flows")
        
        # Comparison table
        total_rows = ownership_rows + len(cash_flows['rental_table'].get('data', [])) + 5
        await self._insert_data_table(ws, cash_flows['comparison_table'], start_row=total_rows, title="Side-by-Side Comparison")
    
    async def _create_charts_sheet(
        self,
        ws: Worksheet,
        excel_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Create charts and visualizations worksheet"""
        chart_images = excel_data.get('chart_images', {})
        
        ws['A1'] = "Charts & Visualizations"
        ws['A1'].font = Font(size=16, bold=True)
        
        # Embed charts as images
        row = 3
        for chart_name, image_path in chart_images.items():
            if Path(image_path).exists():
                try:
                    img = Image(str(image_path))
                    img.width = 600  # Adjust size as needed
                    img.height = 400
                    
                    ws.add_image(img, f'A{row}')
                    row += 25  # Space between charts
                    
                except Exception as e:
                    logger.warning(f"Failed to embed chart {chart_name}: {str(e)}")
    
    async def _create_calculations_sheet(
        self,
        ws: Worksheet,
        excel_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Create detailed calculations worksheet"""
        calculations = excel_data['formatted_tables']['calculations']
        
        ws['A1'] = "Detailed Calculations"
        ws['A1'].font = Font(size=16, bold=True)
        
        current_row = 3
        
        # Insert each calculation section
        for calc_name, calc_data in calculations.items():
            title = calc_name.replace('_', ' ').title()
            await self._insert_data_table(ws, calc_data, start_row=current_row, title=title)
            current_row += len(calc_data.get('data', [])) + 5
    
    async def _create_assumptions_sheet(
        self,
        ws: Worksheet,
        excel_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> None:
        """Create input assumptions worksheet"""
        assumptions = excel_data['formatted_tables']['assumptions']
        
        ws['A1'] = "Input Assumptions & Parameters"
        ws['A1'].font = Font(size=16, bold=True)
        
        await self._insert_data_table(ws, assumptions, start_row=3, title="All Input Parameters")
    
    async def _insert_data_table(
        self,
        ws: Worksheet,
        table_data: Dict[str, Any],
        start_row: int,
        title: str
    ) -> None:
        """Insert formatted data table into worksheet"""
        
        # Section title
        ws[f'A{start_row}'] = title
        ws[f'A{start_row}'].font = Font(size=14, bold=True)
        
        # Headers
        headers = table_data.get('headers', [])
        data_rows = table_data.get('data', [])
        
        header_row = start_row + 2
        for col_idx, header in enumerate(headers):
            col_letter = get_column_letter(col_idx + 1)
            ws[f'{col_letter}{header_row}'] = header
            ws[f'{col_letter}{header_row}'].font = Font(bold=True)
        
        # Data rows
        for row_idx, data_row in enumerate(data_rows):
            excel_row = header_row + row_idx + 1
            for col_idx, cell_value in enumerate(data_row):
                col_letter = get_column_letter(col_idx + 1)
                ws[f'{col_letter}{excel_row}'] = cell_value
                
                # Apply formatting based on data type
                if isinstance(cell_value, (int, float)) and abs(cell_value) > 1000:
                    ws[f'{col_letter}{excel_row}'].number_format = '$#,##0'
    
    async def _apply_workbook_styling(self, template_config: Dict[str, Any]) -> None:
        """Apply professional styling to entire workbook"""
        
        for ws in self.workbook.worksheets:
            # Set column widths
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            # Apply borders and formatting
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value is not None:
                        cell.border = Border(
                            left=Side(style='thin'),
                            right=Side(style='thin'), 
                            top=Side(style='thin'),
                            bottom=Side(style='thin')
                        )
                        cell.alignment = Alignment(vertical='center')
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.workbook:
            try:
                self.workbook.close()
            except:
                pass