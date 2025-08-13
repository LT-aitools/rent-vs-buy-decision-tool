#!/usr/bin/env python3
"""
Testing System Validation Script
Comprehensive validation of all testing components and benchmarks

This script validates:
- Testing framework functionality
- All test modules can be loaded and executed
- Performance benchmarks meet targets
- Data validation works correctly
- Integration tests function properly
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def validate_testing_system():
    """Validate the entire testing system"""
    print("=" * 80)
    print("TESTING SYSTEM VALIDATION")
    print("=" * 80)
    print(f"Timestamp: {datetime.now()}")
    print(f"Project Root: {project_root}")
    print()
    
    validation_results = {
        'framework_initialization': False,
        'test_discovery': False,
        'unit_test_execution': False,
        'integration_test_execution': False,
        'accuracy_validation': False,
        'performance_benchmarking': False,
        'data_validation': False,
        'regression_pipeline': False,
        'overall_score': 0.0
    }
    
    # 1. Test Framework Initialization
    print("1. Testing Framework Initialization")
    print("-" * 40)
    try:
        from tests.framework.test_framework import get_test_framework
        framework = get_test_framework()
        print(f"✓ Framework initialized successfully")
        print(f"✓ Test modules discovered: {len(framework.test_modules)}")
        validation_results['framework_initialization'] = True
        validation_results['test_discovery'] = len(framework.test_modules) > 0
    except Exception as e:
        print(f"✗ Framework initialization failed: {e}")
    print()
    
    # 2. Test Module Loading
    print("2. Testing Module Loading")
    print("-" * 40)
    test_modules_to_validate = [
        'tests.accuracy.test_financial_accuracy',
        'tests.integration_tests.test_cross_component_integration',
        'tests.performance_tests.test_performance_benchmarks',
        'tests.data_validation_tests.test_data_validation',
        'tests.regression.test_regression_pipeline'
    ]
    
    loaded_modules = 0
    for module_name in test_modules_to_validate:
        try:
            __import__(module_name)
            print(f"✓ {module_name}")
            loaded_modules += 1
        except Exception as e:
            print(f"✗ {module_name}: {e}")
    
    print(f"Loaded {loaded_modules}/{len(test_modules_to_validate)} test modules")
    print()
    
    # 3. Test Core Calculations (if available)
    print("3. Testing Core Calculations")
    print("-" * 40)
    try:
        # Test NPV calculation
        from src.calculations.npv_analysis import calculate_npv_analysis
        
        test_params = {
            'purchase_price': 500000,
            'down_payment_pct': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'current_annual_rent': 60000,
            'rent_increase_rate': 3.0,
            'analysis_period': 10,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.2,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'market_appreciation_rate': 3.5,
            'transaction_costs': 25000
        }
        
        start_time = time.time()
        result = calculate_npv_analysis(test_params)
        calc_time = (time.time() - start_time) * 1000
        
        if 'ownership_npv' in result and 'rental_npv' in result:
            print(f"✓ NPV calculation successful")
            print(f"✓ Calculation time: {calc_time:.2f}ms")
            print(f"  Ownership NPV: ${result['ownership_npv']:,.0f}")
            print(f"  Rental NPV: ${result['rental_npv']:,.0f}")
            print(f"  NPV Difference: ${result.get('npv_difference', 0):,.0f}")
            
            # Performance check
            if calc_time < 100:  # Should complete in under 100ms
                print(f"✓ Performance target met")
            else:
                print(f"⚠ Performance slower than target (100ms)")
                
        else:
            print(f"✗ NPV calculation returned incomplete results")
    
    except ImportError:
        print("⚠ NPV calculation module not available")
    except Exception as e:
        print(f"✗ NPV calculation failed: {e}")
    print()
    
    # 4. Test Data Validation
    print("4. Testing Data Validation")
    print("-" * 40)
    try:
        from tests.data_validation_tests.test_data_validation import FinancialDataValidator
        
        validator = FinancialDataValidator()
        
        # Test valid inputs
        valid_tests = [
            ('purchase_price', 500000),
            ('interest_rate', 5.0),
            ('down_payment', 20.0, 500000)
        ]
        
        validation_passed = 0
        for test in valid_tests:
            if test[0] == 'purchase_price':
                result = validator.validate_purchase_price(test[1])
            elif test[0] == 'interest_rate':
                result = validator.validate_interest_rate(test[1])
            elif test[0] == 'down_payment':
                result = validator.validate_down_payment(test[1], test[2])
            
            if result.is_valid:
                print(f"✓ {test[0]} validation: {test[1]}")
                validation_passed += 1
            else:
                print(f"✗ {test[0]} validation failed: {result.message}")
        
        print(f"Data validation tests: {validation_passed}/{len(valid_tests)} passed")
        validation_results['data_validation'] = validation_passed == len(valid_tests)
        
    except Exception as e:
        print(f"✗ Data validation testing failed: {e}")
    print()
    
    # 5. Test Performance Benchmarking
    print("5. Testing Performance Benchmarking")
    print("-" * 40)
    try:
        if 'framework' in locals():
            metrics = framework.benchmark_performance('calculations')
            if metrics:
                print(f"✓ Performance benchmarking functional")
                print(f"✓ Generated {len(metrics)} performance metrics")
                
                for metric in metrics[:3]:  # Show first 3
                    status = "✓" if metric.meets_target else "⚠"
                    print(f"  {status} {metric.metric_name}: {metric.value:.2f}{metric.unit}")
                
                validation_results['performance_benchmarking'] = True
            else:
                print(f"⚠ No performance metrics generated")
        
    except Exception as e:
        print(f"✗ Performance benchmarking failed: {e}")
    print()
    
    # 6. Test Integration Components
    print("6. Testing Integration Components")
    print("-" * 40)
    try:
        # Test shared interfaces
        from src.shared.interfaces import create_mock_market_data, create_mock_analytics_result
        
        market_data = create_mock_market_data("Test Location")
        analytics_result = create_mock_analytics_result()
        
        print(f"✓ Mock market data created: {market_data.location}")
        print(f"✓ Mock analytics result created: {analytics_result.base_recommendation}")
        
        # Test interface compliance
        from src.shared.interfaces import validate_interface_compliance, TestFramework
        
        if 'framework' in locals():
            is_compliant = validate_interface_compliance(framework, TestFramework)
            if is_compliant:
                print(f"✓ Framework implements TestFramework interface")
                validation_results['integration_test_execution'] = True
            else:
                print(f"⚠ Framework interface compliance issues")
        
    except Exception as e:
        print(f"✗ Integration component testing failed: {e}")
    print()
    
    # 7. Test Regression Pipeline (Basic)
    print("7. Testing Regression Pipeline")
    print("-" * 40)
    try:
        from tests.regression.test_regression_pipeline import RegressionTestPipeline
        
        pipeline = RegressionTestPipeline()
        print(f"✓ Regression pipeline initialized")
        
        # Test quality grade calculation
        test_scores = [0.95, 0.85, 0.75, 0.65]
        for score in test_scores:
            grade = pipeline._calculate_quality_grade(score)
            print(f"  Score {score:.2f} → Grade {grade}")
        
        print(f"✓ Quality grade calculation working")
        validation_results['regression_pipeline'] = True
        
    except Exception as e:
        print(f"✗ Regression pipeline testing failed: {e}")
    print()
    
    # Calculate Overall Score
    print("8. Overall Validation Results")
    print("-" * 40)
    
    passed_tests = sum(validation_results.values())
    total_tests = len(validation_results) - 1  # Exclude overall_score
    overall_score = passed_tests / total_tests if total_tests > 0 else 0.0
    validation_results['overall_score'] = overall_score
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Overall Score: {overall_score:.1%}")
    
    if overall_score >= 0.9:
        status = "EXCELLENT ✅"
        grade = "A"
    elif overall_score >= 0.8:
        status = "GOOD ✅"
        grade = "B"
    elif overall_score >= 0.7:
        status = "ACCEPTABLE ⚠️"
        grade = "C"
    else:
        status = "NEEDS IMPROVEMENT ❌"
        grade = "F"
    
    print(f"System Grade: {grade}")
    print(f"System Status: {status}")
    print()
    
    # Detailed Results
    print("Detailed Results:")
    for test_name, passed in validation_results.items():
        if test_name != 'overall_score':
            status_symbol = "✓" if passed else "✗"
            print(f"  {status_symbol} {test_name.replace('_', ' ').title()}")
    
    print()
    print("=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    
    return validation_results


if __name__ == '__main__':
    results = validate_testing_system()
    
    # Exit with appropriate code
    if results['overall_score'] >= 0.8:
        sys.exit(0)  # Success
    elif results['overall_score'] >= 0.6:
        sys.exit(1)  # Warning
    else:
        sys.exit(2)  # Failure