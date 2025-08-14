#!/usr/bin/env python3
"""
Test script to debug session state with user overrides
"""

import sys
import os
sys.path.append('src')

import asyncio
from data.address_api_handler import get_address_api_handler, reset_address_api_handler
from data.data_priority_manager import get_data_priority_manager

async def test_with_user_overrides():
    print("=== Testing with Existing User Overrides ===")
    
    # Get clean handler and priority manager
    handler = reset_address_api_handler()
    priority_manager = get_data_priority_manager()
    
    # 1. Simulate user making a manual change first
    print("\n1. User manually sets interest rate to 8.5%")
    priority_manager.set_user_override('interest_rate', 8.5, 'user_manual_input')
    
    value_data = priority_manager.get_value('interest_rate')
    print(f"   Interest rate after user override: {value_data}")
    
    # 2. Now try to process US address (which should clear and reset)
    print("\n2. Processing 'NY USA' (should clear overrides and set API data)...")
    result = await handler.handle_address_change('NY USA')
    print(f"   Result: {result}")
    
    value_data = priority_manager.get_value('interest_rate')
    print(f"   Interest rate after API update: {value_data}")
    
    # 3. Test Argentina (should clear everything)
    print("\n3. Processing 'Argentina' (should clear all data)...")
    result = await handler.handle_address_change('Argentina')
    print(f"   Result: {result}")
    
    value_data = priority_manager.get_value('interest_rate')
    print(f"   Interest rate after Argentina: {value_data}")

if __name__ == "__main__":
    asyncio.run(test_with_user_overrides())