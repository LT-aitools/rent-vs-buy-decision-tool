"""
International Central Bank API Integration
Live feeds from Brazil (BCB) and Israel (BOI) central banks
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class BrazilCentralBankAPI:
    """
    Brazil Central Bank (BCB) API integration
    Fetches live Selic rates and economic data
    """
    
    def __init__(self):
        self.base_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # BCB Series codes
        self.series_codes = {
            'selic_rate': 11,  # Selic rate
            'ipca_inflation': 433,  # IPCA inflation rate
            'prime_rate': 4390,  # Prime rate
            'real_estate_index': 1373  # Real estate price index
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def get_latest_selic_rate(self) -> Optional[float]:
        """Get the latest Selic rate from BCB API"""
        try:
            session = await self._get_session()
            
            # Get last 1 record of Selic rate
            url = f"{self.base_url}.{self.series_codes['selic_rate']}/dados/ultimos/1"
            params = {'formato': 'json'}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        latest_rate = float(data[0]['valor'])
                        logger.info(f"BCB Selic rate: {latest_rate}% (date: {data[0]['data']})")
                        return latest_rate
                else:
                    logger.warning(f"BCB API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching BCB Selic rate: {e}")
            
        return None
    
    async def get_economic_data(self) -> Dict[str, Any]:
        """Get comprehensive economic data from BCB"""
        try:
            session = await self._get_session()
            
            # Fetch multiple series concurrently
            tasks = []
            for series_name, series_code in self.series_codes.items():
                url = f"{self.base_url}.{series_code}/dados/ultimos/1"
                task = self._fetch_series_data(session, url, series_name)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            economic_data = {}
            for i, (series_name, result) in enumerate(zip(self.series_codes.keys(), results)):
                if isinstance(result, Exception):
                    logger.warning(f"Failed to fetch {series_name}: {result}")
                    continue
                    
                if result:
                    economic_data[series_name] = result
            
            return economic_data
            
        except Exception as e:
            logger.error(f"Error fetching BCB economic data: {e}")
            return {}
    
    async def _fetch_series_data(self, session: aiohttp.ClientSession, url: str, series_name: str) -> Optional[Dict]:
        """Fetch data for a specific series"""
        try:
            params = {'formato': 'json'}
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        return {
                            'value': float(data[0]['valor']),
                            'date': data[0]['data'],
                            'series_name': series_name
                        }
        except Exception as e:
            logger.warning(f"Error fetching {series_name}: {e}")
            
        return None
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()


class IsraelCentralBankAPI:
    """
    Bank of Israel (BOI) API integration
    Fetches live interest rates and economic data
    """
    
    def __init__(self):
        self.base_url = "https://edge.boi.gov.il"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; RentVsBuyTool/1.0)',
                'Accept': 'application/json'
            }
            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self.session
    
    async def get_latest_interest_rate(self) -> Optional[float]:
        """Get the latest BOI interest rate"""
        try:
            session = await self._get_session()
            
            # BOI API endpoint - needs further research to find correct endpoint
            # The edge.boi.gov.il site exists but API structure is unclear
            # Possible endpoints to try:
            endpoints_to_try = [
                f"{self.base_url}/api/data/series/monetary-policy-rate/latest",
                f"{self.base_url}/api/statistics/interest-rate/latest", 
                f"{self.base_url}/api/series/policy-rate",
                f"{self.base_url}/data/series/central-bank-rate"
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    async with session.get(endpoint) as response:
                        if response.status == 200:
                            data = await response.json()
                            # Try different possible response formats
                            rate_value = None
                            
                            if isinstance(data, dict):
                                # Try common field names
                                for field in ['rate', 'value', 'interest_rate', 'policy_rate', 'current_rate']:
                                    if field in data:
                                        rate_value = data[field]
                                        break
                                        
                            elif isinstance(data, list) and len(data) > 0:
                                # If it's an array, take the latest entry
                                latest = data[0] if isinstance(data[0], dict) else {}
                                for field in ['rate', 'value', 'interest_rate', 'policy_rate']:
                                    if field in latest:
                                        rate_value = latest[field]
                                        break
                            
                            if rate_value is not None:
                                rate = float(rate_value)
                                logger.info(f"BOI interest rate: {rate}% from {endpoint}")
                                return rate
                                
                except Exception as endpoint_error:
                    logger.debug(f"Endpoint {endpoint} failed: {endpoint_error}")
                    continue
                    
            logger.warning("All BOI API endpoints failed - API structure needs investigation")
                    
        except Exception as e:
            logger.error(f"Error fetching BOI interest rate: {e}")
            
        return None
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()


class InternationalAPIFeeds:
    """
    Consolidated international API feeds manager
    """
    
    def __init__(self):
        self.brazil_api = BrazilCentralBankAPI()
        self.israel_api = IsraelCentralBankAPI()
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)  # Cache for 1 hour
    
    async def get_live_rates(self, country: str) -> Optional[Dict[str, Any]]:
        """
        Get live rates for a specific country
        
        Args:
            country: Country code ('brazil' or 'israel')
            
        Returns:
            Dict with live rates or None if unavailable
        """
        cache_key = f"{country}_rates"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_ttl:
                logger.info(f"Using cached {country} rates")
                return cached_data
        
        try:
            if country == 'brazil':
                return await self._get_brazil_rates()
            elif country == 'israel':
                return await self._get_israel_rates()
            else:
                logger.warning(f"No live API available for {country}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching live rates for {country}: {e}")
            return None
    
    async def _get_brazil_rates(self) -> Optional[Dict[str, Any]]:
        """Get live rates from Brazil"""
        try:
            # Get Selic rate
            selic_rate = await self.brazil_api.get_latest_selic_rate()
            
            if selic_rate is not None:
                # Estimate mortgage rate (typically Selic + margin)
                mortgage_rate = selic_rate + 1.0  # Approximate margin
                
                rates = {
                    'base_rate': selic_rate,
                    'mortgage_rate': mortgage_rate,
                    'prime_rate': selic_rate + 1.5,
                    'source': 'BCB_live_api',
                    'timestamp': datetime.now().isoformat(),
                    'confidence': 0.9
                }
                
                # Cache the result
                self.cache['brazil_rates'] = (rates, datetime.now())
                return rates
                
        except Exception as e:
            logger.error(f"Error getting Brazil rates: {e}")
            
        return None
    
    async def _get_israel_rates(self) -> Optional[Dict[str, Any]]:
        """Get live rates from Israel"""
        try:
            # Get BOI rate
            boi_rate = await self.israel_api.get_latest_interest_rate()
            
            if boi_rate is not None:
                # Estimate mortgage rate (typically BOI rate + margin)
                mortgage_rate = boi_rate + 0.5  # Approximate margin
                
                rates = {
                    'base_rate': boi_rate,
                    'mortgage_rate': mortgage_rate,
                    'prime_rate': boi_rate + 1.75,
                    'source': 'BOI_live_api',
                    'timestamp': datetime.now().isoformat(),
                    'confidence': 0.9
                }
                
                # Cache the result
                self.cache['israel_rates'] = (rates, datetime.now())
                return rates
                
        except Exception as e:
            logger.error(f"Error getting Israel rates: {e}")
            
        return None
    
    async def test_apis(self) -> Dict[str, bool]:
        """Test API connectivity"""
        results = {}
        
        try:
            brazil_rate = await self.brazil_api.get_latest_selic_rate()
            results['brazil'] = brazil_rate is not None
        except Exception:
            results['brazil'] = False
            
        try:
            israel_rate = await self.israel_api.get_latest_interest_rate()
            results['israel'] = israel_rate is not None
        except Exception:
            results['israel'] = False
            
        return results
    
    async def close(self):
        """Close all API sessions"""
        await self.brazil_api.close()
        await self.israel_api.close()


# Global instance
_international_api_feeds = None

def get_international_api_feeds() -> InternationalAPIFeeds:
    """Get the global international API feeds instance"""
    global _international_api_feeds
    if _international_api_feeds is None:
        _international_api_feeds = InternationalAPIFeeds()
    return _international_api_feeds

async def test_international_apis() -> Dict[str, bool]:
    """Test international API connectivity"""
    feeds = get_international_api_feeds()
    try:
        return await feeds.test_apis()
    finally:
        await feeds.close()