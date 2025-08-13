"""
Testing Framework Configuration
Centralized configuration constants for the testing system
"""

import os
from typing import Dict, Any

# Performance Targets and Thresholds
class PerformanceTargets:
    """Performance benchmark targets in milliseconds"""
    SINGLE_NPV_CALCULATION_MS = 50.0
    BATCH_NPV_CALCULATION_MS = 2000.0  # 100 calculations
    MORTGAGE_CALCULATION_MS = 5.0
    AMORTIZATION_SCHEDULE_MS = 100.0
    SENSITIVITY_ANALYSIS_MS = 500.0
    FULL_WORKFLOW_MS = 1000.0
    CSV_EXPORT_MS = 100.0

class QualityTargets:
    """Quality assurance targets and thresholds"""
    COVERAGE_TARGET_PCT = 95.0
    MINIMUM_COVERAGE_PCT = 85.0
    ACCURACY_TOLERANCE = 0.0001  # 4 decimal places
    PERFORMANCE_TIMEOUT_SECONDS = 30.0
    
class RegressionThresholds:
    """Regression detection thresholds"""
    FAILURE_RATE_THRESHOLD = 0.05  # 5% failure rate increase triggers alert
    PERFORMANCE_DEGRADATION_THRESHOLD = 1.2  # 20% performance degradation
    QUALITY_SCORE_THRESHOLD = 0.8  # 80% minimum quality score
    
class MemoryLimits:
    """Memory usage limits and targets"""
    BATCH_MEMORY_GROWTH_MB = 50.0  # Max memory growth for 1000 calculations
    SINGLE_CALCULATION_MEMORY_MB = 100.0  # Max memory for single calculation
    
class TestConfiguration:
    """Main test configuration with environment overrides"""
    
    def __init__(self):
        # Base configuration
        self.coverage_target = float(os.getenv('TEST_COVERAGE_TARGET', QualityTargets.COVERAGE_TARGET_PCT))
        self.accuracy_tolerance = float(os.getenv('TEST_ACCURACY_TOLERANCE', QualityTargets.ACCURACY_TOLERANCE))
        self.performance_timeout = float(os.getenv('TEST_PERFORMANCE_TIMEOUT', QualityTargets.PERFORMANCE_TIMEOUT_SECONDS))
        
        # Regression thresholds
        self.failure_threshold = float(os.getenv('REGRESSION_FAILURE_THRESHOLD', RegressionThresholds.FAILURE_RATE_THRESHOLD))
        self.performance_threshold = float(os.getenv('REGRESSION_PERFORMANCE_THRESHOLD', RegressionThresholds.PERFORMANCE_DEGRADATION_THRESHOLD))
        self.quality_threshold = float(os.getenv('REGRESSION_QUALITY_THRESHOLD', RegressionThresholds.QUALITY_SCORE_THRESHOLD))
        
        # Performance targets
        self.performance_targets = {
            'single_npv_calculation': PerformanceTargets.SINGLE_NPV_CALCULATION_MS,
            'batch_npv_calculation': PerformanceTargets.BATCH_NPV_CALCULATION_MS,
            'mortgage_calculation': PerformanceTargets.MORTGAGE_CALCULATION_MS,
            'amortization_schedule': PerformanceTargets.AMORTIZATION_SCHEDULE_MS,
            'sensitivity_analysis': PerformanceTargets.SENSITIVITY_ANALYSIS_MS,
            'full_workflow': PerformanceTargets.FULL_WORKFLOW_MS,
            'csv_export': PerformanceTargets.CSV_EXPORT_MS
        }
        
        # Memory limits
        self.memory_limits = {
            'batch_growth_mb': MemoryLimits.BATCH_MEMORY_GROWTH_MB,
            'single_calculation_mb': MemoryLimits.SINGLE_CALCULATION_MEMORY_MB
        }
        
        # Test execution settings
        self.quick_mode_components = ['calculations', 'analysis_integration', 'npv_integration']
        self.critical_test_modules = ['accuracy', 'integration', 'performance']
        
        # Logging configuration
        self.log_level = os.getenv('TEST_LOG_LEVEL', 'INFO')
        self.log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
    def get_performance_target(self, metric_name: str) -> float:
        """Get performance target for a specific metric"""
        return self.performance_targets.get(metric_name, 1000.0)  # Default 1 second
        
    def get_memory_limit(self, limit_name: str) -> float:
        """Get memory limit for a specific type"""
        return self.memory_limits.get(limit_name, 100.0)  # Default 100MB
        
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return {
            'coverage_target': self.coverage_target,
            'accuracy_tolerance': self.accuracy_tolerance,
            'performance_timeout': self.performance_timeout,
            'failure_threshold': self.failure_threshold,
            'performance_threshold': self.performance_threshold,
            'quality_threshold': self.quality_threshold,
            'performance_targets': self.performance_targets,
            'memory_limits': self.memory_limits,
            'log_level': self.log_level
        }

# Global configuration instance
config = TestConfiguration()

# Component name constants
class ComponentNames:
    """Standardized component names for testing"""
    CALCULATIONS = 'calculations'
    ANALYSIS_INTEGRATION = 'analysis_integration'
    NPV_INTEGRATION = 'npv_integration'
    DECISION_ENGINE = 'decision_engine'
    SENSITIVITY = 'sensitivity'
    RESULTS_PROCESSOR = 'results_processor'
    EXPORT = 'export'
    VALIDATION = 'validation'
    
# Test type constants
class TestTypes:
    """Test type identifiers"""
    UNIT = 'unit'
    INTEGRATION = 'integration'
    ACCURACY = 'accuracy'
    PERFORMANCE = 'performance'
    VALIDATION = 'validation'
    REGRESSION = 'regression'