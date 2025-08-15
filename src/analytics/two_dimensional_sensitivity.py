"""
Two-Dimensional Sensitivity Analysis - Interactive Table Generator

Creates sensitivity tables where users can select X and Y axis metrics
and see NPV differences across various parameter combinations.

Features:
- Interactive metric selection (rent increase rate, interest rate, inflation, market appreciation rate)
- Customizable percentage change ranges
- High-performance parallel calculation
- Table format optimized for dashboard display
"""

import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from ..shared.interfaces import AnalyticsEngine
from ..calculations.npv_analysis import calculate_npv_comparison
from .input_validation import validate_and_sanitize_base_params, ValidationError, SecurityError

logger = logging.getLogger(__name__)


@dataclass
class TwoDimensionalSensitivityConfig:
    """Configuration for two-dimensional sensitivity analysis"""
    max_workers: int = 4
    timeout_seconds: float = 10.0
    default_x_range: List[float] = None
    default_y_range: List[float] = None
    
    def __post_init__(self):
        if self.default_x_range is None:
            self.default_x_range = [-2.0, -1.0, 0.0, 1.0, 2.0]  # % changes
        if self.default_y_range is None:
            self.default_y_range = [-2.0, -1.0, 0.0, 1.0, 2.0]  # % changes


@dataclass
class SensitivityTableResult:
    """Result of two-dimensional sensitivity analysis"""
    x_metric: str
    y_metric: str
    x_values: List[float]
    y_values: List[float]
    npv_differences: List[List[float]]  # 2D array of NPV differences
    base_npv_difference: float
    calculation_time: float
    x_label: str
    y_label: str


class TwoDimensionalSensitivityEngine:
    """
    Two-dimensional sensitivity analysis engine for interactive tables.
    
    Allows users to select any two metrics and see NPV impact across 
    various percentage changes in both metrics simultaneously.
    """
    
    # Available metrics for analysis
    AVAILABLE_METRICS = {
        'rent_increase_rate': {
            'param_name': 'rent_increase_rate',
            'display_name': 'Rent Increase Rate',
            'unit': '%',
            'base_range': [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0]
        },
        'interest_rate': {
            'param_name': 'interest_rate', 
            'display_name': 'Interest Rate',
            'unit': '%',
            'base_range': [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0]
        },
        'inflation_rate': {
            'param_name': 'inflation_rate',
            'display_name': 'Inflation Rate', 
            'unit': '%',
            'base_range': [-1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
        },
        'market_appreciation_rate': {
            'param_name': 'market_appreciation_rate',
            'display_name': 'Market Appreciation Rate',
            'unit': '%', 
            'base_range': [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0]
        }
    }
    
    def __init__(self, config: Optional[TwoDimensionalSensitivityConfig] = None):
        self.config = config or TwoDimensionalSensitivityConfig()
        # LRU cache with size limit to prevent memory leaks
        self._table_cache = {}
        self._cache_lock = threading.Lock()
        self._cache_max_size = 50  # Maximum cached tables
        self._cache_access_order = []  # Track access order for LRU
    
    def create_sensitivity_table(
        self,
        base_params: Dict[str, float],
        x_metric: str,
        y_metric: str,
        x_range: Optional[List[float]] = None,
        y_range: Optional[List[float]] = None
    ) -> SensitivityTableResult:
        """
        Create two-dimensional sensitivity table.
        
        Args:
            base_params: Base case parameters for NPV calculation
            x_metric: Metric for X-axis (column headers)
            y_metric: Metric for Y-axis (row headers) 
            x_range: List of percentage changes for X-axis (e.g., [-2.0, 0.0, 2.0])
            y_range: List of percentage changes for Y-axis
            
        Returns:
            SensitivityTableResult with 2D NPV difference table
        """
        start_time = time.time()
        
        # Validate and sanitize inputs
        try:
            sanitized_params = validate_and_sanitize_base_params(base_params)
        except (ValidationError, SecurityError) as e:
            logger.error(f"Input validation failed: {e}")
            raise ValueError(f"Invalid input parameters: {e}")
        
        # Validate metrics
        if x_metric not in self.AVAILABLE_METRICS:
            raise ValueError(f"Invalid X metric: {x_metric}. Available: {list(self.AVAILABLE_METRICS.keys())}")
        if y_metric not in self.AVAILABLE_METRICS:
            raise ValueError(f"Invalid Y metric: {y_metric}. Available: {list(self.AVAILABLE_METRICS.keys())}")
        if x_metric == y_metric:
            raise ValueError("X and Y metrics must be different")
        
        # Use default ranges if not provided
        if x_range is None:
            x_range = self.AVAILABLE_METRICS[x_metric]['base_range']
        if y_range is None:
            y_range = self.AVAILABLE_METRICS[y_metric]['base_range']
        
        # Validate ranges
        x_range = self._validate_range(x_range, "X-axis")
        y_range = self._validate_range(y_range, "Y-axis")
        
        # Check cache first
        cache_key = self._get_cache_key(sanitized_params, x_metric, y_metric, x_range, y_range)
        with self._cache_lock:
            if cache_key in self._table_cache:
                cached_result = self._table_cache[cache_key]
                # Update access order for LRU
                self._cache_access_order.remove(cache_key)
                self._cache_access_order.append(cache_key)
                logger.info(f"Sensitivity table from cache in {time.time() - start_time:.3f}s")
                return cached_result
        
        logger.info(f"Creating {len(y_range)}x{len(x_range)} sensitivity table for {y_metric} vs {x_metric}")
        
        # Ensure required parameters
        base_params = self._ensure_required_params(sanitized_params)
        
        # Calculate base case NPV
        base_npv_result = calculate_npv_comparison(**base_params)
        base_npv_difference = base_npv_result['npv_difference']
        
        # Generate all parameter combinations
        param_combinations = []
        for y_change in y_range:
            for x_change in x_range:
                param_combinations.append((x_change, y_change))
        
        # Calculate NPV for all combinations in parallel
        npv_results = self._calculate_npv_combinations_parallel(
            base_params, x_metric, y_metric, param_combinations
        )
        
        # Organize results into 2D array
        npv_differences = []
        result_index = 0
        
        for y_change in y_range:
            row = []
            for x_change in x_range:
                npv_diff = npv_results[result_index] - base_npv_difference
                row.append(npv_diff)
                result_index += 1
            npv_differences.append(row)
        
        # Create result
        result = SensitivityTableResult(
            x_metric=x_metric,
            y_metric=y_metric,
            x_values=x_range,
            y_values=y_range,
            npv_differences=npv_differences,
            base_npv_difference=base_npv_difference,
            calculation_time=time.time() - start_time,
            x_label=self.AVAILABLE_METRICS[x_metric]['display_name'],
            y_label=self.AVAILABLE_METRICS[y_metric]['display_name']
        )
        
        # Cache results with LRU management
        with self._cache_lock:
            if len(self._table_cache) >= self._cache_max_size:
                if self._cache_access_order:
                    oldest_key = self._cache_access_order.pop(0)
                    self._table_cache.pop(oldest_key, None)
                    logger.debug(f"Evicted sensitivity table cache entry")
            
            self._table_cache[cache_key] = result
            self._cache_access_order.append(cache_key)
        
        logger.info(f"Sensitivity table completed in {result.calculation_time:.3f}s")
        return result
    
    def _calculate_npv_combinations_parallel(
        self,
        base_params: Dict[str, float],
        x_metric: str,
        y_metric: str, 
        combinations: List[Tuple[float, float]]
    ) -> List[float]:
        """Calculate NPV for all parameter combinations in parallel."""
        
        x_param_name = self.AVAILABLE_METRICS[x_metric]['param_name']
        y_param_name = self.AVAILABLE_METRICS[y_metric]['param_name']
        
        npv_results = [0.0] * len(combinations)
        
        def calculate_combination_npv(index_and_combo):
            index, (x_change, y_change) = index_and_combo
            try:
                # Create modified parameters
                modified_params = base_params.copy()
                
                # Apply percentage changes
                x_base_value = base_params.get(x_param_name, 0.0)
                y_base_value = base_params.get(y_param_name, 0.0)
                
                modified_params[x_param_name] = x_base_value + x_change
                modified_params[y_param_name] = y_base_value + y_change
                
                # Calculate NPV
                npv_result = calculate_npv_comparison(**modified_params)
                return index, npv_result['npv_difference']
                
            except Exception as e:
                logger.error(f"NPV calculation failed for combination {index}: {e}")
                return index, 0.0
        
        # Execute calculations in parallel
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            indexed_combinations = list(enumerate(combinations))
            future_to_index = {
                executor.submit(calculate_combination_npv, combo): combo[0] 
                for combo in indexed_combinations
            }
            
            for future in as_completed(future_to_index, timeout=self.config.timeout_seconds):
                try:
                    index, npv_value = future.result(timeout=0.1)
                    npv_results[index] = npv_value
                except Exception as e:
                    index = future_to_index[future]
                    logger.error(f"Failed to get result for combination {index}: {e}")
                    npv_results[index] = 0.0
        
        return npv_results
    
    def _validate_range(self, range_values: List[float], axis_name: str) -> List[float]:
        """Validate and sanitize range values."""
        if not isinstance(range_values, (list, tuple)):
            raise ValueError(f"{axis_name} range must be a list or tuple")
        
        if len(range_values) == 0:
            raise ValueError(f"{axis_name} range cannot be empty")
        
        if len(range_values) > 10:
            raise ValueError(f"{axis_name} range cannot have more than 10 values")
        
        # Sanitize and validate each value
        sanitized_range = []
        for i, val in enumerate(range_values):
            try:
                float_val = float(val)
                if abs(float_val) > 20.0:  # Reasonable limit for percentage changes
                    raise ValueError(f"{axis_name} range value {float_val} exceeds ±20% limit")
                sanitized_range.append(float_val)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid {axis_name} range value at index {i}: {val}")
        
        return sorted(sanitized_range)  # Sort for consistent display
    
    def _ensure_required_params(self, base_params: Dict[str, float]) -> Dict[str, float]:
        """Ensure all required parameters are present with defaults."""
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
                
        return complete_params
    
    def _get_cache_key(
        self,
        base_params: Dict[str, float],
        x_metric: str,
        y_metric: str,
        x_range: List[float],
        y_range: List[float]
    ) -> str:
        """Generate cache key for table parameters."""
        import hashlib
        
        # Sort parameters for consistent key
        param_str = ','.join(f"{k}:{v}" for k, v in sorted(base_params.items()))
        config_str = f"{x_metric}:{y_metric}:{x_range}:{y_range}"
        
        # Use SHA-256 for secure hashing
        full_str = f"{param_str}#{config_str}"
        return hashlib.sha256(full_str.encode()).hexdigest()
    
    def get_available_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get list of available metrics for selection."""
        return self.AVAILABLE_METRICS.copy()
    
    def format_table_for_display(self, result: SensitivityTableResult, format_currency: bool = True) -> Dict[str, Any]:
        """Format sensitivity table result for dashboard display."""
        
        # Format NPV differences for display
        formatted_table = []
        
        for i, y_val in enumerate(result.y_values):
            row = {'y_value': f"{y_val:+.1f}%"}
            for j, x_val in enumerate(result.x_values):
                npv_diff = result.npv_differences[i][j]
                if format_currency:
                    if abs(npv_diff) >= 1000:
                        formatted_val = f"${npv_diff/1000:,.0f}K"
                    else:
                        formatted_val = f"${npv_diff:,.0f}"
                else:
                    formatted_val = f"{npv_diff:,.0f}"
                row[f"x_{j}"] = formatted_val
            formatted_table.append(row)
        
        return {
            'table_data': formatted_table,
            'x_headers': [f"{val:+.1f}%" for val in result.x_values],
            'x_label': result.x_label,
            'y_label': result.y_label,
            'base_npv': f"${result.base_npv_difference:,.0f}",
            'calculation_time': f"{result.calculation_time:.2f}s",
            'table_size': f"{len(result.y_values)}×{len(result.x_values)}"
        }


# Convenience functions

def create_quick_sensitivity_table(
    base_params: Dict[str, float],
    x_metric: str = 'interest_rate',
    y_metric: str = 'market_appreciation_rate'
) -> SensitivityTableResult:
    """
    Convenience function for quick sensitivity table creation.
    
    Args:
        base_params: Base case parameters
        x_metric: X-axis metric (default: interest_rate)
        y_metric: Y-axis metric (default: market_appreciation_rate)
        
    Returns:
        SensitivityTableResult with 2D analysis
    """
    engine = TwoDimensionalSensitivityEngine()
    return engine.create_sensitivity_table(base_params, x_metric, y_metric)


if __name__ == "__main__":
    # Example usage
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
    
    engine = TwoDimensionalSensitivityEngine()
    
    # Create sensitivity table
    result = engine.create_sensitivity_table(
        test_params,
        x_metric='interest_rate',
        y_metric='market_appreciation_rate',
        x_range=[-2.0, -1.0, 0.0, 1.0, 2.0],
        y_range=[-2.0, -1.0, 0.0, 1.0, 2.0]
    )
    
    # Format for display
    display_data = engine.format_table_for_display(result)
    
    print("✅ Two-Dimensional Sensitivity Table Created")
    print(f"Table size: {display_data['table_size']}")
    print(f"Calculation time: {display_data['calculation_time']}")
    print(f"X-axis: {display_data['x_label']}")
    print(f"Y-axis: {display_data['y_label']}")