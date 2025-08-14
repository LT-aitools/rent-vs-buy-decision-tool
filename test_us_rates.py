#!/usr/bin/env python3
"""
Test script to debug US rate handling
"""

import sys
import os
sys.path.append('src')

import asyncio
from data.address_api_handler import get_address_api_handler, reset_address_api_handler
from data.data_priority_manager import get_data_priority_manager

async def test_us_rates():
    print("=== Testing US Rate Handling ===")
    
    # Reset everything for clean test
    handler = reset_address_api_handler()
    priority_manager = get_data_priority_manager()
    
    print("\n1. Initial state:")
    try:
        value_data = priority_manager.get_value('interest_rate')
        print(f"   Interest rate: {value_data}")
    except ValueError:
        print("   Interest rate: Not set")
    
    print("\n2. Processing 'NY USA'...")
    result = await handler.handle_address_change('NY USA')
    print(f"   Result: {result}")
    
    print("\n3. State after processing:")
    try:
        value_data = priority_manager.get_value('interest_rate')
        print(f"   Interest rate: {value_data}")
    except ValueError:
        print("   Interest rate: Not set")
    
    # Check other fields too
    fields_to_check = ['interest_rate', 'interest_rate_15_year', 'federal_funds_rate']
    print("\n4. All rate fields:")
    for field in fields_to_check:
        try:
            value_data = priority_manager.get_value(field)
            print(f"   {field}: {value_data}")
        except ValueError:
            print(f"   {field}: Not set")

if __name__ == "__main__":
    asyncio.run(test_us_rates())