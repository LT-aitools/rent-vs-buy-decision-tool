#!/usr/bin/env python3
"""
Test user override functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.data_priority_manager import get_data_priority_manager, reset_data_priority_manager

def test_user_override_flow():
    """Test the flow of API data -> User override"""
    
    print("🧪 Testing User Override Flow")
    print("=" * 40)
    
    # Reset and get priority manager
    reset_data_priority_manager()
    priority_manager = get_data_priority_manager()
    
    field_name = 'market_appreciation_rate'
    
    # Step 1: Set API data (like from Poland)
    print("Step 1: Set API data")
    priority_manager.set_api_data(
        field_name,
        6.5,
        'international_data_for_Warsaw, Poland_(2024-08-14)',
        metadata={'country': 'Poland', 'data_date': '2024-08-14'}
    )
    
    field_data = priority_manager.get_value(field_name)
    print(f"   Value: {field_data['value']}%")
    print(f"   Source: {field_data['source']}")
    print(f"   User Modified: {field_data['user_modified']}")
    print(f"   Priority: {field_data['priority_level']}")
    print("   → Should show BLUE 'API Updated' indicator")
    
    # Step 2: User changes the value
    print(f"\nStep 2: User changes value to 8.8%")
    priority_manager.set_user_override(field_name, 8.8, 'user_manual_input')
    
    field_data = priority_manager.get_value(field_name)
    print(f"   Value: {field_data['value']}%")
    print(f"   Source: {field_data['source']}")
    print(f"   User Modified: {field_data['user_modified']}")
    print(f"   Priority: {field_data['priority_level']}")
    print("   → Should show ORANGE 'User Override' indicator")
    
    print(f"\n✅ Test Complete!")
    print("The UI should now switch from blue API indicator to orange User Override indicator")


if __name__ == "__main__":
    test_user_override_flow()