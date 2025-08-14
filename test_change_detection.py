#!/usr/bin/env python3
"""
Test the user interaction change detection logic
This simulates the specific bug scenario where API updates were being marked as user modifications
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Mock streamlit session_state for testing
class MockSessionState:
    def __init__(self):
        self._data = {}
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __getitem__(self, key):
        return self._data[key]

# Mock streamlit module
class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()

# Replace the streamlit import in the module
sys.modules['streamlit'] = MockStreamlit()

from data.data_priority_manager import reset_data_priority_manager

# Import the function we want to test
# We need to import this after setting up the mock
import importlib.util
spec = importlib.util.spec_from_file_location(
    "input_forms", 
    os.path.join(os.path.dirname(__file__), "src", "components", "input_forms.py")
)
input_forms = importlib.util.module_from_spec(spec)

# Set up the mock streamlit in the input_forms module
input_forms.st = MockStreamlit()
spec.loader.exec_module(input_forms)

def test_api_update_not_marked_as_user_change():
    """Test that API updates are NOT marked as user changes"""
    print("\n=== Testing API Update Detection ===")
    
    # Reset for clean test
    priority_manager = reset_data_priority_manager()
    st = MockStreamlit()
    
    # Set up initial state
    field_name = 'interest_rate'
    prev_value = 7.0
    api_value = 12.5  # Brazil rate
    
    # Simulate API update in progress
    st.session_state['_api_update_in_progress'] = True
    
    # Test the change detection function
    is_user_change = input_forms._is_user_interaction_change(field_name, api_value, prev_value)
    
    print(f"Previous value: {prev_value}")
    print(f"New value (from API): {api_value}")
    print(f"API update in progress: {st.session_state.get('_api_update_in_progress')}")
    print(f"Detected as user interaction: {is_user_change}")
    
    # This should be False (not a user interaction)
    if not is_user_change:
        print("✅ PASS: API update correctly NOT marked as user interaction")
        return True
    else:
        print("❌ FAIL: API update incorrectly marked as user interaction")
        return False

def test_actual_user_change_detected():
    """Test that actual user changes ARE marked as user changes"""
    print("\n=== Testing User Change Detection ===")
    
    # Reset for clean test
    priority_manager = reset_data_priority_manager()
    st = MockStreamlit()
    
    # Set up state - NOT in API update mode
    field_name = 'interest_rate'
    prev_value = 7.0
    user_value = 8.5  # User manually changed it
    
    # No API update in progress
    st.session_state['_api_update_in_progress'] = False
    
    # Test the change detection function
    is_user_change = input_forms._is_user_interaction_change(field_name, user_value, prev_value)
    
    print(f"Previous value: {prev_value}")
    print(f"New value (user input): {user_value}")
    print(f"API update in progress: {st.session_state.get('_api_update_in_progress')}")
    print(f"Detected as user interaction: {is_user_change}")
    
    # This should be True (is a user interaction)
    if is_user_change:
        print("✅ PASS: User change correctly marked as user interaction")
        return True
    else:
        print("❌ FAIL: User change incorrectly NOT marked as user interaction")
        return False

def test_api_value_match_detection():
    """Test that changes matching API values are detected as API updates"""
    print("\n=== Testing API Value Match Detection ===")
    
    # Reset for clean test
    priority_manager = reset_data_priority_manager()
    st = MockStreamlit()
    
    field_name = 'interest_rate'
    api_value = 12.5
    prev_value = 7.0
    
    # Set up API data in priority manager
    priority_manager.set_api_data(field_name, api_value, 'international_data')
    
    # No API update flag set, but the value matches API data
    st.session_state['_api_update_in_progress'] = False
    
    # Test the change detection function
    is_user_change = input_forms._is_user_interaction_change(field_name, api_value, prev_value)
    
    print(f"Previous value: {prev_value}")
    print(f"New value: {api_value}")
    print(f"API data value: {api_value}")
    print(f"Values match API data: True")
    print(f"Detected as user interaction: {is_user_change}")
    
    # This should be False (matches API data, likely programmatic)
    if not is_user_change:
        print("✅ PASS: Value matching API data correctly NOT marked as user interaction")
        return True
    else:
        print("❌ FAIL: Value matching API data incorrectly marked as user interaction")
        return False

def main():
    """Run all change detection tests"""
    print("Testing User Interaction Change Detection Logic")
    print("=" * 60)
    
    results = []
    
    # Test API updates are not marked as user changes
    results.append(("API Update Detection", test_api_update_not_marked_as_user_change()))
    
    # Test actual user changes are marked correctly
    results.append(("User Change Detection", test_actual_user_change_detected()))
    
    # Test API value matching detection
    results.append(("API Value Match Detection", test_api_value_match_detection()))
    
    print("\n" + "=" * 60)
    print("RESULTS:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Change detection logic is working correctly!")
        print("- API updates are not marked as user interactions")
        print("- User changes are properly detected")
        print("- Value matching API data is handled correctly")
    else:
        print("\n🚨 Issues detected in change detection logic")

if __name__ == "__main__":
    main()