"""
Enhanced Security Utilities
Security fixes for UX enhancement components

This module provides secure utilities for:
- HTML sanitization and validation
- Input validation and sanitization
- Safe caching strategies
- Error handling patterns
"""

import html
import re
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass

class InputSanitizer:
    """Secure input sanitization utilities"""
    
    def __init__(self):
        # Allowed HTML tags for limited HTML rendering
        self.allowed_tags = {
            'b', 'i', 'em', 'strong', 'u', 'br', 'p', 'div', 'span'
        }
        
        # Dangerous patterns to filter
        self.dangerous_patterns = [
            r'<script.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe',
            r'<object',
            r'<embed'
        ]
    
    def sanitize_html(self, html_content: str) -> str:
        """
        Sanitize HTML content to prevent XSS attacks
        
        Args:
            html_content: Raw HTML string
            
        Returns:
            Sanitized HTML string
            
        Raises:
            SecurityError: If dangerous content is detected
        """
        if not isinstance(html_content, str):
            return str(html_content)
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, html_content, re.IGNORECASE | re.DOTALL):
                logger.warning(f"Dangerous pattern detected in HTML: {pattern}")
                raise SecurityError(f"Potentially dangerous HTML content detected")
        
        # Escape HTML entities
        sanitized = html.escape(html_content, quote=True)
        
        return sanitized
    
    def sanitize_css(self, css_content: str) -> str:
        """
        Sanitize CSS content to prevent CSS injection
        
        Args:
            css_content: Raw CSS string
            
        Returns:
            Sanitized CSS string
        """
        if not isinstance(css_content, str):
            return ""
        
        # Remove potentially dangerous CSS properties
        dangerous_css_patterns = [
            r'expression\s*\(',
            r'@import',
            r'javascript:',
            r'vbscript:',
            r'data:',
            r'url\s*\(\s*["\']?\s*javascript:',
        ]
        
        sanitized = css_content
        for pattern in dangerous_css_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def validate_input_length(self, input_value: str, max_length: int = 1000) -> str:
        """
        Validate and truncate input to prevent DoS attacks
        
        Args:
            input_value: Input string to validate
            max_length: Maximum allowed length
            
        Returns:
            Validated and potentially truncated string
        """
        if not isinstance(input_value, str):
            input_value = str(input_value)
        
        if len(input_value) > max_length:
            logger.warning(f"Input truncated from {len(input_value)} to {max_length} characters")
            return input_value[:max_length]
        
        return input_value
    
    def sanitize_user_input(self, user_input: Any) -> str:
        """
        Comprehensive user input sanitization
        
        Args:
            user_input: Any user-provided input
            
        Returns:
            Sanitized string
        """
        try:
            # Convert to string
            input_str = str(user_input) if user_input is not None else ""
            
            # Validate length
            input_str = self.validate_input_length(input_str)
            
            # Remove control characters
            input_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', input_str)
            
            # Escape HTML
            input_str = html.escape(input_str, quote=True)
            
            return input_str
            
        except Exception as e:
            logger.error(f"Error sanitizing input: {e}")
            return ""


class SecureCacheManager:
    """Secure caching with proper cleanup and validation"""
    
    def __init__(self, max_size: int = 100, max_age_minutes: int = 60):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.max_age_minutes = max_age_minutes
    
    def _generate_secure_key(self, *args, **kwargs) -> str:
        """
        Generate secure cache key using cryptographic hash
        
        Args:
            *args: Arguments to hash
            **kwargs: Keyword arguments to hash
            
        Returns:
            Secure hash string
        """
        try:
            # Create deterministic string representation
            key_data = f"{args}_{sorted(kwargs.items())}"
            
            # Use SHA-256 for secure hashing
            return hashlib.sha256(key_data.encode('utf-8')).hexdigest()[:32]
            
        except Exception as e:
            logger.error(f"Error generating cache key: {e}")
            # Fallback to timestamp-based key
            return hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:32]
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve item from cache with age validation
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if valid, None otherwise
        """
        try:
            if key not in self.cache:
                return None
            
            cache_entry = self.cache[key]
            
            # Check age
            age_minutes = (datetime.now() - cache_entry['timestamp']).total_seconds() / 60
            if age_minutes > self.max_age_minutes:
                del self.cache[key]
                return None
            
            return cache_entry['value']
            
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Store item in cache with cleanup
        
        Args:
            key: Cache key
            value: Value to cache
        """
        try:
            # Cleanup old entries if at max size
            if len(self.cache) >= self.max_size:
                self._cleanup_cache()
            
            # Store with timestamp
            self.cache[key] = {
                'value': value,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error storing in cache: {e}")
    
    def _cleanup_cache(self) -> None:
        """Remove oldest entries from cache"""
        try:
            if not self.cache:
                return
            
            # Sort by timestamp and remove oldest half
            sorted_items = sorted(
                self.cache.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            # Keep newest half
            keep_count = self.max_size // 2
            items_to_keep = sorted_items[-keep_count:]
            
            self.cache = dict(items_to_keep)
            
        except Exception as e:
            logger.error(f"Error cleaning cache: {e}")
    
    def clear(self) -> None:
        """Clear entire cache"""
        self.cache.clear()


class ErrorHandler:
    """Centralized error handling for components"""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.logger = logging.getLogger(f"enhanced_ux.{component_name}")
    
    def safe_execute(self, func: callable, *args, fallback=None, **kwargs) -> Any:
        """
        Safely execute function with error handling
        
        Args:
            func: Function to execute
            *args: Function arguments
            fallback: Fallback value on error
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or fallback value
        """
        try:
            return func(*args, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Error in {func.__name__}: {str(e)}")
            
            # Return fallback or safe default
            if fallback is not None:
                return fallback
            
            # Default fallbacks by type
            if hasattr(func, '__annotations__'):
                return_type = func.__annotations__.get('return')
                if return_type == str:
                    return ""
                elif return_type == list:
                    return []
                elif return_type == dict:
                    return {}
                elif return_type == bool:
                    return False
                elif return_type in (int, float):
                    return 0
            
            return None
    
    def log_security_event(self, event_type: str, details: str) -> None:
        """
        Log security-related events
        
        Args:
            event_type: Type of security event
            details: Event details
        """
        self.logger.warning(f"SECURITY EVENT [{event_type}]: {details}")


# Global instances for easy access
input_sanitizer = InputSanitizer()
secure_cache = SecureCacheManager()

def safe_render_html(html_content: str) -> str:
    """
    Safely render HTML content with sanitization
    
    Args:
        html_content: HTML string to render
        
    Returns:
        Sanitized HTML string
    """
    try:
        return input_sanitizer.sanitize_html(html_content)
    except SecurityError:
        logger.error("Blocked potentially dangerous HTML content")
        return "<p>Content blocked for security reasons</p>"
    except Exception as e:
        logger.error(f"Error rendering HTML: {e}")
        return "<p>Error rendering content</p>"

def create_secure_cache_key(*args, **kwargs) -> str:
    """
    Create secure cache key
    
    Args:
        *args: Arguments to hash
        **kwargs: Keyword arguments to hash
        
    Returns:
        Secure cache key
    """
    return secure_cache._generate_secure_key(*args, **kwargs)