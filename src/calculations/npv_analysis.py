"""
NPV Analysis and Cash Flow Integration
Complete financial analysis integrating all calculation modules

This module provides comprehensive NPV analysis by integrating:
- Mortgage payments and amortization schedules
- Annual ownership and rental costs
- Terminal value calculations
- Present value analysis with cost of capital
- Break-even analysis and sensitivity testing

All formulas follow the Business PRD specifications exactly.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

from .mortgage import calculate_mortgage_payment, calculate_loan_amount
from .annual_costs import calculate_annual_ownership_costs, calculate_annual_rental_costs
from .terminal_value import calculate_terminal_value, calculate_rental_terminal_value
from .amortization import calculate_remaining_balance, calculate_payment_breakdown

logger = logging.getLogger(__name__)


def calculate_present_value(
    cash_flow: float,
    discount_rate: float,
    year: int
) -> float:
    """
    Calculate present value of a future cash flow
    
    Args:
        cash_flow: Future cash flow amount
        discount_rate: Annual discount rate (percentage)
        year: Year when cash flow occurs
    
    Returns:
        Present value of the cash flow
        
    Example:
        >>> calculate_present_value(1000, 8.0, 5)
        680.58
    """
    if year <= 0:
        return cash_flow
    
    if discount_rate == 0:
        return cash_flow
    
    discount_factor = (1 + discount_rate / 100) ** year
    return cash_flow / discount_factor


def calculate_ownership_cash_flows(
    purchase_price: float,
    down_payment_pct: float,
    interest_rate: float,
    loan_term: int,
    analysis_period: int,
    # Property cost parameters
    property_tax_rate: float,
    property_tax_escalation: float,
    insurance_cost: float,
    annual_maintenance: float,
    property_management: float = 0.0,
    capex_reserve_rate: float = 1.5,
    obsolescence_risk_rate: float = 0.5,
    inflation_rate: float = 3.0,
    # Terminal value parameters
    land_value_pct: float = 25.0,
    market_appreciation_rate: float = 3.0,
    depreciation_period: int = 39,
    # Tax parameters
    corporate_tax_rate: float = 25.0,
    interest_deductible: bool = True,
    property_tax_deductible: bool = True,
    transaction_costs: float = 0.0
) -> List[Dict[str, float]]:
    """
    Calculate year-by-year cash flows for ownership scenario
    
    Args:
        All parameters needed for ownership cost calculation
    
    Returns:
        List of annual cash flow dictionaries containing:
        - year: Year number
        - mortgage_payment: Annual mortgage payment
        - property_taxes: Property taxes for the year
        - insurance: Insurance cost
        - maintenance: Maintenance cost
        - property_management: Property management fees
        - capex_reserve: CapEx reserve amount
        - obsolescence_cost: Obsolescence risk cost
        - tax_benefits: Tax savings from deductions
        - net_cash_flow: Total annual cash flow (negative = cost)
        - remaining_loan_balance: Outstanding loan balance
        
    Example:
        >>> flows = calculate_ownership_cash_flows(500000, 30, 5.0, 20, 25, ...)
        >>> len(flows)
        25
        >>> flows[0]['net_cash_flow']  # Year 1 net cost
        -45000.0
    """
    # Calculate mortgage details
    mortgage_info = calculate_mortgage_payment(
        purchase_price, down_payment_pct, interest_rate, loan_term, transaction_costs
    )
    
    annual_mortgage_payment = mortgage_info['annual_payment']
    loan_amount = mortgage_info['loan_amount']
    
    # Calculate building value for depreciation
    building_value = purchase_price * (1 - land_value_pct / 100)
    annual_depreciation = building_value / depreciation_period if depreciation_period > 0 else 0
    
    cash_flows = []
    
    for year in range(1, analysis_period + 1):
        # Calculate annual ownership costs
        ownership_costs = calculate_annual_ownership_costs(
            purchase_price,
            property_tax_rate,
            property_tax_escalation,
            insurance_cost,
            annual_maintenance,
            property_management,
            capex_reserve_rate,
            obsolescence_risk_rate,
            inflation_rate,
            year
        )
        
        # Calculate mortgage payment breakdown
        if loan_amount > 0 and year <= loan_term:
            payment_breakdown = calculate_payment_breakdown(
                loan_amount, annual_mortgage_payment, interest_rate, year
            )
            mortgage_interest = payment_breakdown['interest_portion']
            remaining_loan_balance = payment_breakdown['ending_balance']
        else:
            mortgage_interest = 0.0
            remaining_loan_balance = 0.0
        
        # Calculate tax benefits
        interest_deduction = mortgage_interest if interest_deductible else 0.0
        property_tax_deduction = ownership_costs['property_taxes'] if property_tax_deductible else 0.0
        depreciation_deduction = annual_depreciation
        
        total_deductions = interest_deduction + property_tax_deduction + depreciation_deduction
        tax_benefits = total_deductions * corporate_tax_rate / 100
        
        # Calculate net cash flow
        total_costs = (
            annual_mortgage_payment +
            ownership_costs['total_annual_cost']
        )
        
        net_cash_flow = -(total_costs - tax_benefits)  # Negative = outflow
        
        cash_flows.append({
            'year': year,
            'mortgage_payment': float(annual_mortgage_payment),
            'property_taxes': float(ownership_costs['property_taxes']),
            'insurance': float(ownership_costs['insurance']),
            'maintenance': float(ownership_costs['maintenance']),
            'property_management': float(ownership_costs['property_management']),
            'capex_reserve': float(ownership_costs['capex_reserve']),
            'obsolescence_cost': float(ownership_costs['obsolescence_cost']),
            'mortgage_interest': float(mortgage_interest),
            'tax_benefits': float(tax_benefits),
            'total_costs': float(total_costs),
            'net_cash_flow': float(net_cash_flow),
            'remaining_loan_balance': float(remaining_loan_balance)
        })
    
    return cash_flows


def calculate_rental_cash_flows(
    current_annual_rent: float,
    rent_increase_rate: float,
    analysis_period: int,
    corporate_tax_rate: float = 25.0,
    rent_deductible: bool = True
) -> List[Dict[str, float]]:
    """
    Calculate year-by-year cash flows for rental scenario
    
    Args:
        current_annual_rent: Current annual rent cost
        rent_increase_rate: Annual rent escalation rate (percentage)
        analysis_period: Analysis time horizon
        corporate_tax_rate: Corporate tax rate (percentage)
        rent_deductible: Is rent expense tax deductible
    
    Returns:
        List of annual cash flow dictionaries
    """
    cash_flows = []
    
    for year in range(1, analysis_period + 1):
        # Calculate annual rent with escalation
        rental_costs = calculate_annual_rental_costs(
            current_annual_rent, rent_increase_rate, year
        )
        
        annual_rent = rental_costs['annual_rent']
        
        # Calculate tax benefits
        tax_benefits = annual_rent * corporate_tax_rate / 100 if rent_deductible else 0.0
        
        # Net cash flow (negative = outflow)
        net_cash_flow = -(annual_rent - tax_benefits)
        
        cash_flows.append({
            'year': year,
            'annual_rent': float(annual_rent),
            'tax_benefits': float(tax_benefits),
            'net_cash_flow': float(net_cash_flow)
        })
    
    return cash_flows


def calculate_npv_comparison(
    # Purchase scenario parameters
    purchase_price: float,
    down_payment_pct: float,
    interest_rate: float,
    loan_term: int,
    transaction_costs: float,
    # Rental scenario parameters
    current_annual_rent: float,
    rent_increase_rate: float,
    # Common parameters
    analysis_period: int,
    cost_of_capital: float,
    # Property cost parameters
    property_tax_rate: float = 1.2,
    property_tax_escalation: float = 2.0,
    insurance_cost: float = 5000,
    annual_maintenance: float = 10000,
    property_management: float = 0.0,
    capex_reserve_rate: float = 1.5,
    obsolescence_risk_rate: float = 0.5,
    inflation_rate: float = 3.0,
    # Terminal value parameters
    land_value_pct: float = 25.0,
    market_appreciation_rate: float = 3.0,
    depreciation_period: int = 39,
    # Tax parameters
    corporate_tax_rate: float = 25.0,
    interest_deductible: bool = True,
    property_tax_deductible: bool = True,
    rent_deductible: bool = True,
    # Initial costs
    security_deposit: float = 0.0,
    rental_commission: float = 0.0,
    moving_costs: float = 0.0,
    space_improvement_cost: float = 0.0
) -> Dict[str, float]:
    """
    Calculate complete NPV comparison between ownership and rental
    
    This is the main analysis function that integrates all calculations
    and provides the final recommendation.
    
    Returns:
        Dictionary with comprehensive NPV analysis:
        - ownership_npv: Net present value of ownership scenario
        - rental_npv: Net present value of rental scenario
        - npv_difference: NPV advantage (positive = ownership better)
        - ownership_initial_investment: Initial cash required for purchase
        - rental_initial_investment: Initial cash required for rental
        - terminal_value_advantage: Terminal value difference
        - recommendation: "BUY", "RENT", or "MARGINAL"
        - confidence: "High", "Medium", "Low"
    """
    # Calculate initial investments
    mortgage_info = calculate_mortgage_payment(
        purchase_price, down_payment_pct, interest_rate, loan_term, transaction_costs, space_improvement_cost
    )
    ownership_initial_investment = mortgage_info['total_initial_investment']
    rental_initial_investment = security_deposit + rental_commission + moving_costs
    
    # Calculate ownership cash flows
    ownership_flows = calculate_ownership_cash_flows(
        purchase_price, down_payment_pct, interest_rate, loan_term, analysis_period,
        property_tax_rate, property_tax_escalation, insurance_cost, annual_maintenance,
        property_management, capex_reserve_rate, obsolescence_risk_rate, inflation_rate,
        land_value_pct, market_appreciation_rate, depreciation_period,
        corporate_tax_rate, interest_deductible, property_tax_deductible, transaction_costs
    )
    
    # Calculate rental cash flows
    rental_flows = calculate_rental_cash_flows(
        current_annual_rent, rent_increase_rate, analysis_period,
        corporate_tax_rate, rent_deductible
    )
    
    # Calculate terminal values
    final_loan_balance = ownership_flows[-1]['remaining_loan_balance']
    ownership_terminal = calculate_terminal_value(
        purchase_price, land_value_pct, market_appreciation_rate,
        depreciation_period, analysis_period, final_loan_balance
    )
    
    rental_terminal = calculate_rental_terminal_value(
        security_deposit, inflation_rate, analysis_period
    )
    
    # Calculate NPVs
    ownership_pv_flows = []
    rental_pv_flows = []
    
    for year in range(analysis_period):
        # Present value of annual cash flows
        ownership_pv = calculate_present_value(
            ownership_flows[year]['net_cash_flow'], cost_of_capital, year + 1
        )
        rental_pv = calculate_present_value(
            rental_flows[year]['net_cash_flow'], cost_of_capital, year + 1
        )
        
        ownership_pv_flows.append(ownership_pv)
        rental_pv_flows.append(rental_pv)
    
    # Present value of terminal values (with safe dictionary access)
    net_property_equity = ownership_terminal.get('net_property_equity', 0.0)
    if net_property_equity == 0.0:
        logger.warning("Terminal value missing net_property_equity field, using 0.0")
    
    ownership_terminal_pv = calculate_present_value(
        net_property_equity, cost_of_capital, analysis_period
    )
    security_deposit_recovery = rental_terminal.get('security_deposit_recovery', 0.0)
    if security_deposit_recovery == 0.0:
        logger.warning("Terminal value missing security_deposit_recovery field, using 0.0")
    
    rental_terminal_pv = calculate_present_value(
        security_deposit_recovery, cost_of_capital, analysis_period
    )
    
    # Calculate total NPVs (including initial investments and terminal values)
    ownership_npv = -ownership_initial_investment + sum(ownership_pv_flows) + ownership_terminal_pv
    rental_npv = -rental_initial_investment + sum(rental_pv_flows) + rental_terminal_pv
    
    # NPV difference (positive = ownership better)
    npv_difference = ownership_npv - rental_npv
    terminal_value_advantage = ownership_terminal_pv - rental_terminal_pv
    
    # Generate recommendation
    if npv_difference > 1000000:
        recommendation = "BUY"
        confidence = "High"
    elif npv_difference > 500000:
        recommendation = "BUY"
        confidence = "Medium"
    elif npv_difference > -500000:
        recommendation = "MARGINAL"
        confidence = "Low"
    elif npv_difference > -1000000:
        recommendation = "RENT"
        confidence = "Medium"
    else:
        recommendation = "RENT"
        confidence = "High"
    
    return {
        'ownership_npv': float(ownership_npv),
        'rental_npv': float(rental_npv),
        'npv_difference': float(npv_difference),
        'ownership_initial_investment': float(ownership_initial_investment),
        'rental_initial_investment': float(rental_initial_investment),
        'terminal_value_advantage': float(terminal_value_advantage),
        'ownership_terminal_value': float(ownership_terminal_pv),
        'rental_terminal_value': float(rental_terminal_pv),
        'recommendation': recommendation,
        'confidence': confidence,
        'analysis_period': analysis_period,
        'cost_of_capital': cost_of_capital
    }


def calculate_break_even_analysis(
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]]
) -> Dict[str, float]:
    """
    Calculate operational break-even analysis
    
    Args:
        ownership_flows: List of ownership cash flows
        rental_flows: List of rental cash flows
    
    Returns:
        Dictionary with break-even metrics
    """
    cumulative_ownership = 0.0
    cumulative_rental = 0.0
    break_even_year = None
    
    yearly_differences = []
    
    for year in range(len(ownership_flows)):
        annual_ownership = abs(ownership_flows[year]['net_cash_flow'])
        annual_rental = abs(rental_flows[year]['net_cash_flow'])
        
        cumulative_ownership += annual_ownership
        cumulative_rental += annual_rental
        
        annual_difference = annual_ownership - annual_rental
        yearly_differences.append(annual_difference)
        
        # Check for break-even (when ownership becomes cheaper annually)
        if break_even_year is None and annual_ownership < annual_rental:
            break_even_year = year + 1
    
    return {
        'break_even_year': break_even_year,
        'cumulative_cost_difference': cumulative_ownership - cumulative_rental,
        'average_annual_difference': sum(yearly_differences) / len(yearly_differences) if yearly_differences else 0.0,
        'yearly_differences': yearly_differences
    }


def calculate_sensitivity_analysis(
    base_params: Dict,
    sensitivity_params: Dict[str, List[float]]
) -> Dict[str, Dict[str, float]]:
    """
    Perform sensitivity analysis on key parameters
    
    Args:
        base_params: Base case parameters for NPV calculation
        sensitivity_params: Dictionary of parameter names and test values
    
    Returns:
        Dictionary of sensitivity results
    """
    results = {}
    
    for param_name, test_values in sensitivity_params.items():
        param_results = {}
        
        for test_value in test_values:
            # Create modified parameters
            modified_params = base_params.copy()
            modified_params[param_name] = test_value
            
            try:
                # Calculate NPV with modified parameter
                npv_result = calculate_npv_comparison(**modified_params)
                param_results[f"{param_name}_{test_value}"] = {
                    'npv_difference': npv_result['npv_difference'],
                    'recommendation': npv_result['recommendation']
                }
            except Exception as e:
                logger.error(f"Sensitivity analysis failed for {param_name}={test_value}: {e}")
                param_results[f"{param_name}_{test_value}"] = {
                    'npv_difference': 0.0,
                    'recommendation': 'ERROR'
                }
        
        results[param_name] = param_results
    
    return results


def calculate_cash_flow_analysis(
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]],
    cost_of_capital: float
) -> Dict[str, List[float]]:
    """
    Calculate detailed cash flow analysis metrics
    
    Args:
        ownership_flows: Ownership cash flow data
        rental_flows: Rental cash flow data
        cost_of_capital: Discount rate for present value calculations
    
    Returns:
        Dictionary with detailed cash flow metrics by year
    """
    years = []
    annual_differences = []
    cumulative_differences = []
    present_value_differences = []
    
    cumulative_diff = 0.0
    
    for year in range(len(ownership_flows)):
        year_num = year + 1
        years.append(year_num)
        
        # Calculate annual difference (negative = ownership costs more)
        ownership_cost = abs(ownership_flows[year]['net_cash_flow'])
        rental_cost = abs(rental_flows[year]['net_cash_flow'])
        annual_diff = ownership_cost - rental_cost
        
        annual_differences.append(annual_diff)
        
        # Update cumulative difference
        cumulative_diff += annual_diff
        cumulative_differences.append(cumulative_diff)
        
        # Calculate present value of annual difference
        pv_diff = calculate_present_value(annual_diff, cost_of_capital, year_num)
        present_value_differences.append(pv_diff)
    
    return {
        'years': years,
        'annual_differences': annual_differences,
        'cumulative_differences': cumulative_differences,
        'present_value_differences': present_value_differences
    }


def _test_npv_calculations():
    """Internal function to test NPV calculation accuracy"""
    # Simple test case
    test_params = {
        'purchase_price': 500000,
        'down_payment_pct': 30,
        'interest_rate': 5.0,
        'loan_term': 20,
        'transaction_costs': 25000,
        'current_annual_rent': 24000,
        'rent_increase_rate': 3.0,
        'analysis_period': 25,
        'cost_of_capital': 8.0
    }
    
    try:
        result = calculate_npv_comparison(**test_params)
        
        # Basic sanity checks
        tests = [
            ('has_ownership_npv', 'ownership_npv' in result),
            ('has_rental_npv', 'rental_npv' in result),
            ('has_npv_difference', 'npv_difference' in result),
            ('has_recommendation', 'recommendation' in result and result['recommendation'] in ['BUY', 'RENT', 'MARGINAL']),
            ('npv_difference_calculation', abs((result['ownership_npv'] - result['rental_npv']) - result['npv_difference']) < 1.0)
        ]
        
        return {
            'tests': tests,
            'result': result,
            'all_passed': all(test[1] for test in tests)
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'all_passed': False
        }


if __name__ == "__main__":
    # Run basic test
    test_result = _test_npv_calculations()
    if test_result.get('all_passed', False):
        print("NPV analysis test: PASSED")
        print(f"NPV Difference: ${test_result['result']['npv_difference']:,.2f}")
        print(f"Recommendation: {test_result['result']['recommendation']}")
    else:
        print("NPV analysis test: FAILED")
        if 'error' in test_result:
            print(f"Error: {test_result['error']}")
        else:
            for test_name, passed in test_result.get('tests', []):
                if not passed:
                    print(f"Failed test: {test_name}")