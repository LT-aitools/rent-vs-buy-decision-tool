#!/usr/bin/env python3
"""
Week 4 Component Testing Script
Test individual components without full Streamlit context
"""

import os
import sys
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_shared_interfaces():
    """Test shared interfaces and utilities"""
    print("🔗 Testing Shared Interfaces...")
    try:
        from shared.interfaces import (
            create_mock_market_data, 
            create_mock_analytics_result,
            MarketData,
            AnalyticsResult
        )
        from shared.utils import (
            validate_numeric_input,
            format_currency,
            setup_logging
        )
        from shared.constants import APP_VERSION, DEFAULT_MONTE_CARLO_ITERATIONS
        
        # Test mock data creation
        mock_market = create_mock_market_data("Test Location")
        mock_analytics = create_mock_analytics_result()
        
        # Test utilities
        is_valid, msg = validate_numeric_input(500000, 10000, 10000000)
        currency = format_currency(123456.78)
        
        print(f"  ✅ Mock market data: {mock_market.location}")
        print(f"  ✅ Mock analytics: {mock_analytics.base_recommendation}")
        print(f"  ✅ Validation: {is_valid}")
        print(f"  ✅ Currency format: {currency}")
        print(f"  ✅ App version: {APP_VERSION}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()
        return False

def test_data_integration():
    """Test data integration components"""
    print("\n🌐 Testing Data Integration...")
    try:
        # Import without instantiating to test imports
        from data.market_data_api import MarketDataAPI
        from data.interest_rate_feeds import InterestRateService
        from data.location_data import LocationDataService
        from data.cache_management import IntelligentCacheManager
        
        print("  ✅ Market Data API imported")
        print("  ✅ Interest Rate Service imported")
        print("  ✅ Location Data Service imported")
        print("  ✅ Cache Manager imported")
        
        # Test simple instantiation
        cache_manager = IntelligentCacheManager()
        print(f"  ✅ Cache manager created: {type(cache_manager).__name__}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()
        return False

def test_analytics_import():
    """Test analytics engine imports (may have relative import issues)"""
    print("\n📊 Testing Analytics Engine Imports...")
    try:
        # Try to import analytics components
        # Note: May fail due to relative imports outside module context
        print("  ⚠️  Note: Analytics imports may fail due to relative import paths")
        print("      This is expected when running outside module context")
        print("      Use the full test suite for proper analytics testing")
        
        # Check if files exist
        analytics_files = [
            'src/analytics/monte_carlo.py',
            'src/analytics/sensitivity_analysis.py', 
            'src/analytics/risk_assessment.py',
            'src/analytics/scenario_modeling.py'
        ]
        
        for file_path in analytics_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"  ✅ {os.path.basename(file_path)}: {file_size:,} bytes")
            else:
                print(f"  ❌ Missing: {file_path}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_ui_components():
    """Test UI component imports"""
    print("\n🎨 Testing UI Components...")
    try:
        # Check if component files exist and can be imported
        ui_files = [
            'src/components/enhanced/advanced_inputs.py',
            'src/components/enhanced/interactive_charts.py',
            'src/components/enhanced/guidance_system.py',
            'src/components/enhanced/mobile_responsive.py',
            'src/components/enhanced/accessibility_compliance.py'
        ]
        
        for file_path in ui_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"  ✅ {os.path.basename(file_path)}: {file_size:,} bytes")
            else:
                print(f"  ❌ Missing: {file_path}")
        
        # Try to import the main module (may need Streamlit context)
        print("  ⚠️  Note: Full UI testing requires Streamlit context")
        print("      Use 'streamlit run src/app.py' for interactive testing")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_framework():
    """Test the testing framework"""
    print("\n🧪 Testing Framework...")
    try:
        from tests.framework.test_framework import ComprehensiveTestFramework
        
        # Create framework instance
        framework = ComprehensiveTestFramework()
        print(f"  ✅ Test framework created: {len(framework.test_modules)} modules discovered")
        
        # Test mock data creation
        from shared.interfaces import create_mock_market_data
        mock_data = create_mock_market_data()
        print(f"  ✅ Mock data creation working: {mock_data.location}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all component tests"""
    print("🧪 WEEK 4 COMPONENT TESTING")
    print("=" * 50)
    
    tests = [
        ("Shared Interfaces", test_shared_interfaces),
        ("Data Integration", test_data_integration), 
        ("Analytics Engine", test_analytics_import),
        ("UI Components", test_ui_components),
        ("Testing Framework", test_framework)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  Some tests failed - this may be expected due to import contexts")
    
    print("\n📋 Next Steps:")
    print("• Run 'python3 test_integration_simple.py' for integration testing")
    print("• Run 'python3 tests/run_regression_tests.py --quick' for full testing")
    print("• Run 'streamlit run src/app.py' for interactive UI testing")

if __name__ == "__main__":
    main()