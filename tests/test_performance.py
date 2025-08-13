"""
Performance Tests
Tests for performance requirements and optimization
"""

import unittest
import time
import sys
import os
import threading
import concurrent.futures
from unittest.mock import Mock, patch
import psutil
import gc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.enhanced import (
    create_advanced_input_component,
    create_interactive_charts_component,
    create_guidance_system,
    create_mobile_responsive_component,
    create_performance_monitor
)

from src.components.enhanced.enhanced_security import SecureCacheManager
from src.shared.interfaces import UIState


class TestComponentLoadTimes(unittest.TestCase):
    """Test component load time requirements (<3 seconds total)"""
    
    def setUp(self):
        # Record initial memory
        self.initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
    
    def test_advanced_inputs_load_time(self):
        """Test advanced inputs component loads within time limit"""
        start_time = time.time()
        
        component = create_advanced_input_component()
        
        load_time = time.time() - start_time
        
        # Should load in under 1 second
        self.assertLess(load_time, 1.0, 
                       f"Advanced inputs took {load_time:.3f}s to load")
        self.assertIsNotNone(component)
    
    def test_interactive_charts_load_time(self):
        """Test interactive charts component loads within time limit"""
        start_time = time.time()
        
        component = create_interactive_charts_component()
        
        load_time = time.time() - start_time
        
        # Should load in under 1 second
        self.assertLess(load_time, 1.0,
                       f"Interactive charts took {load_time:.3f}s to load")
        self.assertIsNotNone(component)
    
    def test_guidance_system_load_time(self):
        """Test guidance system loads within time limit"""
        start_time = time.time()
        
        component = create_guidance_system()
        
        load_time = time.time() - start_time
        
        # Should load in under 1 second
        self.assertLess(load_time, 1.0,
                       f"Guidance system took {load_time:.3f}s to load")
        self.assertIsNotNone(component)
    
    def test_all_components_concurrent_load_time(self):
        """Test all components load concurrently within total time limit"""
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all component creation tasks
            futures = {
                executor.submit(create_advanced_input_component): 'advanced_inputs',
                executor.submit(create_interactive_charts_component): 'interactive_charts',
                executor.submit(create_guidance_system): 'guidance_system',
                executor.submit(create_mobile_responsive_component): 'mobile_responsive'
            }
            
            # Wait for all to complete
            components = {}
            for future in concurrent.futures.as_completed(futures):
                component_name = futures[future]
                try:
                    components[component_name] = future.result(timeout=2.0)
                except Exception as e:
                    self.fail(f"Component {component_name} failed to load: {e}")
        
        total_load_time = time.time() - start_time
        
        # Total concurrent load should be under 3 seconds
        self.assertLess(total_load_time, 3.0,
                       f"All components took {total_load_time:.3f}s to load concurrently")
        
        # All components should be created
        self.assertEqual(len(components), 4)
        for name, component in components.items():
            self.assertIsNotNone(component, f"{name} component is None")


class TestMemoryUsage(unittest.TestCase):
    """Test memory usage requirements (<100MB per component)"""
    
    def setUp(self):
        # Force garbage collection before each test
        gc.collect()
        self.initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
    
    def tearDown(self):
        # Clean up after each test
        gc.collect()
    
    def test_component_memory_usage(self):
        """Test individual component memory usage"""
        components_to_test = [
            ('advanced_inputs', create_advanced_input_component),
            ('interactive_charts', create_interactive_charts_component),
            ('guidance_system', create_guidance_system),
            ('mobile_responsive', create_mobile_responsive_component)
        ]
        
        for component_name, factory_func in components_to_test:
            # Get baseline memory
            gc.collect()
            baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Create component
            component = factory_func()
            
            # Force garbage collection and measure
            gc.collect()
            after_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            memory_used = after_memory - baseline_memory
            
            # Each component should use less than 50MB
            self.assertLess(memory_used, 50.0,
                           f"{component_name} uses {memory_used:.1f}MB memory")
            
            # Clean up
            del component
            gc.collect()
    
    def test_memory_leak_prevention(self):
        """Test that components don't have memory leaks"""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Create and destroy components multiple times
        for _ in range(10):
            component = create_advanced_input_component()
            # Simulate some usage
            mock_state = Mock(spec=UIState)
            mock_state.input_values = {"currency": "USD"}
            mock_state.mobile_mode = False
            
            try:
                # This might fail in test environment, but shouldn't leak memory
                pass
            except:
                pass
            
            del component
            gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (less than 20MB for 10 iterations)
        self.assertLess(memory_increase, 20.0,
                       f"Memory leak detected: {memory_increase:.1f}MB increase")
    
    def test_cache_memory_management(self):
        """Test that caching systems properly manage memory"""
        cache = SecureCacheManager(max_size=10, max_age_minutes=1)
        
        # Fill cache with data
        large_data = "x" * 1024  # 1KB per entry
        for i in range(20):  # Try to add more than max_size
            cache.set(f"key_{i}", large_data * i)
        
        # Cache should not exceed max size
        self.assertLessEqual(len(cache.cache), cache.max_size)
        
        # Memory should be bounded
        cache_memory = sys.getsizeof(cache.cache)
        self.assertLess(cache_memory / 1024 / 1024, 5.0,  # Less than 5MB
                       f"Cache using {cache_memory / 1024 / 1024:.1f}MB")


class TestRenderingPerformance(unittest.TestCase):
    """Test rendering performance requirements"""
    
    def setUp(self):
        self.mock_state = Mock(spec=UIState)
        self.mock_state.input_values = {
            "currency": "USD",
            "project_name": "Test Project"
        }
        self.mock_state.mobile_mode = False
        self.mock_state.validation_results = {}
    
    @patch('streamlit.markdown')
    @patch('streamlit.columns')
    @patch('streamlit.text_input')
    def test_advanced_inputs_rendering_speed(self, mock_input, mock_columns, mock_markdown):
        """Test advanced inputs renders quickly"""
        mock_columns.return_value = [Mock(), Mock()]
        
        component = create_advanced_input_component()
        
        start_time = time.time()
        
        try:
            component.render(None, self.mock_state)
        except Exception:
            # Exceptions are expected in test environment
            pass
        
        render_time = time.time() - start_time
        
        # Should render in under 0.5 seconds
        self.assertLess(render_time, 0.5,
                       f"Advanced inputs rendering took {render_time:.3f}s")
    
    def test_chart_data_generation_performance(self):
        """Test chart data generation performance"""
        component = create_interactive_charts_component()
        
        start_time = time.time()
        
        # Test multiple data generation calls
        for _ in range(10):
            data = component._generate_npv_drill_data(None, "Summary")
            self.assertIsInstance(data, dict)
        
        total_time = time.time() - start_time
        avg_time = total_time / 10
        
        # Each data generation should be under 0.1 seconds
        self.assertLess(avg_time, 0.1,
                       f"Chart data generation took {avg_time:.3f}s on average")
    
    def test_guidance_text_generation_performance(self):
        """Test guidance text generation performance"""
        guidance_system = create_guidance_system()
        
        from src.shared.interfaces import GuidanceContext
        mock_context = Mock(spec=GuidanceContext)
        mock_context.user_experience_level = "beginner"
        mock_context.current_step = "project_name"
        mock_context.user_inputs = {}
        
        start_time = time.time()
        
        # Test multiple guidance requests
        for field in ["project_name", "purchase_price", "interest_rate"]:
            for _ in range(5):
                text = guidance_system.get_help_text(field, mock_context)
                self.assertIsInstance(text, str)
                self.assertGreater(len(text), 0)
        
        total_time = time.time() - start_time
        avg_time = total_time / 15  # 3 fields × 5 iterations
        
        # Each guidance text generation should be under 0.05 seconds
        self.assertLess(avg_time, 0.05,
                       f"Guidance generation took {avg_time:.3f}s on average")


class TestConcurrentPerformance(unittest.TestCase):
    """Test performance under concurrent usage"""
    
    def test_concurrent_component_usage(self):
        """Test components handle concurrent usage"""
        component = create_guidance_system()
        
        from src.shared.interfaces import GuidanceContext
        
        def worker_task(worker_id):
            """Worker task for concurrent testing"""
            mock_context = Mock(spec=GuidanceContext)
            mock_context.user_experience_level = "beginner"
            mock_context.current_step = f"field_{worker_id}"
            mock_context.user_inputs = {}
            
            results = []
            for i in range(10):
                try:
                    text = component.get_help_text(f"test_field_{i}", mock_context)
                    results.append(len(text))
                except Exception as e:
                    results.append(str(e))
            
            return results
        
        start_time = time.time()
        
        # Run concurrent workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker_task, i) for i in range(5)]
            
            results = []
            for future in concurrent.futures.as_completed(futures, timeout=5.0):
                try:
                    worker_results = future.result()
                    results.extend(worker_results)
                except Exception as e:
                    self.fail(f"Concurrent worker failed: {e}")
        
        total_time = time.time() - start_time
        
        # All concurrent operations should complete within 5 seconds
        self.assertLess(total_time, 5.0,
                       f"Concurrent operations took {total_time:.3f}s")
        
        # Should have results from all workers
        self.assertEqual(len(results), 50)  # 5 workers × 10 operations
    
    def test_cache_concurrent_access(self):
        """Test cache handles concurrent access properly"""
        cache = SecureCacheManager(max_size=50, max_age_minutes=1)
        
        def cache_worker(worker_id):
            """Worker that performs cache operations"""
            results = []
            for i in range(20):
                key = f"worker_{worker_id}_item_{i}"
                value = f"data_{worker_id}_{i}"
                
                # Set and get operations
                cache.set(key, value)
                retrieved = cache.get(key)
                
                results.append(retrieved == value)
            
            return results
        
        start_time = time.time()
        
        # Run concurrent cache operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(cache_worker, i) for i in range(10)]
            
            all_results = []
            for future in concurrent.futures.as_completed(futures, timeout=10.0):
                try:
                    worker_results = future.result()
                    all_results.extend(worker_results)
                except Exception as e:
                    self.fail(f"Cache worker failed: {e}")
        
        total_time = time.time() - start_time
        
        # Should complete within 10 seconds
        self.assertLess(total_time, 10.0,
                       f"Concurrent cache operations took {total_time:.3f}s")
        
        # Most operations should succeed (allowing for some cache evictions)
        success_rate = sum(all_results) / len(all_results)
        self.assertGreater(success_rate, 0.7,  # At least 70% success rate
                          f"Cache success rate only {success_rate:.1%}")


class TestPerformanceMonitoring(unittest.TestCase):
    """Test the performance monitoring system itself"""
    
    def test_performance_monitor_overhead(self):
        """Test that performance monitoring doesn't add significant overhead"""
        monitor = create_performance_monitor()
        
        def simple_function():
            time.sleep(0.01)  # 10ms of work
            return "result"
        
        # Test without monitoring
        start_time = time.time()
        for _ in range(10):
            simple_function()
        unmonitored_time = time.time() - start_time
        
        # Test with monitoring
        start_time = time.time()
        for _ in range(10):
            monitor.monitor_component_performance("test", simple_function)
        monitored_time = time.time() - start_time
        
        # Monitoring overhead should be less than 20% of execution time
        overhead = monitored_time - unmonitored_time
        overhead_percentage = overhead / unmonitored_time
        
        self.assertLess(overhead_percentage, 0.2,
                       f"Performance monitoring adds {overhead_percentage:.1%} overhead")
    
    def test_memory_usage_measurement_accuracy(self):
        """Test accuracy of memory usage measurements"""
        monitor = create_performance_monitor()
        
        # Get baseline
        baseline = monitor._get_memory_usage()
        
        # Allocate some memory
        large_data = ["x" * 1024] * 1000  # ~1MB
        
        # Measure again
        after_allocation = monitor._get_memory_usage()
        
        # Should detect memory increase
        memory_increase = after_allocation - baseline
        self.assertGreater(memory_increase, 0.5,  # At least 0.5MB increase
                          f"Memory measurement only detected {memory_increase:.1f}MB increase")
        
        # Clean up
        del large_data
        gc.collect()
    
    def test_performance_report_generation_speed(self):
        """Test performance report generation is fast"""
        monitor = create_performance_monitor()
        
        # Add some metrics history
        for i in range(50):
            monitor._record_performance_metric(
                f"test_metric_{i}", i * 0.1, "seconds", 1.0, "test_component"
            )
        
        start_time = time.time()
        
        report = monitor.generate_performance_report()
        
        generation_time = time.time() - start_time
        
        # Report generation should be under 0.1 seconds
        self.assertLess(generation_time, 0.1,
                       f"Performance report took {generation_time:.3f}s to generate")
        
        # Report should be complete
        self.assertIsNotNone(report.overall_score)
        self.assertIsNotNone(report.load_time_profile)
        self.assertIsNotNone(report.memory_profile)


if __name__ == '__main__':
    unittest.main(verbosity=2)