#!/usr/bin/env python3
"""
Debug script to check what data is being exported
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Mock Streamlit session state with sample user data
class MockSessionState:
    def __init__(self):
        self.data = {
            'purchase_price': 850000,  # User's actual value
            'current_annual_rent': 45000,  # User's actual value
            'analysis_period': 20,  # User's actual value
            'down_payment_percent': 25.0,  # User's actual value
            'interest_rate': 6.5,  # User's actual value
        }
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def __contains__(self, key):
        return key in self.data
    
    def __getitem__(self, key):
        return self.data[key]

# Mock streamlit
import streamlit as st
st.session_state = MockSessionState()

# Test the export data preparation
from components.session_management import SessionManager

def test_export_data():
    """Test what data gets exported"""
    print("=== Testing Export Data ===")
    
    manager = SessionManager()
    export_data = manager.export_session_data()
    
    print(f"Export data keys: {list(export_data.keys())}")
    print(f"Inputs keys: {list(export_data['inputs'].keys())}")
    
    # Check key values
    key_fields = ['purchase_price', 'current_annual_rent', 'analysis_period', 'down_payment_percent', 'interest_rate']
    
    print("\n=== Key Field Values ===")
    for field in key_fields:
        session_value = st.session_state.get(field)
        export_value = export_data['inputs'].get(field)
        print(f"{field}:")
        print(f"  Session State: {session_value}")
        print(f"  Export Data:   {export_value}")
        print(f"  Match: {session_value == export_value}")
        print()

if __name__ == "__main__":
    test_export_data()