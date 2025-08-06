"""
Financial Calculations Engine
All corrected mathematical formulas for hold-forever investment analysis

Based on the validated Business PRD with proper edge case handling
and mathematically sound formulas.

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

def calculate_mortgage_payment(
    loan_amount: float,
    interest_rate: float,
    loan_term: int,
    down_payment_pct: float
) -> float:
    """
    Calculate annual mortgage payment with edge case handling
    
    Args:
        loan_amount: Total loan amount
        interest_rate: Annual interest rate (as percentage)
        loan_term: Loan term in years
        down_payment_pct: Down payment percentage
    
    Returns:
        Annual mortgage payment
    """
    # Edge case: 100% down payment
    if down_payment_pct >= 100:
        return 0.0
    
    # Edge case: 0% interest rate
    if interest_rate == 0:
        return loan_amount / loan_term
    
    # Standard PMT calculation
    monthly_rate = interest_rate / 100 / 12
    num_payments = loan_term * 12
    monthly_payment = np.pmt(monthly_rate, num_payments, -loan_amount)
    
    return monthly_payment * 12

def calculate_annual_ownership_costs(
    purchase_price: float,
    property_tax_rate: float,
    property_tax_escalation: float,
    insurance_cost: float,
    annual_maintenance: float,
    property_management: float,
    capex_reserve: float,
    obsolescence_risk: float,
    inflation_rate: float,
    year: int
) -> Dict[str, float]:
    """
    Calculate annual ownership costs with proper Year-1 indexing
    
    Returns:
        Dictionary of cost components
    """
    # Year-1 indexing: Year 1 uses base costs, escalation begins Year 2
    escalation_factor = (1 + inflation_rate/100) ** (year - 1)
    tax_escalation_factor = (1 + property_tax_escalation/100) ** (year - 1)
    
    costs = {
        'property_taxes': purchase_price * property_tax_rate/100 * tax_escalation_factor,
        'insurance': insurance_cost * escalation_factor,
        'maintenance': annual_maintenance * escalation_factor,
        'property_management': property_management * escalation_factor,
        'capex_reserve': purchase_price * capex_reserve/100 * escalation_factor,
        'obsolescence_cost': purchase_price * obsolescence_risk/100 * escalation_factor,
    }
    
    return costs

def calculate_terminal_value(
    purchase_price: float,
    land_value_pct: float,
    market_appreciation_rate: float,
    depreciation_period: int,
    analysis_period: int,
    remaining_loan_balance: float
) -> Dict[str, float]:
    """
    Calculate terminal value for hold-forever strategy
    
    Returns:
        Dictionary with terminal value components
    """
    land_value = purchase_price * land_value_pct / 100
    building_value = purchase_price - land_value
    
    # Land appreciates, building depreciates then appreciates
    land_value_end = land_value * (1 + market_appreciation_rate/100) ** analysis_period
    
    # Calculate building depreciation
    accumulated_depreciation = min(building_value, building_value * analysis_period / depreciation_period)
    depreciated_building = building_value - accumulated_depreciation
    building_value_end = depreciated_building * (1 + market_appreciation_rate/100) ** analysis_period
    
    terminal_property_value = land_value_end + building_value_end
    net_property_equity = terminal_property_value - remaining_loan_balance
    
    return {
        'land_value_end': land_value_end,
        'building_value_end': building_value_end,
        'terminal_property_value': terminal_property_value,
        'net_property_equity': net_property_equity
    }

# Placeholder for additional calculation functions
# Full implementation will include:
# - calculate_amortization_schedule()
# - calculate_npv_analysis()
# - calculate_sensitivity_analysis()
# - calculate_operational_breakeven()
# - etc.

# TODO: Implement remaining calculation functions based on Technical PRD