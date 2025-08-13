"""
Testing Framework Module
Week 4 Testing & QA Components
"""

from .test_framework import ComprehensiveTestFramework, get_test_framework
from .config import config, ComponentNames, TestTypes, PerformanceTargets, QualityTargets
from .logging_config import get_logger, testing_logger

__all__ = [
    'ComprehensiveTestFramework', 
    'get_test_framework',
    'config',
    'ComponentNames',
    'TestTypes',
    'PerformanceTargets',
    'QualityTargets',
    'get_logger',
    'testing_logger'
]