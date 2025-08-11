"""
Executive PDF Templates
Professional report templates for Real Estate Decision Tool

This module provides:
- Executive Summary template (2-3 pages): Key metrics, recommendation, NPV comparison
- Detailed Analysis template (8-12 pages): Complete analysis with all charts and tables
- Investor Presentation template (6-8 pages): Investment focus with risk analysis
- Template customization and branding options

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch, mm
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (
        Paragraph, Spacer, Table, TableStyle, PageBreak, 
        Image, KeepTogether, HRFlowable
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available - templates will be limited")

from .layout_engine import LayoutEngine, ContentType

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Available template types"""
    EXECUTIVE = "executive"
    DETAILED = "detailed" 
    INVESTOR = "investor"


@dataclass
class TemplateConfig:
    """Configuration for template customization"""
    template_type: TemplateType
    page_size: str = 'letter'
    margin_preset: str = 'executive'
    color_scheme: str = 'corporate'
    include_toc: bool = False
    include_appendix: bool = False
    branding: Dict[str, Any] = None


class ExecutiveTemplateBuilder:
    """
    Professional template builder for executive reports
    
    Creates polished, executive-ready reports with consistent branding,
    professional layouts, and strategic presentation of analysis results.
    """
    
    # Corporate color schemes - initialized in __init__
    COLOR_SCHEMES = None
    
    @staticmethod
    def _get_color_schemes():
        """Get color schemes - only available when ReportLab is imported"""
        if not REPORTLAB_AVAILABLE:
            return {}
        
        return {
            'corporate': {
                'primary': HexColor('#FF6B6B'),
                'secondary': HexColor('#74B9FF'),
                'success': HexColor('#96CEB4'),
                'warning': HexColor('#FECA57'),
                'danger': HexColor('#FF7675'),
                'dark': HexColor('#2D3436'),
                'light': HexColor('#F8F9FA'),
                'muted': HexColor('#6C757D')
            },
            'professional': {
                'primary': HexColor('#1E3A8A'),
                'secondary': HexColor('#1F2937'),
                'success': HexColor('#059669'),
                'warning': HexColor('#D97706'),
                'danger': HexColor('#DC2626'),
                'dark': HexColor('#111827'),
                'light': HexColor('#F9FAFB'),
                'muted': HexColor('#6B7280')
            },
            'investor': {
                'primary': HexColor('#7C3AED'),
                'secondary': HexColor('#059669'),
                'success': HexColor('#10B981'),
                'warning': HexColor('#F59E0B'),
                'danger': HexColor('#EF4444'),
                'dark': HexColor('#1F2937'),
                'light': HexColor('#FAFAFA'),
                'muted': HexColor('#64748B')
            }
        }
    
    def __init__(self, config: TemplateConfig):
        """
        Initialize template builder
        
        Args:
            config: Template configuration
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for template building")
        
        self.config = config
        self.layout = LayoutEngine(config.page_size, config.margin_preset)
        color_schemes = self._get_color_schemes()
        self.colors = color_schemes.get(config.color_scheme, color_schemes.get('corporate', {}))
        
        # Initialize custom styles
        self.styles = self._create_template_styles()
        
        logger.info(f"Template builder initialized: {config.template_type.value}")
    
    def _create_template_styles(self) -> Dict[str, ParagraphStyle]:
        """Create template-specific styles"""
        
        styles = {}
        
        # Executive styles
        styles['ExecutiveTitle'] = ParagraphStyle(
            'ExecutiveTitle',
            fontSize=28,
            spaceAfter=24,
            textColor=self.colors['primary'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        styles['ExecutiveSubtitle'] = ParagraphStyle(
            'ExecutiveSubtitle',
            fontSize=16,
            spaceAfter=20,
            textColor=self.colors['dark'],
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        styles['RecommendationBox'] = ParagraphStyle(
            'RecommendationBox',
            fontSize=18,
            spaceAfter=16,
            spaceBefore=16,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            borderWidth=2,
            borderColor=self.colors['primary'],
            borderPadding=16,
            backColor=self.colors['light']
        )
        
        styles['KeyMetric'] = ParagraphStyle(
            'KeyMetric',
            fontSize=24,
            spaceAfter=4,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        styles['MetricLabel'] = ParagraphStyle(
            'MetricLabel',
            fontSize=11,
            spaceAfter=12,
            textColor=self.colors['muted'],
            fontName='Helvetica',
            alignment=TA_CENTER
        )
        
        styles['SectionHeader'] = ParagraphStyle(
            'SectionHeader',
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=self.colors['dark'],
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=self.colors['primary'],
            borderPadding=8,
            leftIndent=0,
            backColor=self.colors['light']
        )
        
        styles['ExecutiveBody'] = ParagraphStyle(
            'ExecutiveBody',
            fontSize=12,
            spaceAfter=8,
            textColor=self.colors['dark'],
            fontName='Helvetica',
            alignment=TA_JUSTIFY,
            leftIndent=12,
            rightIndent=12
        )
        
        styles['Highlight'] = ParagraphStyle(
            'Highlight',
            fontSize=12,
            spaceAfter=8,
            textColor=self.colors['primary'],
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            leftIndent=20
        )
        
        styles['RiskBox'] = ParagraphStyle(
            'RiskBox',
            fontSize=11,
            spaceAfter=8,
            textColor=self.colors['dark'],
            fontName='Helvetica',
            alignment=TA_JUSTIFY,
            borderWidth=1,
            borderColor=self.colors['warning'],
            borderPadding=12,
            backColor=HexColor('#FFFBF0')
        )
        
        return styles
    
    def build_executive_summary(
        self,
        export_data: Dict[str, Any],
        chart_images: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Build Executive Summary template content
        
        Args:
            export_data: Complete export data
            chart_images: Pre-rendered chart images
            
        Returns:
            List of ReportLab flowables
        """
        story = []
        analysis_results = export_data.get('analysis_results', {})
        inputs = export_data.get('inputs', {})
        
        # Title page
        story.append(Paragraph("REAL ESTATE INVESTMENT ANALYSIS", self.styles['ExecutiveTitle']))
        story.append(Paragraph("Executive Summary & Recommendation", self.styles['ExecutiveSubtitle']))
        story.append(Spacer(1, 0.5 * inch))
        
        # Executive recommendation
        recommendation = analysis_results.get('recommendation', 'UNKNOWN')
        confidence = analysis_results.get('confidence', 'Medium')
        
        rec_text = f"<b>STRATEGIC RECOMMENDATION: {recommendation}</b><br/>Analysis Confidence: {confidence}"
        story.append(Paragraph(rec_text, self.styles['RecommendationBox']))
        
        # Key metrics dashboard
        story.append(Paragraph("Investment Analysis Summary", self.styles['SectionHeader']))
        
        # Create metrics table
        metrics_data = self._create_executive_metrics_table(analysis_results)
        story.append(metrics_data)
        story.append(Spacer(1, 0.25 * inch))
        
        # NPV comparison visualization
        if chart_images and 'npv_comparison' in chart_images:
            story.append(Paragraph("Net Present Value Analysis", self.styles['SectionHeader']))
            chart_width, chart_height = self.layout.optimize_chart_size(ContentType.CHART, 12, 1.6)
            chart_img = Image(str(chart_images['npv_comparison']), width=chart_width, height=chart_height)
            story.append(chart_img)
            story.append(Spacer(1, 0.2 * inch))
        
        # Strategic insights
        story.append(PageBreak())
        story.append(Paragraph("Strategic Investment Insights", self.styles['SectionHeader']))
        
        insights_text = self._generate_strategic_insights(analysis_results, inputs)
        story.append(Paragraph(insights_text, self.styles['ExecutiveBody']))
        
        # Risk assessment
        story.append(Paragraph("Risk Assessment", self.styles['SectionHeader']))
        
        risk_text = self._generate_risk_assessment(analysis_results, confidence)
        story.append(Paragraph(risk_text, self.styles['RiskBox']))
        
        # Investment timeline
        story.append(Paragraph("Key Assumptions & Parameters", self.styles['SectionHeader']))
        
        assumptions_text = self._generate_assumptions_summary(inputs)
        story.append(Paragraph(assumptions_text, self.styles['ExecutiveBody']))
        
        # Add footer
        story.extend(self._create_report_footer())
        
        return story
    
    def build_detailed_analysis(
        self,
        export_data: Dict[str, Any],
        chart_images: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Build Detailed Analysis template content
        
        Args:
            export_data: Complete export data
            chart_images: Pre-rendered chart images
            
        Returns:
            List of ReportLab flowables
        """
        story = []
        
        # Start with executive summary
        story.extend(self.build_executive_summary(export_data, chart_images))
        
        # Add detailed sections
        story.append(PageBreak())
        story.append(Paragraph("DETAILED FINANCIAL ANALYSIS", self.styles['ExecutiveTitle']))
        
        # Methodology section
        story.append(Paragraph("Analysis Methodology", self.styles['SectionHeader']))
        methodology_text = self._generate_methodology_section(export_data.get('inputs', {}))
        story.append(Paragraph(methodology_text, self.styles['ExecutiveBody']))
        
        # Cash flow analysis
        if chart_images:
            story.append(PageBreak())
            story.append(Paragraph("Cash Flow Analysis", self.styles['SectionHeader']))
            
            if 'annual_cash_flows' in chart_images:
                story.append(Paragraph("Annual Cash Flow Projections", self.styles['Highlight']))
                chart_width, chart_height = self.layout.optimize_chart_size(ContentType.CHART, 12, 1.8)
                annual_chart = Image(str(chart_images['annual_cash_flows']), width=chart_width, height=chart_height)
                story.append(annual_chart)
                story.append(Spacer(1, 0.2 * inch))
            
            if 'cumulative_cash_flows' in chart_images:
                story.append(Paragraph("Cumulative Cash Flow Analysis", self.styles['Highlight']))
                cumulative_chart = Image(str(chart_images['cumulative_cash_flows']), width=chart_width, height=chart_height)
                story.append(cumulative_chart)
                story.append(Spacer(1, 0.2 * inch))
        
        # Financial metrics deep dive
        if chart_images and 'financial_metrics' in chart_images:
            story.append(PageBreak())
            story.append(Paragraph("Comprehensive Financial Metrics", self.styles['SectionHeader']))
            metrics_chart = Image(str(chart_images['financial_metrics']), width=chart_width, height=chart_height-1*inch)
            story.append(metrics_chart)
        
        # Sensitivity analysis
        if chart_images and 'sensitivity_analysis' in chart_images:
            story.append(PageBreak())
            story.append(Paragraph("Sensitivity Analysis", self.styles['SectionHeader']))
            
            sensitivity_text = """
            The sensitivity analysis examines how changes in key assumptions impact the Net Present Value
            of each scenario. This analysis helps identify the most critical factors in the investment decision
            and provides insight into the robustness of the recommendation under different market conditions.
            """
            story.append(Paragraph(sensitivity_text, self.styles['ExecutiveBody']))
            
            sensitivity_chart = Image(str(chart_images['sensitivity_analysis']), width=chart_width, height=chart_height-1*inch)
            story.append(sensitivity_chart)
        
        # Cash flow tables
        story.append(PageBreak())
        story.append(Paragraph("Detailed Cash Flow Projections", self.styles['SectionHeader']))
        
        # Add ownership cash flow table
        ownership_flows = export_data.get('ownership_flows', {})
        if ownership_flows:
            story.append(Paragraph("Ownership Scenario - Annual Cash Flows", self.styles['Highlight']))
            ownership_table = self._create_detailed_cash_flow_table(ownership_flows, "ownership")
            story.append(ownership_table)
            story.append(Spacer(1, 0.25 * inch))
        
        # Add rental cash flow table
        rental_flows = export_data.get('rental_flows', {})
        if rental_flows:
            story.append(Paragraph("Rental Scenario - Annual Cash Flows", self.styles['Highlight']))
            rental_table = self._create_detailed_cash_flow_table(rental_flows, "rental")
            story.append(rental_table)
        
        # Add appendix with assumptions
        story.append(PageBreak())
        story.append(Paragraph("Appendix: Complete Assumptions", self.styles['SectionHeader']))
        
        detailed_assumptions = self._generate_detailed_assumptions(export_data.get('inputs', {}))
        story.append(Paragraph(detailed_assumptions, self.styles['ExecutiveBody']))
        
        return story
    
    def build_investor_presentation(
        self,
        export_data: Dict[str, Any],
        chart_images: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Build Investor Presentation template content
        
        Args:
            export_data: Complete export data
            chart_images: Pre-rendered chart images
            
        Returns:
            List of ReportLab flowables
        """
        story = []
        analysis_results = export_data.get('analysis_results', {})
        inputs = export_data.get('inputs', {})
        
        # Investment opportunity title
        story.append(Paragraph("REAL ESTATE INVESTMENT OPPORTUNITY", self.styles['ExecutiveTitle']))
        story.append(Paragraph("Investment Analysis & Strategic Recommendation", self.styles['ExecutiveSubtitle']))
        story.append(Spacer(1, 0.5 * inch))
        
        # Investment thesis
        story.append(Paragraph("Investment Thesis", self.styles['SectionHeader']))
        
        thesis_text = self._generate_investment_thesis(analysis_results, inputs)
        story.append(Paragraph(thesis_text, self.styles['ExecutiveBody']))
        
        # Key investment metrics
        story.append(Paragraph("Investment Metrics", self.styles['SectionHeader']))
        
        investment_metrics = self._create_investor_metrics_table(analysis_results)
        story.append(investment_metrics)
        story.append(Spacer(1, 0.25 * inch))
        
        # Financial projections
        story.append(PageBreak())
        story.append(Paragraph("Financial Projections", self.styles['SectionHeader']))
        
        if chart_images and 'npv_comparison' in chart_images:
            chart_width, chart_height = self.layout.optimize_chart_size(ContentType.CHART, 12, 1.5)
            npv_chart = Image(str(chart_images['npv_comparison']), width=chart_width, height=chart_height)
            story.append(npv_chart)
            story.append(Spacer(1, 0.2 * inch))
        
        if chart_images and 'annual_cash_flows' in chart_images:
            story.append(Paragraph("Projected Cash Flow Performance", self.styles['Highlight']))
            cash_flow_chart = Image(str(chart_images['annual_cash_flows']), width=chart_width, height=chart_height)
            story.append(cash_flow_chart)
        
        # Market opportunity
        story.append(PageBreak())
        story.append(Paragraph("Market Opportunity & Positioning", self.styles['SectionHeader']))
        
        market_text = self._generate_market_opportunity_text(inputs)
        story.append(Paragraph(market_text, self.styles['ExecutiveBody']))
        
        # Risk analysis for investors
        story.append(Paragraph("Investment Risk Profile", self.styles['SectionHeader']))
        
        if chart_images and 'sensitivity_analysis' in chart_images:
            sensitivity_chart = Image(str(chart_images['sensitivity_analysis']), width=chart_width, height=chart_height-0.5*inch)
            story.append(sensitivity_chart)
            story.append(Spacer(1, 0.2 * inch))
        
        investor_risk_text = self._generate_investor_risk_analysis(analysis_results)
        story.append(Paragraph(investor_risk_text, self.styles['RiskBox']))
        
        # Investment timeline and milestones
        story.append(PageBreak())
        story.append(Paragraph("Investment Timeline & Key Milestones", self.styles['SectionHeader']))
        
        timeline_text = self._generate_investment_timeline(inputs)
        story.append(Paragraph(timeline_text, self.styles['ExecutiveBody']))
        
        # Return expectations
        story.append(Paragraph("Return Expectations & Exit Strategy", self.styles['SectionHeader']))
        
        returns_text = self._generate_return_expectations(analysis_results, inputs)
        story.append(Paragraph(returns_text, self.styles['ExecutiveBody']))
        
        return story
    
    def _create_executive_metrics_table(self, analysis_results: Dict[str, Any]) -> Table:
        """Create executive-level metrics table"""
        
        data = [
            ['Financial Metric', 'Ownership Scenario', 'Rental Scenario', 'Advantage'],
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
                'Lower' if analysis_results.get('rental_initial_investment', 0) < analysis_results.get('ownership_initial_investment', 0) else 'Higher'
            ],
            [
                'NPV Advantage',
                '-',
                '-',
                f"${abs(analysis_results.get('npv_difference', 0)):,.0f}"
            ]
        ]
        
        col_widths = self.layout.calculate_table_column_widths(4, column_ratios=[2.5, 2, 2, 1.5])
        table = Table(data, colWidths=col_widths)
        
        # Map our colors to layout engine expected format
        table_colors = {
            'header_bg': self.colors['primary'],
            'header_text': self.colors.get('white', self.colors['light']),
            'row_bg': self.colors['light'],
            'text': self.colors['dark'],
            'border': self.colors['muted']
        }
        table.setStyle(self.layout.create_table_style('executive', table_colors))
        
        return table
    
    def _create_investor_metrics_table(self, analysis_results: Dict[str, Any]) -> Table:
        """Create investor-focused metrics table"""
        
        data = [
            ['Investment Metric', 'Value', 'Significance'],
            [
                'Recommended Strategy',
                analysis_results.get('recommendation', 'UNKNOWN'),
                'Primary Investment Direction'
            ],
            [
                'NPV Advantage',
                f"${abs(analysis_results.get('npv_difference', 0)):,.0f}",
                'Financial Benefit Over Alternative'
            ],
            [
                'Confidence Level',
                analysis_results.get('confidence', 'Medium'),
                'Risk Assessment'
            ],
            [
                'IRR Differential',
                f"{(analysis_results.get('ownership_irr', 0) - analysis_results.get('rental_irr', 0)) * 100:.1f}%",
                'Return Rate Advantage'
            ]
        ]
        
        col_widths = self.layout.calculate_table_column_widths(3, column_ratios=[2, 1.5, 2.5])
        table = Table(data, colWidths=col_widths)
        
        # Map colors for table style
        table_colors = {
            'header_bg': self.colors['primary'],
            'header_text': self.colors.get('white', self.colors['light']),
            'row_bg': self.colors['light'],
            'text': self.colors['dark'],
            'border': self.colors['muted']
        }
        table.setStyle(self.layout.create_table_style('professional', table_colors))
        
        return table
    
    def _create_detailed_cash_flow_table(self, flows_data: Dict[str, Any], scenario: str) -> Table:
        """Create detailed cash flow projection table"""
        
        annual_flows = flows_data.get('annual_cash_flows', [])
        if not annual_flows:
            return Paragraph(f"No cash flow data available for {scenario} scenario", self.styles['ExecutiveBody'])
        
        # Show first 10 years and summary
        data = [['Year', 'Annual Cash Flow', 'Cumulative Cash Flow']]
        cumulative = 0
        
        for i, flow in enumerate(annual_flows[:10]):
            cumulative += flow
            data.append([
                str(i + 1),
                f"${flow:,.0f}",
                f"${cumulative:,.0f}"
            ])
        
        if len(annual_flows) > 10:
            data.append(['...', '...', '...'])
            final_cumulative = sum(annual_flows)
            data.append([
                f"Year {len(annual_flows)}",
                f"${annual_flows[-1]:,.0f}",
                f"${final_cumulative:,.0f}"
            ])
        
        col_widths = self.layout.calculate_table_column_widths(3)
        table = Table(data, colWidths=col_widths)
        
        # Map colors for table style
        table_colors = {
            'header_bg': self.colors['primary'],
            'header_text': self.colors.get('white', self.colors['light']),
            'row_bg': self.colors['light'],
            'text': self.colors['dark'],
            'border': self.colors['muted']
        }
        table.setStyle(self.layout.create_table_style('professional', table_colors))
        
        return table
    
    def _generate_strategic_insights(self, analysis_results: Dict[str, Any], inputs: Dict[str, Any]) -> str:
        """Generate strategic insights text"""
        
        recommendation = analysis_results.get('recommendation', 'UNKNOWN')
        npv_diff = analysis_results.get('npv_difference', 0)
        
        insights = f"""
        <b>Primary Strategic Finding:</b> The analysis strongly supports {recommendation.lower()} as the optimal
        financial strategy for this real estate decision, providing a net advantage of ${abs(npv_diff):,.0f}
        in present value terms.
        
        <b>Key Value Drivers:</b>
        • Market positioning in current interest rate environment
        • Tax optimization through {recommendation.lower()} scenario
        • Cash flow timing and liquidity considerations
        • Long-term wealth building strategy alignment
        
        <b>Decision Confidence:</b> This recommendation is based on comprehensive financial modeling
        incorporating market assumptions, tax implications, and opportunity costs over the full analysis period.
        """
        
        return insights
    
    def _generate_risk_assessment(self, analysis_results: Dict[str, Any], confidence: str) -> str:
        """Generate risk assessment text"""
        
        risk_text = f"""
        <b>Risk Profile: {confidence} Risk Investment</b>
        
        <b>Primary Risk Factors:</b>
        • Interest rate volatility impacting financing costs and opportunity returns
        • Real estate market cycles affecting property values and rental rates
        • Tax policy changes potentially altering investment benefits
        • Economic conditions influencing employment and housing demand
        
        <b>Risk Mitigation:</b>
        • Conservative assumptions used in base case analysis
        • Sensitivity analysis identifying key variable impacts
        • Diversification considerations for overall portfolio
        
        <b>Monitoring Requirements:</b>
        Regular review recommended as market conditions evolve and personal circumstances change.
        """
        
        return risk_text
    
    def _generate_assumptions_summary(self, inputs: Dict[str, Any]) -> str:
        """Generate assumptions summary"""
        
        return f"""
        <b>Core Financial Assumptions:</b><br/>
        • Analysis Period: {inputs.get('analysis_period', 25)} years<br/>
        • Cost of Capital: {inputs.get('cost_of_capital', 8.0):.1f}% annually<br/>
        • Property Tax Rate: {inputs.get('property_tax_rate', 1.2):.1f}%<br/>
        • Rent Growth Rate: {inputs.get('rent_increase_rate', 3.0):.1f}% annually<br/>
        • Property Appreciation: {inputs.get('property_appreciation_rate', 3.5):.1f}% annually<br/>
        
        <b>Purchase Scenario:</b><br/>
        • Property Value: ${inputs.get('purchase_price', 0):,.0f}<br/>
        • Down Payment: {inputs.get('down_payment_percent', 30.0):.0f}%<br/>
        • Mortgage Rate: {inputs.get('interest_rate', 5.0):.1f}%<br/>
        
        <b>Rental Scenario:</b><br/>
        • Annual Rent: ${inputs.get('current_annual_rent', 0):,.0f}<br/>
        • Security Deposit: ${inputs.get('security_deposit', 0):,.0f}<br/>
        """
    
    def _generate_methodology_section(self, inputs: Dict[str, Any]) -> str:
        """Generate methodology section"""
        
        return """
        <b>Analysis Framework:</b><br/>
        This analysis employs Net Present Value (NPV) methodology to compare the total cost of ownership 
        versus rental over the specified time horizon. All cash flows are discounted to present value using 
        the specified cost of capital.
        
        <b>Ownership Scenario Modeling:</b><br/>
        • Initial investment including down payment, closing costs, and transaction fees<br/>
        • Monthly mortgage payments (principal and interest)<br/>
        • Property taxes with annual escalation<br/>
        • Insurance, maintenance, and property management costs<br/>
        • Tax benefits from mortgage interest and property tax deductions<br/>
        • Terminal value from property sale at end of period<br/>
        
        <b>Rental Scenario Modeling:</b><br/>
        • Initial costs including security deposits and moving expenses<br/>
        • Monthly rent payments with annual increases<br/>
        • Investment of down payment savings in alternative investments<br/>
        • Tax implications of investment returns<br/>
        
        <b>Sensitivity Considerations:</b><br/>
        Key assumptions are tested for impact on final recommendation to ensure robustness 
        of the analysis under varying market conditions.
        """
    
    def _generate_detailed_assumptions(self, inputs: Dict[str, Any]) -> str:
        """Generate detailed assumptions appendix"""
        
        return f"""
        <b>Complete Model Assumptions:</b>
        
        <b>Financial Parameters:</b>
        • Cost of Capital: {inputs.get('cost_of_capital', 8.0):.1f}%
        • Analysis Period: {inputs.get('analysis_period', 25)} years
        • Tax Rate (Federal + State): {inputs.get('tax_rate', 32.0):.1f}%
        • Inflation Rate: {inputs.get('inflation_rate', 2.5):.1f}%
        
        <b>Property-Specific Inputs:</b>
        • Purchase Price: ${inputs.get('purchase_price', 0):,.0f}
        • Down Payment: {inputs.get('down_payment_percent', 30.0):.1f}%
        • Mortgage Interest Rate: {inputs.get('interest_rate', 5.0):.1f}%
        • Loan Term: {inputs.get('loan_term', 20)} years
        • Property Tax Rate: {inputs.get('property_tax_rate', 1.2):.1f}%
        • Property Tax Escalation: {inputs.get('property_tax_escalation_rate', 2.0):.1f}%
        • Annual Insurance: ${inputs.get('insurance_cost', 5000):,.0f}
        • Maintenance Rate: {inputs.get('annual_maintenance_percent', 2.0):.1f}% of property value
        • Property Appreciation: {inputs.get('property_appreciation_rate', 3.5):.1f}%
        
        <b>Rental Parameters:</b>
        • Current Annual Rent: ${inputs.get('current_annual_rent', 0):,.0f}
        • Rent Increase Rate: {inputs.get('rent_increase_rate', 3.0):.1f}%
        • Security Deposit: ${inputs.get('security_deposit', 0):,.0f}
        • Moving Costs: ${inputs.get('moving_costs', 3000):,.0f}
        
        <b>Transaction Costs:</b>
        • Purchase Transaction: {inputs.get('transaction_costs_percent', 5.0):.1f}%
        • Sale Transaction: {inputs.get('sale_transaction_costs_percent', 6.0):.1f}%
        
        All assumptions are based on current market conditions and industry standards,
        with conservative estimates used where uncertainty exists.
        """
    
    def _generate_investment_thesis(self, analysis_results: Dict[str, Any], inputs: Dict[str, Any]) -> str:
        """Generate investment thesis for investor presentation"""
        
        recommendation = analysis_results.get('recommendation', 'UNKNOWN')
        npv_advantage = abs(analysis_results.get('npv_difference', 0))
        
        return f"""
        <b>Investment Opportunity:</b> {recommendation} STRATEGY
        
        Our comprehensive financial analysis indicates that pursuing the {recommendation.lower()} strategy
        provides superior risk-adjusted returns with a net present value advantage of ${npv_advantage:,.0f}
        over the alternative approach.
        
        <b>Strategic Rationale:</b>
        • Market timing alignment with current interest rate environment
        • Optimal capital allocation given investment timeline and objectives
        • Risk-return profile optimization for the specified holding period
        • Tax efficiency maximization through strategic structuring
        
        <b>Competitive Advantage:</b>
        This analysis incorporates detailed market research, conservative assumptions, and comprehensive
        sensitivity testing to ensure robust decision-making under various economic scenarios.
        """
    
    def _generate_market_opportunity_text(self, inputs: Dict[str, Any]) -> str:
        """Generate market opportunity section"""
        
        return f"""
        <b>Market Context:</b>
        The current real estate market presents unique opportunities given interest rate positioning
        and housing market dynamics. Our analysis incorporates:
        
        • Property appreciation assumptions of {inputs.get('property_appreciation_rate', 3.5):.1f}% annually
        • Rental market growth projections of {inputs.get('rent_increase_rate', 3.0):.1f}% annually
        • Interest rate environment with mortgage rates at {inputs.get('interest_rate', 5.0):.1f}%
        
        <b>Strategic Positioning:</b>
        The recommended strategy positions the investment to capitalize on long-term demographic trends
        while maintaining flexibility to adapt to changing market conditions.
        
        <b>Market Risk Mitigation:</b>
        Conservative assumptions and sensitivity analysis ensure the recommendation remains valid
        across reasonable market scenarios.
        """
    
    def _generate_investor_risk_analysis(self, analysis_results: Dict[str, Any]) -> str:
        """Generate investor-focused risk analysis"""
        
        confidence = analysis_results.get('confidence', 'Medium')
        
        return f"""
        <b>Investment Risk Assessment: {confidence} Risk Profile</b>
        
        <b>Risk Factors & Mitigation:</b>
        • Market Risk: Diversification across asset classes recommended
        • Interest Rate Risk: Fixed-rate financing provides protection against rising rates
        • Liquidity Risk: Investment timeline aligns with typical market cycles
        • Operational Risk: Professional management options available to minimize hands-on requirements
        
        <b>Sensitivity Analysis Results:</b>
        The recommendation remains robust under reasonable variations in key assumptions,
        providing confidence in the strategic direction.
        
        <b>Exit Strategy:</b>
        Multiple exit options available including sale, refinancing, or conversion to rental property,
        providing flexibility as market conditions evolve.
        """
    
    def _generate_investment_timeline(self, inputs: Dict[str, Any]) -> str:
        """Generate investment timeline"""
        
        analysis_period = inputs.get('analysis_period', 25)
        
        return f"""
        <b>Investment Timeline: {analysis_period}-Year Analysis Period</b>
        
        <b>Phase 1 (Years 1-3): Acquisition & Establishment</b>
        • Property acquisition and financing completion
        • Initial occupancy and cash flow stabilization
        • Tax benefit optimization and strategy refinement
        
        <b>Phase 2 (Years 4-15): Growth & Optimization</b>
        • Equity building through principal paydown
        • Property appreciation realization
        • Potential refinancing evaluation for rate optimization
        
        <b>Phase 3 (Years 16-{analysis_period}): Maturation & Exit Planning</b>
        • Exit strategy evaluation and execution
        • Terminal value realization through sale or portfolio transition
        • Tax planning for disposition
        
        <b>Key Milestones:</b>
        Regular performance reviews recommended annually with strategic assessments
        every 3-5 years to ensure continued alignment with investment objectives.
        """
    
    def _generate_return_expectations(self, analysis_results: Dict[str, Any], inputs: Dict[str, Any]) -> str:
        """Generate return expectations section"""
        
        ownership_irr = analysis_results.get('ownership_irr', 0) * 100
        rental_irr = analysis_results.get('rental_irr', 0) * 100
        
        return f"""
        <b>Return Expectations:</b>
        
        <b>Projected Returns:</b>
        • Ownership Scenario IRR: {ownership_irr:.1f}%
        • Rental + Investment IRR: {rental_irr:.1f}%
        • NPV Advantage: ${abs(analysis_results.get('npv_difference', 0)):,.0f}
        
        <b>Return Components:</b>
        • Capital appreciation through property value growth
        • Tax benefits from mortgage interest and property tax deductions
        • Equity building through mortgage principal reduction
        • Opportunity cost optimization through strategic capital allocation
        
        <b>Performance Monitoring:</b>
        Annual review of actual vs. projected performance with adjustments
        for changing market conditions and personal circumstances.
        
        <b>Exit Strategy Options:</b>
        • Traditional sale at market value
        • 1031 exchange for portfolio optimization
        • Conversion to rental income property
        • Refinancing for liquidity while maintaining ownership
        """
    
    def _create_report_footer(self) -> List[Any]:
        """Create standardized report footer"""
        
        footer_elements = []
        
        footer_elements.append(Spacer(1, 0.5 * inch))
        footer_elements.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=self.colors['muted']))
        footer_elements.append(Spacer(1, 0.1 * inch))
        
        footer_text = f"""
        <i>Generated by Real Estate Decision Tool | {datetime.now().strftime('%B %d, %Y %I:%M %p')}</i><br/>
        This analysis is based on the assumptions provided and current market conditions. 
        Consult with qualified financial and tax professionals before making investment decisions.
        """
        
        footer_style = ParagraphStyle(
            'ReportFooter',
            fontSize=8,
            textColor=self.colors['muted'],
            fontName='Helvetica',
            alignment=TA_CENTER,
            spaceAfter=12
        )
        
        footer_elements.append(Paragraph(footer_text, footer_style))
        
        return footer_elements