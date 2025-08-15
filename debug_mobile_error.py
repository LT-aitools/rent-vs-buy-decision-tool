#!/usr/bin/env python3
"""
Debug script to reproduce the mobile "rent increase rate is not defined" error
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analytics.input_validation import AnalyticsInputValidator
from utils.defaults import DEFAULT_VALUES

def test_mobile_session_state():
    """Test case simulating mobile session state issue"""
    print("🔍 Testing mobile session state issue...")
    
    # Simulate incomplete session state that might occur on mobile
    incomplete_params = {
        'purchase_price': 500000,
        'current_annual_rent': 60000,
        # Missing rent_increase_rate - this might be the issue
        'analysis_period': 25,
        'cost_of_capital': 8.0
    }
    
    print(f"📱 Mobile-like incomplete params: {list(incomplete_params.keys())}")
    
    try:
        # Try validation with incomplete parameters
        validated = AnalyticsInputValidator.validate_base_parameters(incomplete_params)
        print("✅ Validation passed")
        print(f"🔧 Validated params: {list(validated.keys())}")
        
        if 'rent_increase_rate' in validated:
            print(f"✅ rent_increase_rate present: {validated['rent_increase_rate']}")
        else:
            print("❌ rent_increase_rate missing from validated params!")
            
    except Exception as e:
        print(f"❌ Validation error: {e}")
        print(f"🐛 Error type: {type(e).__name__}")
        return False
    
    return True

def test_default_values():
    """Test that DEFAULT_VALUES includes rent_increase_rate"""
    print("\n🔍 Testing DEFAULT_VALUES...")
    
    if 'rent_increase_rate' in DEFAULT_VALUES:
        print(f"✅ rent_increase_rate in DEFAULT_VALUES: {DEFAULT_VALUES['rent_increase_rate']}")
        return True
    else:
        print("❌ rent_increase_rate missing from DEFAULT_VALUES!")
        print(f"📋 Available keys: {list(DEFAULT_VALUES.keys())}")
        return False

def test_parameter_extraction():
    """Test parameter extraction from session state simulation"""
    print("\n🔍 Testing parameter extraction...")
    
    # Simulate session state with all required parameters
    full_session_state = DEFAULT_VALUES.copy()
    full_session_state.update({
        'purchase_price': 500000,
        'current_annual_rent': 60000,
        'rent_increase_rate': 3.0
    })
    
    # Extract relevant parameters (simulating what might happen in analysis)
    relevant_fields = [
        "purchase_price", "down_payment", "interest_rate", "loan_term",
        "property_tax_annual", "property_tax_escalation",
        "current_annual_rent", "rent_increase_rate", "analysis_period", 
        "cost_of_capital"
    ]
    
    extracted = {}
    for field in relevant_fields:
        if field in full_session_state:
            extracted[field] = full_session_state[field]
        else:
            print(f"⚠️  Missing field: {field}")
    
    print(f"📊 Extracted {len(extracted)}/{len(relevant_fields)} parameters")
    
    if 'rent_increase_rate' in extracted:
        print(f"✅ rent_increase_rate extracted: {extracted['rent_increase_rate']}")
        return True
    else:
        print("❌ rent_increase_rate missing from extraction!")
        return False

def main():
    """Run all diagnostic tests"""
    print("🏠 Mobile Error Diagnostic Tool")
    print("=" * 40)
    
    tests = [
        ("Default Values", test_default_values),
        ("Mobile Session State", test_mobile_session_state),
        ("Parameter Extraction", test_parameter_extraction)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"📊 Result: {'✅ PASS' if result else '❌ FAIL'}")
        except Exception as e:
            print(f"💥 Test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("📋 Test Summary:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if not all_passed:
        print("\n💡 Potential fixes:")
        print("1. Ensure DEFAULT_VALUES includes all required parameters")
        print("2. Add fallback values in parameter extraction")
        print("3. Improve mobile session state persistence")

if __name__ == "__main__":
    main()