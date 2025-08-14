"""
API Configuration for Real Estate Data Integration
Configures connections to various real estate and financial data APIs
"""

import os
from typing import Dict, Any, Optional

def get_api_config() -> Dict[str, Any]:
    """
    Get API configuration from environment variables and defaults
    
    Environment Variables:
    - FRED_API_KEY: Federal Reserve Economic Data API key (free from https://fred.stlouisfed.org/docs/api/api_key.html)
    - QUANDL_API_KEY: Quandl API key for additional financial data (optional)
    - ALPHA_VANTAGE_API_KEY: Alpha Vantage API key for market data (free from https://www.alphavantage.co/support/#api-key)
    """
    
    config = {
        # Federal Reserve Economic Data (FRED) - Free API
        'fred_api_key': os.getenv('FRED_API_KEY'),
        'fred_base_url': 'https://api.stlouisfed.org/fred',
        
        # Alpha Vantage for real estate and financial data - Free tier available
        'alpha_vantage_api_key': os.getenv('ALPHA_VANTAGE_API_KEY'),
        'alpha_vantage_base_url': 'https://www.alphavantage.co/query',
        
        # US Bureau of Labor Statistics (BLS) - Free, no key required
        'bls_base_url': 'https://api.bls.gov/publicAPI/v2/timeseries/data',
        
        # US Census Bureau - Free, no key required  
        'census_base_url': 'https://api.census.gov/data',
        
        # Timeout settings
        'timeout': 30,
        'max_retries': 3,
        'fallback_enabled': True,
        
        # Cache settings
        'cache_duration_hours': 24,
        'max_cache_size_mb': 100,
        
        # Rate limiting
        'rate_limit_per_hour': 1000,
        'rate_limit_per_minute': 20
    }
    
    return config


def get_interest_rate_config() -> Dict[str, Any]:
    """Get configuration specifically for interest rate feeds"""
    base_config = get_api_config()
    
    return {
        'fred_api_key': base_config['fred_api_key'],
        'timeout': base_config['timeout'],
        'max_retries': base_config['max_retries'],
        
        # FRED series IDs for interest rates
        'fred_series': {
            '30_year_fixed': 'MORTGAGE30US',      # 30-Year Fixed Rate Mortgage Average
            '15_year_fixed': 'MORTGAGE15US',      # 15-Year Fixed Rate Mortgage Average  
            'federal_funds_rate': 'FEDFUNDS',     # Federal Funds Effective Rate
            '10_year_treasury': 'GS10',           # 10-Year Treasury Constant Maturity Rate
            '30_year_treasury': 'GS30',           # 30-Year Treasury Constant Maturity Rate
            'prime_rate': 'DPRIME',               # Bank Prime Loan Rate
        },
        
        # Backup sources
        'backup_sources': [
            {
                'name': 'freddie_mac_pmms',
                'url': 'http://www.freddiemac.com/pmms',
                'weight': 0.9
            },
            {
                'name': 'bankrate',
                'url': 'https://www.bankrate.com/mortgages/mortgage-rates',
                'weight': 0.7,
                'parser': 'html'
            }
        ]
    }


def get_market_data_config() -> Dict[str, Any]:
    """Get configuration for market data APIs"""
    base_config = get_api_config()
    
    return {
        'alpha_vantage_api_key': base_config['alpha_vantage_api_key'],
        'timeout': base_config['timeout'],
        'max_retries': base_config['max_retries'],
        
        # Primary APIs for real estate data
        'primary_apis': {
            'alpha_vantage': {
                'url': base_config['alpha_vantage_base_url'],
                'key': base_config['alpha_vantage_api_key'],
                'weight': 1.0,
                'functions': {
                    'real_estate': 'REAL_ESTATE',
                    'economic_indicators': 'ECONOMIC_INDICATORS'
                }
            }
        },
        
        # Free data sources (no API key required)
        'free_sources': {
            'bls': {
                'url': base_config['bls_base_url'],
                'weight': 0.8,
                'series_ids': {
                    'cpi_housing': 'CUUR0000SAH1',        # Consumer Price Index: Housing
                    'unemployment': 'LNS14000000',        # Unemployment Rate
                    'employment_cost': 'CIU1010000000000A' # Employment Cost Index
                }
            },
            'census': {
                'url': base_config['census_base_url'],
                'weight': 0.7,
                'datasets': {
                    'housing': '2021/acs/acs1',           # American Community Survey: Housing
                    'population': '2021/pep/population',   # Population Estimates
                    'income': '2021/acs/acs1/subject'     # Income and Earnings
                }
            }
        },
        
        # Fallback data for when APIs are unavailable
        'fallback_data': {
            'median_rent_per_sqm': 25.0,
            'rental_vacancy_rate': 6.5,
            'rental_growth_rate': 3.0,
            'median_property_price': 400000,
            'property_appreciation_rate': 4.0,
            'months_on_market': 2.5,
            'local_inflation_rate': 3.2,
            'unemployment_rate': 4.0,
            'population_growth_rate': 1.2
        }
    }


def validate_api_configuration() -> Dict[str, Any]:
    """
    Validate API configuration and return status
    
    Returns:
        Dict with validation results and recommendations
    """
    config = get_api_config()
    interest_config = get_interest_rate_config()
    market_config = get_market_data_config()
    
    validation = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'api_status': {},
        'recommendations': []
    }
    
    # Check FRED API key
    if not config.get('fred_api_key'):
        validation['warnings'].append('FRED API key not configured - using mock interest rate data')
        validation['recommendations'].append('Get free FRED API key from https://fred.stlouisfed.org/docs/api/api_key.html')
        validation['api_status']['fred'] = 'mock_data'
    else:
        validation['api_status']['fred'] = 'configured'
    
    # Check Alpha Vantage API key
    if not config.get('alpha_vantage_api_key'):
        validation['warnings'].append('Alpha Vantage API key not configured - limited market data available')
        validation['recommendations'].append('Get free Alpha Vantage API key from https://www.alphavantage.co/support/#api-key')
        validation['api_status']['alpha_vantage'] = 'mock_data'
    else:
        validation['api_status']['alpha_vantage'] = 'configured'
    
    # Free APIs (always available)
    validation['api_status']['bls'] = 'available'
    validation['api_status']['census'] = 'available'
    
    # Overall status
    if validation['errors']:
        validation['valid'] = False
    
    return validation


def get_setup_instructions() -> str:
    """
    Get setup instructions for API configuration
    
    Returns:
        String with setup instructions
    """
    
    instructions = """
🔧 API SETUP INSTRUCTIONS

To enable real-time market data and interest rates, set up these free API keys:

1. 📊 FEDERAL RESERVE ECONOMIC DATA (FRED) - Required for interest rates
   • Go to: https://fred.stlouisfed.org/docs/api/api_key.html
   • Sign up for free account
   • Get your API key
   • Set environment variable: export FRED_API_KEY=your_key_here

2. 📈 ALPHA VANTAGE - Optional for enhanced market data  
   • Go to: https://www.alphavantage.co/support/#api-key
   • Sign up for free account (500 requests/day)
   • Get your API key
   • Set environment variable: export ALPHA_VANTAGE_API_KEY=your_key_here

3. 🏛️ BLS & CENSUS - Free APIs (no key required)
   • Bureau of Labor Statistics: Automatic
   • US Census Bureau: Automatic

💡 Without API keys, the app will use realistic mock data that updates periodically.

🔄 To apply changes:
   • Set environment variables in your terminal
   • Restart the Streamlit application
   • Check API status in the Data Integration tab

📝 Current Status: Run `python -c "from src.data.api_config import validate_api_configuration; print(validate_api_configuration())"` to check
"""
    
    return instructions


if __name__ == "__main__":
    # Test configuration
    print("🔧 API CONFIGURATION TEST")
    print("=" * 50)
    
    config = get_api_config()
    validation = validate_api_configuration()
    
    print("📊 Current Configuration:")
    for key, value in validation['api_status'].items():
        status_emoji = "✅" if value == "configured" else "⚠️" if value == "available" else "❌"
        print(f"   {status_emoji} {key}: {value}")
    
    print(f"\n📋 Validation Status: {'✅ Valid' if validation['valid'] else '❌ Issues found'}")
    
    if validation['warnings']:
        print("\n⚠️ Warnings:")
        for warning in validation['warnings']:
            print(f"   • {warning}")
    
    if validation['recommendations']:
        print("\n💡 Recommendations:")
        for rec in validation['recommendations']:
            print(f"   • {rec}")
    
    print("\n" + get_setup_instructions())