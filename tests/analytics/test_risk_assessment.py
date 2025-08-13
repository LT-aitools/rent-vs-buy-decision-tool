"""
Unit tests for Risk Assessment Engine

Comprehensive test suite covering:
- Risk factor calculation and scoring
- Overall risk level determination
- Market data integration
- Risk mitigation recommendations
- Confidence scoring
- Error handling and validation
"""

import unittest
import pytest
import numpy as np
import time
from typing import Dict, List
from unittest.mock import patch, MagicMock
from datetime import datetime

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analytics.risk_assessment import (
    RiskAssessmentEngine, RiskConfig, RiskCategory, RiskFactor,
    create_mock_market_data_for_risk_assessment, run_quick_risk_assessment
)
from src.shared.interfaces import RiskAssessment, RiskLevel, MarketData


class TestRiskAssessmentEngine(unittest.TestCase):
    """Test suite for RiskAssessmentEngine"""
    
    def setUp(self):
        self.engine = RiskAssessmentEngine()
        self.base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000,
            'down_payment_pct': 30.0,
            'interest_rate': 5.0,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0,
            'analysis_period': 20,
            'loan_term': 15,
            'annual_maintenance': 10000,
            'property_management': 0.0
        }
        self.market_data = create_mock_market_data_for_risk_assessment()
    
    def test_initialization(self):
        """Test engine initialization"""
        self.assertIsInstance(self.engine, RiskAssessmentEngine)
        self.assertIsInstance(self.engine.config, RiskConfig)
        self.assertEqual(self.engine._risk_cache, {})
    
    def test_custom_config_initialization(self):
        """Test initialization with custom config"""
        custom_config = RiskConfig(
            risk_tolerance="conservative",
            confidence_threshold=0.9,
            market_risk_weight=0.3
        )
        engine = RiskAssessmentEngine(custom_config)
        
        self.assertEqual(engine.config.risk_tolerance, "conservative")
        self.assertEqual(engine.config.confidence_threshold, 0.9)
        self.assertEqual(engine.config.market_risk_weight, 0.3)
    
    def test_assess_risk_basic(self):
        """Test basic risk assessment functionality"""
        result = self.engine.assess_risk(self.base_params, self.market_data)
        
        self.assertIsInstance(result, RiskAssessment)
        self.assertIsInstance(result.overall_risk_level, RiskLevel)
        self.assertIsInstance(result.risk_factors, dict)
        self.assertIsInstance(result.risk_description, str)
        self.assertIsInstance(result.mitigation_suggestions, list)
        self.assertIsInstance(result.confidence_score, float)
        
        # Check risk factors are in valid range
        for factor_name, score in result.risk_factors.items():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            self.assertIsInstance(factor_name, str)
        
        # Check confidence score is in valid range
        self.assertGreaterEqual(result.confidence_score, 0.0)
        self.assertLessEqual(result.confidence_score, 1.0)
        
        # Check risk description is meaningful
        self.assertGreater(len(result.risk_description), 10)
    
    def test_empty_parameters_error(self):
        """Test error handling for empty parameters"""
        with self.assertRaises(ValueError) as context:
            self.engine.assess_risk({}, self.market_data)
        self.assertIn("Analysis parameters cannot be empty", str(context.exception))
    
    def test_empty_market_data_error(self):
        """Test error handling for empty market data"""
        with self.assertRaises(ValueError) as context:
            self.engine.assess_risk(self.base_params, None)
        self.assertIn("Market data cannot be empty", str(context.exception))
    
    def test_market_risk_assessment(self):
        """Test market risk factor calculation"""
        market_risks = self.engine._assess_market_risk(self.base_params, self.market_data)
        
        self.assertIsInstance(market_risks, dict)
        expected_factors = [
            'property_market_volatility',
            'rental_market_risk', 
            'economic_environment_risk'
        ]
        
        for factor in expected_factors:
            self.assertIn(factor, market_risks)
            self.assertGreaterEqual(market_risks[factor], 0.0)
            self.assertLessEqual(market_risks[factor], 1.0)
    
    def test_financial_risk_assessment(self):
        """Test financial risk factor calculation"""
        financial_risks = self.engine._assess_financial_risk(self.base_params)
        
        self.assertIsInstance(financial_risks, dict)
        expected_factors = [
            'leverage_risk',
            'cash_flow_risk',
            'interest_rate_sensitivity'
        ]
        
        for factor in expected_factors:
            self.assertIn(factor, financial_risks)
            self.assertGreaterEqual(financial_risks[factor], 0.0)
            self.assertLessEqual(financial_risks[factor], 1.0)
    
    def test_liquidity_risk_assessment(self):
        """Test liquidity risk factor calculation"""
        liquidity_risks = self.engine._assess_liquidity_risk(self.base_params, self.market_data)
        
        self.assertIsInstance(liquidity_risks, dict)
        expected_factors = [
            'market_liquidity_risk',
            'investment_size_risk',
            'holding_period_risk'
        ]
        
        for factor in expected_factors:
            self.assertIn(factor, liquidity_risks)
            self.assertGreaterEqual(liquidity_risks[factor], 0.0)
            self.assertLessEqual(liquidity_risks[factor], 1.0)
    
    def test_interest_rate_risk_assessment(self):
        """Test interest rate risk factor calculation"""
        rate_risks = self.engine._assess_interest_rate_risk(self.base_params, self.market_data)
        
        self.assertIsInstance(rate_risks, dict)
        expected_factors = [
            'rate_level_risk',
            'rate_trend_risk',
            'refinancing_risk'
        ]
        
        for factor in expected_factors:
            self.assertIn(factor, rate_risks)
            self.assertGreaterEqual(rate_risks[factor], 0.0)
            self.assertLessEqual(rate_risks[factor], 1.0)
    
    def test_operational_risk_assessment(self):
        """Test operational risk factor calculation"""
        operational_risks = self.engine._assess_operational_risk(self.base_params)
        
        self.assertIsInstance(operational_risks, dict)
        expected_factors = [
            'maintenance_risk',
            'property_management_risk',
            'obsolescence_risk'
        ]
        
        for factor in expected_factors:
            self.assertIn(factor, operational_risks)
            self.assertGreaterEqual(operational_risks[factor], 0.0)
            self.assertLessEqual(operational_risks[factor], 1.0)
    
    def test_overall_risk_score_calculation(self):
        """Test overall risk score calculation"""
        # Create known risk factors
        risk_factors = {
            'property_market_volatility': 0.6,
            'rental_market_risk': 0.4,
            'economic_environment_risk': 0.5,
            'leverage_risk': 0.7,
            'cash_flow_risk': 0.3,
            'interest_rate_sensitivity': 0.5,
            'market_liquidity_risk': 0.4,
            'investment_size_risk': 0.3,
            'holding_period_risk': 0.2,
            'rate_level_risk': 0.6,
            'rate_trend_risk': 0.5,
            'refinancing_risk': 0.4,
            'maintenance_risk': 0.5,
            'property_management_risk': 0.6,
            'obsolescence_risk': 0.3
        }
        
        overall_score = self.engine._calculate_overall_risk_score(risk_factors)
        
        self.assertIsInstance(overall_score, float)
        self.assertGreaterEqual(overall_score, 0.0)
        self.assertLessEqual(overall_score, 1.0)
        
        # Score should be weighted average of category scores
        self.assertGreater(overall_score, 0.3)  # With these values, should be > 0.3
        self.assertLess(overall_score, 0.7)     # But < 0.7
    
    def test_risk_level_determination(self):
        """Test risk level determination logic"""
        # Test all risk levels
        test_cases = [
            (0.1, RiskLevel.LOW),
            (0.5, RiskLevel.MEDIUM),
            (0.7, RiskLevel.HIGH),
            (0.9, RiskLevel.CRITICAL)
        ]
        
        for score, expected_level in test_cases:
            level = self.engine._determine_risk_level(score)
            self.assertEqual(level, expected_level)
    
    def test_risk_description_generation(self):
        """Test risk description generation"""
        risk_factors = {
            'leverage_risk': 0.8,
            'market_liquidity_risk': 0.7,
            'interest_rate_sensitivity': 0.6
        }
        
        description = self.engine._generate_risk_description(
            RiskLevel.HIGH, risk_factors, 0.75
        )
        
        self.assertIsInstance(description, str)
        self.assertGreater(len(description), 20)
        self.assertIn("high risk", description.lower())
        self.assertIn("0.75", description)  # Should include score
    
    def test_mitigation_suggestions_generation(self):
        """Test mitigation suggestions generation"""
        high_risk_factors = {
            'leverage_risk': 0.8,
            'cash_flow_risk': 0.7,
            'market_liquidity_risk': 0.9,
            'interest_rate_sensitivity': 0.8
        }
        
        suggestions = self.engine._generate_mitigation_suggestions(
            high_risk_factors, RiskLevel.HIGH, self.base_params
        )
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        self.assertLessEqual(len(suggestions), 8)  # Should be capped
        
        # Should contain specific suggestions for high-risk factors
        suggestion_text = ' '.join(suggestions).lower()
        self.assertIn("down payment", suggestion_text)  # For leverage risk
        self.assertIn("cash", suggestion_text)  # For cash flow risk
    
    def test_confidence_score_calculation(self):
        """Test confidence score calculation"""
        risk_factors = {'test_factor': 0.5}
        
        confidence = self.engine._calculate_confidence_score(
            self.market_data, risk_factors, self.base_params
        )
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.1)  # Minimum bound
        self.assertLessEqual(confidence, 1.0)     # Maximum bound
    
    def test_high_leverage_scenario(self):
        """Test risk assessment with high leverage"""
        high_leverage_params = self.base_params.copy()
        high_leverage_params['down_payment_pct'] = 10.0  # High leverage (90% LTV)
        
        result = self.engine.assess_risk(high_leverage_params, self.market_data)
        
        # Should detect high leverage risk
        self.assertIn('leverage_risk', result.risk_factors)
        self.assertGreater(result.risk_factors['leverage_risk'], 0.5)
        
        # Overall risk should be higher
        self.assertIn(result.overall_risk_level, [RiskLevel.HIGH, RiskLevel.CRITICAL])
    
    def test_high_interest_rate_scenario(self):
        """Test risk assessment with high interest rates"""
        # Create market data with high interest rates
        high_rate_market = create_mock_market_data_for_risk_assessment()
        high_rate_market.current_mortgage_rates = {"30_year_fixed": 10.0, "15_year_fixed": 9.5}
        high_rate_market.rate_trend = "rising"
        
        result = self.engine.assess_risk(self.base_params, high_rate_market)
        
        # Should detect interest rate risk
        self.assertIn('rate_level_risk', result.risk_factors)
        self.assertGreater(result.risk_factors['rate_level_risk'], 0.5)
    
    def test_poor_market_conditions_scenario(self):
        """Test risk assessment with poor market conditions"""
        poor_market = create_mock_market_data_for_risk_assessment()
        poor_market.rental_vacancy_rate = 15.0  # High vacancy
        poor_market.property_appreciation_rate = -2.0  # Negative appreciation
        poor_market.unemployment_rate = 12.0  # High unemployment
        poor_market.months_on_market = 8.0  # Long time on market
        
        result = self.engine.assess_risk(self.base_params, poor_market)
        
        # Should detect multiple market risks
        self.assertIn('rental_market_risk', result.risk_factors)
        self.assertIn('property_market_volatility', result.risk_factors)
        self.assertIn('economic_environment_risk', result.risk_factors)
        self.assertIn('market_liquidity_risk', result.risk_factors)
        
        # Overall risk should be high
        self.assertIn(result.overall_risk_level, [RiskLevel.HIGH, RiskLevel.CRITICAL])
    
    def test_low_risk_scenario(self):
        """Test risk assessment with low-risk parameters"""
        low_risk_params = self.base_params.copy()
        low_risk_params['down_payment_pct'] = 50.0  # High down payment
        low_risk_params['interest_rate'] = 3.0     # Low interest rate
        low_risk_params['annual_maintenance'] = 5000  # Low maintenance
        low_risk_params['property_management'] = 3000  # Professional management
        
        # Good market conditions
        good_market = create_mock_market_data_for_risk_assessment()
        good_market.rental_vacancy_rate = 3.0
        good_market.property_appreciation_rate = 4.0
        good_market.unemployment_rate = 3.0
        good_market.months_on_market = 1.5
        good_market.current_mortgage_rates = {"30_year_fixed": 3.5}
        
        result = self.engine.assess_risk(low_risk_params, good_market)
        
        # Should have lower overall risk
        self.assertIn(result.overall_risk_level, [RiskLevel.LOW, RiskLevel.MEDIUM])
        
        # Most risk factors should be low
        low_risk_factors = [f for f, score in result.risk_factors.items() if score < 0.4]
        self.assertGreater(len(low_risk_factors), len(result.risk_factors) / 2)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def setUp(self):
        self.base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000,
            'down_payment_pct': 30.0,
            'interest_rate': 5.0,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0
        }
    
    def test_create_mock_market_data(self):
        """Test mock market data creation"""
        market_data = create_mock_market_data_for_risk_assessment("Test City")
        
        self.assertIsInstance(market_data, MarketData)
        self.assertEqual(market_data.location, "Test City")
        self.assertIsInstance(market_data.zip_code, str)
        self.assertGreater(market_data.median_rent_per_sqm, 0)
        self.assertGreater(market_data.median_property_price, 0)
        self.assertIsInstance(market_data.current_mortgage_rates, dict)
        self.assertGreater(market_data.confidence_score, 0)
        self.assertLessEqual(market_data.confidence_score, 1)
        self.assertIsInstance(market_data.data_timestamp, datetime)
    
    def test_run_quick_risk_assessment_with_market_data(self):
        """Test quick risk assessment with provided market data"""
        market_data = create_mock_market_data_for_risk_assessment()
        result = run_quick_risk_assessment(self.base_params, market_data)
        
        self.assertIsInstance(result, RiskAssessment)
        self.assertIsInstance(result.overall_risk_level, RiskLevel)
        self.assertIsInstance(result.risk_factors, dict)
        self.assertGreater(len(result.risk_factors), 0)
    
    def test_run_quick_risk_assessment_without_market_data(self):
        """Test quick risk assessment with default market data"""
        result = run_quick_risk_assessment(self.base_params)
        
        self.assertIsInstance(result, RiskAssessment)
        self.assertIsInstance(result.overall_risk_level, RiskLevel)
        self.assertIsInstance(result.risk_factors, dict)
        self.assertGreater(len(result.risk_factors), 0)


class TestRiskConfig(unittest.TestCase):
    """Test risk assessment configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = RiskConfig()
        
        self.assertEqual(config.risk_tolerance, "moderate")
        self.assertEqual(config.confidence_threshold, 0.75)
        self.assertEqual(config.max_acceptable_risk_score, 0.7)
        self.assertEqual(config.market_data_freshness_hours, 24.0)
        self.assertFalse(config.monte_carlo_integration)
        
        # Check risk factor weights sum to 1.0
        total_weight = (
            config.market_risk_weight +
            config.financial_risk_weight +
            config.liquidity_risk_weight +
            config.interest_rate_risk_weight +
            config.operational_risk_weight
        )
        self.assertAlmostEqual(total_weight, 1.0, places=2)
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = RiskConfig(
            risk_tolerance="conservative",
            confidence_threshold=0.9,
            market_risk_weight=0.4,
            financial_risk_weight=0.3,
            liquidity_risk_weight=0.1,
            interest_rate_risk_weight=0.1,
            operational_risk_weight=0.1
        )
        
        self.assertEqual(config.risk_tolerance, "conservative")
        self.assertEqual(config.confidence_threshold, 0.9)
        self.assertEqual(config.market_risk_weight, 0.4)
        
        # Check custom weights sum to 1.0
        total_weight = (
            config.market_risk_weight +
            config.financial_risk_weight +
            config.liquidity_risk_weight +
            config.interest_rate_risk_weight +
            config.operational_risk_weight
        )
        self.assertAlmostEqual(total_weight, 1.0, places=2)


class TestRiskFactor(unittest.TestCase):
    """Test RiskFactor dataclass"""
    
    def test_risk_factor_creation(self):
        """Test risk factor creation"""
        risk_factor = RiskFactor(
            name="test_risk",
            category=RiskCategory.MARKET_RISK,
            weight=0.3,
            current_value=0.6,
            risk_threshold_low=0.4,
            risk_threshold_high=0.8,
            description="Test risk factor"
        )
        
        self.assertEqual(risk_factor.name, "test_risk")
        self.assertEqual(risk_factor.category, RiskCategory.MARKET_RISK)
        self.assertEqual(risk_factor.weight, 0.3)
        self.assertEqual(risk_factor.current_value, 0.6)
        self.assertEqual(risk_factor.risk_threshold_low, 0.4)
        self.assertEqual(risk_factor.risk_threshold_high, 0.8)


class TestRiskCategory(unittest.TestCase):
    """Test RiskCategory enumeration"""
    
    def test_risk_categories_exist(self):
        """Test that all expected risk categories exist"""
        expected_categories = [
            "market_risk", "financial_risk", "liquidity_risk",
            "interest_rate_risk", "operational_risk", "regulatory_risk",
            "concentration_risk"
        ]
        
        for expected in expected_categories:
            category = RiskCategory(expected)
            self.assertEqual(category.value, expected)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        self.engine = RiskAssessmentEngine()
        self.base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000,
            'down_payment_pct': 30.0,
            'interest_rate': 5.0,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0
        }
        self.market_data = create_mock_market_data_for_risk_assessment()
    
    def test_zero_values(self):
        """Test handling of zero parameter values"""
        zero_params = self.base_params.copy()
        zero_params['down_payment_pct'] = 0.0  # No down payment
        zero_params['annual_maintenance'] = 0.0  # No maintenance
        zero_params['property_management'] = 0.0  # No property management
        
        result = self.engine.assess_risk(zero_params, self.market_data)
        
        # Should handle zeros without crashing
        self.assertIsInstance(result, RiskAssessment)
        self.assertIsInstance(result.overall_risk_level, RiskLevel)
    
    def test_negative_values(self):
        """Test handling of negative parameter values"""
        negative_params = self.base_params.copy()
        negative_params['market_appreciation_rate'] = -5.0  # Negative appreciation
        
        # Negative market data
        negative_market = create_mock_market_data_for_risk_assessment()
        negative_market.property_appreciation_rate = -3.0
        negative_market.population_growth_rate = -1.0
        
        result = self.engine.assess_risk(negative_params, negative_market)
        
        # Should handle negative values appropriately
        self.assertIsInstance(result, RiskAssessment)
        # Negative values should generally increase risk
        self.assertIn(result.overall_risk_level, [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL])
    
    def test_extreme_values(self):
        """Test handling of extreme parameter values"""
        extreme_params = self.base_params.copy()
        extreme_params['purchase_price'] = 100000000  # $100M property
        extreme_params['interest_rate'] = 50.0  # 50% interest rate
        extreme_params['down_payment_pct'] = 1.0  # 1% down payment
        
        # Extreme market data
        extreme_market = create_mock_market_data_for_risk_assessment()
        extreme_market.rental_vacancy_rate = 50.0  # 50% vacancy
        extreme_market.unemployment_rate = 30.0  # 30% unemployment
        extreme_market.months_on_market = 24.0  # 2 years on market
        
        result = self.engine.assess_risk(extreme_params, extreme_market)
        
        # Should handle extremes without crashing
        self.assertIsInstance(result, RiskAssessment)
        # Extreme values should result in high risk
        self.assertEqual(result.overall_risk_level, RiskLevel.CRITICAL)
    
    def test_missing_market_data_fields(self):
        """Test handling of incomplete market data"""
        incomplete_market = MarketData(
            location="Test",
            zip_code="12345",
            median_rent_per_sqm=20.0,
            rental_vacancy_rate=5.0,
            rental_growth_rate=3.0,
            median_property_price=400000.0,
            property_appreciation_rate=3.0,
            months_on_market=2.0,
            current_mortgage_rates={"30_year_fixed": 6.0},
            rate_trend="stable",
            local_inflation_rate=3.0,
            unemployment_rate=5.0,
            population_growth_rate=1.0,
            data_timestamp=datetime.now(),
            data_sources=["test"],
            confidence_score=0.8,
            freshness_hours=12.0
        )
        
        # Should handle incomplete data
        result = self.engine.assess_risk(self.base_params, incomplete_market)
        self.assertIsInstance(result, RiskAssessment)
    
    def test_very_low_confidence_market_data(self):
        """Test handling of low-confidence market data"""
        low_confidence_market = create_mock_market_data_for_risk_assessment()
        low_confidence_market.confidence_score = 0.1  # Very low confidence
        low_confidence_market.freshness_hours = 168.0  # Week-old data
        
        result = self.engine.assess_risk(self.base_params, low_confidence_market)
        
        # Should impact confidence score
        self.assertIsInstance(result, RiskAssessment)
        self.assertLess(result.confidence_score, 0.7)  # Should be lower confidence
    
    def test_all_risk_factors_high(self):
        """Test scenario where all risk factors are high"""
        high_risk_params = {
            'purchase_price': 2000000,  # Expensive property
            'current_annual_rent': 20000,  # Low rent relative to price
            'down_payment_pct': 5.0,  # Very low down payment
            'interest_rate': 12.0,  # High interest rate
            'market_appreciation_rate': -2.0,  # Negative appreciation
            'rent_increase_rate': 0.5,  # Low rent growth
            'cost_of_capital': 15.0,  # High cost of capital
            'analysis_period': 5,  # Short holding period
            'annual_maintenance': 50000,  # High maintenance
            'property_management': 0.0  # Self-managed
        }
        
        poor_market = create_mock_market_data_for_risk_assessment()
        poor_market.rental_vacancy_rate = 20.0
        poor_market.property_appreciation_rate = -5.0
        poor_market.unemployment_rate = 15.0
        poor_market.months_on_market = 12.0
        poor_market.current_mortgage_rates = {"30_year_fixed": 12.0}
        poor_market.rate_trend = "rising"
        
        result = self.engine.assess_risk(high_risk_params, poor_market)
        
        # Should be critical risk
        self.assertEqual(result.overall_risk_level, RiskLevel.CRITICAL)
        
        # Should have many risk factors above 0.5
        high_risk_factors = [f for f, score in result.risk_factors.items() if score > 0.5]
        self.assertGreater(len(high_risk_factors), len(result.risk_factors) * 0.6)
        
        # Should have many mitigation suggestions
        self.assertGreater(len(result.mitigation_suggestions), 3)


class TestPerformance(unittest.TestCase):
    """Test performance characteristics"""
    
    def setUp(self):
        self.engine = RiskAssessmentEngine()
        self.base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000,
            'down_payment_pct': 30.0,
            'interest_rate': 5.0,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0
        }
        self.market_data = create_mock_market_data_for_risk_assessment()
    
    def test_assessment_performance(self):
        """Test that risk assessment completes quickly"""
        start_time = time.time()
        result = self.engine.assess_risk(self.base_params, self.market_data)
        elapsed = time.time() - start_time
        
        self.assertLess(elapsed, 1.0)  # Should complete in under 1 second
        self.assertIsInstance(result, RiskAssessment)
    
    def test_multiple_assessments_performance(self):
        """Test performance with multiple consecutive assessments"""
        start_time = time.time()
        
        for _ in range(10):
            result = self.engine.assess_risk(self.base_params, self.market_data)
            self.assertIsInstance(result, RiskAssessment)
        
        elapsed = time.time() - start_time
        self.assertLess(elapsed, 5.0)  # 10 assessments in under 5 seconds


if __name__ == '__main__':
    unittest.main(verbosity=2)