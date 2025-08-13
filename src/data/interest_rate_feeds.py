"""
Interest Rate Feeds Integration
Connects to Federal Reserve and other financial data sources for current interest rates
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
import xml.etree.ElementTree as ET
import json
import re

logger = logging.getLogger(__name__)


class InterestRateFeedError(Exception):
    """Custom exception for interest rate feed errors"""
    pass


class InterestRateFeeds:
    """
    Federal Reserve and financial institution interest rate integration
    Provides current mortgage rates with trend analysis
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.timeout = self.config.get('timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        
        # Federal Reserve Economic Data (FRED) API
        self.fred_api_key = self.config.get('fred_api_key')
        self.fred_base_url = 'https://api.stlouisfed.org/fred'
        
        # Additional rate sources
        self.rate_sources = {
            'fred': {
                'url': self.fred_base_url,
                'weight': 1.0,
                'series_ids': {
                    '30_year_fixed': 'MORTGAGE30US',
                    '15_year_fixed': 'MORTGAGE15US',
                    'federal_funds_rate': 'FEDFUNDS',
                    '10_year_treasury': 'GS10'
                }
            },
            'freddie_mac': {
                'url': 'http://www.freddiemac.com/pmms/pmms_archives.html',
                'weight': 0.9,
                'parser': 'html'
            },
            'bankrate': {
                'url': 'https://api.bankrate-mock.com/v1/rates',
                'weight': 0.7,
                'parser': 'json'
            }
        }
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache = {}
        self.cache_duration = timedelta(hours=1)  # Cache rates for 1 hour
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create async HTTP session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def get_current_rates(self, rate_types: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Get current interest rates from multiple sources
        
        Args:
            rate_types: List of rate types to fetch. If None, gets all available types.
                       Options: ['30_year_fixed', '15_year_fixed', 'jumbo_30', 'federal_funds_rate']
        
        Returns:
            Dictionary of rate_type -> current_rate
        """
        if rate_types is None:
            rate_types = ['30_year_fixed', '15_year_fixed', 'jumbo_30', 'federal_funds_rate']
        
        logger.info(f"Fetching current rates: {rate_types}")
        
        # Check cache first
        cached_rates = self._get_cached_rates(rate_types)
        if cached_rates:
            return cached_rates
        
        # Try multiple sources
        all_rates = {}
        source_weights = {}
        
        for source_name, source_config in self.rate_sources.items():
            try:
                rates = await self._fetch_from_source(source_name, source_config, rate_types)
                weight = source_config['weight']
                
                for rate_type, rate_value in rates.items():
                    if rate_type not in all_rates:
                        all_rates[rate_type] = []
                        source_weights[rate_type] = []
                    
                    all_rates[rate_type].append(rate_value)
                    source_weights[rate_type].append(weight)
                    
            except Exception as e:
                logger.warning(f"Failed to fetch rates from {source_name}: {e}")
                continue
        
        # Calculate weighted averages
        final_rates = {}
        for rate_type in rate_types:
            if rate_type in all_rates and all_rates[rate_type]:
                rates = all_rates[rate_type]
                weights = source_weights[rate_type]
                
                weighted_sum = sum(rate * weight for rate, weight in zip(rates, weights))
                weight_sum = sum(weights)
                
                if weight_sum > 0:
                    final_rates[rate_type] = round(weighted_sum / weight_sum, 3)
        
        # Add fallback rates for missing data
        final_rates = self._add_fallback_rates(final_rates, rate_types)
        
        # Cache the results
        self._cache_rates(final_rates)
        
        return final_rates
    
    async def _fetch_from_source(
        self, 
        source_name: str, 
        source_config: Dict, 
        rate_types: List[str]
    ) -> Dict[str, float]:
        """Fetch rates from a specific source"""
        
        if source_name == 'fred':
            return await self._fetch_from_fred(source_config, rate_types)
        elif source_name == 'freddie_mac':
            return await self._fetch_from_freddie_mac(source_config, rate_types)
        elif source_name == 'bankrate':
            return await self._fetch_from_bankrate(source_config, rate_types)
        else:
            raise InterestRateFeedError(f"Unknown source: {source_name}")
    
    async def _fetch_from_fred(self, config: Dict, rate_types: List[str]) -> Dict[str, float]:
        """Fetch rates from Federal Reserve Economic Data (FRED)"""
        if not self.fred_api_key:
            logger.warning("FRED API key not configured, using mock data")
            return self._get_mock_fred_data(rate_types)
        
        session = await self._get_session()
        rates = {}
        
        series_ids = config['series_ids']
        
        for rate_type in rate_types:
            if rate_type not in series_ids:
                continue
                
            series_id = series_ids[rate_type]
            
            params = {
                'series_id': series_id,
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'limit': 1,
                'sort_order': 'desc'
            }
            
            url = f"{config['url']}/series/observations"
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        observations = data.get('observations', [])
                        
                        if observations and observations[0].get('value') != '.':
                            rates[rate_type] = float(observations[0]['value'])
                            logger.info(f"Fetched {rate_type} from FRED: {rates[rate_type]}%")
                        
            except Exception as e:
                logger.warning(f"Error fetching {rate_type} from FRED: {e}")
                continue
        
        return rates
    
    async def _fetch_from_freddie_mac(self, config: Dict, rate_types: List[str]) -> Dict[str, float]:
        """Fetch rates from Freddie Mac (mock implementation)"""
        # In production, this would parse Freddie Mac's Primary Mortgage Market Survey
        logger.info("Fetching rates from Freddie Mac (mock)")
        
        mock_rates = {
            '30_year_fixed': 6.81,
            '15_year_fixed': 6.24
        }
        
        return {rate_type: rate for rate_type, rate in mock_rates.items() 
                if rate_type in rate_types}
    
    async def _fetch_from_bankrate(self, config: Dict, rate_types: List[str]) -> Dict[str, float]:
        """Fetch rates from Bankrate or similar service (mock implementation)"""
        logger.info("Fetching rates from Bankrate (mock)")
        
        mock_rates = {
            '30_year_fixed': 6.85,
            '15_year_fixed': 6.30,
            'jumbo_30': 7.15
        }
        
        return {rate_type: rate for rate_type, rate in mock_rates.items() 
                if rate_type in rate_types}
    
    def _get_mock_fred_data(self, rate_types: List[str]) -> Dict[str, float]:
        """Get mock FRED data when API key is not available"""
        mock_data = {
            '30_year_fixed': 6.78,
            '15_year_fixed': 6.21,
            'federal_funds_rate': 5.25,
            '10_year_treasury': 4.45
        }
        
        return {rate_type: rate for rate_type, rate in mock_data.items() 
                if rate_type in rate_types}
    
    def _add_fallback_rates(self, rates: Dict[str, float], requested_types: List[str]) -> Dict[str, float]:
        """Add fallback rates for missing data"""
        fallback_rates = {
            '30_year_fixed': 7.00,
            '15_year_fixed': 6.50,
            'jumbo_30': 7.25,
            'federal_funds_rate': 5.25,
            '10_year_treasury': 4.50
        }
        
        for rate_type in requested_types:
            if rate_type not in rates:
                rates[rate_type] = fallback_rates.get(rate_type, 7.00)
                logger.warning(f"Using fallback rate for {rate_type}: {rates[rate_type]}%")
        
        return rates
    
    async def get_rate_trend(self, rate_type: str = '30_year_fixed', days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze rate trend over specified period
        
        Args:
            rate_type: Type of rate to analyze
            days_back: Number of days to look back for trend analysis
        
        Returns:
            Dictionary with trend analysis including direction, magnitude, and forecast
        """
        logger.info(f"Analyzing trend for {rate_type} over {days_back} days")
        
        # In production, this would fetch historical data and perform real analysis
        # For now, return mock trend analysis
        current_rate = (await self.get_current_rates([rate_type]))[rate_type]
        
        # Mock historical data points (would be real API calls in production)
        historical_rates = [
            current_rate + 0.15,  # 30 days ago
            current_rate + 0.08,  # 20 days ago
            current_rate + 0.05,  # 10 days ago
            current_rate          # today
        ]
        
        # Calculate trend
        if len(historical_rates) < 2:
            trend_direction = "insufficient_data"
            trend_magnitude = 0.0
        else:
            rate_change = historical_rates[-1] - historical_rates[0]
            
            if abs(rate_change) < 0.05:
                trend_direction = "stable"
            elif rate_change > 0:
                trend_direction = "rising"
            else:
                trend_direction = "falling"
            
            trend_magnitude = abs(rate_change)
        
        # Simple forecast (would use more sophisticated models in production)
        if trend_direction == "rising":
            forecast = current_rate + 0.1
        elif trend_direction == "falling":
            forecast = current_rate - 0.1
        else:
            forecast = current_rate
        
        return {
            'rate_type': rate_type,
            'current_rate': current_rate,
            'trend_direction': trend_direction,
            'trend_magnitude': trend_magnitude,
            'days_analyzed': days_back,
            'historical_rates': historical_rates,
            'forecast_30_days': forecast,
            'confidence_level': 0.75,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _get_cached_rates(self, rate_types: List[str]) -> Optional[Dict[str, float]]:
        """Check if we have cached rates that are still fresh"""
        if not self.cache:
            return None
        
        cache_time = self.cache.get('timestamp')
        if not cache_time or datetime.now() - cache_time > self.cache_duration:
            return None
        
        cached_rates = self.cache.get('rates', {})
        
        # Check if all requested rates are in cache
        if all(rate_type in cached_rates for rate_type in rate_types):
            logger.info("Using cached interest rates")
            return {rate_type: cached_rates[rate_type] for rate_type in rate_types}
        
        return None
    
    def _cache_rates(self, rates: Dict[str, float]) -> None:
        """Cache the fetched rates"""
        self.cache = {
            'rates': rates,
            'timestamp': datetime.now()
        }
    
    async def get_lender_specific_rates(self, lender_types: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
        """
        Get rates from specific lender categories
        
        Args:
            lender_types: List of lender types ['banks', 'credit_unions', 'online_lenders']
        
        Returns:
            Dictionary of lender_type -> rates
        """
        if lender_types is None:
            lender_types = ['banks', 'credit_unions', 'online_lenders']
        
        # Mock implementation - in production would query lender APIs
        mock_lender_rates = {
            'banks': {
                '30_year_fixed': 6.85,
                '15_year_fixed': 6.32,
                'jumbo_30': 7.12
            },
            'credit_unions': {
                '30_year_fixed': 6.65,
                '15_year_fixed': 6.15,
                'jumbo_30': 6.95
            },
            'online_lenders': {
                '30_year_fixed': 6.75,
                '15_year_fixed': 6.28,
                'jumbo_30': 7.05
            }
        }
        
        return {lender_type: rates for lender_type, rates in mock_lender_rates.items() 
                if lender_type in lender_types}
    
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


class RateComparisonService:
    """Service for comparing and analyzing interest rates"""
    
    def __init__(self, rate_feeds: InterestRateFeeds):
        self.rate_feeds = rate_feeds
    
    async def compare_loan_options(
        self, 
        loan_amount: float,
        loan_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare different loan options based on current rates
        
        Args:
            loan_amount: Loan amount for calculations
            loan_types: Types of loans to compare
        
        Returns:
            Comparison analysis with monthly payments and total costs
        """
        if loan_types is None:
            loan_types = ['30_year_fixed', '15_year_fixed']
        
        current_rates = await self.rate_feeds.get_current_rates(loan_types)
        comparison = {}
        
        for loan_type in loan_types:
            if loan_type not in current_rates:
                continue
            
            rate = current_rates[loan_type] / 100  # Convert percentage to decimal
            
            # Calculate monthly payment (simplified)
            if '30_year' in loan_type:
                n_payments = 360
            elif '15_year' in loan_type:
                n_payments = 180
            else:
                n_payments = 360  # Default to 30 years
            
            monthly_rate = rate / 12
            monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate)**n_payments) / \
                            ((1 + monthly_rate)**n_payments - 1)
            
            total_cost = monthly_payment * n_payments
            total_interest = total_cost - loan_amount
            
            comparison[loan_type] = {
                'interest_rate': current_rates[loan_type],
                'monthly_payment': round(monthly_payment, 2),
                'total_cost': round(total_cost, 2),
                'total_interest': round(total_interest, 2),
                'term_years': n_payments // 12
            }
        
        return {
            'loan_amount': loan_amount,
            'comparisons': comparison,
            'analysis_date': datetime.now().isoformat(),
            'best_monthly_payment': min(comparison.values(), key=lambda x: x['monthly_payment']),
            'best_total_cost': min(comparison.values(), key=lambda x: x['total_cost'])
        }


def create_interest_rate_feeds(config: Optional[Dict] = None) -> InterestRateFeeds:
    """Factory function to create InterestRateFeeds instance"""
    return InterestRateFeeds(config)