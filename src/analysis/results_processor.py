"""
Results Processor
Professional formatting and presentation of analysis results

This module provides:
- Currency formatting and professional number display
- Key Performance Indicator (KPI) generation
- Executive summary tables and data structures
- Standardized visualization data preparation
- Professional presentation formatting for all outputs

All formatting follows business presentation standards exactly.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime, date
import numpy as np
import pandas as pd

# Import formatting utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import formatting utilities with fallback handling
try:
    from utils.formatting import format_currency, format_percentage, format_number, CURRENCY_SYMBOLS
except ImportError:
    # Fallback formatting functions if utils.formatting is not available
    def format_currency(amount, currency="USD", include_cents=True):
        """Fallback currency formatting"""
        if amount is None:
            return "N/A"
        symbol = "$" if currency == "USD" else currency
        if include_cents:
            return f"{symbol}{amount:,.2f}"
        else:
            return f"{symbol}{amount:,.0f}"
    
    def format_percentage(value, decimal_places=1):
        """Fallback percentage formatting"""
        if value is None:
            return "N/A"
        return f"{value:.{decimal_places}f}%"
    
    def format_number(value, decimal_places=0):
        """Fallback number formatting"""
        if value is None:
            return "N/A"
        if decimal_places > 0:
            return f"{value:,.{decimal_places}f}"
        else:
            return f"{value:,.0f}"
    
    CURRENCY_SYMBOLS = {
        "USD": "$", "EUR": "€", "GBP": "£", "CAD": "C$",
        "AUD": "A$", "ILS": "₪", "LEI": "lei", "PLN": "zł"
    }

logger = logging.getLogger(__name__)


class ResultsProcessor:
    """
    Professional Results Processor for Real Estate Analysis
    
    Transforms raw calculation results into executive-ready presentations
    with proper formatting, KPIs, and professional data structures.
    """
    
    def __init__(self, currency: str = "USD"):
        """
        Initialize Results Processor
        
        Args:
            currency: Base currency for formatting (USD, EUR, GBP, etc.)
        """
        self.currency = currency
        self.currency_symbol = CURRENCY_SYMBOLS.get(currency, currency)
        self.processing_timestamp = datetime.now()
        
    def process_npv_analysis_results(
        self, 
        npv_results: Dict[str, Any],
        decision_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process NPV analysis results into presentation-ready format
        
        Args:
            npv_results: Raw NPV analysis results
            decision_results: Optional decision engine results
            
        Returns:
            Professionally formatted results with KPIs
        """
        if not npv_results.get('calculation_successful', False):
            return self._format_error_results(npv_results)
        
        processed_results = {
            'executive_summary': self._create_executive_summary(npv_results, decision_results),
            'key_metrics': self._extract_key_metrics(npv_results),
            'financial_comparison': self._create_financial_comparison(npv_results),
            'cash_flow_summary': self._create_cash_flow_summary(npv_results),
            'investment_analysis': self._create_investment_analysis(npv_results),
            'metadata': self._create_metadata(npv_results),
            'presentation_tables': self._create_presentation_tables(npv_results),
            'visualization_data': self._prepare_visualization_data(npv_results)
        }
        
        return processed_results
    
    def _create_executive_summary(
        self, 
        npv_results: Dict[str, Any],
        decision_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create executive summary section"""
        
        recommendation = npv_results.get('recommendation', 'UNKNOWN')
        confidence = npv_results.get('confidence', 'Unknown')
        npv_difference = npv_results.get('npv_difference', 0)
        
        # Use decision results if available
        if decision_results:
            recommendation = decision_results.get('recommendation', recommendation)
            confidence = decision_results.get('confidence_level', confidence)
        
        # Create recommendation icon and color
        if recommendation in ['STRONG_BUY', 'BUY']:
            recommendation_icon = "✅"
            recommendation_color = "success"
            action_text = "Proceed with property purchase"
        elif recommendation in ['MARGINAL_BUY', 'NEUTRAL']:
            recommendation_icon = "⚖️"
            recommendation_color = "warning"
            action_text = "Consider purchase with careful risk assessment"
        elif recommendation in ['MARGINAL_RENT', 'RENT', 'STRONG_RENT']:
            recommendation_icon = "🏠"
            recommendation_color = "info"
            action_text = "Continue with rental arrangement"
        else:
            recommendation_icon = "❌"
            recommendation_color = "error"
            action_text = "Analysis incomplete - review inputs"
        
        return {
            'recommendation': recommendation,
            'recommendation_formatted': f"{recommendation_icon} {recommendation.replace('_', ' ').title()}",
            'recommendation_color': recommendation_color,
            'confidence_level': confidence,
            'action_text': action_text,
            'npv_advantage': format_currency(npv_difference, self.currency, include_cents=False),
            'npv_advantage_raw': float(npv_difference),
            'analysis_period': npv_results.get('analysis_period', 25),
            'cost_of_capital': format_percentage(npv_results.get('cost_of_capital', 8)),
            'summary_statement': self._generate_summary_statement(npv_difference, recommendation)
        }
    
    def _extract_key_metrics(self, npv_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and format key performance indicators"""
        
        # Core NPV metrics
        ownership_npv = npv_results.get('ownership_npv', 0)
        rental_npv = npv_results.get('rental_npv', 0)
        npv_difference = npv_results.get('npv_difference', 0)
        
        # Investment metrics  
        initial_investment = npv_results.get('ownership_initial_investment', 0)
        terminal_value_advantage = npv_results.get('terminal_value_advantage', 0)
        
        # Calculate derived metrics
        # Calculate proper NPV-based ROI
        if initial_investment > 0:
            roi_percentage = (ownership_npv + initial_investment) / initial_investment * 100
        elif initial_investment == 0:
            roi_percentage = float('inf') if npv_difference > 0 else 0.0
        else:
            roi_percentage = 0.0
        terminal_contribution = (terminal_value_advantage / npv_difference * 100) if npv_difference != 0 else 0
        
        return {
            # Primary NPV Metrics
            'ownership_npv': {
                'value': format_currency(ownership_npv, self.currency, include_cents=False),
                'raw_value': float(ownership_npv),
                'label': 'Ownership NPV',
                'description': 'Net present value of ownership scenario'
            },
            'rental_npv': {
                'value': format_currency(rental_npv, self.currency, include_cents=False),
                'raw_value': float(rental_npv),
                'label': 'Rental NPV',
                'description': 'Net present value of rental scenario'
            },
            'npv_advantage': {
                'value': format_currency(npv_difference, self.currency, include_cents=False),
                'raw_value': float(npv_difference),
                'label': 'NPV Advantage',
                'description': 'Net present value difference (positive = ownership better)',
                'is_positive': npv_difference >= 0
            },
            
            # Investment Metrics
            'initial_investment': {
                'value': format_currency(initial_investment, self.currency, include_cents=False),
                'raw_value': float(initial_investment),
                'label': 'Initial Investment',
                'description': 'Total upfront investment required for ownership'
            },
            'roi_percentage': {
                'value': format_percentage(roi_percentage),
                'raw_value': float(roi_percentage),
                'label': 'Return on Investment',
                'description': 'NPV advantage as percentage of initial investment'
            },
            'terminal_value_advantage': {
                'value': format_currency(terminal_value_advantage, self.currency, include_cents=False),
                'raw_value': float(terminal_value_advantage),
                'label': 'Terminal Value Advantage',
                'description': 'Present value of terminal wealth difference'
            },
            'terminal_contribution': {
                'value': format_percentage(terminal_contribution),
                'raw_value': float(terminal_contribution),
                'label': 'Terminal Value Contribution',
                'description': 'Percentage of NPV advantage from terminal value'
            }
        }
    
    def _create_financial_comparison(self, npv_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create side-by-side financial comparison"""
        
        ownership_npv = npv_results.get('ownership_npv', 0)
        rental_npv = npv_results.get('rental_npv', 0)
        initial_investment = npv_results.get('ownership_initial_investment', 0)
        rental_initial = npv_results.get('rental_initial_investment', 0)
        ownership_terminal = npv_results.get('ownership_terminal_value', 0)
        rental_terminal = npv_results.get('rental_terminal_value', 0)
        
        return {
            'ownership_scenario': {
                'initial_investment': format_currency(initial_investment, self.currency, include_cents=False),
                'total_npv': format_currency(ownership_npv, self.currency, include_cents=False),
                'terminal_value': format_currency(ownership_terminal, self.currency, include_cents=False),
                'scenario_type': 'Property Ownership',
                'color_class': 'ownership-scenario'
            },
            'rental_scenario': {
                'initial_investment': format_currency(rental_initial, self.currency, include_cents=False),
                'total_npv': format_currency(rental_npv, self.currency, include_cents=False),
                'terminal_value': format_currency(rental_terminal, self.currency, include_cents=False),
                'scenario_type': 'Property Rental',
                'color_class': 'rental-scenario'
            },
            'comparison_metrics': {
                'npv_difference': format_currency(ownership_npv - rental_npv, self.currency, include_cents=False),
                'initial_difference': format_currency(initial_investment - rental_initial, self.currency, include_cents=False),
                'terminal_difference': format_currency(ownership_terminal - rental_terminal, self.currency, include_cents=False)
            }
        }
    
    def _create_cash_flow_summary(self, npv_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create cash flow analysis summary"""
        
        # Get raw input parameters for cash flow context
        params = npv_results.get('input_parameters', {})
        analysis_period = npv_results.get('analysis_period', 25)
        
        # Estimate annual costs (simplified for summary)
        purchase_price = params.get('purchase_price', 500000)
        annual_rent = params.get('current_annual_rent', 120000)
        
        # Create simplified cash flow summary
        return {
            'analysis_period': analysis_period,
            'annual_ownership_cost_estimate': format_currency(purchase_price * 0.08, self.currency, include_cents=False),  # Rough 8% of value
            'annual_rental_cost_estimate': format_currency(annual_rent, self.currency, include_cents=False),
            'total_ownership_costs_estimate': format_currency(purchase_price * 0.08 * analysis_period, self.currency, include_cents=False),
            'total_rental_costs_estimate': format_currency(annual_rent * analysis_period * 1.5, self.currency, include_cents=False),  # With escalation
            'cash_flow_note': 'Estimates based on NPV analysis inputs - see detailed calculations for year-by-year breakdown'
        }
    
    def _create_investment_analysis(self, npv_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create investment analysis section"""
        
        params = npv_results.get('input_parameters', {})
        
        # Extract key investment parameters
        purchase_price = params.get('purchase_price', 0)
        down_payment_pct = params.get('down_payment_pct', 30)
        interest_rate = params.get('interest_rate', 5)
        market_appreciation = params.get('market_appreciation_rate', 3)
        cost_of_capital = params.get('cost_of_capital', 8)
        
        # Calculate investment ratios
        initial_investment = npv_results.get('ownership_initial_investment', 0)
        npv_difference = npv_results.get('npv_difference', 0)
        
        # Calculate proper investment multiple based on NPV-based ROI
        if initial_investment > 0:
            ownership_npv = npv_results.get('ownership_npv', 0)
            investment_multiple = (ownership_npv + initial_investment) / initial_investment
        else:
            investment_multiple = 0.0
        
        return {
            'purchase_analysis': {
                'purchase_price': format_currency(purchase_price, self.currency, include_cents=False),
                'down_payment': format_percentage(down_payment_pct),
                'financing_rate': format_percentage(interest_rate),
                'initial_equity': format_currency(initial_investment, self.currency, include_cents=False)
            },
            'market_assumptions': {
                'property_appreciation': format_percentage(market_appreciation),
                'cost_of_capital': format_percentage(cost_of_capital),
                'discount_spread': format_percentage(cost_of_capital - market_appreciation)
            },
            'investment_returns': {
                'investment_multiple': f"{investment_multiple:.2f}x",
                'investment_multiple_raw': float(investment_multiple),
                'npv_per_dollar_invested': format_currency(investment_multiple, self.currency),
                'investment_grade': self._classify_investment_grade(investment_multiple)
            }
        }
    
    def _create_metadata(self, npv_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create analysis metadata"""
        
        return {
            'calculation_timestamp': npv_results.get('calculation_timestamp', self.processing_timestamp.isoformat()),
            'processing_timestamp': self.processing_timestamp.isoformat(),
            'currency': self.currency,
            'currency_symbol': self.currency_symbol,
            'validation_status': {
                'has_errors': len(npv_results.get('validation_errors', [])) > 0,
                'has_warnings': len(npv_results.get('calculation_warnings', [])) > 0,
                'errors': npv_results.get('validation_errors', []),
                'warnings': npv_results.get('calculation_warnings', [])
            },
            'analysis_parameters': {
                'analysis_period': npv_results.get('analysis_period', 25),
                'cost_of_capital': npv_results.get('cost_of_capital', 8),
                'calculation_method': 'NPV Analysis with Terminal Value'
            }
        }
    
    def _create_presentation_tables(self, npv_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create tables formatted for presentation"""
        
        # Summary table
        summary_table = [
            ['Metric', 'Ownership', 'Rental', 'Advantage'],
            ['Initial Investment', 
             format_currency(npv_results.get('ownership_initial_investment', 0), self.currency, include_cents=False),
             format_currency(npv_results.get('rental_initial_investment', 0), self.currency, include_cents=False),
             format_currency(npv_results.get('ownership_initial_investment', 0) - npv_results.get('rental_initial_investment', 0), self.currency, include_cents=False)],
            ['Net Present Value',
             format_currency(npv_results.get('ownership_npv', 0), self.currency, include_cents=False),
             format_currency(npv_results.get('rental_npv', 0), self.currency, include_cents=False),
             format_currency(npv_results.get('npv_difference', 0), self.currency, include_cents=False)],
            ['Terminal Value',
             format_currency(npv_results.get('ownership_terminal_value', 0), self.currency, include_cents=False),
             format_currency(npv_results.get('rental_terminal_value', 0), self.currency, include_cents=False),
             format_currency(npv_results.get('terminal_value_advantage', 0), self.currency, include_cents=False)]
        ]
        
        # Parameters table
        params = npv_results.get('input_parameters', {})
        parameters_table = [
            ['Parameter', 'Value'],
            ['Purchase Price', format_currency(params.get('purchase_price', 0), self.currency, include_cents=False)],
            ['Annual Rent', format_currency(params.get('current_annual_rent', 0), self.currency, include_cents=False)],
            ['Down Payment', format_percentage(params.get('down_payment_pct', 30))],
            ['Interest Rate', format_percentage(params.get('interest_rate', 5))],
            ['Market Appreciation', format_percentage(params.get('market_appreciation_rate', 3))],
            ['Cost of Capital', format_percentage(params.get('cost_of_capital', 8))],
            ['Analysis Period', f"{params.get('analysis_period', 25)} years"]
        ]
        
        return {
            'summary_table': summary_table,
            'parameters_table': parameters_table,
            'table_notes': [
                'All monetary values are in present value terms',
                'NPV calculations include terminal value assumptions',
                'Positive NPV advantage indicates ownership is preferable'
            ]
        }
    
    def _prepare_visualization_data(self, npv_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data structures for charts and visualizations"""
        
        # NPV comparison data for bar chart
        npv_comparison = {
            'categories': ['Ownership NPV', 'Rental NPV'],
            'values': [
                npv_results.get('ownership_npv', 0),
                npv_results.get('rental_npv', 0)
            ],
            'colors': ['#2E8B57', '#4682B4'],  # Sea Green, Steel Blue
            'formatted_values': [
                format_currency(npv_results.get('ownership_npv', 0), self.currency, include_cents=False),
                format_currency(npv_results.get('rental_npv', 0), self.currency, include_cents=False)
            ]
        }
        
        # Investment breakdown for pie chart
        initial_investment = npv_results.get('ownership_initial_investment', 0)
        terminal_value = npv_results.get('ownership_terminal_value', 0)
        
        investment_breakdown = {
            'categories': ['Initial Investment', 'NPV of Cash Flows', 'Terminal Value'],
            'values': [
                initial_investment,
                abs(npv_results.get('ownership_npv', 0)) - terminal_value,
                terminal_value
            ],
            'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1']
        }
        
        # Metrics for gauge charts
        # Calculate proper NPV-based ROI
        if initial_investment > 0:
            ownership_npv = npv_results.get('ownership_npv', 0)
            roi_percentage = (ownership_npv + initial_investment) / initial_investment * 100
        else:
            roi_percentage = 0.0
        
        gauge_metrics = {
            'roi_gauge': {
                'value': roi_percentage,
                'min_value': -50,
                'max_value': 50,
                'title': 'Return on Investment (%)',
                'color_ranges': [
                    {'min': -50, 'max': 0, 'color': '#FF6B6B'},
                    {'min': 0, 'max': 15, 'color': '#FFE66D'},
                    {'min': 15, 'max': 50, 'color': '#4ECDC4'}
                ]
            }
        }
        
        return {
            'npv_comparison': npv_comparison,
            'investment_breakdown': investment_breakdown,
            'gauge_metrics': gauge_metrics,
            'data_notes': [
                'Charts show present value amounts',
                'ROI calculated as NPV advantage / initial investment',
                'Terminal value represents final wealth position'
            ]
        }
    
    def _generate_summary_statement(self, npv_difference: float, recommendation: str) -> str:
        """Generate one-line executive summary statement"""
        
        amount_text = format_currency(abs(npv_difference), self.currency, include_cents=False)
        
        if npv_difference > 1000000:
            return f"Strong financial case for ownership with {amount_text} NPV advantage over rental."
        elif npv_difference > 100000:
            return f"Ownership shows {amount_text} NPV advantage - recommend proceeding with purchase."
        elif npv_difference > 0:
            return f"Marginal advantage for ownership ({amount_text} NPV benefit) - consider risk factors."
        elif npv_difference > -100000:
            return f"Minimal difference between scenarios ({amount_text}) - either option viable."
        else:
            return f"Rental preferred with {amount_text} cost advantage over ownership."
    
    def _classify_investment_grade(self, investment_multiple: float) -> str:
        """Classify investment quality based on multiple"""
        
        if investment_multiple >= 3.0:
            return "Excellent"
        elif investment_multiple >= 2.0:
            return "Very Good"
        elif investment_multiple >= 1.5:
            return "Good"
        elif investment_multiple >= 1.0:
            return "Fair"
        elif investment_multiple >= 0.5:
            return "Poor"
        else:
            return "Very Poor"
    
    def _format_error_results(self, npv_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format error results for display with proper error categorization
        
        Error categories:
        - VALIDATION_ERROR: Input validation failures
        - CALCULATION_ERROR: Mathematical computation failures  
        - SYSTEM_ERROR: System or dependency failures
        - DATA_ERROR: Missing or malformed data
        """
        
        error_message = npv_results.get('error_message', 'Unknown calculation error')
        validation_errors = npv_results.get('validation_errors', [])
        
        # Categorize the error
        error_category, error_severity = self._categorize_error(error_message, validation_errors)
        
        # Get category-specific actions and descriptions
        category_info = self._get_error_category_info(error_category)
        
        return {
            'executive_summary': {
                'recommendation': 'ERROR',
                'recommendation_formatted': f'❌ {category_info["display_name"]}',
                'recommendation_color': 'error',
                'confidence_level': 'N/A',
                'action_text': category_info["primary_action"],
                'npv_advantage': 'N/A',
                'summary_statement': f'{category_info["description"]}: {error_message}'
            },
            'error_details': {
                'primary_error': error_message,
                'error_category': error_category,
                'error_severity': error_severity,
                'validation_errors': validation_errors,
                'suggested_actions': category_info["suggested_actions"]
            },
            'metadata': {
                'calculation_timestamp': npv_results.get('calculation_timestamp', datetime.now().isoformat()),
                'processing_timestamp': self.processing_timestamp.isoformat(),
                'currency': self.currency,
                'analysis_successful': False
            }
        }
    
    def process_sensitivity_results(
        self, 
        sensitivity_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process sensitivity analysis results for presentation
        
        Args:
            sensitivity_results: Raw sensitivity analysis results
            
        Returns:
            Formatted sensitivity analysis presentation data
        """
        if not sensitivity_results:
            return {'error': 'No sensitivity results provided'}
        
        # Process tornado chart data
        tornado_data = []
        for item in sensitivity_results.get('tornado_data', []):
            tornado_data.append({
                'parameter': item.get('parameter', 'Unknown'),
                'sensitivity_range': format_currency(item.get('sensitivity_range', 0), self.currency, include_cents=False),
                'sensitivity_range_raw': item.get('sensitivity_range', 0),
                'parameter_name': item.get('parameter_name', '')
            })
        
        # Process break-even summary
        break_even_formatted = {}
        for param_name, break_even_data in sensitivity_results.get('break_even_summary', {}).items():
            break_even_value = break_even_data.get('break_even_value')
            base_value = break_even_data.get('base_value')
            
            if break_even_value is not None and base_value is not None:
                percentage_change = ((break_even_value - base_value) / base_value * 100) if base_value != 0 else 0
                
                break_even_formatted[param_name] = {
                    'label': break_even_data.get('label', param_name),
                    'break_even_value': f"{break_even_value:.2f}",
                    'base_value': f"{base_value:.2f}",
                    'percentage_change': format_percentage(percentage_change),
                    'percentage_change_raw': percentage_change
                }
        
        return {
            'tornado_chart_data': tornado_data,
            'break_even_summary': break_even_formatted,
            'analysis_summary': sensitivity_results.get('analysis_summary', {}),
            'most_sensitive_parameter': sensitivity_results.get('most_sensitive_parameter'),
            'recommendation_stability': sensitivity_results.get('analysis_summary', {}).get('recommendation_stability', 'Unknown')
        }
    
    def create_executive_dashboard_data(
        self, 
        npv_results: Dict[str, Any],
        decision_results: Optional[Dict[str, Any]] = None,
        sensitivity_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive dashboard data for executive presentation
        
        Args:
            npv_results: NPV analysis results
            decision_results: Decision engine results
            sensitivity_results: Sensitivity analysis results
            
        Returns:
            Complete executive dashboard data structure
        """
        # Process main results
        main_results = self.process_npv_analysis_results(npv_results, decision_results)
        
        # Add sensitivity analysis if available
        sensitivity_data = {}
        if sensitivity_results:
            sensitivity_data = self.process_sensitivity_results(sensitivity_results)
        
        # Create dashboard sections
        dashboard = {
            'header': {
                'title': 'Real Estate Investment Analysis',
                'subtitle': f'Buy vs Rent Decision Analysis',
                'timestamp': self.processing_timestamp.strftime('%B %d, %Y at %I:%M %p'),
                'currency': self.currency
            },
            'recommendation_card': main_results.get('executive_summary', {}),
            'key_metrics_cards': self._create_metrics_cards(main_results.get('key_metrics', {})),
            'financial_comparison_table': main_results.get('financial_comparison', {}),
            'investment_analysis_section': main_results.get('investment_analysis', {}),
            'sensitivity_section': sensitivity_data,
            'presentation_charts': main_results.get('visualization_data', {}),
            'metadata': main_results.get('metadata', {})
        }
        
        return dashboard
    
    def _create_metrics_cards(self, key_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create metric cards for dashboard display"""
        
        cards = []
        
        # Primary metrics for cards
        primary_metrics = [
            'npv_advantage',
            'initial_investment', 
            'roi_percentage',
            'terminal_value_advantage'
        ]
        
        for metric_key in primary_metrics:
            if metric_key in key_metrics:
                metric_data = key_metrics[metric_key]
                
                # Determine card color based on metric and value
                card_color = 'primary'
                if metric_key == 'npv_advantage':
                    card_color = 'success' if metric_data.get('is_positive', False) else 'danger'
                elif metric_key == 'roi_percentage':
                    roi_raw = metric_data.get('raw_value', 0)
                    card_color = 'success' if roi_raw >= 10 else 'warning' if roi_raw >= 0 else 'danger'
                
                cards.append({
                    'title': metric_data.get('label', metric_key.title()),
                    'value': metric_data.get('value', 'N/A'),
                    'description': metric_data.get('description', ''),
                    'color': card_color,
                    'metric_key': metric_key
                })
        
        return cards
    
    def export_to_csv(self, processed_results: Dict[str, Any]) -> str:
        """
        Export processed results to CSV format
        
        Args:
            processed_results: Processed analysis results
            
        Returns:
            CSV-formatted string
        """
        try:
            # Create summary data for CSV
            summary_data = []
            
            # Executive summary
            exec_summary = processed_results.get('executive_summary', {})
            summary_data.append(['Metric', 'Value'])
            summary_data.append(['Recommendation', exec_summary.get('recommendation', 'N/A')])
            summary_data.append(['Confidence Level', exec_summary.get('confidence_level', 'N/A')])
            summary_data.append(['NPV Advantage', exec_summary.get('npv_advantage', 'N/A')])
            summary_data.append(['', ''])  # Blank row
            
            # Key metrics
            key_metrics = processed_results.get('key_metrics', {})
            summary_data.append(['Key Metrics', ''])
            for metric_key, metric_data in key_metrics.items():
                summary_data.append([metric_data.get('label', metric_key), metric_data.get('value', 'N/A')])
            
            # Convert to CSV string
            csv_lines = []
            for row in summary_data:
                csv_lines.append(','.join([f'"{str(cell)}"' for cell in row]))
            
            return '\n'.join(csv_lines)
            
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return f"Error,CSV export failed: {str(e)}"
    
    def _categorize_error(self, error_message: str, validation_errors: List[str]) -> Tuple[str, str]:
        """
        Categorize error type and determine severity
        
        Returns:
            Tuple of (error_category, error_severity)
        """
        error_message_lower = error_message.lower()
        
        # Check for validation errors first
        if validation_errors or 'validation' in error_message_lower or 'invalid' in error_message_lower:
            return 'VALIDATION_ERROR', 'MEDIUM'
        
        # Check for calculation errors
        if any(keyword in error_message_lower for keyword in ['division by zero', 'math', 'calculation', 'compute', 'nan', 'infinity']):
            return 'CALCULATION_ERROR', 'HIGH'
            
        # Check for system errors
        if any(keyword in error_message_lower for keyword in ['import', 'module', 'system', 'permission', 'file not found']):
            return 'SYSTEM_ERROR', 'HIGH'
            
        # Check for data errors
        if any(keyword in error_message_lower for keyword in ['missing', 'empty', 'null', 'data', 'field']):
            return 'DATA_ERROR', 'MEDIUM'
        
        # Default to system error for unknown issues
        return 'SYSTEM_ERROR', 'HIGH'
    
    def _get_error_category_info(self, error_category: str) -> Dict[str, Any]:
        """Get display information and suggested actions for error category"""
        
        category_info = {
            'VALIDATION_ERROR': {
                'display_name': 'Input Validation Error',
                'description': 'Invalid input parameters provided',
                'primary_action': 'Review and correct input values',
                'suggested_actions': [
                    'Check all required fields are filled with valid values',
                    'Verify numeric inputs are within acceptable ranges',
                    'Ensure percentages are between 0-100%',
                    'Confirm purchase price and rent values are reasonable'
                ]
            },
            'CALCULATION_ERROR': {
                'display_name': 'Calculation Error',
                'description': 'Mathematical computation failed',
                'primary_action': 'Check input values causing calculation issues',
                'suggested_actions': [
                    'Review for zero or negative values where positive required',
                    'Check for extreme values that may cause overflow',
                    'Verify interest rates and percentages are reasonable',
                    'Ensure analysis period is appropriate'
                ]
            },
            'SYSTEM_ERROR': {
                'display_name': 'System Error',
                'description': 'System or dependency issue occurred',
                'primary_action': 'Contact system administrator',
                'suggested_actions': [
                    'Refresh the page and try again',
                    'Check system status and dependencies',
                    'Contact technical support if problem persists',
                    'Try with simplified input values'
                ]
            },
            'DATA_ERROR': {
                'display_name': 'Data Error',
                'description': 'Missing or malformed data detected',
                'primary_action': 'Provide all required data fields',
                'suggested_actions': [
                    'Fill in all required fields',
                    'Check data format and structure',
                    'Verify uploaded files are valid',
                    'Ensure all numeric fields contain numbers'
                ]
            }
        }
        
        return category_info.get(error_category, category_info['SYSTEM_ERROR'])


# Convenience functions for external use
def process_analysis_results(
    npv_results: Dict[str, Any], 
    currency: str = "USD",
    decision_results: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process analysis results with default settings
    
    Args:
        npv_results: NPV analysis results
        currency: Currency for formatting
        decision_results: Optional decision results
        
    Returns:
        Processed results ready for presentation
    """
    processor = ResultsProcessor(currency)
    return processor.process_npv_analysis_results(npv_results, decision_results)


def create_executive_summary(
    npv_results: Dict[str, Any], 
    currency: str = "USD"
) -> Dict[str, Any]:
    """
    Create executive summary from NPV results
    
    Args:
        npv_results: NPV analysis results
        currency: Currency for formatting
        
    Returns:
        Executive summary data
    """
    processor = ResultsProcessor(currency)
    processed = processor.process_npv_analysis_results(npv_results)
    return processed.get('executive_summary', {})


if __name__ == "__main__":
    # Test the results processor
    print("Testing Results Processor...")
    
    # Create test NPV results
    test_npv_results = {
        'calculation_successful': True,
        'npv_difference': 750000,
        'ownership_npv': -2500000,
        'rental_npv': -3250000,
        'ownership_initial_investment': 150000,
        'rental_initial_investment': 15000,
        'terminal_value_advantage': 500000,
        'ownership_terminal_value': 800000,
        'rental_terminal_value': 300000,
        'recommendation': 'BUY',
        'confidence': 'Medium',
        'analysis_period': 25,
        'cost_of_capital': 8.0,
        'input_parameters': {
            'purchase_price': 500000,
            'current_annual_rent': 120000,
            'down_payment_pct': 30,
            'interest_rate': 5.0,
            'market_appreciation_rate': 3.5,
            'cost_of_capital': 8.0,
            'analysis_period': 25
        }
    }
    
    # Test results processing
    processor = ResultsProcessor("USD")
    processed_results = processor.process_npv_analysis_results(test_npv_results)
    
    print("✅ Results processing completed")
    
    # Test key components
    executive_summary = processed_results.get('executive_summary', {})
    key_metrics = processed_results.get('key_metrics', {})
    
    print(f"Recommendation: {executive_summary.get('recommendation_formatted')}")
    print(f"NPV Advantage: {executive_summary.get('npv_advantage')}")
    print(f"ROI: {key_metrics.get('roi_percentage', {}).get('value', 'N/A')}")
    
    # Test dashboard creation
    dashboard_data = processor.create_executive_dashboard_data(test_npv_results)
    print(f"\n✅ Executive dashboard created with {len(dashboard_data)} sections")
    
    # Test CSV export
    csv_data = processor.export_to_csv(processed_results)
    print(f"✅ CSV export completed ({len(csv_data)} characters)")
    print(f"CSV preview: {csv_data[:100]}...")