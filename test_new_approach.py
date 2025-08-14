#!/usr/bin/env python3
"""
Test the new simplified country dropdown approach
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from data.data_priority_manager import reset_data_priority_manager
from data.international_data import get_international_provider

def test_country_scenarios():
    """Test different country scenarios"""
    print("Testing New Country Dropdown Approach")
    print("=" * 50)
    
    # Reset for clean test
    priority_manager = reset_data_priority_manager()
    international_provider = get_international_provider()
    
    test_cases = [
        ("usa", "United States"),
        ("brazil", "Brazil"),
        ("uk", "United Kingdom"), 
        ("argentina", "Argentina (Other)"),
        ("china", "China (Other)")
    ]
    
    for country_code, country_name in test_cases:
        print(f"\n=== Testing {country_name} ===")
        
        if country_code == "usa":
            print("Expected: Live FRED API data")
            print("Expected tooltips: 🔵 Blue API indicators")
            
        elif country_code in ["brazil", "uk"]:
            # Get international data - need to test the lookup
            print(f"Looking up data for: {country_code}")
            data = international_provider.get_international_estimates(country_code)
            if data['estimates']:
                print(f"Expected: Static data available")
                print("Expected tooltips: 🔵 Blue API indicators")
                
                # Show sample data
                estimates = data['estimates']
                print(f"Sample data: Interest Rate = {estimates.get('interest_rate', 'N/A')}%")
            else:
                print("Expected: No data found")
                
        else:
            # Unsupported countries like Argentina, China
            data = international_provider.get_international_estimates(country_code)
            if not data['estimates']:
                print("Expected: Default values")
                print("Expected tooltips: No indicators (clean interface)")
            else:
                print("Unexpected: Found data for unsupported country")
    
    print("\n" + "=" * 50)
    print("User Override Test:")
    print("1. Select Brazil → Should show blue API tooltip")
    print("2. User changes interest rate → Should show orange User Override tooltip")
    print("3. User changes back to country → Should show blue API tooltip again")
    print("")
    print("✅ Ready to test in Streamlit app!")

if __name__ == "__main__":
    test_country_scenarios()