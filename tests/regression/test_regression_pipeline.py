"""
Automated Regression Testing Pipeline
Comprehensive regression testing to prevent quality degradation

This module provides:
- Automated test execution pipeline
- Regression detection and alerting
- Historical result comparison
- Performance regression monitoring
- Quality metric tracking
"""

import unittest
import json
import os
import sys
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import hashlib

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tests.framework.test_framework import get_test_framework
from src.shared.interfaces import TestSuiteResult, PerformanceMetric


class RegressionTestPipeline:
    """Automated regression testing pipeline"""
    
    def __init__(self, results_dir: str = None):
        """Initialize regression testing pipeline"""
        self.project_root = Path(project_root)
        self.results_dir = Path(results_dir) if results_dir else self.project_root / "tests" / "regression" / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.baseline_file = self.results_dir / "baseline.json"
        self.history_file = self.results_dir / "test_history.json"
        self.performance_file = self.results_dir / "performance_baseline.json"
        
        self.test_framework = get_test_framework()
        
        # Regression thresholds
        self.failure_threshold = 0.05  # 5% failure rate increase
        self.performance_threshold = 1.2  # 20% performance degradation
        self.coverage_threshold = 0.95  # 95% minimum coverage
    
    def run_full_regression_suite(self) -> Dict[str, Any]:
        """Run the complete regression test suite"""
        print("Starting comprehensive regression test suite...")
        start_time = datetime.now()
        
        results = {
            'timestamp': start_time.isoformat(),
            'test_results': {},
            'performance_results': {},
            'regression_analysis': {},
            'quality_metrics': {},
            'summary': {}
        }
        
        try:
            # 1. Run unit tests for all components
            print("Running unit tests...")
            unit_results = self._run_unit_tests()
            results['test_results']['unit_tests'] = unit_results
            
            # 2. Run integration tests
            print("Running integration tests...")
            integration_results = self._run_integration_tests()
            results['test_results']['integration_tests'] = integration_results
            
            # 3. Run accuracy validation tests
            print("Running accuracy validation...")
            accuracy_results = self._run_accuracy_tests()
            results['test_results']['accuracy_tests'] = accuracy_results
            
            # 4. Run performance benchmarks
            print("Running performance benchmarks...")
            performance_results = self._run_performance_tests()
            results['performance_results'] = performance_results
            
            # 5. Run data validation tests
            print("Running data validation tests...")
            validation_results = self._run_validation_tests()
            results['test_results']['validation_tests'] = validation_results
            
            # 6. Analyze for regressions
            print("Analyzing for regressions...")
            regression_analysis = self._analyze_regressions(results)
            results['regression_analysis'] = regression_analysis
            
            # 7. Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(results)
            results['quality_metrics'] = quality_metrics
            
            # 8. Generate summary
            summary = self._generate_summary(results)
            results['summary'] = summary
            
            # 9. Save results
            self._save_results(results)
            
            execution_time = datetime.now() - start_time
            results['execution_time_seconds'] = execution_time.total_seconds()
            
            print(f"Regression test suite completed in {execution_time}")
            
        except Exception as e:
            results['error'] = str(e)
            results['status'] = 'FAILED'
            print(f"Regression test suite failed: {e}")
        
        return results
    
    def _run_unit_tests(self) -> Dict[str, TestSuiteResult]:
        """Run unit tests for all components"""
        unit_results = {}
        
        # Get all available test modules
        test_modules = self.test_framework.test_modules
        
        for component_name in test_modules.keys():
            try:
                result = self.test_framework.run_unit_tests(component_name)
                unit_results[component_name] = {
                    'total_tests': result.total_tests,
                    'passed_tests': result.passed_tests,
                    'failed_tests': result.failed_tests,
                    'coverage_percentage': result.coverage_percentage,
                    'execution_time_ms': result.execution_time_ms,
                    'success_rate': result.passed_tests / max(result.total_tests, 1)
                }
            except Exception as e:
                unit_results[component_name] = {
                    'error': str(e),
                    'total_tests': 0,
                    'passed_tests': 0,
                    'failed_tests': 0,
                    'coverage_percentage': 0.0,
                    'execution_time_ms': 0.0,
                    'success_rate': 0.0
                }
        
        return unit_results
    
    def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        try:
            result = self.test_framework.run_integration_tests()
            return {
                'total_tests': result.total_tests,
                'passed_tests': result.passed_tests,
                'failed_tests': result.failed_tests,
                'coverage_percentage': result.coverage_percentage,
                'execution_time_ms': result.execution_time_ms,
                'success_rate': result.passed_tests / max(result.total_tests, 1)
            }
        except Exception as e:
            return {
                'error': str(e),
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'coverage_percentage': 0.0,
                'execution_time_ms': 0.0,
                'success_rate': 0.0
            }
    
    def _run_accuracy_tests(self) -> Dict[str, Any]:
        """Run financial accuracy validation tests"""
        try:
            # Import accuracy test cases
            from tests.accuracy.test_financial_accuracy import TestNPVAccuracy
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromTestCase(TestNPVAccuracy)
            
            # Run tests
            runner = unittest.TextTestRunner(stream=open(os.devnull, 'w'))
            result = runner.run(suite)
            
            return {
                'total_tests': result.testsRun,
                'passed_tests': result.testsRun - len(result.failures) - len(result.errors),
                'failed_tests': len(result.failures) + len(result.errors),
                'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1),
                'accuracy_validated': len(result.failures) + len(result.errors) == 0
            }
        except Exception as e:
            return {
                'error': str(e),
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'success_rate': 0.0,
                'accuracy_validated': False
            }
    
    def _run_performance_tests(self) -> Dict[str, List[PerformanceMetric]]:
        """Run performance benchmark tests"""
        performance_results = {}
        
        # Test key components
        components_to_benchmark = ['calculations', 'analysis', 'integration', 'export']
        
        for component in components_to_benchmark:
            try:
                metrics = self.test_framework.benchmark_performance(component)
                performance_results[component] = [
                    {
                        'metric_name': m.metric_name,
                        'value': m.value,
                        'unit': m.unit,
                        'target_value': m.target_value,
                        'meets_target': m.meets_target,
                        'timestamp': m.timestamp.isoformat()
                    }
                    for m in metrics
                ]
            except Exception as e:
                performance_results[component] = {
                    'error': str(e)
                }
        
        return performance_results
    
    def _run_validation_tests(self) -> Dict[str, Any]:
        """Run data validation tests"""
        try:
            from tests.data_validation_tests.test_data_validation import TestInputValidation
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromTestCase(TestInputValidation)
            
            # Run tests
            runner = unittest.TextTestRunner(stream=open(os.devnull, 'w'))
            result = runner.run(suite)
            
            return {
                'total_tests': result.testsRun,
                'passed_tests': result.testsRun - len(result.failures) - len(result.errors),
                'failed_tests': len(result.failures) + len(result.errors),
                'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1),
                'validation_passed': len(result.failures) + len(result.errors) == 0
            }
        except Exception as e:
            return {
                'error': str(e),
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'success_rate': 0.0,
                'validation_passed': False
            }
    
    def _analyze_regressions(self, current_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current results against baseline for regressions"""
        regression_analysis = {
            'regressions_detected': [],
            'performance_regressions': [],
            'improvements': [],
            'overall_status': 'PASS'
        }
        
        # Load baseline if it exists
        baseline = self._load_baseline()
        if not baseline:
            regression_analysis['status'] = 'NO_BASELINE'
            return regression_analysis
        
        # Compare test success rates
        current_unit = current_results.get('test_results', {}).get('unit_tests', {})
        baseline_unit = baseline.get('test_results', {}).get('unit_tests', {})
        
        for component, current_data in current_unit.items():
            if component in baseline_unit:
                current_rate = current_data.get('success_rate', 0)
                baseline_rate = baseline_unit[component].get('success_rate', 0)
                
                if baseline_rate - current_rate > self.failure_threshold:
                    regression_analysis['regressions_detected'].append({
                        'component': component,
                        'type': 'test_failure_rate',
                        'current_rate': current_rate,
                        'baseline_rate': baseline_rate,
                        'degradation': baseline_rate - current_rate
                    })
        
        # Compare performance metrics
        current_perf = current_results.get('performance_results', {})
        baseline_perf = baseline.get('performance_results', {})
        
        for component, current_metrics in current_perf.items():
            if component in baseline_perf and not isinstance(current_metrics, dict) or 'error' not in current_metrics:
                baseline_metrics = baseline_perf[component]
                
                if isinstance(current_metrics, list) and isinstance(baseline_metrics, list):
                    for current_metric in current_metrics:
                        # Find corresponding baseline metric
                        baseline_metric = next(
                            (bm for bm in baseline_metrics if bm['metric_name'] == current_metric['metric_name']),
                            None
                        )
                        
                        if baseline_metric:
                            current_value = current_metric['value']
                            baseline_value = baseline_metric['value']
                            
                            if current_value > baseline_value * self.performance_threshold:
                                regression_analysis['performance_regressions'].append({
                                    'component': component,
                                    'metric': current_metric['metric_name'],
                                    'current_value': current_value,
                                    'baseline_value': baseline_value,
                                    'degradation_ratio': current_value / baseline_value
                                })
        
        # Set overall status
        if regression_analysis['regressions_detected'] or regression_analysis['performance_regressions']:
            regression_analysis['overall_status'] = 'REGRESSION_DETECTED'
        
        return regression_analysis
    
    def _calculate_quality_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall quality metrics"""
        quality_metrics = {}
        
        # Overall test coverage
        unit_tests = results.get('test_results', {}).get('unit_tests', {})
        if unit_tests:
            coverages = [data.get('coverage_percentage', 0) for data in unit_tests.values() 
                        if isinstance(data, dict) and 'coverage_percentage' in data]
            if coverages:
                quality_metrics['average_coverage'] = sum(coverages) / len(coverages)
                quality_metrics['min_coverage'] = min(coverages)
                quality_metrics['coverage_target_met'] = min(coverages) >= (self.coverage_threshold * 100)
        
        # Overall success rate
        all_success_rates = []
        for test_category in results.get('test_results', {}).values():
            if isinstance(test_category, dict):
                if 'success_rate' in test_category:
                    all_success_rates.append(test_category['success_rate'])
                elif isinstance(test_category, dict):
                    for component_data in test_category.values():
                        if isinstance(component_data, dict) and 'success_rate' in component_data:
                            all_success_rates.append(component_data['success_rate'])
        
        if all_success_rates:
            quality_metrics['overall_success_rate'] = sum(all_success_rates) / len(all_success_rates)
            quality_metrics['min_success_rate'] = min(all_success_rates)
        
        # Performance quality
        perf_results = results.get('performance_results', {})
        performance_quality = []
        
        for component_metrics in perf_results.values():
            if isinstance(component_metrics, list):
                for metric in component_metrics:
                    if isinstance(metric, dict) and 'meets_target' in metric:
                        performance_quality.append(1.0 if metric['meets_target'] else 0.0)
        
        if performance_quality:
            quality_metrics['performance_target_rate'] = sum(performance_quality) / len(performance_quality)
        
        # Quality score (weighted combination)
        weights = {
            'success_rate': 0.4,
            'coverage': 0.3,
            'performance': 0.3
        }
        
        quality_score = 0.0
        if 'overall_success_rate' in quality_metrics:
            quality_score += weights['success_rate'] * quality_metrics['overall_success_rate']
        
        if 'average_coverage' in quality_metrics:
            quality_score += weights['coverage'] * (quality_metrics['average_coverage'] / 100)
        
        if 'performance_target_rate' in quality_metrics:
            quality_score += weights['performance'] * quality_metrics['performance_target_rate']
        
        quality_metrics['overall_quality_score'] = quality_score
        quality_metrics['quality_grade'] = self._calculate_quality_grade(quality_score)
        
        return quality_metrics
    
    def _calculate_quality_grade(self, score: float) -> str:
        """Calculate quality grade from score"""
        if score >= 0.95:
            return 'A+'
        elif score >= 0.90:
            return 'A'
        elif score >= 0.85:
            return 'B+'
        elif score >= 0.80:
            return 'B'
        elif score >= 0.75:
            return 'C+'
        elif score >= 0.70:
            return 'C'
        else:
            return 'F'
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of test results"""
        summary = {
            'timestamp': results['timestamp'],
            'overall_status': 'PASS',
            'total_tests': 0,
            'total_passed': 0,
            'total_failed': 0,
            'key_findings': [],
            'recommendations': []
        }
        
        # Count total tests
        for test_category in results.get('test_results', {}).values():
            if isinstance(test_category, dict):
                if 'total_tests' in test_category:
                    summary['total_tests'] += test_category.get('total_tests', 0)
                    summary['total_passed'] += test_category.get('passed_tests', 0)
                    summary['total_failed'] += test_category.get('failed_tests', 0)
                else:
                    # Unit tests (nested structure)
                    for component_data in test_category.values():
                        if isinstance(component_data, dict):
                            summary['total_tests'] += component_data.get('total_tests', 0)
                            summary['total_passed'] += component_data.get('passed_tests', 0)
                            summary['total_failed'] += component_data.get('failed_tests', 0)
        
        # Analyze regression results
        regression_analysis = results.get('regression_analysis', {})
        if regression_analysis.get('overall_status') == 'REGRESSION_DETECTED':
            summary['overall_status'] = 'REGRESSION_DETECTED'
            summary['key_findings'].append("Performance or quality regression detected")
        
        # Analyze quality metrics
        quality_metrics = results.get('quality_metrics', {})
        if quality_metrics.get('overall_quality_score', 0) < 0.8:
            summary['overall_status'] = 'QUALITY_CONCERNS'
            summary['key_findings'].append("Overall quality score below acceptable threshold")
        
        # Add success rate
        if summary['total_tests'] > 0:
            summary['success_rate'] = summary['total_passed'] / summary['total_tests']
        else:
            summary['success_rate'] = 0.0
        
        # Generate recommendations
        if summary['total_failed'] > 0:
            summary['recommendations'].append(f"Address {summary['total_failed']} failing tests")
        
        if quality_metrics.get('min_coverage', 100) < (self.coverage_threshold * 100):
            summary['recommendations'].append("Improve test coverage to meet 95% target")
        
        if regression_analysis.get('performance_regressions'):
            summary['recommendations'].append("Investigate performance regressions")
        
        return summary
    
    def _load_baseline(self) -> Optional[Dict[str, Any]]:
        """Load baseline test results"""
        try:
            if self.baseline_file.exists():
                with open(self.baseline_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load baseline: {e}")
        return None
    
    def _save_results(self, results: Dict[str, Any]):
        """Save test results and update history"""
        # Save current results as potential new baseline
        result_hash = self._calculate_result_hash(results)
        result_file = self.results_dir / f"results_{result_hash[:8]}.json"
        
        try:
            with open(result_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save detailed results: {e}")
        
        # Update history
        try:
            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            
            # Add current run to history
            history_entry = {
                'timestamp': results['timestamp'],
                'overall_status': results.get('summary', {}).get('overall_status', 'UNKNOWN'),
                'total_tests': results.get('summary', {}).get('total_tests', 0),
                'success_rate': results.get('summary', {}).get('success_rate', 0.0),
                'quality_score': results.get('quality_metrics', {}).get('overall_quality_score', 0.0),
                'execution_time': results.get('execution_time_seconds', 0.0),
                'result_file': result_file.name
            }
            
            history.append(history_entry)
            
            # Keep only last 100 entries
            if len(history) > 100:
                history = history[-100:]
            
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Warning: Could not update test history: {e}")
        
        # Update baseline if this run is successful
        if results.get('summary', {}).get('overall_status') == 'PASS':
            try:
                with open(self.baseline_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
            except Exception as e:
                print(f"Warning: Could not update baseline: {e}")
    
    def _calculate_result_hash(self, results: Dict[str, Any]) -> str:
        """Calculate hash of results for unique identification"""
        # Create a simplified version of results for hashing
        hash_data = {
            'timestamp': results.get('timestamp'),
            'summary': results.get('summary', {}),
            'quality_metrics': results.get('quality_metrics', {})
        }
        
        result_str = json.dumps(hash_data, sort_keys=True, default=str)
        return hashlib.md5(result_str.encode()).hexdigest()
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable test report"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("REGRESSION TEST SUITE REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Executive Summary
        summary = results.get('summary', {})
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Timestamp: {summary.get('timestamp', 'Unknown')}")
        report_lines.append(f"Overall Status: {summary.get('overall_status', 'Unknown')}")
        report_lines.append(f"Total Tests: {summary.get('total_tests', 0)}")
        report_lines.append(f"Tests Passed: {summary.get('total_passed', 0)}")
        report_lines.append(f"Tests Failed: {summary.get('total_failed', 0)}")
        report_lines.append(f"Success Rate: {summary.get('success_rate', 0):.1%}")
        report_lines.append("")
        
        # Quality Metrics
        quality = results.get('quality_metrics', {})
        if quality:
            report_lines.append("QUALITY METRICS")
            report_lines.append("-" * 40)
            report_lines.append(f"Overall Quality Score: {quality.get('overall_quality_score', 0):.3f}")
            report_lines.append(f"Quality Grade: {quality.get('quality_grade', 'Unknown')}")
            report_lines.append(f"Average Coverage: {quality.get('average_coverage', 0):.1f}%")
            report_lines.append(f"Min Coverage: {quality.get('min_coverage', 0):.1f}%")
            report_lines.append(f"Performance Target Rate: {quality.get('performance_target_rate', 0):.1%}")
            report_lines.append("")
        
        # Regression Analysis
        regression = results.get('regression_analysis', {})
        if regression.get('regressions_detected') or regression.get('performance_regressions'):
            report_lines.append("REGRESSIONS DETECTED")
            report_lines.append("-" * 40)
            
            for reg in regression.get('regressions_detected', []):
                report_lines.append(f"• {reg['component']}: {reg['type']} degraded by {reg['degradation']:.1%}")
            
            for reg in regression.get('performance_regressions', []):
                report_lines.append(f"• {reg['component']}.{reg['metric']}: {reg['degradation_ratio']:.1f}x slower")
            
            report_lines.append("")
        
        # Recommendations
        recommendations = summary.get('recommendations', [])
        if recommendations:
            report_lines.append("RECOMMENDATIONS")
            report_lines.append("-" * 40)
            for rec in recommendations:
                report_lines.append(f"• {rec}")
            report_lines.append("")
        
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)


class TestRegressionPipeline(unittest.TestCase):
    """Test the regression testing pipeline itself"""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        pipeline = RegressionTestPipeline()
        
        self.assertIsNotNone(pipeline.test_framework)
        self.assertTrue(pipeline.results_dir.exists())
        self.assertGreater(pipeline.coverage_threshold, 0)
        self.assertGreater(pipeline.performance_threshold, 1.0)
    
    def test_quality_grade_calculation(self):
        """Test quality grade calculation"""
        pipeline = RegressionTestPipeline()
        
        test_cases = [
            (0.98, 'A+'),
            (0.92, 'A'),
            (0.87, 'B+'),
            (0.82, 'B'),
            (0.77, 'C+'),
            (0.72, 'C'),
            (0.60, 'F')
        ]
        
        for score, expected_grade in test_cases:
            actual_grade = pipeline._calculate_quality_grade(score)
            self.assertEqual(actual_grade, expected_grade, 
                           f"Score {score} should be grade {expected_grade}, got {actual_grade}")
    
    def test_report_generation(self):
        """Test report generation"""
        pipeline = RegressionTestPipeline()
        
        mock_results = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'overall_status': 'PASS',
                'total_tests': 150,
                'total_passed': 145,
                'total_failed': 5,
                'success_rate': 0.967
            },
            'quality_metrics': {
                'overall_quality_score': 0.892,
                'quality_grade': 'A',
                'average_coverage': 96.5,
                'min_coverage': 89.2
            },
            'regression_analysis': {
                'regressions_detected': [],
                'performance_regressions': []
            }
        }
        
        report = pipeline.generate_report(mock_results)
        
        self.assertIn("REGRESSION TEST SUITE REPORT", report)
        self.assertIn("EXECUTIVE SUMMARY", report)
        self.assertIn("QUALITY METRICS", report)
        self.assertIn("Total Tests: 150", report)
        self.assertIn("Quality Grade: A", report)


if __name__ == '__main__':
    # Can be run as standalone regression pipeline or as unit tests
    if len(sys.argv) > 1 and sys.argv[1] == 'run-pipeline':
        # Run regression pipeline
        pipeline = RegressionTestPipeline()
        results = pipeline.run_full_regression_suite()
        
        # Print report
        report = pipeline.generate_report(results)
        print(report)
        
        # Exit with appropriate code
        status = results.get('summary', {}).get('overall_status', 'UNKNOWN')
        if status in ['REGRESSION_DETECTED', 'QUALITY_CONCERNS']:
            sys.exit(1)
        elif status == 'PASS':
            sys.exit(0)
        else:
            sys.exit(2)  # Unknown status
    else:
        # Run as unit tests
        unittest.main(verbosity=2)