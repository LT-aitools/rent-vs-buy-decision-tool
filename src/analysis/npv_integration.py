"""
NPV Integration Engine
Connects Streamlit UI session state to calculation functions with validation

This module provides:
- Input validation pipeline: UI → Calculations → Results  
- Transformation of user inputs into calculation-ready parameters
- Edge case handling and error management
- Professional data structure standardization
- Session state integration for Streamlit

All integrations follow the Business PRD specifications exactly.
"""

import streamlit as st
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculations.npv_analysis import calculate_npv_comparison
from calculations.mortgage import calculate_mortgage_payment, calculate_loan_amount
from calculations.annual_costs import calculate_annual_ownership_costs, calculate_annual_rental_costs
from calculations.terminal_value import calculate_terminal_value, calculate_rental_terminal_value
from utils.defaults import DEFAULT_VALUES, get_default_value
# Import formatting utilities with fallback handling
try:
    from utils.formatting import format_currency, format_percentage
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

logger = logging.getLogger(__name__)


class NPVIntegrationEngine:
    """
    NPV Integration Engine - Bridge between Streamlit UI and calculation functions
    
    This class handles the complete data pipeline:
    1. Extract inputs from Streamlit session state
    2. Validate and transform inputs for calculations
    3. Execute NPV calculations with error handling
    4. Return standardized results for visualization
    """
    
    def __init__(self):
        """Initialize the NPV Integration Engine"""
        self.validation_errors = []
        self.calculation_warnings = []
        self.last_calculation_time = None
        
    def extract_inputs_from_session(self, session_state: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extract and validate all inputs from Streamlit session state
        
        Args:
            session_state: Streamlit session state dict (uses st.session_state if None)
        
        Returns:
            Dictionary with standardized input parameters for calculations
            
        Raises:
            ValueError: If critical inputs are missing or invalid
        """
        if session_state is None:
            session_state = st.session_state
            
        # Extract all inputs with defaults
        inputs = {}
        self.validation_errors = []
        
        # Critical inputs that must be present
        critical_fields = [
            'purchase_price', 'current_annual_rent', 'ownership_property_size', 
            'rental_property_size', 'current_space_needed', 'analysis_period', 'cost_of_capital'
        ]
        
        # Extract all fields with validation
        for field_name, default_value in DEFAULT_VALUES.items():
            raw_value = session_state.get(field_name, default_value)
            
            # Handle special field types
            if field_name == 'analysis_date' and isinstance(raw_value, (datetime, date)):
                inputs[field_name] = raw_value
            elif field_name in ['interest_deductible', 'property_tax_deductible', 'rent_deductible', 'subletting_potential']:
                inputs[field_name] = bool(raw_value)
            elif field_name in ['project_name', 'location', 'analyst_name', 'currency', 'property_type', 'future_expansion_year']:
                inputs[field_name] = str(raw_value) if raw_value else default_value
            else:
                # Numeric fields
                try:
                    if raw_value is None or raw_value == '':
                        inputs[field_name] = float(default_value) if default_value is not None else 0.0
                    else:
                        inputs[field_name] = float(raw_value)
                except (ValueError, TypeError) as e:
                    self.validation_errors.append(f"Invalid value for {field_name}: {raw_value}")
                    inputs[field_name] = float(default_value) if default_value is not None else 0.0
        
        # Validate critical fields
        for field in critical_fields:
            if inputs.get(field) is None or inputs.get(field) <= 0:
                self.validation_errors.append(f"Critical field '{field}' is missing or invalid")
        
        # Additional logical validations
        if inputs.get('down_payment_percent', 0) < 0 or inputs.get('down_payment_percent', 0) > 100:
            self.validation_errors.append("Down payment percentage must be between 0% and 100%")
            
        # Check that current space needed doesn't exceed either property size
        current_space = inputs.get('current_space_needed', 0)
        ownership_size = inputs.get('ownership_property_size', 0)
        rental_size = inputs.get('rental_property_size', 0)
        
        if current_space > ownership_size:
            self.validation_errors.append(f"Current space needed ({current_space:,.0f} m²) exceeds ownership property size ({ownership_size:,.0f} m²)")
        
        if current_space > rental_size:
            self.validation_errors.append(f"Current space needed ({current_space:,.0f} m²) exceeds rental property size ({rental_size:,.0f} m²)")
            
        if inputs.get('interest_rate', 0) < 0 or inputs.get('interest_rate', 0) > 20:
            self.validation_errors.append("Interest rate must be between 0% and 20%")
            
        # Log validation results
        if self.validation_errors:
            logger.warning(f"Input validation errors: {self.validation_errors}")
            
        return inputs
    
    def transform_inputs_for_calculations(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform UI inputs into calculation-ready parameters
        
        Args:
            inputs: Raw inputs from session state
            
        Returns:
            Parameters formatted for calculation functions
        """
        # Create calculation parameters dictionary
        calc_params = {
            # Purchase scenario parameters
            'purchase_price': float(inputs.get('purchase_price', 500000)),
            'down_payment_pct': float(inputs.get('down_payment_percent', 30.0)),
            'interest_rate': float(inputs.get('interest_rate', 5.0)),
            'loan_term': int(inputs.get('loan_term', 20)),
            'transaction_costs': float(inputs.get('purchase_price', 500000)) * float(inputs.get('transaction_costs_percent', 5.0)) / 100,
            
            # Rental scenario parameters  
            'current_annual_rent': float(inputs.get('current_annual_rent', 120000)),
            'rent_increase_rate': float(inputs.get('rent_increase_rate', 3.0)),
            'security_deposit': float(inputs.get('current_annual_rent', 120000)) / 12 * float(inputs.get('security_deposit_months', 2)),
            'rental_commission': float(inputs.get('current_annual_rent', 120000)) / 12 * float(inputs.get('rental_commission_months', 1)),
            'moving_costs': float(inputs.get('moving_costs', 10000)),
            
            # Common parameters
            'analysis_period': int(inputs.get('analysis_period', 25)),
            'cost_of_capital': float(inputs.get('cost_of_capital', 8.0)),
            
            # Property cost parameters
            'property_tax_rate': float(inputs.get('property_tax_rate', 1.2)),
            'property_tax_escalation': float(inputs.get('property_tax_escalation_rate', 2.0)),
            'insurance_cost': float(inputs.get('insurance_cost', 5000)),
            'annual_maintenance': float(inputs.get('purchase_price', 500000)) * float(inputs.get('annual_maintenance_percent', 2.0)) / 100,
            'property_management': float(inputs.get('property_management', 0)),
            'capex_reserve_rate': float(inputs.get('longterm_capex_reserve', 1.5)),
            'obsolescence_risk_rate': float(inputs.get('obsolescence_risk_factor', 0.5)),
            'inflation_rate': float(inputs.get('inflation_rate', 3.0)),
            
            # Terminal value parameters
            'land_value_pct': float(inputs.get('land_value_percent', 25.0)),
            'market_appreciation_rate': float(inputs.get('market_appreciation_rate', 3.0)),
            'depreciation_period': int(inputs.get('depreciation_period', 39)),
            
            # Tax parameters
            'corporate_tax_rate': float(inputs.get('corporate_tax_rate', 25.0)),
            'interest_deductible': bool(inputs.get('interest_deductible', True)),
            'property_tax_deductible': bool(inputs.get('property_tax_deductible', True)),
            'rent_deductible': bool(inputs.get('rent_deductible', True))
        }
        
        return calc_params
    
    def execute_npv_analysis(self, calc_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute NPV analysis with comprehensive error handling
        
        Args:
            calc_params: Calculation-ready parameters
            
        Returns:
            NPV analysis results with metadata
        """
        try:
            # Record calculation start time
            self.last_calculation_time = datetime.now()
            
            # Execute NPV comparison
            results = calculate_npv_comparison(**calc_params)
            
            # Add calculation metadata
            results.update({
                'calculation_timestamp': self.last_calculation_time.isoformat(),
                'input_parameters': calc_params.copy(),
                'validation_errors': self.validation_errors.copy(),
                'calculation_warnings': self.calculation_warnings.copy(),
                'calculation_successful': True
            })
            
            logger.info(f"NPV calculation completed successfully. Recommendation: {results.get('recommendation')}")
            
            return results
            
        except Exception as e:
            error_msg = f"NPV calculation failed: {str(e)}"
            logger.error(error_msg)
            
            # Return error result
            return {
                'calculation_successful': False,
                'error_message': error_msg,
                'recommendation': 'ERROR',
                'confidence': 'Low',
                'npv_difference': 0.0,
                'ownership_npv': 0.0,
                'rental_npv': 0.0,
                'calculation_timestamp': datetime.now().isoformat(),
                'input_parameters': calc_params.copy(),
                'validation_errors': self.validation_errors.copy()
            }
    
    def validate_calculation_inputs(self, calc_params: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Perform deep validation of calculation parameters
        
        Args:
            calc_params: Parameters for NPV calculation
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate required parameters exist
        required_params = [
            'purchase_price', 'current_annual_rent', 'analysis_period', 'cost_of_capital'
        ]
        
        for param in required_params:
            if param not in calc_params or calc_params[param] is None:
                errors.append(f"Missing required parameter: {param}")
        
        # Validate parameter ranges (comprehensive validation for all key parameters)
        validations = [
            # Core financial parameters
            ('purchase_price', lambda x: x > 0, "Purchase price must be positive"),
            ('current_annual_rent', lambda x: x > 0, "Annual rent must be positive"),
            ('down_payment_pct', lambda x: 0 <= x <= 100, "Down payment must be 0-100%"),
            ('interest_rate', lambda x: 0 <= x <= 25, "Interest rate must be 0-25%"),
            ('analysis_period', lambda x: 1 <= x <= 100, "Analysis period must be 1-100 years"),
            ('cost_of_capital', lambda x: 0 <= x <= 50, "Cost of capital must be 0-50%"),
            ('loan_term', lambda x: 0 <= x <= 50, "Loan term must be 0-50 years"),
            
            # Rental parameters
            ('rent_increase_rate', lambda x: 0 <= x <= 20, "Rent increase rate must be 0-20%"),
            ('security_deposit', lambda x: x >= 0, "Security deposit cannot be negative"),
            ('rental_commission', lambda x: x >= 0, "Rental commission cannot be negative"),
            ('moving_costs', lambda x: x >= 0, "Moving costs cannot be negative"),
            
            # Property costs
            ('property_tax_rate', lambda x: 0 <= x <= 10, "Property tax rate must be 0-10%"),
            ('property_tax_escalation', lambda x: 0 <= x <= 10, "Property tax escalation must be 0-10%"),
            ('insurance_cost', lambda x: x >= 0, "Insurance cost cannot be negative"),
            ('annual_maintenance', lambda x: x >= 0, "Annual maintenance cannot be negative"),
            ('property_management', lambda x: x >= 0, "Property management cost cannot be negative"),
            ('capex_reserve_rate', lambda x: 0 <= x <= 10, "CapEx reserve rate must be 0-10%"),
            ('obsolescence_risk_rate', lambda x: 0 <= x <= 5, "Obsolescence risk rate must be 0-5%"),
            ('inflation_rate', lambda x: 0 <= x <= 20, "Inflation rate must be 0-20%"),
            
            # Terminal value parameters
            ('land_value_pct', lambda x: 0 <= x <= 100, "Land value percentage must be 0-100%"),
            ('market_appreciation_rate', lambda x: -5 <= x <= 20, "Market appreciation rate must be -5% to 20%"),
            ('depreciation_period', lambda x: x >= 1, "Depreciation period must be at least 1 year"),
            
            # Tax parameters
            ('corporate_tax_rate', lambda x: 0 <= x <= 50, "Corporate tax rate must be 0-50%"),
        ]
        
        for param, validator, error_msg in validations:
            if param in calc_params:
                try:
                    if not validator(calc_params[param]):
                        errors.append(error_msg)
                except (TypeError, ValueError):
                    errors.append(f"Invalid value type for {param}")
        
        # Logical consistency checks
        if calc_params.get('down_payment_pct', 0) == 100 and calc_params.get('loan_term', 0) > 0:
            self.calculation_warnings.append("100% down payment with loan term specified - no loan will be needed")
            
        if calc_params.get('interest_rate', 0) == 0 and calc_params.get('loan_term', 0) == 0:
            errors.append("Cannot have both 0% interest rate and 0-year loan term")
        
        return len(errors) == 0, errors
    
    def run_complete_analysis(self, session_state: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute complete NPV analysis pipeline from session state to results
        
        Args:
            session_state: Streamlit session state (uses st.session_state if None)
            
        Returns:
            Complete analysis results with all metadata
        """
        try:
            # Step 1: Extract inputs from session state
            raw_inputs = self.extract_inputs_from_session(session_state)
            
            # Step 2: Transform inputs for calculations
            calc_params = self.transform_inputs_for_calculations(raw_inputs)
            
            # Step 3: Validate calculation parameters
            is_valid, param_errors = self.validate_calculation_inputs(calc_params)
            self.validation_errors.extend(param_errors)
            
            if not is_valid:
                return {
                    'calculation_successful': False,
                    'error_message': f"Input validation failed: {param_errors}",
                    'recommendation': 'ERROR',
                    'validation_errors': self.validation_errors,
                    'raw_inputs': raw_inputs,
                    'calc_params': calc_params
                }
            
            # Step 4: Execute NPV analysis
            results = self.execute_npv_analysis(calc_params)
            
            # Step 5: Add raw inputs for reference
            results['raw_inputs'] = raw_inputs
            
            return results
            
        except Exception as e:
            error_msg = f"Complete analysis pipeline failed: {str(e)}"
            logger.error(error_msg)
            
            return {
                'calculation_successful': False,
                'error_message': error_msg,
                'recommendation': 'ERROR',
                'validation_errors': self.validation_errors
            }
    
    def get_calculation_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate executive summary of calculation results
        
        Args:
            results: NPV analysis results
            
        Returns:
            Executive summary with key metrics
        """
        if not results.get('calculation_successful', False):
            return {
                'status': 'Failed',
                'error': results.get('error_message', 'Unknown error'),
                'recommendation': 'Cannot determine'
            }
        
        # Extract key metrics
        npv_diff = results.get('npv_difference', 0)
        recommendation = results.get('recommendation', 'UNKNOWN')
        confidence = results.get('confidence', 'Low')
        
        # Get currency from raw inputs
        currency = results.get('raw_inputs', {}).get('currency', 'USD')
        
        # Format monetary values
        ownership_npv = results.get('ownership_npv', 0)
        rental_npv = results.get('rental_npv', 0)
        initial_investment = results.get('ownership_initial_investment', 0)
        
        summary = {
            'status': 'Success',
            'recommendation': recommendation,
            'confidence': confidence,
            'npv_advantage': format_currency(npv_diff, currency, include_cents=False),
            'ownership_npv': format_currency(ownership_npv, currency, include_cents=False),
            'rental_npv': format_currency(rental_npv, currency, include_cents=False),
            'initial_investment': format_currency(initial_investment, currency, include_cents=False),
            'analysis_period': results.get('analysis_period', 25),
            'cost_of_capital': format_percentage(results.get('cost_of_capital', 8)),
            'calculation_time': results.get('calculation_timestamp', 'Unknown')
        }
        
        # Add recommendation explanation
        if npv_diff > 500000:
            summary['explanation'] = f"Strong financial advantage for ownership ({summary['npv_advantage']} NPV benefit)"
        elif npv_diff > 0:
            summary['explanation'] = f"Moderate advantage for ownership ({summary['npv_advantage']} NPV benefit)"  
        elif npv_diff > -500000:
            summary['explanation'] = f"Marginal difference ({summary['npv_advantage']} NPV difference)"
        else:
            summary['explanation'] = f"Clear advantage for rental (avoid {format_currency(abs(npv_diff), currency, include_cents=False)} NPV loss)"
        
        return summary
    
    def clear_validation_errors(self):
        """Clear validation errors and warnings"""
        self.validation_errors = []
        self.calculation_warnings = []
    
    def get_validation_status(self) -> Dict[str, Any]:
        """
        Get current validation status
        
        Returns:
            Validation status summary
        """
        return {
            'has_errors': len(self.validation_errors) > 0,
            'has_warnings': len(self.calculation_warnings) > 0,
            'error_count': len(self.validation_errors),
            'warning_count': len(self.calculation_warnings),
            'errors': self.validation_errors.copy(),
            'warnings': self.calculation_warnings.copy(),
            'last_calculation': self.last_calculation_time.isoformat() if self.last_calculation_time else None
        }


# Global integration engine instance
@st.cache_resource  
def get_npv_integration_engine():
    """Get singleton NPV integration engine instance"""
    return NPVIntegrationEngine()


def run_npv_analysis_from_session() -> Dict[str, Any]:
    """
    Convenience function to run NPV analysis from current session state
    
    Returns:
        Complete NPV analysis results
    """
    engine = get_npv_integration_engine()
    return engine.run_complete_analysis()


def get_analysis_readiness() -> Dict[str, Any]:
    """
    Check if session state has sufficient inputs for analysis
    
    Returns:
        Readiness status and missing requirements
    """
    engine = get_npv_integration_engine()
    
    # Extract current inputs
    inputs = engine.extract_inputs_from_session()
    
    # Check critical fields
    critical_fields = [
        'purchase_price', 'current_annual_rent', 'ownership_property_size',
        'rental_property_size', 'current_space_needed', 'analysis_period', 'cost_of_capital'
    ]
    
    missing_fields = []
    for field in critical_fields:
        if not inputs.get(field) or inputs.get(field) <= 0:
            missing_fields.append(field)
    
    is_ready = len(missing_fields) == 0 and len(engine.validation_errors) == 0
    
    return {
        'ready_for_analysis': is_ready,
        'missing_fields': missing_fields,
        'validation_errors': engine.validation_errors.copy(),
        'completion_percentage': max(0, (len(critical_fields) - len(missing_fields)) / len(critical_fields) * 100)
    }


if __name__ == "__main__":
    # Test the integration engine
    print("Testing NPV Integration Engine...")
    
    # Create test session data
    test_session = {
        'purchase_price': 500000,
        'current_annual_rent': 120000,
        'ownership_property_size': 5000,
        'rental_property_size': 4500,
        'current_space_needed': 4000,
        'analysis_period': 25,
        'cost_of_capital': 8.0,
        'down_payment_percent': 30.0,
        'interest_rate': 5.0,
        'loan_term': 20,
        'currency': 'USD'
    }
    
    # Test integration
    engine = NPVIntegrationEngine()
    results = engine.run_complete_analysis(test_session)
    
    if results.get('calculation_successful'):
        print("✅ Integration test PASSED")
        print(f"Recommendation: {results.get('recommendation')}")
        print(f"NPV Difference: ${results.get('npv_difference', 0):,.2f}")
        
        summary = engine.get_calculation_summary(results)
        print(f"Summary: {summary.get('explanation')}")
    else:
        print("❌ Integration test FAILED")
        print(f"Error: {results.get('error_message')}")