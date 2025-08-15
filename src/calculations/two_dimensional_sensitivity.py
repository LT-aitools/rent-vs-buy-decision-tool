"""
Two-Dimensional Sensitivity Analysis for Dashboard Integration

Replaces the current one-dimensional sensitivity analysis with interactive
two-dimensional tables where users can select X and Y axis metrics.
"""

import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .npv_analysis import calculate_npv_comparison

logger = logging.getLogger(__name__)


def calculate_2d_sensitivity_analysis(
    base_params: Dict[str, float],
    x_metric: str,
    y_metric: str,
    x_range: Optional[List[float]] = None,
    y_range: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Calculate two-dimensional sensitivity analysis for dashboard display.
    
    Args:
        base_params: Base case parameters for NPV calculation
        x_metric: Metric for X-axis (column headers)
        y_metric: Metric for Y-axis (row headers) 
        x_range: List of percentage changes for X-axis (e.g., [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5])
        y_range: List of percentage changes for Y-axis
        
    Returns:
        Dictionary with table data ready for dashboard display
    """
    
    # Available metrics with display names
    AVAILABLE_METRICS = {
        'rent_increase_rate': 'Rent Increase Rate',
        'interest_rate': 'Interest Rate',
        'inflation_rate': 'Inflation Rate',
        'market_appreciation_rate': 'Market Appreciation Rate'
    }
    
    # Validate metrics
    if x_metric not in AVAILABLE_METRICS:
        raise ValueError(f"Invalid X metric: {x_metric}. Available: {list(AVAILABLE_METRICS.keys())}")
    if y_metric not in AVAILABLE_METRICS:
        raise ValueError(f"Invalid Y metric: {y_metric}. Available: {list(AVAILABLE_METRICS.keys())}")
    if x_metric == y_metric:
        raise ValueError("X and Y metrics must be different")
    
    # Use default ranges if not provided
    if x_range is None:
        x_range = [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
    if y_range is None:
        y_range = [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
    
    start_time = time.time()
    
    # Get actual values being used in analysis
    x_actual_value = base_params.get(x_metric, 0.0)
    y_actual_value = base_params.get(y_metric, 0.0)
    
    # Calculate base case NPV
    base_npv_result = calculate_npv_comparison(**base_params)
    base_npv_difference = base_npv_result['npv_difference']
    
    logger.info(f"Creating {len(y_range)}x{len(x_range)} sensitivity table for {y_metric} vs {x_metric}")
    
    # Generate all parameter combinations
    param_combinations = []
    for y_change in y_range:
        for x_change in x_range:
            param_combinations.append((x_change, y_change))
    
    # Calculate NPV for all combinations in parallel
    npv_results = _calculate_npv_combinations_parallel(
        base_params, x_metric, y_metric, param_combinations
    )
    
    # Organize results into 2D array
    npv_differences = []
    result_index = 0
    
    for y_change in y_range:
        row = []
        for x_change in x_range:
            # Use actual NPV difference for this parameter combination, not change from base
            npv_diff = npv_results[result_index]
            row.append(npv_diff)
            result_index += 1
        npv_differences.append(row)
    
    calculation_time = time.time() - start_time
    
    return {
        'x_metric': x_metric,
        'y_metric': y_metric,
        'x_metric_display': AVAILABLE_METRICS[x_metric],
        'y_metric_display': AVAILABLE_METRICS[y_metric],
        'x_values': x_range,
        'y_values': y_range,
        'x_actual_value': x_actual_value,
        'y_actual_value': y_actual_value,
        'npv_differences': npv_differences,
        'base_npv_difference': base_npv_difference,
        'calculation_time': calculation_time,
        'table_size': f"{len(y_range)}×{len(x_range)}"
    }


def _calculate_npv_combinations_parallel(
    base_params: Dict[str, float],
    x_metric: str,
    y_metric: str, 
    combinations: List[Tuple[float, float]]
) -> List[float]:
    """Calculate NPV for all parameter combinations in parallel."""
    
    npv_results = [0.0] * len(combinations)
    
    def calculate_combination_npv(index_and_combo):
        index, (x_change, y_change) = index_and_combo
        try:
            # Create modified parameters
            modified_params = base_params.copy()
            
            # Apply percentage changes
            x_base_value = base_params.get(x_metric, 0.0)
            y_base_value = base_params.get(y_metric, 0.0)
            
            modified_params[x_metric] = x_base_value + x_change
            modified_params[y_metric] = y_base_value + y_change
            
            # Calculate NPV
            npv_result = calculate_npv_comparison(**modified_params)
            return index, npv_result['npv_difference']
            
        except Exception as e:
            logger.error(f"NPV calculation failed for combination {index}: {e}")
            return index, 0.0
    
    # Execute calculations in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        indexed_combinations = list(enumerate(combinations))
        future_to_index = {
            executor.submit(calculate_combination_npv, combo): combo[0] 
            for combo in indexed_combinations
        }
        
        for future in as_completed(future_to_index, timeout=10.0):
            try:
                index, npv_value = future.result(timeout=0.1)
                npv_results[index] = npv_value
            except Exception as e:
                index = future_to_index[future]
                logger.error(f"Failed to get result for combination {index}: {e}")
                npv_results[index] = 0.0
    
    return npv_results


def format_2d_sensitivity_for_streamlit(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format two-dimensional sensitivity table result for Streamlit display.
    
    Args:
        result: Result from calculate_2d_sensitivity_analysis
        
    Returns:
        Dictionary with formatted data for Streamlit tables
    """
    
    # Create column headers with actual values
    x_headers = []
    for i, x_change in enumerate(result['x_values']):
        if x_change == 0.0:
            header = f"{result['x_actual_value']:.1f}%"
        else:
            actual_x_value = result['x_actual_value'] + x_change
            header = f"{actual_x_value:.1f}%"
        x_headers.append(header)
    
    # Create change indicators for headers
    x_change_indicators = []
    for x_change in result['x_values']:
        if x_change == 0.0:
            x_change_indicators.append("(0%)")
        else:
            x_change_indicators.append(f"({x_change:+.1f}%)")
    
    # Create table data
    table_data = []
    
    for i, y_change in enumerate(result['y_values']):
        # Row label with actual value
        if y_change == 0.0:
            row_label = f"{result['y_actual_value']:.1f}%"
            change_indicator = "(0%)"
        else:
            actual_y_value = result['y_actual_value'] + y_change
            row_label = f"{actual_y_value:.1f}%"
            change_indicator = f"({y_change:+.1f}%)"
        
        # Create row data
        row = {
            'y_label': row_label,
            'y_change': change_indicator
        }
        
        # Add NPV differences for each column
        for j, x_change in enumerate(result['x_values']):
            npv_diff = result['npv_differences'][i][j]
            
            # Format currency
            if abs(npv_diff) >= 1000:
                formatted_val = f"${npv_diff/1000:,.0f}K"
            else:
                formatted_val = f"${npv_diff:,.0f}"
            
            row[f'col_{j}'] = formatted_val
            row[f'col_{j}_raw'] = npv_diff  # Keep raw value for sorting/filtering
        
        table_data.append(row)
    
    return {
        'table_data': table_data,
        'x_headers': x_headers,
        'x_change_indicators': x_change_indicators,
        'x_metric_display': result['x_metric_display'],
        'y_metric_display': result['y_metric_display'],
        'base_npv': f"${result['base_npv_difference']:,.0f}",
        'calculation_time': f"{result['calculation_time']:.2f}s",
        'table_size': result['table_size'],
        'num_columns': len(result['x_values']),
        'num_rows': len(result['y_values'])
    }


def get_available_sensitivity_metrics() -> Dict[str, str]:
    """Get list of available metrics for sensitivity analysis selection."""
    return {
        'rent_increase_rate': 'Rent Increase Rate',
        'interest_rate': 'Interest Rate', 
        'inflation_rate': 'Inflation Rate',
        'market_appreciation_rate': 'Market Appreciation Rate'
    }


# Backward compatibility function to replace the old sensitivity analysis
def calculate_sensitivity_analysis(
    base_params: Dict,
    sensitivity_params: Dict[str, List[float]]
) -> Dict[str, Dict[str, float]]:
    """
    DEPRECATED: Legacy one-dimensional sensitivity analysis function.
    
    This function maintains backward compatibility but now uses the new
    two-dimensional analysis for better insights.
    
    For new implementations, use calculate_2d_sensitivity_analysis() instead.
    """
    import warnings
    warnings.warn(
        "calculate_sensitivity_analysis is deprecated. Use calculate_2d_sensitivity_analysis() for better insights.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # If only one parameter is provided, create a simple analysis
    if len(sensitivity_params) == 1:
        param_name = list(sensitivity_params.keys())[0]
        test_values = sensitivity_params[param_name]
        
        results = {}
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
    
    else:
        # For multiple parameters, suggest using 2D analysis
        logger.warning("Multiple parameter sensitivity analysis detected. Consider using calculate_2d_sensitivity_analysis() for better insights.")
        
        # Return simplified results for backward compatibility
        results = {}
        for param_name, test_values in sensitivity_params.items():
            param_results = {}
            
            for test_value in test_values:
                modified_params = base_params.copy()
                modified_params[param_name] = test_value
                
                try:
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