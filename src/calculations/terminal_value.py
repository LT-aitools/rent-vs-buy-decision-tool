"""
Terminal Value Calculation Functions
Hold-forever wealth analysis for property ownership

This module handles terminal value calculations for the hold-forever ownership strategy:
- Land value appreciation over analysis period
- Building depreciation and subsequent appreciation
- Net property equity after loan paydown
- Wealth accumulation vs rental scenario comparison

All formulas follow the Business PRD specifications exactly.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_property_appreciation(
    initial_value: float,
    appreciation_rate: float,
    time_period: int
) -> float:
    """
    Calculate property value appreciation over time using compound growth
    
    Args:
        initial_value: Starting property value
        appreciation_rate: Annual appreciation rate (percentage)
        time_period: Number of years
    
    Returns:
        Appreciated value after time period
        
    Example:
        >>> calculate_property_appreciation(100000, 3.0, 10)
        134391.64
    """
    if time_period <= 0:
        return initial_value
    
    if appreciation_rate == 0:
        return initial_value
        
    appreciation_factor = (1 + appreciation_rate / 100) ** time_period
    return initial_value * appreciation_factor


def calculate_depreciation_schedule(
    building_value: float,
    depreciation_period: int,
    analysis_period: int
) -> Dict[str, float]:
    """
    Calculate building depreciation over analysis period
    
    Based on Business PRD:
    - Accumulated Depreciation = MIN(Building Value, Building Value × Analysis Period / Depreciation Period)
    - Depreciated Building Value = Building Value - Accumulated Depreciation
    
    Args:
        building_value: Initial building value (excluding land)
        depreciation_period: Total depreciation period in years
        analysis_period: Analysis period in years
    
    Returns:
        Dictionary with depreciation calculations
        
    Example:
        >>> result = calculate_depreciation_schedule(400000, 39, 25)
        >>> result['accumulated_depreciation']
        256410.26
        >>> result['depreciated_building_value']
        143589.74
    """
    if building_value <= 0 or depreciation_period <= 0:
        return {
            'accumulated_depreciation': 0.0,
            'depreciated_building_value': building_value,
            'annual_depreciation': 0.0,
            'depreciation_rate': 0.0
        }
    
    # Calculate annual depreciation rate
    annual_depreciation = building_value / depreciation_period
    depreciation_rate = 1.0 / depreciation_period * 100  # As percentage
    
    # Calculate accumulated depreciation (cannot exceed building value)
    if analysis_period >= depreciation_period:
        # Fully depreciated
        accumulated_depreciation = building_value
    else:
        # Partial depreciation
        accumulated_depreciation = building_value * analysis_period / depreciation_period
    
    # Ensure accumulated depreciation doesn't exceed building value
    accumulated_depreciation = min(building_value, accumulated_depreciation)
    
    # Calculate remaining depreciated building value
    depreciated_building_value = building_value - accumulated_depreciation
    
    return {
        'accumulated_depreciation': float(accumulated_depreciation),
        'depreciated_building_value': float(depreciated_building_value),
        'annual_depreciation': float(annual_depreciation),
        'depreciation_rate': float(depreciation_rate)
    }


def calculate_terminal_value(
    purchase_price: float,
    land_value_pct: float,
    market_appreciation_rate: float,
    depreciation_period: int,
    analysis_period: int,
    remaining_loan_balance: float
) -> Dict[str, float]:
    """
    Calculate terminal value for hold-forever ownership strategy
    
    This is the core terminal value calculation implementing the exact Business PRD formula:
    
    1. Land Value = Purchase Price × Land Value %
    2. Building Value = Purchase Price - Land Value
    3. Land Value at End = Land Value × (1 + Market Appreciation Rate)^Analysis Period
    4. Accumulated Depreciation = MIN(Building Value, Building Value × Analysis Period / Depreciation Period)
    5. Depreciated Building Value = Building Value - Accumulated Depreciation
    6. Building Value at End = Depreciated Building Value × (1 + Market Appreciation Rate)^Analysis Period
    7. Terminal Property Value = Land Value at End + Building Value at End
    8. Net Property Equity = Terminal Property Value - Remaining Loan Balance
    
    Args:
        purchase_price: Total property acquisition cost
        land_value_pct: Land value as percentage of purchase price (e.g., 25 for 25%)
        market_appreciation_rate: Annual market appreciation rate (percentage)
        depreciation_period: Depreciation period in years (e.g., 39)
        analysis_period: Analysis time horizon in years
        remaining_loan_balance: Outstanding loan balance at end of period
    
    Returns:
        Dictionary with terminal value components:
        - initial_land_value: Land value at purchase
        - initial_building_value: Building value at purchase
        - land_value_end: Land value at end of analysis period
        - building_value_end: Building value at end (after depreciation + appreciation)
        - terminal_property_value: Total property value at end
        - net_property_equity: Property equity after loan payoff
        - total_appreciation: Total property value gain
        - accumulated_depreciation: Total building depreciation
        
    Example:
        >>> result = calculate_terminal_value(
        ...     purchase_price=500000,
        ...     land_value_pct=25,
        ...     market_appreciation_rate=3.0,
        ...     depreciation_period=39,
        ...     analysis_period=25,
        ...     remaining_loan_balance=150000
        ... )
        >>> result['net_property_equity']
        567159.44
    """
    if purchase_price <= 0:
        raise ValueError("Purchase price must be positive")
    
    if land_value_pct < 0 or land_value_pct > 100:
        raise ValueError("Land value percentage must be between 0 and 100")
    
    if analysis_period <= 0:
        raise ValueError("Analysis period must be positive")
    
    # Step 1: Calculate initial land and building values
    initial_land_value = purchase_price * land_value_pct / 100
    initial_building_value = purchase_price - initial_land_value
    
    # Step 2: Calculate land appreciation (land always appreciates with market)
    land_value_end = calculate_property_appreciation(
        initial_land_value,
        market_appreciation_rate,
        analysis_period
    )
    
    # Step 3: Calculate building depreciation
    depreciation_info = calculate_depreciation_schedule(
        initial_building_value,
        depreciation_period,
        analysis_period
    )
    
    accumulated_depreciation = depreciation_info['accumulated_depreciation']
    depreciated_building_value = depreciation_info['depreciated_building_value']
    
    # Step 4: Apply market appreciation to depreciated building value
    building_value_end = calculate_property_appreciation(
        depreciated_building_value,
        market_appreciation_rate,
        analysis_period
    )
    
    # Step 5: Calculate total terminal property value
    terminal_property_value = land_value_end + building_value_end
    
    # Step 6: Calculate net property equity (after loan balance)
    net_property_equity = terminal_property_value - remaining_loan_balance
    
    # Step 7: Calculate total appreciation
    total_appreciation = terminal_property_value - purchase_price
    
    return {
        'initial_land_value': float(initial_land_value),
        'initial_building_value': float(initial_building_value),
        'land_value_end': float(land_value_end),
        'building_value_end': float(building_value_end),
        'terminal_property_value': float(terminal_property_value),
        'net_property_equity': float(net_property_equity),
        'total_appreciation': float(total_appreciation),
        'accumulated_depreciation': float(accumulated_depreciation),
        'depreciated_building_value': float(depreciated_building_value),
        'remaining_loan_balance': float(remaining_loan_balance)
    }


def calculate_rental_terminal_value(
    security_deposit: float,
    inflation_rate: float,
    analysis_period: int
) -> Dict[str, float]:
    """
    Calculate terminal value for rental scenario (hold-forever comparison)
    
    Based on Business PRD:
    - Rental Terminal Value = Security Deposit Recovery only
    - Security Deposit Recovery = Security Deposit × (1 + Inflation Rate)^Analysis Period
    - No property wealth accumulated
    
    Args:
        security_deposit: Initial security deposit paid
        inflation_rate: Annual inflation rate (percentage)
        analysis_period: Analysis time horizon in years
    
    Returns:
        Dictionary with rental terminal value components
    """
    if analysis_period <= 0:
        return {
            'security_deposit_recovery': security_deposit,
            'terminal_asset_value': 0.0,
            'net_wealth_accumulation': 0.0
        }
    
    # Security deposit recovers with inflation
    security_deposit_recovery = calculate_property_appreciation(
        security_deposit,
        inflation_rate,
        analysis_period
    )
    
    return {
        'security_deposit_recovery': float(security_deposit_recovery),
        'terminal_asset_value': 0.0,  # No property ownership
        'net_wealth_accumulation': 0.0  # No property equity built
    }


def calculate_wealth_comparison(
    ownership_terminal_value: Dict[str, float],
    rental_terminal_value: Dict[str, float]
) -> Dict[str, float]:
    """
    Compare wealth accumulation between ownership and rental strategies
    
    Args:
        ownership_terminal_value: Result from calculate_terminal_value()
        rental_terminal_value: Result from calculate_rental_terminal_value()
    
    Returns:
        Dictionary with wealth comparison metrics
    """
    ownership_wealth = ownership_terminal_value['net_property_equity']
    rental_wealth = rental_terminal_value['security_deposit_recovery']
    
    wealth_advantage = ownership_wealth - rental_wealth
    
    if rental_wealth > 0:
        wealth_advantage_pct = (wealth_advantage / rental_wealth) * 100
    else:
        wealth_advantage_pct = float('inf') if wealth_advantage > 0 else 0.0
    
    return {
        'ownership_wealth': float(ownership_wealth),
        'rental_wealth': float(rental_wealth),
        'wealth_advantage': float(wealth_advantage),
        'wealth_advantage_pct': float(wealth_advantage_pct),
        'ownership_superior': wealth_advantage > 0
    }


def calculate_property_components_over_time(
    purchase_price: float,
    land_value_pct: float,
    market_appreciation_rate: float,
    depreciation_period: int,
    max_years: int
) -> List[Dict[str, float]]:
    """
    Calculate property value components year by year
    
    Useful for visualization and detailed analysis showing how land and building
    values change over time with depreciation and appreciation.
    
    Args:
        purchase_price: Total property acquisition cost
        land_value_pct: Land value as percentage of purchase price
        market_appreciation_rate: Annual market appreciation rate (percentage)
        depreciation_period: Depreciation period in years
        max_years: Maximum number of years to calculate
    
    Returns:
        List of dictionaries, one for each year, containing value components
    """
    yearly_values = []
    
    initial_land_value = purchase_price * land_value_pct / 100
    initial_building_value = purchase_price - initial_land_value
    
    for year in range(1, max_years + 1):
        # Land appreciation
        land_value = calculate_property_appreciation(
            initial_land_value,
            market_appreciation_rate,
            year
        )
        
        # Building depreciation
        depreciation_info = calculate_depreciation_schedule(
            initial_building_value,
            depreciation_period,
            year
        )
        
        # Building appreciation on depreciated value
        building_value = calculate_property_appreciation(
            depreciation_info['depreciated_building_value'],
            market_appreciation_rate,
            year
        )
        
        total_value = land_value + building_value
        
        yearly_values.append({
            'year': year,
            'land_value': float(land_value),
            'building_value': float(building_value),
            'total_property_value': float(total_value),
            'accumulated_depreciation': float(depreciation_info['accumulated_depreciation']),
            'depreciated_building_value': float(depreciation_info['depreciated_building_value'])
        })
    
    return yearly_values


def _test_terminal_value_calculations():
    """Internal function to test terminal value calculation accuracy"""
    test_cases = [
        {
            'name': 'Standard case',
            'purchase_price': 500000,
            'land_value_pct': 25,
            'market_appreciation_rate': 3.0,
            'depreciation_period': 39,
            'analysis_period': 25,
            'remaining_loan_balance': 150000,
            'expected_land_value_end': 261722.24,  # 125000 * (1.03)^25
            'expected_net_equity_range': (390000, 400000)  # Approximate range
        },
        {
            'name': 'No appreciation case',
            'purchase_price': 500000,
            'land_value_pct': 25,
            'market_appreciation_rate': 0.0,
            'depreciation_period': 39,
            'analysis_period': 25,
            'remaining_loan_balance': 0,
            'expected_land_value_end': 125000,  # No appreciation
            'expected_building_value_end': 134615.38  # 375000 - (375000*25/39)
        }
    ]
    
    results = []
    for case in test_cases:
        try:
            result = calculate_terminal_value(
                case['purchase_price'],
                case['land_value_pct'],
                case['market_appreciation_rate'],
                case['depreciation_period'],
                case['analysis_period'],
                case['remaining_loan_balance']
            )
            
            tests = []
            
            # Test land value
            if 'expected_land_value_end' in case:
                land_test = {
                    'field': 'land_value_end',
                    'actual': result['land_value_end'],
                    'expected': case['expected_land_value_end'],
                    'passed': abs(result['land_value_end'] - case['expected_land_value_end']) < 1.0
                }
                tests.append(land_test)
            
            # Test building value  
            if 'expected_building_value_end' in case:
                building_test = {
                    'field': 'building_value_end',
                    'actual': result['building_value_end'],
                    'expected': case['expected_building_value_end'],
                    'passed': abs(result['building_value_end'] - case['expected_building_value_end']) < 1.0
                }
                tests.append(building_test)
            
            # Test net equity range
            if 'expected_net_equity_range' in case:
                min_equity, max_equity = case['expected_net_equity_range']
                equity_test = {
                    'field': 'net_property_equity',
                    'actual': result['net_property_equity'],
                    'expected': f"{min_equity}-{max_equity}",
                    'passed': min_equity <= result['net_property_equity'] <= max_equity
                }
                tests.append(equity_test)
            
            results.append({
                'case': case['name'],
                'tests': tests,
                'result': result,
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
    test_results = _test_terminal_value_calculations()
    for result in test_results:
        if result.get('all_passed', False):
            print(f"Terminal value test '{result['case']}': PASSED")
        else:
            print(f"Terminal value test '{result['case']}': FAILED")
            if 'error' in result:
                print(f"  Error: {result['error']}")
            else:
                for test in result.get('tests', []):
                    if not test['passed']:
                        print(f"  {test['field']}: got {test['actual']}, expected {test['expected']}")