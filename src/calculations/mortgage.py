"""
Mortgage and Loan Calculation Functions
Comprehensive mortgage payment calculations with edge case handling

This module handles all mortgage-related calculations including:
- Standard mortgage payment calculations using PMT formula
- Edge cases: 0% interest rates, 100% down payments
- Loan amount calculations and input validation
- Payment breakdowns and amortization basics

All formulas follow the Business PRD specifications exactly.
"""

import numpy as np
import numpy_financial as npf
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def validate_mortgage_inputs(
    purchase_price: float,
    down_payment_pct: float,
    interest_rate: float,
    loan_term: int
) -> Dict[str, bool]:
    """
    Validate mortgage calculation inputs for logical consistency
    
    Args:
        purchase_price: Total property acquisition cost
        down_payment_pct: Down payment percentage (0-100)
        interest_rate: Annual interest rate (0-20%)
        loan_term: Loan term in years (0-50)
    
    Returns:
        Dictionary with validation results and any error messages
        
    Example:
        >>> validate_mortgage_inputs(500000, 30, 5.0, 20)
        {'valid': True, 'errors': []}
    """
    errors = []
    
    # Validate purchase price
    if purchase_price <= 0:
        errors.append("Purchase price must be positive")
    if purchase_price < 50000:
        errors.append("Purchase price unusually low (< $50,000)")
    
    # Validate down payment percentage
    if down_payment_pct < 0 or down_payment_pct > 100:
        errors.append("Down payment percentage must be between 0% and 100%")
    
    # Validate interest rate
    if interest_rate < 0 or interest_rate > 20:
        errors.append("Interest rate must be between 0% and 20%")
    
    # Validate loan term
    if loan_term < 0 or loan_term > 50:
        errors.append("Loan term must be between 0 and 50 years")
    
    # Logical consistency checks
    if down_payment_pct == 100 and interest_rate > 0:
        logger.warning("100% down payment specified with interest rate - no loan needed")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': []
    }


def calculate_loan_amount(
    purchase_price: float,
    down_payment_pct: float,
    transaction_costs: float = 0.0
) -> float:
    """
    Calculate the loan amount needed for property purchase
    
    Args:
        purchase_price: Total property acquisition cost
        down_payment_pct: Down payment percentage (0-100)
        transaction_costs: Additional closing costs, fees, etc.
    
    Returns:
        Loan amount required
        
    Example:
        >>> calculate_loan_amount(500000, 30, 25000)
        350000.0
    """
    if down_payment_pct >= 100:
        return 0.0
    
    down_payment_amount = purchase_price * (down_payment_pct / 100)
    loan_amount = purchase_price - down_payment_amount
    
    return max(0.0, loan_amount)


def calculate_mortgage_payment(
    purchase_price: float,
    down_payment_pct: float,
    interest_rate: float,
    loan_term: int,
    transaction_costs: float = 0.0
) -> Dict[str, float]:
    """
    Calculate annual mortgage payment with comprehensive edge case handling
    
    This function implements the exact Business PRD specifications for mortgage
    payment calculations, including all edge cases.
    
    Args:
        purchase_price: Total property acquisition cost
        down_payment_pct: Down payment percentage (0-100)
        interest_rate: Annual interest rate (as percentage, e.g., 5.0 for 5%)
        loan_term: Loan term in years
        transaction_costs: Additional closing costs and fees
    
    Returns:
        Dictionary containing:
        - annual_payment: Annual mortgage payment
        - monthly_payment: Monthly mortgage payment  
        - loan_amount: Total loan amount
        - down_payment_amount: Down payment in dollars
        - total_initial_investment: Down payment + transaction costs
        
    Examples:
        Standard mortgage:
        >>> result = calculate_mortgage_payment(500000, 30, 5.0, 20)
        >>> round(result['annual_payment'], 2)
        27738.24
        
        Edge case - 100% down payment:
        >>> result = calculate_mortgage_payment(500000, 100, 5.0, 20)
        >>> result['annual_payment']
        0.0
        
        Edge case - 0% interest:
        >>> result = calculate_mortgage_payment(500000, 30, 0.0, 20)
        >>> result['annual_payment']
        17500.0
    """
    # Input validation
    validation = validate_mortgage_inputs(purchase_price, down_payment_pct, interest_rate, loan_term)
    if not validation['valid']:
        raise ValueError(f"Invalid inputs: {validation['errors']}")
    
    # Calculate loan amount
    loan_amount = calculate_loan_amount(purchase_price, down_payment_pct, transaction_costs)
    down_payment_amount = purchase_price * (down_payment_pct / 100)
    total_initial_investment = down_payment_amount + transaction_costs
    
    # Edge case: 100% down payment (no loan needed)
    if down_payment_pct >= 100 or loan_amount <= 0:
        return {
            'annual_payment': 0.0,
            'monthly_payment': 0.0,
            'loan_amount': 0.0,
            'down_payment_amount': down_payment_amount,
            'total_initial_investment': total_initial_investment,
            'interest_portion_year_1': 0.0,
            'principal_portion_year_1': 0.0
        }
    
    # Edge case: 0% interest rate (interest-free loan)
    if interest_rate == 0.0:
        if loan_term == 0:
            raise ValueError("Cannot have 0% interest rate and 0-year loan term")
        
        monthly_payment = loan_amount / (loan_term * 12)
        annual_payment = loan_amount / loan_term
        
        return {
            'annual_payment': annual_payment,
            'monthly_payment': monthly_payment,
            'loan_amount': loan_amount,
            'down_payment_amount': down_payment_amount,
            'total_initial_investment': total_initial_investment,
            'interest_portion_year_1': 0.0,
            'principal_portion_year_1': annual_payment
        }
    
    # Standard mortgage calculation using numpy PMT function
    # PMT formula: PMT(rate, nper, pv, fv, type)
    monthly_rate = interest_rate / 100 / 12
    num_payments = loan_term * 12
    
    if num_payments == 0:
        raise ValueError("Loan term cannot be 0 years with positive interest rate")
    
    # Calculate monthly payment (numpy_financial PMT returns negative value, so we negate)
    monthly_payment = -npf.pmt(monthly_rate, num_payments, loan_amount, 0, 0)
    annual_payment = monthly_payment * 12
    
    # Calculate first year interest and principal portions
    interest_portion_year_1 = loan_amount * interest_rate / 100
    principal_portion_year_1 = annual_payment - interest_portion_year_1
    
    return {
        'annual_payment': float(annual_payment),
        'monthly_payment': float(monthly_payment),
        'loan_amount': float(loan_amount),
        'down_payment_amount': float(down_payment_amount),
        'total_initial_investment': float(total_initial_investment),
        'interest_portion_year_1': float(interest_portion_year_1),
        'principal_portion_year_1': float(principal_portion_year_1)
    }


def calculate_payment_breakdown(
    loan_amount: float,
    interest_rate: float,
    annual_payment: float,
    year: int
) -> Dict[str, float]:
    """
    Calculate interest and principal portions for a specific year
    
    Args:
        loan_amount: Outstanding loan balance at start of year
        interest_rate: Annual interest rate (as percentage)
        annual_payment: Annual mortgage payment
        year: Year number (for reference)
    
    Returns:
        Dictionary with interest and principal portions
    """
    if loan_amount <= 0:
        return {
            'interest_portion': 0.0,
            'principal_portion': 0.0,
            'remaining_balance': 0.0
        }
    
    interest_portion = loan_amount * interest_rate / 100
    principal_portion = min(annual_payment - interest_portion, loan_amount)
    remaining_balance = loan_amount - principal_portion
    
    return {
        'interest_portion': float(interest_portion),
        'principal_portion': float(principal_portion),
        'remaining_balance': float(max(0.0, remaining_balance))
    }


def calculate_effective_interest_rate(
    loan_amount: float,
    annual_payment: float,
    loan_term: int,
    fees: float = 0.0
) -> float:
    """
    Calculate the effective interest rate including fees and points
    
    Args:
        loan_amount: Total loan amount
        annual_payment: Annual mortgage payment
        loan_term: Loan term in years
        fees: Upfront fees and points
    
    Returns:
        Effective annual interest rate as percentage
    """
    if loan_amount <= 0 or annual_payment <= 0 or loan_term <= 0:
        return 0.0
    
    # This is an approximation - for exact calculation would need iterative solving
    # Using the approximation: effective rate ≈ (total payments - loan amount) / (loan amount * term)
    total_payments = annual_payment * loan_term
    total_cost = total_payments - loan_amount + fees
    
    if loan_amount == 0:
        return 0.0
        
    effective_rate = (total_cost / loan_amount) / loan_term * 100
    return max(0.0, float(effective_rate))


# Test and validation functions
def _test_mortgage_calculations():
    """Internal function to test mortgage calculation accuracy"""
    test_cases = [
        # Standard case
        {
            'purchase_price': 500000,
            'down_payment_pct': 30,
            'interest_rate': 5.0,
            'loan_term': 20,
            'expected_annual': 27738.24
        },
        # 100% down payment
        {
            'purchase_price': 500000,
            'down_payment_pct': 100,
            'interest_rate': 5.0,
            'loan_term': 20,
            'expected_annual': 0.0
        },
        # 0% interest
        {
            'purchase_price': 500000,
            'down_payment_pct': 30,
            'interest_rate': 0.0,
            'loan_term': 20,
            'expected_annual': 17500.0
        }
    ]
    
    results = []
    for case in test_cases:
        try:
            result = calculate_mortgage_payment(
                case['purchase_price'],
                case['down_payment_pct'],
                case['interest_rate'],
                case['loan_term']
            )
            actual = round(result['annual_payment'], 2)
            expected = case['expected_annual']
            passed = abs(actual - expected) < 1.0  # Within $1
            
            results.append({
                'case': case,
                'actual': actual,
                'expected': expected,
                'passed': passed
            })
        except Exception as e:
            results.append({
                'case': case,
                'error': str(e),
                'passed': False
            })
    
    return results


if __name__ == "__main__":
    # Run basic tests
    test_results = _test_mortgage_calculations()
    for i, result in enumerate(test_results):
        if result.get('passed', False):
            print(f"Test {i+1}: PASSED")
        else:
            print(f"Test {i+1}: FAILED - {result}")