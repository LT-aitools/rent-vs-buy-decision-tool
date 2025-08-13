"""
Week 4 Shared Module
Central module for shared interfaces, constants, and utilities

This module provides the foundation for sub-agent work tree coordination
and ensures consistent interfaces across all components.
"""

from .interfaces import (
    # Core Data Types
    AnalysisType,
    RiskLevel,
    ValidationStatus,
    
    # Analytics Interfaces
    SensitivityVariable,
    SensitivityResult,
    ScenarioDefinition,
    MonteCarloResult,
    RiskAssessment,
    AnalyticsResult,
    AnalyticsEngine,
    
    # User Experience Interfaces
    ValidationResult,
    GuidanceContext,
    UIState,
    UIComponent,
    GuidanceSystem,
    
    # Data Integration Interfaces
    MarketData,
    DataRequest,
    DataValidationResult,
    DataProvider,
    
    # Testing Interfaces
    TestResult,
    PerformanceMetric,
    AccuracyTestCase,
    TestSuiteResult,
    TestFramework,
    
    # Integration Interfaces
    IntegrationRequest,
    IntegrationResponse,
    IntegrationBus,
    
    # Utility Functions
    validate_interface_compliance,
    create_mock_market_data,
    create_mock_analytics_result
)

from .constants import (
    # Application Configuration
    APP_NAME,
    APP_VERSION,
    WORK_TREE_VERSIONS,
    
    # Performance Targets
    MAX_PAGE_LOAD_TIME,
    MAX_SENSITIVITY_ANALYSIS_TIME,
    MAX_MONTE_CARLO_TIME,
    MIN_TEST_COVERAGE,
    
    # Financial Constants
    DEFAULT_ANALYSIS_PERIOD_YEARS,
    DEFAULT_DISCOUNT_RATE,
    DEFAULT_INFLATION_RATE,
    DEFAULT_MONTE_CARLO_ITERATIONS,
    
    # Data Configuration
    API_TIMEOUT_SECONDS,
    CACHE_DEFAULT_TTL_HOURS,
    MIN_DATA_CONFIDENCE_SCORE,
    
    # UI Configuration
    MOBILE_BREAKPOINT_PX,
    VALIDATION_MESSAGES,
    WCAG_COMPLIANCE_LEVEL,
    
    # Testing Configuration
    ACCURACY_TEST_TOLERANCE,
    KNOWN_TEST_CASES,
    
    # Utility Functions
    get_env_var,
    is_debug_mode,
    get_cache_dir,
    get_log_dir
)

from .utils import (
    # Logging
    setup_logging,
    log_execution_time,
    
    # Validation
    validate_numeric_input,
    validate_percentage,
    validate_required_fields,
    
    # Mathematical
    round_to_precision,
    calculate_percentage_change,
    is_approximately_equal,
    safe_divide,
    clamp,
    
    # Serialization
    serialize_dataclass,
    serialize_to_json,
    
    # Caching
    generate_cache_key,
    is_cache_valid,
    create_cache_path,
    
    # Performance
    PerformanceTimer,
    memory_usage_mb,
    
    # Error Handling
    RetryableError,
    retry_on_failure,
    safe_execute,
    
    # String Utilities
    format_currency,
    format_percentage,
    truncate_string,
    
    # System
    get_system_info,
    ensure_directory_exists,
    
    # Testing
    create_test_data
)

# Version information
__version__ = APP_VERSION
__author__ = "Real Estate Decision Tool Team"
__description__ = "Shared interfaces and utilities for Week 4 sub-agent development"

# Module metadata
__all__ = [
    # Interfaces
    "AnalysisType", "RiskLevel", "ValidationStatus",
    "SensitivityVariable", "SensitivityResult", "ScenarioDefinition",
    "MonteCarloResult", "RiskAssessment", "AnalyticsResult", "AnalyticsEngine",
    "ValidationResult", "GuidanceContext", "UIState", "UIComponent", "GuidanceSystem",
    "MarketData", "DataRequest", "DataValidationResult", "DataProvider",
    "TestResult", "PerformanceMetric", "AccuracyTestCase", "TestSuiteResult", "TestFramework",
    "IntegrationRequest", "IntegrationResponse", "IntegrationBus",
    "validate_interface_compliance", "create_mock_market_data", "create_mock_analytics_result",
    
    # Constants
    "APP_NAME", "APP_VERSION", "WORK_TREE_VERSIONS",
    "MAX_PAGE_LOAD_TIME", "MAX_SENSITIVITY_ANALYSIS_TIME", "MAX_MONTE_CARLO_TIME", "MIN_TEST_COVERAGE",
    "DEFAULT_ANALYSIS_PERIOD_YEARS", "DEFAULT_DISCOUNT_RATE", "DEFAULT_INFLATION_RATE", "DEFAULT_MONTE_CARLO_ITERATIONS",
    "API_TIMEOUT_SECONDS", "CACHE_DEFAULT_TTL_HOURS", "MIN_DATA_CONFIDENCE_SCORE",
    "MOBILE_BREAKPOINT_PX", "VALIDATION_MESSAGES", "WCAG_COMPLIANCE_LEVEL",
    "ACCURACY_TEST_TOLERANCE", "KNOWN_TEST_CASES",
    "get_env_var", "is_debug_mode", "get_cache_dir", "get_log_dir",
    
    # Utilities
    "setup_logging", "log_execution_time",
    "validate_numeric_input", "validate_percentage", "validate_required_fields",
    "round_to_precision", "calculate_percentage_change", "is_approximately_equal", "safe_divide", "clamp",
    "serialize_dataclass", "serialize_to_json",
    "generate_cache_key", "is_cache_valid", "create_cache_path",
    "PerformanceTimer", "memory_usage_mb",
    "RetryableError", "retry_on_failure", "safe_execute",
    "format_currency", "format_percentage", "truncate_string",
    "get_system_info", "ensure_directory_exists",
    "create_test_data"
]


def get_work_tree_info() -> dict:
    """Get information about all work trees and their versions"""
    return {
        "shared_module_version": __version__,
        "work_trees": WORK_TREE_VERSIONS,
        "supported_analysis_types": [t.value for t in AnalysisType],
        "performance_targets": {
            "max_page_load_time": MAX_PAGE_LOAD_TIME,
            "max_sensitivity_analysis_time": MAX_SENSITIVITY_ANALYSIS_TIME,
            "max_monte_carlo_time": MAX_MONTE_CARLO_TIME,
            "min_test_coverage": MIN_TEST_COVERAGE
        }
    }


def validate_work_tree_compatibility(component: object, expected_interface: type) -> dict:
    """
    Validate that a component from a work tree implements expected interfaces
    
    Args:
        component: Component instance to validate
        expected_interface: Expected interface class
    
    Returns:
        Validation result with compatibility information
    """
    is_compatible = validate_interface_compliance(component, expected_interface)
    
    return {
        "is_compatible": is_compatible,
        "component_type": type(component).__name__,
        "expected_interface": expected_interface.__name__,
        "missing_methods": _get_missing_methods(component, expected_interface) if not is_compatible else [],
        "timestamp": get_system_info()["timestamp"]
    }


def _get_missing_methods(component: object, interface_class: type) -> list:
    """Get list of missing methods from interface"""
    if not hasattr(interface_class, '__abstractmethods__'):
        return []
    
    required_methods = interface_class.__abstractmethods__
    component_methods = dir(component)
    
    return [method for method in required_methods if method not in component_methods]


# Initialization message
def _log_module_initialization():
    """Log module initialization for debugging"""
    logger = setup_logging("shared_module")
    logger.info(f"Shared module initialized - Version {__version__}")
    logger.debug(f"Work tree versions: {WORK_TREE_VERSIONS}")


# Initialize logging when module is imported
_log_module_initialization()