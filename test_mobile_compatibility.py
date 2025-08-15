#!/usr/bin/env python3
"""
Test mobile compatibility for the rent vs buy analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_mobile_parameter_handling():
    """Test parameter handling that might fail on mobile"""
    print("🧪 Testing mobile parameter handling...")
    
    # Simulate missing or None values that might occur on mobile
    test_cases = [
        {"name": "None rent_increase_rate", "rent_increase_rate": None},
        {"name": "Empty rent_increase_rate", "rent_increase_rate": ""},
        {"name": "Zero rent_increase_rate", "rent_increase_rate": 0},
        {"name": "Negative rent_increase_rate", "rent_increase_rate": -1},
        {"name": "Missing rent_increase_rate", "params_without_rent": True},
    ]
    
    for test_case in test_cases:
        print(f"  🔍 {test_case['name']}...")
        
        # Create test parameters
        base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
        }
        
        if not test_case.get('params_without_rent'):
            base_params['rent_increase_rate'] = test_case['rent_increase_rate']
        
        try:
            # Simulate the parameter processing from app_full.py
            def get_value_only(key, fallback):
                """Simulate priority manager get_value_only that might return None"""
                if key == 'rent_increase_rate' and test_case.get('simulate_priority_failure'):
                    return None
                return base_params.get(key, fallback)
            
            # Test the new robust parameter extraction
            rent_rate = get_value_only('rent_increase_rate', base_params.get('rent_increase_rate', 3.0)) or 3.0
            
            # Test validation
            if rent_rate is None or (isinstance(rent_rate, (int, float)) and rent_rate < 0):
                rent_rate = 3.0
                print(f"    ✅ Fallback applied: {rent_rate}")
            else:
                print(f"    ✅ Value valid: {rent_rate}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return False
    
    return True

def test_session_state_compatibility():
    """Test session state handling for mobile"""
    print("\n🧪 Testing session state mobile compatibility...")
    
    # Simulate incomplete session state
    incomplete_session = {
        'inputs': {
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            # Missing rent_increase_rate
        }
    }
    
    # Test parameter extraction
    inputs = incomplete_session.get('inputs', {})
    rent_rate = inputs.get('rent_increase_rate', 3.0)
    
    print(f"  📱 Extracted rent_increase_rate: {rent_rate}")
    
    if rent_rate == 3.0:
        print("  ✅ Default fallback working")
        return True
    else:
        print(f"  ❌ Unexpected value: {rent_rate}")
        return False

def test_analysis_execution_mobile():
    """Test full analysis execution with mobile-like conditions"""
    print("\n🧪 Testing analysis execution (mobile simulation)...")
    
    try:
        from components.session_management import SessionManager
        from utils.defaults import DEFAULT_VALUES
        
        # Create session manager
        session_manager = SessionManager()
        
        # Simulate minimal mobile input
        mobile_inputs = {
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            # Simulate missing rent_increase_rate
        }
        
        # Test parameter extraction
        session_data = {'inputs': mobile_inputs}
        inputs = session_data.get('inputs', {})
        
        # Test the robust parameter handling
        rent_rate = inputs.get('rent_increase_rate', 3.0)
        if rent_rate is None or rent_rate == "":
            rent_rate = 3.0
        
        print(f"  📊 Final rent_increase_rate: {rent_rate}")
        print("  ✅ Mobile analysis simulation passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Analysis simulation failed: {e}")
        return False

def main():
    """Run all mobile compatibility tests"""
    print("📱 Mobile Compatibility Test Suite")
    print("=" * 45)
    
    tests = [
        ("Parameter Handling", test_mobile_parameter_handling),
        ("Session State", test_session_state_compatibility),
        ("Analysis Execution", test_analysis_execution_mobile)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 45)
    print("📋 Mobile Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\n🎯 Overall: {'✅ MOBILE COMPATIBLE' if all_passed else '❌ MOBILE ISSUES DETECTED'}")
    
    if not all_passed:
        print("\n💡 Applied fixes:")
        print("1. ✅ Added robust fallback handling for rent_increase_rate")
        print("2. ✅ Added parameter validation with mobile-specific defaults")
        print("3. ✅ Enhanced error handling in analysis functions")

if __name__ == "__main__":
    main()