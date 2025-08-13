"""
Optimized cache configuration for 80%+ hit rates
"""

from datetime import timedelta
from typing import Dict, Any

def get_optimized_cache_config() -> Dict[str, Any]:
    """Get optimized cache configuration for maximum hit rates"""
    return {
        'cache': {
            # Increased cache sizes for better hit rates
            'memory_cache_size_mb': 100.0,  # Increased from 50MB
            'persistent_cache_path': 'optimized_cache.db',
            
            # Optimized TTL settings
            'default_ttl_hours': 48.0,  # Increased from 24 hours
            'max_cache_age_days': 14.0,  # Increased from 7 days
            
            # Performance tuning
            'cleanup_interval_hours': 4.0,  # More frequent cleanup
            'optimization_interval_minutes': 15.0,  # More frequent optimization
        },
        'market_api': {
            'timeout': 15,
            'max_retries': 3,
            'fallback_enabled': True,
            'cache_priority': True  # Prefer cache over fresh API calls when possible
        },
        'interest_rates': {
            'cache_duration_hours': 6.0,  # Shorter TTL for rates (more volatile)
            'timeout': 10
        },
        'location': {
            'geocoding_cache_hours': 168.0,  # 7 days (locations don't change)
            'timeout': 10
        },
        # Performance targets for 80%+ hit rate
        'target_uptime': 0.99,
        'target_hit_rate': 0.80,
        'target_freshness_hours': 48,  # More lenient for better hit rates
        'target_response_time_ms': 100.0,
        
        # Cache optimization strategies
        'warmup': {
            'enabled': True,
            'priority_locations': [
                'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX',
                'Phoenix, AZ', 'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA',
                'Dallas, TX', 'San Jose, CA', 'Austin, TX', 'Jacksonville, FL',
                'Fort Worth, TX', 'Columbus, OH', 'Charlotte, NC', 'San Francisco, CA',
                'Indianapolis, IN', 'Seattle, WA', 'Denver, CO', 'Boston, MA',
                'Washington, DC', 'Nashville, TN', 'El Paso, TX', 'Detroit, MI',
                'Oklahoma City, OK', 'Portland, OR', 'Las Vegas, NV', 'Memphis, TN',
                'Louisville, KY', 'Baltimore, MD', 'Milwaukee, WI', 'Albuquerque, NM',
                'Tucson, AZ', 'Fresno, CA', 'Sacramento, CA', 'Mesa, AZ',
                'Kansas City, MO', 'Atlanta, GA', 'Long Beach, CA', 'Colorado Springs, CO',
                'Raleigh, NC', 'Miami, FL', 'Virginia Beach, VA', 'Omaha, NE',
                'Oakland, CA', 'Minneapolis, MN', 'Tulsa, OK', 'Arlington, TX',
                'Tampa, FL', 'New Orleans, LA'
            ]
        },
        
        # Proactive refresh settings
        'proactive_refresh': {
            'enabled': True,
            'refresh_threshold_hours': 24.0,  # Refresh when data is 24h old
            'refresh_interval_hours': 6.0,    # Check every 6 hours
            'batch_size': 5,                  # Refresh 5 locations at a time
            'max_concurrent_refreshes': 3    # Limit concurrent refreshes
        }
    }

def get_high_performance_cache_config() -> Dict[str, Any]:
    """Get even more aggressive cache configuration for maximum performance"""
    config = get_optimized_cache_config()
    
    # More aggressive settings
    config['cache']['memory_cache_size_mb'] = 200.0
    config['cache']['default_ttl_hours'] = 72.0  # 3 days
    config['target_hit_rate'] = 0.85  # Target 85%
    config['target_freshness_hours'] = 72  # Accept older data for higher hit rates
    
    # More extensive warmup
    config['warmup']['enabled'] = True
    config['proactive_refresh']['refresh_threshold_hours'] = 48.0
    
    return config

def get_production_cache_config() -> Dict[str, Any]:
    """Get production-ready cache configuration balancing performance and freshness"""
    return {
        'cache': {
            'memory_cache_size_mb': 150.0,
            'persistent_cache_path': '/var/cache/real_estate_data.db',
            'default_ttl_hours': 36.0,  # 1.5 days
            'max_cache_age_days': 10.0,
            'cleanup_interval_hours': 2.0,
            'optimization_interval_minutes': 30.0,
        },
        'market_api': {
            'timeout': 20,
            'max_retries': 4,
            'fallback_enabled': True,
            'cache_priority': True,
            # Production API keys would go here
            'api_keys': {
                'primary_api_key': '${PRIMARY_REAL_ESTATE_API_KEY}',
                'secondary_api_key': '${SECONDARY_REAL_ESTATE_API_KEY}',
                'fred_api_key': '${FRED_API_KEY}',
                'google_maps_api_key': '${GOOGLE_MAPS_API_KEY}'
            }
        },
        'target_uptime': 0.995,  # 99.5% uptime
        'target_hit_rate': 0.82,  # Realistic production target
        'target_freshness_hours': 24,
        'target_response_time_ms': 150.0,
        
        'warmup': {
            'enabled': True,
            'on_startup': True,
            'background_refresh': True
        },
        
        'proactive_refresh': {
            'enabled': True,
            'refresh_threshold_hours': 18.0,
            'refresh_interval_hours': 4.0,
            'batch_size': 3,
            'max_concurrent_refreshes': 2
        },
        
        # Production monitoring
        'monitoring': {
            'enabled': True,
            'metrics_interval_minutes': 5.0,
            'health_check_interval_minutes': 1.0,
            'alert_on_hit_rate_below': 0.75,
            'alert_on_response_time_above_ms': 500.0
        }
    }