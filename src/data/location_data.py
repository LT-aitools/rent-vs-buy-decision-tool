"""
Location-based Market Data Integration
Handles geocoding, location validation, and region-specific market intelligence
"""

import aiohttp
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging
import json
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LocationInfo:
    """Standardized location information"""
    address: str
    city: str
    state: str
    zip_code: Optional[str]
    county: Optional[str]
    country: str
    latitude: float
    longitude: float
    is_us_location: bool
    metro_area: Optional[str]
    confidence_score: float


@dataclass
class MarketMetrics:
    """Location-specific market metrics"""
    location_info: LocationInfo
    
    # Market characteristics
    market_type: str  # "urban", "suburban", "rural"
    population: Optional[int]
    median_income: Optional[float]
    cost_of_living_index: Optional[float]
    
    # Real estate market indicators
    market_competitiveness: str  # "buyers", "sellers", "balanced"
    inventory_months: float
    price_per_sqft_trend: str  # "rising", "falling", "stable"
    
    # Economic indicators
    job_growth_rate: Optional[float]
    major_employers: List[str]
    transportation_score: Optional[float]
    
    # Quality metrics
    data_timestamp: datetime
    sources: List[str]
    confidence_score: float


class LocationDataService:
    """
    Service for location intelligence and market analysis
    Integrates with geocoding and demographic data services
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.timeout = self.config.get('timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        
        # API configuration
        self.google_api_key = self.config.get('google_maps_api_key')
        self.census_api_key = self.config.get('census_api_key')
        self.mapbox_api_key = self.config.get('mapbox_api_key')
        
        # Service endpoints
        self.endpoints = {
            'google_geocoding': {
                'url': 'https://maps.googleapis.com/maps/api/geocode/json',
                'key_param': 'key'
            },
            'census_acs': {
                'url': 'https://api.census.gov/data/2022/acs/acs5',
                'key_param': 'key'
            },
            'mapbox_geocoding': {
                'url': 'https://api.mapbox.com/geocoding/v5/mapbox.places',
                'key_param': 'access_token'
            }
        }
        
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Location cache
        self.location_cache = {}
        self.market_cache = {}
        
        # US state/territory mappings
        self.us_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS',
            'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY',
            'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
            'DC', 'PR', 'VI', 'GU', 'AS', 'MP'
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create async HTTP session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def geocode_location(self, address: str) -> LocationInfo:
        """
        Convert address to standardized location information with coordinates
        
        Args:
            address: Address string to geocode
            
        Returns:
            LocationInfo with coordinates and standardized address components
        """
        logger.info(f"Geocoding address: {address}")
        
        # Check cache first
        cache_key = address.lower().strip()
        if cache_key in self.location_cache:
            return self.location_cache[cache_key]
        
        # Try multiple geocoding services
        location_info = None
        
        # Try Google Maps first
        if self.google_api_key:
            try:
                location_info = await self._geocode_with_google(address)
            except Exception as e:
                logger.warning(f"Google geocoding failed: {e}")
        
        # Fall back to Mapbox
        if not location_info and self.mapbox_api_key:
            try:
                location_info = await self._geocode_with_mapbox(address)
            except Exception as e:
                logger.warning(f"Mapbox geocoding failed: {e}")
        
        # Final fallback to simple parsing
        if not location_info:
            location_info = self._parse_address_simple(address)
        
        # Cache the result
        self.location_cache[cache_key] = location_info
        
        return location_info
    
    async def _geocode_with_google(self, address: str) -> LocationInfo:
        """Geocode using Google Maps API"""
        session = await self._get_session()
        
        params = {
            'address': address,
            'key': self.google_api_key,
            'components': 'country:US'  # Bias towards US locations
        }
        
        url = self.endpoints['google_geocoding']['url']
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                
                if data['status'] == 'OK' and data['results']:
                    result = data['results'][0]
                    return self._parse_google_result(result, address)
        
        raise Exception("Google geocoding failed")
    
    async def _geocode_with_mapbox(self, address: str) -> LocationInfo:
        """Geocode using Mapbox API"""
        session = await self._get_session()
        
        encoded_address = address.replace(' ', '%20')
        url = f"{self.endpoints['mapbox_geocoding']['url']}/{encoded_address}.json"
        
        params = {
            'access_token': self.mapbox_api_key,
            'country': 'US',
            'types': 'address,postcode,district,place,region'
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                
                if data['features']:
                    feature = data['features'][0]
                    return self._parse_mapbox_result(feature, address)
        
        raise Exception("Mapbox geocoding failed")
    
    def _parse_google_result(self, result: Dict, original_address: str) -> LocationInfo:
        """Parse Google Maps geocoding result"""
        components = {comp['types'][0]: comp for comp in result['address_components']}
        
        city = components.get('locality', {}).get('long_name', '')
        if not city:
            city = components.get('administrative_area_level_3', {}).get('long_name', '')
        
        state = components.get('administrative_area_level_1', {}).get('short_name', '')
        zip_code = components.get('postal_code', {}).get('long_name')
        county = components.get('administrative_area_level_2', {}).get('long_name', '').replace(' County', '')
        country = components.get('country', {}).get('short_name', 'US')
        
        location = result['geometry']['location']
        
        return LocationInfo(
            address=result['formatted_address'],
            city=city,
            state=state,
            zip_code=zip_code,
            county=county,
            country=country,
            latitude=location['lat'],
            longitude=location['lng'],
            is_us_location=country == 'US',
            metro_area=self._determine_metro_area(city, state),
            confidence_score=0.9
        )
    
    def _parse_mapbox_result(self, feature: Dict, original_address: str) -> LocationInfo:
        """Parse Mapbox geocoding result"""
        properties = feature.get('properties', {})
        context = {item['id']: item for item in feature.get('context', [])}
        
        # Extract address components
        address = feature.get('place_name', original_address)
        coordinates = feature['geometry']['coordinates']  # [lng, lat]
        
        # Parse location components
        city = properties.get('locality', '')
        state = context.get('region', {}).get('short_code', '').split('-')[-1] if 'region' in context else ''
        zip_code = context.get('postcode', {}).get('text')
        country = context.get('country', {}).get('short_code', 'US')
        
        return LocationInfo(
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            county=None,
            country=country,
            latitude=coordinates[1],
            longitude=coordinates[0],
            is_us_location=country == 'US',
            metro_area=self._determine_metro_area(city, state),
            confidence_score=0.8
        )
    
    def _parse_address_simple(self, address: str) -> LocationInfo:
        """Simple address parsing as fallback"""
        logger.warning(f"Using simple address parsing for: {address}")
        
        # Basic parsing patterns
        zip_pattern = r'\b\d{5}(-\d{4})?\b'
        state_pattern = r'\b([A-Z]{2})\b'
        
        zip_match = re.search(zip_pattern, address)
        state_match = re.search(state_pattern, address)
        
        zip_code = zip_match.group(0) if zip_match else None
        state = state_match.group(1) if state_match and state_match.group(1) in self.us_states else ''
        
        # Extract city (rough approximation)
        parts = address.split(',')
        city = parts[0].strip() if len(parts) > 1 else ''
        
        return LocationInfo(
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            county=None,
            country='US',
            latitude=40.7128,  # Default to NYC coordinates
            longitude=-74.0060,
            is_us_location=True,
            metro_area=None,
            confidence_score=0.3
        )
    
    def _determine_metro_area(self, city: str, state: str) -> Optional[str]:
        """Determine metro area from city and state"""
        metro_areas = {
            ('New York', 'NY'): 'New York-Newark-Jersey City',
            ('Los Angeles', 'CA'): 'Los Angeles-Long Beach-Anaheim',
            ('Chicago', 'IL'): 'Chicago-Naperville-Elgin',
            ('Dallas', 'TX'): 'Dallas-Fort Worth-Arlington',
            ('Houston', 'TX'): 'Houston-The Woodlands-Sugar Land',
            ('Washington', 'DC'): 'Washington-Arlington-Alexandria',
            ('Miami', 'FL'): 'Miami-Fort Lauderdale-West Palm Beach',
            ('Philadelphia', 'PA'): 'Philadelphia-Camden-Wilmington',
            ('Atlanta', 'GA'): 'Atlanta-Sandy Springs-Roswell',
            ('Boston', 'MA'): 'Boston-Cambridge-Newton',
            ('Phoenix', 'AZ'): 'Phoenix-Mesa-Scottsdale',
            ('San Francisco', 'CA'): 'San Francisco-Oakland-Hayward',
            ('Riverside', 'CA'): 'Riverside-San Bernardino-Ontario',
            ('Detroit', 'MI'): 'Detroit-Warren-Dearborn',
            ('Seattle', 'WA'): 'Seattle-Tacoma-Bellevue',
            ('Minneapolis', 'MN'): 'Minneapolis-St. Paul-Bloomington',
            ('San Diego', 'CA'): 'San Diego-Carlsbad',
            ('Tampa', 'FL'): 'Tampa-St. Petersburg-Clearwater',
            ('Denver', 'CO'): 'Denver-Aurora-Lakewood',
            ('Baltimore', 'MD'): 'Baltimore-Columbia-Towson'
        }
        
        return metro_areas.get((city, state))
    
    async def get_market_metrics(self, location_info: LocationInfo) -> MarketMetrics:
        """
        Get comprehensive market metrics for a location
        
        Args:
            location_info: Standardized location information
            
        Returns:
            MarketMetrics with demographic and economic data
        """
        logger.info(f"Fetching market metrics for {location_info.city}, {location_info.state}")
        
        # Check cache
        cache_key = f"{location_info.city}_{location_info.state}_{location_info.zip_code}"
        if cache_key in self.market_cache:
            cached_data = self.market_cache[cache_key]
            if (datetime.now() - cached_data.data_timestamp).total_seconds() < 86400:  # 24 hours
                return cached_data
        
        # Gather market data from multiple sources
        try:
            demographic_data = await self._get_demographic_data(location_info)
            economic_data = await self._get_economic_indicators(location_info)
            real_estate_data = await self._get_real_estate_indicators(location_info)
            
        except Exception as e:
            logger.warning(f"Failed to fetch market metrics: {e}")
            # Return basic metrics with fallback data
            demographic_data = self._get_fallback_demographics()
            economic_data = self._get_fallback_economics()
            real_estate_data = self._get_fallback_real_estate()
        
        # Combine all data
        market_metrics = MarketMetrics(
            location_info=location_info,
            
            # Market characteristics
            market_type=self._classify_market_type(location_info, demographic_data),
            population=demographic_data.get('population'),
            median_income=demographic_data.get('median_income'),
            cost_of_living_index=economic_data.get('cost_of_living_index'),
            
            # Real estate indicators
            market_competitiveness=real_estate_data.get('market_balance', 'balanced'),
            inventory_months=real_estate_data.get('inventory_months', 3.5),
            price_per_sqft_trend=real_estate_data.get('price_trend', 'stable'),
            
            # Economic indicators
            job_growth_rate=economic_data.get('job_growth_rate'),
            major_employers=economic_data.get('major_employers', []),
            transportation_score=economic_data.get('transportation_score'),
            
            # Quality metrics
            data_timestamp=datetime.now(),
            sources=['census', 'bls', 'market_apis'],
            confidence_score=location_info.confidence_score * 0.8
        )
        
        # Cache the result
        self.market_cache[cache_key] = market_metrics
        
        return market_metrics
    
    async def _get_demographic_data(self, location_info: LocationInfo) -> Dict[str, Any]:
        """Fetch demographic data from Census API"""
        if not self.census_api_key or not location_info.is_us_location:
            return self._get_fallback_demographics()
        
        # Mock implementation - in production would call Census API
        return {
            'population': 150000,
            'median_income': 65000,
            'age_median': 36.5,
            'education_college_pct': 45.2
        }
    
    async def _get_economic_indicators(self, location_info: LocationInfo) -> Dict[str, Any]:
        """Fetch economic indicators"""
        # Mock implementation
        return {
            'cost_of_living_index': 105.2,
            'job_growth_rate': 2.1,
            'major_employers': ['TechCorp', 'Regional Hospital', 'State University'],
            'transportation_score': 7.2,
            'unemployment_rate': 4.2
        }
    
    async def _get_real_estate_indicators(self, location_info: LocationInfo) -> Dict[str, Any]:
        """Fetch real estate market indicators"""
        # Mock implementation
        return {
            'market_balance': 'sellers',
            'inventory_months': 2.1,
            'price_trend': 'rising',
            'days_on_market': 25,
            'sale_to_list_ratio': 1.02
        }
    
    def _get_fallback_demographics(self) -> Dict[str, Any]:
        """Fallback demographic data"""
        return {
            'population': None,
            'median_income': None,
            'age_median': None,
            'education_college_pct': None
        }
    
    def _get_fallback_economics(self) -> Dict[str, Any]:
        """Fallback economic data"""
        return {
            'cost_of_living_index': None,
            'job_growth_rate': None,
            'major_employers': [],
            'transportation_score': None,
            'unemployment_rate': None
        }
    
    def _get_fallback_real_estate(self) -> Dict[str, Any]:
        """Fallback real estate data"""
        return {
            'market_balance': 'balanced',
            'inventory_months': 4.0,
            'price_trend': 'stable',
            'days_on_market': 30,
            'sale_to_list_ratio': 1.0
        }
    
    def _classify_market_type(self, location_info: LocationInfo, demographic_data: Dict) -> str:
        """Classify market as urban, suburban, or rural"""
        population = demographic_data.get('population', 0)
        
        if population > 500000:
            return 'urban'
        elif population > 50000:
            return 'suburban'
        else:
            return 'rural'
    
    async def validate_location(self, address: str) -> Tuple[bool, str, Optional[LocationInfo]]:
        """
        Validate and standardize a location
        
        Returns:
            Tuple of (is_valid, message, location_info)
        """
        try:
            location_info = await self.geocode_location(address)
            
            if location_info.confidence_score < 0.5:
                return False, "Location could not be reliably geocoded", location_info
            
            if not location_info.is_us_location:
                return True, "International location - limited data available", location_info
            
            return True, "Location validated successfully", location_info
            
        except Exception as e:
            logger.error(f"Location validation failed: {e}")
            return False, f"Location validation error: {str(e)}", None
    
    async def get_comparable_locations(
        self, 
        location_info: LocationInfo, 
        radius_miles: float = 25
    ) -> List[LocationInfo]:
        """
        Find comparable locations within specified radius
        
        Args:
            location_info: Base location
            radius_miles: Search radius in miles
            
        Returns:
            List of comparable locations
        """
        # Mock implementation - in production would use spatial queries
        logger.info(f"Finding comparable locations within {radius_miles} miles of {location_info.city}")
        
        # Return mock comparable locations
        comparables = []
        base_lat, base_lng = location_info.latitude, location_info.longitude
        
        # Generate some mock nearby locations
        offsets = [(0.1, 0.1), (-0.1, 0.1), (0.1, -0.1), (-0.1, -0.1)]
        
        for i, (lat_offset, lng_offset) in enumerate(offsets):
            comparable = LocationInfo(
                address=f"Comparable Location {i+1}",
                city=f"Nearby City {i+1}",
                state=location_info.state,
                zip_code=f"{location_info.zip_code[:-1] if location_info.zip_code else '1234'}{i}",
                county=location_info.county,
                country=location_info.country,
                latitude=base_lat + lat_offset,
                longitude=base_lng + lng_offset,
                is_us_location=location_info.is_us_location,
                metro_area=location_info.metro_area,
                confidence_score=0.7
            )
            comparables.append(comparable)
        
        return comparables
    
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
                pass


def create_location_data_service(config: Optional[Dict] = None) -> LocationDataService:
    """Factory function to create LocationDataService instance"""
    return LocationDataService(config)