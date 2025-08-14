#!/usr/bin/env python3
"""
Demo script showing API integration in action
Run this alongside the Streamlit app to see live rates
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.address_api_handler import get_address_api_handler
from data.international_data import get_international_provider
import logging

logging.basicConfig(level=logging.INFO)


async def demo_address_api_integration():
    """Demonstrate the address API integration with live rates"""
    
    print("🏠 Rent vs Buy Tool - Live API Integration Demo")
    print("=" * 60)
    
    handler = get_address_api_handler()
    
    # Test addresses that should trigger live API calls
    test_addresses = [
        "São Paulo, Brazil",
        "Rio de Janeiro, Brazil", 
        "Tel Aviv, Israel",
        "Jerusalem, Israel",
        "New York, NY, USA",
        "London, UK"
    ]
    
    print("\n🌍 Testing international address API integration...")
    
    for address in test_addresses:
        print(f"\n📍 Testing: {address}")
        print("-" * 40)
        
        try:
            # This simulates what happens when user enters an address
            result = await handler.handle_address_change(address)
            
            if result['updated']:
                print(f"✅ API Update Successful")
                print(f"   Rates fetched: {result.get('rates_fetched', {})}")
                print(f"   Fields updated: {sum(result.get('field_updates', {}).values())} fields")
                
                # Show current field values after API update
                current_values = handler.get_current_field_values()
                
                # Show interest rate specifically
                if 'interest_rate' in current_values:
                    rate_info = current_values['interest_rate']
                    print(f"   Interest Rate: {rate_info['value']:.3f}%")
                    print(f"   Source: {rate_info['source']}")
                    print(f"   Priority: {rate_info['priority_level']}")
                    
                    if rate_info['source'].endswith('_live'):
                        print(f"   🔴 LIVE RATE from API!")
                    else:
                        print(f"   📊 Static/Default rate")
                        
            else:
                print(f"❌ No update: {result.get('reason', 'Unknown')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n" + "=" * 60)
    print("🎯 Summary:")
    print("• Brazil addresses should show LIVE rates from BCB API")
    print("• Israel addresses should show static rates (API needs research)")
    print("• US addresses should show LIVE rates from FRED API") 
    print("• Other countries should show static rates")
    print("\n🌐 Open http://localhost:8501 to see this in the web interface!")


async def demo_live_rate_comparison():
    """Show live vs static rate comparison"""
    
    print("\n🔄 Live vs Static Rate Comparison")
    print("=" * 50)
    
    provider = get_international_provider()
    
    # Test Brazil - should show live vs static difference
    try:
        print("📊 Brazil (São Paulo):")
        
        # Get static rates
        static_data = provider.get_international_estimates("São Paulo, Brazil")
        static_rate = static_data['estimates']['interest_rate']
        print(f"   Static Rate: {static_rate}%")
        
        # Get live rates  
        live_data = await provider.get_international_estimates_with_live_rates("São Paulo, Brazil")
        live_rate = live_data['estimates']['interest_rate']
        live_used = live_data['metadata'].get('live_rate_used', False)
        
        print(f"   Live Rate: {live_rate}%")
        print(f"   Live API Used: {'Yes' if live_used else 'No'}")
        
        if live_used and abs(live_rate - static_rate) > 0.1:
            difference = live_rate - static_rate
            print(f"   🔥 Rate Difference: {difference:+.3f}%")
            print(f"   💡 This difference affects your buy vs rent decision!")
            
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    try:
        print("Starting API integration demo...")
        asyncio.run(demo_address_api_integration())
        asyncio.run(demo_live_rate_comparison())
        
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")