"""
Comprehensive Input Validation and Sanitization for Analytics Engine

Security-focused input validation to prevent:
- Code injection attacks
- Resource exhaustion attacks
- Invalid data corruption
- Memory exhaustion
- Infinite loops and DoS attacks

Features:
- Type validation and coercion
- Range validation with safety limits
- Sanitization of harmful inputs
- Resource consumption limits
- Statistical validation
- Business logic validation
"""

import math
import re
import logging
from typing import Any, Dict, List, Union, Optional, Tuple
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class SecurityError(Exception):
    """Custom exception for security-related validation failures"""
    pass


class InputSanitizer:
    """Comprehensive input sanitization and validation"""
    
    # Security limits
    MAX_ITERATIONS = 100000  # Maximum Monte Carlo iterations
    MAX_ANALYSIS_PERIOD = 100  # Maximum analysis period in years
    MAX_PARAMETER_COUNT = 50  # Maximum number of parameters
    MAX_STRING_LENGTH = 1000  # Maximum string length
    MAX_LIST_LENGTH = 1000  # Maximum list length
    MAX_NUMERIC_VALUE = 1e12  # Maximum numeric value
    MIN_NUMERIC_VALUE = -1e12  # Minimum numeric value
    
    # Business logic limits
    MIN_PURCHASE_PRICE = 1000  # $1,000 minimum
    MAX_PURCHASE_PRICE = 1e9  # $1B maximum
    MIN_RENT = 100  # $100/year minimum
    MAX_RENT = 1e6  # $1M/year maximum
    MIN_INTEREST_RATE = 0.01  # 0.01% minimum
    MAX_INTEREST_RATE = 50.0  # 50% maximum
    MIN_APPRECIATION_RATE = -20.0  # -20% minimum
    MAX_APPRECIATION_RATE = 50.0  # 50% maximum
    MIN_ANALYSIS_PERIOD = 1  # 1 year minimum
    MAX_LOAN_TERM = 100  # 100 years maximum
    MIN_DOWN_PAYMENT_PCT = 0.0  # 0% minimum
    MAX_DOWN_PAYMENT_PCT = 100.0  # 100% maximum
    
    @classmethod
    def sanitize_string(cls, value: Any, max_length: Optional[int] = None) -> str:
        """
        Sanitize string input to prevent injection attacks.
        
        Args:
            value: Input value to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            SecurityError: If input contains harmful content
            ValidationError: If input is invalid
        """
        if value is None:
            return ""
            
        # Convert to string
        try:
            str_value = str(value).strip()
        except Exception as e:
            raise ValidationError(f"Cannot convert to string: {e}")
        
        # Check length
        max_len = max_length or cls.MAX_STRING_LENGTH
        if len(str_value) > max_len:
            raise SecurityError(f"String too long: {len(str_value)} > {max_len}")
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'<script.*?>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'data:.*?base64',  # Data URLs
            r'eval\s*\(',  # Eval functions
            r'exec\s*\(',  # Exec functions
            r'import\s+\w+',  # Import statements
            r'__.*__',  # Dunder methods
            r'\..*\(',  # Method calls
            r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]'  # Control characters
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, str_value, re.IGNORECASE):
                raise SecurityError(f"Potentially harmful content detected: {pattern}")
        
        return str_value
    
    @classmethod
    def sanitize_numeric(
        cls, 
        value: Any, 
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        allow_none: bool = False,
        param_name: str = "parameter"
    ) -> float:
        """
        Sanitize numeric input with range validation.
        
        Args:
            value: Input value to sanitize
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            allow_none: Whether None values are allowed
            param_name: Parameter name for error messages
            
        Returns:
            Sanitized numeric value
            
        Raises:
            ValidationError: If value is invalid
            SecurityError: If value is potentially harmful
        """
        if value is None:
            if allow_none:
                return None
            else:
                raise ValidationError(f"{param_name} cannot be None")
        
        # Handle string inputs
        if isinstance(value, str):
            # Check for dangerous content
            if re.search(r'[a-zA-Z]', value) and value.lower() not in ['inf', '-inf', 'nan']:
                raise SecurityError(f"Non-numeric content in {param_name}: {value}")
            
            try:
                # Use Decimal for safer parsing
                decimal_value = Decimal(value.strip())
                value = float(decimal_value)
            except (InvalidOperation, ValueError) as e:
                raise ValidationError(f"Invalid numeric value for {param_name}: {value}")
        
        # Convert to float
        try:
            numeric_value = float(value)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Cannot convert {param_name} to numeric: {value}")
        
        # Check for dangerous values
        if math.isnan(numeric_value):
            raise SecurityError(f"NaN value not allowed for {param_name}")
        
        if math.isinf(numeric_value):
            raise SecurityError(f"Infinite value not allowed for {param_name}")
        
        # Apply global limits first
        global_min = min_val if min_val is not None else cls.MIN_NUMERIC_VALUE
        global_max = max_val if max_val is not None else cls.MAX_NUMERIC_VALUE
        
        if numeric_value < global_min:
            raise ValidationError(f"{param_name} too small: {numeric_value} < {global_min}")
        
        if numeric_value > global_max:
            raise ValidationError(f"{param_name} too large: {numeric_value} > {global_max}")
        
        return numeric_value
    
    @classmethod
    def sanitize_integer(
        cls,
        value: Any,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
        allow_none: bool = False,
        param_name: str = "parameter"
    ) -> int:
        """Sanitize integer input with range validation."""
        numeric_value = cls.sanitize_numeric(
            value, min_val, max_val, allow_none, param_name
        )
        
        if numeric_value is None and allow_none:
            return None
        
        try:
            return int(numeric_value)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Cannot convert {param_name} to integer: {numeric_value}")
    
    @classmethod
    def sanitize_percentage(
        cls,
        value: Any,
        min_val: float = 0.0,
        max_val: float = 100.0,
        param_name: str = "percentage"
    ) -> float:
        """Sanitize percentage input (0-100 range)."""
        return cls.sanitize_numeric(value, min_val, max_val, False, param_name)
    
    @classmethod
    def sanitize_rate(
        cls,
        value: Any,
        min_val: float = -50.0,
        max_val: float = 100.0,
        param_name: str = "rate"
    ) -> float:
        """Sanitize rate input (typically -50% to 100%)."""
        return cls.sanitize_numeric(value, min_val, max_val, False, param_name)
    
    @classmethod
    def sanitize_list(
        cls,
        value: Any,
        max_length: Optional[int] = None,
        item_validator: Optional[callable] = None,
        param_name: str = "list"
    ) -> List[Any]:
        """
        Sanitize list input with length and content validation.
        
        Args:
            value: Input value to sanitize
            max_length: Maximum allowed list length
            item_validator: Function to validate each item
            param_name: Parameter name for error messages
            
        Returns:
            Sanitized list
        """
        if value is None:
            return []
        
        # Convert to list if needed
        if not isinstance(value, (list, tuple)):
            raise ValidationError(f"{param_name} must be a list or tuple")
        
        # Check length
        max_len = max_length or cls.MAX_LIST_LENGTH
        if len(value) > max_len:
            raise SecurityError(f"List too long: {len(value)} > {max_len}")
        
        # Validate items
        sanitized_list = []
        for i, item in enumerate(value):
            try:
                if item_validator:
                    sanitized_item = item_validator(item)
                else:
                    sanitized_item = item
                sanitized_list.append(sanitized_item)
            except Exception as e:
                raise ValidationError(f"Invalid item {i} in {param_name}: {e}")
        
        return sanitized_list
    
    @classmethod
    def sanitize_dict(
        cls,
        value: Any,
        max_items: Optional[int] = None,
        key_validator: Optional[callable] = None,
        value_validator: Optional[callable] = None,
        param_name: str = "dictionary"
    ) -> Dict[Any, Any]:
        """
        Sanitize dictionary input with size and content validation.
        
        Args:
            value: Input value to sanitize
            max_items: Maximum allowed dictionary size
            key_validator: Function to validate each key
            value_validator: Function to validate each value
            param_name: Parameter name for error messages
            
        Returns:
            Sanitized dictionary
        """
        if value is None:
            return {}
        
        if not isinstance(value, dict):
            raise ValidationError(f"{param_name} must be a dictionary")
        
        # Check size
        max_size = max_items or cls.MAX_PARAMETER_COUNT
        if len(value) > max_size:
            raise SecurityError(f"Dictionary too large: {len(value)} > {max_size}")
        
        # Validate items
        sanitized_dict = {}
        for key, val in value.items():
            try:
                # Validate key
                if key_validator:
                    sanitized_key = key_validator(key)
                else:
                    sanitized_key = cls.sanitize_string(key, 100)  # Limit key length
                
                # Validate value
                if value_validator:
                    sanitized_value = value_validator(val)
                else:
                    sanitized_value = val
                
                sanitized_dict[sanitized_key] = sanitized_value
                
            except Exception as e:
                raise ValidationError(f"Invalid item '{key}' in {param_name}: {e}")
        
        return sanitized_dict


class AnalyticsInputValidator:
    """Specialized validator for analytics engine inputs"""
    
    @staticmethod
    def validate_base_parameters(params: Dict[str, Any]) -> Dict[str, float]:
        """
        Validate and sanitize base analysis parameters.
        
        Args:
            params: Dictionary of analysis parameters
            
        Returns:
            Sanitized parameters dictionary
            
        Raises:
            ValidationError: If parameters are invalid
            SecurityError: If parameters are potentially harmful
        """
        if not isinstance(params, dict):
            raise ValidationError("Parameters must be a dictionary")
        
        # Check parameter count
        if len(params) > InputSanitizer.MAX_PARAMETER_COUNT:
            raise SecurityError(f"Too many parameters: {len(params)} > {InputSanitizer.MAX_PARAMETER_COUNT}")
        
        sanitized_params = {}
        
        # Required parameters with validation
        param_validators = {
            'purchase_price': lambda x: InputSanitizer.sanitize_numeric(
                x, InputSanitizer.MIN_PURCHASE_PRICE, InputSanitizer.MAX_PURCHASE_PRICE, 
                False, "purchase_price"
            ),
            'current_annual_rent': lambda x: InputSanitizer.sanitize_numeric(
                x, InputSanitizer.MIN_RENT, InputSanitizer.MAX_RENT, 
                False, "current_annual_rent"
            ),
            'down_payment_pct': lambda x: InputSanitizer.sanitize_percentage(
                x, InputSanitizer.MIN_DOWN_PAYMENT_PCT, InputSanitizer.MAX_DOWN_PAYMENT_PCT,
                "down_payment_pct"
            ),
            'interest_rate': lambda x: InputSanitizer.sanitize_rate(
                x, InputSanitizer.MIN_INTEREST_RATE, InputSanitizer.MAX_INTEREST_RATE,
                "interest_rate"
            ),
            'market_appreciation_rate': lambda x: InputSanitizer.sanitize_rate(
                x, InputSanitizer.MIN_APPRECIATION_RATE, InputSanitizer.MAX_APPRECIATION_RATE,
                "market_appreciation_rate"
            ),
            'rent_increase_rate': lambda x: InputSanitizer.sanitize_rate(
                x, InputSanitizer.MIN_APPRECIATION_RATE, InputSanitizer.MAX_APPRECIATION_RATE,
                "rent_increase_rate"
            ),
            'cost_of_capital': lambda x: InputSanitizer.sanitize_rate(
                x, InputSanitizer.MIN_INTEREST_RATE, InputSanitizer.MAX_INTEREST_RATE,
                "cost_of_capital"
            ),
            'analysis_period': lambda x: InputSanitizer.sanitize_integer(
                x, InputSanitizer.MIN_ANALYSIS_PERIOD, InputSanitizer.MAX_ANALYSIS_PERIOD,
                False, "analysis_period"
            ),
            'loan_term': lambda x: InputSanitizer.sanitize_integer(
                x, 1, InputSanitizer.MAX_LOAN_TERM, False, "loan_term"
            )
        }
        
        # Optional parameters with defaults
        optional_validators = {
            'transaction_costs': lambda x: InputSanitizer.sanitize_numeric(
                x, 0, InputSanitizer.MAX_PURCHASE_PRICE, True, "transaction_costs"
            ),
            'property_tax_rate': lambda x: InputSanitizer.sanitize_rate(
                x, 0, 10, False, "property_tax_rate"
            ),
            'insurance_cost': lambda x: InputSanitizer.sanitize_numeric(
                x, 0, 1000000, False, "insurance_cost"
            ),
            'annual_maintenance': lambda x: InputSanitizer.sanitize_numeric(
                x, 0, 1000000, False, "annual_maintenance"
            ),
            'property_management': lambda x: InputSanitizer.sanitize_numeric(
                x, 0, 100000, False, "property_management"
            )
        }
        
        # Validate each parameter
        for param_name, validator in param_validators.items():
            if param_name in params:
                try:
                    sanitized_params[param_name] = validator(params[param_name])
                except Exception as e:
                    raise ValidationError(f"Invalid {param_name}: {e}")
            else:
                # Set reasonable defaults for missing required parameters
                defaults = {
                    'purchase_price': 500000,
                    'current_annual_rent': 24000,
                    'down_payment_pct': 20.0,
                    'interest_rate': 5.0,
                    'market_appreciation_rate': 3.0,
                    'rent_increase_rate': 3.0,
                    'cost_of_capital': 8.0,
                    'analysis_period': 20,
                    'loan_term': 20
                }
                if param_name in defaults:
                    sanitized_params[param_name] = defaults[param_name]
        
        # Validate optional parameters
        for param_name, validator in optional_validators.items():
            if param_name in params:
                try:
                    result = validator(params[param_name])
                    if result is not None:
                        sanitized_params[param_name] = result
                except Exception as e:
                    logger.warning(f"Invalid optional parameter {param_name}: {e}")
        
        # Business logic validation
        AnalyticsInputValidator._validate_business_logic(sanitized_params)
        
        return sanitized_params
    
    @staticmethod
    def validate_monte_carlo_iterations(iterations: Any) -> int:
        """Validate Monte Carlo iteration count."""
        sanitized_iterations = InputSanitizer.sanitize_integer(
            iterations, 100, InputSanitizer.MAX_ITERATIONS, False, "iterations"
        )
        
        # Additional business logic
        if sanitized_iterations < 1000:
            logger.warning(f"Low iteration count may produce inaccurate results: {sanitized_iterations}")
        
        return sanitized_iterations
    
    @staticmethod
    def validate_distributions(distributions: Dict[str, Any]) -> Dict[str, Dict]:
        """Validate Monte Carlo distributions."""
        if not isinstance(distributions, dict):
            raise ValidationError("Distributions must be a dictionary")
        
        if len(distributions) == 0:
            raise ValidationError("At least one distribution must be specified")
        
        if len(distributions) > 20:  # Reasonable limit
            raise SecurityError(f"Too many distributions: {len(distributions)} > 20")
        
        valid_distributions = ['normal', 'uniform', 'triangular', 'lognormal', 'beta']
        sanitized_distributions = {}
        
        for var_name, config in distributions.items():
            # Sanitize variable name
            safe_var_name = InputSanitizer.sanitize_string(var_name, 50)
            
            if not isinstance(config, dict):
                raise ValidationError(f"Distribution config for {safe_var_name} must be a dictionary")
            
            # Validate distribution type
            dist_type = config.get('distribution', '').lower()
            if dist_type not in valid_distributions:
                raise ValidationError(f"Invalid distribution type: {dist_type}")
            
            # Validate parameters
            params = config.get('params', [])
            if not isinstance(params, (list, tuple)):
                raise ValidationError(f"Distribution parameters for {safe_var_name} must be a list")
            
            if len(params) > 10:  # Reasonable limit
                raise SecurityError(f"Too many distribution parameters: {len(params)} > 10")
            
            # Sanitize parameters
            sanitized_params = []
            for param in params:
                sanitized_param = InputSanitizer.sanitize_numeric(
                    param, -1e6, 1e6, False, f"distribution parameter for {safe_var_name}"
                )
                sanitized_params.append(sanitized_param)
            
            # Validate parameter count for distribution type
            min_params = {'normal': 2, 'uniform': 2, 'triangular': 3, 'lognormal': 2, 'beta': 4}
            if len(sanitized_params) < min_params.get(dist_type, 1):
                raise ValidationError(f"Insufficient parameters for {dist_type} distribution: {len(sanitized_params)} < {min_params[dist_type]}")
            
            sanitized_distributions[safe_var_name] = {
                'distribution': dist_type,
                'params': sanitized_params
            }
        
        return sanitized_distributions
    
    @staticmethod
    def validate_sensitivity_variables(variables: List[Any]) -> List:
        """Validate sensitivity analysis variables."""
        if not isinstance(variables, (list, tuple)):
            raise ValidationError("Variables must be a list")
        
        if len(variables) == 0:
            raise ValidationError("At least one variable must be specified")
        
        if len(variables) > 20:  # Reasonable limit
            raise SecurityError(f"Too many variables: {len(variables)} > 20")
        
        sanitized_variables = []
        for i, var in enumerate(variables):
            try:
                # Check if it's a SensitivityVariable object or dict
                if hasattr(var, 'name'):
                    # It's already a SensitivityVariable object
                    sanitized_variables.append(var)
                elif isinstance(var, dict):
                    # Convert dict to SensitivityVariable
                    from ..shared.interfaces import SensitivityVariable
                    
                    name = InputSanitizer.sanitize_string(var.get('name', f'var_{i}'), 50)
                    base_value = InputSanitizer.sanitize_numeric(var.get('base_value', 0), param_name=f"{name}_base_value")
                    min_value = InputSanitizer.sanitize_numeric(var.get('min_value', 0), param_name=f"{name}_min_value")
                    max_value = InputSanitizer.sanitize_numeric(var.get('max_value', 0), param_name=f"{name}_max_value")
                    step_size = InputSanitizer.sanitize_numeric(var.get('step_size', 1), 0.001, 1000, False, f"{name}_step_size")
                    unit = InputSanitizer.sanitize_string(var.get('unit', ''), 10)
                    description = InputSanitizer.sanitize_string(var.get('description', ''), 200)
                    
                    if min_value >= max_value:
                        raise ValidationError(f"min_value must be less than max_value for {name}")
                    
                    sanitized_var = SensitivityVariable(
                        name=name,
                        base_value=base_value,
                        min_value=min_value,
                        max_value=max_value,
                        step_size=step_size,
                        unit=unit,
                        description=description
                    )
                    sanitized_variables.append(sanitized_var)
                else:
                    raise ValidationError(f"Variable {i} must be a SensitivityVariable object or dictionary")
                    
            except Exception as e:
                raise ValidationError(f"Invalid variable {i}: {e}")
        
        return sanitized_variables
    
    @staticmethod
    def _validate_business_logic(params: Dict[str, float]) -> None:
        """Validate business logic constraints."""
        # Loan term should not exceed analysis period
        loan_term = params.get('loan_term', 20)
        analysis_period = params.get('analysis_period', 20)
        if loan_term > analysis_period * 2:  # Allow some flexibility
            logger.warning(f"Loan term ({loan_term}) is much longer than analysis period ({analysis_period})")
        
        # Down payment should be reasonable relative to purchase price
        purchase_price = params.get('purchase_price', 500000)
        down_payment_pct = params.get('down_payment_pct', 20)
        down_payment_amount = purchase_price * down_payment_pct / 100
        if down_payment_amount > purchase_price:
            raise ValidationError("Down payment cannot exceed purchase price")
        
        # Interest rate should be reasonable
        interest_rate = params.get('interest_rate', 5.0)
        if interest_rate > 30:
            logger.warning(f"Very high interest rate: {interest_rate}%")
        
        # Cost of capital should generally be higher than interest rate for leverage to make sense
        cost_of_capital = params.get('cost_of_capital', 8.0)
        if cost_of_capital <= interest_rate and down_payment_pct < 100:
            logger.warning(f"Cost of capital ({cost_of_capital}%) is not higher than interest rate ({interest_rate}%)")
        
        # Rent should be somewhat related to purchase price
        current_annual_rent = params.get('current_annual_rent', 24000)
        rent_to_price_ratio = current_annual_rent / purchase_price
        if rent_to_price_ratio < 0.01:  # Less than 1% rent yield
            logger.warning(f"Very low rent-to-price ratio: {rent_to_price_ratio:.2%}")
        elif rent_to_price_ratio > 0.20:  # More than 20% rent yield
            logger.warning(f"Very high rent-to-price ratio: {rent_to_price_ratio:.2%}")


# Utility functions for common validations

def validate_and_sanitize_base_params(params: Dict[str, Any]) -> Dict[str, float]:
    """Convenience function to validate base parameters."""
    return AnalyticsInputValidator.validate_base_parameters(params)


def validate_and_sanitize_monte_carlo_params(
    base_params: Dict[str, Any],
    distributions: Dict[str, Any],
    iterations: Any
) -> Tuple[Dict[str, float], Dict[str, Dict], int]:
    """Convenience function to validate Monte Carlo parameters."""
    sanitized_base = AnalyticsInputValidator.validate_base_parameters(base_params)
    sanitized_distributions = AnalyticsInputValidator.validate_distributions(distributions)
    sanitized_iterations = AnalyticsInputValidator.validate_monte_carlo_iterations(iterations)
    
    return sanitized_base, sanitized_distributions, sanitized_iterations


def validate_and_sanitize_sensitivity_params(
    base_params: Dict[str, Any],
    variables: List[Any]
) -> Tuple[Dict[str, float], List]:
    """Convenience function to validate sensitivity analysis parameters."""
    sanitized_base = AnalyticsInputValidator.validate_base_parameters(base_params)
    sanitized_variables = AnalyticsInputValidator.validate_sensitivity_variables(variables)
    
    return sanitized_base, sanitized_variables


if __name__ == "__main__":
    # Test validation
    test_params = {
        'purchase_price': '500000',  # String input
        'current_annual_rent': 24000,
        'down_payment_pct': 30.0,
        'interest_rate': 5.0,
        'market_appreciation_rate': 3.0,
        'rent_increase_rate': 3.0,
        'cost_of_capital': 8.0
    }
    
    try:
        sanitized = validate_and_sanitize_base_params(test_params)
        print("✅ Validation test passed")
        print(f"Sanitized parameters: {sanitized}")
    except Exception as e:
        print(f"❌ Validation test failed: {e}")