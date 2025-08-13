"""
Real Estate Market Data API Integration
Handles connections to various real estate APIs for US markets with international guidance
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import asdict

from ..shared.interfaces import MarketData, DataRequest, DataValidationResult, DataProvider

logger = logging.getLogger(__name__)


class MarketDataAPI(DataProvider):
    """
    Primary market data API integration with multiple source fallbacks
    Focused on US real estate data with guidance for international markets
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.api_keys = self.config.get('api_keys', {})
        self.timeout = self.config.get('timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        self.fallback_enabled = self.config.get('fallback_enabled', True)
        
        # API endpoints (mock endpoints for development)
        self.endpoints = {
            'primary': {
                'url': self.config.get('primary_api_url', 'https://api.realestate-mock.com/v1'),
                'key': self.api_keys.get('primary_api_key'),
                'weight': 1.0
            },
            'secondary': {
                'url': self.config.get('secondary_api_url', 'https://api.zillow-mock.com/v2'),
                'key': self.api_keys.get('secondary_api_key'),
                'weight': 0.8
            },
            'tertiary': {
                'url': self.config.get('tertiary_api_url', 'https://api.realtor-mock.com/v1'),
                'key': self.api_keys.get('tertiary_api_key'),
                'weight': 0.6
            }
        }
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache_manager = None  # Will be injected
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create async HTTP session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def _make_request(self, endpoint: str, endpoint_config: Dict, params: Dict) -> Dict:
        """Make API request with retry logic"""
        session = await self._get_session()
        
        headers = {}
        if endpoint_config['key']:
            headers['Authorization'] = f"Bearer {endpoint_config['key']}"
            headers['X-API-Key'] = endpoint_config['key']
        
        url = f"{endpoint_config['url']}/market-data"
        
        for attempt in range(self.max_retries):
            try:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully fetched data from {endpoint} (attempt {attempt + 1})")
                        return data
                    elif response.status == 429:  # Rate limited
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limited on {endpoint}, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"API error from {endpoint}: {response.status}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on {endpoint} (attempt {attempt + 1})")
            except Exception as e:
                logger.warning(f"Error on {endpoint} (attempt {attempt + 1}): {e}")
                
            if attempt < self.max_retries - 1:
                await asyncio.sleep(1)
        
        raise Exception(f"Failed to fetch data from {endpoint} after {self.max_retries} attempts")
    
    def get_market_data(self, request: DataRequest) -> MarketData:
        """Retrieve market data for location (sync wrapper for async method)"""
        # This method should rarely be called directly - prefer the async version
        try:
            return asyncio.run(self._get_market_data_async(request))
        except RuntimeError:
            # Already in event loop - return a minimal fallback
            logger.warning("get_market_data called from async context, returning minimal data")
            return self._create_sync_fallback_data(request)
    
    async def _get_market_data_async(self, request: DataRequest) -> MarketData:
        """Async implementation of market data retrieval"""
        logger.info(f"Fetching market data for {request.location}")
        
        # Check cache first if enabled
        if request.fallback_to_cache and self.cache_manager:
            cached_data = self.cache_manager.get_cached_data(request.location)
            if cached_data and cached_data.freshness_hours <= request.max_age_hours:
                logger.info(f"Using cached data for {request.location}")
                return cached_data
        
        # Handle international locations with guidance
        if not self._is_us_location(request.location):
            return self._get_international_guidance(request)
        
        # Try multiple API sources
        api_errors = []
        for endpoint_name, endpoint_config in self.endpoints.items():
            if not endpoint_config['key']:
                continue
                
            try:
                params = self._build_api_params(request)
                raw_data = await self._make_request(endpoint_name, endpoint_config, params)
                
                # Transform API response to our MarketData format
                market_data = self._transform_api_response(
                    raw_data, request, endpoint_name, endpoint_config['weight']
                )
                
                # Update cache
                if self.cache_manager:
                    self.cache_manager.update_cache(request.location, market_data)
                
                return market_data
                
            except Exception as e:
                api_errors.append(f"{endpoint_name}: {str(e)}")
                logger.warning(f"Failed to get data from {endpoint_name}: {e}")
                continue
        
        # If all APIs fail, try fallback mechanisms
        if self.fallback_enabled:
            return await self._get_fallback_data(request, api_errors)
        
        raise Exception(f"Failed to retrieve market data: {'; '.join(api_errors)}")
    
    def _is_us_location(self, location: str) -> bool:
        """Check if location is in the US"""
        us_indicators = ['usa', 'united states', 'us,', ', us', ', usa']
        location_lower = location.lower()
        
        # Check for explicit US indicators
        for indicator in us_indicators:
            if indicator in location_lower:
                return True
        
        # Check for US state abbreviations or names
        us_states = [
            'al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia', 'ks',
            'ky', 'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj', 'nm', 'ny',
            'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt', 'va', 'wa', 'wv', 'wi', 'wy'
        ]
        
        # Simple heuristic: if no country specified and has state-like patterns, assume US
        if not any(country in location_lower for country in ['canada', 'uk', 'australia', 'germany']):
            return True
            
        return False
    
    def _get_international_guidance(self, request: DataRequest) -> MarketData:
        """Provide guidance for international properties"""
        logger.info(f"Providing international guidance for {request.location}")
        
        return MarketData(
            location=request.location,
            zip_code=request.zip_code,
            
            # Default rental market data with guidance note
            median_rent_per_sqm=0.0,
            rental_vacancy_rate=0.0,
            rental_growth_rate=0.0,
            
            # Default property market data
            median_property_price=0.0,
            property_appreciation_rate=0.0,
            months_on_market=0.0,
            
            # Default interest rates
            current_mortgage_rates={"guidance": 0.0},
            rate_trend="unknown",
            
            # Default economic indicators
            local_inflation_rate=0.0,
            unemployment_rate=0.0,
            population_growth_rate=0.0,
            
            # Metadata indicating this is guidance
            data_timestamp=datetime.now(),
            data_sources=["international_guidance"],
            confidence_score=0.0,
            freshness_hours=0.0
        )
    
    def _build_api_params(self, request: DataRequest) -> Dict:
        """Build API parameters from request"""
        params = {
            'location': request.location,
            'data_types': ','.join(request.data_types)
        }
        
        if request.zip_code:
            params['zip_code'] = request.zip_code
            
        return params
    
    def _transform_api_response(
        self, 
        raw_data: Dict, 
        request: DataRequest,
        source: str,
        confidence_weight: float
    ) -> MarketData:
        """Transform API response to MarketData format"""
        
        # Mock data transformation - in production, this would parse real API responses
        base_confidence = 0.85 * confidence_weight
        
        return MarketData(
            location=request.location,
            zip_code=request.zip_code,
            
            # Rental market data
            median_rent_per_sqm=raw_data.get('rental', {}).get('median_rent_sqm', 25.0),
            rental_vacancy_rate=raw_data.get('rental', {}).get('vacancy_rate', 5.2),
            rental_growth_rate=raw_data.get('rental', {}).get('growth_rate', 3.5),
            
            # Property market data
            median_property_price=raw_data.get('property', {}).get('median_price', 450000),
            property_appreciation_rate=raw_data.get('property', {}).get('appreciation_rate', 4.2),
            months_on_market=raw_data.get('property', {}).get('months_on_market', 2.1),
            
            # Interest rates
            current_mortgage_rates=raw_data.get('rates', {
                '30_year_fixed': 6.8,
                '15_year_fixed': 6.3,
                'jumbo_30': 7.1
            }),
            rate_trend=raw_data.get('rate_trend', 'stable'),
            
            # Economic indicators
            local_inflation_rate=raw_data.get('economic', {}).get('inflation', 3.2),
            unemployment_rate=raw_data.get('economic', {}).get('unemployment', 4.1),
            population_growth_rate=raw_data.get('economic', {}).get('population_growth', 1.5),
            
            # Metadata
            data_timestamp=datetime.now(),
            data_sources=[source],
            confidence_score=base_confidence,
            freshness_hours=0.0
        )
    
    async def _get_fallback_data(self, request: DataRequest, errors: List[str]) -> MarketData:
        """Get fallback data when all APIs fail"""
        logger.warning(f"Using fallback data for {request.location}. Errors: {errors}")
        
        # Try cache regardless of age
        if self.cache_manager:
            cached_data = self.cache_manager.get_cached_data(request.location)
            if cached_data:
                cached_data.confidence_score *= 0.5  # Reduce confidence for stale data
                return cached_data
        
        # Return default data with low confidence
        return MarketData(
            location=request.location,
            zip_code=request.zip_code,
            
            # Conservative fallback values
            median_rent_per_sqm=20.0,
            rental_vacancy_rate=6.0,
            rental_growth_rate=2.5,
            
            median_property_price=400000,
            property_appreciation_rate=3.0,
            months_on_market=3.0,
            
            current_mortgage_rates={'30_year_fixed': 7.0, '15_year_fixed': 6.5},
            rate_trend='unknown',
            
            local_inflation_rate=3.0,
            unemployment_rate=5.0,
            population_growth_rate=1.0,
            
            data_timestamp=datetime.now(),
            data_sources=['fallback'],
            confidence_score=0.3,
            freshness_hours=999999.0  # Very stale
        )
    
    def validate_data(self, data: MarketData) -> DataValidationResult:
        """Validate data quality and freshness"""
        issues = []
        recommendations = []
        quality_score = 1.0
        
        # Check data freshness
        if data.freshness_hours > 48:
            issues.append("Data is more than 48 hours old")
            quality_score *= 0.8
            
        # Check confidence score
        if data.confidence_score < 0.5:
            issues.append("Low confidence data source")
            recommendations.append("Consider using multiple data sources")
            quality_score *= 0.7
            
        # Validate data ranges
        if data.median_rent_per_sqm <= 0:
            issues.append("Invalid rental price data")
            quality_score *= 0.6
            
        if data.median_property_price <= 0:
            issues.append("Invalid property price data")
            quality_score *= 0.6
            
        # Check for fallback data
        fallback_used = 'fallback' in data.data_sources or 'international_guidance' in data.data_sources
        
        if fallback_used:
            recommendations.append("API integration failed, using fallback data")
            quality_score *= 0.5
        
        is_valid = quality_score > 0.3 and len(issues) < 3
        
        return DataValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            issues=issues,
            recommendations=recommendations,
            fallback_data_used=fallback_used
        )
    
    def get_cached_data(self, location: str) -> Optional[MarketData]:
        """Retrieve cached data if available"""
        if self.cache_manager:
            return self.cache_manager.get_cached_data(location)
        return None
    
    def update_cache(self, location: str, data: MarketData) -> None:
        """Update cached data"""
        if self.cache_manager:
            self.cache_manager.update_cache(location, data)
    
    def _create_sync_fallback_data(self, request: DataRequest) -> MarketData:
        """Create minimal fallback data synchronously"""
        return MarketData(
            location=request.location,
            zip_code=request.zip_code,
            median_rent_per_sqm=25.0,
            rental_vacancy_rate=6.0,
            rental_growth_rate=2.5,
            median_property_price=400000.0,
            property_appreciation_rate=3.0,
            months_on_market=3.0,
            current_mortgage_rates={'30_year_fixed': 7.0, '15_year_fixed': 6.5},
            rate_trend='unknown',
            local_inflation_rate=3.0,
            unemployment_rate=5.0,
            population_growth_rate=1.0,
            data_timestamp=datetime.now(),
            data_sources=['sync_fallback'],
            confidence_score=0.3,
            freshness_hours=0.0
        )
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.session and not self.session.closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except Exception:
                pass  # Ignore cleanup errors


def create_market_data_api(config: Optional[Dict] = None) -> MarketDataAPI:
    """Factory function to create MarketDataAPI instance"""
    return MarketDataAPI(config)