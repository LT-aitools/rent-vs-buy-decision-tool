"""
Data Validation Tests for Financial Accuracy
Comprehensive validation of input data and business logic

This module provides:
- Input parameter validation
- Business rule enforcement
- Data consistency checks
- Edge case validation
- Financial constraint verification
"""

import unittest
import sys
import os
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from decimal import Decimal, getcontext

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.shared.interfaces import ValidationResult, ValidationStatus, MarketData


class FinancialDataValidator:
    """Financial data validation utility"""
    
    def __init__(self):
        self.validation_errors = []
        self.validation_warnings = []
        
    def validate_purchase_price(self, price: float) -> ValidationResult:
        """Validate purchase price"""
        if price <= 0:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Purchase price must be positive",
                suggestions=["Enter a positive purchase price greater than $0"]
            )
        
        if price < 50000:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Purchase price seems unusually low",
                suggestions=["Verify the purchase price is correct"]
            )
        
        if price > 10000000:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Purchase price seems unusually high",
                suggestions=["Verify the purchase price is correct"]
            )
        
        return ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            message="Valid purchase price"
        )
    
    def validate_down_payment(self, down_payment_pct: float, purchase_price: float) -> ValidationResult:
        """Validate down payment percentage"""
        if down_payment_pct < 0:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Down payment percentage cannot be negative",
                suggestions=["Enter a down payment percentage between 0% and 100%"]
            )
        
        if down_payment_pct > 100:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Down payment percentage cannot exceed 100%",
                suggestions=["Enter a down payment percentage between 0% and 100%"]
            )
        
        down_payment_amount = purchase_price * (down_payment_pct / 100)
        
        if down_payment_pct < 5:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Very low down payment may require PMI",
                suggestions=["Consider including PMI costs in your analysis"]
            )
        
        if down_payment_pct < 20:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Down payment below 20% typically requires PMI",
                suggestions=["Include PMI costs in your analysis"]
            )
        
        return ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            message="Valid down payment percentage"
        )
    
    def validate_interest_rate(self, rate: float) -> ValidationResult:
        """Validate interest rate"""
        if rate < 0:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Interest rate cannot be negative",
                suggestions=["Enter a positive interest rate"]
            )
        
        if rate > 25:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Interest rate seems unrealistically high",
                suggestions=["Verify the interest rate is correct"]
            )
        
        if rate < 1:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Interest rate seems unusually low",
                suggestions=["Verify this rate is available to you"]
            )
        
        if rate > 15:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Interest rate seems high for residential mortgages",
                suggestions=["Verify this is the correct rate"]
            )
        
        return ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            message="Valid interest rate"
        )
    
    def validate_rental_data(self, annual_rent: float, purchase_price: float) -> ValidationResult:
        """Validate rental data against purchase price"""
        if annual_rent <= 0:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Annual rent must be positive",
                suggestions=["Enter a positive annual rent amount"]
            )
        
        # Calculate rent-to-price ratio
        rent_to_price_ratio = annual_rent / purchase_price
        
        if rent_to_price_ratio < 0.03:  # Less than 3%
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Rent-to-price ratio seems low, buying may be favorable",
                suggestions=["Verify rental market data for this location"]
            )
        
        if rent_to_price_ratio > 0.15:  # More than 15%
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Rent-to-price ratio seems high, renting may be favorable",
                suggestions=["Verify rental and purchase price data"]
            )
        
        return ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            message="Reasonable rent-to-price ratio"
        )
    
    def validate_time_parameters(self, analysis_period: int, loan_term: int) -> ValidationResult:
        """Validate time-related parameters"""
        if analysis_period <= 0:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Analysis period must be positive",
                suggestions=["Enter an analysis period of at least 1 year"]
            )
        
        if loan_term <= 0:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Loan term must be positive",
                suggestions=["Enter a loan term of at least 1 year"]
            )
        
        if analysis_period > loan_term:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Analysis period exceeds loan term",
                suggestions=["Consider how mortgage payments change after loan is paid off"]
            )
        
        if analysis_period > 50:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Very long analysis period may reduce accuracy",
                suggestions=["Consider shorter analysis periods for more reliable results"]
            )
        
        return ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            message="Valid time parameters"
        )
    
    def validate_cost_of_capital(self, cost_of_capital: float, interest_rate: float) -> ValidationResult:
        """Validate cost of capital against interest rate"""
        if cost_of_capital <= 0:
            return ValidationResult(
                is_valid=False,
                status=ValidationStatus.ERROR,
                message="Cost of capital must be positive",
                suggestions=["Enter a positive cost of capital rate"]
            )
        
        if cost_of_capital < interest_rate - 2:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Cost of capital seems low relative to mortgage rate",
                suggestions=["Consider if this discount rate reflects your opportunity cost"]
            )
        
        if cost_of_capital > 25:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Cost of capital seems very high",
                suggestions=["Verify this reflects your required return"]
            )
        
        return ValidationResult(
            is_valid=True,
            status=ValidationStatus.VALID,
            message="Valid cost of capital"
        )


class TestInputValidation(unittest.TestCase):
    """Test input parameter validation"""
    
    def setUp(self):
        """Set up validator"""
        self.validator = FinancialDataValidator()
    
    def test_purchase_price_validation(self):
        """Test purchase price validation rules"""
        # Valid prices
        valid_prices = [100000, 250000, 500000, 750000, 1000000]
        for price in valid_prices:
            result = self.validator.validate_purchase_price(price)
            self.assertTrue(result.is_valid, f"Valid price {price} failed validation")
        
        # Invalid prices
        invalid_prices = [-100000, 0, -50000]
        for price in invalid_prices:
            result = self.validator.validate_purchase_price(price)
            self.assertFalse(result.is_valid, f"Invalid price {price} passed validation")
            self.assertEqual(result.status, ValidationStatus.ERROR)
        
        # Warning prices
        warning_prices = [25000, 15000000]
        for price in warning_prices:
            result = self.validator.validate_purchase_price(price)
            self.assertTrue(result.is_valid, f"Warning price {price} marked invalid")
            self.assertEqual(result.status, ValidationStatus.WARNING)
    
    def test_down_payment_validation(self):
        """Test down payment validation rules"""
        purchase_price = 500000
        
        # Valid down payments
        valid_down_payments = [0, 5, 10, 20, 30, 50, 100]
        for dp in valid_down_payments:
            result = self.validator.validate_down_payment(dp, purchase_price)
            self.assertTrue(result.is_valid, f"Valid down payment {dp}% failed validation")
        
        # Invalid down payments
        invalid_down_payments = [-10, -5, 110, 150]
        for dp in invalid_down_payments:
            result = self.validator.validate_down_payment(dp, purchase_price)
            self.assertFalse(result.is_valid, f"Invalid down payment {dp}% passed validation")
            self.assertEqual(result.status, ValidationStatus.ERROR)
    
    def test_interest_rate_validation(self):
        """Test interest rate validation rules"""
        # Valid rates
        valid_rates = [3.0, 4.5, 5.0, 6.5, 7.0]
        for rate in valid_rates:
            result = self.validator.validate_interest_rate(rate)
            self.assertTrue(result.is_valid, f"Valid rate {rate}% failed validation")
        
        # Invalid rates
        invalid_rates = [-1, -5, 30, 50]
        for rate in invalid_rates:
            result = self.validator.validate_interest_rate(rate)
            self.assertFalse(result.is_valid, f"Invalid rate {rate}% passed validation")
            self.assertEqual(result.status, ValidationStatus.ERROR)
    
    def test_rental_data_validation(self):
        """Test rental data validation"""
        purchase_price = 500000
        
        # Test various rent levels
        test_cases = [
            (60000, ValidationStatus.VALID),    # 12% ratio - reasonable
            (15000, ValidationStatus.WARNING),  # 3% ratio - low rent
            (80000, ValidationStatus.WARNING),  # 16% ratio - high rent
            (0, ValidationStatus.ERROR),        # Invalid
            (-10000, ValidationStatus.ERROR)    # Invalid
        ]
        
        for annual_rent, expected_status in test_cases:
            result = self.validator.validate_rental_data(annual_rent, purchase_price)
            if expected_status == ValidationStatus.ERROR:
                self.assertFalse(result.is_valid, f"Invalid rent {annual_rent} passed validation")
            else:
                self.assertTrue(result.is_valid, f"Valid rent {annual_rent} failed validation")
            self.assertEqual(result.status, expected_status)


class TestBusinessRuleValidation(unittest.TestCase):
    """Test business rule enforcement"""
    
    def test_loan_amount_calculation(self):
        """Test loan amount calculation and validation"""
        purchase_price = 500000
        
        test_cases = [
            (20, 400000),   # 20% down = $400k loan
            (0, 500000),    # 0% down = $500k loan
            (50, 250000),   # 50% down = $250k loan
            (100, 0)        # 100% down = $0 loan
        ]
        
        for down_payment_pct, expected_loan in test_cases:
            loan_amount = purchase_price * (1 - down_payment_pct / 100)
            self.assertEqual(loan_amount, expected_loan,
                           f"Loan calculation failed for {down_payment_pct}% down")
    
    def test_debt_to_income_implications(self):
        """Test debt-to-income ratio implications"""
        # Mock monthly income and calculate debt ratios
        monthly_income = 10000
        
        test_cases = [
            (400000, 5.0, 30),  # Loan amount, rate, term
            (300000, 4.5, 25),
            (200000, 6.0, 15)
        ]
        
        for loan_amount, rate, term in test_cases:
            # Simple mortgage payment calculation
            monthly_rate = rate / 100 / 12
            num_payments = term * 12
            
            if monthly_rate > 0:
                monthly_payment = loan_amount * (
                    monthly_rate * (1 + monthly_rate)**num_payments
                ) / ((1 + monthly_rate)**num_payments - 1)
            else:
                monthly_payment = loan_amount / num_payments
            
            debt_to_income = monthly_payment / monthly_income
            
            # DTI should be reasonable (< 0.4 for 40%)
            if debt_to_income > 0.4:
                print(f"High DTI warning: {debt_to_income:.1%} for loan ${loan_amount:,.0f}")
    
    def test_cash_flow_analysis(self):
        """Test cash flow validation"""
        scenarios = [
            {
                'purchase_price': 500000,
                'annual_rent': 60000,
                'property_tax_rate': 1.2,
                'insurance': 5000,
                'maintenance_pct': 2.0
            },
            {
                'purchase_price': 300000,
                'annual_rent': 36000,
                'property_tax_rate': 1.0,
                'insurance': 3000,
                'maintenance_pct': 1.5
            }
        ]
        
        for scenario in scenarios:
            # Calculate annual ownership costs
            property_tax = scenario['purchase_price'] * scenario['property_tax_rate'] / 100
            insurance = scenario['insurance']
            maintenance = scenario['purchase_price'] * scenario['maintenance_pct'] / 100
            
            total_ownership_costs = property_tax + insurance + maintenance
            annual_rent = scenario['annual_rent']
            
            print(f"\nCash Flow Analysis:")
            print(f"  Annual rent: ${annual_rent:,.0f}")
            print(f"  Ownership costs: ${total_ownership_costs:,.0f}")
            print(f"  Cost difference: ${total_ownership_costs - annual_rent:,.0f}")
            
            # Validate costs are reasonable
            self.assertGreater(property_tax, 0)
            self.assertGreater(insurance, 0)
            self.assertGreater(maintenance, 0)


class TestEdgeCaseValidation(unittest.TestCase):
    """Test edge case validation"""
    
    def test_extreme_value_handling(self):
        """Test handling of extreme values"""
        validator = FinancialDataValidator()
        
        # Test extreme purchase prices
        extreme_cases = [
            ('purchase_price', 1, False),          # $1 house
            ('purchase_price', 100000000, True),   # $100M house
            ('interest_rate', 0.001, True),        # 0.001% rate
            ('interest_rate', 24.99, True),        # 24.99% rate
            ('down_payment_pct', 0.01, True),      # 0.01% down
            ('down_payment_pct', 99.99, True)      # 99.99% down
        ]
        
        for param, value, should_be_valid in extreme_cases:
            if param == 'purchase_price':
                result = validator.validate_purchase_price(value)
            elif param == 'interest_rate':
                result = validator.validate_interest_rate(value)
            elif param == 'down_payment_pct':
                result = validator.validate_down_payment(value, 500000)
            
            if should_be_valid:
                self.assertTrue(result.is_valid, f"Edge case {param}={value} should be valid")
            else:
                self.assertFalse(result.is_valid, f"Edge case {param}={value} should be invalid")
    
    def test_precision_handling(self):
        """Test precision in financial calculations"""
        # Test with high precision values
        getcontext().prec = 28
        
        precise_values = [
            Decimal('500000.123456789'),
            Decimal('5.123456789'),
            Decimal('20.987654321')
        ]
        
        for value in precise_values:
            # Convert to float for validation
            float_value = float(value)
            
            # Should handle precision appropriately
            self.assertIsInstance(float_value, float)
            self.assertAlmostEqual(float_value, float(value), places=6)
    
    def test_boundary_conditions(self):
        """Test boundary conditions"""
        validator = FinancialDataValidator()
        
        boundary_tests = [
            # Just at boundaries
            ('interest_rate', 0.0, True),
            ('interest_rate', 25.0, False),
            ('down_payment_pct', 0.0, True),
            ('down_payment_pct', 100.0, True),
            ('purchase_price', 50000.0, True)  # Warning boundary
        ]
        
        for param, value, should_be_valid in boundary_tests:
            if param == 'interest_rate':
                result = validator.validate_interest_rate(value)
            elif param == 'down_payment_pct':
                result = validator.validate_down_payment(value, 500000)
            elif param == 'purchase_price':
                result = validator.validate_purchase_price(value)
            
            if should_be_valid:
                self.assertTrue(result.is_valid, f"Boundary {param}={value} should be valid")
            else:
                self.assertFalse(result.is_valid, f"Boundary {param}={value} should be invalid")


class TestMarketDataValidation(unittest.TestCase):
    """Test market data validation"""
    
    def test_market_data_consistency(self):
        """Test market data internal consistency"""
        # Test with reasonable market data
        market_data = MarketData(
            location="Test City",
            zip_code="12345",
            median_rent_per_sqm=25.0,
            rental_vacancy_rate=5.0,
            rental_growth_rate=3.0,
            median_property_price=500000.0,
            property_appreciation_rate=4.0,
            months_on_market=2.5,
            current_mortgage_rates={"30_year_fixed": 5.5},
            rate_trend="stable",
            local_inflation_rate=3.0,
            unemployment_rate=4.5,
            population_growth_rate=1.2,
            data_timestamp=datetime.now(),
            data_sources=["test_api"],
            confidence_score=0.85,
            freshness_hours=2.0
        )
        
        # Validate data consistency
        self.assertGreater(market_data.confidence_score, 0.0)
        self.assertLessEqual(market_data.confidence_score, 1.0)
        self.assertGreater(market_data.median_property_price, 0)
        self.assertGreater(market_data.median_rent_per_sqm, 0)
        
        # Check economic consistency
        self.assertLess(market_data.rental_vacancy_rate, 50)  # < 50%
        self.assertGreater(market_data.rental_vacancy_rate, 0)  # > 0%
    
    def test_market_data_quality_flags(self):
        """Test market data quality assessment"""
        # Test with questionable data
        questionable_data = MarketData(
            location="Questionable City",
            zip_code="99999",
            median_rent_per_sqm=100.0,  # Very high rent
            rental_vacancy_rate=50.0,   # Very high vacancy
            rental_growth_rate=-10.0,   # Large negative growth
            median_property_price=50000.0,  # Very low price
            property_appreciation_rate=-5.0,  # Depreciation
            months_on_market=24.0,      # Very long time
            current_mortgage_rates={"30_year_fixed": 20.0},  # Very high
            rate_trend="volatile",
            local_inflation_rate=15.0,  # High inflation
            unemployment_rate=25.0,     # Very high unemployment
            population_growth_rate=-5.0,  # Population decline
            data_timestamp=datetime.now(),
            data_sources=["unreliable_source"],
            confidence_score=0.2,       # Low confidence
            freshness_hours=168.0       # Week old data
        )
        
        # Should flag as questionable
        quality_issues = []
        
        if questionable_data.confidence_score < 0.5:
            quality_issues.append("Low confidence score")
        
        if questionable_data.freshness_hours > 24:
            quality_issues.append("Stale data")
        
        if questionable_data.rental_vacancy_rate > 20:
            quality_issues.append("High vacancy rate")
        
        if questionable_data.unemployment_rate > 15:
            quality_issues.append("High unemployment")
        
        self.assertGreater(len(quality_issues), 0, "Should detect data quality issues")


class TestDataIntegrityValidation(unittest.TestCase):
    """Test data integrity and consistency"""
    
    def test_calculation_input_integrity(self):
        """Test integrity of calculation inputs"""
        # Complete valid dataset
        complete_data = {
            'purchase_price': 500000,
            'down_payment_pct': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'current_annual_rent': 60000,
            'rent_increase_rate': 3.0,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.2,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'market_appreciation_rate': 3.5,
            'transaction_costs': 25000
        }
        
        # Test data completeness
        required_fields = [
            'purchase_price', 'down_payment_pct', 'interest_rate',
            'loan_term', 'current_annual_rent', 'analysis_period'
        ]
        
        for field in required_fields:
            self.assertIn(field, complete_data, f"Missing required field: {field}")
            self.assertIsInstance(complete_data[field], (int, float))
            self.assertGreater(complete_data[field], 0, f"Invalid value for {field}")
    
    def test_cross_field_validation(self):
        """Test validation across multiple fields"""
        # Test scenarios where multiple fields must be consistent
        test_scenarios = [
            {
                'scenario': 'High rent vs low price',
                'purchase_price': 200000,
                'annual_rent': 50000,  # 25% ratio - very high
                'expected_warning': True
            },
            {
                'scenario': 'Low rent vs high price',
                'purchase_price': 1000000,
                'annual_rent': 20000,  # 2% ratio - very low
                'expected_warning': True
            },
            {
                'scenario': 'Balanced ratio',
                'purchase_price': 500000,
                'annual_rent': 40000,  # 8% ratio - reasonable
                'expected_warning': False
            }
        ]
        
        validator = FinancialDataValidator()
        
        for scenario in test_scenarios:
            result = validator.validate_rental_data(
                scenario['annual_rent'], 
                scenario['purchase_price']
            )
            
            if scenario['expected_warning']:
                self.assertEqual(result.status, ValidationStatus.WARNING,
                               f"Should warn for {scenario['scenario']}")
            else:
                self.assertEqual(result.status, ValidationStatus.VALID,
                               f"Should be valid for {scenario['scenario']}")


if __name__ == '__main__':
    unittest.main(verbosity=2)