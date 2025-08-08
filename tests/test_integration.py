"""
Integration tests for complete calculation workflows
Tests end-to-end scenarios and mathematical accuracy against Business PRD
"""

import pytest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculations.npv_analysis import (
    calculate_npv_comparison,
    calculate_ownership_cash_flows,
    calculate_rental_cash_flows,
    calculate_break_even_analysis
)
from calculations.mortgage import calculate_mortgage_payment
from calculations.terminal_value import calculate_terminal_value
from calculations.amortization import generate_amortization_schedule


class TestIntegrationScenarios:
    """Integration test suite for complete analysis workflows"""
    
    @pytest.fixture
    def standard_scenario_params(self):
        """Standard test scenario parameters"""
        return {
            'purchase_price': 500000,
            'down_payment_pct': 30,
            'interest_rate': 5.0,
            'loan_term': 20,
            'transaction_costs': 25000,
            'current_annual_rent': 30000,
            'rent_increase_rate': 3.0,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.2,
            'property_tax_escalation': 2.0,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'market_appreciation_rate': 3.0,
            'land_value_pct': 25.0,
            'depreciation_period': 39
        }
    
    def test_complete_npv_analysis_workflow(self, standard_scenario_params):
        """Test complete NPV analysis workflow"""
        result = calculate_npv_comparison(**standard_scenario_params)
        
        # Verify all required outputs are present
        required_fields = [
            'ownership_npv', 'rental_npv', 'npv_difference',
            'ownership_initial_investment', 'rental_initial_investment',
            'terminal_value_advantage', 'recommendation', 'confidence'
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
        
        # Verify NPV difference calculation
        calculated_diff = result['ownership_npv'] - result['rental_npv']
        assert abs(calculated_diff - result['npv_difference']) < 1.0
        
        # Verify recommendation is valid
        assert result['recommendation'] in ['BUY', 'RENT', 'MARGINAL']
        assert result['confidence'] in ['High', 'Medium', 'Low']
        
    def test_buy_favorable_scenario(self):
        """Test scenario strongly favoring purchase"""
        params = {
            'purchase_price': 400000,
            'down_payment_pct': 30,
            'interest_rate': 4.0,  # Low interest rate
            'loan_term': 30,
            'transaction_costs': 20000,
            'current_annual_rent': 40000,  # High rent
            'rent_increase_rate': 5.0,  # High rent increases
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.0,  # Low taxes
            'market_appreciation_rate': 4.0  # Good appreciation
        }
        
        result = calculate_npv_comparison(**params)
        
        # Should favor buying
        assert result['npv_difference'] > 0
        assert result['recommendation'] in ['BUY']
        
    def test_rent_favorable_scenario(self):
        """Test scenario strongly favoring rental"""
        params = {
            'purchase_price': 800000,  # High purchase price
            'down_payment_pct': 20,
            'interest_rate': 8.0,  # High interest rate
            'loan_term': 15,
            'transaction_costs': 50000,  # High transaction costs
            'current_annual_rent': 20000,  # Low rent
            'rent_increase_rate': 1.0,  # Low rent increases
            'analysis_period': 10,  # Short analysis period
            'cost_of_capital': 12.0,  # High cost of capital
            'property_tax_rate': 3.0,  # High taxes
            'market_appreciation_rate': 1.0  # Low appreciation
        }
        
        result = calculate_npv_comparison(**params)
        
        # Should favor renting
        assert result['npv_difference'] < 0
        assert result['recommendation'] == 'RENT'
        
    def test_ownership_cash_flow_integration(self, standard_scenario_params):
        """Test ownership cash flow calculation integration"""
        cash_flows = calculate_ownership_cash_flows(
            purchase_price=standard_scenario_params['purchase_price'],
            down_payment_pct=standard_scenario_params['down_payment_pct'],
            interest_rate=standard_scenario_params['interest_rate'],
            loan_term=standard_scenario_params['loan_term'],
            analysis_period=standard_scenario_params['analysis_period'],
            property_tax_rate=standard_scenario_params['property_tax_rate'],
            property_tax_escalation=standard_scenario_params['property_tax_escalation'],
            insurance_cost=standard_scenario_params['insurance_cost'],
            annual_maintenance=standard_scenario_params['annual_maintenance']
        )
        
        assert len(cash_flows) == standard_scenario_params['analysis_period']
        
        # Verify Year-1 indexing: Year 1 should have base costs
        year_1 = cash_flows[0]
        assert year_1['year'] == 1
        assert year_1['property_taxes'] == 500000 * 0.012  # Base property tax
        assert year_1['insurance'] == 5000  # Base insurance
        
        # Verify escalation in Year 2
        year_2 = cash_flows[1]
        assert year_2['property_taxes'] > year_1['property_taxes']  # Should escalate
        assert year_2['insurance'] > year_1['insurance']  # Should escalate
        
    def test_rental_cash_flow_integration(self, standard_scenario_params):
        """Test rental cash flow calculation integration"""
        cash_flows = calculate_rental_cash_flows(
            current_annual_rent=standard_scenario_params['current_annual_rent'],
            rent_increase_rate=standard_scenario_params['rent_increase_rate'],
            analysis_period=standard_scenario_params['analysis_period']
        )
        
        assert len(cash_flows) == standard_scenario_params['analysis_period']
        
        # Verify Year-1 indexing for rent
        year_1 = cash_flows[0]
        assert year_1['annual_rent'] == standard_scenario_params['current_annual_rent']
        
        # Verify rent escalation
        year_2 = cash_flows[1]
        expected_year_2_rent = 30000 * 1.03
        assert abs(year_2['annual_rent'] - expected_year_2_rent) < 1.0
        
    def test_terminal_value_integration(self, standard_scenario_params):
        """Test terminal value calculation integration"""
        # Calculate mortgage details first
        mortgage_info = calculate_mortgage_payment(
            standard_scenario_params['purchase_price'],
            standard_scenario_params['down_payment_pct'],
            standard_scenario_params['interest_rate'],
            standard_scenario_params['loan_term']
        )
        
        # Generate amortization schedule to get final balance
        schedule = generate_amortization_schedule(
            mortgage_info['loan_amount'],
            mortgage_info['annual_payment'],
            standard_scenario_params['interest_rate'],
            standard_scenario_params['loan_term']
        )
        
        # Get remaining balance at end of analysis period
        if standard_scenario_params['analysis_period'] <= len(schedule):
            remaining_balance = schedule[standard_scenario_params['analysis_period'] - 1]['ending_balance']
        else:
            remaining_balance = 0.0  # Loan paid off
        
        # Calculate terminal value
        terminal = calculate_terminal_value(
            standard_scenario_params['purchase_price'],
            standard_scenario_params['land_value_pct'],
            standard_scenario_params['market_appreciation_rate'],
            standard_scenario_params['depreciation_period'],
            standard_scenario_params['analysis_period'],
            remaining_balance
        )
        
        # Verify terminal value makes sense
        assert terminal['terminal_property_value'] > standard_scenario_params['purchase_price']
        assert terminal['net_property_equity'] > 0
        
    def test_break_even_analysis_integration(self, standard_scenario_params):
        """Test break-even analysis integration"""
        # Get cash flows for both scenarios
        ownership_flows = calculate_ownership_cash_flows(
            purchase_price=standard_scenario_params['purchase_price'],
            down_payment_pct=standard_scenario_params['down_payment_pct'],
            interest_rate=standard_scenario_params['interest_rate'],
            loan_term=standard_scenario_params['loan_term'],
            analysis_period=standard_scenario_params['analysis_period'],
            property_tax_rate=standard_scenario_params['property_tax_rate'],
            property_tax_escalation=standard_scenario_params['property_tax_escalation'],
            insurance_cost=standard_scenario_params['insurance_cost'],
            annual_maintenance=standard_scenario_params['annual_maintenance']
        )
        
        rental_flows = calculate_rental_cash_flows(
            current_annual_rent=standard_scenario_params['current_annual_rent'],
            rent_increase_rate=standard_scenario_params['rent_increase_rate'],
            analysis_period=standard_scenario_params['analysis_period']
        )
        
        # Calculate break-even analysis
        break_even = calculate_break_even_analysis(ownership_flows, rental_flows)
        
        # Verify break-even results
        assert 'break_even_year' in break_even
        assert 'cumulative_cost_difference' in break_even
        assert 'yearly_differences' in break_even
        assert len(break_even['yearly_differences']) == standard_scenario_params['analysis_period']
        
    def test_edge_case_100_percent_down_payment(self):
        """Test complete analysis with 100% down payment"""
        params = {
            'purchase_price': 500000,
            'down_payment_pct': 100,  # No financing
            'interest_rate': 5.0,
            'loan_term': 20,
            'transaction_costs': 25000,
            'current_annual_rent': 30000,
            'rent_increase_rate': 3.0,
            'analysis_period': 25,
            'cost_of_capital': 8.0
        }
        
        result = calculate_npv_comparison(**params)
        
        # Should complete without errors
        assert 'ownership_npv' in result
        assert result['ownership_initial_investment'] == 525000  # Price + transaction costs
        
        # Terminal value should be full property equity (no loan balance)
        assert result['ownership_terminal_value'] > 0
        
    def test_edge_case_zero_interest_rate(self):
        """Test complete analysis with 0% interest rate"""
        params = {
            'purchase_price': 500000,
            'down_payment_pct': 30,
            'interest_rate': 0.0,  # Interest-free loan
            'loan_term': 20,
            'transaction_costs': 25000,
            'current_annual_rent': 30000,
            'rent_increase_rate': 3.0,
            'analysis_period': 25,
            'cost_of_capital': 8.0
        }
        
        result = calculate_npv_comparison(**params)
        
        # Should complete without errors
        assert 'ownership_npv' in result
        assert result['recommendation'] in ['BUY', 'RENT', 'MARGINAL']
        
    def test_mathematical_consistency(self, standard_scenario_params):
        """Test mathematical consistency across calculations"""
        result = calculate_npv_comparison(**standard_scenario_params)
        
        # Verify that ownership NPV minus rental NPV equals NPV difference
        npv_diff_check = abs((result['ownership_npv'] - result['rental_npv']) - result['npv_difference'])
        assert npv_diff_check < 1.0, "NPV difference calculation inconsistent"
        
        # Verify that initial investments are positive
        assert result['ownership_initial_investment'] > 0
        assert result['rental_initial_investment'] >= 0  # Can be zero
        
        # Verify that terminal values make economic sense
        assert result['ownership_terminal_value'] > 0  # Should have property equity
        
    def test_sensitivity_bounds_checking(self):
        """Test that extreme parameter values are handled gracefully"""
        extreme_params = {
            'purchase_price': 10000000,  # Very high price
            'down_payment_pct': 5,  # Very low down payment
            'interest_rate': 15.0,  # High interest rate
            'loan_term': 5,  # Short term
            'transaction_costs': 500000,  # High transaction costs
            'current_annual_rent': 200000,  # High rent
            'rent_increase_rate': 10.0,  # High rent increases
            'analysis_period': 50,  # Long analysis period
            'cost_of_capital': 15.0  # High cost of capital
        }
        
        # Should not throw exceptions
        result = calculate_npv_comparison(**extreme_params)
        assert 'recommendation' in result
        
    def test_year_1_indexing_consistency(self):
        """Test that Year-1 indexing is consistently applied across all cost calculations"""
        params = {
            'purchase_price': 500000,
            'down_payment_pct': 30,
            'interest_rate': 5.0,
            'loan_term': 20,
            'analysis_period': 3,  # Short period for focused testing
            'property_tax_rate': 1.2,
            'property_tax_escalation': 2.0,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'current_annual_rent': 30000,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0,
            'inflation_rate': 3.0
        }
        
        # Get ownership cash flows
        ownership_flows = calculate_ownership_cash_flows(
            purchase_price=params['purchase_price'],
            down_payment_pct=params['down_payment_pct'],
            interest_rate=params['interest_rate'],
            loan_term=params['loan_term'],
            analysis_period=params['analysis_period'],
            property_tax_rate=params['property_tax_rate'],
            property_tax_escalation=params['property_tax_escalation'],
            insurance_cost=params['insurance_cost'],
            annual_maintenance=params['annual_maintenance'],
            inflation_rate=params['inflation_rate']
        )
        
        # Get rental cash flows
        rental_flows = calculate_rental_cash_flows(
            current_annual_rent=params['current_annual_rent'],
            rent_increase_rate=params['rent_increase_rate'],
            analysis_period=params['analysis_period']
        )
        
        # Verify Year 1 uses base costs (Year-1 indexing)
        year_1_ownership = ownership_flows[0]
        assert year_1_ownership['property_taxes'] == 500000 * 0.012  # Base rate, no escalation
        assert year_1_ownership['insurance'] == 5000  # Base cost, no escalation
        assert year_1_ownership['maintenance'] == 10000  # Base cost, no escalation
        
        year_1_rental = rental_flows[0]
        assert year_1_rental['annual_rent'] == 30000  # Base rent, no escalation
        
        # Verify Year 2 shows escalation
        year_2_ownership = ownership_flows[1]
        assert year_2_ownership['property_taxes'] > year_1_ownership['property_taxes']
        assert year_2_ownership['insurance'] > year_1_ownership['insurance']
        
        year_2_rental = rental_flows[1]
        assert year_2_rental['annual_rent'] > year_1_rental['annual_rent']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])