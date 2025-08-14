"""
Annual Cost Calculation Functions
Comprehensive annual operating cost calculations with Year-1 indexing

This module handles all annual cost calculations including:
- Property ownership costs: taxes, insurance, maintenance, CapEx reserves
- Rental costs with escalation patterns
- Critical Year-1 indexing: Year 1 uses base costs, escalation begins Year 2
- Tax benefits and deductions

All formulas follow the Business PRD specifications exactly.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_cost_escalation(
    base_cost: float,
    escalation_rate: float,
    year: int,
    year_1_indexing: bool = True
) -> float:
    """
    Calculate escalated cost using Year-1 indexing pattern
    
    Year-1 indexing means:
    - Year 1: Uses base cost (no escalation)
    - Year 2: base_cost * (1 + escalation_rate)^1
    - Year 3: base_cost * (1 + escalation_rate)^2
    - Year N: base_cost * (1 + escalation_rate)^(N-1)
    
    Args:
        base_cost: Base cost amount in Year 1
        escalation_rate: Annual escalation rate (as percentage)
        year: Year number (1, 2, 3, ...)
        year_1_indexing: Use Year-1 indexing pattern (default True)
    
    Returns:
        Escalated cost for the specified year
        
    Examples:
        >>> calculate_cost_escalation(1000, 3.0, 1)  # Year 1
        1000.0
        >>> calculate_cost_escalation(1000, 3.0, 2)  # Year 2
        1030.0
        >>> calculate_cost_escalation(1000, 3.0, 3)  # Year 3
        1060.9
    """
    if year < 1:
        raise ValueError("Year must be 1 or greater")
    
    if not year_1_indexing:
        # Standard escalation (Year 0 indexing)
        escalation_factor = (1 + escalation_rate / 100) ** year
    else:
        # Year-1 indexing: Year 1 uses base cost, escalation starts Year 2
        escalation_factor = (1 + escalation_rate / 100) ** (year - 1)
    
    return base_cost * escalation_factor


def calculate_annual_ownership_costs(
    purchase_price: float,
    property_tax_rate: float,
    property_tax_escalation: float,
    insurance_cost: float,
    annual_maintenance: float,
    property_management: float,
    capex_reserve_rate: float,
    obsolescence_risk_rate: float,
    inflation_rate: float,
    year: int
) -> Dict[str, float]:
    """
    Calculate all annual ownership costs with proper Year-1 indexing
    
    This function implements the exact Business PRD formula:
    - Property taxes escalate at their own rate
    - All other costs escalate with inflation
    - Year-1 indexing: Year 1 uses base costs, escalation begins Year 2
    
    Args:
        purchase_price: Total property acquisition cost
        property_tax_rate: Annual property tax rate (as percentage of property value)
        property_tax_escalation: Annual property tax assessment increase rate (percentage)
        insurance_cost: Annual property insurance cost (base amount)
        annual_maintenance: Annual maintenance cost (base amount)
        property_management: Annual property management fees (base amount)
        capex_reserve_rate: CapEx reserve rate (as percentage of purchase price)
        obsolescence_risk_rate: Obsolescence risk factor (as percentage of purchase price)
        inflation_rate: General inflation rate (percentage)
        year: Year number (1, 2, 3, ...)
    
    Returns:
        Dictionary of cost components:
        - property_taxes: Property tax amount for the year
        - insurance: Insurance cost for the year
        - maintenance: Maintenance cost for the year
        - property_management: Property management fees for the year
        - capex_reserve: CapEx reserve amount for the year
        - obsolescence_cost: Obsolescence risk cost for the year
        - total_annual_cost: Sum of all cost components
        
    Example:
        >>> costs = calculate_annual_ownership_costs(
        ...     purchase_price=500000,
        ...     property_tax_rate=1.2,
        ...     property_tax_escalation=2.0,
        ...     insurance_cost=5000,
        ...     annual_maintenance=10000,
        ...     property_management=2000,
        ...     capex_reserve_rate=1.5,
        ...     obsolescence_risk_rate=0.5,
        ...     inflation_rate=3.0,
        ...     year=1
        ... )
        >>> costs['property_taxes']
        6000.0
        >>> costs['total_annual_cost']
        32000.0
    """
    if year < 1:
        raise ValueError("Year must be 1 or greater")
    
    # Property taxes: Base on purchase price, escalate with property tax escalation rate
    property_tax_base = purchase_price * property_tax_rate / 100
    property_taxes = calculate_cost_escalation(
        property_tax_base, 
        property_tax_escalation, 
        year
    )
    
    # Insurance: Escalates with inflation
    insurance = calculate_cost_escalation(
        insurance_cost,
        inflation_rate,
        year
    )
    
    # Maintenance: Escalates with inflation
    maintenance = calculate_cost_escalation(
        annual_maintenance,
        inflation_rate,
        year
    )
    
    # Property management: Escalates with inflation
    property_management_cost = calculate_cost_escalation(
        property_management,
        inflation_rate,
        year
    )
    
    # CapEx reserve: Based on purchase price, escalates with inflation
    capex_reserve_base = purchase_price * capex_reserve_rate / 100
    capex_reserve = calculate_cost_escalation(
        capex_reserve_base,
        inflation_rate,
        year
    )
    
    # Obsolescence risk cost: Based on purchase price, escalates with inflation
    obsolescence_cost_base = purchase_price * obsolescence_risk_rate / 100
    obsolescence_cost = calculate_cost_escalation(
        obsolescence_cost_base,
        inflation_rate,
        year
    )
    
    # Calculate total annual cost
    total_annual_cost = (
        property_taxes + 
        insurance + 
        maintenance + 
        property_management_cost + 
        capex_reserve + 
        obsolescence_cost
    )
    
    return {
        'property_taxes': float(property_taxes),
        'insurance': float(insurance),
        'maintenance': float(maintenance),
        'property_management': float(property_management_cost),
        'capex_reserve': float(capex_reserve),
        'obsolescence_cost': float(obsolescence_cost),
        'total_annual_cost': float(total_annual_cost),
        'year': year
    }


def calculate_annual_rental_costs(
    current_annual_rent: float,
    rent_increase_rate: float,
    year: int,
    current_space_needed: Optional[float] = None,
    total_space_rented: Optional[float] = None,
    inflation_rate: float = 0.0
) -> Dict[str, float]:
    """
    Calculate annual rental costs with Year-1 indexing pattern
    
    CORRECTED FORMULA: Rent goes up by both inflation AND rent increase rate
    - Combined growth rate = (1 + inflation_rate/100) × (1 + rent_increase_rate/100) - 1
    - For Year N: Rent = Current Annual Rent × (1 + combined_rate)^(Year-1)
    
    Args:
        current_annual_rent: Current total annual rent cost
        rent_increase_rate: Annual rent escalation rate (percentage)
        year: Year number (1, 2, 3, ...)
        current_space_needed: Current space being rented (for per-unit calculations)
        total_space_rented: Total space rented if different from current needs
        inflation_rate: Annual inflation rate (percentage)
    
    Returns:
        Dictionary containing:
        - annual_rent: Total annual rent for the year
        - rent_per_unit: Rent per square meter (if space provided)
        - total_space: Total space being rented
        - year: Year number
        
    Example:
        >>> costs = calculate_annual_rental_costs(120000, 3.0, 1, inflation_rate=2.5)
        >>> costs['annual_rent']
        120000.0
        >>> costs = calculate_annual_rental_costs(120000, 3.0, 2)
        >>> costs['annual_rent']
        123600.0
    """
    if year < 1:
        raise ValueError("Year must be 1 or greater")
    
    # Calculate combined growth rate: (1 + inflation) × (1 + rent_increase) - 1
    combined_growth_rate = (1 + inflation_rate/100) * (1 + rent_increase_rate/100) - 1
    combined_growth_percentage = combined_growth_rate * 100
    
    # Calculate escalated rent using Year-1 indexing with combined rate
    annual_rent = calculate_cost_escalation(
        current_annual_rent,
        combined_growth_percentage,
        year
    )
    
    # Calculate per-unit rent if space information provided
    rent_per_unit = None
    if current_space_needed and current_space_needed > 0:
        base_rent_per_unit = current_annual_rent / current_space_needed
        rent_per_unit = calculate_cost_escalation(
            base_rent_per_unit,
            combined_growth_percentage,
            year
        )
    
    # Determine total space (use total_space_rented if provided, otherwise current_space_needed)
    total_space = total_space_rented if total_space_rented is not None else current_space_needed
    
    return {
        'annual_rent': float(annual_rent),
        'rent_per_unit': float(rent_per_unit) if rent_per_unit is not None else None,
        'total_space': float(total_space) if total_space is not None else None,
        'year': year
    }


def calculate_property_upgrade_costs(
    purchase_price: float,
    land_value_pct: float,
    upgrade_cycle_years: int,
    year: int,
    upgrade_cost_pct: float = 2.0
) -> float:
    """
    Calculate property upgrade costs for major renovations
    
    Based on Business PRD:
    - Applied in Property Upgrade Cycle Years
    - Original Building Value = Purchase Price - (Purchase Price × Land Value %)
    - Property Upgrade Cost = Original Building Value × 2% (major renovation estimate)
    
    Args:
        purchase_price: Total property acquisition cost
        land_value_pct: Land value as percentage of purchase price
        upgrade_cycle_years: Years between major upgrades (e.g., 15)
        year: Current year number
        upgrade_cost_pct: Upgrade cost as percentage of building value (default 2%)
    
    Returns:
        Property upgrade cost for the year (0 if not an upgrade year)
    """
    if year <= 0 or upgrade_cycle_years <= 0:
        return 0.0
    
    # Check if this is an upgrade year
    if year % upgrade_cycle_years != 0:
        return 0.0
    
    # Calculate building value (excluding land)
    building_value = purchase_price * (1 - land_value_pct / 100)
    
    # Calculate upgrade cost as percentage of building value
    upgrade_cost = building_value * upgrade_cost_pct / 100
    
    return float(upgrade_cost)


def calculate_tax_benefits(
    mortgage_interest: float,
    property_taxes: float,
    depreciation_amount: float,
    corporate_tax_rate: float,
    interest_deductible: bool = True,
    property_tax_deductible: bool = True,
    depreciation_deductible: bool = True
) -> Dict[str, float]:
    """
    Calculate tax benefits from property ownership
    
    Args:
        mortgage_interest: Mortgage interest paid during the year
        property_taxes: Property taxes paid during the year
        depreciation_amount: Depreciation deduction amount
        corporate_tax_rate: Corporate tax rate (percentage)
        interest_deductible: Is mortgage interest tax deductible
        property_tax_deductible: Are property taxes tax deductible
        depreciation_deductible: Is depreciation tax deductible
    
    Returns:
        Dictionary with tax benefit components and total savings
    """
    tax_rate = corporate_tax_rate / 100
    
    # Calculate deductible amounts
    interest_deduction = mortgage_interest if interest_deductible else 0.0
    property_tax_deduction = property_taxes if property_tax_deductible else 0.0
    depreciation_deduction = depreciation_amount if depreciation_deductible else 0.0
    
    # Calculate tax savings
    interest_tax_savings = interest_deduction * tax_rate
    property_tax_savings = property_tax_deduction * tax_rate
    depreciation_tax_savings = depreciation_deduction * tax_rate
    
    total_tax_savings = interest_tax_savings + property_tax_savings + depreciation_tax_savings
    
    return {
        'interest_deduction': float(interest_deduction),
        'property_tax_deduction': float(property_tax_deduction),
        'depreciation_deduction': float(depreciation_deduction),
        'interest_tax_savings': float(interest_tax_savings),
        'property_tax_savings': float(property_tax_savings),
        'depreciation_tax_savings': float(depreciation_tax_savings),
        'total_tax_savings': float(total_tax_savings)
    }


def calculate_subletting_income(
    property_size: float,
    current_space_needed: float,
    subletting_rate_per_unit: float,
    subletting_space_sqm: float,
    subletting_enabled: bool = False,
    year: int = 1,
    rent_increase_rate: float = 0.0,
    inflation_rate: float = 0.0
) -> Dict[str, float]:
    """
    Calculate potential subletting income from specified space with proper escalation
    
    CORRECTED FORMULA: Subletting income goes up by both inflation AND rent increase rate
    - Combined growth rate = (1 + inflation_rate/100) × (1 + rent_increase_rate/100) - 1
    - For Year N: Subletting Rate = Base Rate × (1 + combined_rate)^(Year-1)
    
    Args:
        property_size: Property size in square meters (ownership scenario)
        current_space_needed: Space needed for own operations
        subletting_rate_per_unit: Annual subletting rate per square meter (base year)
        subletting_space_sqm: Actual square meters user plans to sublet
        subletting_enabled: Whether subletting is allowed/feasible
        year: Year number (1, 2, 3, ...) for escalation
        rent_increase_rate: Annual rent escalation rate (percentage)
        inflation_rate: Annual inflation rate (percentage)
    
    Returns:
        Dictionary with subletting calculations
    """
    if not subletting_enabled:
        return {
            'available_space': 0.0,
            'subletting_space': 0.0,
            'subletting_income': 0.0,
            'subletting_enabled': False
        }
    
    # Calculate available space for subletting
    available_space = max(0.0, property_size - current_space_needed)
    
    # Use the minimum of what user wants to sublet and what's actually available
    actual_subletting_space = min(subletting_space_sqm, available_space)
    
    # Calculate escalated subletting rate using combined growth (inflation + rent increase)
    combined_growth_rate = (1 + inflation_rate/100) * (1 + rent_increase_rate/100) - 1
    combined_growth_percentage = combined_growth_rate * 100
    
    escalated_subletting_rate = calculate_cost_escalation(
        subletting_rate_per_unit,
        combined_growth_percentage,
        year
    )
    
    # Calculate subletting income based on actual space and escalated rate
    subletting_income = actual_subletting_space * escalated_subletting_rate
    
    return {
        'available_space': float(available_space),
        'subletting_space': float(actual_subletting_space),
        'subletting_income': float(subletting_income),
        'subletting_enabled': True
    }


def _test_annual_cost_calculations():
    """Internal function to test annual cost calculation accuracy"""
    test_cases = [
        # Year 1 - base costs (no escalation)
        {
            'purchase_price': 500000,
            'property_tax_rate': 1.2,
            'property_tax_escalation': 2.0,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'inflation_rate': 3.0,
            'year': 1,
            'expected_property_taxes': 6000.0,  # 500000 * 1.2% * (1.02)^0
            'expected_insurance': 5000.0,  # 5000 * (1.03)^0
            'expected_maintenance': 10000.0  # 10000 * (1.03)^0
        },
        # Year 2 - first escalation
        {
            'purchase_price': 500000,
            'property_tax_rate': 1.2,
            'property_tax_escalation': 2.0,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'inflation_rate': 3.0,
            'year': 2,
            'expected_property_taxes': 6120.0,  # 500000 * 1.2% * (1.02)^1
            'expected_insurance': 5150.0,  # 5000 * (1.03)^1
            'expected_maintenance': 10300.0  # 10000 * (1.03)^1
        }
    ]
    
    results = []
    for case in test_cases:
        try:
            result = calculate_annual_ownership_costs(
                case['purchase_price'],
                case['property_tax_rate'],
                case['property_tax_escalation'],
                case['insurance_cost'],
                case['annual_maintenance'],
                0,  # property_management
                1.5,  # capex_reserve_rate
                0.5,  # obsolescence_risk_rate
                case['inflation_rate'],
                case['year']
            )
            
            tests = [
                ('property_taxes', case['expected_property_taxes']),
                ('insurance', case['expected_insurance']),
                ('maintenance', case['expected_maintenance'])
            ]
            
            case_results = []
            for field, expected in tests:
                actual = result[field]
                passed = abs(actual - expected) < 0.01  # Within 1 cent
                case_results.append({
                    'field': field,
                    'actual': actual,
                    'expected': expected,
                    'passed': passed
                })
            
            results.append({
                'case': case,
                'tests': case_results,
                'all_passed': all(t['passed'] for t in case_results)
            })
            
        except Exception as e:
            results.append({
                'case': case,
                'error': str(e),
                'all_passed': False
            })
    
    return results


if __name__ == "__main__":
    # Run basic tests
    test_results = _test_annual_cost_calculations()
    for i, result in enumerate(test_results):
        if result.get('all_passed', False):
            print(f"Annual costs test {i+1}: PASSED")
        else:
            print(f"Annual costs test {i+1}: FAILED")
            if 'error' in result:
                print(f"  Error: {result['error']}")
            else:
                for test in result.get('tests', []):
                    if not test['passed']:
                        print(f"  {test['field']}: got {test['actual']}, expected {test['expected']}")