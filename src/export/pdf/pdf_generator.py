"""
PDF Report Generation System
Professional PDF generation for Real Estate Decision Tool

This module provides:
- Professional multi-page PDF report generation using ReportLab
- Corporate branding and styling with consistent color scheme
- Integration with existing chart rendering system
- Support for Executive Summary, Detailed Analysis, and Investor Presentation formats
- High-quality chart embedding and layout management

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import tempfile
import io

# ReportLab imports for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch, mm
    from reportlab.lib.colors import Color, HexColor, black, white, gray
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
        PageBreak, Image, KeepTogether, NextPageTemplate, PageTemplate,
        BaseDocTemplate, Frame
    )
    from reportlab.platypus.tableofcontents import TableOfContents
    from reportlab.lib.utils import ImageReader
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available - PDF generation will be disabled")

# Image processing
try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("Pillow not available - image processing may be limited")

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Professional PDF report generator for Real Estate Decision Tool
    
    Provides comprehensive PDF generation with:
    - Corporate branding and consistent styling
    - Multi-page report layouts
    - Chart integration and high-quality embedding
    - Professional typography and formatting
    - Template-based report generation
    """
    
    # Corporate color scheme (#FF6B6B primary) - initialized in __init__
    COLORS = None
    
    def __init__(self, page_size: str = 'letter'):
        """
        Initialize PDF generator with professional settings
        
        Args:
            page_size: Page size ('letter', 'A4')
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation")
        
        self.page_size = letter if page_size.lower() == 'letter' else A4
        
        # Initialize enhanced color scheme for professional documents
        self.COLORS = {
            'primary': HexColor('#FF6B6B'),           # Primary coral red
            'secondary': HexColor('#74B9FF'),         # Professional blue accent
            'success': HexColor('#00B894'),           # Strong green for positive metrics
            'warning': HexColor('#FDCB6E'),           # Warm yellow for caution
            'danger': HexColor('#E17055'),            # Muted red for negative metrics
            'dark': HexColor('#2D3436'),              # Dark charcoal text
            'light': HexColor('#F8F9FA'),             # Clean light background
            'muted': HexColor('#636E72'),             # Professional muted text
            'accent': HexColor('#A29BFE'),            # Purple accent
            'neutral': HexColor('#DDD6D6'),           # Neutral gray
            'white': white,
            'black': black,
            'gray': HexColor('#B2BEC3')               # Softer gray
        }
        # Optimized margins for professional documents
        self.margins = {
            'top': 0.9 * inch,
            'bottom': 0.9 * inch,
            'left': 0.8 * inch,
            'right': 0.8 * inch
        }
        
        # Initialize styles
        self.styles = self._create_styles()
        
        # Document properties
        self.title = "Real Estate Decision Analysis Report"
        self.subject = "Investment Analysis and Recommendation"
        self.author = "Real Estate Decision Tool"
        self.creator = "LT-aitools Decision Tool"
        
        logger.info("PDF Generator initialized with professional settings")
    
    def _create_styles(self) -> Dict[str, Any]:
        """Create custom paragraph and text styles for consistent formatting"""
        
        base_styles = getSampleStyleSheet()
        custom_styles = {}
        
        # Title style - Improved hierarchy
        custom_styles['Title'] = ParagraphStyle(
            'CustomTitle',
            parent=base_styles['Title'],
            fontSize=22,
            spaceAfter=20,
            spaceBefore=8,
            textColor=self.COLORS['primary'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=26
        )
        
        # Heading styles - Better spacing and hierarchy
        custom_styles['Heading1'] = ParagraphStyle(
            'CustomHeading1',
            parent=base_styles['Heading1'],
            fontSize=16,
            spaceAfter=14,
            spaceBefore=22,
            textColor=self.COLORS['dark'],
            fontName='Helvetica-Bold',
            leading=18
        )
        
        custom_styles['Heading2'] = ParagraphStyle(
            'CustomHeading2',
            parent=base_styles['Heading2'],
            fontSize=13,
            spaceAfter=10,
            spaceBefore=18,
            textColor=self.COLORS['dark'],
            fontName='Helvetica-Bold',
            leading=15
        )
        
        custom_styles['Heading3'] = ParagraphStyle(
            'CustomHeading3',
            fontSize=12,
            spaceAfter=6,
            spaceBefore=12,
            textColor=self.COLORS['muted'],
            fontName='Helvetica-Bold'
        )
        
        # Body text styles
        custom_styles['Normal'] = ParagraphStyle(
            'CustomNormal',
            parent=base_styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=self.COLORS['dark'],
            fontName='Helvetica',
            alignment=TA_JUSTIFY
        )
        
        custom_styles['BodyText'] = ParagraphStyle(
            'CustomBodyText',
            parent=base_styles['BodyText'],
            fontSize=11,
            spaceAfter=8,
            textColor=self.COLORS['dark'],
            fontName='Helvetica',
            alignment=TA_JUSTIFY
        )
        
        # Special styles
        custom_styles['Recommendation'] = ParagraphStyle(
            'Recommendation',
            fontSize=16,
            spaceAfter=12,
            spaceBefore=12,
            textColor=self.COLORS['primary'],
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            borderWidth=2,
            borderColor=self.COLORS['primary'],
            borderPadding=12,
            backColor=self.COLORS['light']
        )
        
        custom_styles['MetricValue'] = ParagraphStyle(
            'MetricValue',
            fontSize=14,
            spaceAfter=4,
            textColor=self.COLORS['primary'],
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        custom_styles['MetricLabel'] = ParagraphStyle(
            'MetricLabel',
            fontSize=10,
            spaceAfter=8,
            textColor=self.COLORS['muted'],
            fontName='Helvetica',
            alignment=TA_CENTER
        )
        
        custom_styles['Footer'] = ParagraphStyle(
            'Footer',
            fontSize=9,
            textColor=self.COLORS['muted'],
            fontName='Helvetica',
            alignment=TA_CENTER
        )
        
        return custom_styles
    
    def generate_report(
        self,
        export_data: Dict[str, Any],
        template_type: str = 'executive',
        output_path: Optional[Path] = None,
        chart_images: Optional[Dict[str, Path]] = None
    ) -> Path:
        """
        Generate complete PDF report from export data
        
        Args:
            export_data: Complete analysis data for report generation
            template_type: Report template ('executive', 'detailed', 'investor')
            output_path: Output file path (temp file if None)
            chart_images: Dictionary of pre-rendered chart image paths
            
        Returns:
            Path to generated PDF file
        """
        logger.info(f"Generating {template_type} PDF report")
        
        # Set up output path
        if output_path is None:
            output_path = Path(tempfile.mktemp(suffix='.pdf'))
        
        # Create document
        doc = self._create_document(output_path)
        
        # Build content based on template type
        story = []
        
        if template_type == 'executive':
            story = self._build_executive_summary(export_data, chart_images)
        elif template_type == 'detailed':
            story = self._build_detailed_analysis(export_data, chart_images)
        elif template_type == 'investor':
            story = self._build_investor_presentation(export_data, chart_images)
        else:
            raise ValueError(f"Unknown template type: {template_type}")
        
        # Generate PDF
        doc.build(story)
        
        logger.info(f"PDF report generated: {output_path}")
        return output_path
    
    def _create_document(self, output_path: Path) -> SimpleDocTemplate:
        """Create ReportLab document with professional formatting"""
        
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=self.page_size,
            topMargin=self.margins['top'],
            bottomMargin=self.margins['bottom'],
            leftMargin=self.margins['left'],
            rightMargin=self.margins['right'],
            title=self.title,
            subject=self.subject,
            author=self.author,
            creator=self.creator
        )
        
        return doc
    
    def _build_executive_summary(
        self, 
        export_data: Dict[str, Any], 
        chart_images: Optional[Dict[str, Path]] = None
    ) -> List[Any]:
        """Build Executive Summary report content (2-3 pages)"""
        
        story = []
        analysis_results = export_data.get('analysis_results', {})
        
        # Title page
        story.append(Paragraph(self.title, self.styles['Title']))
        story.append(Paragraph("Executive Summary", self.styles['Heading1']))
        story.append(Spacer(1, 0.5 * inch))
        
        # Executive recommendation
        recommendation = analysis_results.get('recommendation', 'UNKNOWN')
        confidence = analysis_results.get('confidence', 'Medium')
        
        rec_text = f"<b>RECOMMENDATION: {recommendation}</b><br/>Confidence Level: {confidence}"
        story.append(Paragraph(rec_text, self.styles['Recommendation']))
        story.append(Spacer(1, 0.25 * inch))
        
        # Key metrics summary
        story.append(Paragraph("Key Financial Metrics", self.styles['Heading2']))
        
        metrics_data = [
            ['Metric', 'Ownership', 'Rental', 'Advantage'],
            [
                'Net Present Value',
                f"${analysis_results.get('ownership_npv', 0):,.0f}",
                f"${analysis_results.get('rental_npv', 0):,.0f}",
                'Ownership' if analysis_results.get('ownership_npv', 0) > analysis_results.get('rental_npv', 0) else 'Rental'
            ],
            [
                'Initial Investment',
                f"${analysis_results.get('ownership_initial_investment', 0):,.0f}",
                f"${analysis_results.get('rental_initial_investment', 0):,.0f}",
                'Rental' if analysis_results.get('rental_initial_investment', 0) < analysis_results.get('ownership_initial_investment', 0) else 'Ownership'
            ],
            [
                'NPV Difference',
                '-',
                '-',
                f"${abs(analysis_results.get('npv_difference', 0)):,.0f}"
            ]
        ]
        
        # Enhanced table styling with better proportions and formatting
        metrics_table = Table(metrics_data, colWidths=[2.2*inch, 1.6*inch, 1.6*inch, 1.6*inch], rowHeights=[20, 16, 16, 16, 16])
        metrics_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Data row styling
            ('BACKGROUND', (0, 1), (-1, -1), self.COLORS['light']),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.COLORS['dark']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align first column
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Center align data
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            
            # Borders and lines
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.COLORS['primary']),
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLORS['gray']),
            ('LINEAFTER', (0, 0), (-1, -1), 0.5, self.COLORS['gray']),
            
            # Highlight last column (Advantage)
            ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (3, 1), (3, -1), self.COLORS['primary'])
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 0.25 * inch))
        
        # NPV comparison chart - Improved integration
        if chart_images and 'npv_comparison' in chart_images:
            story.append(Paragraph("NPV Comparison Analysis", self.styles['Heading2']))
            # Better sized chart with professional positioning
            chart_img = Image(str(chart_images['npv_comparison']), width=6.5*inch, height=3.8*inch)
            # Center the chart using KeepTogether
            chart_container = KeepTogether([chart_img])
            story.append(chart_container)
            story.append(Spacer(1, 0.2 * inch))
        
        # Key assumptions
        story.append(PageBreak())
        story.append(Paragraph("Key Assumptions", self.styles['Heading2']))
        
        assumptions_text = f"""
        This analysis is based on the following key assumptions:
        
        <b>Financial Parameters:</b>
        • Cost of Capital: {export_data.get('inputs', {}).get('cost_of_capital', 8.0):.1f}%
        • Analysis Period: {export_data.get('inputs', {}).get('analysis_period', 25)} years
        • Property Tax Rate: {export_data.get('inputs', {}).get('property_tax_rate', 1.2):.1f}%
        
        <b>Market Assumptions:</b>
        • Rent Increase Rate: {export_data.get('inputs', {}).get('rent_increase_rate', 3.0):.1f}% annually
        • Property Appreciation: {export_data.get('inputs', {}).get('property_appreciation_rate', 3.5):.1f}% annually
        
        <b>Purchase Scenario:</b>
        • Purchase Price: ${export_data.get('inputs', {}).get('purchase_price', 0):,.0f}
        • Down Payment: {export_data.get('inputs', {}).get('down_payment_percent', 30.0):.0f}%
        • Interest Rate: {export_data.get('inputs', {}).get('interest_rate', 5.0):.1f}%
        
        <b>Rental Scenario:</b>
        • Current Annual Rent: ${export_data.get('inputs', {}).get('current_annual_rent', 0):,.0f}
        """
        
        story.append(Paragraph(assumptions_text, self.styles['BodyText']))
        story.append(Spacer(1, 0.25 * inch))
        
        # Risk considerations
        story.append(Paragraph("Risk Considerations", self.styles['Heading2']))
        
        risk_text = f"""
        <b>Key Risk Factors:</b>
        
        • <b>Market Risk:</b> Property values and rental rates may fluctuate due to economic conditions
        • <b>Interest Rate Risk:</b> Changes in interest rates affect borrowing costs and investment returns
        • <b>Liquidity Risk:</b> Real estate investments are less liquid than rental arrangements
        • <b>Maintenance Risk:</b> Ownership involves ongoing maintenance and repair costs
        • <b>Tax Risk:</b> Changes in tax regulations may impact the financial benefits of ownership
        
        <b>Confidence Level: {confidence}</b>
        
        The {confidence.lower()} confidence level reflects the reliability of key assumptions and market conditions.
        """
        
        story.append(Paragraph(risk_text, self.styles['BodyText']))
        
        # Footer
        story.append(Spacer(1, 0.5 * inch))
        footer_text = f"Generated by Real Estate Decision Tool | {datetime.now().strftime('%B %d, %Y')}"
        story.append(Paragraph(footer_text, self.styles['Footer']))
        
        return story
    
    def _build_detailed_analysis(
        self,
        export_data: Dict[str, Any],
        chart_images: Optional[Dict[str, Path]] = None
    ) -> List[Any]:
        """Build Detailed Analysis report content (8-12 pages)"""
        
        story = []
        
        # Start with executive summary content
        story.extend(self._build_executive_summary(export_data, chart_images))
        
        # Add detailed sections
        story.append(PageBreak())
        story.append(Paragraph("Detailed Financial Analysis", self.styles['Heading1']))
        
        # Cash flow analysis
        if chart_images and 'annual_cash_flows' in chart_images:
            story.append(Paragraph("Annual Cash Flow Analysis", self.styles['Heading2']))
            annual_chart = Image(str(chart_images['annual_cash_flows']), width=7*inch, height=4.5*inch)
            story.append(annual_chart)
            story.append(Spacer(1, 0.25 * inch))
        
        if chart_images and 'cumulative_cash_flows' in chart_images:
            story.append(Paragraph("Cumulative Cash Flow Analysis", self.styles['Heading2']))
            cumulative_chart = Image(str(chart_images['cumulative_cash_flows']), width=7*inch, height=4.5*inch)
            story.append(cumulative_chart)
            story.append(Spacer(1, 0.25 * inch))
        
        # Financial metrics
        story.append(PageBreak())
        if chart_images and 'financial_metrics' in chart_images:
            story.append(Paragraph("Financial Metrics Comparison", self.styles['Heading2']))
            metrics_chart = Image(str(chart_images['financial_metrics']), width=7*inch, height=4*inch)
            story.append(metrics_chart)
            story.append(Spacer(1, 0.25 * inch))
        
        # Sensitivity analysis
        if chart_images and 'sensitivity_analysis' in chart_images:
            story.append(Paragraph("Sensitivity Analysis", self.styles['Heading2']))
            sensitivity_chart = Image(str(chart_images['sensitivity_analysis']), width=7*inch, height=4*inch)
            story.append(sensitivity_chart)
            story.append(Spacer(1, 0.25 * inch))
        
        # Detailed cash flow tables
        story.append(PageBreak())
        story.append(Paragraph("Cash Flow Projections", self.styles['Heading2']))
        
        # Add cash flow tables if available
        ownership_flows = export_data.get('ownership_flows', {})
        if ownership_flows:
            story.append(self._create_cash_flow_table(ownership_flows, "Ownership Scenario"))
        
        rental_flows = export_data.get('rental_flows', {})
        if rental_flows:
            story.append(self._create_cash_flow_table(rental_flows, "Rental Scenario"))
        
        return story
    
    def _build_investor_presentation(
        self,
        export_data: Dict[str, Any],
        chart_images: Optional[Dict[str, Path]] = None
    ) -> List[Any]:
        """Build Investor Presentation report content (6-8 pages)"""
        
        story = []
        analysis_results = export_data.get('analysis_results', {})
        
        # Title page
        story.append(Paragraph("Investment Analysis Presentation", self.styles['Title']))
        story.append(Paragraph("Real Estate Investment Decision", self.styles['Heading1']))
        story.append(Spacer(1, 0.5 * inch))
        
        # Investment thesis
        story.append(Paragraph("Investment Thesis", self.styles['Heading2']))
        
        thesis_text = f"""
        <b>Investment Opportunity:</b> {analysis_results.get('recommendation', 'UNKNOWN')}
        
        Based on comprehensive financial analysis, the recommended approach provides:
        • Superior Net Present Value of ${analysis_results.get('npv_difference', 0):,.0f}
        • Optimized risk-return profile for the investment horizon
        • Strategic alignment with current market conditions
        """
        
        story.append(Paragraph(thesis_text, self.styles['BodyText']))
        story.append(Spacer(1, 0.25 * inch))
        
        # Key metrics for investors
        story.append(Paragraph("Investment Metrics", self.styles['Heading2']))
        
        if chart_images and 'npv_comparison' in chart_images:
            npv_chart = Image(str(chart_images['npv_comparison']), width=6*inch, height=4*inch)
            story.append(npv_chart)
        
        # Financial projections
        story.append(PageBreak())
        story.append(Paragraph("Financial Projections", self.styles['Heading2']))
        
        if chart_images and 'annual_cash_flows' in chart_images:
            cash_flow_chart = Image(str(chart_images['annual_cash_flows']), width=7*inch, height=4.5*inch)
            story.append(cash_flow_chart)
        
        # Risk assessment
        story.append(PageBreak())
        story.append(Paragraph("Risk Assessment", self.styles['Heading2']))
        
        if chart_images and 'sensitivity_analysis' in chart_images:
            sensitivity_chart = Image(str(chart_images['sensitivity_analysis']), width=7*inch, height=4*inch)
            story.append(sensitivity_chart)
        
        risk_assessment_text = f"""
        <b>Risk Profile: {analysis_results.get('confidence', 'Medium')} Risk</b>
        
        The investment presents a {analysis_results.get('confidence', 'medium').lower()}-risk profile with the following considerations:
        
        <b>Upside Potential:</b>
        • Property appreciation in favorable market conditions
        • Tax benefits and equity building through ownership
        • Potential for rental income optimization
        
        <b>Downside Risks:</b>
        • Market volatility affecting property values
        • Interest rate fluctuations impacting financing costs
        • Maintenance and operational responsibilities
        
        <b>Mitigation Strategies:</b>
        • Diversified investment approach
        • Conservative assumption modeling
        • Regular performance monitoring and adjustment
        """
        
        story.append(Paragraph(risk_assessment_text, self.styles['BodyText']))
        
        return story
    
    def _create_cash_flow_table(self, flows_data: Dict[str, Any], title: str) -> Table:
        """Create formatted cash flow table"""
        
        annual_flows = flows_data.get('annual_cash_flows', [])
        if not annual_flows:
            return Paragraph(f"No cash flow data available for {title}", self.styles['Normal'])
        
        # Create table data (show first 10 years for space)
        table_data = [['Year', 'Annual Cash Flow', 'Cumulative']]
        cumulative = 0
        
        for i, flow in enumerate(annual_flows[:10]):  # First 10 years
            cumulative += flow
            table_data.append([
                str(i + 1),
                f"${flow:,.0f}",
                f"${cumulative:,.0f}"
            ])
        
        if len(annual_flows) > 10:
            table_data.append(['...', '...', '...'])
            # Add final year
            final_cumulative = sum(annual_flows)
            table_data.append([
                str(len(annual_flows)),
                f"${annual_flows[-1]:,.0f}",
                f"${final_cumulative:,.0f}"
            ])
        
        table = Table(table_data, colWidths=[1*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['white']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), self.COLORS['light']),
            ('GRID', (0, 0), (-1, -1), 1, self.COLORS['gray']),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        return table
    
    def get_supported_templates(self) -> List[str]:
        """Get list of supported template types"""
        return ['executive', 'detailed', 'investor']
    
    def validate_export_data(self, export_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate export data for PDF generation
        
        Args:
            export_data: Export data to validate
            
        Returns:
            Dictionary of validation results
        """
        validation = {
            'has_analysis_results': bool(export_data.get('analysis_results')),
            'has_ownership_flows': bool(export_data.get('ownership_flows')),
            'has_rental_flows': bool(export_data.get('rental_flows')),
            'has_inputs': bool(export_data.get('inputs')),
            'has_recommendation': bool(export_data.get('analysis_results', {}).get('recommendation')),
            'reportlab_available': REPORTLAB_AVAILABLE,
            'pil_available': PIL_AVAILABLE
        }
        
        validation['is_valid'] = all([
            validation['has_analysis_results'],
            validation['has_recommendation'],
            validation['reportlab_available']
        ])
        
        return validation