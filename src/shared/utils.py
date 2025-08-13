"""
Week 4 Shared Utilities
Common utility functions for all work trees

This module provides shared functionality that multiple work trees need,
ensuring consistency and reducing code duplication.
"""

import os
import sys
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import asdict, is_dataclass
import functools
import time

from .constants import (
    APP_NAME, APP_VERSION, 
    MIN_ACCURACY_THRESHOLD, 
    get_env_var, 
    is_debug_mode,
    get_cache_dir,
    get_log_dir
)


# ============================================================================
# Logging Utilities
# ============================================================================

def setup_logging(component_name: str, level: str = None) -> logging.Logger:
    """
    Set up logging for a component with standardized format
    
    Args:
        component_name: Name of the component (e.g., "analytics_engine")
        level: Log level override (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    if level is None:
        level = get_env_var("LOG_LEVEL", "INFO")
    
    logger = logging.getLogger(component_name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler for non-debug mode
        if not is_debug_mode():
            log_dir = get_log_dir()
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"{component_name}.log")
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    return logger


def log_execution_time(func):
    """Decorator to log function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            logger.info(f"{func.__name__} completed in {execution_time:.2f}ms")
            return result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} failed after {execution_time:.2f}ms: {e}")
            raise
    
    return wrapper


# ============================================================================
# Data Validation Utilities
# ============================================================================

def validate_numeric_input(
    value: Any, 
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    allow_zero: bool = True
) -> Tuple[bool, str]:
    """
    Validate numeric input with range checking
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        allow_zero: Whether zero is allowed
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        return False, "Must be a valid number"
    
    if not allow_zero and num_value == 0:
        return False, "Value cannot be zero"
    
    if min_value is not None and num_value < min_value:
        return False, f"Value must be at least {min_value}"
    
    if max_value is not None and num_value > max_value:
        return False, f"Value must be no more than {max_value}"
    
    return True, ""


def validate_percentage(value: Any) -> Tuple[bool, str]:
    """Validate percentage input (0-100)"""
    return validate_numeric_input(value, min_value=0, max_value=100)


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate that all required fields are present and not empty
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
    
    Returns:
        List of missing or invalid field names
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    return missing_fields


# ============================================================================
# Mathematical Utilities
# ============================================================================

def round_to_precision(value: float, precision: int = 2) -> float:
    """Round value to specified decimal places"""
    return round(value, precision)


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0 if new_value == 0 else float('inf')
    
    return ((new_value - old_value) / old_value) * 100


def is_approximately_equal(a: float, b: float, tolerance: float = MIN_ACCURACY_THRESHOLD) -> bool:
    """Check if two values are approximately equal within tolerance"""
    return abs(a - b) <= tolerance


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    if denominator == 0:
        return default
    return numerator / denominator


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value between min and max bounds"""
    return max(min_value, min(value, max_value))


# ============================================================================
# Data Serialization Utilities
# ============================================================================

def serialize_dataclass(obj: Any) -> Dict[str, Any]:
    """
    Serialize dataclass to dictionary, handling nested dataclasses
    
    Args:
        obj: Dataclass instance to serialize
    
    Returns:
        Dictionary representation
    """
    if is_dataclass(obj):
        result = {}
        for field_name, field_value in asdict(obj).items():
            if isinstance(field_value, datetime):
                result[field_name] = field_value.isoformat()
            elif is_dataclass(field_value):
                result[field_name] = serialize_dataclass(field_value)
            elif isinstance(field_value, list) and field_value and is_dataclass(field_value[0]):
                result[field_name] = [serialize_dataclass(item) for item in field_value]
            else:
                result[field_name] = field_value
        return result
    return obj


def serialize_to_json(obj: Any, indent: int = 2) -> str:
    """Serialize object to JSON string with proper handling of complex types"""
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif is_dataclass(obj):
            return serialize_dataclass(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    return json.dumps(obj, default=json_serializer, indent=indent)


# ============================================================================
# Caching Utilities
# ============================================================================

def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from function arguments
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        MD5 hash string for cache key
    """
    # Create a string representation of all arguments
    cache_string = str(args) + str(sorted(kwargs.items()))
    
    # Generate MD5 hash
    return hashlib.md5(cache_string.encode()).hexdigest()


def is_cache_valid(cache_timestamp: datetime, max_age_hours: float = 24.0) -> bool:
    """
    Check if cached data is still valid based on age
    
    Args:
        cache_timestamp: When data was cached
        max_age_hours: Maximum age in hours
    
    Returns:
        True if cache is still valid
    """
    if cache_timestamp is None:
        return False
    
    age = datetime.now() - cache_timestamp
    return age.total_seconds() < (max_age_hours * 3600)


def create_cache_path(cache_key: str, cache_type: str = "general") -> str:
    """
    Create full path for cache file
    
    Args:
        cache_key: Unique cache key
        cache_type: Type of cache (e.g., "market_data", "calculations")
    
    Returns:
        Full path to cache file
    """
    cache_dir = get_cache_dir()
    type_dir = os.path.join(cache_dir, cache_type)
    os.makedirs(type_dir, exist_ok=True)
    
    return os.path.join(type_dir, f"{cache_key}.cache")


# ============================================================================
# Performance Monitoring Utilities
# ============================================================================

class PerformanceTimer:
    """Context manager for measuring execution time"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.logger = logging.getLogger("performance")
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        execution_time = (self.end_time - self.start_time) * 1000  # Convert to ms
        
        if exc_type is None:
            self.logger.info(f"{self.operation_name} completed in {execution_time:.2f}ms")
        else:
            self.logger.error(f"{self.operation_name} failed after {execution_time:.2f}ms")
    
    @property
    def execution_time_ms(self) -> float:
        """Get execution time in milliseconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0


def memory_usage_mb() -> float:
    """Get current memory usage in MB"""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        # Fallback if psutil not available
        return 0.0


# ============================================================================
# Error Handling Utilities
# ============================================================================

class RetryableError(Exception):
    """Exception that can be retried"""
    pass


def retry_on_failure(max_attempts: int = 3, delay_seconds: float = 1.0):
    """
    Decorator to retry function on failure
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Delay between retries
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except RetryableError as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay_seconds)
                        continue
                    else:
                        raise
                except Exception as e:
                    # Don't retry on non-retryable errors
                    raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def safe_execute(func, default_return=None, log_errors=True):
    """
    Execute function safely, returning default value on error
    
    Args:
        func: Function to execute
        default_return: Value to return on error
        log_errors: Whether to log errors
    
    Returns:
        Function result or default value
    """
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger = logging.getLogger("error_handler")
            logger.error(f"Safe execution failed: {e}")
        return default_return


# ============================================================================
# String Utilities
# ============================================================================

def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """Format amount as currency with proper commas and decimals"""
    return f"{currency_symbol}{amount:,.2f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format value as percentage"""
    return f"{value:.{decimal_places}f}%"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length with suffix"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


# ============================================================================
# System Information Utilities
# ============================================================================

def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging and monitoring"""
    return {
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "python_version": sys.version,
        "platform": sys.platform,
        "memory_usage_mb": memory_usage_mb(),
        "debug_mode": is_debug_mode(),
        "timestamp": datetime.now().isoformat()
    }


def ensure_directory_exists(directory_path: str) -> None:
    """Ensure directory exists, creating it if necessary"""
    os.makedirs(directory_path, exist_ok=True)


# ============================================================================
# Testing Utilities
# ============================================================================

def create_test_data(data_type: str) -> Dict[str, Any]:
    """Create test data for different scenarios"""
    test_data_templates = {
        "basic_analysis": {
            "purchase_price": 500000,
            "annual_rent": 24000,
            "analysis_period": 10,
            "discount_rate": 8.0,
            "down_payment_pct": 20.0,
            "interest_rate": 6.5,
            "property_tax_rate": 1.2,
            "insurance_cost": 5000,
            "maintenance_cost": 10000
        },
        "high_rent_scenario": {
            "purchase_price": 400000,
            "annual_rent": 36000,
            "analysis_period": 10,
            "discount_rate": 8.0,
            "down_payment_pct": 20.0,
            "interest_rate": 6.5,
            "property_tax_rate": 1.2,
            "insurance_cost": 4000,
            "maintenance_cost": 8000
        },
        "sensitivity_test": {
            "purchase_price": 600000,
            "annual_rent": 30000,
            "analysis_period": 15,
            "discount_rate": 8.0,
            "down_payment_pct": 25.0,
            "interest_rate": 7.0,
            "property_tax_rate": 1.5,
            "insurance_cost": 6000,
            "maintenance_cost": 12000
        }
    }
    
    return test_data_templates.get(data_type, test_data_templates["basic_analysis"])


# ============================================================================
# Initialization Function
# ============================================================================

def initialize_shared_utilities():
    """Initialize shared utilities (create directories, set up logging, etc.)"""
    # Create necessary directories
    ensure_directory_exists(get_cache_dir())
    ensure_directory_exists(get_log_dir())
    
    # Set up root logger
    logger = setup_logging("shared_utils")
    logger.info(f"Shared utilities initialized for {APP_NAME} v{APP_VERSION}")
    
    # Log system information in debug mode
    if is_debug_mode():
        logger.debug(f"System info: {get_system_info()}")


# Initialize when module is imported
initialize_shared_utilities()