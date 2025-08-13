"""
Enhanced User Experience Components
Week 4 UX Enhancement Package

This package contains the enhanced UX components developed for Week 4 of the
Real Estate Decision Tool project, focusing on advanced user experience,
accessibility, and performance optimization.

Components:
- AdvancedInputComponent: Smart input validation and user guidance
- InteractiveChartsComponent: Interactive visualizations with drill-down
- GuidanceSystem: Contextual help and decision guidance
- MobileResponsiveComponent: Mobile-first responsive design
- AccessibilityValidator: WCAG 2.1 AA compliance verification
- PerformanceMonitor: Performance optimization and monitoring

Usage:
    from src.components.enhanced import (
        create_advanced_input_component,
        create_interactive_charts_component,
        create_guidance_system,
        create_mobile_responsive_component,
        create_accessibility_validator,
        create_performance_monitor
    )
"""

# Import all factory functions
from .advanced_inputs import create_advanced_input_component
from .interactive_charts import create_interactive_charts_component
from .guidance_system import create_guidance_system
from .mobile_responsive import create_mobile_responsive_component
from .accessibility_compliance import create_accessibility_validator, show_accessibility_dashboard
from .performance_optimizer import create_performance_monitor, show_performance_dashboard

# Import component classes for direct instantiation if needed
from .advanced_inputs import AdvancedInputComponent
from .interactive_charts import InteractiveChartsComponent
from .guidance_system import EnhancedGuidanceSystem
from .mobile_responsive import MobileResponsiveComponent
from .accessibility_compliance import AccessibilityValidator
from .performance_optimizer import PerformanceMonitor

# Import data classes and interfaces
from .advanced_inputs import SmartInputConfig
from .interactive_charts import ChartConfig, DrillDownLevel
from .guidance_system import GuidanceLevel, GuidanceType, GuidanceContent
from .mobile_responsive import ScreenSize, MobileLayoutConfig
from .accessibility_compliance import AccessibilityIssue, AccessibilityReport
from .performance_optimizer import PerformanceMetric, LoadTimeProfile, MemoryProfile

__version__ = "1.0.0"
__author__ = "Week 4 UX Enhancement Team"

# Component registry for easy access
ENHANCED_COMPONENTS = {
    'advanced_inputs': create_advanced_input_component,
    'interactive_charts': create_interactive_charts_component,
    'guidance_system': create_guidance_system,
    'mobile_responsive': create_mobile_responsive_component,
    'accessibility_validator': create_accessibility_validator,
    'performance_monitor': create_performance_monitor
}

def create_all_components():
    """
    Create all enhanced UX components
    
    Returns:
        Dict[str, Any]: Dictionary of initialized components
    """
    return {
        name: factory() for name, factory in ENHANCED_COMPONENTS.items()
    }

def get_component_info():
    """
    Get information about all available enhanced components
    
    Returns:
        Dict[str, str]: Component names and descriptions
    """
    return {
        'advanced_inputs': 'Smart input validation with contextual feedback and adaptive ranges',
        'interactive_charts': 'Interactive visualizations with drill-down and real-time filtering',
        'guidance_system': 'Contextual help system with progressive tutorials and decision guidance',
        'mobile_responsive': 'Mobile-first responsive design with touch-optimized interfaces',
        'accessibility_validator': 'WCAG 2.1 AA compliance verification and accessibility testing',
        'performance_monitor': 'Real-time performance monitoring with optimization recommendations'
    }

# Package metadata
__all__ = [
    # Factory functions
    'create_advanced_input_component',
    'create_interactive_charts_component', 
    'create_guidance_system',
    'create_mobile_responsive_component',
    'create_accessibility_validator',
    'create_performance_monitor',
    
    # Component classes
    'AdvancedInputComponent',
    'InteractiveChartsComponent',
    'EnhancedGuidanceSystem', 
    'MobileResponsiveComponent',
    'AccessibilityValidator',
    'PerformanceMonitor',
    
    # Data classes
    'SmartInputConfig',
    'ChartConfig',
    'DrillDownLevel',
    'GuidanceLevel',
    'GuidanceType', 
    'GuidanceContent',
    'ScreenSize',
    'MobileLayoutConfig',
    'AccessibilityIssue',
    'AccessibilityReport',
    'PerformanceMetric',
    'LoadTimeProfile',
    'MemoryProfile',
    
    # Utility functions
    'create_all_components',
    'get_component_info',
    'show_accessibility_dashboard',
    'show_performance_dashboard',
    
    # Constants
    'ENHANCED_COMPONENTS'
]