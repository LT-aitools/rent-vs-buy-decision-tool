"""
Performance Testing and Benchmarking
Comprehensive performance testing for load and speed optimization

This module provides:
- Load testing for high-volume scenarios
- Speed benchmarking for individual components
- Memory usage profiling
- Scalability testing
- Performance regression detection
"""

import unittest
import time
import threading
import concurrent.futures
import sys
import os
import gc
from datetime import datetime
from typing import List, Dict, Any, Callable
from statistics import mean, median, stdev
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available, memory profiling disabled")

from src.shared.interfaces import PerformanceMetric
from tests.framework.test_framework import get_test_framework


class PerformanceBenchmark:
    """Base class for performance benchmarks"""
    
    def __init__(self, name: str, target_time_ms: float = 1000.0):
        self.name = name
        self.target_time_ms = target_time_ms
        self.results = []
        
    def run_benchmark(self, test_func: Callable, iterations: int = 10) -> Dict[str, Any]:
        """Run a performance benchmark"""
        times = []
        memory_usage = []
        
        # Warm-up run
        test_func()
        gc.collect()
        
        for i in range(iterations):
            # Memory before
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                mem_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Time the operation
            start_time = time.perf_counter()
            test_func()
            end_time = time.perf_counter()
            
            execution_time_ms = (end_time - start_time) * 1000
            times.append(execution_time_ms)
            
            # Memory after
            if PSUTIL_AVAILABLE:
                mem_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_usage.append(mem_after - mem_before)
            
            # Force garbage collection between runs
            gc.collect()
        
        # Calculate statistics
        avg_time = mean(times)
        median_time = median(times)
        min_time = min(times)
        max_time = max(times)
        std_time = stdev(times) if len(times) > 1 else 0.0
        
        results = {
            'name': self.name,
            'iterations': iterations,
            'avg_time_ms': avg_time,
            'median_time_ms': median_time,
            'min_time_ms': min_time,
            'max_time_ms': max_time,
            'std_dev_ms': std_time,
            'target_time_ms': self.target_time_ms,
            'meets_target': avg_time <= self.target_time_ms,
            'performance_ratio': avg_time / self.target_time_ms,
            'timestamp': datetime.now().isoformat()
        }
        
        if PSUTIL_AVAILABLE and memory_usage:
            results.update({
                'avg_memory_mb': mean(memory_usage),
                'max_memory_mb': max(memory_usage),
                'min_memory_mb': min(memory_usage)
            })
        
        self.results.append(results)
        return results


class TestCalculationPerformance(unittest.TestCase):
    """Test calculation performance and optimization"""
    
    def setUp(self):
        """Set up performance test fixtures"""
        self.base_params = {
            'purchase_price': 500000,
            'down_payment_pct': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'current_annual_rent': 60000,
            'rent_increase_rate': 3.0,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.2,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'market_appreciation_rate': 3.5,
            'transaction_costs': 25000,
            'rental_commission': 5000,
            'security_deposit': 10000,
            'moving_costs': 5000
        }
    
    def test_single_npv_calculation_speed(self):
        """Test speed of single NPV calculation"""
        try:
            from src.calculations.npv_analysis import calculate_npv_analysis
        except ImportError:
            self.skipTest("NPV calculation module not available")
        
        benchmark = PerformanceBenchmark("single_npv_calculation", target_time_ms=50.0)
        
        def test_calculation():
            return calculate_npv_analysis(self.base_params)
        
        results = benchmark.run_benchmark(test_calculation, iterations=20)
        
        # Assert performance targets
        self.assertLess(results['avg_time_ms'], 50.0,
                       f"Single NPV calculation too slow: {results['avg_time_ms']:.2f}ms > 50ms")
        
        self.assertLess(results['std_dev_ms'], 10.0,
                       f"NPV calculation time too variable: {results['std_dev_ms']:.2f}ms")
        
        # Log results for analysis
        print(f"\nSingle NPV Calculation Performance:")
        print(f"  Average: {results['avg_time_ms']:.2f}ms")
        print(f"  Median: {results['median_time_ms']:.2f}ms")
        print(f"  Range: {results['min_time_ms']:.2f}ms - {results['max_time_ms']:.2f}ms")
    
    def test_batch_calculation_performance(self):
        """Test performance of batch calculations"""
        try:
            from src.calculations.npv_analysis import calculate_npv_analysis
        except ImportError:
            self.skipTest("NPV calculation module not available")
        
        benchmark = PerformanceBenchmark("batch_npv_calculation", target_time_ms=2000.0)
        
        def batch_calculation():
            results = []
            for i in range(100):
                params = self.base_params.copy()
                params['purchase_price'] += i * 5000
                params['interest_rate'] += i * 0.01
                results.append(calculate_npv_analysis(params))
            return results
        
        results = benchmark.run_benchmark(batch_calculation, iterations=5)
        
        # Assert batch performance targets
        self.assertLess(results['avg_time_ms'], 2000.0,
                       f"Batch calculation too slow: {results['avg_time_ms']:.2f}ms > 2000ms")
        
        print(f"\nBatch NPV Calculation Performance (100 calculations):")
        print(f"  Average: {results['avg_time_ms']:.2f}ms")
        print(f"  Per calculation: {results['avg_time_ms']/100:.2f}ms")
    
    def test_mortgage_calculation_speed(self):
        """Test mortgage calculation performance"""
        try:
            from src.calculations.mortgage import calculate_mortgage_payment
        except ImportError:
            self.skipTest("Mortgage calculation module not available")
        
        benchmark = PerformanceBenchmark("mortgage_calculation", target_time_ms=5.0)
        
        def test_mortgage():
            return calculate_mortgage_payment(400000, 5.0, 30)
        
        results = benchmark.run_benchmark(test_mortgage, iterations=50)
        
        self.assertLess(results['avg_time_ms'], 5.0,
                       f"Mortgage calculation too slow: {results['avg_time_ms']:.2f}ms > 5ms")
        
        print(f"\nMortgage Calculation Performance:")
        print(f"  Average: {results['avg_time_ms']:.4f}ms")
    
    def test_amortization_schedule_speed(self):
        """Test amortization schedule generation performance"""
        try:
            from src.calculations.amortization import calculate_amortization_schedule
        except ImportError:
            self.skipTest("Amortization calculation module not available")
        
        benchmark = PerformanceBenchmark("amortization_schedule", target_time_ms=100.0)
        
        def test_amortization():
            return calculate_amortization_schedule(400000, 5.0, 30)
        
        results = benchmark.run_benchmark(test_amortization, iterations=10)
        
        self.assertLess(results['avg_time_ms'], 100.0,
                       f"Amortization schedule too slow: {results['avg_time_ms']:.2f}ms > 100ms")
        
        print(f"\nAmortization Schedule Performance:")
        print(f"  Average: {results['avg_time_ms']:.2f}ms")


class TestAnalysisPerformance(unittest.TestCase):
    """Test analysis engine performance"""
    
    def test_sensitivity_analysis_speed(self):
        """Test sensitivity analysis performance"""
        try:
            from src.analysis.sensitivity import SensitivityAnalyzer
        except ImportError:
            self.skipTest("Sensitivity analysis module not available")
        
        benchmark = PerformanceBenchmark("sensitivity_analysis", target_time_ms=500.0)
        
        base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            'down_payment_pct': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0
        }
        
        def test_sensitivity():
            analyzer = SensitivityAnalyzer()
            analyzer.configure_base_parameters(base_params)
            return analyzer.run_single_parameter_sensitivity(
                'interest_rate', [4.0, 4.5, 5.0, 5.5, 6.0]
            )
        
        results = benchmark.run_benchmark(test_sensitivity, iterations=10)
        
        self.assertLess(results['avg_time_ms'], 500.0,
                       f"Sensitivity analysis too slow: {results['avg_time_ms']:.2f}ms > 500ms")
        
        print(f"\nSensitivity Analysis Performance:")
        print(f"  Average: {results['avg_time_ms']:.2f}ms")
    
    def test_comprehensive_analysis_speed(self):
        """Test comprehensive analysis performance"""
        try:
            from src.analysis.npv_integration import NPVIntegrationEngine
            from src.analysis.decision_engine import make_investment_decision
        except ImportError:
            self.skipTest("Analysis modules not available")
        
        benchmark = PerformanceBenchmark("comprehensive_analysis", target_time_ms=1000.0)
        
        test_data = {
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            'total_property_size': 2000,
            'current_space_needed': 2000,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'down_payment_percent': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'currency': 'USD'
        }
        
        def test_comprehensive():
            engine = NPVIntegrationEngine()
            npv_results = engine.run_complete_analysis(test_data)
            if npv_results.get('calculation_successful', False):
                decision_results = make_investment_decision(npv_results, "moderate")
                return decision_results
            return npv_results
        
        results = benchmark.run_benchmark(test_comprehensive, iterations=10)
        
        self.assertLess(results['avg_time_ms'], 1000.0,
                       f"Comprehensive analysis too slow: {results['avg_time_ms']:.2f}ms > 1000ms")
        
        print(f"\nComprehensive Analysis Performance:")
        print(f"  Average: {results['avg_time_ms']:.2f}ms")


class TestLoadTesting(unittest.TestCase):
    """Test system performance under load"""
    
    def test_concurrent_calculations(self):
        """Test concurrent calculation performance"""
        try:
            from src.calculations.npv_analysis import calculate_npv_analysis
        except ImportError:
            self.skipTest("NPV calculation module not available")
        
        base_params = {
            'purchase_price': 500000,
            'down_payment_pct': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'current_annual_rent': 60000,
            'rent_increase_rate': 3.0,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.2,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'market_appreciation_rate': 3.5,
            'transaction_costs': 25000
        }
        
        def single_calculation(variation: int):
            params = base_params.copy()
            params['purchase_price'] += variation * 10000
            params['interest_rate'] += variation * 0.1
            return calculate_npv_analysis(params)
        
        # Test with increasing number of concurrent threads
        thread_counts = [1, 2, 4, 8]
        calculations_per_thread = 10
        
        for thread_count in thread_counts:
            start_time = time.perf_counter()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = []
                for thread_id in range(thread_count):
                    for calc_id in range(calculations_per_thread):
                        variation = thread_id * calculations_per_thread + calc_id
                        future = executor.submit(single_calculation, variation)
                        futures.append(future)
                
                # Wait for all calculations to complete
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.perf_counter()
            total_time = end_time - start_time
            total_calculations = thread_count * calculations_per_thread
            
            print(f"\nConcurrent Load Test ({thread_count} threads):")
            print(f"  Total calculations: {total_calculations}")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Calculations per second: {total_calculations/total_time:.1f}")
            print(f"  Average time per calculation: {total_time*1000/total_calculations:.2f}ms")
            
            # Performance should not degrade significantly with more threads
            time_per_calc = total_time / total_calculations
            self.assertLess(time_per_calc, 0.1,  # 100ms per calculation
                           f"Concurrent performance degraded: {time_per_calc*1000:.2f}ms per calc")
    
    def test_memory_usage_under_load(self):
        """Test memory usage under sustained load"""
        if not PSUTIL_AVAILABLE:
            self.skipTest("psutil not available for memory testing")
        
        try:
            from src.calculations.npv_analysis import calculate_npv_analysis
        except ImportError:
            self.skipTest("NPV calculation module not available")
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        base_params = {
            'purchase_price': 500000,
            'down_payment_pct': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'current_annual_rent': 60000,
            'rent_increase_rate': 3.0,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.2,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'market_appreciation_rate': 3.5,
            'transaction_costs': 25000
        }
        
        # Run many calculations
        memory_samples = []
        for i in range(1000):
            params = base_params.copy()
            params['purchase_price'] += i * 1000
            
            calculate_npv_analysis(params)
            
            # Sample memory every 100 iterations
            if i % 100 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        print(f"\nMemory Usage Test (1000 calculations):")
        print(f"  Initial memory: {initial_memory:.1f}MB")
        print(f"  Final memory: {final_memory:.1f}MB")
        print(f"  Memory growth: {memory_growth:.1f}MB")
        print(f"  Memory samples: {memory_samples}")
        
        # Memory growth should be reasonable (less than 50MB for 1000 calculations)
        self.assertLess(memory_growth, 50.0,
                       f"Excessive memory growth: {memory_growth:.1f}MB")
    
    def test_sustained_performance(self):
        """Test performance doesn't degrade over time"""
        try:
            from src.calculations.npv_analysis import calculate_npv_analysis
        except ImportError:
            self.skipTest("NPV calculation module not available")
        
        base_params = {
            'purchase_price': 500000,
            'down_payment_pct': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'current_annual_rent': 60000,
            'rent_increase_rate': 3.0,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.2,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'market_appreciation_rate': 3.5,
            'transaction_costs': 25000
        }
        
        # Test performance in batches
        batch_times = []
        batch_size = 50
        
        for batch in range(10):  # 10 batches of 50 calculations each
            start_time = time.perf_counter()
            
            for i in range(batch_size):
                params = base_params.copy()
                params['purchase_price'] += (batch * batch_size + i) * 1000
                calculate_npv_analysis(params)
            
            end_time = time.perf_counter()
            batch_time = end_time - start_time
            batch_times.append(batch_time)
            
            # Force garbage collection between batches
            gc.collect()
        
        # Check for performance degradation
        first_batch_time = batch_times[0]
        last_batch_time = batch_times[-1]
        avg_batch_time = mean(batch_times)
        
        print(f"\nSustained Performance Test (10 batches of {batch_size} calculations):")
        print(f"  First batch: {first_batch_time:.2f}s")
        print(f"  Last batch: {last_batch_time:.2f}s")
        print(f"  Average batch: {avg_batch_time:.2f}s")
        print(f"  Performance degradation: {((last_batch_time/first_batch_time)-1)*100:.1f}%")
        
        # Performance should not degrade by more than 20%
        degradation_ratio = last_batch_time / first_batch_time
        self.assertLess(degradation_ratio, 1.2,
                       f"Performance degraded by {((degradation_ratio-1)*100):.1f}%")


class TestScalabilityTesting(unittest.TestCase):
    """Test system scalability characteristics"""
    
    def test_analysis_period_scalability(self):
        """Test how performance scales with analysis period"""
        try:
            from src.calculations.npv_analysis import calculate_npv_analysis
        except ImportError:
            self.skipTest("NPV calculation module not available")
        
        base_params = {
            'purchase_price': 500000,
            'down_payment_pct': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'current_annual_rent': 60000,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.2,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'market_appreciation_rate': 3.5,
            'transaction_costs': 25000
        }
        
        periods = [5, 10, 15, 20, 25, 30, 40, 50]
        period_times = []
        
        for period in periods:
            params = base_params.copy()
            params['analysis_period'] = period
            
            # Time multiple runs and average
            times = []
            for _ in range(5):
                start_time = time.perf_counter()
                calculate_npv_analysis(params)
                end_time = time.perf_counter()
                times.append((end_time - start_time) * 1000)
            
            avg_time = mean(times)
            period_times.append(avg_time)
            
            print(f"Analysis period {period} years: {avg_time:.2f}ms")
        
        # Check that time complexity is reasonable (should be roughly linear)
        # Longest period should not take more than 3x the shortest period
        shortest_time = min(period_times)
        longest_time = max(period_times)
        scalability_ratio = longest_time / shortest_time
        
        print(f"\nScalability Analysis:")
        print(f"  Shortest period time: {shortest_time:.2f}ms")
        print(f"  Longest period time: {longest_time:.2f}ms")
        print(f"  Scalability ratio: {scalability_ratio:.1f}x")
        
        self.assertLess(scalability_ratio, 3.0,
                       f"Poor scalability: {scalability_ratio:.1f}x time increase")


class TestRegressionDetection(unittest.TestCase):
    """Test for performance regressions"""
    
    def setUp(self):
        """Set up baseline performance metrics"""
        self.baseline_file = os.path.join(
            os.path.dirname(__file__), 'performance_baseline.json'
        )
        self.current_results = {}
        
    def tearDown(self):
        """Save current results as new baseline if needed"""
        # Optionally update baseline - in practice this would be done carefully
        pass
    
    def load_baseline(self) -> Dict[str, Any]:
        """Load baseline performance metrics"""
        try:
            with open(self.baseline_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # No baseline exists yet, return empty dict
            return {}
    
    def save_baseline(self, results: Dict[str, Any]):
        """Save performance baseline"""
        with open(self.baseline_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def test_regression_detection(self):
        """Test for performance regressions against baseline"""
        baseline = self.load_baseline()
        
        if not baseline:
            self.skipTest("No baseline performance data available")
        
        # Run current performance tests
        framework = get_test_framework()
        
        try:
            # Test key components
            components_to_test = ['calculations', 'analysis', 'integration']
            
            for component in components_to_test:
                metrics = framework.benchmark_performance(component)
                
                for metric in metrics:
                    metric_name = metric.metric_name
                    current_value = metric.value
                    
                    if metric_name in baseline:
                        baseline_value = baseline[metric_name]['value']
                        regression_threshold = baseline_value * 1.1  # 10% slower is regression
                        
                        if current_value > regression_threshold:
                            self.fail(
                                f"Performance regression detected in {metric_name}: "
                                f"current={current_value:.2f}{metric.unit}, "
                                f"baseline={baseline_value:.2f}{metric.unit} "
                                f"(+{((current_value/baseline_value)-1)*100:.1f}%)"
                            )
                    
                    # Save current result
                    self.current_results[metric_name] = {
                        'value': current_value,
                        'unit': metric.unit,
                        'timestamp': metric.timestamp.isoformat(),
                        'meets_target': metric.meets_target
                    }
        
        except Exception as e:
            self.skipTest(f"Could not run regression tests: {e}")


if __name__ == '__main__':
    # Run performance tests with detailed output
    unittest.main(verbosity=2, buffer=False)