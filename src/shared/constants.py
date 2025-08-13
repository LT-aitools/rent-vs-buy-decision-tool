"""
Week 4 Shared Constants
Application-wide constants and configuration values for all work trees

This module provides centralized configuration to ensure consistency
across all sub-agent work trees.
"""

from typing import Dict, List
import os

# ============================================================================
# Application Configuration
# ============================================================================

# Application Metadata
APP_NAME = "Real Estate Rent vs. Buy Decision Tool"
APP_VERSION = "4.0.0"
APP_DESCRIPTION = "Advanced real estate investment analysis with sensitivity modeling"

# Work Tree Versions
WORK_TREE_VERSIONS = {
    "analytics_engine": "1.0.0",
    "user_experience": "1.0.0", 
    "data_integration": "1.0.0",
    "testing_qa": "1.0.0"
}

# ============================================================================
# Performance Targets
# ============================================================================

# Response Time Targets (seconds)
MAX_PAGE_LOAD_TIME = 3.0
MAX_SENSITIVITY_ANALYSIS_TIME = 2.0
MAX_MONTE_CARLO_TIME = 5.0
MAX_API_RESPONSE_TIME = 1.0

# Memory Limits (MB)
MAX_MEMORY_USAGE = 512
MAX_CACHE_SIZE = 128

# Test Coverage Targets
MIN_TEST_COVERAGE = 95.0
MIN_ACCURACY_THRESHOLD = 0.0001  # 4 decimal places

# ============================================================================
# Financial Calculation Constants
# ============================================================================

# Default Values
DEFAULT_ANALYSIS_PERIOD_YEARS = 10
DEFAULT_DISCOUNT_RATE = 8.0  # percentage
DEFAULT_INFLATION_RATE = 3.0  # percentage
DEFAULT_PROPERTY_TAX_RATE = 1.2  # percentage
DEFAULT_INTEREST_RATE = 6.5  # percentage

# Calculation Limits
MIN_ANALYSIS_PERIOD = 1
MAX_ANALYSIS_PERIOD = 50
MIN_PURCHASE_PRICE = 50000
MAX_PURCHASE_PRICE = 10000000
MIN_RENT = 500
MAX_RENT = 50000

# Monte Carlo Configuration
DEFAULT_MONTE_CARLO_ITERATIONS = 10000
MIN_MONTE_CARLO_ITERATIONS = 1000
MAX_MONTE_CARLO_ITERATIONS = 100000

# Sensitivity Analysis Configuration
DEFAULT_SENSITIVITY_RANGE = 20.0  # +/- percentage
DEFAULT_SENSITIVITY_STEPS = 21  # Number of data points

# ============================================================================
# Data Integration Constants
# ============================================================================

# API Configuration
API_TIMEOUT_SECONDS = 10.0
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 1.0  # seconds

# Cache Configuration  
CACHE_DEFAULT_TTL_HOURS = 24.0
CACHE_MAX_ENTRIES = 1000
CACHE_CLEANUP_INTERVAL_HOURS = 6.0

# Data Quality Thresholds
MIN_DATA_CONFIDENCE_SCORE = 0.5
MAX_DATA_AGE_HOURS = 48.0
MIN_DATA_SOURCES = 1

# ============================================================================
# User Experience Constants
# ============================================================================

# UI Configuration
MOBILE_BREAKPOINT_PX = 768
TABLET_BREAKPOINT_PX = 1024
DESKTOP_BREAKPOINT_PX = 1200

# Validation Messages
VALIDATION_MESSAGES = {
    "required": "This field is required",
    "invalid_number": "Please enter a valid number",
    "out_of_range": "Value must be between {min} and {max}",
    "invalid_percentage": "Percentage must be between 0 and 100",
    "future_date_required": "Date must be in the future"
}

# Help Text Categories
HELP_CATEGORIES = [
    "basic_inputs",
    "financial_details", 
    "market_assumptions",
    "advanced_options",
    "analysis_results"
]

# Accessibility Configuration
WCAG_COMPLIANCE_LEVEL = "AA"
MIN_COLOR_CONTRAST_RATIO = 4.5
MIN_TOUCH_TARGET_SIZE_PX = 44

# ============================================================================
# Testing Constants
# ============================================================================

# Test Data Paths
TEST_DATA_DIR = "tests/fixtures"
MOCK_DATA_FILE = "mock_responses.json"
TEST_CASES_FILE = "known_test_cases.json"

# Test Configuration
TEST_TIMEOUT_SECONDS = 30.0
PERFORMANCE_TEST_ITERATIONS = 100
LOAD_TEST_CONCURRENT_USERS = 10

# Accuracy Test Cases
ACCURACY_TEST_TOLERANCE = 0.01
KNOWN_TEST_CASES = [
    {
        "name": "basic_npv_calculation",
        "inputs": {
            "purchase_price": 500000,
            "annual_rent": 24000,
            "analysis_period": 10,
            "discount_rate": 8.0
        },
        "expected_npv_difference": 164877.32  # Buy NPV - Rent NPV
    },
    {
        "name": "high_rent_scenario",
        "inputs": {
            "purchase_price": 400000,
            "annual_rent": 36000,
            "analysis_period": 10,
            "discount_rate": 8.0
        },
        "expected_recommendation": "Rent"
    }
]

# ============================================================================
# Error Messages and Codes
# ============================================================================

# Error Categories
ERROR_CATEGORIES = {
    "VALIDATION": "VALIDATION",
    "CALCULATION": "CALCULATION", 
    "DATA_SOURCE": "DATA_SOURCE",
    "SYSTEM": "SYSTEM",
    "INTEGRATION": "INTEGRATION"
}

# Standard Error Messages
ERROR_MESSAGES = {
    "CALCULATION_FAILED": "Calculation failed. Please check your inputs and try again.",
    "DATA_UNAVAILABLE": "Market data temporarily unavailable. Using cached data.",
    "API_TIMEOUT": "External data source timeout. Please try again.",
    "INVALID_INPUT": "Invalid input detected. Please correct and retry.",
    "SYSTEM_ERROR": "System error occurred. Please contact support if issue persists."
}

# ============================================================================
# Analytics Configuration
# ============================================================================

# Sensitivity Variables
SENSITIVITY_VARIABLES = [
    {
        "name": "interest_rate",
        "display_name": "Interest Rate",
        "unit": "%",
        "default_range": 2.0,  # +/- percentage points
        "description": "Mortgage interest rate impact on buying decision"
    },
    {
        "name": "property_appreciation",
        "display_name": "Property Appreciation",
        "unit": "%",
        "default_range": 3.0,
        "description": "Annual property value appreciation rate"
    },
    {
        "name": "rent_increase",
        "display_name": "Rent Increases", 
        "unit": "%",
        "default_range": 2.0,
        "description": "Annual rental cost escalation rate"
    },
    {
        "name": "inflation_rate",
        "display_name": "Inflation Rate",
        "unit": "%", 
        "default_range": 2.0,
        "description": "General inflation rate affecting costs"
    },
    {
        "name": "holding_period",
        "display_name": "Holding Period",
        "unit": "years",
        "default_range": 5,  # +/- years
        "description": "Number of years holding the property"
    }
]

# Risk Assessment Factors
RISK_FACTORS = {
    "market_volatility": {
        "weight": 0.3,
        "description": "Property market volatility risk"
    },
    "interest_rate_risk": {
        "weight": 0.25,
        "description": "Interest rate change risk"
    },
    "liquidity_risk": {
        "weight": 0.2,
        "description": "Property liquidity and sale timeline risk"
    },
    "maintenance_risk": {
        "weight": 0.15,
        "description": "Unexpected maintenance and repair costs"
    },
    "economic_risk": {
        "weight": 0.1,
        "description": "Local economic conditions and employment"
    }
}

# ============================================================================
# Data Source Configuration
# ============================================================================

# API Endpoints (placeholder - actual keys in environment variables)
API_ENDPOINTS = {
    "zillow": "https://api.zillow.com/",
    "fred": "https://api.stlouisfed.org/fred/",
    "census": "https://api.census.gov/data/",
    "bls": "https://api.bls.gov/publicAPI/"
}

# Data Source Reliability Scores
DATA_SOURCE_RELIABILITY = {
    "zillow": 0.85,
    "fred": 0.95,
    "census": 0.90,
    "bls": 0.88,
    "manual_input": 0.60
}

# ============================================================================
# File Paths and Directories
# ============================================================================

# Directory Structure
DIRECTORIES = {
    "src": "src",
    "analytics": "src/analytics",
    "components": "src/components/enhanced", 
    "data": "src/data",
    "shared": "src/shared",
    "tests": "tests",
    "cache": "cache",
    "logs": "logs"
}

# File Extensions
SUPPORTED_EXPORT_FORMATS = [".xlsx", ".pdf", ".csv", ".json"]
LOG_FILE_EXTENSION = ".log"
CACHE_FILE_EXTENSION = ".cache"

# ============================================================================
# Environment Configuration
# ============================================================================

# Environment Variables
ENV_VARS = {
    "DEBUG_MODE": "REAL_ESTATE_TOOL_DEBUG",
    "LOG_LEVEL": "REAL_ESTATE_TOOL_LOG_LEVEL",
    "CACHE_ENABLED": "REAL_ESTATE_TOOL_CACHE_ENABLED",
    "API_RATE_LIMIT": "REAL_ESTATE_TOOL_API_RATE_LIMIT"
}

# Default Environment Values
DEFAULT_ENV_VALUES = {
    "DEBUG_MODE": "False",
    "LOG_LEVEL": "INFO",
    "CACHE_ENABLED": "True", 
    "API_RATE_LIMIT": "100"  # requests per minute
}

# ============================================================================
# Utility Functions
# ============================================================================

def get_env_var(var_name: str, default: str = None) -> str:
    """Get environment variable with fallback to default"""
    env_key = ENV_VARS.get(var_name, var_name)
    return os.getenv(env_key, default or DEFAULT_ENV_VALUES.get(var_name, ""))


def is_debug_mode() -> bool:
    """Check if application is in debug mode"""
    return get_env_var("DEBUG_MODE").lower() == "true"


def get_cache_dir() -> str:
    """Get cache directory path"""
    return os.path.join(os.getcwd(), DIRECTORIES["cache"])


def get_log_dir() -> str:
    """Get log directory path"""
    return os.path.join(os.getcwd(), DIRECTORIES["logs"])


# ============================================================================
# Version Information
# ============================================================================

BUILD_INFO = {
    "version": APP_VERSION,
    "build_date": "2025-08-13",
    "python_version": "3.13+",
    "streamlit_version": "1.35+",
    "repository": "https://github.com/LT-aitools/rent-vs-buy-decision-tool"
}

# Feature Flags
FEATURE_FLAGS = {
    "enable_monte_carlo": True,
    "enable_market_data": True,
    "enable_sensitivity_analysis": True,
    "enable_scenario_comparison": True,
    "enable_risk_assessment": True,
    "enable_mobile_ui": True,
    "enable_accessibility": True,
    "enable_caching": True,
    "enable_logging": True
}