#!/usr/bin/env python3
"""
Test script for international API integration
Tests Brazil and Israel central bank API connectivity
"""

import asyncio
import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.international_api_feeds import test_international_apis, get_international_api_feeds
from data.international_data import get_international_provider

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_brazil_api():
    """Test Brazil Central Bank API"""
    print("\n=== Testing Brazil Central Bank API ===")
    
    try:
        feeds = get_international_api_feeds()
        brazil_rates = await feeds.get_live_rates('brazil')
        
        if brazil_rates:
            print(f"✅ Brazil API working!")
            print(f"   Selic Rate: {brazil_rates['base_rate']}%")
            print(f"   Mortgage Rate: {brazil_rates['mortgage_rate']}%")
            print(f"   Source: {brazil_rates['source']}")
            print(f"   Timestamp: {brazil_rates['timestamp']}")
            return True
        else:
            print("❌ Brazil API failed - no data returned")
            return False
            
    except Exception as e:
        print(f"❌ Brazil API error: {e}")
        return False


async def test_israel_api():
    """Test Israel Central Bank API"""
    print("\n=== Testing Israel Central Bank API ===")
    
    try:
        feeds = get_international_api_feeds()
        israel_rates = await feeds.get_live_rates('israel')
        
        if israel_rates:
            print(f"✅ Israel API working!")
            print(f"   BOI Rate: {israel_rates['base_rate']}%")
            print(f"   Mortgage Rate: {israel_rates['mortgage_rate']}%")
            print(f"   Source: {israel_rates['source']}")
            print(f"   Timestamp: {israel_rates['timestamp']}")
            return True
        else:
            print("❌ Israel API failed - no data returned")
            return False
            
    except Exception as e:
        print(f"❌ Israel API error: {e}")
        return False


async def test_integration():
    """Test integration with international data provider"""
    print("\n=== Testing Integration ===")
    
    try:
        provider = get_international_provider()
        
        # Test Brazil
        brazil_data = await provider.get_international_estimates_with_live_rates("São Paulo, Brazil")
        if brazil_data['estimates']:
            live_used = brazil_data['metadata'].get('live_rate_used', False)
            rate = brazil_data['estimates']['interest_rate']
            source = brazil_data['metadata']['source']
            
            print(f"📍 São Paulo, Brazil:")
            print(f"   Interest Rate: {rate}%")
            print(f"   Live Rate Used: {'Yes' if live_used else 'No'}")
            print(f"   Source: {source}")
        
        # Test Israel
        israel_data = await provider.get_international_estimates_with_live_rates("Tel Aviv, Israel")
        if israel_data['estimates']:
            live_used = israel_data['metadata'].get('live_rate_used', False)
            rate = israel_data['estimates']['interest_rate']
            source = israel_data['metadata']['source']
            
            print(f"📍 Tel Aviv, Israel:")
            print(f"   Interest Rate: {rate}%")
            print(f"   Live Rate Used: {'Yes' if live_used else 'No'}")
            print(f"   Source: {source}")
            
        return True
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False


async def main():
    """Main test function"""
    print("🧪 International API Integration Test")
    print("=" * 50)
    
    # Test API connectivity
    api_results = await test_international_apis()
    print(f"\nAPI Connectivity Test Results:")
    print(f"  Brazil: {'✅ Connected' if api_results.get('brazil') else '❌ Failed'}")
    print(f"  Israel: {'✅ Connected' if api_results.get('israel') else '❌ Failed'}")
    
    # Test individual APIs
    brazil_success = await test_brazil_api()
    israel_success = await test_israel_api()
    
    # Test integration
    integration_success = await test_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Summary:")
    print(f"  Brazil API: {'✅ Pass' if brazil_success else '❌ Fail'}")
    print(f"  Israel API: {'✅ Pass' if israel_success else '❌ Fail'}")
    print(f"  Integration: {'✅ Pass' if integration_success else '❌ Fail'}")
    
    overall_success = brazil_success or israel_success  # At least one should work
    print(f"  Overall: {'✅ Pass' if overall_success else '❌ Fail'}")
    
    # Cleanup
    try:
        feeds = get_international_api_feeds()
        await feeds.close()
    except:
        pass
    
    return 0 if overall_success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)