"""
Financial Calculations Engine - Main Module
Complete mathematical formulas for hold-forever investment analysis

This module serves as the main entry point for all financial calculations,
importing and exposing all functions from the modular calculation system.

Based on the validated Business PRD with proper edge case handling
and mathematically sound formulas.

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

# Import all calculation modules
from .calculations import *

# Backward compatibility - expose key functions at module level
# These are the most commonly used functions from the original implementation

def calculate_mortgage_payment_legacy(
    loan_amount: float,
    interest_rate: float,
    loan_term: int,
    down_payment_pct: float
) -> float:
    """
    Legacy mortgage payment calculation function (backward compatibility)
    
    DEPRECATED: Use calculations.mortgage.calculate_mortgage_payment() instead
    
    Args:
        loan_amount: Total loan amount
        interest_rate: Annual interest rate (as percentage)
        loan_term: Loan term in years
        down_payment_pct: Down payment percentage
    
    Returns:
        Annual mortgage payment
    """
    import warnings
    warnings.warn(
        "calculate_mortgage_payment_legacy is deprecated. Use calculations.mortgage.calculate_mortgage_payment() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    from .calculations.mortgage import calculate_mortgage_payment
    
    # Convert parameters to match new function signature
    purchase_price = loan_amount / (1 - down_payment_pct/100)
    
    result = calculate_mortgage_payment(
        purchase_price=purchase_price,
        down_payment_pct=down_payment_pct,
        interest_rate=interest_rate,
        loan_term=loan_term
    )
    
    return result['annual_payment']


# Export all calculation functions at module level for easy access
__all__ = [
    # Main analysis functions
    'calculate_npv_comparison',
    'calculate_ownership_cash_flows',
    'calculate_rental_cash_flows',
    'calculate_break_even_analysis',
    'calculate_sensitivity_analysis',
    
    # Mortgage calculations
    'calculate_mortgage_payment',
    'calculate_loan_amount',
    'validate_mortgage_inputs',
    
    # Annual cost calculations
    'calculate_annual_ownership_costs',
    'calculate_annual_rental_costs',
    'calculate_cost_escalation',
    'calculate_property_upgrade_costs',
    'calculate_tax_benefits',
    'calculate_subletting_income',
    
    # Terminal value analysis
    'calculate_terminal_value',
    'calculate_property_appreciation',
    'calculate_depreciation_schedule',
    'calculate_rental_terminal_value',
    'calculate_wealth_comparison',
    
    # Amortization schedules
    'generate_amortization_schedule',
    'calculate_remaining_balance',
    'calculate_payment_breakdown',
    'calculate_total_interest_paid',
    
    # Utility functions
    'calculate_present_value',
    'calculate_cash_flow_analysis',
    
    # Legacy functions (deprecated)
    'calculate_mortgage_payment_legacy'
]


def get_calculation_summary():
    """
    Get summary of available calculation functions
    
    Returns:
        Dictionary with categorized function lists and descriptions
    """
    return {
        'mortgage_functions': [
            'calculate_mortgage_payment - Complete mortgage payment calculation with edge cases',
            'calculate_loan_amount - Calculate loan amount from purchase details',
            'validate_mortgage_inputs - Input validation for mortgage calculations'
        ],
        'annual_cost_functions': [
            'calculate_annual_ownership_costs - All ownership costs with Year-1 indexing',
            'calculate_annual_rental_costs - Rental costs with escalation',
            'calculate_cost_escalation - Cost escalation with Year-1 indexing pattern',
            'calculate_tax_benefits - Tax savings from ownership',
            'calculate_subletting_income - Income from excess space subletting'
        ],
        'terminal_value_functions': [
            'calculate_terminal_value - Hold-forever wealth analysis',
            'calculate_property_appreciation - Property value appreciation over time',
            'calculate_depreciation_schedule - Building depreciation calculations',
            'calculate_rental_terminal_value - Terminal value for rental scenario',
            'calculate_wealth_comparison - Compare wealth accumulation strategies'
        ],
        'amortization_functions': [
            'generate_amortization_schedule - Complete year-by-year schedule',
            'calculate_remaining_balance - Loan balance for specific year',
            'calculate_payment_breakdown - Interest/principal breakdown',
            'calculate_total_interest_paid - Total interest over loan term'
        ],
        'analysis_functions': [
            'calculate_npv_comparison - Complete NPV analysis and recommendation',
            'calculate_ownership_cash_flows - Year-by-year ownership cash flows',
            'calculate_rental_cash_flows - Year-by-year rental cash flows',
            'calculate_break_even_analysis - Operational break-even analysis',
            'calculate_sensitivity_analysis - Parameter sensitivity testing'
        ],
        'utility_functions': [
            'calculate_present_value - Present value of future cash flows',
            'calculate_cash_flow_analysis - Detailed cash flow metrics'
        ]
    }


def run_calculation_tests():
    """
    Run basic calculation tests to verify mathematical accuracy
    
    Returns:
        Dictionary with test results for each module
    """
    test_results = {
        'mortgage_tests': None,
        'annual_costs_tests': None,
        'terminal_value_tests': None,
        'amortization_tests': None,
        'npv_analysis_tests': None
    }
    
    try:
        from .calculations.mortgage import _test_mortgage_calculations
        test_results['mortgage_tests'] = _test_mortgage_calculations()
    except Exception as e:
        test_results['mortgage_tests'] = {'error': str(e)}
    
    try:
        from .calculations.annual_costs import _test_annual_cost_calculations
        test_results['annual_costs_tests'] = _test_annual_cost_calculations()
    except Exception as e:
        test_results['annual_costs_tests'] = {'error': str(e)}
    
    try:
        from .calculations.terminal_value import _test_terminal_value_calculations
        test_results['terminal_value_tests'] = _test_terminal_value_calculations()
    except Exception as e:
        test_results['terminal_value_tests'] = {'error': str(e)}
    
    try:
        from .calculations.amortization import _test_amortization_calculations
        test_results['amortization_tests'] = _test_amortization_calculations()
    except Exception as e:
        test_results['amortization_tests'] = {'error': str(e)}
    
    try:
        from .calculations.npv_analysis import _test_npv_calculations
        test_results['npv_analysis_tests'] = _test_npv_calculations()
    except Exception as e:
        test_results['npv_analysis_tests'] = {'error': str(e)}
    
    return test_results


# Version information
__version__ = "1.0.0"
__author__ = "Real Estate Decision Tool Team"
__description__ = "Complete financial calculation engine for rent vs. buy analysis"