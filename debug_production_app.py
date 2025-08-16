#!/usr/bin/env python3
"""
Debug script to test if app_full.py loads correctly
This simulates what app.py does in production
"""

import sys
import os

# Add src directory to path (like app.py does)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, current_dir)
sys.path.insert(0, src_dir)

print("🔍 Testing app_full.py execution...")
print(f"📁 Current dir: {current_dir}")
print(f"📁 Src dir: {src_dir}")

try:
    # Try to load app_full.py the same way app.py does
    app_full_path = os.path.join(current_dir, 'src', 'app_full.py')
    
    if os.path.exists(app_full_path):
        print(f"✅ app_full.py found at: {app_full_path}")
        
        # Test if we can read the file
        with open(app_full_path, 'r') as f:
            content = f.read()
            print(f"✅ File readable, {len(content)} characters")
        
        # Test imports that app_full.py needs
        print("\n🔍 Testing critical imports...")
        
        critical_imports = [
            "streamlit",
            "pandas", 
            "numpy",
            "plotly",
            "datetime"
        ]
        
        for module in critical_imports:
            try:
                __import__(module)
                print(f"  ✅ {module}")
            except ImportError as e:
                print(f"  ❌ {module}: {e}")
        
        # Test custom imports
        print("\n🔍 Testing custom imports...")
        custom_imports = [
            "components.session_management",
            "calculations.npv_analysis", 
            "utils.defaults",
            "data.data_priority_manager"
        ]
        
        for module in custom_imports:
            try:
                __import__(module)
                print(f"  ✅ {module}")
            except ImportError as e:
                print(f"  ❌ {module}: {e}")
                
        print("\n🧪 Testing parameter extraction logic...")
        
        # Test the specific rent_increase_rate handling
        test_inputs = {
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            # Missing rent_increase_rate to test fallback
        }
        
        # Simulate the parameter extraction logic
        rent_rate = test_inputs.get('rent_increase_rate', 3.0)
        if rent_rate is None or rent_rate == "":
            rent_rate = 3.0
        
        print(f"  📊 rent_increase_rate test: {rent_rate}")
        
        # Test the enhanced validation logic
        critical_params = ['purchase_price', 'current_annual_rent', 'rent_increase_rate']
        analysis_params = {
            'purchase_price': test_inputs.get('purchase_price'),
            'current_annual_rent': test_inputs.get('current_annual_rent'),
            'rent_increase_rate': rent_rate
        }
        
        for param in critical_params:
            value = analysis_params.get(param)
            if value is None or (isinstance(value, (int, float)) and value < 0):
                if param == 'rent_increase_rate':
                    analysis_params[param] = 3.0
                    print(f"  🔧 Fixed {param}: using default 3.0")
                    
        print(f"  ✅ Final parameters: {analysis_params}")
        
    else:
        print(f"❌ app_full.py NOT found at: {app_full_path}")
        
except Exception as e:
    print(f"💥 Error testing app_full.py: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("🎯 Conclusion:")
print("If all imports show ✅, then app_full.py should work in production")
print("If there are ❌ errors, those need to be fixed for production to work")