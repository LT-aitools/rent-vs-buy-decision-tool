"""
Performance Optimization and Testing
Week 4 UX Enhancement - Performance monitoring and optimization

Features:
- Real-time performance monitoring
- Load time optimization
- Memory usage tracking
- Component rendering performance
- Caching strategies
- Progressive loading
- Performance budgets and alerts
"""

import streamlit as st
import time
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

import gc
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import functools
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.interfaces import UIComponent, UIState


@dataclass
class PerformanceMetric:
    """Performance measurement result"""
    metric_name: str
    value: float
    unit: str
    target_value: float
    meets_target: bool
    timestamp: datetime
    component_name: Optional[str] = None


@dataclass
class LoadTimeProfile:
    """Load time profiling results"""
    total_time: float
    component_times: Dict[str, float]
    resource_loading: float
    rendering_time: float
    interactive_time: float
    largest_contentful_paint: float


@dataclass
class MemoryProfile:
    """Memory usage profiling"""
    current_usage: float
    peak_usage: float
    available_memory: float
    memory_efficient: bool
    recommendations: List[str]


@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    overall_score: float
    load_time_profile: LoadTimeProfile
    memory_profile: MemoryProfile
    metrics: List[PerformanceMetric]
    recommendations: List[str]
    meets_targets: bool


class PerformanceMonitor:
    """Real-time performance monitoring and optimization"""
    
    def __init__(self):
        self.performance_targets = {
            'load_time': 3.0,  # seconds
            'rendering_time': 0.5,  # seconds
            'memory_usage': 100.0,  # MB
            'interactive_time': 1.0,  # seconds
        }
        
        self.metrics_history = []
        self.component_cache = {}
        self.lazy_loading_enabled = True
        
    def monitor_component_performance(self, component_name: str, render_func: Callable) -> Any:
        """Monitor performance of component rendering"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Execute the component rendering
        try:
            result = render_func()
            
            # Measure performance
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            render_time = end_time - start_time
            memory_delta = end_memory - start_memory
            
            # Record metrics
            self._record_performance_metric(
                f"{component_name}_render_time",
                render_time,
                "seconds",
                self.performance_targets['rendering_time'],
                component_name
            )
            
            self._record_performance_metric(
                f"{component_name}_memory_delta",
                memory_delta,
                "MB",
                10.0,  # Target: less than 10MB per component
                component_name
            )
            
            return result
            
        except Exception as e:
            st.error(f"Performance monitoring error for {component_name}: {str(e)}")
            return None
    
    def measure_page_load_performance(self) -> LoadTimeProfile:
        """Measure overall page load performance"""
        if 'page_load_start' not in st.session_state:
            st.session_state['page_load_start'] = time.time()
        
        current_time = time.time()
        total_time = current_time - st.session_state['page_load_start']
        
        # Mock component timing (in practice, would be measured individually)
        component_times = {
            'navigation': 0.1,
            'sidebar': 0.2,
            'main_content': 0.8,
            'charts': 1.2,
            'forms': 0.5
        }
        
        # Calculate derived metrics
        resource_loading = sum(component_times.values()) * 0.3  # 30% resource loading
        rendering_time = sum(component_times.values()) * 0.7   # 70% rendering
        interactive_time = total_time * 0.9  # 90% of total time to interactive
        largest_contentful_paint = total_time * 0.8  # 80% of total time to LCP
        
        return LoadTimeProfile(
            total_time=total_time,
            component_times=component_times,
            resource_loading=resource_loading,
            rendering_time=rendering_time,
            interactive_time=interactive_time,
            largest_contentful_paint=largest_contentful_paint
        )
    
    def analyze_memory_usage(self) -> MemoryProfile:
        """Analyze current memory usage and efficiency"""
        if not PSUTIL_AVAILABLE:
            # Return placeholder values when psutil is not available
            return MemoryProfile(
                current_usage=50.0,
                peak_usage=100.0,
                available_memory=1000.0,
                memory_efficient=True,
                recommendations=["Install psutil for accurate memory monitoring"]
            )
            
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            current_usage = memory_info.rss / 1024 / 1024  # Convert to MB
            
            # Get system memory info
            system_memory = psutil.virtual_memory()
            available_memory = system_memory.available / 1024 / 1024
        except Exception:
            # Fallback if psutil fails
            return MemoryProfile(
                current_usage=50.0,
                peak_usage=100.0,
                available_memory=1000.0,
                memory_efficient=True,
                recommendations=["Memory monitoring unavailable"]
            )
        
        # Estimate peak usage (simplified)
        peak_usage = current_usage * 1.2  # Assume peak is 20% higher
        
        # Determine if memory usage is efficient
        memory_efficient = current_usage < self.performance_targets['memory_usage']
        
        # Generate recommendations
        recommendations = []
        if not memory_efficient:
            recommendations.extend([
                "Consider implementing lazy loading for large components",
                "Review data caching strategies",
                "Optimize image and chart rendering"
            ])
        
        if current_usage > 200:  # MB
            recommendations.append("High memory usage detected - consider component optimization")
        
        return MemoryProfile(
            current_usage=current_usage,
            peak_usage=peak_usage,
            available_memory=available_memory,
            memory_efficient=memory_efficient,
            recommendations=recommendations
        )
    
    def generate_performance_report(self) -> PerformanceReport:
        """Generate comprehensive performance report"""
        load_profile = self.measure_page_load_performance()
        memory_profile = self.analyze_memory_usage()
        
        # Calculate overall score
        load_score = min(100, (self.performance_targets['load_time'] / max(load_profile.total_time, 0.1)) * 100)
        memory_score = min(100, (self.performance_targets['memory_usage'] / max(memory_profile.current_usage, 1)) * 100)
        overall_score = (load_score + memory_score) / 2
        
        # Check if meets targets
        meets_targets = (
            load_profile.total_time <= self.performance_targets['load_time'] and
            memory_profile.memory_efficient
        )
        
        # Generate recommendations
        recommendations = []
        if load_profile.total_time > self.performance_targets['load_time']:
            recommendations.append("🚀 Optimize page load time - currently exceeding 3-second target")
        
        if not memory_profile.memory_efficient:
            recommendations.append("💾 Optimize memory usage - implement efficient data management")
        
        if load_profile.rendering_time > 1.0:
            recommendations.append("🎨 Optimize rendering performance - consider component virtualization")
        
        recommendations.extend(memory_profile.recommendations)
        
        return PerformanceReport(
            overall_score=overall_score,
            load_time_profile=load_profile,
            memory_profile=memory_profile,
            metrics=self.metrics_history[-10:],  # Last 10 metrics
            recommendations=recommendations,
            meets_targets=meets_targets
        )
    
    def optimize_component_loading(self, component_func: Callable, component_name: str) -> Callable:
        """Apply performance optimizations to component loading with secure caching"""
        
        @functools.wraps(component_func)
        def optimized_wrapper(*args, **kwargs):
            try:
                from .enhanced_security import create_secure_cache_key, secure_cache
                
                # Create secure cache key
                cache_key = create_secure_cache_key(component_name, args, kwargs)
                
                # Check secure cache first
                if self._should_use_cache(cache_key):
                    cached_result = secure_cache.get(cache_key)
                    if cached_result is not None:
                        return cached_result
                
                # Apply lazy loading if enabled
                if self.lazy_loading_enabled and self._should_lazy_load(component_name):
                    result = self._lazy_load_component(component_func, args, kwargs, cache_key)
                else:
                    # Execute with performance monitoring
                    result = self.monitor_component_performance(component_name, 
                                                             lambda: component_func(*args, **kwargs))
                
                # Cache result if appropriate using secure cache
                if self._should_cache(component_name) and result is not None:
                    secure_cache.set(cache_key, result)
                
                return result
                
            except Exception as e:
                # Fallback to direct execution on error
                import logging
                logging.error(f"Error in component optimization for {component_name}: {e}")
                return component_func(*args, **kwargs)
        
        return optimized_wrapper
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if not PSUTIL_AVAILABLE:
            return 0.0
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def _record_performance_metric(self, metric_name: str, value: float, unit: str, 
                                 target: float, component_name: str = None) -> None:
        """Record a performance metric"""
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            unit=unit,
            target_value=target,
            meets_target=value <= target,
            timestamp=datetime.now(),
            component_name=component_name
        )
        
        self.metrics_history.append(metric)
        
        # Keep only recent metrics to prevent memory bloat
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-50:]
    
    def _should_use_cache(self, cache_key: str) -> bool:
        """Determine if cache should be used"""
        return cache_key in self.component_cache
    
    def _should_lazy_load(self, component_name: str) -> bool:
        """Determine if component should be lazy loaded"""
        heavy_components = ['interactive_charts', 'large_data_tables', 'complex_visualizations']
        return component_name in heavy_components
    
    def _lazy_load_component(self, component_func: Callable, args: tuple, 
                           kwargs: dict, cache_key: str) -> Any:
        """Implement lazy loading for component"""
        with st.spinner(f"Loading {component_func.__name__}..."):
            # Add small delay to demonstrate lazy loading
            time.sleep(0.1)
            result = component_func(*args, **kwargs)
            
            # Cache the lazy-loaded result
            self.component_cache[cache_key] = result
            return result
    
    def _should_cache(self, component_name: str) -> bool:
        """Determine if component result should be cached"""
        cacheable_components = ['charts', 'calculations', 'static_content']
        return any(cacheable in component_name.lower() for cacheable in cacheable_components)


class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
    
    def optimize_streamlit_config(self) -> None:
        """Apply Streamlit-specific performance optimizations"""
        # Set page config for better performance
        if 'performance_config_set' not in st.session_state:
            st.set_page_config(
                page_title="Real Estate Analysis Tool",
                page_icon="🏠",
                layout="wide",
                initial_sidebar_state="collapsed"  # Faster initial load
            )
            st.session_state['performance_config_set'] = True
    
    def implement_progressive_loading(self, components: List[str]) -> None:
        """Implement progressive loading strategy"""
        if 'progressive_loading_step' not in st.session_state:
            st.session_state['progressive_loading_step'] = 0
        
        current_step = st.session_state['progressive_loading_step']
        
        # Load components progressively
        if current_step < len(components):
            component_name = components[current_step]
            
            # Show loading progress
            progress = (current_step + 1) / len(components)
            st.progress(progress, text=f"Loading {component_name}...")
            
            # Simulate component loading
            time.sleep(0.5)  # Remove in production
            
            # Move to next component
            st.session_state['progressive_loading_step'] = current_step + 1
            st.rerun()
    
    def apply_caching_strategies(self) -> None:
        """Apply various caching strategies"""
        # Session state caching for expensive calculations
        if 'calculation_cache' not in st.session_state:
            st.session_state['calculation_cache'] = {}
        
        # Browser caching headers (would be set in deployment)
        cache_headers = {
            'Cache-Control': 'public, max-age=3600',  # 1 hour cache
            'ETag': f"version-{datetime.now().strftime('%Y%m%d')}"
        }
        
        # Component-level caching
        @st.cache_data(ttl=300)  # 5 minute cache
        def cached_calculation(input_params):
            # Expensive calculation here
            return {"result": "cached_value"}
        
        return cached_calculation
    
    def optimize_data_loading(self, data_size: str = "large") -> Dict[str, Any]:
        """Optimize data loading strategies"""
        optimization_strategies = {
            "small": {
                "batch_size": 1000,
                "use_pagination": False,
                "lazy_load": False
            },
            "medium": {
                "batch_size": 500,
                "use_pagination": True,
                "lazy_load": False
            },
            "large": {
                "batch_size": 100,
                "use_pagination": True,
                "lazy_load": True
            }
        }
        
        return optimization_strategies.get(data_size, optimization_strategies["medium"])
    
    def monitor_real_time_performance(self) -> None:
        """Monitor real-time performance metrics"""
        # Create performance dashboard in sidebar
        with st.sidebar:
            st.markdown("### ⚡ Performance Monitor")
            
            # Real-time metrics
            current_memory = self.monitor._get_memory_usage()
            load_profile = self.monitor.measure_page_load_performance()
            
            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Memory", f"{current_memory:.1f} MB", 
                         delta=f"Target: {self.monitor.performance_targets['memory_usage']:.0f} MB")
            
            with col2:
                st.metric("Load Time", f"{load_profile.total_time:.2f}s",
                         delta=f"Target: {self.monitor.performance_targets['load_time']:.1f}s")
            
            # Performance status
            if (current_memory <= self.monitor.performance_targets['memory_usage'] and 
                load_profile.total_time <= self.monitor.performance_targets['load_time']):
                st.success("🎯 Performance targets met")
            else:
                st.warning("⚠️ Performance optimization needed")


def create_performance_monitor() -> PerformanceMonitor:
    """Factory function to create performance monitor"""
    return PerformanceMonitor()


def show_performance_dashboard() -> None:
    """Display comprehensive performance dashboard"""
    st.markdown("### ⚡ Performance Dashboard")
    st.markdown("*Real-time performance monitoring and optimization*")
    
    # Create performance monitor
    monitor = create_performance_monitor()
    
    # Generate performance report
    with st.spinner("Analyzing performance metrics..."):
        report = monitor.generate_performance_report()
    
    # Overall performance score
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score_color = "green" if report.overall_score >= 80 else "orange" if report.overall_score >= 60 else "red"
        st.metric("Performance Score", f"{report.overall_score:.0f}/100")
        
    with col2:
        load_status = "✅" if report.load_time_profile.total_time <= 3.0 else "❌"
        st.metric("Load Time", f"{report.load_time_profile.total_time:.2f}s", 
                 delta=f"{load_status} Target: 3.0s")
    
    with col3:
        memory_status = "✅" if report.memory_profile.memory_efficient else "❌"
        st.metric("Memory Usage", f"{report.memory_profile.current_usage:.1f} MB",
                 delta=f"{memory_status} Target: 100 MB")
    
    with col4:
        targets_status = "🎯 Met" if report.meets_targets else "⚠️ Needs Work"
        st.metric("Performance Targets", targets_status)
    
    # Detailed performance breakdown
    st.markdown("---")
    
    # Load time breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⏱️ Load Time Breakdown")
        
        # Component load times
        component_data = report.load_time_profile.component_times
        if component_data:
            for component, load_time in sorted(component_data.items(), key=lambda x: x[1], reverse=True):
                percentage = (load_time / report.load_time_profile.total_time) * 100
                st.write(f"**{component.replace('_', ' ').title()}**: {load_time:.2f}s ({percentage:.1f}%)")
        
        # Performance indicators
        indicators = [
            ("Resource Loading", report.load_time_profile.resource_loading, 1.0),
            ("Rendering Time", report.load_time_profile.rendering_time, 0.5),
            ("Interactive Time", report.load_time_profile.interactive_time, 1.0),
            ("Largest Contentful Paint", report.load_time_profile.largest_contentful_paint, 2.5)
        ]
        
        for name, value, target in indicators:
            status = "✅" if value <= target else "⚠️"
            st.write(f"{status} **{name}**: {value:.2f}s (target: {target:.1f}s)")
    
    with col2:
        st.markdown("#### 💾 Memory Analysis")
        
        memory_data = [
            ("Current Usage", report.memory_profile.current_usage, "MB"),
            ("Peak Usage", report.memory_profile.peak_usage, "MB"),
            ("Available Memory", report.memory_profile.available_memory, "MB")
        ]
        
        for name, value, unit in memory_data:
            st.write(f"**{name}**: {value:.1f} {unit}")
        
        # Memory efficiency status
        if report.memory_profile.memory_efficient:
            st.success("✅ Memory usage is efficient")
        else:
            st.warning("⚠️ Memory usage needs optimization")
        
        # Memory recommendations
        if report.memory_profile.recommendations:
            st.markdown("**Recommendations:**")
            for rec in report.memory_profile.recommendations:
                st.write(f"• {rec}")
    
    # Performance recommendations
    st.markdown("---")
    st.markdown("#### 💡 Performance Recommendations")
    
    if report.recommendations:
        for i, recommendation in enumerate(report.recommendations):
            priority = "🔥 High" if i < 2 else "🟡 Medium" if i < 4 else "🔵 Low"
            st.write(f"**{priority} Priority**: {recommendation}")
    else:
        st.success("🎉 No performance recommendations - system is optimized!")
    
    # Performance trends (mock data)
    st.markdown("---")
    st.markdown("#### 📈 Performance Trends")
    
    # Mock trend data
    import plotly.graph_objects as go
    from datetime import datetime, timedelta
    
    dates = [datetime.now() - timedelta(hours=i) for i in range(24, 0, -1)]
    load_times = [2.1 + 0.5 * (i % 3) for i in range(24)]
    memory_usage = [85 + 15 * (i % 4) / 4 for i in range(24)]
    
    fig = go.Figure()
    
    # Load time trend
    fig.add_trace(go.Scatter(
        x=dates,
        y=load_times,
        mode='lines+markers',
        name='Load Time (s)',
        line=dict(color='blue')
    ))
    
    # Memory usage trend (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=dates,
        y=memory_usage,
        mode='lines+markers',
        name='Memory Usage (MB)',
        yaxis='y2',
        line=dict(color='red')
    ))
    
    # Add target lines
    fig.add_hline(y=3.0, line_dash="dash", line_color="blue", 
                  annotation_text="Load Time Target (3s)")
    fig.add_hline(y=100, line_dash="dash", line_color="red", 
                  annotation_text="Memory Target (100MB)", yaxis="y2")
    
    fig.update_layout(
        title='Performance Trends (Last 24 Hours)',
        xaxis_title='Time',
        yaxis=dict(title='Load Time (seconds)', side='left'),
        yaxis2=dict(title='Memory Usage (MB)', overlaying='y', side='right'),
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance optimization controls
    st.markdown("---")
    st.markdown("#### ⚙️ Performance Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Clear Cache", help="Clear component cache to free memory"):
            monitor.component_cache.clear()
            st.success("Cache cleared!")
    
    with col2:
        lazy_loading = st.checkbox("⚡ Enable Lazy Loading", 
                                 value=monitor.lazy_loading_enabled,
                                 help="Load components on demand")
        monitor.lazy_loading_enabled = lazy_loading
    
    with col3:
        if st.button("🔄 Force Garbage Collection", help="Trigger memory cleanup"):
            gc.collect()
            st.success("Memory cleanup performed!")
    
    # Performance tips
    with st.expander("💡 Performance Optimization Tips", expanded=False):
        tips = [
            "**Lazy Loading**: Enable lazy loading for heavy components like charts and large data tables",
            "**Caching**: Use @st.cache_data for expensive calculations and data processing",
            "**Component Optimization**: Break down large components into smaller, focused pieces",
            "**Memory Management**: Clear unused data from session state regularly",
            "**Progressive Enhancement**: Load core functionality first, then enhance with advanced features",
            "**Image Optimization**: Compress images and use appropriate formats (WebP when possible)",
            "**Code Splitting**: Load JavaScript and CSS only when needed",
            "**Database Optimization**: Use efficient queries and connection pooling",
            "**CDN Usage**: Serve static assets from a Content Delivery Network",
            "**Monitoring**: Regularly monitor performance metrics and set up alerts"
        ]
        
        for tip in tips:
            st.markdown(f"• {tip}")


def demo_performance_optimization():
    """Demo function for performance optimization features"""
    st.title("⚡ Performance Optimization Demo")
    
    # Show performance dashboard
    show_performance_dashboard()
    
    # Demo performance monitoring
    st.markdown("---")
    st.markdown("### 🧪 Performance Monitoring Demo")
    
    monitor = create_performance_monitor()
    optimizer = PerformanceOptimizer()
    
    # Test component performance
    if st.button("🧮 Test Heavy Calculation"):
        def heavy_calculation():
            # Simulate expensive operation
            total = 0
            for i in range(100000):
                total += i ** 0.5
            return total
        
        result = monitor.monitor_component_performance("heavy_calculation", heavy_calculation)
        st.write(f"Calculation result: {result:.2f}")
        st.success("Performance metrics recorded!")
    
    # Real-time performance monitoring
    optimizer.monitor_real_time_performance()


