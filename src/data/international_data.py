"""
International Market Data Handler
Provides country-specific financial data and market estimates
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import re
import asyncio

logger = logging.getLogger(__name__)


class InternationalDataProvider:
    """
    Provides international market data and financial parameters
    """
    
    def __init__(self):
        self.country_data = self._initialize_country_data()
        self.live_api_enabled = True  # Enable live API feeds
        self._api_feeds = None  # Lazy loaded
        
    def _initialize_country_data(self) -> Dict[str, Dict[str, Any]]:
        """Initialize country-specific financial data"""
        return {
            # Major English-speaking markets
            'uk': {
                'name': 'United Kingdom',
                'currency': 'GBP',
                'interest_rates': {
                    'base_rate': 5.25,  # Bank of England base rate
                    'mortgage_rate': 5.8,
                    'prime_rate': 6.0
                },
                'market_data': {
                    'property_appreciation_rate': 2.8,
                    'rent_increase_rate': 4.5,
                    'inflation_rate': 3.9,
                    'property_tax_rate': 0.0,  # No property tax, but council tax exists
                    'stamp_duty_rate': 3.0,  # UK equivalent
                },
                'tax_data': {
                    'corporate_tax_rate': 25.0,  # UK Corporation Tax main rate
                    'source': 'HMRC_2024',
                    'notes': 'Main rate for companies with profits over £250,000. Small profits rate is 19%.'
                },
                'confidence': 0.85,
                'source': 'BOE_ONS_data',
                'data_date': '2024-08-14',
                'api_available': False
            },
            'canada': {
                'name': 'Canada',
                'currency': 'CAD',
                'interest_rates': {
                    'base_rate': 5.0,  # Bank of Canada rate
                    'mortgage_rate': 5.8,
                    'prime_rate': 7.2
                },
                'market_data': {
                    'property_appreciation_rate': 3.2,
                    'rent_increase_rate': 3.8,
                    'inflation_rate': 3.4,
                    'property_tax_rate': 1.1,  # Average across provinces
                },
                'tax_data': {
                    'corporate_tax_rate': 26.7,  # Combined federal (15%) + average provincial (11.7%)
                    'source': 'CRA_PwC_2024',
                    'notes': 'Combined federal and provincial rates. Varies by province (Ontario: 26.5%, BC: 27%, Quebec: 26.5%).'
                },
                'confidence': 0.8,
                'source': 'BOC_StatsCan_data',
                'data_date': '2024-08-14',
                'api_available': False
            },
            'australia': {
                'name': 'Australia',
                'currency': 'AUD',
                'interest_rates': {
                    'base_rate': 4.35,  # RBA cash rate
                    'mortgage_rate': 5.2,
                    'prime_rate': 5.5
                },
                'market_data': {
                    'property_appreciation_rate': 4.1,
                    'rent_increase_rate': 4.8,
                    'inflation_rate': 4.1,
                    'property_tax_rate': 0.7,  # Land tax varies by state
                },
                'tax_data': {
                    'corporate_tax_rate': 30.0,  # Federal 30% for companies
                    'source': 'ATO_2024',
                    'notes': 'Standard company tax rate. Small business rate is 25% for eligible companies.'
                },
                'confidence': 0.8,
                'source': 'RBA_ABS_data',
                'data_date': '2024-08-14',
                'api_available': False
            },
            'germany': {
                'name': 'Germany',
                'currency': 'EUR',
                'interest_rates': {
                    'base_rate': 4.5,  # ECB rate
                    'mortgage_rate': 3.8,
                    'prime_rate': 4.2
                },
                'market_data': {
                    'property_appreciation_rate': 2.1,
                    'rent_increase_rate': 2.8,
                    'inflation_rate': 3.2,
                    'property_tax_rate': 0.35,  # Grundsteuer
                },
                'tax_data': {
                    'corporate_tax_rate': 29.9,  # Combined federal + solidarity surcharge + trade tax
                    'source': 'BMF_OECD_2024',
                    'notes': 'Includes corporate income tax (15%), solidarity surcharge (5.5%), and average trade tax (14.4%).'
                },
                'confidence': 0.75,
                'source': 'ECB_Destatis_data',
                'data_date': '2024-08-14',
                'api_available': False
            },
            'france': {
                'name': 'France',
                'currency': 'EUR',
                'interest_rates': {
                    'base_rate': 4.5,  # ECB rate
                    'mortgage_rate': 3.9,
                    'prime_rate': 4.3
                },
                'market_data': {
                    'property_appreciation_rate': 2.3,
                    'rent_increase_rate': 2.5,
                    'inflation_rate': 3.1,
                    'property_tax_rate': 1.2,  # Taxe foncière
                },
                'tax_data': {
                    'corporate_tax_rate': 25.8,  # Standard corporate income tax rate
                    'source': 'DGFiP_2024',
                    'notes': 'Standard rate. Reduced rate of 15% applies to SMEs on profits up to €42,500.'
                },
                'confidence': 0.75,
                'source': 'ECB_INSEE_data',
                'data_date': '2024-08-14',
                'api_available': False
            },
            'netherlands': {
                'name': 'Netherlands',
                'currency': 'EUR',
                'interest_rates': {
                    'base_rate': 4.5,  # ECB rate
                    'mortgage_rate': 4.1,
                    'prime_rate': 4.4
                },
                'market_data': {
                    'property_appreciation_rate': 3.8,
                    'rent_increase_rate': 3.2,
                    'inflation_rate': 2.8,
                    'property_tax_rate': 0.0,  # No property tax, but OZB exists
                },
                'tax_data': {
                    'corporate_tax_rate': 25.8,  # Standard corporate income tax rate
                    'source': 'Belastingdienst_2024',
                    'notes': 'Rate of 25.8% on profits above €200,000. Rate of 19% on profits up to €200,000.'
                },
                'confidence': 0.75,
                'source': 'ECB_CBS_data',
                'data_date': '2024-08-14',
                'api_available': False
            },
            'japan': {
                'name': 'Japan',
                'currency': 'JPY',
                'interest_rates': {
                    'base_rate': 0.1,  # BOJ rate
                    'mortgage_rate': 1.3,
                    'prime_rate': 1.475
                },
                'market_data': {
                    'property_appreciation_rate': 0.8,
                    'rent_increase_rate': 0.5,
                    'inflation_rate': 2.6,
                    'property_tax_rate': 1.4,  # Fixed asset tax
                },
                'tax_data': {
                    'corporate_tax_rate': 29.7,  # Combined corporate tax rates
                    'source': 'NTA_METI_2024',
                    'notes': 'Combined national corporate tax (23.2%) and local inhabitants tax (varies by municipality).'
                },
                'confidence': 0.7,
                'source': 'BOJ_MLIT_data',
                'data_date': '2024-08-14',
                'api_available': False
            },
            'singapore': {
                'name': 'Singapore',
                'currency': 'SGD',
                'interest_rates': {
                    'base_rate': 3.5,  # MAS rate
                    'mortgage_rate': 4.2,
                    'prime_rate': 5.5
                },
                'market_data': {
                    'property_appreciation_rate': 2.8,
                    'rent_increase_rate': 3.5,
                    'inflation_rate': 2.4,
                    'property_tax_rate': 0.16,  # Based on annual value
                },
                'tax_data': {
                    'corporate_tax_rate': 17.0,  # Standard corporate income tax rate
                    'source': 'IRAS_2024',
                    'notes': 'Standard rate of 17%. Partial tax exemption available for qualifying companies.'
                },
                'confidence': 0.85,
                'source': 'MAS_URA_data',
                'data_date': '2024-08-14',
                'api_available': False
            },
            'brazil': {
                'name': 'Brazil',
                'currency': 'BRL',
                'interest_rates': {
                    'base_rate': 11.75,  # BCB Selic rate
                    'mortgage_rate': 12.5,
                    'prime_rate': 13.2
                },
                'market_data': {
                    'property_appreciation_rate': 5.8,
                    'rent_increase_rate': 7.2,
                    'inflation_rate': 4.8,
                    'property_tax_rate': 1.2,  # IPTU varies by municipality
                },
                'tax_data': {
                    'corporate_tax_rate': 34.0,  # Combined IRPJ + CSLL
                    'source': 'RFB_2024',
                    'notes': 'Combined Corporate Income Tax (IRPJ, 15%) and Social Contribution (CSLL, 9%) plus additional rates on higher profits.'
                },
                'confidence': 0.7,
                'source': 'BCB_IBGE_data',
                'data_date': '2024-08-14',  # Date when rates were sourced
                'api_available': True,  # BCB has API: https://api.bcb.gov.br
                'api_endpoint': 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados'
            },
            'poland': {
                'name': 'Poland',
                'currency': 'PLN',
                'interest_rates': {
                    'base_rate': 5.75,  # NBP rate
                    'mortgage_rate': 7.2,
                    'prime_rate': 7.8
                },
                'market_data': {
                    'property_appreciation_rate': 6.5,
                    'rent_increase_rate': 8.1,
                    'inflation_rate': 3.7,
                    'property_tax_rate': 0.8,  # Local property tax
                },
                'tax_data': {
                    'corporate_tax_rate': 19.0,  # Standard corporate income tax rate
                    'source': 'MF_Poland_2024',
                    'notes': 'Standard CIT rate of 19%. Reduced rate of 9% for small taxpayers.'
                },
                'confidence': 0.75,
                'source': 'NBP_GUS_data',
                'data_date': '2024-08-14',  # Date when rates were sourced
                'api_available': False  # No live API integration yet
            },
            'israel': {
                'name': 'Israel',
                'currency': 'ILS',
                'interest_rates': {
                    'base_rate': 4.75,  # BOI rate  
                    'mortgage_rate': 5.3,
                    'prime_rate': 6.5
                },
                'market_data': {
                    'property_appreciation_rate': 4.2,
                    'rent_increase_rate': 5.8,
                    'inflation_rate': 3.1,
                    'property_tax_rate': 0.6,  # Arnona (municipal tax)
                },
                'tax_data': {
                    'corporate_tax_rate': 23.0,  # Standard corporate tax rate
                    'source': 'ITA_Israel_2024',
                    'notes': 'Standard corporate tax rate of 23%. Reduced rates available for specific industries and zones.'
                },
                'confidence': 0.8,
                'source': 'BOI_CBS_data',
                'data_date': '2024-08-14',  # Date when rates were sourced  
                'api_available': True,  # BOI has API: edge.boi.gov.il
                'api_endpoint': 'https://edge.boi.gov.il'
            },
            'romania': {
                'name': 'Romania',
                'currency': 'RON',
                'interest_rates': {
                    'base_rate': 7.0,  # NBR policy rate
                    'mortgage_rate': 8.2,
                    'prime_rate': 8.5
                },
                'market_data': {
                    'property_appreciation_rate': 6.8,  # Strong property market growth
                    'rent_increase_rate': 7.5,         # High rental growth in major cities
                    'inflation_rate': 5.2,             # Current Romanian inflation
                    'property_tax_rate': 0.2,          # Local property tax (varies by city)
                },
                'tax_data': {
                    'corporate_tax_rate': 16.0,  # Standard corporate income tax rate
                    'source': 'ANAF_Romania_2024',
                    'notes': 'Standard rate of 16%. Reduced rates available for micro-enterprises and specific activities.'
                },
                'confidence': 0.75,
                'source': 'NBR_INS_data',
                'data_date': '2024-08-14',  # Date when rates were sourced
                'api_available': False,  # No live API integration yet
                'api_endpoint': None
            }
        }
    
    def parse_location(self, location: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Parse location string to extract city, state/region, country
        
        Args:
            location: Location string like "London, UK" or "Toronto, ON, Canada"
            
        Returns:
            Tuple of (city, state/region, country)
        """
        if not location:
            return None, None, None
            
        # Clean and split location
        location = location.strip()
        parts = [part.strip() for part in location.split(',')]
        
        city = parts[0] if parts else None
        
        # Country mapping
        country_aliases = {
            'uk': 'uk', 'united kingdom': 'uk', 'britain': 'uk', 'england': 'uk',
            'canada': 'canada', 'ca': 'canada',
            'australia': 'australia', 'au': 'australia', 'aus': 'australia',
            'germany': 'germany', 'de': 'germany', 'deutschland': 'germany',
            'france': 'france', 'fr': 'france', 'fra': 'france',
            'netherlands': 'netherlands', 'nl': 'netherlands', 'holland': 'netherlands',
            'japan': 'japan', 'jp': 'japan', 'jpn': 'japan',
            'singapore': 'singapore', 'sg': 'singapore', 'sgp': 'singapore',
            'brazil': 'brazil', 'br': 'brazil', 'brasil': 'brazil',
            'poland': 'poland', 'pl': 'poland', 'polska': 'poland',
            'israel': 'israel', 'il': 'israel', 'isr': 'israel',
            'georgia': 'georgia', 'ge': 'georgia',
            'armenia': 'armenia', 'am': 'armenia',
            'ukraine': 'ukraine', 'ua': 'ukraine',
            'romania': 'romania', 'ro': 'romania',
            'china': 'china', 'cn': 'china', 'prc': 'china',
            'usa': 'usa', 'us': 'usa', 'united states': 'usa', 'america': 'usa'
        }
        
        country = None
        state = None
        
        if len(parts) == 2:
            # Format: "City, Country" or "City, State"
            second_part = parts[1].lower()
            if second_part in country_aliases:
                country = country_aliases[second_part]
            else:
                # Might be a state (for US/Canada/Australia)
                state = parts[1]
                
        elif len(parts) == 3:
            # Format: "City, State, Country"
            state = parts[1]
            country_part = parts[2].lower()
            country = country_aliases.get(country_part)
            
        elif len(parts) == 1:
            # Just city name - try to infer country from major cities
            city_country_map = {
                'london': 'uk', 'manchester': 'uk', 'birmingham': 'uk', 'liverpool': 'uk',
                'toronto': 'canada', 'vancouver': 'canada', 'montreal': 'canada', 'calgary': 'canada',
                'sydney': 'australia', 'melbourne': 'australia', 'brisbane': 'australia', 'perth': 'australia',
                'berlin': 'germany', 'munich': 'germany', 'hamburg': 'germany', 'frankfurt': 'germany',
                'paris': 'france', 'lyon': 'france', 'marseille': 'france', 'toulouse': 'france',
                'amsterdam': 'netherlands', 'rotterdam': 'netherlands', 'the hague': 'netherlands',
                'tokyo': 'japan', 'osaka': 'japan', 'kyoto': 'japan', 'yokohama': 'japan',
                'singapore': 'singapore',
                'sao paulo': 'brazil', 'rio de janeiro': 'brazil', 'brasilia': 'brazil', 'salvador': 'brazil',
                'warsaw': 'poland', 'krakow': 'poland', 'gdansk': 'poland', 'wroclaw': 'poland',
                'tel aviv': 'israel', 'jerusalem': 'israel', 'haifa': 'israel', 'beersheba': 'israel'
            }
            country = city_country_map.get(city.lower())
            
        return city, state, country
    
    def get_country_data(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get country-specific financial data for a location
        
        Args:
            location: Location string
            
        Returns:
            Dict with country financial data or None if not found
        """
        city, state, country = self.parse_location(location)
        
        if country and country in self.country_data:
            data = self.country_data[country].copy()
            data['parsed_location'] = {
                'city': city,
                'state': state,
                'country': country
            }
            return data
            
        return None
    
    async def _get_api_feeds(self):
        """Lazy load international API feeds"""
        if self._api_feeds is None:
            try:
                from .international_api_feeds import get_international_api_feeds
                self._api_feeds = get_international_api_feeds()
            except ImportError:
                logger.warning("International API feeds not available")
                self._api_feeds = None
        return self._api_feeds
    
    async def get_live_rates(self, country: str) -> Optional[Dict[str, Any]]:
        """
        Get live interest rates from central bank APIs
        
        Args:
            country: Country code ('brazil', 'israel')
            
        Returns:
            Dict with live rates or None if unavailable
        """
        if not self.live_api_enabled:
            return None
            
        try:
            api_feeds = await self._get_api_feeds()
            if api_feeds is None:
                return None
                
            live_rates = await api_feeds.get_live_rates(country)
            if live_rates:
                logger.info(f"Retrieved live rates for {country}: {live_rates['mortgage_rate']}%")
                return live_rates
                
        except Exception as e:
            logger.error(f"Error fetching live rates for {country}: {e}")
            
        return None
    
    def get_international_estimates(self, location: str) -> Dict[str, Any]:
        """
        Get international estimates for a location
        
        Args:
            location: Location string or country code
            
        Returns:
            Dict with estimated financial parameters
        """
        # Check if location is a direct country code first
        if location.lower() in self.country_data:
            country_data = self.country_data[location.lower()]
        else:
            # Try parsing as a full location string
            country_data = self.get_country_data(location)
            if country_data is None:
                # If parsing failed, try as direct country lookup
                country_data = self.country_data.get(location.lower())
        
        if country_data:
            # Start with static data
            estimates = {
                'interest_rate': country_data['interest_rates']['mortgage_rate'],
                'market_appreciation_rate': country_data['market_data']['property_appreciation_rate'],
                'rent_increase_rate': country_data['market_data']['rent_increase_rate'],
                'property_tax_rate': country_data['market_data']['property_tax_rate'],
                'inflation_rate': country_data['market_data']['inflation_rate'],
                'corporate_tax_rate': country_data['tax_data']['corporate_tax_rate'],
            }
            
            metadata = {
                'country': country_data['name'],
                'currency': country_data['currency'],
                'confidence': country_data['confidence'],
                'source': country_data['source'],
                'data_date': country_data.get('data_date', '2024-08-14'),  # When rates were sourced
                'api_available': country_data.get('api_available', False),  # Whether live API exists
                'last_updated': datetime.now().isoformat(),
                'tax_info': {
                    'corporate_tax_source': country_data['tax_data']['source'],
                    'corporate_tax_notes': country_data['tax_data']['notes']
                }
            }
            
            return {'estimates': estimates, 'metadata': metadata}
        
        # Return None for unknown international locations
        return {'estimates': {}, 'metadata': {'country': 'Unknown', 'confidence': 0.0}}
    
    async def get_international_estimates_with_live_rates(self, location: str) -> Dict[str, Any]:
        """
        Get international estimates with live rates when available
        
        Args:
            location: Location string
            
        Returns:
            Dict with estimated financial parameters (live rates if available)
        """
        # Get base country data
        result = self.get_international_estimates(location)
        
        if not result['estimates']:
            return result
            
        # Try to get live rates for supported countries
        city, state, country = self.parse_location(location)
        
        if country in ['brazil', 'israel'] and self.live_api_enabled:
            try:
                live_rates = await self.get_live_rates(country)
                
                if live_rates and 'mortgage_rate' in live_rates:
                    # Update with live rate
                    old_rate = result['estimates']['interest_rate']
                    new_rate = live_rates['mortgage_rate']
                    
                    result['estimates']['interest_rate'] = new_rate
                    result['metadata']['source'] = f"{live_rates['source']}_live"
                    result['metadata']['confidence'] = live_rates['confidence']
                    result['metadata']['live_rate_used'] = True
                    result['metadata']['static_rate'] = old_rate
                    result['metadata']['rate_updated'] = live_rates['timestamp']
                    
                    logger.info(f"Updated {country} rate: {old_rate}% → {new_rate}% (live API)")
                else:
                    result['metadata']['live_rate_used'] = False
                    logger.info(f"Live rate not available for {country}, using static rate")
                    
            except Exception as e:
                logger.warning(f"Failed to get live rate for {country}: {e}")
                result['metadata']['live_rate_used'] = False
                result['metadata']['live_rate_error'] = str(e)
        else:
            result['metadata']['live_rate_used'] = False
            
        return result
    
    def is_supported_country(self, location: str) -> bool:
        """Check if we have data for this country"""
        _, _, country = self.parse_location(location)
        return country in self.country_data if country else False
    
    def get_supported_countries(self) -> List[str]:
        """Get list of supported countries"""
        return [data['name'] for data in self.country_data.values()]


# Global instance
_international_provider = None

def get_international_provider() -> InternationalDataProvider:
    """Get the global international data provider"""
    global _international_provider
    if _international_provider is None:
        _international_provider = InternationalDataProvider()
    return _international_provider