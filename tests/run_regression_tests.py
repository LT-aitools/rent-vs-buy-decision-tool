#!/usr/bin/env python3
"""
Regression Test Runner
Automated script to run comprehensive regression tests

Usage:
    python tests/run_regression_tests.py                    # Run full suite
    python tests/run_regression_tests.py --quick           # Run quick subset
    python tests/run_regression_tests.py --performance     # Performance tests only
    python tests/run_regression_tests.py --report-only     # Generate report from latest results
"""

import sys
import argparse
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.regression.test_regression_pipeline import RegressionTestPipeline


def main():
    """Main regression test runner"""
    parser = argparse.ArgumentParser(description='Run regression test suite')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick regression tests only')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests only') 
    parser.add_argument('--report-only', action='store_true',
                       help='Generate report from latest results without running tests')
    parser.add_argument('--baseline', action='store_true',
                       help='Update baseline with current results')
    parser.add_argument('--output', type=str,
                       help='Output directory for test results')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = RegressionTestPipeline(results_dir=args.output)
    
    if args.report_only:
        # Generate report from latest results
        baseline = pipeline._load_baseline()
        if baseline:
            report = pipeline.generate_report(baseline)
            print(report)
        else:
            print("No baseline results found to report on")
            sys.exit(1)
        return
    
    # Run regression tests
    if args.quick:
        print("Running quick regression test suite...")
        # For quick mode, run a subset of tests
        results = run_quick_regression_suite(pipeline)
    elif args.performance:
        print("Running performance regression tests...")
        results = run_performance_regression_suite(pipeline)
    else:
        print("Running full regression test suite...")
        results = pipeline.run_full_regression_suite()
    
    # Generate and display report
    report = pipeline.generate_report(results)
    print("\n" + report)
    
    # Save results if requested
    if args.baseline:
        print("Updating baseline with current results...")
        # Force save as baseline
        with open(pipeline.baseline_file, 'w') as f:
            import json
            json.dump(results, f, indent=2, default=str)
        print(f"Baseline updated: {pipeline.baseline_file}")
    
    # Exit with appropriate status code
    status = results.get('summary', {}).get('overall_status', 'UNKNOWN')
    if status == 'REGRESSION_DETECTED':
        print("\n❌ REGRESSION DETECTED - Tests failed due to regressions")
        sys.exit(1)
    elif status == 'QUALITY_CONCERNS':
        print("\n⚠️  QUALITY CONCERNS - Tests passed but quality metrics below threshold")
        sys.exit(1)
    elif status == 'PASS':
        print("\n✅ ALL TESTS PASSED - No regressions detected")
        sys.exit(0)
    else:
        print(f"\n❓ UNKNOWN STATUS: {status}")
        sys.exit(2)


def run_quick_regression_suite(pipeline: RegressionTestPipeline) -> dict:
    """Run a quick subset of regression tests"""
    import time
    from datetime import datetime
    
    start_time = datetime.now()
    
    results = {
        'timestamp': start_time.isoformat(),
        'test_results': {},
        'regression_analysis': {},
        'quality_metrics': {},
        'summary': {},
        'mode': 'quick'
    }
    
    try:
        # Run only critical tests
        print("Running critical unit tests...")
        critical_components = ['calculations', 'analysis_integration', 'npv_integration']
        unit_results = {}
        
        for component in critical_components:
            try:
                result = pipeline.test_framework.run_unit_tests(component)
                unit_results[component] = {
                    'total_tests': result.total_tests,
                    'passed_tests': result.passed_tests,
                    'failed_tests': result.failed_tests,
                    'success_rate': result.passed_tests / max(result.total_tests, 1)
                }
            except Exception as e:
                unit_results[component] = {'error': str(e), 'success_rate': 0.0}
        
        results['test_results']['unit_tests'] = unit_results
        
        # Run quick accuracy validation
        print("Running accuracy validation...")
        accuracy_results = pipeline._run_accuracy_tests()
        results['test_results']['accuracy_tests'] = accuracy_results
        
        # Analyze for regressions
        regression_analysis = pipeline._analyze_regressions(results)
        results['regression_analysis'] = regression_analysis
        
        # Calculate basic quality metrics
        all_success_rates = []
        for component_data in unit_results.values():
            if 'success_rate' in component_data:
                all_success_rates.append(component_data['success_rate'])
        
        if accuracy_results.get('success_rate'):
            all_success_rates.append(accuracy_results['success_rate'])
        
        overall_success_rate = sum(all_success_rates) / len(all_success_rates) if all_success_rates else 0.0
        
        results['quality_metrics'] = {
            'overall_success_rate': overall_success_rate,
            'overall_quality_score': overall_success_rate * 0.9,  # Penalty for quick mode
            'quality_grade': pipeline._calculate_quality_grade(overall_success_rate * 0.9)
        }
        
        # Generate summary
        total_tests = sum(data.get('total_tests', 0) for data in unit_results.values())
        total_passed = sum(data.get('passed_tests', 0) for data in unit_results.values())
        total_failed = sum(data.get('failed_tests', 0) for data in unit_results.values())
        
        total_tests += accuracy_results.get('total_tests', 0)
        total_passed += accuracy_results.get('passed_tests', 0)
        total_failed += accuracy_results.get('failed_tests', 0)
        
        results['summary'] = {
            'timestamp': results['timestamp'],
            'overall_status': 'REGRESSION_DETECTED' if regression_analysis.get('regressions_detected') else 'PASS',
            'total_tests': total_tests,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'success_rate': total_passed / max(total_tests, 1),
            'mode': 'quick'
        }
        
        execution_time = datetime.now() - start_time
        results['execution_time_seconds'] = execution_time.total_seconds()
        
    except Exception as e:
        results['error'] = str(e)
        results['summary'] = {'overall_status': 'FAILED', 'total_tests': 0}
    
    return results


def run_performance_regression_suite(pipeline: RegressionTestPipeline) -> dict:
    """Run performance-focused regression tests"""
    import time
    from datetime import datetime
    
    start_time = datetime.now()
    
    results = {
        'timestamp': start_time.isoformat(),
        'performance_results': {},
        'regression_analysis': {},
        'quality_metrics': {},
        'summary': {},
        'mode': 'performance'
    }
    
    try:
        # Run comprehensive performance tests
        print("Running performance benchmarks...")
        performance_results = pipeline._run_performance_tests()
        results['performance_results'] = performance_results
        
        # Analyze performance regressions
        regression_analysis = pipeline._analyze_regressions(results)
        results['regression_analysis'] = regression_analysis
        
        # Calculate performance quality metrics
        performance_quality = []
        for component_metrics in performance_results.values():
            if isinstance(component_metrics, list):
                for metric in component_metrics:
                    if isinstance(metric, dict) and 'meets_target' in metric:
                        performance_quality.append(1.0 if metric['meets_target'] else 0.0)
        
        performance_target_rate = sum(performance_quality) / len(performance_quality) if performance_quality else 0.0
        
        results['quality_metrics'] = {
            'performance_target_rate': performance_target_rate,
            'overall_quality_score': performance_target_rate,
            'quality_grade': pipeline._calculate_quality_grade(performance_target_rate)
        }
        
        # Generate summary
        results['summary'] = {
            'timestamp': results['timestamp'],
            'overall_status': 'REGRESSION_DETECTED' if regression_analysis.get('performance_regressions') else 'PASS',
            'total_tests': len(performance_quality),
            'total_passed': sum(performance_quality),
            'total_failed': len(performance_quality) - sum(performance_quality),
            'success_rate': performance_target_rate,
            'mode': 'performance'
        }
        
        execution_time = datetime.now() - start_time
        results['execution_time_seconds'] = execution_time.total_seconds()
        
    except Exception as e:
        results['error'] = str(e)
        results['summary'] = {'overall_status': 'FAILED', 'total_tests': 0}
    
    return results


if __name__ == '__main__':
    main()