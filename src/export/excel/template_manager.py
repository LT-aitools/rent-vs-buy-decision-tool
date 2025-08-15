"""
Excel Template Manager
Manages different Excel export templates and configurations

This module provides:
- Multiple template types (Executive, Detailed, Investor, Full Analysis)
- Template configuration and validation
- Customizable headers and branding
- Worksheet structure definitions
- Professional styling presets

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Available Excel template types"""
    EXECUTIVE = "executive"
    DETAILED = "detailed"
    INVESTOR = "investor"
    FULL_ANALYSIS = "full_analysis"


class ExcelTemplateManager:
    """
    Manages Excel export templates and configurations
    
    Provides different template configurations for various use cases:
    - Executive: High-level summary for executives
    - Detailed: Comprehensive analysis for analysts  
    - Investor: Investment-focused metrics for investors
    - Full Analysis: Complete data dump for deep analysis
    """
    
    def __init__(self):
        """Initialize template manager with predefined configurations"""
        self.templates = self._load_template_configurations()
        logger.info("ExcelTemplateManager initialized with templates: %s", list(self.templates.keys()))
    
    def _load_template_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Load all template configurations"""
        
        return {
            TemplateType.EXECUTIVE.value: {
                'name': 'Executive Summary',
                'description': 'High-level summary for executive review',
                'worksheets': [
                    {
                        'name': 'Executive Summary',
                        'type': 'executive_summary',
                        'order': 1,
                        'include_charts': True,
                        'chart_types': ['recommendation_chart', 'npv_comparison'],
                        'sections': [
                            'recommendation',
                            'key_metrics',
                            'financial_summary',
                            'risk_assessment'
                        ]
                    },
                    {
                        'name': 'Key Assumptions',
                        'type': 'assumptions',
                        'order': 2,
                        'include_charts': False,
                        'sections': ['critical_assumptions']
                    }
                ],
                'branding': {
                    'company_name': 'Real Estate Decision Analytics',
                    'report_title': 'Executive Investment Summary',
                    'color_scheme': 'professional',
                    'include_logo': True
                },
                'formatting': {
                    'currency_precision': 0,  # No cents for executive view
                    'percentage_precision': 1,
                    'highlight_recommendations': True,
                    'use_conditional_formatting': True
                }
            },
            
            TemplateType.DETAILED.value: {
                'name': 'Detailed Analysis',
                'description': 'Comprehensive analysis for financial professionals',
                'worksheets': [
                    {
                        'name': 'Executive Summary',
                        'type': 'executive_summary',
                        'order': 1,
                        'include_charts': True,
                        'chart_types': ['npv_comparison', 'cash_flow_trend'],
                        'sections': [
                            'recommendation',
                            'key_metrics',
                            'financial_summary',
                            'sensitivity_summary'
                        ]
                    },
                    {
                        'name': 'Cash Flow Analysis',
                        'type': 'cash_flows',
                        'order': 2,
                        'include_charts': True,
                        'chart_types': ['annual_cash_flows', 'cumulative_cash_flows'],
                        'sections': [
                            'ownership_cash_flows',
                            'rental_cash_flows',
                            'comparison_table',
                            'npv_calculations'
                        ]
                    },
                    {
                        'name': 'Charts & Data',
                        'type': 'charts',
                        'order': 3,
                        'include_charts': True,
                        'chart_types': ['all_charts'],
                        'sections': ['embedded_charts']
                    },
                    {
                        'name': 'Detailed Calculations',
                        'type': 'calculations',
                        'order': 4,
                        'include_charts': False,
                        'sections': [
                            'mortgage_schedule',
                            'tax_calculations',
                            'terminal_value',
                            'depreciation_schedule'
                        ]
                    },
                    {
                        'name': 'Sensitivity Analysis',
                        'type': 'sensitivity',
                        'order': 5,
                        'include_charts': False,
                        'sections': ['2d_sensitivity_tables', 'interpretation_guide']
                    },
                    {
                        'name': 'Input Assumptions',
                        'type': 'assumptions',
                        'order': 6,
                        'include_charts': False,
                        'sections': ['all_assumptions']
                    }
                ],
                'branding': {
                    'company_name': 'Real Estate Decision Analytics',
                    'report_title': 'Comprehensive Investment Analysis',
                    'color_scheme': 'detailed',
                    'include_logo': True
                },
                'formatting': {
                    'currency_precision': 2,  # Include cents for detailed view
                    'percentage_precision': 2,
                    'highlight_recommendations': True,
                    'use_conditional_formatting': True,
                    'show_formulas': False,
                    'freeze_panes': True
                }
            },
            
            TemplateType.INVESTOR.value: {
                'name': 'Investor Report',
                'description': 'Investment-focused metrics for stakeholders',
                'worksheets': [
                    {
                        'name': 'Investment Summary',
                        'type': 'executive_summary',
                        'order': 1,
                        'include_charts': True,
                        'chart_types': ['roi_analysis', 'risk_return_chart'],
                        'sections': [
                            'investment_recommendation',
                            'financial_returns',
                            'risk_metrics',
                            'market_assumptions'
                        ]
                    },
                    {
                        'name': 'Financial Projections',
                        'type': 'cash_flows',
                        'order': 2,
                        'include_charts': True,
                        'chart_types': ['projected_returns', 'cash_flow_waterfall'],
                        'sections': [
                            'projected_cash_flows',
                            'return_analysis',
                            'break_even_analysis'
                        ]
                    },
                    {
                        'name': 'Risk Analysis',
                        'type': 'calculations',
                        'order': 3,
                        'include_charts': True,
                        'chart_types': ['sensitivity_analysis', 'scenario_analysis'],
                        'sections': [
                            'sensitivity_analysis',
                            'scenario_modeling',
                            'risk_mitigation'
                        ]
                    },
                    {
                        'name': 'Key Assumptions',
                        'type': 'assumptions',
                        'order': 4,
                        'include_charts': False,
                        'sections': ['investment_assumptions']
                    }
                ],
                'branding': {
                    'company_name': 'Real Estate Investment Analytics',
                    'report_title': 'Investment Decision Report',
                    'color_scheme': 'investor',
                    'include_logo': True
                },
                'formatting': {
                    'currency_precision': 0,
                    'percentage_precision': 2,
                    'highlight_recommendations': True,
                    'use_conditional_formatting': True,
                    'show_irr_calculations': True,
                    'include_benchmarks': True
                }
            },
            
            TemplateType.FULL_ANALYSIS.value: {
                'name': 'Complete Analysis',
                'description': 'Full data export for comprehensive review',
                'worksheets': [
                    {
                        'name': 'Executive Summary',
                        'type': 'executive_summary',
                        'order': 1,
                        'include_charts': True,
                        'chart_types': ['all_summary_charts'],
                        'sections': ['complete_summary']
                    },
                    {
                        'name': 'Cash Flow Analysis',
                        'type': 'cash_flows',
                        'order': 2,
                        'include_charts': True,
                        'chart_types': ['all_cash_flow_charts'],
                        'sections': ['complete_cash_flows']
                    },
                    {
                        'name': 'Charts & Visualizations',
                        'type': 'charts',
                        'order': 3,
                        'include_charts': True,
                        'chart_types': ['all_charts'],
                        'sections': ['all_visualizations']
                    },
                    {
                        'name': 'Detailed Calculations',
                        'type': 'calculations',
                        'order': 4,
                        'include_charts': False,
                        'sections': ['all_calculations']
                    },
                    {
                        'name': 'Input Assumptions',
                        'type': 'assumptions',
                        'order': 5,
                        'include_charts': False,
                        'sections': ['all_assumptions']
                    },
                    {
                        'name': 'Sensitivity Analysis',
                        'type': 'sensitivity',
                        'order': 6,
                        'include_charts': True,
                        'chart_types': ['sensitivity_charts'],
                        'sections': ['sensitivity_tables']
                    },
                    {
                        'name': 'Raw Data',
                        'type': 'raw_data',
                        'order': 7,
                        'include_charts': False,
                        'sections': ['session_data', 'calculation_intermediates']
                    }
                ],
                'branding': {
                    'company_name': 'Real Estate Decision Analytics',
                    'report_title': 'Complete Investment Analysis',
                    'color_scheme': 'comprehensive',
                    'include_logo': True
                },
                'formatting': {
                    'currency_precision': 2,
                    'percentage_precision': 3,
                    'highlight_recommendations': True,
                    'use_conditional_formatting': True,
                    'show_formulas': True,
                    'freeze_panes': True,
                    'include_data_validation': True,
                    'enable_filtering': True
                }
            }
        }
    
    async def get_template_config(self, template_type: str) -> Dict[str, Any]:
        """
        Get configuration for specified template type
        
        Args:
            template_type: Template type identifier
            
        Returns:
            Complete template configuration
            
        Raises:
            ValueError: If template type is not supported
        """
        if template_type not in self.templates:
            raise ValueError(f"Unsupported template type: {template_type}. Available types: {list(self.templates.keys())}")
        
        config = self.templates[template_type].copy()
        
        # Add dynamic metadata
        config['generation_metadata'] = {
            'template_type': template_type,
            'generated_at': datetime.now().isoformat(),
            'template_version': '1.0.0',
            'generator': 'Real Estate Decision Tool'
        }
        
        logger.info(f"Retrieved template configuration: {template_type}")
        return config
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """
        Get list of available template types with descriptions
        
        Returns:
            List of template info dictionaries
        """
        templates_info = []
        
        for template_id, config in self.templates.items():
            templates_info.append({
                'id': template_id,
                'name': config['name'],
                'description': config['description'],
                'worksheet_count': len(config['worksheets'])
            })
        
        return templates_info
    
    def validate_template_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate template configuration completeness
        
        Args:
            config: Template configuration to validate
            
        Returns:
            Validation results with any issues found
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required top-level keys
        required_keys = ['name', 'description', 'worksheets', 'branding', 'formatting']
        for key in required_keys:
            if key not in config:
                validation_results['errors'].append(f"Missing required key: {key}")
                validation_results['is_valid'] = False
        
        # Validate worksheets
        if 'worksheets' in config:
            worksheets = config['worksheets']
            if not isinstance(worksheets, list) or len(worksheets) == 0:
                validation_results['errors'].append("Worksheets must be a non-empty list")
                validation_results['is_valid'] = False
            else:
                # Validate each worksheet
                worksheet_names = set()
                for i, worksheet in enumerate(worksheets):
                    worksheet_validation = self._validate_worksheet_config(worksheet, i)
                    validation_results['errors'].extend(worksheet_validation['errors'])
                    validation_results['warnings'].extend(worksheet_validation['warnings'])
                    
                    if not worksheet_validation['is_valid']:
                        validation_results['is_valid'] = False
                    
                    # Check for duplicate names
                    name = worksheet.get('name', f'Sheet_{i}')
                    if name in worksheet_names:
                        validation_results['errors'].append(f"Duplicate worksheet name: {name}")
                        validation_results['is_valid'] = False
                    worksheet_names.add(name)
        
        # Validate branding
        if 'branding' in config:
            branding = config['branding']
            if not isinstance(branding, dict):
                validation_results['errors'].append("Branding must be a dictionary")
                validation_results['is_valid'] = False
        
        # Validate formatting
        if 'formatting' in config:
            formatting = config['formatting']
            if not isinstance(formatting, dict):
                validation_results['errors'].append("Formatting must be a dictionary")
                validation_results['is_valid'] = False
        
        return validation_results
    
    def _validate_worksheet_config(self, worksheet: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate individual worksheet configuration"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Required worksheet keys
        required_keys = ['name', 'type', 'order']
        for key in required_keys:
            if key not in worksheet:
                validation_results['errors'].append(f"Worksheet {index}: Missing required key '{key}'")
                validation_results['is_valid'] = False
        
        # Validate worksheet type
        valid_types = ['executive_summary', 'cash_flows', 'charts', 'calculations', 'assumptions', 'sensitivity', 'raw_data']
        worksheet_type = worksheet.get('type')
        if worksheet_type and worksheet_type not in valid_types:
            validation_results['warnings'].append(f"Worksheet {index}: Unknown worksheet type '{worksheet_type}'")
        
        # Validate order
        order = worksheet.get('order')
        if order is not None and (not isinstance(order, int) or order < 1):
            validation_results['errors'].append(f"Worksheet {index}: Order must be a positive integer")
            validation_results['is_valid'] = False
        
        return validation_results
    
    def customize_template(
        self,
        base_template: str,
        customizations: Dict[str, Any],
        custom_name: Optional[str] = None
    ) -> str:
        """
        Create customized version of existing template
        
        Args:
            base_template: Base template type to customize
            customizations: Dictionary of customizations to apply
            custom_name: Optional name for the custom template
            
        Returns:
            ID of the new custom template
            
        Raises:
            ValueError: If base template doesn't exist
        """
        if base_template not in self.templates:
            raise ValueError(f"Base template '{base_template}' not found")
        
        # Create custom template ID
        custom_id = custom_name if custom_name else f"{base_template}_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Deep copy base template
        import copy
        custom_config = copy.deepcopy(self.templates[base_template])
        
        # Apply customizations
        self._apply_customizations(custom_config, customizations)
        
        # Update metadata
        custom_config['name'] = custom_name or f"Custom {custom_config['name']}"
        custom_config['description'] = f"Customized version of {base_template}"
        custom_config['base_template'] = base_template
        custom_config['customized_at'] = datetime.now().isoformat()
        
        # Store custom template
        self.templates[custom_id] = custom_config
        
        logger.info(f"Created custom template '{custom_id}' based on '{base_template}'")
        return custom_id
    
    def _apply_customizations(self, config: Dict[str, Any], customizations: Dict[str, Any]) -> None:
        """Apply customizations to template configuration"""
        
        for key, value in customizations.items():
            if key == 'worksheets':
                # Handle worksheet customizations
                self._customize_worksheets(config.get('worksheets', []), value)
            elif key in ['branding', 'formatting']:
                # Handle nested dictionary updates
                if key in config:
                    config[key].update(value)
                else:
                    config[key] = value
            else:
                # Handle direct value updates
                config[key] = value
    
    def _customize_worksheets(self, worksheets: List[Dict[str, Any]], worksheet_customizations: Dict[str, Any]) -> None:
        """Apply customizations to worksheet configurations"""
        
        # Handle adding new worksheets
        if 'add' in worksheet_customizations:
            for new_worksheet in worksheet_customizations['add']:
                worksheets.append(new_worksheet)
        
        # Handle removing worksheets
        if 'remove' in worksheet_customizations:
            worksheets_to_remove = worksheet_customizations['remove']
            worksheets[:] = [ws for ws in worksheets if ws.get('name') not in worksheets_to_remove]
        
        # Handle modifying existing worksheets
        if 'modify' in worksheet_customizations:
            modifications = worksheet_customizations['modify']
            for worksheet in worksheets:
                worksheet_name = worksheet.get('name')
                if worksheet_name in modifications:
                    worksheet.update(modifications[worksheet_name])
    
    def get_template_preview(self, template_type: str) -> Dict[str, Any]:
        """
        Get preview information for a template type
        
        Args:
            template_type: Template type to preview
            
        Returns:
            Preview information including worksheet list and key features
        """
        if template_type not in self.templates:
            raise ValueError(f"Template type '{template_type}' not found")
        
        config = self.templates[template_type]
        
        return {
            'template_id': template_type,
            'name': config['name'],
            'description': config['description'],
            'worksheet_count': len(config['worksheets']),
            'worksheets': [
                {
                    'name': ws['name'],
                    'type': ws['type'],
                    'includes_charts': ws.get('include_charts', False),
                    'sections': ws.get('sections', [])
                }
                for ws in config['worksheets']
            ],
            'features': {
                'includes_charts': any(ws.get('include_charts', False) for ws in config['worksheets']),
                'currency_precision': config['formatting'].get('currency_precision', 2),
                'conditional_formatting': config['formatting'].get('use_conditional_formatting', False),
                'custom_branding': config['branding'].get('include_logo', False)
            }
        }
    
    def get_color_schemes(self) -> Dict[str, Dict[str, str]]:
        """
        Get available color schemes for templates
        
        Returns:
            Dictionary of color scheme definitions
        """
        return {
            'professional': {
                'primary': 'FF6B6B',      # Real Estate Decision Tool primary
                'secondary': 'FFA07A',    # Light salmon
                'success': '96CEB4',      # Mint green
                'warning': 'FECA57',      # Yellow
                'danger': 'FF7675',       # Light red
                'info': '74B9FF',         # Light blue
                'light': 'F8F9FA',        # Light gray
                'dark': '2D3436'          # Dark gray
            },
            'detailed': {
                'primary': '2E86AB',      # Professional blue
                'secondary': '4F95A3',    # Medium blue
                'success': '8FBC8F',      # Light green
                'warning': 'F4A261',      # Orange
                'danger': 'E63946',       # Red
                'info': '457B9D',         # Dark blue
                'light': 'F1FAEE',        # Off-white
                'dark': '1D3557'          # Navy
            },
            'investor': {
                'primary': '264653',      # Dark teal
                'secondary': '2A9D8F',    # Teal
                'success': '43AA8B',      # Green
                'warning': 'F9C74F',      # Gold
                'danger': 'F8961E',       # Orange
                'info': '277DA1',         # Blue
                'light': 'F1FAEE',        # Light green
                'dark': '264653'          # Dark teal
            },
            'comprehensive': {
                'primary': '6A4C93',      # Purple
                'secondary': '9C89B8',    # Light purple
                'success': '4CAF50',      # Green
                'warning': 'FF9800',      # Orange
                'danger': 'F44336',       # Red
                'info': '2196F3',         # Blue
                'light': 'F3E5F5',        # Light purple
                'dark': '4A148C'          # Dark purple
            }
        }
    
    def get_recommended_template(self, export_context: Dict[str, Any]) -> str:
        """
        Get recommended template based on export context and data size
        
        Args:
            export_context: Context information about the export
            
        Returns:
            Recommended template type
        """
        # Default to detailed template
        recommended = TemplateType.DETAILED.value
        
        # Executive template for simple presentations
        if export_context.get('presentation_mode') == 'executive':
            recommended = TemplateType.EXECUTIVE.value
        
        # Investor template for investment decisions
        elif export_context.get('audience') == 'investors':
            recommended = TemplateType.INVESTOR.value
        
        # Full analysis for comprehensive reviews
        elif export_context.get('include_sensitivity', True) and export_context.get('include_raw_data', False):
            recommended = TemplateType.FULL_ANALYSIS.value
        
        logger.info(f"Recommended template: {recommended} based on context")
        return recommended
    
    def get_template_size_estimate(self, template_type: str, data_points: int = 25) -> Dict[str, Any]:
        """
        Estimate template size and complexity
        
        Args:
            template_type: Template type to analyze
            data_points: Number of years/data points in analysis
            
        Returns:
            Size estimate information
        """
        if template_type not in self.templates:
            raise ValueError(f"Template type '{template_type}' not found")
        
        config = self.templates[template_type]
        worksheet_count = len(config['worksheets'])
        
        # Estimate data rows based on worksheets and data points
        estimated_rows = 0
        for worksheet in config['worksheets']:
            if worksheet['type'] == 'cash_flows':
                estimated_rows += data_points * 3  # Ownership, rental, comparison tables
            elif worksheet['type'] == 'calculations':
                estimated_rows += 50  # Various calculation tables
            elif worksheet['type'] == 'assumptions':
                estimated_rows += 30  # Input parameters
            elif worksheet['type'] == 'charts':
                estimated_rows += 10  # Chart titles and spacing
            else:
                estimated_rows += 20  # Other content
        
        # Rough file size estimate (Excel files compress well)
        estimated_size_kb = (estimated_rows * worksheet_count * 0.5) + 100  # Base size
        
        return {
            'template_type': template_type,
            'worksheet_count': worksheet_count,
            'estimated_rows': estimated_rows,
            'estimated_size_kb': round(estimated_size_kb),
            'complexity': 'Low' if worksheet_count <= 2 else 'Medium' if worksheet_count <= 4 else 'High',
            'generation_time_estimate_seconds': worksheet_count * 2 + (10 if config.get('worksheets', [{}])[0].get('include_charts') else 0)
        }