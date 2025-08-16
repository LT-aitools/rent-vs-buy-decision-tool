#!/usr/bin/env python3
"""
Debug script to find the specific cause of 'name rent_increase_rate is not defined'
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Test the exact parameters from the user's error
test_params = {
    'purchase_price': 3200000.0,
    'down_payment_pct': 30.0,
    'interest_rate': 5.06,
    'loan_term': 20,
    'transaction_costs': 2560000.0,
    'current_annual_rent': 1300000,
    'rent_increase_rate': 1.5,  # This is present!
    'moving_costs': 500000,
    'analysis_period': 25,
    'cost_of_capital': 8.0,
}

print("🔍 Testing NPV calculation with exact user parameters...")
print(f"📊 rent_increase_rate value: {test_params['rent_increase_rate']}")

try:
    from calculations.npv_analysis import calculate_npv_comparison
    
    print("✅ Successfully imported calculate_npv_comparison")
    
    # Test the function call
    result = calculate_npv_comparison(**test_params)
    print("✅ NPV calculation succeeded!")
    print(f"📈 NPV result: {result.get('npv_difference', 'N/A')}")
    
except Exception as e:
    print(f"❌ Error in NPV calculation: {e}")
    import traceback
    print("\n🔍 Full traceback:")
    print(traceback.format_exc())
    
    # Check if this is the exact error the user is seeing
    if "rent_increase_rate" in str(e) and "not defined" in str(e):
        print("\n🎯 This matches the user's error!")
        
        # Try to identify the problematic line
        tb = traceback.extract_tb(e.__traceback__)
        for frame in tb:
            if "rent_increase_rate" in frame.line:
                print(f"📍 Problematic line: {frame.filename}:{frame.lineno}")
                print(f"📝 Code: {frame.line}")