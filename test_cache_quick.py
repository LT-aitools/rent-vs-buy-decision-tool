"""
Quick cache performance test - focused on core functionality
"""

import asyncio
import sys
import os
import tempfile
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.shared.interfaces import DataRequest
from src.data.data_integration_service import create_data_integration_service

async def test_cache_quick():
    """Quick test of cache functionality"""
    print("⚡ Quick Cache Performance Test")
    print("=" * 50)
    
    # Create temporary cache
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_cache_path = temp_file.name
    temp_file.close()
    
    try:
        # Configure service without extensive warmup
        config = {
            'cache': {
                'persistent_cache_path': temp_cache_path,
                'memory_cache_size_mb': 10.0,
                'default_ttl_hours': 24.0
            },
            'market_api': {
                'timeout': 5,
                'max_retries': 1,
                'fallback_enabled': True
            }
        }
        
        service = create_data_integration_service(config)
        
        # Initialize without warmup
        print("🔧 Initializing service (no warmup)...")
        await service.initialize()
        print("✅ Service ready")
        
        # Test location
        test_location = "San Francisco, CA"
        request = DataRequest(
            location=test_location,
            zip_code=None,
            data_types=['rental', 'property'],
            max_age_hours=24,
            fallback_to_cache=True
        )
        
        # Request 1: First time (should be cache miss)
        print(f"\n📊 Request 1: First request for {test_location}")
        start_time = time.time()
        data1 = await service.get_market_data(request)
        time1 = (time.time() - start_time) * 1000
        print(f"⏱️  Response time: {time1:.1f}ms")
        print(f"📝 Data sources: {data1.data_sources}")
        print(f"🎯 Confidence: {data1.confidence_score:.2f}")
        
        # Request 2: Repeat immediately (should hit cache)
        print(f"\n📊 Request 2: Repeat request for {test_location}")
        start_time = time.time()
        data2 = await service.get_market_data(request)
        time2 = (time.time() - start_time) * 1000
        print(f"⏱️  Response time: {time2:.1f}ms")
        print(f"📝 Data sources: {data2.data_sources}")
        print(f"🎯 Confidence: {data2.confidence_score:.2f}")
        
        # Request 3: Another repeat (should hit cache again)
        print(f"\n📊 Request 3: Third request for {test_location}")
        start_time = time.time()
        data3 = await service.get_market_data(request)
        time3 = (time.time() - start_time) * 1000
        print(f"⏱️  Response time: {time3:.1f}ms")
        print(f"📝 Data sources: {data3.data_sources}")
        print(f"🎯 Confidence: {data3.confidence_score:.2f}")
        
        # Test different location
        test_location2 = "Seattle, WA"
        request2 = DataRequest(
            location=test_location2,
            zip_code=None,
            data_types=['rental', 'property'],
            max_age_hours=24,
            fallback_to_cache=True
        )
        
        print(f"\n📊 Request 4: New location {test_location2}")
        start_time = time.time()
        data4 = await service.get_market_data(request2)
        time4 = (time.time() - start_time) * 1000
        print(f"⏱️  Response time: {time4:.1f}ms")
        print(f"📝 Data sources: {data4.data_sources}")
        
        # Request 5: Repeat new location (should hit cache)
        print(f"\n📊 Request 5: Repeat {test_location2}")
        start_time = time.time()
        data5 = await service.get_market_data(request2)
        time5 = (time.time() - start_time) * 1000
        print(f"⏱️  Response time: {time5:.1f}ms")
        print(f"📝 Data sources: {data5.data_sources}")
        
        # Get cache statistics
        cache_stats = await service.cache_manager.get_performance_stats()
        
        print(f"\n" + "=" * 50)
        print("📈 CACHE ANALYSIS")
        print("=" * 50)
        
        # Analyze response times
        times = [time1, time2, time3, time4, time5]
        avg_time = sum(times) / len(times)
        
        # Identify likely cache hits (faster responses)
        cache_threshold = 5.0  # 5ms threshold for cache hits
        likely_cache_hits = sum(1 for t in times if t < cache_threshold)
        likely_cache_misses = len(times) - likely_cache_hits
        
        print(f"\n⏱️  Response Time Analysis:")
        print(f"• Request 1 (SF, first): {time1:.1f}ms")
        print(f"• Request 2 (SF, repeat): {time2:.1f}ms {'⚡ CACHE HIT' if time2 < cache_threshold else '🔄 CACHE MISS'}")
        print(f"• Request 3 (SF, repeat): {time3:.1f}ms {'⚡ CACHE HIT' if time3 < cache_threshold else '🔄 CACHE MISS'}")
        print(f"• Request 4 (SEA, first): {time4:.1f}ms")
        print(f"• Request 5 (SEA, repeat): {time5:.1f}ms {'⚡ CACHE HIT' if time5 < cache_threshold else '🔄 CACHE MISS'}")
        print(f"• Average response time: {avg_time:.1f}ms")
        
        print(f"\n📊 Cache Performance:")
        print(f"• Official hit rate: {cache_stats.hit_rate:.2%}")
        print(f"• Official hits: {cache_stats.hit_count}")
        print(f"• Official misses: {cache_stats.miss_count}")
        print(f"• Total requests: {cache_stats.total_requests}")
        print(f"• Cache entries: {cache_stats.entry_count}")
        print(f"• Cache size: {cache_stats.cache_size_mb:.2f}MB")
        
        # Performance improvement analysis
        repeat_times = [time2, time3, time5]  # Repeat requests
        first_times = [time1, time4]  # First-time requests
        
        avg_repeat = sum(repeat_times) / len(repeat_times) if repeat_times else 0
        avg_first = sum(first_times) / len(first_times) if first_times else 0
        
        speedup = avg_first / avg_repeat if avg_repeat > 0 else 1.0
        
        print(f"\n🚀 Performance Improvement:")
        print(f"• Average first request: {avg_first:.1f}ms")
        print(f"• Average repeat request: {avg_repeat:.1f}ms")
        print(f"• Cache speedup: {speedup:.1f}x faster")
        
        # Success criteria
        cache_working = cache_stats.entry_count > 0
        hit_rate_ok = cache_stats.hit_rate >= 0.4  # At least 40% for this test
        cache_faster = speedup > 1.0
        
        print(f"\n✅ SUCCESS CRITERIA:")
        print(f"• Cache entries created: {'✅ PASS' if cache_working else '❌ FAIL'} ({cache_stats.entry_count} entries)")
        print(f"• Hit rate acceptable: {'✅ PASS' if hit_rate_ok else '❌ FAIL'} ({cache_stats.hit_rate:.1%})")
        print(f"• Cache provides speedup: {'✅ PASS' if cache_faster else '❌ FAIL'} ({speedup:.1f}x)")
        
        overall_success = cache_working and hit_rate_ok and cache_faster
        
        print(f"\n🏆 OVERALL RESULT: {'✅ CACHE WORKING' if overall_success else '⚠️ NEEDS WORK'}")
        
        if overall_success:
            estimated_production_hit_rate = min(0.85, cache_stats.hit_rate * 2)  # Estimate with warmup
            print(f"🎉 Cache system is functional!")
            print(f"📈 Estimated production hit rate: {estimated_production_hit_rate:.1%} (with warmup)")
        else:
            print("🔧 Cache system needs additional optimization")
        
        await service.shutdown()
        return overall_success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            os.unlink(temp_cache_path)
        except:
            pass

if __name__ == "__main__":
    success = asyncio.run(test_cache_quick())
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Cache test completed")
    sys.exit(0 if success else 1)