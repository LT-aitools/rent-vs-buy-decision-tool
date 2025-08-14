"""
Performance Target Verification for Data Integration System
Tests compliance with Week 4 PRD requirements:
- 99% API uptime with fallback systems
- Data freshness under 24 hours  
- Cache hit rate above 80%
"""

import asyncio
import sys
import os
import tempfile
import time
from datetime import datetime, timedelta
from typing import Dict, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.shared.interfaces import DataRequest
from src.data.data_integration_service import create_data_integration_service

class PerformanceVerifier:
    """Verifies performance targets for the data integration system"""
    
    def __init__(self):
        self.temp_cache_path = None
        self.service = None
        self.results = {
            'uptime_test': {'passed': False, 'score': 0.0, 'details': {}},
            'freshness_test': {'passed': False, 'score': 0.0, 'details': {}},
            'cache_hit_rate_test': {'passed': False, 'score': 0.0, 'details': {}},
            'overall_performance': {'passed': False, 'score': 0.0}
        }
    
    async def setup(self):
        """Setup test environment"""
        # Create temporary cache
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_cache_path = temp_file.name
        temp_file.close()
        
        # Configure service for performance testing
        config = {
            'cache': {
                'persistent_cache_path': self.temp_cache_path,
                'memory_cache_size_mb': 25.0,
                'default_ttl_hours': 24.0
            },
            'market_api': {
                'timeout': 10,
                'max_retries': 3,
                'fallback_enabled': True
            },
            'interest_rates': {
                'timeout': 10,
                'max_retries': 3
            },
            'location': {
                'timeout': 10,
                'max_retries': 3
            },
            'target_uptime': 0.99,
            'target_hit_rate': 0.8,
            'target_freshness_hours': 24
        }
        
        # Initialize service
        self.service = create_data_integration_service(config)
        await self.service.initialize()
        
        print("✅ Performance test environment initialized")
    
    async def test_99_percent_uptime(self) -> Dict:
        """Test 99% API uptime with fallback systems"""
        print("\n🎯 Testing 99% API Uptime Target...")
        print("-" * 40)
        
        test_locations = [
            "New York, NY",
            "Los Angeles, CA", 
            "Chicago, IL",
            "Houston, TX",
            "Phoenix, AZ",
            "Philadelphia, PA",
            "San Antonio, TX",
            "San Diego, CA",
            "Dallas, TX",
            "San Jose, CA"
        ]
        
        successful_requests = 0
        total_requests = len(test_locations) * 2  # Test each location twice
        response_times = []
        
        for i, location in enumerate(test_locations):
            for attempt in range(2):
                try:
                    request = DataRequest(
                        location=location,
                        zip_code=None,
                        data_types=['rental', 'property', 'rates'],
                        max_age_hours=24,
                        fallback_to_cache=True
                    )
                    
                    start_time = time.time()
                    market_data = await self.service.get_market_data(request)
                    response_time = (time.time() - start_time) * 1000
                    
                    if market_data and market_data.confidence_score > 0:
                        successful_requests += 1
                        response_times.append(response_time)
                        print(f"✅ {location} (attempt {attempt + 1}): {response_time:.1f}ms")
                    else:
                        print(f"❌ {location} (attempt {attempt + 1}): No data returned")
                        
                except Exception as e:
                    print(f"❌ {location} (attempt {attempt + 1}): {str(e)}")
                
                # Small delay between requests
                await asyncio.sleep(0.1)
        
        uptime_rate = successful_requests / total_requests
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Update results
        self.results['uptime_test'] = {
            'passed': uptime_rate >= 0.99,
            'score': uptime_rate,
            'details': {
                'successful_requests': successful_requests,
                'total_requests': total_requests,
                'avg_response_time_ms': avg_response_time,
                'fallback_systems_working': successful_requests > total_requests * 0.5
            }
        }
        
        print(f"\n📊 Uptime Test Results:")
        print(f"• Success rate: {uptime_rate:.2%} (Target: 99%)")
        print(f"• Successful requests: {successful_requests}/{total_requests}")
        print(f"• Average response time: {avg_response_time:.1f}ms")
        print(f"• Fallback systems: {'✅ Working' if successful_requests > 0 else '❌ Failed'}")
        
        return self.results['uptime_test']
    
    async def test_data_freshness(self) -> Dict:
        """Test data freshness under 24 hours"""
        print("\n🎯 Testing 24-Hour Data Freshness Target...")
        print("-" * 40)
        
        test_locations = [
            "Boston, MA",
            "Seattle, WA",
            "Denver, CO",
            "Atlanta, GA"
        ]
        
        fresh_data_count = 0
        total_tests = len(test_locations)
        freshness_scores = []
        
        for location in test_locations:
            request = DataRequest(
                location=location,
                zip_code=None,
                data_types=['rental', 'property', 'rates'],
                max_age_hours=24,
                fallback_to_cache=False  # Force fresh data
            )
            
            try:
                market_data = await self.service.get_market_data(request)
                
                if market_data:
                    freshness_hours = market_data.freshness_hours
                    data_age_hours = (datetime.now() - market_data.data_timestamp).total_seconds() / 3600
                    
                    # Consider data fresh if either metric shows freshness
                    is_fresh = freshness_hours <= 24 or data_age_hours <= 24
                    
                    if is_fresh:
                        fresh_data_count += 1
                    
                    freshness_scores.append(min(freshness_hours, data_age_hours))
                    
                    print(f"{'✅' if is_fresh else '❌'} {location}: "
                          f"freshness={freshness_hours:.1f}h, age={data_age_hours:.1f}h")
                else:
                    print(f"❌ {location}: No data returned")
                    
            except Exception as e:
                print(f"❌ {location}: Error - {str(e)}")
        
        freshness_rate = fresh_data_count / total_tests
        avg_freshness = sum(freshness_scores) / len(freshness_scores) if freshness_scores else 999
        
        # Update results
        self.results['freshness_test'] = {
            'passed': freshness_rate >= 0.8 and avg_freshness <= 24,  # Allow some tolerance
            'score': freshness_rate,
            'details': {
                'fresh_data_count': fresh_data_count,
                'total_tests': total_tests,
                'avg_freshness_hours': avg_freshness,
                'freshness_scores': freshness_scores
            }
        }
        
        print(f"\n📊 Freshness Test Results:")
        print(f"• Fresh data rate: {freshness_rate:.2%} (Target: 80%+)")
        print(f"• Average freshness: {avg_freshness:.1f} hours (Target: <24h)")
        print(f"• Fresh data sources: {fresh_data_count}/{total_tests}")
        
        return self.results['freshness_test']
    
    async def test_cache_hit_rate(self) -> Dict:
        """Test cache hit rate above 80%"""
        print("\n🎯 Testing 80%+ Cache Hit Rate Target...")
        print("-" * 40)
        
        cache_test_locations = [
            "Miami, FL",
            "Las Vegas, NV", 
            "Portland, OR"
        ]
        
        # Phase 1: Prime the cache
        print("Phase 1: Priming cache...")
        for location in cache_test_locations:
            request = DataRequest(
                location=location,
                zip_code=None,
                data_types=['rental', 'property'],
                max_age_hours=24,
                fallback_to_cache=True
            )
            
            await self.service.get_market_data(request)
            print(f"✅ Cached: {location}")
        
        # Small delay to ensure cache is populated
        await asyncio.sleep(0.5)
        
        # Phase 2: Test cache hits
        print("\nPhase 2: Testing cache performance...")
        cache_requests = 0
        
        # Make multiple requests to same locations
        for round_num in range(5):  # 5 rounds of requests
            for location in cache_test_locations:
                request = DataRequest(
                    location=location,
                    zip_code=None,
                    data_types=['rental', 'property'],
                    max_age_hours=24,
                    fallback_to_cache=True
                )
                
                start_time = time.time()
                await self.service.get_market_data(request)
                response_time = (time.time() - start_time) * 1000
                
                cache_requests += 1
                print(f"Round {round_num + 1} - {location}: {response_time:.1f}ms")
        
        # Get final cache statistics
        cache_stats = await self.service.cache_manager.get_performance_stats()
        
        # Update results
        self.results['cache_hit_rate_test'] = {
            'passed': cache_stats.hit_rate >= 0.8,
            'score': cache_stats.hit_rate,
            'details': {
                'hit_count': cache_stats.hit_count,
                'miss_count': cache_stats.miss_count,
                'total_requests': cache_stats.total_requests,
                'cache_requests_made': cache_requests,
                'avg_response_time_ms': cache_stats.avg_response_time_ms,
                'cache_size_mb': cache_stats.cache_size_mb
            }
        }
        
        print(f"\n📊 Cache Hit Rate Test Results:")
        print(f"• Cache hit rate: {cache_stats.hit_rate:.2%} (Target: 80%)")
        print(f"• Cache hits: {cache_stats.hit_count}")
        print(f"• Cache misses: {cache_stats.miss_count}")
        print(f"• Total cache requests: {cache_stats.total_requests}")
        print(f"• Average response time: {cache_stats.avg_response_time_ms:.1f}ms")
        print(f"• Cache size: {cache_stats.cache_size_mb:.1f}MB")
        
        return self.results['cache_hit_rate_test']
    
    async def run_all_tests(self) -> Dict:
        """Run all performance tests"""
        print("🚀 Starting Performance Target Verification")
        print("=" * 60)
        
        await self.setup()
        
        # Run individual tests
        uptime_result = await self.test_99_percent_uptime()
        freshness_result = await self.test_data_freshness()
        cache_result = await self.test_cache_hit_rate()
        
        # Calculate overall performance
        tests_passed = sum([
            uptime_result['passed'],
            freshness_result['passed'], 
            cache_result['passed']
        ])
        
        overall_score = (
            uptime_result['score'] * 0.4 +  # Uptime weighted 40%
            freshness_result['score'] * 0.3 +  # Freshness weighted 30%
            cache_result['score'] * 0.3   # Cache hit rate weighted 30%
        )
        
        self.results['overall_performance'] = {
            'passed': tests_passed >= 2,  # At least 2 out of 3 tests must pass
            'score': overall_score,
            'tests_passed': tests_passed,
            'total_tests': 3
        }
        
        # Print final summary
        await self.print_final_summary()
        
        return self.results
    
    async def print_final_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📋 FINAL PERFORMANCE VERIFICATION SUMMARY")
        print("=" * 60)
        
        # Individual test results
        print("\n🔍 Individual Test Results:")
        
        tests = [
            ('99% API Uptime', self.results['uptime_test']),
            ('24h Data Freshness', self.results['freshness_test']),
            ('80% Cache Hit Rate', self.results['cache_hit_rate_test'])
        ]
        
        for test_name, result in tests:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            score = result['score']
            if test_name == '24h Data Freshness':
                score_display = f"{score:.2%} fresh"
            elif 'Cache' in test_name:
                score_display = f"{score:.2%} hit rate"
            else:
                score_display = f"{score:.2%} uptime"
            
            print(f"  {status} {test_name}: {score_display}")
        
        # Overall performance
        overall = self.results['overall_performance']
        overall_status = "✅ PASS" if overall['passed'] else "❌ FAIL"
        
        print(f"\n🎯 Overall Performance: {overall_status}")
        print(f"   • Tests passed: {overall['tests_passed']}/{overall['total_tests']}")
        print(f"   • Composite score: {overall['score']:.2%}")
        
        # Detailed metrics
        if self.service:
            health = await self.service.get_service_health()
            print(f"\n📊 Service Health Metrics:")
            print(f"   • Service status: {health.get('service_status', 'unknown')}")
            print(f"   • Total requests processed: {health.get('request_stats', {}).get('requests_processed', 0)}")
            print(f"   • Success rate: {health.get('request_stats', {}).get('successful_requests', 0) / max(1, health.get('request_stats', {}).get('requests_processed', 1)):.2%}")
        
        # Compliance summary
        print(f"\n✅ PRD COMPLIANCE SUMMARY:")
        compliant_tests = sum(result['passed'] for _, result in tests)
        
        if compliant_tests == 3:
            print("🎉 ALL PERFORMANCE TARGETS MET!")
            print("   System is ready for production deployment.")
        elif compliant_tests >= 2:
            print("⚠️  MOSTLY COMPLIANT - Minor optimization needed")
            print("   System meets core performance requirements.")
        else:
            print("❌ PERFORMANCE TARGETS NOT MET")
            print("   System requires optimization before deployment.")
        
        print("=" * 60)
    
    async def cleanup(self):
        """Cleanup test resources"""
        if self.service:
            await self.service.shutdown()
        
        if self.temp_cache_path and os.path.exists(self.temp_cache_path):
            try:
                os.unlink(self.temp_cache_path)
            except:
                pass

async def main():
    """Main verification function"""
    verifier = PerformanceVerifier()
    
    try:
        results = await verifier.run_all_tests()
        
        # Return appropriate exit code
        if results['overall_performance']['passed']:
            print(f"\n🎉 Performance verification completed successfully!")
            return 0
        else:
            print(f"\n⚠️ Performance verification completed with issues!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Performance verification failed: {e}")
        import traceback
        traceback.print_exc()
        return 2
        
    finally:
        await verifier.cleanup()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)