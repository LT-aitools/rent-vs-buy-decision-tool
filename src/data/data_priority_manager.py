"""
Data Priority Manager
Implements the data hierarchy: User Input > API Data > Default Data
Ensures user-provided values always take precedence over API data
"""

import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class DataPriorityManager:
    """
    Manages data priority hierarchy for the real estate analysis tool
    Dynamic behavior: Default -> API updates -> User overrides
    """
    
    def __init__(self):
        self.user_overrides = {}  # User has manually changed these fields
        self.api_data = {}
        self.default_data = {}
        self.user_touched_fields = set()  # Track which fields user has manually modified
        self.last_updated = datetime.now()
        
    def set_user_override(self, key: str, value: Any, source: str = "user_input") -> None:
        """
        Set a user override value that takes precedence over API and default data
        This marks the field as user-touched, preventing future API updates
        
        Args:
            key: The data key (e.g., 'interest_rate', 'market_appreciation_rate')
            value: The user-provided value
            source: Source description for logging
        """
        self.user_overrides[key] = {
            'value': value,
            'source': source,
            'timestamp': datetime.now()
        }
        self.user_touched_fields.add(key)  # Mark as user-modified
        logger.info(f"User override set: {key} = {value} (source: {source})")
        
    def set_api_data(self, key: str, value: Any, source: str = "api", confidence: float = 1.0, force_update: bool = False, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Set API data that will be used if user hasn't manually modified the field
        
        Args:
            key: The data key
            value: The API-provided value
            source: API source name
            confidence: Confidence level of the API data (0.0 to 1.0)
            force_update: If True, update even if user has touched the field
            metadata: Additional metadata (data_date, country, etc.)
            
        Returns:
            True if the API data was set/updated, False if blocked by user override
        """
        # Don't override user-modified fields unless forced
        if key in self.user_touched_fields and not force_update:
            logger.debug(f"API data blocked for {key} - user has manually modified this field")
            return False
            
        api_entry = {
            'value': value,
            'source': source,
            'confidence': confidence,
            'timestamp': datetime.now()
        }
        
        # Add metadata if provided
        if metadata:
            api_entry['metadata'] = metadata
            
        self.api_data[key] = api_entry
        logger.debug(f"API data set: {key} = {value} (source: {source}, confidence: {confidence})")
        return True
        
    def set_default_data(self, key: str, value: Any, source: str = "default") -> None:
        """
        Set default fallback data used when no user override or API data exists
        
        Args:
            key: The data key
            value: The default value
            source: Source description
        """
        self.default_data[key] = {
            'value': value,
            'source': source,
            'timestamp': datetime.now()
        }
        logger.debug(f"Default data set: {key} = {value} (source: {source})")
        
    def get_value(self, key: str, default_fallback: Any = None) -> Dict[str, Any]:
        """
        Get the appropriate value for a key based on dynamic priority logic:
        1. User override (if user has manually modified the field)
        2. API data (if available and user hasn't touched the field)  
        3. Default data (fallback)
        
        Args:
            key: The data key to retrieve
            default_fallback: Final fallback value if key not found anywhere
            
        Returns:
            Dict with 'value', 'source', 'priority_level', and metadata
        """
        # Priority 1: User override (user has manually changed this field)
        if key in self.user_overrides:
            override_data = self.user_overrides[key]
            return {
                'value': override_data['value'],
                'source': override_data['source'],
                'priority_level': 'user_override',
                'timestamp': override_data['timestamp'],
                'confidence': 1.0,
                'user_modified': True
            }
        
        # Priority 2: API data (if available and user hasn't modified the field)
        if key in self.api_data:
            api_data = self.api_data[key]
            result = {
                'value': api_data['value'],
                'source': api_data['source'], 
                'priority_level': 'api_data',
                'timestamp': api_data['timestamp'],
                'confidence': api_data.get('confidence', 1.0),
                'user_modified': False
            }
            
            # Include metadata if available
            if 'metadata' in api_data:
                result['metadata'] = api_data['metadata']
                
            return result
            
        # Priority 3: Default data
        if key in self.default_data:
            default_data = self.default_data[key]
            return {
                'value': default_data['value'],
                'source': default_data['source'],
                'priority_level': 'default_data',
                'timestamp': default_data['timestamp'],
                'confidence': 0.7,
                'user_modified': False
            }
            
        # Final fallback
        if default_fallback is not None:
            logger.warning(f"Using final fallback for {key}: {default_fallback}")
            return {
                'value': default_fallback,
                'source': 'final_fallback',
                'priority_level': 'fallback',
                'timestamp': datetime.now(),
                'confidence': 0.3,
                'user_modified': False
            }
            
        raise ValueError(f"No data available for key: {key}")
        
    def get_value_only(self, key: str, default_fallback: Any = None) -> Any:
        """
        Get just the value (not metadata) for a key
        
        Args:
            key: The data key to retrieve
            default_fallback: Final fallback value if key not found
            
        Returns:
            The actual value
        """
        try:
            return self.get_value(key, default_fallback)['value']
        except ValueError:
            return default_fallback
            
    def clear_user_overrides(self) -> None:
        """Clear all user overrides and user-touched fields"""
        self.user_overrides.clear()
        self.user_touched_fields.clear()  # Also clear the touched fields set
        logger.info("All user overrides and touched fields cleared")
        
    def clear_api_data(self) -> None:
        """Clear all API data"""
        self.api_data.clear()
        logger.info("All API data cleared")
        
    def get_data_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Get a summary of all data sources and their priority status
        
        Returns:
            Dict organized by data key with priority information
        """
        all_keys = set(self.user_overrides.keys()) | set(self.api_data.keys()) | set(self.default_data.keys())
        
        summary = {}
        for key in all_keys:
            try:
                active_data = self.get_value(key)
                summary[key] = {
                    'active_value': active_data['value'],
                    'active_source': active_data['source'],
                    'priority_level': active_data['priority_level'],
                    'has_user_override': key in self.user_overrides,
                    'has_api_data': key in self.api_data,
                    'has_default': key in self.default_data,
                    'confidence': active_data.get('confidence', 1.0)
                }
            except ValueError:
                summary[key] = {
                    'active_value': None,
                    'active_source': None,
                    'priority_level': None,
                    'has_user_override': key in self.user_overrides,
                    'has_api_data': key in self.api_data,
                    'has_default': key in self.default_data,
                    'confidence': 0.0
                }
                
        return summary
        
    def bulk_update_from_session(self, session_data: Dict[str, Any]) -> None:
        """
        Update user overrides from session data
        
        Args:
            session_data: Dictionary of user inputs from session
        """
        # Map common session keys to data keys
        session_mapping = {
            'interest_rate': 'interest_rate',
            'market_appreciation_rate': 'market_appreciation_rate',
            'rent_increase_rate': 'rent_increase_rate', 
            'property_tax_rate': 'property_tax_rate',
            'inflation_rate': 'inflation_rate',
            'cost_of_capital': 'cost_of_capital',
            'corporate_tax_rate': 'corporate_tax_rate'
        }
        
        inputs = session_data.get('inputs', {})
        updated_count = 0
        
        for session_key, data_key in session_mapping.items():
            if session_key in inputs and inputs[session_key] is not None:
                self.set_user_override(data_key, inputs[session_key], f"user_input:{session_key}")
                updated_count += 1
                
        logger.info(f"Updated {updated_count} user overrides from session data")
        
    def update_from_address_api(self, address: str, interest_rates: Dict[str, float], market_data: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
        """
        Update data from API based on address input, respecting user-touched fields
        
        Args:
            address: The user-provided address
            interest_rates: Interest rates from API
            market_data: Optional market data from API
            
        Returns:
            Dict showing which fields were updated
        """
        updates = {}
        
        # Interest rate fields (FRED API)
        interest_rate_mapping = {
            '30_year_fixed': 'interest_rate',
            '15_year_fixed': 'interest_rate_15_year',
            'federal_funds_rate': 'federal_funds_rate'
        }
        
        for api_key, data_key in interest_rate_mapping.items():
            if api_key in interest_rates:
                updates[data_key] = self.set_api_data(
                    data_key, 
                    interest_rates[api_key], 
                    f"fred_api_for_{address}"
                )
        
        # Market data fields (if available from market API)
        if market_data:
            market_mapping = {
                'property_appreciation_rate': 'market_appreciation_rate',
                'rental_growth_rate': 'rent_increase_rate', 
                'local_inflation_rate': 'inflation_rate',
                'property_tax_rate': 'property_tax_rate',
                'unemployment_rate': 'unemployment_rate',
                'population_growth_rate': 'population_growth_rate',
                'median_rent_per_sqm': 'median_rent_per_sqm',
                'median_property_price': 'median_property_price',
                'rental_vacancy_rate': 'rental_vacancy_rate'
            }
            
            for api_key, data_key in market_mapping.items():
                if api_key in market_data:
                    confidence = market_data.get('confidence_score', 0.8)
                    updates[data_key] = self.set_api_data(
                        data_key,
                        market_data[api_key],
                        f"market_api_for_{address}",
                        confidence
                    )
                    
        # For now, create some location-based estimates for market data
        # This would be replaced with real market API integration
        location_estimates = self._get_location_based_estimates(address)
        for field, value in location_estimates.items():
            if field not in updates:  # Only if not already updated from real API
                updates[field] = self.set_api_data(
                    field,
                    value,
                    f"location_estimate_for_{address}",
                    0.6  # Lower confidence for estimates
                )
            
        logger.info(f"Address-based API update for {address}: {sum(updates.values())}/{len(updates)} fields updated")
        return updates
    
    def _get_location_based_estimates(self, address: str) -> Dict[str, float]:
        """
        Generate location-based estimates for market data
        Handles both US and international locations
        """
        estimates = {}
        
        # First try international data
        try:
            from data.international_data import get_international_provider
            international_provider = get_international_provider()
            
            # Parse location to determine if it's international
            city, state, country = international_provider.parse_location(address)
            
            # Only use international data for non-US countries
            if country and country != 'usa':
                international_data = international_provider.get_international_estimates(address)
                if international_data['estimates']:
                    logger.info(f"Using international data for {address}: {international_data['metadata']['country']}")
                    # For international locations, exclude interest_rate as it's handled separately
                    int_estimates = international_data['estimates'].copy()
                    int_estimates.pop('interest_rate', None)  # Remove interest rate - handled by address handler
                    
                    # Store metadata for UI display
                    metadata = international_data['metadata']
                    for field_name, value in int_estimates.items():
                        self.set_api_data(
                            field_name, 
                            value, 
                            f"international_data_for_{address}", 
                            confidence=metadata.get('confidence', 0.75),
                            metadata=metadata
                        )
                    
                    return int_estimates
                
        except ImportError:
            logger.warning("International data provider not available")
        
        # Fall back to US-specific estimates
        address_lower = address.lower()
        
        # Check if this looks like a US location
        us_indicators = ['usa', 'united states', 'us,', ', us']
        is_likely_us = any(indicator in address_lower for indicator in us_indicators)
        
        # Check for non-US country indicators
        non_us_countries = ['uk', 'canada', 'australia', 'germany', 'france', 'japan', 'singapore', 'brazil', 'poland', 'israel', 'georgia', 'armenia', 'ukraine', 'russia', 'turkey', 'romania', 'china']
        is_likely_international = any(country in address_lower for country in non_us_countries)
        
        if is_likely_international and not is_likely_us:
            # International location without specific data - return empty dict to use defaults
            logger.info(f"International location detected ({address}) - no specific data, using defaults")
            return {}  # Return empty dict so defaults are used
        
        # US-specific estimates (existing logic)
        # Market appreciation rate estimates
        if any(city in address_lower for city in ['san francisco', 'new york', 'seattle', 'boston']):
            estimates['market_appreciation_rate'] = 4.5  # High-growth cities
        elif any(city in address_lower for city in ['austin', 'denver', 'miami', 'portland']):
            estimates['market_appreciation_rate'] = 3.8  # Medium-growth cities
        else:
            estimates['market_appreciation_rate'] = 3.2  # Average
            
        # Rent increase rate estimates (nominal rates)
        us_inflation_rate = 3.0  # Current US inflation target
        if any(city in address_lower for city in ['san francisco', 'new york', 'boston']):
            nominal_rent_rate = 4.2
        elif any(city in address_lower for city in ['los angeles', 'chicago', 'washington']):
            nominal_rent_rate = 3.5
        else:
            nominal_rent_rate = 3.1
        
        # Apply inflation adjustment to prevent double-counting
        real_rent_rate = max(0.0, round(nominal_rent_rate - us_inflation_rate, 1))  # Round to 1 decimal, minimum 0%
        estimates['rent_increase_rate'] = real_rent_rate
        estimates['inflation_rate'] = us_inflation_rate
        estimates['corporate_tax_rate'] = 25.0  # US federal corporate tax rate (21%) + average state (4%)
            
        # Property tax rate estimates by state
        state_tax_rates = {
            'ca': 0.8, 'ny': 1.4, 'tx': 1.9, 'fl': 1.0, 'wa': 1.1,
            'il': 2.3, 'pa': 1.6, 'oh': 1.6, 'ga': 1.0, 'nc': 1.0
        }
        
        for state, rate in state_tax_rates.items():
            if f', {state}' in address_lower or f' {state} ' in address_lower:
                estimates['property_tax_rate'] = rate
                break
        else:
            estimates['property_tax_rate'] = 1.2  # US national average
            
        return estimates
        
    def is_field_user_modified(self, key: str) -> bool:
        """Check if a field has been manually modified by the user"""
        return key in self.user_touched_fields
        
    def reset_field_to_api(self, key: str) -> bool:
        """
        Reset a field to allow API updates again (removes user override)
        
        Args:
            key: The field to reset
            
        Returns:
            True if field was reset, False if no user override existed
        """
        if key in self.user_overrides:
            del self.user_overrides[key]
            
        if key in self.user_touched_fields:
            self.user_touched_fields.remove(key)
            logger.info(f"Field {key} reset to allow API updates")
            return True
            
        return False
        
    def apply_api_rates(self, interest_rates: Dict[str, float], market_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Apply API-sourced rates and market data
        
        Args:
            interest_rates: Dictionary of interest rates from API
            market_data: Optional market data from API
        """
        # Apply interest rates
        rate_mapping = {
            '30_year_fixed': 'interest_rate_30_year',
            '15_year_fixed': 'interest_rate_15_year',
            'federal_funds_rate': 'federal_funds_rate'
        }
        
        for api_key, data_key in rate_mapping.items():
            if api_key in interest_rates:
                self.set_api_data(data_key, interest_rates[api_key], f"fred_api:{api_key}")
                
        # Apply market data if provided
        if market_data:
            market_mapping = {
                'property_appreciation_rate': 'market_appreciation_rate',
                'rental_growth_rate': 'rent_increase_rate',
                'local_inflation_rate': 'local_inflation_rate'
            }
            
            for market_key, data_key in market_mapping.items():
                if market_key in market_data:
                    confidence = market_data.get('confidence_score', 0.8)
                    self.set_api_data(data_key, market_data[market_key], f"market_api:{market_key}", confidence)
                    
    def initialize_defaults(self) -> None:
        """Initialize system with default values for all API-integrated fields"""
        defaults = {
            # Interest rates (FRED API)
            'interest_rate': 7.0,
            'interest_rate_30_year': 6.78,
            'interest_rate_15_year': 6.21,
            'federal_funds_rate': 5.25,
            
            # Market data (Market API + Economic data)
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'property_tax_rate': 1.2,
            'inflation_rate': 3.0,
            'local_inflation_rate': 3.0,
            'unemployment_rate': 4.1,
            'population_growth_rate': 1.0,
            
            # Other calculated/derived fields
            'cost_of_capital': 8.0,
            'median_rent_per_sqm': 25.0,
            'median_property_price': 450000.0,
            'rental_vacancy_rate': 5.2
        }
        
        for key, value in defaults.items():
            self.set_default_data(key, value, "system_default")
            
        logger.info(f"Initialized {len(defaults)} default values")


# Global instance for the application
_global_priority_manager = None

def get_data_priority_manager() -> DataPriorityManager:
    """Get the global data priority manager instance"""
    global _global_priority_manager
    if _global_priority_manager is None:
        _global_priority_manager = DataPriorityManager()
        _global_priority_manager.initialize_defaults()
    return _global_priority_manager

def reset_data_priority_manager() -> DataPriorityManager:
    """Reset and get a fresh data priority manager instance"""
    global _global_priority_manager
    _global_priority_manager = DataPriorityManager()
    _global_priority_manager.initialize_defaults()
    return _global_priority_manager