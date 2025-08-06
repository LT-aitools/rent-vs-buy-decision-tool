"""
Unit tests for terminal value calculation functions
Tests hold-forever wealth analysis and property appreciation
"""

import pytest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculations.terminal_value import (
    calculate_property_appreciation,
    calculate_depreciation_schedule,
    calculate_terminal_value,
    calculate_rental_terminal_value,
    calculate_wealth_comparison,
    calculate_property_components_over_time
)


class TestTerminalValueCalculations:
    """Test suite for terminal value calculation functions"""
    
    def test_property_appreciation_calculation(self):
        """Test basic property appreciation calculation"""
        appreciated_value = calculate_property_appreciation(
            initial_value=100000,
            appreciation_rate=3.0,
            time_period=10
        )
        
        expected_value = 100000 * (1.03 ** 10)  # 134,391.64
        assert abs(appreciated_value - expected_value) < 1.0
        
    def test_property_appreciation_zero_rate(self):
        """Test property appreciation with 0% rate"""
        appreciated_value = calculate_property_appreciation(
            initial_value=100000,
            appreciation_rate=0.0,
            time_period=10
        )
        
        assert appreciated_value == 100000  # No appreciation
        
    def test_property_appreciation_zero_time(self):
        """Test property appreciation with 0 years"""
        appreciated_value = calculate_property_appreciation(
            initial_value=100000,
            appreciation_rate=3.0,
            time_period=0
        )
        
        assert appreciated_value == 100000  # No time passed
        
    def test_depreciation_schedule_partial(self):
        """Test building depreciation schedule - partial period"""
        depreciation = calculate_depreciation_schedule(
            building_value=400000,
            depreciation_period=39,
            analysis_period=25
        )
        
        expected_accumulated = 400000 * 25 / 39  # 256,410.26
        expected_depreciated = 400000 - expected_accumulated  # 143,589.74
        
        assert abs(depreciation['accumulated_depreciation'] - expected_accumulated) < 1.0
        assert abs(depreciation['depreciated_building_value'] - expected_depreciated) < 1.0
        assert abs(depreciation['annual_depreciation'] - (400000 / 39)) < 1.0
        
    def test_depreciation_schedule_full_period(self):
        """Test building depreciation schedule - full depreciation"""
        depreciation = calculate_depreciation_schedule(
            building_value=400000,
            depreciation_period=39,
            analysis_period=50  # Longer than depreciation period
        )
        
        # Should be fully depreciated
        assert depreciation['accumulated_depreciation'] == 400000
        assert depreciation['depreciated_building_value'] == 0.0
        
    def test_depreciation_schedule_zero_values(self):
        """Test depreciation schedule with zero values"""
        depreciation = calculate_depreciation_schedule(
            building_value=0,
            depreciation_period=39,
            analysis_period=25
        )
        
        assert depreciation['accumulated_depreciation'] == 0.0
        assert depreciation['depreciated_building_value'] == 0.0
        assert depreciation['annual_depreciation'] == 0.0
        
    def test_terminal_value_calculation_standard(self):
        """Test complete terminal value calculation - standard case"""
        terminal = calculate_terminal_value(
            purchase_price=500000,
            land_value_pct=25,
            market_appreciation_rate=3.0,
            depreciation_period=39,
            analysis_period=25,
            remaining_loan_balance=150000
        )
        
        # Verify initial values
        assert terminal['initial_land_value'] == 125000  # 500000 * 25%
        assert terminal['initial_building_value'] == 375000  # 500000 - 125000
        
        # Verify land appreciation
        expected_land_end = 125000 * (1.03 ** 25)
        assert abs(terminal['land_value_end'] - expected_land_end) < 1.0
        
        # Verify building depreciation and appreciation
        accumulated_depreciation = 375000 * 25 / 39
        depreciated_building = 375000 - accumulated_depreciation
        expected_building_end = depreciated_building * (1.03 ** 25)
        assert abs(terminal['building_value_end'] - expected_building_end) < 1.0
        
        # Verify net equity calculation
        total_property_value = terminal['land_value_end'] + terminal['building_value_end']
        expected_net_equity = total_property_value - 150000
        assert abs(terminal['net_property_equity'] - expected_net_equity) < 1.0
        
    def test_terminal_value_no_appreciation(self):
        """Test terminal value with 0% appreciation"""
        terminal = calculate_terminal_value(
            purchase_price=500000,
            land_value_pct=25,
            market_appreciation_rate=0.0,
            depreciation_period=39,
            analysis_period=25,
            remaining_loan_balance=0
        )
        
        # Land should remain at initial value
        assert terminal['land_value_end'] == 125000
        
        # Building should only show depreciation effect
        accumulated_depreciation = 375000 * 25 / 39
        expected_building_end = 375000 - accumulated_depreciation
        assert abs(terminal['building_value_end'] - expected_building_end) < 1.0
        
    def test_terminal_value_no_loan_balance(self):
        """Test terminal value with no remaining loan balance"""
        terminal = calculate_terminal_value(
            purchase_price=500000,
            land_value_pct=25,
            market_appreciation_rate=3.0,
            depreciation_period=39,
            analysis_period=25,
            remaining_loan_balance=0  # No remaining loan
        )
        
        # Net equity should equal total property value
        expected_net_equity = terminal['terminal_property_value']
        assert terminal['net_property_equity'] == expected_net_equity
        
    def test_terminal_value_invalid_inputs(self):
        """Test terminal value with invalid inputs"""
        with pytest.raises(ValueError):
            calculate_terminal_value(
                purchase_price=-500000,  # Negative price
                land_value_pct=25,
                market_appreciation_rate=3.0,
                depreciation_period=39,
                analysis_period=25,
                remaining_loan_balance=0
            )
        
        with pytest.raises(ValueError):
            calculate_terminal_value(
                purchase_price=500000,
                land_value_pct=150,  # Invalid land percentage
                market_appreciation_rate=3.0,
                depreciation_period=39,
                analysis_period=25,
                remaining_loan_balance=0
            )
            
    def test_rental_terminal_value(self):
        """Test rental terminal value calculation"""
        rental_terminal = calculate_rental_terminal_value(
            security_deposit=10000,
            inflation_rate=3.0,
            analysis_period=25
        )
        
        expected_recovery = 10000 * (1.03 ** 25)
        assert abs(rental_terminal['security_deposit_recovery'] - expected_recovery) < 1.0
        assert rental_terminal['terminal_asset_value'] == 0.0
        assert rental_terminal['net_wealth_accumulation'] == 0.0
        
    def test_rental_terminal_value_zero_period(self):
        """Test rental terminal value with zero analysis period"""
        rental_terminal = calculate_rental_terminal_value(
            security_deposit=10000,
            inflation_rate=3.0,
            analysis_period=0
        )
        
        assert rental_terminal['security_deposit_recovery'] == 10000
        
    def test_wealth_comparison(self):
        """Test wealth comparison between ownership and rental"""
        ownership_terminal = {
            'net_property_equity': 750000
        }
        rental_terminal = {
            'security_deposit_recovery': 20000
        }
        
        comparison = calculate_wealth_comparison(ownership_terminal, rental_terminal)
        
        assert comparison['ownership_wealth'] == 750000
        assert comparison['rental_wealth'] == 20000
        assert comparison['wealth_advantage'] == 730000
        assert comparison['ownership_superior'] is True
        
        # Test percentage calculation
        expected_pct = (730000 / 20000) * 100
        assert abs(comparison['wealth_advantage_pct'] - expected_pct) < 0.01
        
    def test_wealth_comparison_rental_superior(self):
        """Test wealth comparison where rental is superior"""
        ownership_terminal = {
            'net_property_equity': 15000  # Low due to market crash
        }
        rental_terminal = {
            'security_deposit_recovery': 20000
        }
        
        comparison = calculate_wealth_comparison(ownership_terminal, rental_terminal)
        
        assert comparison['wealth_advantage'] == -5000
        assert comparison['ownership_superior'] is False
        
    def test_property_components_over_time(self):
        """Test property value components calculation over time"""
        yearly_values = calculate_property_components_over_time(
            purchase_price=500000,
            land_value_pct=25,
            market_appreciation_rate=3.0,
            depreciation_period=39,
            max_years=5
        )
        
        assert len(yearly_values) == 5
        
        # Test Year 1 values
        year_1 = yearly_values[0]
        assert year_1['year'] == 1
        assert year_1['land_value'] == 125000 * 1.03  # First year appreciation
        
        # Test that total value increases over time (despite depreciation)
        assert yearly_values[4]['total_property_value'] > yearly_values[0]['total_property_value']
        
    def test_land_value_edge_cases(self):
        """Test terminal value with edge case land value percentages"""
        # 100% land value (no building)
        terminal_all_land = calculate_terminal_value(
            purchase_price=500000,
            land_value_pct=100,
            market_appreciation_rate=3.0,
            depreciation_period=39,
            analysis_period=25,
            remaining_loan_balance=0
        )
        
        assert terminal_all_land['initial_building_value'] == 0
        assert terminal_all_land['building_value_end'] == 0
        assert terminal_all_land['accumulated_depreciation'] == 0
        
        # 0% land value (all building)
        terminal_all_building = calculate_terminal_value(
            purchase_price=500000,
            land_value_pct=0,
            market_appreciation_rate=3.0,
            depreciation_period=39,
            analysis_period=25,
            remaining_loan_balance=0
        )
        
        assert terminal_all_building['initial_land_value'] == 0
        assert terminal_all_building['land_value_end'] == 0
        
    def test_high_appreciation_rate(self):
        """Test terminal value with high appreciation rate"""
        terminal = calculate_terminal_value(
            purchase_price=500000,
            land_value_pct=25,
            market_appreciation_rate=10.0,  # High appreciation
            depreciation_period=39,
            analysis_period=25,
            remaining_loan_balance=100000
        )
        
        # Should result in very high property values
        assert terminal['terminal_property_value'] > 2000000
        assert terminal['net_property_equity'] > 1900000


if __name__ == "__main__":
    pytest.main([__file__])