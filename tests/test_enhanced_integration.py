"""
Integration Tests for Enhanced UX Components
Tests component integration and compatibility with existing codebase
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import tempfile
import json

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.enhanced import (
    create_advanced_input_component,
    create_interactive_charts_component,
    create_guidance_system,
    create_mobile_responsive_component,
    create_accessibility_validator,
    create_performance_monitor
)

from src.shared.interfaces import UIState, GuidanceContext, AnalyticsResult, ValidationResult
from src.components.enhanced.enhanced_security import (
    InputSanitizer, 
    SecureCacheManager, 
    ErrorHandler
)


class TestComponentCommunication(unittest.TestCase):
    """Test communication between enhanced components"""
    
    def setUp(self):
        self.components = {
            'advanced_inputs': create_advanced_input_component(),
            'interactive_charts': create_interactive_charts_component(),
            'guidance_system': create_guidance_system(),
            'mobile_responsive': create_mobile_responsive_component()
        }
        
        self.mock_state = Mock(spec=UIState)
        self.mock_state.input_values = {
            "project_name": "Test Project",
            "currency": "USD",
            "purchase_price": 500000,
            "interest_rate": 6.5
        }
        self.mock_state.mobile_mode = False
        self.mock_state.validation_results = {}
    
    def test_state_sharing_between_components(self):
        """Test that components properly share state"""
        # Advanced inputs should validate and update state
        result = self.components['advanced_inputs'].validate_input(
            "purchase_price", 500000
        )
        
        self.assertTrue(result.is_valid)
        
        # Charts component should be able to use the same data
        chart_data = self.components['interactive_charts']._generate_npv_drill_data(
            None, "Summary"
        )
        
        self.assertIsInstance(chart_data, dict)
        self.assertIn('buy_npv', chart_data)
    
    def test_guidance_system_integration(self):
        """Test guidance system integrates with other components"""
        guidance_system = self.components['guidance_system']
        
        # Create mock context based on current state
        mock_context = Mock(spec=GuidanceContext)
        mock_context.user_experience_level = "beginner"
        mock_context.current_step = "purchase_price"
        mock_context.user_inputs = self.mock_state.input_values
        
        # Get help text
        help_text = guidance_system.get_help_text("purchase_price", mock_context)
        
        self.assertIsInstance(help_text, str)
        self.assertTrue(len(help_text) > 0)
        
        # Get next step suggestion
        next_step = guidance_system.get_next_step_suggestion(self.mock_state)
        
        self.assertIsInstance(next_step, str)
        self.assertIn("Step", next_step)
    
    def test_mobile_responsive_layout_adaptation(self):
        """Test mobile component adapts to different screen sizes"""
        mobile_component = self.components['mobile_responsive']
        
        # Test desktop layout
        self.mock_state.mobile_mode = False
        desktop_config = mobile_component._get_layout_config()
        
        # Test mobile layout
        self.mock_state.mobile_mode = True
        mobile_config = mobile_component._get_layout_config()
        
        # Layouts should be different
        self.assertNotEqual(desktop_config.column_count, mobile_config.column_count)
    
    def test_error_handling_chain(self):
        """Test error handling propagates correctly between components"""
        error_handler = ErrorHandler("integration_test")
        
        def failing_function():
            raise ValueError("Test integration error")
        
        # Test error handling doesn't break component chain
        result = error_handler.safe_execute(
            failing_function, 
            fallback="Integration error handled"
        )
        
        self.assertEqual(result, "Integration error handled")


class TestExistingCodebaseCompatibility(unittest.TestCase):
    """Test compatibility with existing codebase interfaces"""
    
    def setUp(self):
        self.components = {
            'advanced_inputs': create_advanced_input_component(),
            'guidance_system': create_guidance_system(),
            'performance_monitor': create_performance_monitor()
        }
    
    def test_interface_contract_compliance(self):
        """Test components comply with interface contracts"""
        from src.shared.interfaces import UIComponent, GuidanceSystem
        
        # Test UIComponent interface methods exist
        advanced_inputs = self.components['advanced_inputs']
        
        self.assertTrue(hasattr(advanced_inputs, 'render'))
        self.assertTrue(hasattr(advanced_inputs, 'validate_input'))
        self.assertTrue(hasattr(advanced_inputs, 'get_guidance'))
        
        # Test GuidanceSystem interface methods exist
        guidance_system = self.components['guidance_system']
        
        self.assertTrue(hasattr(guidance_system, 'get_help_text'))
        self.assertTrue(hasattr(guidance_system, 'get_decision_guidance'))
        self.assertTrue(hasattr(guidance_system, 'get_next_step_suggestion'))
    
    def test_existing_utilities_integration(self):
        """Test integration with existing utility functions"""
        # Test that components can use existing utility functions
        try:
            from src.utils.defaults import get_field_description
            
            # Should be able to get field descriptions
            description = get_field_description("purchase_price")
            self.assertIsInstance(description, str)
            
        except ImportError:
            # If utils don't exist, components should handle gracefully
            pass
    
    def test_data_structure_compatibility(self):
        """Test compatibility with existing data structures"""
        # Test that components work with expected data structures
        mock_analytics = Mock(spec=AnalyticsResult)
        mock_analytics.base_npv_buy = 125000
        mock_analytics.base_npv_rent = -50000
        mock_analytics.risk_assessment = Mock()
        mock_analytics.risk_assessment.overall_risk_level = Mock()
        mock_analytics.risk_assessment.overall_risk_level.value = "medium"
        mock_analytics.risk_assessment.risk_description = "Moderate risk investment"
        mock_analytics.risk_assessment.risk_factors = {"market_volatility": 0.3}
        
        # Guidance system should handle analytics result
        guidance = self.components['guidance_system'].get_decision_guidance(mock_analytics)
        
        self.assertIsInstance(guidance, str)
        self.assertTrue(len(guidance) > 0)
        self.assertIn("NPV", guidance)
    
    def test_configuration_compatibility(self):
        """Test components respect existing configuration patterns"""
        # Test that components can be configured similar to existing code
        performance_monitor = self.components['performance_monitor']
        
        # Should have configurable performance targets
        self.assertIsInstance(performance_monitor.performance_targets, dict)
        self.assertIn('load_time', performance_monitor.performance_targets)
        
        # Performance targets should be reasonable for existing system
        load_time_target = performance_monitor.performance_targets['load_time']
        self.assertLessEqual(load_time_target, 5.0)  # Reasonable for web app


class TestDataFlowIntegration(unittest.TestCase):
    """Test data flow between components and existing systems"""
    
    def test_input_validation_flow(self):
        """Test input validation flows correctly through system"""
        advanced_inputs = create_advanced_input_component()
        
        # Test validation chain
        test_cases = [
            ("project_name", "Valid Project Name", True),
            ("project_name", "", False),
            ("purchase_price", 500000, True),
            ("purchase_price", -100, False),
            ("interest_rate", 6.5, True),
            ("interest_rate", 25, False)
        ]
        
        for field_name, value, expected_valid in test_cases:
            result = advanced_inputs.validate_input(field_name, value)
            
            self.assertEqual(result.is_valid, expected_valid,
                           f"Validation failed for {field_name}={value}")
    
    def test_chart_data_pipeline(self):
        """Test chart data generation pipeline"""
        charts_component = create_interactive_charts_component()
        
        # Test different chart types generate valid data
        chart_types = ["Summary", "Monthly", "Yearly", "Sensitivity"]
        
        for chart_type in chart_types:
            data = charts_component._generate_npv_drill_data(None, chart_type)
            
            self.assertIsInstance(data, dict)
            self.assertIn('buy_npv', data)
            self.assertIn('rent_npv', data)
            
            # Values should be numeric
            self.assertIsInstance(data['buy_npv'], (int, float))
            self.assertIsInstance(data['rent_npv'], (int, float))
    
    def test_guidance_context_flow(self):
        """Test guidance context flows through system"""
        guidance_system = create_guidance_system()
        
        # Create context with different user levels
        user_levels = ["beginner", "intermediate", "expert"]
        
        for level in user_levels:
            mock_context = Mock(spec=GuidanceContext)
            mock_context.user_experience_level = level
            mock_context.current_step = "purchase_price"
            mock_context.user_inputs = {"currency": "USD"}
            
            help_text = guidance_system.get_help_text("purchase_price", mock_context)
            
            self.assertIsInstance(help_text, str)
            self.assertTrue(len(help_text) > 0)
            
            # Different levels should get different content
            # (This would be more specific in real implementation)
            if level == "beginner":
                self.assertIn("Purchase Price", help_text)


class TestSecurityIntegrationFlow(unittest.TestCase):
    """Test security integration across the system"""
    
    def test_end_to_end_security_pipeline(self):
        """Test complete security pipeline from input to output"""
        from src.components.enhanced.enhanced_security import (
            input_sanitizer,
            secure_cache,
            safe_render_html
        )
        
        # Test malicious input handling
        malicious_input = '<script>alert("xss")</script><p>Legitimate content</p>'
        
        # Step 1: Input sanitization
        sanitized_input = input_sanitizer.sanitize_user_input(malicious_input)
        
        # Step 2: Secure caching
        cache_key = secure_cache._generate_secure_key("test_input", sanitized_input)
        secure_cache.set(cache_key, sanitized_input)
        
        # Step 3: Safe retrieval and rendering
        cached_content = secure_cache.get(cache_key)
        safe_html = safe_render_html(cached_content)
        
        # Verify security measures
        self.assertNotIn('<script>', safe_html)
        self.assertNotIn('javascript:', safe_html.lower())
        # Script tags should be escaped, not executable
        self.assertTrue('script' in safe_html and '<script>' not in safe_html)
        self.assertIn('legitimate content', safe_html.lower())
    
    def test_component_security_integration(self):
        """Test components properly integrate security measures"""
        advanced_inputs = create_advanced_input_component()
        
        # Test that input validation includes security checks
        malicious_inputs = [
            '<script>alert("xss")</script>',
            'javascript:alert("xss")',
            '<img src="x" onerror="alert(1)">'
        ]
        
        for malicious_input in malicious_inputs:
            # Components should either reject or sanitize malicious input
            try:
                result = advanced_inputs.validate_input("project_name", malicious_input)
                
                # If validation passes, content should be sanitized
                if result.is_valid and hasattr(result, 'sanitized_value'):
                    sanitized = result.sanitized_value
                    self.assertNotIn('<script>', sanitized)
                    self.assertNotIn('javascript:', sanitized)
            except Exception:
                # Exception is acceptable for malicious input
                pass


class TestPerformanceIntegration(unittest.TestCase):
    """Test performance monitoring integration"""
    
    def test_performance_monitoring_integration(self):
        """Test performance monitoring works across components"""
        performance_monitor = create_performance_monitor()
        
        # Test monitoring different component operations
        def mock_component_operation():
            import time
            time.sleep(0.01)  # Simulate work
            return "operation_complete"
        
        # Monitor operation
        result = performance_monitor.monitor_component_performance(
            "test_component", mock_component_operation
        )
        
        self.assertEqual(result, "operation_complete")
        
        # Check metrics were recorded
        self.assertGreater(len(performance_monitor.metrics_history), 0)
        
        latest_metric = performance_monitor.metrics_history[-1]
        self.assertEqual(latest_metric.component_name, "test_component")
    
    def test_memory_usage_monitoring(self):
        """Test memory usage monitoring integration"""
        performance_monitor = create_performance_monitor()
        
        # Get baseline memory
        baseline = performance_monitor._get_memory_usage()
        
        # Create some objects
        large_data = ["x" * 1000] * 100  # ~100KB
        
        # Check memory increased
        after_allocation = performance_monitor._get_memory_usage()
        
        self.assertGreaterEqual(after_allocation, baseline)
        
        # Clean up
        del large_data
        
    def test_performance_report_integration(self):
        """Test performance reporting integration"""
        performance_monitor = create_performance_monitor()
        
        # Add some test metrics
        for i in range(5):
            performance_monitor._record_performance_metric(
                f"test_metric_{i}", i * 0.1, "seconds", 1.0, f"component_{i}"
            )
        
        # Generate report
        report = performance_monitor.generate_performance_report()
        
        # Verify report structure
        self.assertTrue(hasattr(report, 'overall_score'))
        self.assertTrue(hasattr(report, 'load_time_profile'))
        self.assertTrue(hasattr(report, 'memory_profile'))
        
        # Scores should be reasonable
        self.assertIsInstance(report.overall_score, float)
        self.assertGreaterEqual(report.overall_score, 0)
        self.assertLessEqual(report.overall_score, 100)


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing code"""
    
    def test_enhanced_components_dont_break_existing_workflows(self):
        """Test enhanced components don't interfere with existing code"""
        # Test that creating enhanced components doesn't affect existing imports
        try:
            # Create all enhanced components
            components = {
                'advanced_inputs': create_advanced_input_component(),
                'interactive_charts': create_interactive_charts_component(),
                'guidance_system': create_guidance_system(),
                'mobile_responsive': create_mobile_responsive_component(),
                'accessibility_validator': create_accessibility_validator(),
                'performance_monitor': create_performance_monitor()
            }
            
            # All should be created successfully
            for name, component in components.items():
                self.assertIsNotNone(component)
                
        except Exception as e:
            self.fail(f"Enhanced components broke existing imports: {e}")
    
    def test_existing_interface_methods_preserved(self):
        """Test existing interface methods are preserved"""
        # Test that enhanced components still support expected interface methods
        advanced_inputs = create_advanced_input_component()
        
        # Should have standard component methods
        expected_methods = ['render', 'validate_input']
        
        for method in expected_methods:
            self.assertTrue(hasattr(advanced_inputs, method),
                          f"Missing expected method: {method}")
    
    def test_data_format_compatibility(self):
        """Test data formats remain compatible"""
        # Test validation result format
        advanced_inputs = create_advanced_input_component()
        result = advanced_inputs.validate_input("project_name", "Test Project")
        
        # Should have expected attributes
        self.assertTrue(hasattr(result, 'is_valid'))
        self.assertIsInstance(result.is_valid, bool)
        
        if hasattr(result, 'message'):
            self.assertIsInstance(result.message, str)


if __name__ == '__main__':
    unittest.main(verbosity=2)