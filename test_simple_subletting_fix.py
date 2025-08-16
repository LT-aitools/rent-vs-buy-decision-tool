#!/usr/bin/env python3
"""
Simple test to verify the rent_increase_rate fix works with subletting enabled
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_subletting_with_rent_increase_rate():
    """Test the exact scenario: subletting enabled + rent_increase_rate = 1%"""
    print("🧪 Testing Subletting + rent_increase_rate = 1%")
    print("=" * 45)
    
    # Minimal parameters that match the exact failing scenario
    test_params = {
        # Required basic parameters
        'purchase_price': 3200000.0,
        'down_payment_pct': 30.0,
        'interest_rate': 5.06,
        'loan_term': 20,
        'transaction_costs': 256000.0,  # 8% of purchase price
        'current_annual_rent': 1300000,
        'rent_increase_rate': 1.0,  # The problematic value that caused the error
        'analysis_period': 25,
        'cost_of_capital': 8.0,
        
        # Subletting parameters - THIS TRIGGERS THE CODE PATH THAT WAS FAILING
        'subletting_potential': True,
        'subletting_rate': 120.0,
        'subletting_space_sqm': 2000,
        'ownership_property_size': 8000,
        'current_space_needed': 6000  # So there's space available for subletting
    }
    
    print(f"🔍 Test conditions:")
    print(f"  - rent_increase_rate: {test_params['rent_increase_rate']}%")
    print(f"  - subletting_potential: {test_params['subletting_potential']}")
    print(f"  - subletting_space_sqm: {test_params['subletting_space_sqm']}")
    print()
    
    try:
        from calculations.npv_analysis import calculate_npv_comparison
        
        print("✅ Successfully imported calculate_npv_comparison")
        
        # This exact combination was causing "name 'rent_increase_rate' is not defined"
        print("🔍 Running NPV analysis...")
        result = calculate_npv_comparison(**test_params)
        
        print("🎉 SUCCESS! NPV calculation completed without NameError!")
        print()
        print("📊 Results:")
        print(f"  - NPV Difference: ${result.get('npv_difference', 0):,.2f}")
        print(f"  - Recommendation: {result.get('recommendation', 'N/A')}")
        
        # Test a few different rent increase rates to be thorough
        problematic_rates = [0.5, 1.0, 1.5, 2.0]
        print(f"\n🔍 Testing multiple rent_increase_rate values:")
        
        for rate in problematic_rates:
            test_params_copy = test_params.copy()
            test_params_copy['rent_increase_rate'] = rate
            
            try:
                result = calculate_npv_comparison(**test_params_copy)
                print(f"  ✅ {rate}%: NPV = ${result.get('npv_difference', 0):,.0f}")
            except Exception as e:
                print(f"  ❌ {rate}%: ERROR - {e}")
                if "rent_increase_rate" in str(e):
                    print("      ^ This is the original error!")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        
        if "rent_increase_rate" in str(e) and "not defined" in str(e):
            print("\n🚨 This is the exact error the user reported!")
            print("   The import fix did not resolve the issue.")
        
        import traceback
        print(f"\n🔍 Full error details:")
        print(traceback.format_exc())
        return False

def main():
    print("🏠 Testing Subletting + rent_increase_rate Fix")
    print("=" * 50)
    print("This test reproduces the exact conditions that caused:")
    print("  Error: name 'rent_increase_rate' is not defined")
    print()
    print("Conditions:")
    print("  - Australia selected (API data available)")
    print("  - User overrode rent_increase_rate to 1%") 
    print("  - Subletting enabled")
    print()
    
    success = test_subletting_with_rent_increase_rate()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: The import fix resolved the issue!")
        print("   ✅ Subletting + rent_increase_rate now works")
        print("   ✅ No more NameError when users override API data")
    else:
        print("❌ FAILURE: The issue persists")
        print("   The import fix may not have been sufficient")

if __name__ == "__main__":
    main()