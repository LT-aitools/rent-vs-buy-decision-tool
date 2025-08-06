"""
Unit tests for mortgage calculation functions
Tests all edge cases and mathematical accuracy
"""

import pytest
import numpy as np
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculations.mortgage import (
    calculate_mortgage_payment,
    calculate_loan_amount,
    validate_mortgage_inputs,
    calculate_payment_breakdown,
    calculate_effective_interest_rate
)


class TestMortgageCalculations:
    """Test suite for mortgage calculation functions"""
    
    def test_standard_mortgage_calculation(self):
        """Test standard mortgage payment calculation"""
        result = calculate_mortgage_payment(
            purchase_price=500000,
            down_payment_pct=30,
            interest_rate=5.0,
            loan_term=20
        )
        
        # Expected values calculated using financial calculator
        assert abs(result['annual_payment'] - 27718.14) < 1.0
        assert abs(result['loan_amount'] - 350000) < 1.0
        assert abs(result['down_payment_amount'] - 150000) < 1.0
        
    def test_100_percent_down_payment(self):
        """Test edge case: 100% down payment"""
        result = calculate_mortgage_payment(
            purchase_price=500000,
            down_payment_pct=100,
            interest_rate=5.0,
            loan_term=20
        )
        
        assert result['annual_payment'] == 0.0
        assert result['loan_amount'] == 0.0
        assert result['down_payment_amount'] == 500000
        
    def test_zero_interest_rate(self):
        """Test edge case: 0% interest rate"""
        result = calculate_mortgage_payment(
            purchase_price=500000,
            down_payment_pct=30,
            interest_rate=0.0,
            loan_term=20
        )
        
        expected_annual_payment = 350000 / 20  # 17,500
        assert abs(result['annual_payment'] - expected_annual_payment) < 1.0
        assert result['interest_portion_year_1'] == 0.0
        assert result['principal_portion_year_1'] == expected_annual_payment
        
    def test_loan_amount_calculation(self):
        """Test loan amount calculation"""
        loan_amount = calculate_loan_amount(
            purchase_price=500000,
            down_payment_pct=30,
            transaction_costs=25000
        )
        
        assert loan_amount == 350000  # 500000 - (500000 * 0.30)
        
    def test_loan_amount_100_percent_down(self):
        """Test loan amount with 100% down payment"""
        loan_amount = calculate_loan_amount(
            purchase_price=500000,
            down_payment_pct=100
        )
        
        assert loan_amount == 0.0
        
    def test_input_validation_valid_inputs(self):
        """Test input validation with valid inputs"""
        validation = validate_mortgage_inputs(
            purchase_price=500000,
            down_payment_pct=30,
            interest_rate=5.0,
            loan_term=20
        )
        
        assert validation['valid'] is True
        assert len(validation['errors']) == 0
        
    def test_input_validation_invalid_inputs(self):
        """Test input validation with invalid inputs"""
        validation = validate_mortgage_inputs(
            purchase_price=-100000,  # Invalid: negative
            down_payment_pct=150,    # Invalid: > 100%
            interest_rate=25.0,      # Invalid: > 20%
            loan_term=60             # Invalid: > 50 years
        )
        
        assert validation['valid'] is False
        assert len(validation['errors']) > 0
        
    def test_payment_breakdown(self):
        """Test payment breakdown calculation"""
        breakdown = calculate_payment_breakdown(
            loan_amount=350000,
            interest_rate=5.0,
            annual_payment=27718.14,
            year=1
        )
        
        expected_interest = 350000 * 0.05  # 17,500
        expected_principal = 27718.14 - expected_interest  # 10,218.14
        
        assert abs(breakdown['interest_portion'] - expected_interest) < 1.0
        assert abs(breakdown['principal_portion'] - expected_principal) < 1.0
        
    def test_effective_interest_rate(self):
        """Test effective interest rate calculation"""
        effective_rate = calculate_effective_interest_rate(
            loan_amount=350000,
            annual_payment=27718.14,
            loan_term=20,
            fees=5000
        )
        
        # Should be slightly higher than 5% due to fees
        assert effective_rate > 5.0
        assert effective_rate < 7.0  # Reasonable upper bound
        
    def test_very_low_purchase_price(self):
        """Test with very low purchase price"""
        result = calculate_mortgage_payment(
            purchase_price=100000,
            down_payment_pct=20,
            interest_rate=5.0,
            loan_term=15
        )
        
        expected_loan = 80000
        assert abs(result['loan_amount'] - expected_loan) < 1.0
        assert result['annual_payment'] > 0
        
    def test_very_high_interest_rate(self):
        """Test with high but valid interest rate"""
        result = calculate_mortgage_payment(
            purchase_price=500000,
            down_payment_pct=30,
            interest_rate=15.0,
            loan_term=20
        )
        
        # High interest should result in much higher payment
        assert result['annual_payment'] > 40000
        assert result['interest_portion_year_1'] > 50000
        
    def test_short_loan_term(self):
        """Test with short loan term"""
        result = calculate_mortgage_payment(
            purchase_price=500000,
            down_payment_pct=30,
            interest_rate=5.0,
            loan_term=5
        )
        
        # Short term should result in higher annual payment
        assert result['annual_payment'] > 70000
        
    def test_transaction_costs_inclusion(self):
        """Test that transaction costs are included in initial investment"""
        result = calculate_mortgage_payment(
            purchase_price=500000,
            down_payment_pct=30,
            interest_rate=5.0,
            loan_term=20,
            transaction_costs=25000
        )
        
        expected_initial = 150000 + 25000  # Down payment + transaction costs
        assert abs(result['total_initial_investment'] - expected_initial) < 1.0


if __name__ == "__main__":
    pytest.main([__file__])