"""
Health check and stability utilities for Streamlit Cloud
Helps prevent crashes and memory issues
"""

import streamlit as st
import psutil
import gc
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

class StreamlitHealthManager:
    """Manages app health and prevents common Streamlit Cloud crashes"""
    
    def __init__(self):
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(minutes=30)  # Cleanup every 30 minutes
        self.max_memory_mb = 512  # Streamlit Cloud limit
        
    def check_and_cleanup(self) -> None:
        """Periodic health check and cleanup"""
        now = datetime.now()
        
        # Only run cleanup periodically to avoid performance impact
        if now - self.last_cleanup >= self.cleanup_interval:
            self._memory_cleanup()
            self._session_cleanup()
            self.last_cleanup = now
            
    def _memory_cleanup(self) -> None:
        """Clean up memory to prevent OOM crashes"""
        try:
            # Get current memory usage
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > self.max_memory_mb * 0.8:  # 80% of limit
                logger.warning(f"High memory usage: {memory_mb:.1f}MB")
                
                # Force garbage collection
                gc.collect()
                
                # Clear large session state items if they exist
                large_keys = []
                for key in st.session_state.keys():
                    try:
                        # Check if session state item is large
                        import sys
                        size = sys.getsizeof(st.session_state[key])
                        if size > 10 * 1024 * 1024:  # 10MB
                            large_keys.append(key)
                    except:
                        pass
                
                # Clear large items (but keep essential data)
                essential_keys = {
                    'analysis_results', 'ownership_flows', 'rental_flows',
                    'purchase_price', 'current_annual_rent', 'rent_increase_rate'
                }
                
                for key in large_keys:
                    if key not in essential_keys:
                        logger.info(f"Clearing large session state item: {key}")
                        del st.session_state[key]
                
                gc.collect()
                
        except Exception as e:
            logger.error(f"Memory cleanup failed: {e}")
    
    def _session_cleanup(self) -> None:
        """Clean up old session data"""
        try:
            # Clear temporary/cache keys that might accumulate
            temp_keys = [key for key in st.session_state.keys() 
                        if key.startswith('_temp_') or key.startswith('_cache_')]
            
            for key in temp_keys:
                del st.session_state[key]
                
        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")
    
    def add_health_metrics(self) -> None:
        """Add health metrics to sidebar (debug mode)"""
        if st.sidebar.checkbox("Show Health Metrics", value=False):
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent()
                
                st.sidebar.metric("Memory Usage", f"{memory_mb:.1f} MB")
                st.sidebar.metric("CPU Usage", f"{cpu_percent:.1f}%")
                st.sidebar.metric("Session Keys", len(st.session_state.keys()))
                
                if memory_mb > self.max_memory_mb * 0.7:
                    st.sidebar.warning("⚠️ High memory usage detected")
                    
            except Exception as e:
                st.sidebar.error(f"Health check error: {e}")

# Global health manager instance
_health_manager: Optional[StreamlitHealthManager] = None

def get_health_manager() -> StreamlitHealthManager:
    """Get or create global health manager"""
    global _health_manager
    if _health_manager is None:
        _health_manager = StreamlitHealthManager()
    return _health_manager

def periodic_health_check():
    """Run periodic health check - call this in your main app"""
    health_manager = get_health_manager()
    health_manager.check_and_cleanup()