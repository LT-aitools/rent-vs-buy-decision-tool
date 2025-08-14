"""
API Status Information
Tracks the status of international API integrations
"""

from typing import Dict, Any
from datetime import datetime


def get_api_status() -> Dict[str, Any]:
    """
    Get current status of all API integrations
    
    Returns:
        Dict with API status information
    """
    return {
        'brazil': {
            'name': 'Brazil Central Bank (BCB)',
            'status': 'active',
            'api_url': 'https://api.bcb.gov.br',
            'endpoint': '/dados/serie/bcdata.sgs.11/dados',
            'data_source': 'Selic Rate (Series 11)',
            'last_tested': '2025-08-14',
            'works': True,
            'notes': 'Full API integration working. Fetches live Selic rates.',
            'rate_calculation': 'Mortgage Rate = Selic Rate + 1% margin',
            'confidence': 0.95
        },
        'israel': {
            'name': 'Bank of Israel (BOI)',
            'status': 'investigating',
            'api_url': 'https://edge.boi.gov.il',
            'endpoint': 'TBD - API structure unclear',
            'data_source': 'Monetary Policy Rate',
            'last_tested': '2025-08-14',
            'works': False,
            'notes': 'API exists but endpoint structure needs investigation. Falls back to static rates.',
            'rate_calculation': 'Using static rate 5.3% until API integration complete',
            'confidence': 0.8,
            'fallback_rate': 5.3,
            'todo': 'Research correct API endpoints at edge.boi.gov.il'
        },
        'usa': {
            'name': 'Federal Reserve Economic Data (FRED)',
            'status': 'active',
            'api_url': 'https://api.stlouisfed.org',
            'endpoint': '/fred/series/observations',
            'data_source': 'Multiple mortgage rate series',
            'last_tested': '2025-08-14',
            'works': True,
            'notes': 'Full integration working via existing interest_rate_feeds.py',
            'confidence': 0.95
        },
        'other_countries': {
            'status': 'static_data',
            'countries': [
                'UK (Bank of England)',
                'Canada (Bank of Canada)', 
                'Australia (RBA)',
                'Germany (ECB)',
                'France (ECB)',
                'Netherlands (ECB)',
                'Japan (BOJ)',
                'Singapore (MAS)',
                'Poland (NBP)'
            ],
            'notes': 'Using static rates with known data dates. API integration possible but not implemented.',
            'confidence': 0.75,
            'data_date': '2024-08-14'
        }
    }


def print_api_status():
    """Print formatted API status report"""
    status = get_api_status()
    
    print("🌍 International API Status Report")
    print("=" * 50)
    
    for country, info in status.items():
        if country == 'other_countries':
            continue
            
        status_emoji = "✅" if info.get('works') else "🔍" if info.get('status') == 'investigating' else "❌"
        
        print(f"\n{status_emoji} {info['name']}")
        print(f"   Status: {info['status']}")
        print(f"   API URL: {info['api_url']}")
        print(f"   Endpoint: {info['endpoint']}")
        print(f"   Works: {'Yes' if info.get('works') else 'No'}")
        print(f"   Confidence: {info['confidence']*100:.0f}%")
        print(f"   Notes: {info['notes']}")
        
        if 'rate_calculation' in info:
            print(f"   Rate Calc: {info['rate_calculation']}")
    
    # Other countries
    other = status['other_countries']
    print(f"\n📊 {len(other['countries'])} Other Countries")
    print(f"   Status: {other['status']}")
    print(f"   Data Date: {other['data_date']}")
    print(f"   Countries: {', '.join(other['countries'][:5])}...")
    print(f"   Notes: {other['notes']}")


if __name__ == "__main__":
    print_api_status()