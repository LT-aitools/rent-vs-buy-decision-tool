"""
Unit tests for annual cost calculation functions
Tests Year-1 indexing and cost escalation patterns
"""

import pytest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculations.annual_costs import (
    calculate_cost_escalation,
    calculate_annual_ownership_costs,
    calculate_annual_rental_costs,
    calculate_property_upgrade_costs,
    calculate_tax_benefits,
    calculate_subletting_income
)


class TestAnnualCostCalculations:
    """Test suite for annual cost calculation functions"""
    
    def test_year_1_indexing_escalation(self):
        """Test Year-1 indexing pattern for cost escalation"""
        base_cost = 1000
        escalation_rate = 3.0
        
        # Year 1: No escalation (Year-1 indexing)
        year_1 = calculate_cost_escalation(base_cost, escalation_rate, 1)
        assert year_1 == 1000.0
        
        # Year 2: First escalation (1000 * 1.03^1)
        year_2 = calculate_cost_escalation(base_cost, escalation_rate, 2)
        assert abs(year_2 - 1030.0) < 0.01
        
        # Year 3: Second escalation (1000 * 1.03^2)
        year_3 = calculate_cost_escalation(base_cost, escalation_rate, 3)
        assert abs(year_3 - 1060.9) < 0.01
        
    def test_standard_escalation_pattern(self):
        """Test standard (Year-0) escalation pattern"""
        base_cost = 1000
        escalation_rate = 3.0
        
        # Standard escalation (not Year-1 indexing)
        year_1_standard = calculate_cost_escalation(
            base_cost, escalation_rate, 1, year_1_indexing=False
        )
        assert abs(year_1_standard - 1030.0) < 0.01  # 1000 * 1.03^1
        
    def test_annual_ownership_costs_year_1(self):
        """Test annual ownership costs calculation for Year 1"""
        costs = calculate_annual_ownership_costs(
            purchase_price=500000,
            property_tax_rate=1.2,
            property_tax_escalation=2.0,
            insurance_cost=5000,
            annual_maintenance=10000,
            property_management=2000,
            capex_reserve_rate=1.5,
            obsolescence_risk_rate=0.5,
            inflation_rate=3.0,
            year=1
        )
        
        # Year 1 should use base costs (no escalation)
        assert costs['property_taxes'] == 6000.0  # 500000 * 1.2%
        assert costs['insurance'] == 5000.0
        assert costs['maintenance'] == 10000.0
        assert costs['property_management'] == 2000.0
        assert costs['capex_reserve'] == 7500.0  # 500000 * 1.5%
        assert costs['obsolescence_cost'] == 2500.0  # 500000 * 0.5%
        
    def test_annual_ownership_costs_year_2(self):
        """Test annual ownership costs calculation for Year 2 with escalation"""
        costs = calculate_annual_ownership_costs(
            purchase_price=500000,
            property_tax_rate=1.2,
            property_tax_escalation=2.0,
            insurance_cost=5000,
            annual_maintenance=10000,
            property_management=2000,
            capex_reserve_rate=1.5,
            obsolescence_risk_rate=0.5,
            inflation_rate=3.0,
            year=2
        )
        
        # Year 2 should show first escalation
        assert abs(costs['property_taxes'] - 6120.0) < 0.01  # 6000 * 1.02
        assert abs(costs['insurance'] - 5150.0) < 0.01  # 5000 * 1.03
        assert abs(costs['maintenance'] - 10300.0) < 0.01  # 10000 * 1.03
        assert abs(costs['capex_reserve'] - 7725.0) < 0.01  # 7500 * 1.03
        
    def test_annual_rental_costs_year_1_indexing(self):
        """Test rental costs with Year-1 indexing"""
        # Year 1
        costs_year_1 = calculate_annual_rental_costs(
            current_annual_rent=120000,
            rent_increase_rate=3.0,
            year=1
        )
        assert costs_year_1['annual_rent'] == 120000.0
        
        # Year 2
        costs_year_2 = calculate_annual_rental_costs(
            current_annual_rent=120000,
            rent_increase_rate=3.0,
            year=2
        )
        assert abs(costs_year_2['annual_rent'] - 123600.0) < 0.01  # 120000 * 1.03
        
    def test_rental_costs_with_space_calculation(self):
        """Test rental costs with space-based calculations"""
        costs = calculate_annual_rental_costs(
            current_annual_rent=120000,
            rent_increase_rate=3.0,
            year=1,
            current_space_needed=10000,  # 10,000 sq meters
            total_space_rented=10000
        )
        
        assert costs['rent_per_unit'] == 12.0  # 120000 / 10000
        assert costs['total_space'] == 10000
        
    def test_property_upgrade_costs(self):
        """Test property upgrade cost calculation"""
        # Year 15 (upgrade year with 15-year cycle)
        upgrade_cost = calculate_property_upgrade_costs(
            purchase_price=500000,
            land_value_pct=25,
            upgrade_cycle_years=15,
            year=15
        )
        
        building_value = 500000 * 0.75  # 375,000
        expected_upgrade = building_value * 0.02  # 7,500
        assert abs(upgrade_cost - expected_upgrade) < 0.01
        
        # Year 14 (not an upgrade year)
        no_upgrade_cost = calculate_property_upgrade_costs(
            purchase_price=500000,
            land_value_pct=25,
            upgrade_cycle_years=15,
            year=14
        )
        assert no_upgrade_cost == 0.0
        
    def test_tax_benefits_calculation(self):
        """Test tax benefits calculation"""
        benefits = calculate_tax_benefits(
            mortgage_interest=17500,
            property_taxes=6000,
            depreciation_amount=10000,
            corporate_tax_rate=25.0,
            interest_deductible=True,
            property_tax_deductible=True,
            depreciation_deductible=True
        )
        
        expected_total_deductions = 17500 + 6000 + 10000  # 33,500
        expected_tax_savings = 33500 * 0.25  # 8,375
        
        assert abs(benefits['total_tax_savings'] - expected_tax_savings) < 0.01
        assert benefits['interest_deduction'] == 17500
        assert benefits['property_tax_deduction'] == 6000
        assert benefits['depreciation_deduction'] == 10000
        
    def test_tax_benefits_non_deductible(self):
        """Test tax benefits with non-deductible items"""
        benefits = calculate_tax_benefits(
            mortgage_interest=17500,
            property_taxes=6000,
            depreciation_amount=10000,
            corporate_tax_rate=25.0,
            interest_deductible=False,  # Not deductible
            property_tax_deductible=True,
            depreciation_deductible=True
        )
        
        expected_deductions = 0 + 6000 + 10000  # 16,000
        expected_tax_savings = 16000 * 0.25  # 4,000
        
        assert abs(benefits['total_tax_savings'] - expected_tax_savings) < 0.01
        assert benefits['interest_deduction'] == 0.0
        
    def test_subletting_income_calculation(self):
        """Test subletting income calculation"""
        income = calculate_subletting_income(
            property_size=15000,  # 15,000 sq meters
            current_space_needed=10000,  # 10,000 sq meters needed
            subletting_rate_per_unit=8.0,  # $8 per sq meter annually
            subletting_space_sqm=4000,  # User wants to sublet 4,000 sq meters
            subletting_enabled=True
        )
        
        available_space = 15000 - 10000  # 5,000 sq meters available
        actual_subletting_space = 4000  # User wants 4,000 (less than available)
        expected_income = 4000 * 8.0  # 32,000
        
        assert income['available_space'] == 5000
        assert income['subletting_space'] == 4000
        assert abs(income['subletting_income'] - expected_income) < 0.01
        
    def test_subletting_disabled(self):
        """Test subletting calculation when disabled"""
        income = calculate_subletting_income(
            property_size=15000,
            current_space_needed=10000,
            subletting_rate_per_unit=8.0,
            subletting_space_sqm=4000,
            subletting_enabled=False
        )
        
        assert income['subletting_income'] == 0.0
        assert income['subletting_space'] == 0.0
        assert income['subletting_enabled'] is False
        
    def test_no_excess_space_subletting(self):
        """Test subletting when no excess space available"""
        income = calculate_subletting_income(
            property_size=10000,
            current_space_needed=12000,  # Need more than available
            subletting_rate_per_unit=8.0,
            subletting_space_sqm=2000,  # User wants to sublet but no space available
            subletting_enabled=True
        )
        
        assert income['available_space'] == 0.0  # max(0, 10000-12000)
        assert income['subletting_space'] == 0.0  # Can't sublet when no available space
        assert income['subletting_income'] == 0.0
        
    def test_zero_escalation_rate(self):
        """Test cost escalation with 0% escalation rate"""
        escalated_cost = calculate_cost_escalation(
            base_cost=1000,
            escalation_rate=0.0,
            year=5
        )
        
        assert escalated_cost == 1000.0  # No escalation
        
    def test_negative_year_error(self):
        """Test error handling for negative year values"""
        with pytest.raises(ValueError):
            calculate_cost_escalation(1000, 3.0, 0)
        
        with pytest.raises(ValueError):
            calculate_cost_escalation(1000, 3.0, -1)


if __name__ == "__main__":
    pytest.main([__file__])