#!/usr/bin/env python3
"""
Test script to verify the rent_increase_rate fix works with:
1. API defaults overridden by user
2. Subletting enabled 
3. Specific rent_increase_rate values that caused the error
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_api_override_with_subletting():
    """Test the exact scenario that was causing the NameError"""
    print("🧪 Testing API Override + Subletting Scenario")
    print("=" * 50)
    
    # Test parameters that match the user's failing case
    test_params = {
        # Basic purchase parameters
        'purchase_price': 3200000.0,
        'down_payment_pct': 30.0,
        'interest_rate': 5.06,  # User overrode API default
        'loan_term': 20,
        'transaction_costs': 2560000.0,
        
        # Rental parameters - USER OVERRODE API DEFAULT
        'current_annual_rent': 1300000,
        'rent_increase_rate': 1.0,  # USER SET TO 1% (was API default ~4.5%)
        'moving_costs': 500000,
        
        # Common parameters
        'analysis_period': 25,
        'cost_of_capital': 8.0,
        
        # Property parameters
        'property_tax_rate': 1.2,
        'property_tax_escalation': 2.0,
        'insurance_cost': 5000,
        'annual_maintenance': 10000,
        'property_management': 0.0,
        'capex_reserve_rate': 1.5,
        'obsolescence_risk_rate': 0.5,
        'inflation_rate': 3.0,
        'market_appreciation_rate': 3.5,
        'land_value_pct': 30.0,
        'depreciation_period': 40,
        
        # Tax parameters
        'corporate_tax_rate': 25.0,
        'interest_deductible': True,
        'property_tax_deductible': True,
        'depreciation_deductible': True,
        'rent_deductible': True,
        
        # Space and expansion
        'future_expansion_year': 'Never',
        'additional_space_needed': 0.0,
        'current_space_needed': 8000,
        'ownership_property_size': 8000,
        'rental_property_size': 8000,
        'space_improvement_cost': 0.0,
        
        # SUBLETTING ENABLED - This triggers the problematic code path
        'subletting_potential': True,
        'subletting_rate': 120.0,  # Rate per sqm
        'subletting_space_sqm': 2000,  # 2000 sqm available for subletting
        
        # Property upgrade
        'property_upgrade_cycle': 30
    }
    
    print(f"🔍 Key test conditions:")
    print(f"  - rent_increase_rate: {test_params['rent_increase_rate']}% (USER OVERRIDE)")
    print(f"  - subletting_potential: {test_params['subletting_potential']}")
    print(f"  - subletting_space_sqm: {test_params['subletting_space_sqm']} sqm")
    print(f"  - interest_rate: {test_params['interest_rate']}% (USER OVERRIDE)")
    print()
    
    try:
        from calculations.npv_analysis import calculate_npv_comparison
        
        print("✅ Successfully imported calculate_npv_comparison")
        
        # This is the exact call that was failing in production
        print("🔍 Running NPV analysis with subletting + API overrides...")
        result = calculate_npv_comparison(**test_params)
        
        print("✅ NPV calculation succeeded!")
        print()
        print("📊 Key Results:")
        print(f"  - NPV Difference: ${result.get('npv_difference', 0):,.2f}")
        print(f"  - Recommendation: {result.get('recommendation', 'N/A')}")
        print(f"  - Ownership NPV: ${result.get('ownership_npv', 0):,.2f}")
        print(f"  - Rental NPV: ${result.get('rental_npv', 0):,.2f}")
        
        # Test multiple rent increase rates that could be problematic
        test_rates = [0.5, 1.0, 1.5, 2.0, 3.0, 4.5]
        print(f"\n🧪 Testing multiple rent_increase_rate values:")
        
        for rate in test_rates:
            test_params_copy = test_params.copy()
            test_params_copy['rent_increase_rate'] = rate
            
            try:
                result = calculate_npv_comparison(**test_params_copy)
                npv_diff = result.get('npv_difference', 0)
                print(f"  ✅ rent_increase_rate {rate}%: NPV = ${npv_diff:,.0f}")
            except Exception as e:
                print(f"  ❌ rent_increase_rate {rate}%: ERROR - {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR in NPV calculation: {e}")
        import traceback
        print("\n🔍 Full traceback:")
        print(traceback.format_exc())
        
        # Check if this is the specific rent_increase_rate error
        if "rent_increase_rate" in str(e) and "not defined" in str(e):
            print("\n🚨 This is the exact error the user was experiencing!")
            print("   The import fix should have resolved this.")
        
        return False

def test_cash_flow_calculations():
    """Test the cash flow calculations that also use rent_increase_rate"""
    print("\n🧪 Testing Cash Flow Calculations")
    print("=" * 40)
    
    try:
        from calculations.npv_analysis import calculate_ownership_cash_flows, calculate_rental_cash_flows
        
        # Test ownership cash flows (includes subletting)
        print("🔍 Testing ownership cash flows with subletting...")
        ownership_flows = calculate_ownership_cash_flows(
            purchase_price=3200000.0,
            down_payment_pct=30.0,
            interest_rate=5.06,
            loan_term=20,
            analysis_period=25,
            property_tax_rate=1.2,
            property_tax_escalation=2.0,
            insurance_cost=5000,
            annual_maintenance=10000,
            capex_reserve_rate=1.5,
            obsolescence_risk_rate=0.5,
            inflation_rate=3.0,
            market_appreciation_rate=3.5,
            land_value_pct=30.0,
            depreciation_period=40,
            corporate_tax_rate=25.0,
            # Subletting parameters
            subletting_potential=True,
            subletting_rate=120.0,
            subletting_space_sqm=2000,
            ownership_property_size=8000,
            current_space_needed=8000,
            rent_increase_rate=1.0,  # The problematic value
            future_expansion_year='Never'
        )
        
        print(f"✅ Ownership cash flows calculated: {len(ownership_flows)} years")
        
        # Test rental cash flows
        print("🔍 Testing rental cash flows...")
        rental_flows = calculate_rental_cash_flows(
            current_annual_rent=1300000,
            rent_increase_rate=1.0,  # The problematic value
            analysis_period=25,
            corporate_tax_rate=25.0,
            rent_deductible=True,
            future_expansion_year='Never',
            additional_space_needed=0.0,
            current_space_needed=8000,
            rental_property_size=8000,
            inflation_rate=3.0
        )
        
        print(f"✅ Rental cash flows calculated: {len(rental_flows)} years")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR in cash flow calculations: {e}")
        return False

def main():
    """Run all tests"""
    print("🏠 Comprehensive Test: API Override + Subletting Fix")
    print("=" * 60)
    print("Testing the exact scenario that caused the NameError:")
    print("- User selected Australia (API data available)")
    print("- User overrode rent_increase_rate to 1%") 
    print("- User enabled subletting")
    print("- This combination caused 'name rent_increase_rate is not defined'")
    print()
    
    tests = [
        ("NPV Analysis with API Override + Subletting", test_api_override_with_subletting),
        ("Cash Flow Calculations", test_cash_flow_calculations)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 SUCCESS: The import fix has resolved the rent_increase_rate error!")
        print("   Users can now override API data and use subletting without NameError.")
    else:
        print("\n⚠️  FAILURE: The error may still exist or there are other issues.")

if __name__ == "__main__":
    main()