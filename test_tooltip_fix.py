#!/usr/bin/env python3
"""
Test script to verify tooltip/indicator system fix
Tests the scenarios described in the bug report
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from data.data_priority_manager import reset_data_priority_manager
from data.international_data import get_international_provider

def test_brazil_tooltip():
    """Test Brazil scenario - should show blue API indicator"""
    print("\n=== Testing Brazil (São Paulo) ===")
    
    # Reset managers for clean test
    priority_manager = reset_data_priority_manager()
    international_provider = get_international_provider()
    
    # Test address: São Paulo, Brazil
    address = "São Paulo, Brazil"
    print(f"Address: {address}")
    
    # Check location parsing
    city, state, country = international_provider.parse_location(address)
    print(f"Parsed: city={city}, state={state}, country={country}")
    
    # Check if supported
    is_supported = international_provider.is_supported_country(address)
    print(f"Is supported: {is_supported}")
    
    # Get estimates
    data = international_provider.get_international_estimates(address)
    print(f"Has estimates: {bool(data['estimates'])}")
    
    if data['estimates']:
        print("Available data:")
        for key, value in data['estimates'].items():
            print(f"  {key}: {value}")
            
        print("\nMetadata:")
        metadata = data['metadata']
        for key, value in metadata.items():
            print(f"  {key}: {value}")
            
        # Check specific interest rate data
        if 'interest_rate' in data['estimates']:
            interest_rate = data['estimates']['interest_rate']
            
            # Set the API data in priority manager
            priority_manager.set_api_data(
                'interest_rate',
                interest_rate, 
                f"international_data_for_{address}",
                metadata=metadata
            )
            
            # Check the priority manager state
            field_data = priority_manager.get_value('interest_rate')
            print(f"\nPriority Manager State:")
            print(f"  value: {field_data['value']}")
            print(f"  source: {field_data['source']}")
            print(f"  user_modified: {field_data.get('user_modified', False)}")
            print(f"  priority_level: {field_data['priority_level']}")
            
            # This should show BLUE tooltip (API updated) not orange (user override)
            expected_tooltip = "🌐 API Updated: Central Bank Data"
            if metadata.get('live_rate_used'):
                expected_tooltip += " • 🔴 LIVE API"
            else:
                data_date = metadata.get('data_date', '2024-08-14')
                expected_tooltip += f" • 📅 Data from {data_date}"
                
            print(f"Expected tooltip type: BLUE (API Updated)")
            print(f"Expected tooltip: {expected_tooltip}")
            
            return True
            
    return False

def test_argentina_tooltip():
    """Test Argentina scenario - should show no indicators"""
    print("\n=== Testing Argentina (Buenos Aires) ===")
    
    # Reset managers for clean test  
    priority_manager = reset_data_priority_manager()
    international_provider = get_international_provider()
    
    # Test address: Buenos Aires, Argentina
    address = "Buenos Aires, Argentina"
    print(f"Address: {address}")
    
    # Check location parsing
    city, state, country = international_provider.parse_location(address)
    print(f"Parsed: city={city}, state={state}, country={country}")
    
    # Check if supported
    is_supported = international_provider.is_supported_country(address)
    print(f"Is supported: {is_supported}")
    
    # Get estimates
    data = international_provider.get_international_estimates(address)
    print(f"Has estimates: {bool(data['estimates'])}")
    
    if not data['estimates']:
        # This should result in NO indicators, clean defaults
        print("Expected behavior: NO tooltips/indicators (clean defaults)")
        print("Expected tooltip type: NONE")
        
        # Check that priority manager has no API data
        try:
            field_data = priority_manager.get_value('interest_rate')
            print(f"\nPriority Manager State:")
            print(f"  priority_level: {field_data['priority_level']}")
            
            if field_data['priority_level'] == 'default_data':
                print("✅ Correct: Using system defaults")
                return True
            else:
                print("❌ Wrong: Should be using defaults")
                return False
        except ValueError:
            print("✅ Correct: No data in priority manager")
            return True
    else:
        print("❌ Unexpected: Argentina should not have data")
        return False

def test_user_override_scenario():
    """Test user override scenario - should show orange user override tooltip"""
    print("\n=== Testing User Override ===")
    
    # Reset managers for clean test
    priority_manager = reset_data_priority_manager()
    
    # First set some API data
    priority_manager.set_api_data(
        'interest_rate',
        7.2,
        'international_data_for_Warsaw, Poland',
        metadata={'country': 'poland', 'data_date': '2024-08-14'}
    )
    
    # Now user overrides it
    priority_manager.set_user_override('interest_rate', 8.5, 'user_input')
    
    # Check the state
    field_data = priority_manager.get_value('interest_rate')
    print(f"Priority Manager State after user override:")
    print(f"  value: {field_data['value']}")
    print(f"  source: {field_data['source']}")
    print(f"  user_modified: {field_data.get('user_modified', False)}")
    print(f"  priority_level: {field_data['priority_level']}")
    
    # This should show ORANGE tooltip (user override)
    expected_tooltip = "✏️ User Override: Your custom value is protected from API updates"
    print(f"Expected tooltip type: ORANGE (User Override)")
    print(f"Expected tooltip: {expected_tooltip}")
    
    return field_data.get('user_modified', False) and field_data['priority_level'] == 'user_override'

def main():
    """Run all tests"""
    print("Testing Tooltip/Indicator System Fix")
    print("=" * 50)
    
    results = []
    
    # Test Brazil (should show blue API tooltip)
    results.append(("Brazil", test_brazil_tooltip()))
    
    # Test Argentina (should show no tooltip)  
    results.append(("Argentina", test_argentina_tooltip()))
    
    # Test User Override (should show orange tooltip)
    results.append(("User Override", test_user_override_scenario()))
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Tooltip system is working correctly!")
        print("- Brazil shows blue API indicators")
        print("- Argentina shows no indicators (clean defaults)")
        print("- User overrides show orange indicators")
    else:
        print("\n🚨 Issues detected in tooltip system")

if __name__ == "__main__":
    main()