#!/usr/bin/env python3
"""
Comprehensive Validation of 2D Sensitivity Analysis NPV Values
This test verifies that all NPV values in the table are calculated correctly.
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_2d_sensitivity_npv_accuracy():
    """Test that all NPV values in the 2D sensitivity table are calculated correctly"""
    
    print("🔍 Testing 2D Sensitivity Analysis NPV Value Accuracy")
    print("=" * 60)
    
    try:
        from calculations.two_dimensional_sensitivity import calculate_2d_sensitivity_analysis
        from calculations.npv_analysis import calculate_npv_comparison
        
        # Test parameters
        base_params = {
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
            'property_upgrade_cycle': 30
        }
        
        print("📊 Testing 3x3 sensitivity table...")
        
        # Run 2D sensitivity analysis with small range for testing
        x_metric = 'interest_rate'
        y_metric = 'market_appreciation_rate'
        x_range = [-1.0, 0.0, 1.0]
        y_range = [-1.0, 0.0, 1.0]
        
        result = calculate_2d_sensitivity_analysis(
            base_params=base_params,
            x_metric=x_metric,
            y_metric=y_metric,
            x_range=x_range,
            y_range=y_range
        )
        
        if not result:
            print("❌ 2D sensitivity calculation failed")
            return False
        
        print(f"✅ 2D sensitivity calculation completed")
        print(f"   Base NPV: ${result['base_npv_difference']:,.0f}")
        print(f"   Table size: {result['table_size']}")
        
        # Verify each cell by manually calculating NPV for those parameters
        print("\n🔍 Verifying individual cell calculations...")
        
        errors = []
        verified_count = 0
        
        for i, y_change in enumerate(y_range):
            for j, x_change in enumerate(x_range):
                # Create modified parameters for this cell
                test_params = base_params.copy()
                
                # Apply the parameter changes
                x_base_value = base_params[x_metric]
                y_base_value = base_params[y_metric]
                
                test_params[x_metric] = x_base_value + x_change
                test_params[y_metric] = y_base_value + y_change
                
                # Calculate NPV manually for verification
                manual_npv_result = calculate_npv_comparison(**test_params)
                manual_npv = manual_npv_result['npv_difference']
                
                # Get NPV from 2D table
                table_npv = result['npv_differences'][i][j]
                
                # Check if they match (within $1 tolerance for rounding)
                difference = abs(manual_npv - table_npv)
                
                if difference > 1.0:
                    errors.append({
                        'cell': f"({x_change:+.1f}%, {y_change:+.1f}%)",
                        'manual_npv': manual_npv,
                        'table_npv': table_npv,
                        'difference': difference,
                        'x_param': f"{x_metric}={test_params[x_metric]:.1f}",
                        'y_param': f"{y_metric}={test_params[y_metric]:.1f}"
                    })
                else:
                    verified_count += 1
                
                print(f"   Cell ({x_change:+.1f}%, {y_change:+.1f}%): Manual=${manual_npv:,.0f}, Table=${table_npv:,.0f}, Diff=${difference:.0f}")
        
        print(f"\n📋 Verification Results:")
        print(f"   ✅ Verified cells: {verified_count}/{len(x_range) * len(y_range)}")
        print(f"   ❌ Error cells: {len(errors)}")
        
        if errors:
            print("\n❌ Errors found in these cells:")
            for error in errors:
                print(f"   {error['cell']}: {error['x_param']}, {error['y_param']}")
                print(f"      Manual NPV: ${error['manual_npv']:,.0f}")
                print(f"      Table NPV:  ${error['table_npv']:,.0f}")
                print(f"      Difference: ${error['difference']:,.0f}")
                print()
            return False
        else:
            print("✅ All NPV values in the table are calculated correctly!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parameter_range_accuracy():
    """Test that parameter changes are applied correctly across the range"""
    
    print("\n🔧 Testing Parameter Range Application")
    print("=" * 40)
    
    try:
        from calculations.two_dimensional_sensitivity import calculate_2d_sensitivity_analysis
        from calculations.npv_analysis import calculate_npv_comparison
        
        # Test with different metrics and ranges
        base_params = {
            'purchase_price': 600000,
            'current_annual_rent': 30000,
            'down_payment_pct': 20.0,
            'interest_rate': 6.0,
            'loan_term': 25,
            'transaction_costs': 30000,
            'rent_increase_rate': 2.5,
            'analysis_period': 20,
            'cost_of_capital': 7.5,
            'property_tax_rate': 1.5,
            'property_tax_escalation': 2.5,
            'insurance_cost': 6000,
            'annual_maintenance': 12000,
            'property_management': 0,
            'capex_reserve_rate': 2.0,
            'obsolescence_risk_rate': 0.75,
            'inflation_rate': 2.5,
            'land_value_pct': 30.0,
            'market_appreciation_rate': 4.0,
            'depreciation_period': 39,
            'corporate_tax_rate': 30.0,
            'interest_deductible': True,
            'property_tax_deductible': True,
            'rent_deductible': True,
            'moving_costs': 5000,
            'space_improvement_cost': 10000,
            'future_expansion_year': 'Never',
            'additional_space_needed': 0,
            'current_space_needed': 0,
            'ownership_property_size': 0,
            'rental_property_size': 0,
            'subletting_potential': False,
            'subletting_rate': 0,
            'subletting_space_sqm': 0,
            'property_upgrade_cycle': 30
        }
        
        # Test rent increase rate vs inflation rate
        x_metric = 'rent_increase_rate'
        y_metric = 'inflation_rate'
        
        print(f"Testing {x_metric} vs {y_metric}")
        print(f"Base {x_metric}: {base_params[x_metric]:.1f}%")
        print(f"Base {y_metric}: {base_params[y_metric]:.1f}%")
        
        # Test specific corner cases
        test_cases = [
            (-0.5, -0.5, "Both parameters decrease"),
            (0.0, 0.0, "Base case (no changes)"),
            (+1.0, +1.0, "Both parameters increase"),
            (-1.0, +1.0, "X decreases, Y increases"),
            (+1.0, -1.0, "X increases, Y decreases")
        ]
        
        all_passed = True
        
        for x_change, y_change, description in test_cases:
            print(f"\n🧪 Testing: {description}")
            print(f"   Changes: {x_metric}{x_change:+.1f}%, {y_metric}{y_change:+.1f}%")
            
            # Manual calculation
            test_params = base_params.copy()
            test_params[x_metric] = base_params[x_metric] + x_change
            test_params[y_metric] = base_params[y_metric] + y_change
            
            manual_result = calculate_npv_comparison(**test_params)
            manual_npv = manual_result['npv_difference']
            
            print(f"   Expected parameter values:")
            print(f"     {x_metric}: {test_params[x_metric]:.1f}%")
            print(f"     {y_metric}: {test_params[y_metric]:.1f}%")
            print(f"   Manual NPV calculation: ${manual_npv:,.0f}")
            
            # 2D sensitivity calculation for this specific case
            result = calculate_2d_sensitivity_analysis(
                base_params=base_params,
                x_metric=x_metric,
                y_metric=y_metric,
                x_range=[x_change],
                y_range=[y_change]
            )
            
            if result:
                table_npv = result['npv_differences'][0][0]
                difference = abs(manual_npv - table_npv)
                
                print(f"   2D sensitivity NPV:     ${table_npv:,.0f}")
                print(f"   Difference:             ${difference:.0f}")
                
                if difference > 1.0:
                    print(f"   ❌ MISMATCH! Difference too large")
                    all_passed = False
                else:
                    print(f"   ✅ MATCH! Values are consistent")
            else:
                print(f"   ❌ 2D calculation failed")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Parameter range test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Running Comprehensive 2D Sensitivity Analysis Validation")
    print()
    
    success = True
    
    # Run NPV accuracy test
    if not test_2d_sensitivity_npv_accuracy():
        success = False
    
    # Run parameter range test
    if not test_parameter_range_accuracy():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL VALIDATION TESTS PASSED!")
        print("\n✅ The 2D sensitivity analysis NPV calculations are accurate")
        print("✅ All table values are calculated correctly")
        print("✅ Parameter changes are applied properly")
        print("✅ Results are consistent with manual calculations")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
        print("\n🔧 The 2D sensitivity analysis may need fixes")
    
    print("=" * 60)