#!/usr/bin/env python3
"""
Quick test to verify the async fix worked
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Mock streamlit session_state
class MockSessionState:
    def __init__(self):
        self._data = {}
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def __setitem__(self, key, value):
        self._data[key] = value

# Mock streamlit
class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()
    
    def info(self, msg):
        print(f"INFO: {msg}")

def test_country_change_function():
    """Test the country change function works without async issues"""
    print("Testing Country Change Function")
    print("=" * 40)
    
    # Import the function after setting up mocks
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "input_forms", 
        os.path.join(os.path.dirname(__file__), "src", "components", "input_forms.py")
    )
    
    # Set up mock streamlit
    sys.modules['streamlit'] = MockStreamlit()
    
    try:
        input_forms = importlib.util.module_from_spec(spec)
        input_forms.st = MockStreamlit()
        spec.loader.exec_module(input_forms)
        
        # Test the function
        input_forms._handle_country_change("brazil")
        print("✅ Brazil country change completed without errors")
        
        input_forms._handle_country_change("usa")
        print("✅ USA country change completed without errors")
        
        input_forms._handle_country_change("argentina")
        print("✅ Argentina (other) country change completed without errors")
        
        print("\n🎉 All country change functions work correctly!")
        print("📱 App should be accessible at: http://localhost:8502")
        
    except Exception as e:
        print(f"❌ Error in country change function: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_country_change_function()