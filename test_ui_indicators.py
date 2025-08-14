#!/usr/bin/env python3
"""
Test script to demonstrate what UI indicators will show for different locations
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.address_api_handler import get_address_api_handler
from data.data_priority_manager import reset_data_priority_manager


async def demo_ui_indicators():
    """Demo what the UI indicators will look like for different locations"""
    
    print("🖥️  UI Indicator Demo - What You'll See in Localhost")
    print("=" * 70)
    
    test_locations = [
        "Warsaw, Poland",
        "São Paulo, Brazil", 
        "Tel Aviv, Israel",
        "London, UK",
        "New York, NY, USA"
    ]
    
    for location in test_locations:
        print(f"\n📍 Location: {location}")
        print("-" * 50)
        
        # Reset data to simulate fresh load
        reset_data_priority_manager()
        handler = get_address_api_handler()
        handler.priority_manager = reset_data_priority_manager()
        
        # Process address
        result = await handler.handle_address_change(location)
        
        if result['updated']:
            # Show what the UI indicator will display
            field_values = handler.get_current_field_values()
            
            if 'interest_rate' in field_values:
                rate_info = field_values['interest_rate']
                metadata = rate_info.get('metadata', {})
                source = rate_info.get('source', '')
                value = rate_info.get('value', 0)
                
                # Simulate what _show_api_indicator would display
                print(f"🌐 API Updated Indicator Will Show:")
                
                # Determine what extra info will be shown
                data_date = metadata.get('data_date', '')
                live_rate_used = metadata.get('live_rate_used', False)
                api_available = metadata.get('api_available', False)
                
                if live_rate_used:
                    extra_info = "🔴 LIVE API"
                    color = "#4CAF50"  # Green for live
                elif data_date:
                    extra_info = f"📅 Data from {data_date}"
                    color = "#2196F3"  # Blue for static with date
                else:
                    extra_info = "📊 Static data"
                    color = "#FF9800"  # Orange for unknown date
                
                # Format source name
                source_display = source.replace('_', ' ').replace('fred api', 'Federal Reserve').replace('international data', 'Central Bank Data')
                
                print(f"   ┌─────────────────────────────────────────────────┐")
                print(f"   │ 🌐 API Updated: {source_display}")
                print(f"   │ Value: {value}% • {extra_info}")
                print(f"   └─────────────────────────────────────────────────┘")
                
                # Show what this means
                if live_rate_used:
                    print(f"   ✨ This rate is LIVE from the central bank API!")
                elif data_date:
                    print(f"   📊 This is static data from {data_date}")
                    days_old = "approximately 0 days old"  # Since our data is from 2024-08-14
                    print(f"   ⏰ Rate is {days_old}")
                else:
                    print(f"   ⚠️  Data date unknown - needs investigation")
                    
            else:
                print(f"   ❌ No interest rate data available")
        else:
            print(f"   ❌ No API update for this location")
    
    print(f"\n" + "=" * 70)
    print("🎯 Summary of What You'll See in the UI:")
    print("• 🔴 LIVE API = Real-time rates from central bank")
    print("• 📅 Data from [date] = Static rates with known date") 
    print("• 📊 Static data = Fallback rates")
    print("• Color coding helps distinguish live vs static data")
    print("\n🌐 Open http://localhost:8501 and enter these addresses to see the indicators!")


if __name__ == "__main__":
    try:
        asyncio.run(demo_ui_indicators())
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")