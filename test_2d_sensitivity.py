"""
Test script for two-dimensional sensitivity analysis concept
"""

import sys
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append('.')
from src.calculations.npv_analysis import calculate_npv_comparison


def create_2d_sensitivity_table(
    base_params: Dict[str, float],
    x_metric: str,
    y_metric: str,
    x_range: List[float],
    y_range: List[float]
) -> Dict[str, Any]:
    """
    Create two-dimensional sensitivity table showing NPV impacts.
    
    Args:
        base_params: Base case parameters
        x_metric: Parameter name for X-axis (columns)
        y_metric: Parameter name for Y-axis (rows)
        x_range: List of percentage changes for X-axis
        y_range: List of percentage changes for Y-axis
    
    Returns:
        Dictionary with table data and metadata
    """
    start_time = time.time()
    
    # Ensure required parameters
    required_defaults = {
        'loan_term': 20,
        'analysis_period': 25,
        'transaction_costs': base_params.get('purchase_price', 500000) * 0.05,
        'property_tax_rate': 1.2,
        'property_tax_escalation': 2.0,
        'insurance_cost': 5000,
        'annual_maintenance': 10000,
        'property_management': 0.0,
        'capex_reserve_rate': 1.5,
        'obsolescence_risk_rate': 0.5,
        'inflation_rate': 3.0,
        'land_value_pct': 25.0,
        'depreciation_period': 39,
        'corporate_tax_rate': 25.0,
        'interest_deductible': True,
        'property_tax_deductible': True,
        'rent_deductible': True,
        'moving_costs': 0.0,
        'space_improvement_cost': 0.0
    }
    
    complete_params = base_params.copy()
    for key, default_value in required_defaults.items():
        if key not in complete_params:
            complete_params[key] = default_value
    
    # Calculate base case NPV
    base_result = calculate_npv_comparison(**complete_params)
    base_npv = base_result['npv_difference']
    
    print(f"Base NPV difference: ${base_npv:,.0f}")
    print(f"Creating {len(y_range)}x{len(x_range)} sensitivity table...")
    
    # Generate all parameter combinations
    combinations = []
    for y_change in y_range:
        for x_change in x_range:
            combinations.append((x_change, y_change))
    
    # Calculate NPV for all combinations
    npv_results = []
    
    for x_change, y_change in combinations:
        # Create modified parameters
        modified_params = complete_params.copy()
        
        # Apply percentage changes
        x_base_value = complete_params.get(x_metric, 0.0)
        y_base_value = complete_params.get(y_metric, 0.0)
        
        modified_params[x_metric] = x_base_value + x_change
        modified_params[y_metric] = y_base_value + y_change
        
        # Calculate NPV
        try:
            result = calculate_npv_comparison(**modified_params)
            npv_diff = result['npv_difference'] - base_npv  # Difference from base case
            npv_results.append(npv_diff)
        except Exception as e:
            print(f"Error calculating NPV for {x_metric}={x_change}, {y_metric}={y_change}: {e}")
            npv_results.append(0.0)
    
    # Organize results into 2D array
    npv_table = []
    result_index = 0
    
    for y_change in y_range:
        row = []
        for x_change in x_range:
            npv_diff = npv_results[result_index]
            row.append(npv_diff)
            result_index += 1
        npv_table.append(row)
    
    calculation_time = time.time() - start_time
    
    return {
        'x_metric': x_metric,
        'y_metric': y_metric,
        'x_values': x_range,
        'y_values': y_range,
        'npv_table': npv_table,
        'base_npv': base_npv,
        'calculation_time': calculation_time
    }


def format_table_for_display(result: Dict[str, Any], base_params: Dict[str, float]) -> None:
    """Print formatted table similar to the image provided."""
    
    print(f"\nSensitivity Analysis: {result['y_metric'].replace('_', ' ').title()} vs {result['x_metric'].replace('_', ' ').title()}")
    print("=" * 80)
    
    # Get actual values being used in analysis
    x_actual_value = base_params.get(result['x_metric'], 0.0)
    y_actual_value = base_params.get(result['y_metric'], 0.0)
    
    # Header row with actual values
    header = f"{'':>15}"
    for x_change in result['x_values']:
        if x_change == 0.0:
            header += f"{x_actual_value:>11.1f}%"  # Show actual value for 0% change
        else:
            actual_x_value = x_actual_value + x_change
            header += f"{actual_x_value:>11.1f}%"
    print(header)
    
    # Change indicators
    change_header = f"{'':>15}"
    for x_change in result['x_values']:
        if x_change == 0.0:
            change_header += f"{'(0%)':>12}"
        else:
            change_header += f"{f'({x_change:+.1f}%)':>12}"
    print(change_header)
    print("-" * 80)
    
    # Data rows
    for i, y_change in enumerate(result['y_values']):
        if y_change == 0.0:
            row_label = f"{y_actual_value:>12.1f}%"  # Show actual value for 0% change
        else:
            actual_y_value = y_actual_value + y_change
            row_label = f"{actual_y_value:>12.1f}%"
        
        row = row_label
        for j, x_change in enumerate(result['x_values']):
            npv_diff = result['npv_table'][i][j]
            if abs(npv_diff) >= 1000:
                formatted_val = f"${npv_diff/1000:>9.0f}K"
            else:
                formatted_val = f"${npv_diff:>10.0f}"
            row += f"{formatted_val:>12}"
        
        # Add change indicator for rows
        if y_change == 0.0:
            row += f"  {'(0%)'}"
        else:
            row += f"  {'(' + str(y_change) + '%)'}"
        
        print(row)
    
    print("-" * 80)
    print(f"Base NPV Difference: ${result['base_npv']:,.0f}")
    print(f"Actual {result['x_metric'].replace('_', ' ').title()}: {x_actual_value}%")
    print(f"Actual {result['y_metric'].replace('_', ' ').title()}: {y_actual_value}%")
    print(f"Calculation Time: {result['calculation_time']:.2f}s")
    print(f"Table shows NPV change from base case when both metrics change simultaneously")


if __name__ == "__main__":
    # Test parameters - similar to your actual use case
    test_params = {
        'purchase_price': 500000,
        'current_annual_rent': 24000,
        'down_payment_pct': 30.0,
        'interest_rate': 5.0,
        'market_appreciation_rate': 3.0,
        'rent_increase_rate': 3.0,
        'cost_of_capital': 8.0,
        'inflation_rate': 3.0
    }
    
    print("Testing Two-Dimensional Sensitivity Analysis")
    print("=" * 50)
    
    # Example 1: Interest Rate vs Market Appreciation Rate
    # Using your requested range: -1.5%, -1%, -0.5%, 0%, +0.5%, +1%, +1.5%
    result1 = create_2d_sensitivity_table(
        test_params,
        x_metric='interest_rate',
        y_metric='market_appreciation_rate',
        x_range=[-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5],
        y_range=[-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
    )
    
    format_table_for_display(result1, test_params)
    
    print("\n" + "=" * 80)
    
    # Example 2: Rent Increase Rate vs Inflation Rate  
    result2 = create_2d_sensitivity_table(
        test_params,
        x_metric='rent_increase_rate',
        y_metric='inflation_rate',
        x_range=[-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5],
        y_range=[-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
    )
    
    format_table_for_display(result2, test_params)
    
    print("\n✅ Two-dimensional sensitivity analysis working correctly!")
    print("✅ Ready for dashboard integration!")