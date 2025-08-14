#!/usr/bin/env python3
"""
Debug the UI component to see exactly what it will display
"""

import sys
import os
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def simulate_ui_indicator(field_name, current_value, field_data):
    """Simulate what the _show_api_indicator function will display"""
    
    source = field_data.get('source', '')
    is_api_updated = any(keyword in source.lower() for keyword in ['api', 'estimate', 'fred', 'market', 'location', 'international'])
    is_user_modified = field_data.get('user_modified', False)
    
    if is_api_updated and not is_user_modified:
        # Show API indicator with styled background
        source_display = _format_api_source(source)
        
        # Check for metadata (data date)
        metadata = field_data.get('metadata', {})
        data_date = metadata.get('data_date', '')
        live_rate_used = metadata.get('live_rate_used', False)
        api_available = metadata.get('api_available', False)
        
        # Extract date from source name as fallback
        if not data_date and '(' in source and ')' in source:
            # Extract date from source like "international_data_for_Warsaw, Poland_(2024-08-14)"
            date_match = re.search(r'\((\d{4}-\d{2}-\d{2})\)', source)
            if date_match:
                data_date = date_match.group(1)
        
        # Create additional info for static vs live data
        extra_info = ""
        if live_rate_used:
            extra_info = f" • 🔴 LIVE API"
        elif data_date:
            extra_info = f" • 📅 Data from {data_date}"
        elif not api_available and 'international' in source.lower():
            extra_info = f" • 📊 Static data"
        
        indicator_html = f'🌐 API Updated: {source_display} • Value: {current_value}{"%" if "rate" in field_name else ""}{extra_info}'
        
        return indicator_html
    
    return None


def _format_api_source(source: str) -> str:
    """Format API source for display"""
    source_mapping = {
        'fred_api': 'Federal Reserve (FRED)',
        'market_api': 'Market Data API',
        'location_estimate': 'Location-based Estimate',
        'international_data': 'Central Bank Data',
        'bcb_live_api': 'Brazil Central Bank (Live)',
        'boi_live_api': 'Israel Central Bank (Live)'
    }
    
    # Clean up source name
    clean_source = source.lower()
    
    # Remove location-specific parts
    clean_source = re.sub(r'_for_.*?_\(', '_(', clean_source)
    clean_source = re.sub(r'_for_.*', '', clean_source)
    
    for key, display_name in source_mapping.items():
        if key in clean_source:
            return display_name
    
    # Default formatting
    formatted = source.replace('_', ' ').title()
    formatted = re.sub(r'Api|API', 'API', formatted)
    return formatted


def test_ui_component():
    """Test the UI component with real data"""
    
    print("🖥️  UI Component Debug Test")
    print("=" * 50)
    
    # Test case 1: Poland with date in source
    print("\n📍 Test Case 1: Warsaw, Poland")
    field_data_poland = {
        'value': 7.2,
        'source': 'international_data_for_Warsaw, Poland_(2024-08-14)',
        'priority_level': 'api_data',
        'user_modified': False,
        'metadata': {
            'country': 'Poland',
            'data_date': '2024-08-14',
            'api_available': False
        }
    }
    
    indicator = simulate_ui_indicator('interest_rate', 7.2, field_data_poland)
    print(f"UI will show: {indicator}")
    
    # Test case 2: Brazil with live data
    print("\n📍 Test Case 2: São Paulo, Brazil (Live)")
    field_data_brazil = {
        'value': 1.055131,
        'source': 'international_data_for_São Paulo, Brazil_(2024-08-14)',
        'priority_level': 'api_data', 
        'user_modified': False,
        'metadata': {
            'country': 'Brazil',
            'data_date': '2024-08-14',
            'api_available': True,
            'live_rate_used': True
        }
    }
    
    indicator = simulate_ui_indicator('interest_rate', 1.055131, field_data_brazil)
    print(f"UI will show: {indicator}")
    
    # Test case 3: Source without date
    print("\n📍 Test Case 3: Generic API source")
    field_data_generic = {
        'value': 6.5,
        'source': 'fred_api_for_New York, NY',
        'priority_level': 'api_data',
        'user_modified': False,
        'metadata': {}
    }
    
    indicator = simulate_ui_indicator('interest_rate', 6.5, field_data_generic)
    print(f"UI will show: {indicator}")
    
    print(f"\n" + "=" * 50)
    print("📋 Summary:")
    print("• Poland should show: 📅 Data from 2024-08-14")
    print("• Brazil (live) should show: 🔴 LIVE API")
    print("• Generic should show: no extra date info")


if __name__ == "__main__":
    test_ui_component()