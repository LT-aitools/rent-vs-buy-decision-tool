#!/usr/bin/env python3
"""
Test Dashboard Integration of 2D Sensitivity Analysis
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_dashboard_integration():
    """Test that the dashboard can properly integrate with 2D sensitivity analysis"""
    
    print("🔧 Testing Dashboard Integration for 2D Sensitivity Analysis")
    print("=" * 60)
    
    try:
        # Test imports from main app perspective
        print("📦 Testing imports...")
        
        from calculations.two_dimensional_sensitivity import (
            calculate_2d_sensitivity_analysis,
            format_2d_sensitivity_for_streamlit,
            get_available_sensitivity_metrics
        )
        print("✅ Successfully imported 2D sensitivity functions")
        
        # Test getting metrics
        metrics = get_available_sensitivity_metrics()
        print(f"✅ Available metrics: {list(metrics.keys())}")
        print(f"   Display names: {list(metrics.values())}")
        
        # Test analysis results structure (simulate what dashboard receives)
        mock_analysis_results = {
            'purchase_price': 500000,
            'current_annual_rent': 24000,
            'down_payment_pct': 30.0,
            'interest_rate': 5.0,
            'loan_term': 20,
            'transaction_costs': 25000,
            'rent_increase_rate': 3.0,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.2,
            'property_tax_escalation': 2.0,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'property_management': 0,
            'capex_reserve_rate': 1.5,
            'obsolescence_risk_rate': 0.5,
            'inflation_rate': 3.0,
            'land_value_pct': 25.0,
            'market_appreciation_rate': 3.0,
            'depreciation_period': 39,
            'corporate_tax_rate': 25.0,
            'interest_deductible': True,
            'property_tax_deductible': True,
            'rent_deductible': True,
            'moving_costs': 0.0,
            'space_improvement_cost': 0.0,
            'future_expansion_year': 'Never',
            'additional_space_needed': 0,
            'current_space_needed': 0,
            'ownership_property_size': 0,
            'rental_property_size': 0,
            'subletting_potential': False,
            'subletting_rate': 0,
            'subletting_space_sqm': 0,
            'property_upgrade_cycle': 30,
            'npv_difference': 150000,
            'recommendation': 'BUY',
            'confidence': 'Medium'
        }
        print("✅ Created mock analysis results")
        
        # Test parameter extraction (simulating dashboard behavior)
        base_params = {
            key: mock_analysis_results.get(key, 0) 
            for key in [
                'purchase_price', 'current_annual_rent', 'down_payment_pct',
                'interest_rate', 'loan_term', 'transaction_costs',
                'rent_increase_rate', 'analysis_period', 'cost_of_capital',
                'property_tax_rate', 'property_tax_escalation', 'insurance_cost',
                'annual_maintenance', 'property_management', 'capex_reserve_rate',
                'obsolescence_risk_rate', 'inflation_rate', 'land_value_pct',
                'market_appreciation_rate', 'depreciation_period', 'corporate_tax_rate'
            ]
        }
        
        # Add boolean and string parameters
        base_params.update({
            'interest_deductible': mock_analysis_results.get('interest_deductible', True),
            'property_tax_deductible': mock_analysis_results.get('property_tax_deductible', True),
            'rent_deductible': mock_analysis_results.get('rent_deductible', True),
            'moving_costs': mock_analysis_results.get('moving_costs', 0.0),
            'space_improvement_cost': mock_analysis_results.get('space_improvement_cost', 0.0),
            'future_expansion_year': mock_analysis_results.get('future_expansion_year', 'Never'),
            'additional_space_needed': mock_analysis_results.get('additional_space_needed', 0),
            'current_space_needed': mock_analysis_results.get('current_space_needed', 0),
            'ownership_property_size': mock_analysis_results.get('ownership_property_size', 0),
            'rental_property_size': mock_analysis_results.get('rental_property_size', 0),
            'subletting_potential': mock_analysis_results.get('subletting_potential', False),
            'subletting_rate': mock_analysis_results.get('subletting_rate', 0),
            'subletting_space_sqm': mock_analysis_results.get('subletting_space_sqm', 0),
            'property_upgrade_cycle': mock_analysis_results.get('property_upgrade_cycle', 30)
        })
        
        print("✅ Extracted base parameters for analysis")
        
        # Test 2D sensitivity calculation
        print("📊 Testing 2D sensitivity calculation...")
        x_metric = 'interest_rate'
        y_metric = 'market_appreciation_rate'
        
        result = calculate_2d_sensitivity_analysis(
            base_params=base_params,
            x_metric=x_metric,
            y_metric=y_metric,
            x_range=[-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5],
            y_range=[-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
        )
        
        if result:
            print(f"✅ 2D sensitivity calculation successful")
            print(f"   X metric: {result['x_metric_display']}")
            print(f"   Y metric: {result['y_metric_display']}")
            print(f"   Calculation time: {result['calculation_time']:.3f}s")
            print(f"   Table size: {result['table_size']}")
            print(f"   Base NPV difference: ${result['base_npv_difference']:,.0f}")
            
            # Test formatting for Streamlit
            print("🎨 Testing Streamlit formatting...")
            formatted = format_2d_sensitivity_for_streamlit(result)
            
            print(f"✅ Streamlit formatting successful")
            print(f"   Number of columns: {formatted['num_columns']}")
            print(f"   Number of rows: {formatted['num_rows']}")
            print(f"   Base NPV display: {formatted['base_npv']}")
            
            # Show a sample of the table data
            if formatted['table_data']:
                print("📋 Sample table data:")
                first_row = formatted['table_data'][0]
                print(f"   First row label: {first_row['y_label']} {first_row['y_change']}")
                print(f"   First value: {first_row.get('col_0', 'N/A')}")
            
            print("\n🎯 Dashboard Integration Test Results:")
            print("   ✅ Imports working correctly")
            print("   ✅ Parameter extraction successful")
            print("   ✅ 2D calculation working")
            print("   ✅ Streamlit formatting working")
            print("   ✅ Ready for dashboard integration!")
            
        else:
            print("❌ 2D sensitivity calculation failed")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_metric_selection():
    """Test that metric selection and validation works correctly"""
    
    print("\n🔧 Testing Metric Selection Logic")
    print("=" * 40)
    
    try:
        from calculations.two_dimensional_sensitivity import get_available_sensitivity_metrics
        
        metrics = get_available_sensitivity_metrics()
        metric_options = list(metrics.values())
        metric_keys = list(metrics.keys())
        
        print(f"Available options: {metric_options}")
        print(f"Corresponding keys: {metric_keys}")
        
        # Test metric selection logic
        x_metric_display = metric_options[1]  # Interest Rate
        y_metric_display = metric_options[3]  # Market Appreciation Rate
        
        x_metric = metric_keys[metric_options.index(x_metric_display)]
        y_metric = metric_keys[metric_options.index(y_metric_display)]
        
        print(f"✅ X-axis selection: {x_metric_display} -> {x_metric}")
        print(f"✅ Y-axis selection: {y_metric_display} -> {y_metric}")
        
        # Test validation
        if x_metric == y_metric:
            print("❌ Validation failed: same metric selected")
            return False
        else:
            print("✅ Validation passed: different metrics selected")
        
        return True
        
    except Exception as e:
        print(f"❌ Metric selection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running Dashboard Integration Tests for 2D Sensitivity Analysis")
    print()
    
    success = True
    
    # Run main integration test
    if not test_dashboard_integration():
        success = False
    
    # Run metric selection test
    if not test_metric_selection():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED - Dashboard integration ready!")
        print("\n✨ The 2D sensitivity analysis has been successfully integrated")
        print("   and is ready to replace the old sensitivity analysis in the dashboard.")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
    
    print("=" * 60)