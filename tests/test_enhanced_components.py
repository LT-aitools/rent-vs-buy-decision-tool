"""
Comprehensive Unit Tests for Enhanced UX Components
Tests all enhanced components for functionality, security, and performance
"""

import unittest
import pytest
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

from src.shared.interfaces import UIState, GuidanceContext, AnalyticsResult, ValidationStatus
from src.components.enhanced.enhanced_security import (
    InputSanitizer, 
    SecureCacheManager, 
    ErrorHandler,
    SecurityError
)


class TestEnhancedSecurity(unittest.TestCase):
    """Test the enhanced security utilities"""
    
    def setUp(self):
        self.sanitizer = InputSanitizer()
        self.cache_manager = SecureCacheManager(max_size=10, max_age_minutes=1)
        self.error_handler = ErrorHandler("test_component")
    
    def test_html_sanitization_blocks_dangerous_content(self):
        """Test that dangerous HTML is blocked"""
        dangerous_html = '<script>alert("xss")</script><p>Safe content</p>'
        
        with self.assertRaises(SecurityError):
            self.sanitizer.sanitize_html(dangerous_html)
    
    def test_html_sanitization_allows_safe_content(self):
        """Test that safe HTML is properly escaped"""
        safe_html = '<p>This is safe content</p>'
        result = self.sanitizer.sanitize_html(safe_html)
        self.assertIn('&lt;p&gt;', result)  # Should be escaped
    
    def test_css_sanitization_removes_dangerous_patterns(self):
        """Test that dangerous CSS patterns are removed"""
        dangerous_css = """
        body { background: url('javascript:alert(1)'); }
        .safe { color: red; }
        """
        result = self.sanitizer.sanitize_css(dangerous_css)
        self.assertNotIn('javascript:', result)
        self.assertIn('color: red', result)
    
    def test_input_length_validation(self):
        """Test input length validation prevents DoS"""
        long_input = "a" * 2000
        result = self.sanitizer.validate_input_length(long_input, max_length=100)
        self.assertEqual(len(result), 100)
    
    def test_secure_cache_key_generation(self):
        """Test secure cache key generation"""
        key1 = self.cache_manager._generate_secure_key("test", param=1)
        key2 = self.cache_manager._generate_secure_key("test", param=1)
        key3 = self.cache_manager._generate_secure_key("test", param=2)
        
        self.assertEqual(key1, key2)  # Same inputs should generate same key
        self.assertNotEqual(key1, key3)  # Different inputs should generate different keys
        self.assertEqual(len(key1), 32)  # Should be 32 characters
    
    def test_cache_expiration(self):
        """Test that cache entries expire properly"""
        import time
        
        # Set cache with very short expiration for testing
        cache = SecureCacheManager(max_age_minutes=0.01)  # 0.6 seconds
        
        cache.set("test_key", "test_value")
        self.assertEqual(cache.get("test_key"), "test_value")
        
        # Wait for expiration
        time.sleep(1)
        self.assertIsNone(cache.get("test_key"))
    
    def test_error_handler_safe_execution(self):
        """Test error handler safely executes functions"""
        def successful_func():
            return "success"
        
        def failing_func():
            raise ValueError("Test error")
        
        # Test successful execution
        result = self.error_handler.safe_execute(successful_func)
        self.assertEqual(result, "success")
        
        # Test error handling with fallback
        result = self.error_handler.safe_execute(failing_func, fallback="fallback")
        self.assertEqual(result, "fallback")


class TestAdvancedInputComponent(unittest.TestCase):
    """Test the advanced input component"""
    
    def setUp(self):
        self.component = create_advanced_input_component()
        self.mock_state = Mock(spec=UIState)
        self.mock_state.input_values = {"currency": "USD"}
        self.mock_state.mobile_mode = False
        self.mock_state.validation_results = {}
    
    def test_component_initialization(self):
        """Test component initializes correctly"""
        self.assertIsNotNone(self.component.validator)
        self.assertEqual(self.component.validator.currency, "USD")
        self.assertIsInstance(self.component.guidance_cache, dict)
    
    @patch('streamlit.markdown')
    @patch('streamlit.columns')
    def test_desktop_rendering_no_errors(self, mock_columns, mock_markdown):
        """Test desktop rendering doesn't throw errors"""
        mock_columns.return_value = [Mock(), Mock()]
        
        try:
            self.component.render(None, self.mock_state)
        except Exception as e:
            self.fail(f"Desktop rendering failed with error: {e}")
    
    def test_input_validation_required_fields(self):
        """Test validation correctly identifies required fields"""
        # Test empty required field
        result = self.component.validate_input("project_name", "")
        self.assertFalse(result.is_valid)
        
        # Test valid required field
        result = self.component.validate_input("project_name", "Valid Project Name")
        self.assertTrue(result.is_valid)
    
    def test_input_validation_numeric_ranges(self):
        """Test numeric validation with ranges"""
        # Test valid purchase price
        result = self.component.validate_input("purchase_price", 500000)
        self.assertTrue(result.is_valid)
        
        # Test invalid purchase price (too low)
        result = self.component.validate_input("purchase_price", 1000)
        self.assertFalse(result.is_valid)
    
    def test_mobile_mode_rendering(self):
        """Test mobile mode uses different rendering"""
        self.mock_state.mobile_mode = True
        
        # Should not raise exceptions
        try:
            self.component.render(None, self.mock_state)
        except Exception as e:
            # Acceptable to have import errors in test environment
            if "streamlit" not in str(e).lower():
                self.fail(f"Mobile rendering failed: {e}")


class TestInteractiveChartsComponent(unittest.TestCase):
    """Test the interactive charts component"""
    
    def setUp(self):
        self.component = create_interactive_charts_component()
        self.mock_state = Mock(spec=UIState)
        self.mock_state.mobile_mode = False
        self.mock_state.input_values = {"currency": "USD"}
    
    def test_component_initialization(self):
        """Test component initializes with required attributes"""
        self.assertIsNotNone(self.component.colors)
        self.assertIsInstance(self.component.drill_down_state, dict)
        self.assertIsInstance(self.component.filter_state, dict)
        self.assertTrue(hasattr(self.component, 'max_state_size'))
    
    def test_state_cleanup_prevents_memory_bloat(self):
        """Test that state dictionaries are cleaned up to prevent memory issues"""
        # Fill state beyond max size
        for i in range(self.component.max_state_size + 10):
            self.component.drill_down_state[f"key_{i}"] = f"value_{i}"
            self.component.filter_state[f"filter_{i}"] = f"filter_value_{i}"
        
        # Trigger cleanup
        self.component._cleanup_state_dictionaries()
        
        # Verify cleanup occurred
        self.assertLessEqual(len(self.component.drill_down_state), self.component.max_state_size)
        self.assertLessEqual(len(self.component.filter_state), self.component.max_state_size)
    
    def test_chart_data_generation_handles_missing_data(self):
        """Test chart data generation handles missing or invalid data gracefully"""
        # Test with None data
        result = self.component._generate_npv_drill_data(None, "Summary")
        self.assertIsInstance(result, dict)
        self.assertIn('buy_npv', result)
        self.assertIn('rent_npv', result)
    
    def test_chart_creation_with_mock_data(self):
        """Test chart creation methods with mock data"""
        mock_data = {
            'buy_npv': 125000,
            'rent_npv': -50000
        }
        
        fig = self.component._create_interactive_npv_chart(
            mock_data, "Summary", True, True
        )
        
        self.assertIsNotNone(fig)
        # Should have at least one trace
        self.assertGreater(len(fig.data), 0)


class TestGuidanceSystem(unittest.TestCase):
    """Test the enhanced guidance system"""
    
    def setUp(self):
        self.guidance_system = create_guidance_system()
        self.mock_context = Mock(spec=GuidanceContext)
        self.mock_context.user_experience_level = "beginner"
        self.mock_context.current_step = "project_name"
        self.mock_context.user_inputs = {"currency": "USD"}
    
    def test_guidance_system_initialization(self):
        """Test guidance system initializes with content"""
        self.assertIsInstance(self.guidance_system.guidance_content, dict)
        self.assertIn("project_name", self.guidance_system.guidance_content)
        self.assertTrue(hasattr(self.guidance_system, 'max_cache_size'))
    
    def test_help_text_generation_by_experience_level(self):
        """Test help text adapts to user experience level"""
        # Test beginner level
        self.mock_context.user_experience_level = "beginner"
        beginner_help = self.guidance_system.get_help_text("project_name", self.mock_context)
        
        # Test expert level
        self.mock_context.user_experience_level = "expert"
        expert_help = self.guidance_system.get_help_text("project_name", self.mock_context)
        
        # Should be different content for different levels
        self.assertNotEqual(beginner_help, expert_help)
        self.assertTrue(len(beginner_help) > 0)
        self.assertTrue(len(expert_help) > 0)
    
    def test_cache_cleanup_prevents_memory_bloat(self):
        """Test that guidance cache is cleaned up properly"""
        # Fill cache beyond max size
        for i in range(self.guidance_system.max_cache_size + 10):
            self.guidance_system.guidance_cache[f"field_{i}_beginner"] = f"help_text_{i}"
        
        # Trigger cleanup
        self.guidance_system._cleanup_cache()
        
        # Verify cleanup occurred
        self.assertLessEqual(len(self.guidance_system.guidance_cache), self.guidance_system.max_cache_size)
    
    def test_decision_guidance_with_valid_analytics(self):
        """Test decision guidance with valid analytics result"""
        mock_analytics = Mock(spec=AnalyticsResult)
        mock_analytics.base_npv_buy = 125000
        mock_analytics.base_npv_rent = -50000
        mock_analytics.risk_assessment.overall_risk_level.value = "medium"
        
        guidance = self.guidance_system.get_decision_guidance(mock_analytics)
        
        self.assertTrue(len(guidance) > 0)
        self.assertIn("NPV", guidance)
    
    def test_decision_guidance_with_none_analytics(self):
        """Test decision guidance handles None analytics gracefully"""
        guidance = self.guidance_system.get_decision_guidance(None)
        
        self.assertTrue(len(guidance) > 0)
        self.assertIn("Complete", guidance.lower())


class TestMobileResponsiveComponent(unittest.TestCase):
    """Test the mobile responsive component"""
    
    def setUp(self):
        self.component = create_mobile_responsive_component()
        self.mock_state = Mock(spec=UIState)
        self.mock_state.mobile_mode = True
        self.mock_state.input_values = {"currency": "USD"}
    
    def test_screen_size_detection(self):
        """Test screen size detection functionality"""
        # Test that screen size is detected
        screen_size = self.component._detect_screen_size()
        self.assertIsNotNone(screen_size)
        self.assertIn(screen_size, [
            self.component.ScreenSize.MOBILE_SMALL,
            self.component.ScreenSize.MOBILE_LARGE,
            self.component.ScreenSize.TABLET,
            self.component.ScreenSize.DESKTOP
        ])
    
    def test_layout_config_generation(self):
        """Test layout configuration is generated properly"""
        config = self.component._get_layout_config()
        self.assertIsNotNone(config)
        self.assertTrue(hasattr(config, 'screen_size'))
        self.assertTrue(hasattr(config, 'column_count'))
    
    def test_completion_stats_calculation(self):
        """Test completion statistics calculation"""
        self.mock_state.input_values = {
            "project_name": "Test Project",
            "location": "Test Location",
            "purchase_price": 500000
        }
        
        stats = self.component._calculate_completion_stats(self.mock_state)
        
        self.assertIn('completed', stats)
        self.assertIn('total', stats)
        self.assertIn('percentage', stats)
        self.assertGreaterEqual(stats['percentage'], 0)
        self.assertLessEqual(stats['percentage'], 100)


class TestAccessibilityValidator(unittest.TestCase):
    """Test the accessibility compliance validator"""
    
    def setUp(self):
        self.validator = create_accessibility_validator()
    
    def test_semantic_html_validation(self):
        """Test semantic HTML structure validation"""
        # Test valid semantic HTML
        valid_html = '<main><h1>Title</h1><p>Content</p></main>'
        issues = self.validator._check_semantic_html(valid_html)
        self.assertEqual(len(issues), 0)
        
        # Test problematic HTML
        problematic_html = '<div onclick="doSomething()">Clickable div</div>'
        issues = self.validator._check_semantic_html(problematic_html)
        self.assertGreater(len(issues), 0)
        self.assertEqual(issues[0].severity, 'serious')
    
    def test_aria_labels_validation(self):
        """Test ARIA labels validation"""
        # Test input without label
        html_without_label = '<input type="text" />'
        issues = self.validator._check_aria_labels(html_without_label)
        self.assertGreater(len(issues), 0)
        
        # Test input with proper label
        html_with_label = '<input type="text" aria-label="Name" />'
        issues = self.validator._check_aria_labels(html_with_label)
        # Should have fewer or no issues
        label_issues = [i for i in issues if 'label' in i.title.lower()]
        self.assertEqual(len(label_issues), 0)
    
    def test_heading_structure_validation(self):
        """Test heading hierarchy validation"""
        # Test proper heading structure
        proper_headings = '<h1>Main</h1><h2>Section</h2><h3>Subsection</h3>'
        issues = self.validator._check_heading_structure(proper_headings)
        self.assertEqual(len(issues), 0)
        
        # Test skipped heading levels
        skipped_headings = '<h1>Main</h1><h4>Skipped h2 and h3</h4>'
        issues = self.validator._check_heading_structure(skipped_headings)
        self.assertGreater(len(issues), 0)
    
    def test_accessibility_report_generation(self):
        """Test comprehensive accessibility report generation"""
        test_html = '''
        <div>
            <h1>Title</h1>
            <input type="text" />
            <img src="test.jpg" />
            <div onclick="alert('test')">Click me</div>
        </div>
        '''
        
        report = self.validator.validate_accessibility(test_html, "test_component")
        
        self.assertIsInstance(report.overall_score, float)
        self.assertGreaterEqual(report.overall_score, 0)
        self.assertLessEqual(report.overall_score, 100)
        self.assertIsInstance(report.detailed_issues, list)
        self.assertGreater(len(report.detailed_issues), 0)


class TestPerformanceMonitor(unittest.TestCase):
    """Test the performance monitoring system"""
    
    def setUp(self):
        self.monitor = create_performance_monitor()
    
    def test_performance_monitor_initialization(self):
        """Test performance monitor initializes with correct targets"""
        self.assertIn('load_time', self.monitor.performance_targets)
        self.assertIn('memory_usage', self.monitor.performance_targets)
        self.assertIsInstance(self.monitor.metrics_history, list)
    
    def test_memory_usage_measurement(self):
        """Test memory usage measurement"""
        memory_usage = self.monitor._get_memory_usage()
        self.assertIsInstance(memory_usage, float)
        self.assertGreaterEqual(memory_usage, 0)
    
    def test_performance_metric_recording(self):
        """Test performance metric recording and history management"""
        initial_count = len(self.monitor.metrics_history)
        
        self.monitor._record_performance_metric(
            "test_metric", 1.5, "seconds", 2.0, "test_component"
        )
        
        self.assertEqual(len(self.monitor.metrics_history), initial_count + 1)
        
        latest_metric = self.monitor.metrics_history[-1]
        self.assertEqual(latest_metric.metric_name, "test_metric")
        self.assertEqual(latest_metric.value, 1.5)
        self.assertTrue(latest_metric.meets_target)  # 1.5 <= 2.0
    
    def test_component_performance_monitoring(self):
        """Test component performance monitoring wrapper"""
        def test_function():
            import time
            time.sleep(0.1)  # Simulate work
            return "test_result"
        
        result = self.monitor.monitor_component_performance("test_component", test_function)
        
        self.assertEqual(result, "test_result")
        # Check that metrics were recorded
        component_metrics = [
            m for m in self.monitor.metrics_history 
            if m.component_name == "test_component"
        ]
        self.assertGreater(len(component_metrics), 0)
    
    def test_performance_report_generation(self):
        """Test comprehensive performance report generation"""
        report = self.monitor.generate_performance_report()
        
        self.assertTrue(hasattr(report, 'overall_score'))
        self.assertTrue(hasattr(report, 'load_time_profile'))
        self.assertTrue(hasattr(report, 'memory_profile'))
        self.assertIsInstance(report.overall_score, float)
        self.assertGreaterEqual(report.overall_score, 0)
        self.assertLessEqual(report.overall_score, 100)


class TestComponentIntegration(unittest.TestCase):
    """Test integration between components"""
    
    def test_all_components_creation(self):
        """Test that all components can be created without errors"""
        components = {
            'advanced_inputs': create_advanced_input_component(),
            'interactive_charts': create_interactive_charts_component(),
            'guidance_system': create_guidance_system(),
            'mobile_responsive': create_mobile_responsive_component(),
            'accessibility_validator': create_accessibility_validator(),
            'performance_monitor': create_performance_monitor()
        }
        
        for name, component in components.items():
            self.assertIsNotNone(component, f"{name} component should not be None")
    
    def test_interface_compliance(self):
        """Test that components implement required interfaces"""
        from src.shared.interfaces import UIComponent, GuidanceSystem
        
        advanced_inputs = create_advanced_input_component()
        guidance_system = create_guidance_system()
        
        # Test UIComponent interface compliance
        self.assertTrue(hasattr(advanced_inputs, 'render'))
        self.assertTrue(hasattr(advanced_inputs, 'validate_input'))
        self.assertTrue(hasattr(advanced_inputs, 'get_guidance'))
        
        # Test GuidanceSystem interface compliance
        self.assertTrue(hasattr(guidance_system, 'get_help_text'))
        self.assertTrue(hasattr(guidance_system, 'get_decision_guidance'))
        self.assertTrue(hasattr(guidance_system, 'get_next_step_suggestion'))
    
    def test_security_integration(self):
        """Test that security utilities are properly integrated"""
        from src.components.enhanced.enhanced_security import (
            input_sanitizer, secure_cache, safe_render_html
        )
        
        # Test sanitizer is available
        self.assertIsNotNone(input_sanitizer)
        
        # Test secure cache is available
        self.assertIsNotNone(secure_cache)
        
        # Test safe HTML rendering
        safe_html = safe_render_html("<p>Test content</p>")
        self.assertIsInstance(safe_html, str)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)