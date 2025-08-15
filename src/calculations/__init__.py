"""
Financial Calculations Engine
Core mathematical functions for rent vs. buy analysis

This module provides comprehensive financial analysis functions for real estate
investment decisions, with focus on hold-forever ownership strategies.

Modules:
    - mortgage: Mortgage payment calculations with edge case handling
    - annual_costs: Annual operating cost calculations with Year-1 indexing
    - terminal_value: Hold-forever wealth analysis
    - amortization: Loan amortization schedule tracking
    - npv_analysis: Net present value analysis and cash flow integration

All calculations follow the Business PRD specifications with proper
edge case handling and mathematical accuracy.

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

from .mortgage import (
    calculate_mortgage_payment,
    calculate_loan_amount,
    validate_mortgage_inputs
)

from .annual_costs import (
    calculate_annual_ownership_costs,
    calculate_annual_rental_costs,
    calculate_cost_escalation,
    calculate_subletting_income
)

from .terminal_value import (
    calculate_terminal_value,
    calculate_property_appreciation,
    calculate_depreciation_schedule
)

from .amortization import (
    generate_amortization_schedule,
    calculate_remaining_balance,
    calculate_payment_breakdown
)

from .npv_analysis import (
    calculate_npv_comparison,
    calculate_cash_flow_analysis,
    calculate_break_even_analysis,
    calculate_ownership_cash_flows,
    calculate_rental_cash_flows
)

from .two_dimensional_sensitivity import (
    calculate_sensitivity_analysis,  # Backward compatibility function
    calculate_2d_sensitivity_analysis,
    format_2d_sensitivity_for_streamlit,
    get_available_sensitivity_metrics
)

__version__ = "1.0.0"
__all__ = [
    # Mortgage calculations
    'calculate_mortgage_payment',
    'calculate_loan_amount', 
    'validate_mortgage_inputs',
    
    # Annual cost calculations
    'calculate_annual_ownership_costs',
    'calculate_annual_rental_costs',
    'calculate_cost_escalation',
    'calculate_subletting_income',
    
    # Terminal value analysis
    'calculate_terminal_value',
    'calculate_property_appreciation',
    'calculate_depreciation_schedule',
    
    # Amortization schedules
    'generate_amortization_schedule',
    'calculate_remaining_balance',
    'calculate_payment_breakdown',
    
    # NPV and cash flow analysis
    'calculate_npv_comparison',
    'calculate_cash_flow_analysis',
    'calculate_break_even_analysis',
    'calculate_ownership_cash_flows',
    'calculate_rental_cash_flows',
    'calculate_sensitivity_analysis',
    
    # New 2D sensitivity analysis
    'calculate_2d_sensitivity_analysis',
    'format_2d_sensitivity_for_streamlit',
    'get_available_sensitivity_metrics'
]