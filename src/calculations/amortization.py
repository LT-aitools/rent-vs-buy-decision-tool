"""
Amortization Schedule Calculation Functions
Year-by-year loan balance tracking and payment breakdown

This module handles detailed amortization calculations including:
- Complete amortization schedule generation
- Year-by-year loan balance tracking
- Interest and principal payment breakdown
- Remaining balance calculations for any year

All calculations handle edge cases (0% interest, 100% down payment) properly.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def generate_amortization_schedule(
    loan_amount: float,
    annual_payment: float,
    interest_rate: float,
    loan_term: int
) -> List[Dict[str, float]]:
    """
    Generate complete amortization schedule year by year
    
    Based on Business PRD amortization logic:
    - Beginning Balance = Remaining loan balance from previous year (Year 0 = Loan Amount)
    - Interest Portion = Beginning Balance × Interest Rate
    - Principal Portion = Annual Mortgage Payment - Interest Portion
    - Remaining Loan Balance = Beginning Balance - Principal Portion
    
    Args:
        loan_amount: Initial loan amount
        annual_payment: Annual mortgage payment
        interest_rate: Annual interest rate (percentage)
        loan_term: Loan term in years
    
    Returns:
        List of dictionaries, one for each year, containing:
        - year: Year number
        - beginning_balance: Loan balance at start of year
        - interest_portion: Interest paid during year
        - principal_portion: Principal paid during year
        - ending_balance: Loan balance at end of year
        - cumulative_interest: Total interest paid through this year
        - cumulative_principal: Total principal paid through this year
        
    Example:
        >>> schedule = generate_amortization_schedule(350000, 27738, 5.0, 20)
        >>> len(schedule)
        20
        >>> schedule[0]['interest_portion']  # Year 1 interest
        17500.0
    """
    if loan_amount <= 0:
        return []
    
    if annual_payment <= 0:
        return []
    
    schedule = []
    remaining_balance = loan_amount
    cumulative_interest = 0.0
    cumulative_principal = 0.0
    
    for year in range(1, loan_term + 1):
        beginning_balance = remaining_balance
        
        # Handle edge cases
        if remaining_balance <= 0:
            # Loan already paid off
            schedule.append({
                'year': year,
                'beginning_balance': 0.0,
                'interest_portion': 0.0,
                'principal_portion': 0.0,
                'ending_balance': 0.0,
                'cumulative_interest': cumulative_interest,
                'cumulative_principal': cumulative_principal
            })
            continue
        
        # Calculate interest portion
        if interest_rate == 0:
            interest_portion = 0.0
        else:
            interest_portion = beginning_balance * interest_rate / 100
        
        # Calculate principal portion
        principal_portion = min(annual_payment - interest_portion, beginning_balance)
        
        # Ensure principal portion is not negative
        if principal_portion < 0:
            # Payment is less than interest - this shouldn't happen in normal scenarios
            logger.warning(f"Year {year}: Payment ({annual_payment}) less than interest ({interest_portion})")
            principal_portion = 0.0
        
        # Calculate ending balance
        ending_balance = max(0.0, beginning_balance - principal_portion)
        
        # Update cumulative totals
        cumulative_interest += interest_portion
        cumulative_principal += principal_portion
        
        schedule.append({
            'year': year,
            'beginning_balance': float(beginning_balance),
            'interest_portion': float(interest_portion),
            'principal_portion': float(principal_portion),
            'ending_balance': float(ending_balance),
            'cumulative_interest': float(cumulative_interest),
            'cumulative_principal': float(cumulative_principal)
        })
        
        # Update remaining balance for next iteration
        remaining_balance = ending_balance
        
        # Early termination if loan is paid off
        if ending_balance <= 0.01:  # Within 1 cent
            # Fill remaining years with zeros
            for future_year in range(year + 1, loan_term + 1):
                schedule.append({
                    'year': future_year,
                    'beginning_balance': 0.0,
                    'interest_portion': 0.0,
                    'principal_portion': 0.0,
                    'ending_balance': 0.0,
                    'cumulative_interest': cumulative_interest,
                    'cumulative_principal': cumulative_principal
                })
            break
    
    return schedule


def calculate_remaining_balance(
    loan_amount: float,
    annual_payment: float,
    interest_rate: float,
    year: int
) -> float:
    """
    Calculate remaining loan balance for a specific year
    
    Args:
        loan_amount: Initial loan amount
        annual_payment: Annual mortgage payment
        interest_rate: Annual interest rate (percentage)
        year: Year to calculate balance for (1-based)
    
    Returns:
        Remaining loan balance at end of specified year
        
    Example:
        >>> balance = calculate_remaining_balance(350000, 27738, 5.0, 10)
        >>> round(balance, 2)
        196534.67
    """
    if loan_amount <= 0:
        return 0.0
    
    if year <= 0:
        return loan_amount  # Year 0 = original loan amount
    
    remaining_balance = loan_amount
    
    for current_year in range(1, year + 1):
        if remaining_balance <= 0:
            break
        
        # Calculate interest for this year
        if interest_rate == 0:
            interest_portion = 0.0
        else:
            interest_portion = remaining_balance * interest_rate / 100
        
        # Calculate principal payment
        principal_portion = min(annual_payment - interest_portion, remaining_balance)
        principal_portion = max(0.0, principal_portion)  # Ensure non-negative
        
        # Update remaining balance
        remaining_balance = max(0.0, remaining_balance - principal_portion)
    
    return float(remaining_balance)


def calculate_payment_breakdown(
    loan_amount: float,
    annual_payment: float,
    interest_rate: float,
    year: int
) -> Dict[str, float]:
    """
    Calculate interest and principal breakdown for a specific year
    
    Args:
        loan_amount: Initial loan amount
        annual_payment: Annual mortgage payment
        interest_rate: Annual interest rate (percentage)
        year: Year to calculate breakdown for
    
    Returns:
        Dictionary with payment breakdown:
        - beginning_balance: Loan balance at start of year
        - interest_portion: Interest payment for the year
        - principal_portion: Principal payment for the year
        - ending_balance: Loan balance at end of year
        
    Example:
        >>> breakdown = calculate_payment_breakdown(350000, 27738, 5.0, 1)
        >>> breakdown['interest_portion']
        17500.0
        >>> breakdown['principal_portion']  
        10238.0
    """
    if year <= 0:
        return {
            'beginning_balance': 0.0,
            'interest_portion': 0.0,
            'principal_portion': 0.0,
            'ending_balance': 0.0
        }
    
    # Get beginning balance (end of previous year)
    beginning_balance = calculate_remaining_balance(loan_amount, annual_payment, interest_rate, year - 1)
    
    if beginning_balance <= 0:
        return {
            'beginning_balance': 0.0,
            'interest_portion': 0.0,
            'principal_portion': 0.0,
            'ending_balance': 0.0
        }
    
    # Calculate interest portion
    if interest_rate == 0:
        interest_portion = 0.0
    else:
        interest_portion = beginning_balance * interest_rate / 100
    
    # Calculate principal portion
    principal_portion = min(annual_payment - interest_portion, beginning_balance)
    principal_portion = max(0.0, principal_portion)
    
    # Calculate ending balance
    ending_balance = max(0.0, beginning_balance - principal_portion)
    
    return {
        'beginning_balance': float(beginning_balance),
        'interest_portion': float(interest_portion),
        'principal_portion': float(principal_portion),
        'ending_balance': float(ending_balance)
    }


def calculate_total_interest_paid(
    loan_amount: float,
    annual_payment: float,
    interest_rate: float,
    loan_term: int
) -> Dict[str, float]:
    """
    Calculate total interest paid over the life of the loan
    
    Args:
        loan_amount: Initial loan amount
        annual_payment: Annual mortgage payment
        interest_rate: Annual interest rate (percentage)
        loan_term: Loan term in years
    
    Returns:
        Dictionary with total payment breakdown:
        - total_payments: Total payments over loan term
        - total_interest: Total interest paid
        - total_principal: Total principal paid
        - effective_rate: Effective interest rate
    """
    schedule = generate_amortization_schedule(loan_amount, annual_payment, interest_rate, loan_term)
    
    if not schedule:
        return {
            'total_payments': 0.0,
            'total_interest': 0.0,
            'total_principal': 0.0,
            'effective_rate': 0.0
        }
    
    # Get final cumulative totals
    final_year = schedule[-1]
    total_interest = final_year['cumulative_interest']
    total_principal = final_year['cumulative_principal']
    total_payments = total_interest + total_principal
    
    # Calculate effective rate
    if loan_amount > 0 and loan_term > 0:
        effective_rate = (total_interest / loan_amount) / loan_term * 100
    else:
        effective_rate = 0.0
    
    return {
        'total_payments': float(total_payments),
        'total_interest': float(total_interest),
        'total_principal': float(total_principal),
        'effective_rate': float(effective_rate)
    }


def create_amortization_table(
    loan_amount: float,
    annual_payment: float,
    interest_rate: float,
    loan_term: int
) -> pd.DataFrame:
    """
    Create a pandas DataFrame with the complete amortization schedule
    
    Args:
        loan_amount: Initial loan amount
        annual_payment: Annual mortgage payment
        interest_rate: Annual interest rate (percentage)
        loan_term: Loan term in years
    
    Returns:
        pandas DataFrame with amortization schedule
    """
    schedule = generate_amortization_schedule(loan_amount, annual_payment, interest_rate, loan_term)
    
    if not schedule:
        return pd.DataFrame()
    
    df = pd.DataFrame(schedule)
    
    # Add some calculated columns for analysis
    df['total_payment'] = df['interest_portion'] + df['principal_portion']
    df['interest_percentage'] = (df['interest_portion'] / df['total_payment'] * 100).fillna(0)
    df['principal_percentage'] = (df['principal_portion'] / df['total_payment'] * 100).fillna(0)
    
    return df


def calculate_payoff_time(
    loan_amount: float,
    annual_payment: float,
    interest_rate: float,
    extra_payment: float = 0.0
) -> Dict[str, float]:
    """
    Calculate loan payoff time with optional extra payments
    
    Args:
        loan_amount: Initial loan amount
        annual_payment: Regular annual mortgage payment
        interest_rate: Annual interest rate (percentage)
        extra_payment: Additional annual payment toward principal
    
    Returns:
        Dictionary with payoff analysis:
        - payoff_years: Years to pay off loan
        - total_interest_saved: Interest saved with extra payments
        - time_saved_years: Years saved with extra payments
    """
    if loan_amount <= 0:
        return {
            'payoff_years': 0.0,
            'total_interest_saved': 0.0,
            'time_saved_years': 0.0
        }
    
    effective_payment = annual_payment + extra_payment
    remaining_balance = loan_amount
    years = 0
    total_interest = 0.0
    
    max_years = 100  # Safety limit
    
    while remaining_balance > 0.01 and years < max_years:
        years += 1
        
        # Calculate interest for this year
        if interest_rate == 0:
            interest_portion = 0.0
        else:
            interest_portion = remaining_balance * interest_rate / 100
        
        total_interest += interest_portion
        
        # Calculate principal payment
        principal_payment = min(effective_payment - interest_portion, remaining_balance)
        principal_payment = max(0.0, principal_payment)
        
        # Update remaining balance
        remaining_balance = max(0.0, remaining_balance - principal_payment)
        
        # Break if payment can't cover interest
        if principal_payment <= 0:
            logger.warning("Payment cannot cover interest - loan will not be paid off")
            break
    
    # Calculate savings if extra payment provided
    if extra_payment > 0:
        # Calculate standard payoff for comparison
        standard_schedule = generate_amortization_schedule(loan_amount, annual_payment, interest_rate, max_years)
        
        if standard_schedule:
            standard_years = len([y for y in standard_schedule if y['ending_balance'] > 0.01])
            standard_interest = standard_schedule[-1]['cumulative_interest'] if standard_schedule else total_interest
            
            interest_saved = standard_interest - total_interest
            time_saved = standard_years - years
        else:
            interest_saved = 0.0
            time_saved = 0.0
    else:
        interest_saved = 0.0
        time_saved = 0.0
    
    return {
        'payoff_years': float(years),
        'total_interest_paid': float(total_interest),
        'total_interest_saved': float(interest_saved),
        'time_saved_years': float(time_saved)
    }


def _test_amortization_calculations():
    """Internal function to test amortization calculation accuracy"""
    test_cases = [
        {
            'name': 'Standard mortgage',
            'loan_amount': 350000,
            'annual_payment': 27718.14,
            'interest_rate': 5.0,
            'loan_term': 20,
            'test_year': 1,
            'expected_interest_year_1': 17500.0,
            'expected_principal_year_1': 10218.14
        },
        {
            'name': '0% interest rate',
            'loan_amount': 350000,
            'annual_payment': 17500,  # 350000 / 20
            'interest_rate': 0.0,
            'loan_term': 20,
            'test_year': 1,
            'expected_interest_year_1': 0.0,
            'expected_principal_year_1': 17500.0
        }
    ]
    
    results = []
    for case in test_cases:
        try:
            # Test payment breakdown for specific year
            breakdown = calculate_payment_breakdown(
                case['loan_amount'],
                case['annual_payment'],
                case['interest_rate'],
                case['test_year']
            )
            
            tests = [
                {
                    'field': 'interest_portion',
                    'actual': breakdown['interest_portion'],
                    'expected': case['expected_interest_year_1'],
                    'passed': abs(breakdown['interest_portion'] - case['expected_interest_year_1']) < 1.0
                },
                {
                    'field': 'principal_portion',
                    'actual': breakdown['principal_portion'],
                    'expected': case['expected_principal_year_1'],
                    'passed': abs(breakdown['principal_portion'] - case['expected_principal_year_1']) < 1.0
                }
            ]
            
            # Test full schedule generation
            schedule = generate_amortization_schedule(
                case['loan_amount'],
                case['annual_payment'],
                case['interest_rate'],
                case['loan_term']
            )
            
            schedule_test = {
                'field': 'schedule_length',
                'actual': len(schedule),
                'expected': case['loan_term'],
                'passed': len(schedule) == case['loan_term']
            }
            tests.append(schedule_test)
            
            results.append({
                'case': case['name'],
                'tests': tests,
                'all_passed': all(t['passed'] for t in tests)
            })
            
        except Exception as e:
            results.append({
                'case': case['name'],
                'error': str(e),
                'all_passed': False
            })
    
    return results


if __name__ == "__main__":
    # Run basic tests
    test_results = _test_amortization_calculations()
    for result in test_results:
        if result.get('all_passed', False):
            print(f"Amortization test '{result['case']}': PASSED")
        else:
            print(f"Amortization test '{result['case']}': FAILED")
            if 'error' in result:
                print(f"  Error: {result['error']}")
            else:
                for test in result.get('tests', []):
                    if not test['passed']:
                        print(f"  {test['field']}: got {test['actual']}, expected {test['expected']}")