"""
Address-based API Handler
Triggers API updates when user enters address information
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from data.data_priority_manager import get_data_priority_manager
from data.interest_rate_feeds import create_interest_rate_feeds

logger = logging.getLogger(__name__)


class AddressAPIHandler:
    """
    Handles API updates triggered by address changes
    Implements the flow: Address input -> API lookup -> Update fields (if not user-modified)
    """
    
    def __init__(self):
        self.last_address = None
        self.last_update = None
        self.priority_manager = get_data_priority_manager()
        
    async def handle_address_change(self, address: str, zip_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle address change by fetching updated rates and market data
        
        Args:
            address: The user-provided address
            zip_code: Optional zip code
            
        Returns:
            Dict with update results and any errors
        """
        if not address or address == self.last_address:
            return {'updated': False, 'reason': 'No address change'}
            
        logger.info(f"Processing address change: {address}")
        
        try:
            # Check if this is an international location
            from data.international_data import get_international_provider
            international_provider = get_international_provider()
            
            current_rates = {}
            market_data = None
            
            # Only fetch US rates for US locations
            if self._is_us_location(address):
                # Clear any existing international API data when switching to US location
                self.priority_manager.clear_api_data()
                # Fetch US interest rates from FRED
                rate_feeds = create_interest_rate_feeds()
                current_rates = await rate_feeds.get_current_rates(['30_year_fixed', '15_year_fixed'])
                await rate_feeds.close()
            else:
                # For international locations, try live rates first, then fallback to static
                try:
                    # Try to get live rates (async version preferred)
                    international_data = await international_provider.get_international_estimates_with_live_rates(address)
                except Exception as e:
                    # Fallback to static version if async fails
                    logger.debug(f"Async international data failed, using static: {e}")
                    international_data = international_provider.get_international_estimates(address)
                
                if international_data['estimates']:
                    # Clear any existing API data when switching to supported international location
                    self.priority_manager.clear_api_data()
                    
                    # Set all international data fields with metadata
                    metadata = international_data['metadata']
                    estimates = international_data['estimates']
                    
                    # Map all international fields to priority manager
                    field_mapping = {
                        'interest_rate': 'interest_rate',
                        'market_appreciation_rate': 'market_appreciation_rate', 
                        'rent_increase_rate': 'rent_increase_rate',
                        'property_tax_rate': 'property_tax_rate',
                        'inflation_rate': 'inflation_rate'
                    }
                    
                    for field_name, value in estimates.items():
                        if field_name in field_mapping:
                            priority_field = field_mapping[field_name]
                            # Include data date in source name as fallback
                            data_date = metadata.get('data_date', '2024-08-14')
                            source_name = f"international_data_for_{address}_({data_date})"
                            
                            self.priority_manager.set_api_data(
                                priority_field,
                                value,
                                source_name,
                                confidence=metadata.get('confidence', 0.75),
                                metadata=metadata
                            )
                    
                    # Also set current_rates for compatibility
                    int_rate = estimates.get('interest_rate')
                    if int_rate:
                        current_rates['30_year_fixed'] = int_rate
                        
                        # Add metadata about live rate usage
                        if metadata.get('live_rate_used'):
                            logger.info(f"Using live rate for {address}: {int_rate}% from {metadata['source']}")
                        else:
                            logger.info(f"Using static rate for {address}: {int_rate}% (data from {metadata.get('data_date', 'unknown date')})")
                else:
                    # No international data found - clear API data to prevent old tooltips
                    self.priority_manager.clear_api_data()
                    logger.info(f"No data available for {address}, cleared API data for clean defaults")
                        
            # Fetch market data (if we had a real market API)
            # Note: Market data API integration would go here in production
                
            # For international data, we've already set the metadata directly
            # Only use update_from_address_api for US data (FRED)
            if self._is_us_location(address):
                # Update priority manager with new API data
                logger.info(f"Updating US rates for {address}: {current_rates}")
                updates = self.priority_manager.update_from_address_api(
                    address, 
                    current_rates, 
                    market_data
                )
                logger.info(f"US rate updates: {updates}")
            else:
                # For international data, only show updates if we actually have data
                if current_rates or (international_data and international_data['estimates']):
                    # We have international data - show updates
                    updates = {field: True for field in ['interest_rate', 'market_appreciation_rate', 'rent_increase_rate', 'property_tax_rate', 'inflation_rate']}
                else:
                    # No international data found - no updates to report
                    updates = {}
            
            # Track this update
            self.last_address = address
            self.last_update = datetime.now()
            
            # Only claim "updated" if we actually updated fields
            actually_updated = len(current_rates) > 0 or len(updates) > 0
            
            return {
                'updated': actually_updated,
                'address': address,
                'rates_fetched': current_rates,
                'field_updates': updates,
                'timestamp': self.last_update.isoformat() if actually_updated else None
            }
            
        except Exception as e:
            logger.error(f"Error handling address change: {e}")
            return {
                'updated': False,
                'error': str(e),
                'address': address
            }
    
    def get_current_field_values(self) -> Dict[str, Any]:
        """
        Get current values for all API-managed fields
        
        Returns:
            Dict of field names to their current values and metadata
        """
        # All fields that can be updated via API
        fields = [
            'interest_rate', 'interest_rate_15_year', 'federal_funds_rate',
            'market_appreciation_rate', 'rent_increase_rate', 'property_tax_rate',
            'inflation_rate', 'unemployment_rate', 'population_growth_rate',
            'median_rent_per_sqm', 'median_property_price', 'rental_vacancy_rate'
        ]
        result = {}
        
        for field in fields:
            try:
                value_data = self.priority_manager.get_value(field)
                result[field] = {
                    'value': value_data['value'],
                    'source': value_data['source'],
                    'user_modified': value_data.get('user_modified', False),
                    'priority_level': value_data['priority_level']
                }
            except ValueError:
                result[field] = {
                    'value': None,
                    'source': 'not_available',
                    'user_modified': False,
                    'priority_level': None
                }
                
        return result
    
    def mark_field_as_user_modified(self, field: str, value: Any) -> None:
        """
        Mark a field as user-modified when user changes it manually
        
        Args:
            field: The field name
            value: The new user-provided value
        """
        self.priority_manager.set_user_override(field, value, "user_manual_input")
        logger.info(f"Field {field} marked as user-modified with value: {value}")
        
    def reset_field_to_api(self, field: str) -> bool:
        """
        Reset a field to allow API updates again
        
        Args:
            field: The field to reset
            
        Returns:
            True if reset was successful
        """
        return self.priority_manager.reset_field_to_api(field)
        
    def _is_us_location(self, address: str) -> bool:
        """Check if location appears to be in the US"""
        from data.international_data import get_international_provider
        international_provider = get_international_provider()
        
        city, state, country = international_provider.parse_location(address)
        
        # If country is explicitly identified and it's not US, return False
        if country and country != 'usa':
            return False
            
        # If country is explicitly US, return True
        if country == 'usa':
            return True
            
        # If no country specified, use heuristics (existing logic)
        address_lower = address.lower()
        us_indicators = ['usa', 'united states', 'us,', ', us']
        
        # Check for explicit US indicators
        if any(indicator in address_lower for indicator in us_indicators):
            return True
            
        # Check for non-US country indicators
        non_us_countries = ['uk', 'canada', 'australia', 'germany', 'france', 'japan', 'singapore', 'brazil', 'poland', 'israel', 'sweden', 'norway', 'denmark', 'italy', 'spain', 'georgia', 'armenia', 'ukraine', 'russia', 'turkey', 'romania', 'china']
        if any(country in address_lower for country in non_us_countries):
            return False
            
        # Default to US if unclear (existing behavior)
        return True


# Global instance
_global_address_handler = None

def get_address_api_handler() -> AddressAPIHandler:
    """Get the global address API handler instance"""
    global _global_address_handler
    if _global_address_handler is None:
        _global_address_handler = AddressAPIHandler()
    return _global_address_handler

def reset_address_api_handler() -> AddressAPIHandler:
    """Reset and get a fresh address API handler instance"""
    global _global_address_handler
    _global_address_handler = AddressAPIHandler()
    return _global_address_handler