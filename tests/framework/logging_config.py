"""
Testing Framework Logging Configuration
Centralized logging setup for the testing system
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import config


class TestingLogger:
    """Centralized logging configuration for testing framework"""
    
    def __init__(self):
        self._loggers = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Setup root logger configuration"""
        # Create logs directory
        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger('testing_framework')
        root_logger.setLevel(getattr(logging, config.log_level.upper()))
        
        # Prevent duplicate handlers
        if root_logger.handlers:
            root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(logs_dir / "testing_framework.log")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Test results handler
        results_handler = logging.FileHandler(logs_dir / "test_results.log")
        results_handler.setLevel(logging.INFO)
        results_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        results_handler.setFormatter(results_formatter)
        
        # Create results logger
        results_logger = logging.getLogger('testing_framework.results')
        results_logger.addHandler(results_handler)
        results_logger.setLevel(logging.INFO)
        results_logger.propagate = False  # Don't propagate to root logger
        
        self._loggers['root'] = root_logger
        self._loggers['results'] = results_logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get logger instance for specific component"""
        if name in self._loggers:
            return self._loggers[name]
        
        # Create component-specific logger
        logger = logging.getLogger(f'testing_framework.{name}')
        self._loggers[name] = logger
        return logger
    
    def log_test_result(self, test_name: str, status: str, duration_ms: float, details: Optional[str] = None):
        """Log test execution result"""
        results_logger = self._loggers['results']
        message = f"TEST: {test_name} | STATUS: {status} | DURATION: {duration_ms:.2f}ms"
        if details:
            message += f" | DETAILS: {details}"
        
        if status == 'PASS':
            results_logger.info(message)
        elif status == 'FAIL':
            results_logger.error(message)
        else:
            results_logger.warning(message)
    
    def log_performance_metric(self, component: str, metric_name: str, value: float, unit: str, meets_target: bool):
        """Log performance metric"""
        results_logger = self._loggers['results']
        status = "✓" if meets_target else "⚠"
        message = f"PERFORMANCE: {component}.{metric_name} = {value:.2f}{unit} {status}"
        results_logger.info(message)
    
    def log_coverage_result(self, component: str, coverage_pct: float, target_pct: float):
        """Log coverage result"""
        results_logger = self._loggers['results']
        status = "✓" if coverage_pct >= target_pct else "⚠"
        message = f"COVERAGE: {component} = {coverage_pct:.1f}% (target: {target_pct:.1f}%) {status}"
        results_logger.info(message)
    
    def log_regression_detection(self, component: str, regression_type: str, severity: str, details: str):
        """Log regression detection"""
        results_logger = self._loggers['results']
        message = f"REGRESSION: {component} | TYPE: {regression_type} | SEVERITY: {severity} | {details}"
        
        if severity.upper() in ['CRITICAL', 'HIGH']:
            results_logger.error(message)
        else:
            results_logger.warning(message)


# Global logger instance
testing_logger = TestingLogger()


def get_logger(component: str = 'framework') -> logging.Logger:
    """Get logger instance for component"""
    return testing_logger.get_logger(component)


def log_test_start(test_name: str):
    """Log test start"""
    logger = get_logger('execution')
    logger.info(f"Starting test: {test_name}")


def log_test_completion(test_name: str, status: str, duration_ms: float, details: Optional[str] = None):
    """Log test completion"""
    testing_logger.log_test_result(test_name, status, duration_ms, details)


def log_performance_result(component: str, metric_name: str, value: float, unit: str, target: float):
    """Log performance result"""
    meets_target = value <= target if unit in ['ms', 's'] else value >= target
    testing_logger.log_performance_metric(component, metric_name, value, unit, meets_target)


def log_coverage_result(component: str, coverage_pct: float, target_pct: float = 95.0):
    """Log coverage result"""
    testing_logger.log_coverage_result(component, coverage_pct, target_pct)


def log_regression(component: str, regression_type: str, severity: str, details: str):
    """Log regression detection"""
    testing_logger.log_regression_detection(component, regression_type, severity, details)