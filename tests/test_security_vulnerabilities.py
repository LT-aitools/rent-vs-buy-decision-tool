"""
Security Vulnerability Tests
Specialized tests for security issues and attack vectors
"""

import unittest
import pytest
import sys
import os
from unittest.mock import Mock, patch
import tempfile
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.components.enhanced.enhanced_security import (
    InputSanitizer, 
    SecureCacheManager, 
    ErrorHandler,
    SecurityError
)


class TestXSSPrevention(unittest.TestCase):
    """Test Cross-Site Scripting (XSS) prevention"""
    
    def setUp(self):
        self.sanitizer = InputSanitizer()
    
    def test_script_tag_injection_blocked(self):
        """Test that script tags are blocked"""
        malicious_inputs = [
            '<script>alert("xss")</script>',
            '<SCRIPT>alert("xss")</SCRIPT>',
            '<script src="http://evil.com/malicious.js"></script>',
            '<script>document.cookie="evil"</script>',
        ]
        
        for malicious_input in malicious_inputs:
            with self.assertRaises(SecurityError, 
                                 msg=f"Failed to block: {malicious_input}"):
                self.sanitizer.sanitize_html(malicious_input)
    
    def test_javascript_url_injection_blocked(self):
        """Test that javascript: URLs are blocked"""
        malicious_inputs = [
            'javascript:alert("xss")',
            'JAVASCRIPT:alert("xss")',
            'JaVaScRiPt:alert("xss")',
        ]
        
        for malicious_input in malicious_inputs:
            with self.assertRaises(SecurityError,
                                 msg=f"Failed to block: {malicious_input}"):
                self.sanitizer.sanitize_html(malicious_input)
    
    def test_event_handler_injection_blocked(self):
        """Test that HTML event handlers are blocked"""
        malicious_inputs = [
            '<img src="x" onerror="alert(1)">',
            '<div onclick="alert(1)">Click me</div>',
            '<body onload="alert(1)">',
            '<input onfocus="alert(1)">',
        ]
        
        for malicious_input in malicious_inputs:
            with self.assertRaises(SecurityError,
                                 msg=f"Failed to block: {malicious_input}"):
                self.sanitizer.sanitize_html(malicious_input)
    
    def test_iframe_injection_blocked(self):
        """Test that iframe injections are blocked"""
        malicious_inputs = [
            '<iframe src="http://evil.com"></iframe>',
            '<IFRAME src="javascript:alert(1)"></IFRAME>',
            '<iframe srcdoc="<script>alert(1)</script>"></iframe>',
        ]
        
        for malicious_input in malicious_inputs:
            with self.assertRaises(SecurityError,
                                 msg=f"Failed to block: {malicious_input}"):
                self.sanitizer.sanitize_html(malicious_input)
    
    def test_safe_content_allowed(self):
        """Test that safe content is properly escaped but allowed"""
        safe_inputs = [
            '<p>This is safe paragraph text</p>',
            '<div class="container">Safe div content</div>',
            '<h1>Safe heading</h1>',
            'Plain text with no HTML',
        ]
        
        for safe_input in safe_inputs:
            try:
                result = self.sanitizer.sanitize_html(safe_input)
                self.assertIsInstance(result, str)
                self.assertGreater(len(result), 0)
            except SecurityError:
                self.fail(f"Safe content was incorrectly blocked: {safe_input}")


class TestCSSInjectionPrevention(unittest.TestCase):
    """Test CSS injection prevention"""
    
    def setUp(self):
        self.sanitizer = InputSanitizer()
    
    def test_css_expression_blocked(self):
        """Test that CSS expressions are blocked"""
        malicious_css = [
            'background: expression(alert("xss"));',
            'width: expression(alert("xss"));',
            'color: expression(alert("xss"));',
        ]
        
        for css in malicious_css:
            result = self.sanitizer.sanitize_css(css)
            self.assertNotIn('expression', result.lower())
    
    def test_css_import_blocked(self):
        """Test that @import statements are blocked"""
        malicious_css = [
            '@import url("http://evil.com/malicious.css");',
            '@IMPORT url("javascript:alert(1)");',
        ]
        
        for css in malicious_css:
            result = self.sanitizer.sanitize_css(css)
            self.assertNotIn('@import', result.lower())
    
    def test_css_javascript_url_blocked(self):
        """Test that javascript: URLs in CSS are blocked"""
        malicious_css = [
            'background: url("javascript:alert(1)");',
            'background-image: url(javascript:alert(1));',
        ]
        
        for css in malicious_css:
            result = self.sanitizer.sanitize_css(css)
            self.assertNotIn('javascript:', result.lower())
    
    def test_safe_css_preserved(self):
        """Test that safe CSS is preserved"""
        safe_css = """
        .container {
            background-color: #f0f0f0;
            margin: 10px;
            padding: 20px;
            border-radius: 5px;
        }
        """
        
        result = self.sanitizer.sanitize_css(safe_css)
        self.assertIn('background-color', result)
        self.assertIn('#f0f0f0', result)
        self.assertIn('margin', result)


class TestInputValidationAttacks(unittest.TestCase):
    """Test various input validation attack vectors"""
    
    def setUp(self):
        self.sanitizer = InputSanitizer()
    
    def test_dos_prevention_long_input(self):
        """Test prevention of DoS attacks via extremely long input"""
        # Generate very long string
        long_input = "A" * 100000  # 100KB string
        
        result = self.sanitizer.validate_input_length(long_input, max_length=1000)
        self.assertEqual(len(result), 1000)
        self.assertEqual(result, "A" * 1000)
    
    def test_control_character_removal(self):
        """Test removal of control characters"""
        malicious_input = "Normal text\x00\x01\x02\x03\x7F"
        
        result = self.sanitizer.sanitize_user_input(malicious_input)
        
        # Should not contain any control characters
        for char in result:
            self.assertFalse(ord(char) < 32 and char not in '\t\n\r',
                           f"Control character found: {ord(char)}")
    
    def test_null_byte_injection_prevention(self):
        """Test prevention of null byte injection attacks"""
        malicious_inputs = [
            "normal\x00<script>alert(1)</script>",
            "file.txt\x00.php",
            "user\x00admin",
        ]
        
        for malicious_input in malicious_inputs:
            result = self.sanitizer.sanitize_user_input(malicious_input)
            self.assertNotIn('\x00', result)
    
    def test_unicode_normalization_attacks(self):
        """Test prevention of Unicode normalization attacks"""
        # Unicode characters that might bypass filters
        unicode_attacks = [
            "\u003cscript\u003e",  # <script> in Unicode
            "\uFF1Cscript\uFF1E",  # Fullwidth < and >
            "\u02BCscript\u02BC",   # Modifier letters
        ]
        
        for attack in unicode_attacks:
            result = self.sanitizer.sanitize_user_input(attack)
            # Should be escaped or sanitized
            self.assertNotIn('<script>', result.lower())


class TestCacheSecurityAttacks(unittest.TestCase):
    """Test cache security and attack prevention"""
    
    def setUp(self):
        self.cache = SecureCacheManager(max_size=10, max_age_minutes=5)
    
    def test_cache_key_collision_resistance(self):
        """Test that cache keys resist collision attacks"""
        # Try to create keys that might collide
        similar_inputs = [
            ("user", "123"),
            ("use", "r123"),
            ("us", "er123"),
        ]
        
        keys = []
        for args in similar_inputs:
            key = self.cache._generate_secure_key(*args)
            keys.append(key)
        
        # All keys should be different
        self.assertEqual(len(keys), len(set(keys)), "Cache key collision detected")
    
    def test_cache_size_limit_enforcement(self):
        """Test that cache size limits are enforced to prevent memory attacks"""
        # Fill cache to capacity
        for i in range(self.cache.max_size):
            self.cache.set(f"key_{i}", f"value_{i}")
        
        self.assertEqual(len(self.cache.cache), self.cache.max_size)
        
        # Add one more item
        self.cache.set("overflow_key", "overflow_value")
        
        # Cache should not exceed max size
        self.assertLessEqual(len(self.cache.cache), self.cache.max_size)
    
    def test_cache_poisoning_prevention(self):
        """Test prevention of cache poisoning attacks"""
        # Try to inject malicious content
        malicious_content = "<script>alert('cache poisoned')</script>"
        
        self.cache.set("test_key", malicious_content)
        retrieved = self.cache.get("test_key")
        
        # Content should be retrieved as-is (validation should happen elsewhere)
        # But cache itself shouldn't be corrupted
        self.assertEqual(retrieved, malicious_content)
        self.assertTrue(len(self.cache.cache) > 0)
    
    def test_cache_timing_attacks_mitigation(self):
        """Test mitigation of timing attacks on cache"""
        import time
        
        # Store an item
        self.cache.set("existing_key", "value")
        
        # Time cache hits vs misses
        start_time = time.time()
        result1 = self.cache.get("existing_key")
        hit_time = time.time() - start_time
        
        start_time = time.time()
        result2 = self.cache.get("nonexistent_key")
        miss_time = time.time() - start_time
        
        # Timing difference should be minimal (within reasonable bounds)
        # This is a basic test - more sophisticated timing analysis would be needed for production
        self.assertIsNotNone(result1)
        self.assertIsNone(result2)
        
        # Both operations should be fast
        self.assertLess(hit_time, 0.01)  # Less than 10ms
        self.assertLess(miss_time, 0.01)  # Less than 10ms


class TestErrorHandlingSecurityImplications(unittest.TestCase):
    """Test security implications of error handling"""
    
    def setUp(self):
        self.error_handler = ErrorHandler("security_test")
    
    def test_error_information_disclosure_prevention(self):
        """Test that detailed error information is not disclosed to users"""
        def failing_function():
            # Simulate a function that might leak sensitive information in errors
            sensitive_data = "password=secret123, api_key=abc123"
            raise ValueError(f"Database connection failed: {sensitive_data}")
        
        # Error handler should not propagate sensitive information
        with patch('logging.Logger.error') as mock_logger:
            result = self.error_handler.safe_execute(
                failing_function, 
                fallback="Generic error occurred"
            )
            
            # Should return fallback, not expose error details
            self.assertEqual(result, "Generic error occurred")
            
            # Should log error but not expose it to user
            mock_logger.assert_called_once()
    
    def test_exception_chaining_security(self):
        """Test that exception chaining doesn't leak information"""
        def nested_failing_function():
            try:
                # Inner function that might contain sensitive info
                secret_key = "super_secret_api_key_123"
                raise ValueError(f"Authentication failed with key: {secret_key}")
            except ValueError as e:
                # Re-raise with different message
                raise RuntimeError("Database operation failed") from e
        
        result = self.error_handler.safe_execute(
            nested_failing_function,
            fallback="Operation failed"
        )
        
        # Should not expose the sensitive information from the original exception
        self.assertEqual(result, "Operation failed")
    
    def test_resource_exhaustion_in_error_handling(self):
        """Test that error handling itself doesn't cause resource exhaustion"""
        def memory_exhausting_error():
            # Function that tries to exhaust memory in error handling
            large_data = "A" * (10**6)  # 1MB string
            raise MemoryError(f"Out of memory processing: {large_data}")
        
        # Error handler should handle this gracefully without exhausting resources
        for _ in range(10):
            result = self.error_handler.safe_execute(
                memory_exhausting_error,
                fallback="Memory error"
            )
            self.assertEqual(result, "Memory error")


class TestSecurityIntegration(unittest.TestCase):
    """Test integration of security measures across components"""
    
    def test_end_to_end_security_pipeline(self):
        """Test complete security pipeline from input to output"""
        from src.components.enhanced.enhanced_security import (
            input_sanitizer, 
            secure_cache,
            safe_render_html
        )
        
        # Simulate user input with potential XSS
        malicious_input = '<script>alert("xss")</script><p>Legitimate content</p>'
        
        # Step 1: Sanitize user input
        sanitized_input = input_sanitizer.sanitize_user_input(malicious_input)
        
        # Step 2: Store in secure cache
        cache_key = secure_cache._generate_secure_key("user_input", sanitized_input)
        secure_cache.set(cache_key, sanitized_input)
        
        # Step 3: Retrieve and render safely
        cached_content = secure_cache.get(cache_key)
        safe_html = safe_render_html(cached_content)
        
        # Verify security measures worked
        self.assertNotIn('<script>', safe_html)
        self.assertNotIn('javascript:', safe_html.lower())
        # Script tags should be escaped, not executable (double escaping is safe)
        self.assertTrue('script' in safe_html and '<script>' not in safe_html)
        # But legitimate content should be preserved (escaped)
        self.assertIn('legitimate content', safe_html.lower())
    
    def test_security_logging_and_monitoring(self):
        """Test that security events are properly logged"""
        error_handler = ErrorHandler("security_test")
        
        with patch('logging.Logger.warning') as mock_logger:
            error_handler.log_security_event("XSS_ATTEMPT", "Blocked malicious script")
            
            # Should log the security event
            mock_logger.assert_called_once()
            args = mock_logger.call_args[0][0]
            self.assertIn("SECURITY EVENT", args)
            self.assertIn("XSS_ATTEMPT", args)


if __name__ == '__main__':
    unittest.main(verbosity=2)