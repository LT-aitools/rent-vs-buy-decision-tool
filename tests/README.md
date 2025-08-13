# Week 4 Testing & QA System

## 🎯 Overview

The comprehensive Testing and Quality Assurance system provides automated testing, performance benchmarking, and quality monitoring for the Real Estate Rent vs. Buy Decision Tool.

## 🚀 Quick Start

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Usage
```bash
# Run full regression test suite
python3 tests/run_regression_tests.py

# Quick smoke test
python3 tests/run_regression_tests.py --quick

# Performance testing only
python3 tests/run_regression_tests.py --performance

# Validate testing system
python3 tests/validate_testing_system.py
```

## 📁 Architecture

```
tests/
├── framework/                 # Core testing framework
│   ├── test_framework.py     # Main TestFramework implementation
│   ├── config.py             # Configuration constants
│   ├── logging_config.py     # Logging setup
│   └── __init__.py
├── accuracy/                 # Financial accuracy tests
├── integration_tests/        # Cross-component integration
├── performance_tests/        # Load and speed testing  
├── data_validation_tests/    # Input validation
├── regression/              # Automated regression testing
└── logs/                    # Test execution logs
```

## ⚙️ Configuration

### Environment Variables

The testing system supports configuration via environment variables:

```bash
# Coverage targets
export TEST_COVERAGE_TARGET=95.0        # Target coverage percentage
export TEST_ACCURACY_TOLERANCE=0.0001   # Financial accuracy tolerance

# Performance settings  
export TEST_PERFORMANCE_TIMEOUT=30.0    # Test timeout in seconds

# Regression thresholds
export REGRESSION_FAILURE_THRESHOLD=0.05     # 5% failure rate increase
export REGRESSION_PERFORMANCE_THRESHOLD=1.2  # 20% performance degradation
export REGRESSION_QUALITY_THRESHOLD=0.8      # 80% minimum quality score

# Logging
export TEST_LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
```

### Configuration Classes

#### Performance Targets
```python
from tests.framework import PerformanceTargets

# Access performance targets
print(f"NPV calculation target: {PerformanceTargets.SINGLE_NPV_CALCULATION_MS}ms")
print(f"Batch processing target: {PerformanceTargets.BATCH_NPV_CALCULATION_MS}ms")
```

#### Quality Targets
```python
from tests.framework import QualityTargets

# Access quality targets
print(f"Coverage target: {QualityTargets.COVERAGE_TARGET_PCT}%")
print(f"Accuracy tolerance: {QualityTargets.ACCURACY_TOLERANCE}")
```

## 🧪 Test Types

### 1. Unit Tests
Test individual components in isolation:
```python
from tests.framework import get_test_framework

framework = get_test_framework()
result = framework.run_unit_tests('calculations')
print(f"Coverage: {result.coverage_percentage:.1f}%")
```

### 2. Integration Tests  
Test component interactions:
```python
result = framework.run_integration_tests()
print(f"Tests passed: {result.passed_tests}/{result.total_tests}")
```

### 3. Accuracy Tests
Validate financial calculations to 4 decimal places:
```python
from src.shared.interfaces import AccuracyTestCase

test_case = AccuracyTestCase(
    test_name="npv_calculation",
    inputs={'purchase_price': 500000, 'interest_rate': 5.0},
    expected_outputs={'npv_difference': 125000.0},
    tolerance=0.0001
)

result = framework.validate_accuracy([test_case])
```

### 4. Performance Tests
Benchmark component performance:
```python
metrics = framework.benchmark_performance('calculations')
for metric in metrics:
    print(f"{metric.metric_name}: {metric.value:.2f}{metric.unit}")
```

## 📊 Quality Monitoring

### Quality Scoring
The system calculates an overall quality score based on:
- **Test Success Rate (40%)**: Percentage of passing tests
- **Coverage (30%)**: Code coverage percentage  
- **Performance (30%)**: Performance target achievement rate

### Quality Grades
- **A+**: 95%+ overall quality score
- **A**: 90-94% overall quality score  
- **B+**: 85-89% overall quality score
- **B**: 80-84% overall quality score
- **C+**: 75-79% overall quality score
- **C**: 70-74% overall quality score
- **F**: <70% overall quality score

### Regression Detection
Automatically detects:
- **Test Regressions**: >5% increase in failure rate
- **Performance Regressions**: >20% performance degradation
- **Quality Regressions**: Quality score drops below 80%

## 📈 Performance Benchmarks

### Target Performance Metrics

| Component | Metric | Target | Unit |
|-----------|---------|---------|------|
| NPV Calculation | Single calculation | 50 | ms |
| NPV Calculation | Batch (100 calcs) | 2000 | ms |
| Mortgage | Payment calculation | 5 | ms |
| Amortization | Schedule generation | 100 | ms |
| Analysis | Sensitivity analysis | 500 | ms |
| Workflow | Complete analysis | 1000 | ms |
| Export | CSV generation | 100 | ms |

### Memory Limits

| Test Type | Limit | Unit |
|-----------|-------|------|
| Single calculation | 100 | MB |
| Batch processing (1000) | 50 | MB growth |

## 🔍 Logging

### Log Files
- **`logs/testing_framework.log`**: Detailed framework logs
- **`logs/test_results.log`**: Test execution results
- **`logs/performance_metrics.log`**: Performance measurements

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General information about test execution
- **WARNING**: Warning conditions (performance issues, low coverage)
- **ERROR**: Error conditions (test failures, regressions)

### Programmatic Logging
```python
from tests.framework import get_logger

logger = get_logger('my_component')
logger.info("Starting component test")
logger.warning("Performance below target")
logger.error("Test failed with exception")
```

## 🔄 Regression Testing Pipeline

### Automated Pipeline
The regression pipeline runs:
1. **Unit tests** for all components
2. **Integration tests** across work trees
3. **Accuracy validation** for financial calculations
4. **Performance benchmarking** with target comparison
5. **Data validation** tests
6. **Regression analysis** against baseline
7. **Quality metrics** calculation
8. **Executive reporting**

### Pipeline Modes

#### Full Mode (Default)
```bash
python3 tests/run_regression_tests.py
```
Runs complete test suite with full analysis.

#### Quick Mode
```bash
python3 tests/run_regression_tests.py --quick
```
Runs critical tests only for fast feedback.

#### Performance Mode
```bash
python3 tests/run_regression_tests.py --performance
```
Focuses on performance benchmarking and regression detection.

### Baseline Management
```bash
# Update baseline after successful run
python3 tests/run_regression_tests.py --baseline

# Generate report from existing results
python3 tests/run_regression_tests.py --report-only
```

## 🛠️ Extending the Framework

### Adding New Test Types
1. Create test module in appropriate directory
2. Inherit from `unittest.TestCase`
3. Use framework logging and configuration

```python
import unittest
from tests.framework import get_logger, config

class TestMyComponent(unittest.TestCase):
    def setUp(self):
        self.logger = get_logger('my_component')
        self.tolerance = config.accuracy_tolerance
    
    def test_my_function(self):
        self.logger.info("Testing my function")
        # Your test logic here
```

### Adding Performance Benchmarks
```python
from tests.framework import config

def benchmark_my_component(self, component_name: str) -> List[PerformanceMetric]:
    target_ms = config.get_performance_target('my_metric')
    
    # Benchmark logic here
    
    return [PerformanceMetric(
        metric_name='my_metric',
        value=measured_time_ms,
        unit='ms', 
        target_value=target_ms,
        meets_target=measured_time_ms <= target_ms,
        timestamp=datetime.now()
    )]
```

## 🔧 Troubleshooting

### Common Issues

#### Coverage Tool Not Found
```bash
pip install coverage pytest-cov
```

#### Performance Monitoring Disabled
```bash
pip install psutil
```

#### Module Import Errors
Ensure project root is in Python path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Debug Mode
Enable verbose logging:
```bash
export TEST_LOG_LEVEL=DEBUG
python3 tests/run_regression_tests.py
```

## 📚 API Reference

### TestFramework Interface
```python
class TestFramework(abc.ABC):
    @abc.abstractmethod
    def run_unit_tests(self, component_name: str) -> TestSuiteResult:
        """Run unit tests for a component"""
        
    @abc.abstractmethod  
    def run_integration_tests(self) -> TestSuiteResult:
        """Run integration tests"""
        
    @abc.abstractmethod
    def validate_accuracy(self, test_cases: List[AccuracyTestCase]) -> TestSuiteResult:
        """Validate financial calculation accuracy"""
        
    @abc.abstractmethod
    def benchmark_performance(self, component_name: str) -> List[PerformanceMetric]:
        """Benchmark component performance"""
```

### Configuration API
```python
from tests.framework import config

# Access configuration
print(f"Coverage target: {config.coverage_target}%")
print(f"Performance timeout: {config.performance_timeout}s")

# Get specific targets
target_ms = config.get_performance_target('single_npv_calculation') 
memory_limit = config.get_memory_limit('batch_growth_mb')
```

### Logging API
```python
from tests.framework.logging_config import (
    log_test_start,
    log_test_completion, 
    log_performance_result,
    log_coverage_result,
    log_regression
)

# Log test execution
log_test_start("my_test")
log_test_completion("my_test", "PASS", 45.2, "All assertions passed")

# Log performance
log_performance_result("calculations", "npv_calc", 42.5, "ms", 50.0)

# Log coverage
log_coverage_result("calculations", 96.5, 95.0)

# Log regression
log_regression("calculations", "performance", "HIGH", "Response time increased 50%")
```

## 🎯 Best Practices

### Test Writing
1. **Use descriptive test names** that explain what is being tested
2. **Keep tests independent** - no test should depend on another
3. **Use appropriate tolerances** for financial calculations (0.0001)
4. **Include edge cases** - zero values, extremes, boundary conditions
5. **Mock external dependencies** to ensure test isolation

### Performance Testing
1. **Warm-up runs** before timing to avoid cold start effects
2. **Multiple iterations** and statistical analysis of results  
3. **Memory profiling** to detect leaks and excessive usage
4. **Concurrent testing** to validate thread safety

### Quality Assurance  
1. **Maintain 95%+ coverage** on all critical components
2. **Monitor performance baselines** and detect regressions early
3. **Regular baseline updates** after confirmed improvements
4. **Document test rationale** and expected behavior

This comprehensive testing system ensures high code quality, performance, and reliability for the Real Estate Decision Tool.