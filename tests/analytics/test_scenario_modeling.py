"""
Unit tests for Scenario Modeling Engine

Comprehensive test suite covering:
- Economic scenario creation and analysis
- Custom scenario functionality
- Scenario ranking and comparison
- Expected value calculations
- Error handling and validation
"""

import unittest
import pytest
import numpy as np
import time
from typing import Dict, List
from unittest.mock import patch, MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analytics.scenario_modeling import (
    ScenarioModelingEngine, ScenarioConfig, EconomicScenarioType,
    run_quick_scenario_analysis
)
from src.shared.interfaces import ScenarioDefinition


class TestScenarioModelingEngine(unittest.TestCase):
    """Test suite for ScenarioModelingEngine"""
    
    def setUp(self):
        self.engine = ScenarioModelingEngine()
        self.base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000,
            'down_payment_pct': 30.0,
            'interest_rate': 5.0,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0,
            'analysis_period': 20,
            'loan_term': 15
        }
    
    def test_initialization(self):
        """Test engine initialization"""
        self.assertIsInstance(self.engine, ScenarioModelingEngine)
        self.assertIsInstance(self.engine.config, ScenarioConfig)
        self.assertEqual(self.engine._scenario_cache, {})
    
    def test_custom_config_initialization(self):
        """Test initialization with custom config"""
        custom_config = ScenarioConfig(
            max_workers=2,
            timeout_seconds=5.0,
            include_monte_carlo=True
        )
        engine = ScenarioModelingEngine(custom_config)
        
        self.assertEqual(engine.config.max_workers, 2)
        self.assertEqual(engine.config.timeout_seconds, 5.0)
        self.assertTrue(engine.config.include_monte_carlo)
    
    def test_create_economic_scenarios(self):
        """Test creation of standard economic scenarios"""
        scenarios = self.engine.create_economic_scenarios(self.base_params)
        
        self.assertIsInstance(scenarios, list)
        self.assertGreater(len(scenarios), 0)
        
        scenario_names = [s.name for s in scenarios]
        expected_scenarios = [
            "Economic Recession", "Economic Growth", "High Interest Rates",
            "Property Market Boom", "Economic Stability"
        ]
        
        for expected in expected_scenarios:
            self.assertIn(expected, scenario_names)
        
        # Test scenario properties
        for scenario in scenarios:
            self.assertIsInstance(scenario, ScenarioDefinition)
            self.assertIsInstance(scenario.name, str)
            self.assertIsInstance(scenario.description, str)
            self.assertIsInstance(scenario.parameters, dict)
            self.assertGreater(len(scenario.parameters), 0)
            
            if scenario.probability is not None:
                self.assertGreaterEqual(scenario.probability, 0.0)
                self.assertLessEqual(scenario.probability, 1.0)
    
    def test_scenario_parameter_logic(self):
        """Test that economic scenarios have logical parameter changes"""
        scenarios = self.engine.create_economic_scenarios(self.base_params)
        
        recession_scenario = next(s for s in scenarios if "Recession" in s.name)
        growth_scenario = next(s for s in scenarios if "Growth" in s.name)
        
        # Recession should have higher interest rates than base
        base_rate = self.base_params['interest_rate']
        recession_rate = recession_scenario.parameters.get('interest_rate', base_rate)
        self.assertGreater(recession_rate, base_rate)
        
        # Growth scenario should have higher appreciation than base
        base_appreciation = self.base_params['market_appreciation_rate']
        growth_appreciation = growth_scenario.parameters.get('market_appreciation_rate', base_appreciation)
        self.assertGreater(growth_appreciation, base_appreciation)
    
    def test_create_custom_scenario(self):
        """Test custom scenario creation"""
        custom_scenario = self.engine.create_custom_scenario(
            name="Custom Test Scenario",
            description="A test scenario",
            parameter_variations={'interest_rate': 7.0, 'market_appreciation_rate': 5.0},
            probability=0.25
        )
        
        self.assertIsInstance(custom_scenario, ScenarioDefinition)
        self.assertEqual(custom_scenario.name, "Custom Test Scenario")
        self.assertEqual(custom_scenario.description, "A test scenario")
        self.assertEqual(custom_scenario.parameters['interest_rate'], 7.0)
        self.assertEqual(custom_scenario.parameters['market_appreciation_rate'], 5.0)
        self.assertEqual(custom_scenario.probability, 0.25)
    
    def test_run_scenario_analysis(self):
        """Test basic scenario analysis functionality"""
        scenarios = self.engine.create_economic_scenarios(self.base_params)[:3]  # Test with 3 scenarios
        
        results = self.engine.run_scenario_analysis(self.base_params, scenarios)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 3)  # Should include base case + scenarios + summary
        
        # Check for base case
        base_case = next((r for r in results if r.get('scenario_name') == 'Base Case'), None)
        self.assertIsNotNone(base_case)
        self.assertIn('npv_difference', base_case)
        self.assertIn('recommendation', base_case)
        
        # Check scenario results
        scenario_results = [r for r in results if r.get('scenario_name') in [s.name for s in scenarios]]
        self.assertEqual(len(scenario_results), 3)
        
        for result in scenario_results:
            self.assertIn('npv_difference', result)
            self.assertIn('recommendation', result)
            self.assertIn('vs_base_case', result)
            self.assertIn('calculation_successful', result)
    
    def test_empty_parameters_error(self):
        """Test error handling for empty parameters"""
        scenarios = self.engine.create_economic_scenarios(self.base_params)[:1]
        
        with self.assertRaises(ValueError) as context:
            self.engine.run_scenario_analysis({}, scenarios)
        self.assertIn("Base parameters cannot be empty", str(context.exception))
    
    def test_empty_scenarios_error(self):
        """Test error handling for empty scenarios"""
        with self.assertRaises(ValueError) as context:
            self.engine.run_scenario_analysis(self.base_params, [])
        self.assertIn("Scenarios list cannot be empty", str(context.exception))
    
    def test_scenario_ranking(self):
        """Test scenario ranking functionality"""
        scenarios = self.engine.create_economic_scenarios(self.base_params)[:3]
        results = self.engine.run_scenario_analysis(self.base_params, scenarios)
        
        scenario_results = [r for r in results if r.get('calculation_successful', False) and 'vs_base_case' in r]
        
        if len(scenario_results) > 1:
            # Test NPV difference ranking
            ranked_npv = self.engine.rank_scenarios(scenario_results, 'npv_difference')
            self.assertEqual(len(ranked_npv), len(scenario_results))
            
            # Check ranking order
            for i in range(len(ranked_npv) - 1):
                current_npv = ranked_npv[i].get('npv_difference', float('-inf'))
                next_npv = ranked_npv[i + 1].get('npv_difference', float('-inf'))
                self.assertGreaterEqual(current_npv, next_npv)
            
            # Check rank numbers
            for i, result in enumerate(ranked_npv):
                self.assertEqual(result['rank'], i + 1)
    
    def test_expected_value_calculation(self):
        """Test probability-weighted expected value calculation"""
        # Create scenarios with probabilities
        scenarios = [
            ScenarioDefinition("Scenario A", "Test A", {'interest_rate': 4.0}, 0.3),
            ScenarioDefinition("Scenario B", "Test B", {'interest_rate': 6.0}, 0.5),
            ScenarioDefinition("Scenario C", "Test C", {'interest_rate': 8.0}, 0.2)
        ]
        
        results = self.engine.run_scenario_analysis(self.base_params, scenarios)
        scenario_results = [r for r in results if r.get('probability') is not None and r.get('calculation_successful', False)]
        
        if len(scenario_results) > 0:
            expected_value = self.engine.calculate_expected_value(scenario_results)
            
            self.assertIsInstance(expected_value, dict)
            self.assertIn('expected_npv_difference', expected_value)
            self.assertIn('expected_ownership_npv', expected_value)
            self.assertIn('expected_rental_npv', expected_value)
            self.assertIn('npv_standard_deviation', expected_value)
            self.assertIn('total_probability', expected_value)
            self.assertIn('valid_scenarios', expected_value)
            
            # Check probability normalization
            total_prob = expected_value['total_probability']
            self.assertAlmostEqual(total_prob, 1.0, delta=0.1)  # Allow some tolerance
            
            # Check that standard deviation is non-negative
            self.assertGreaterEqual(expected_value['npv_standard_deviation'], 0)
    
    def test_analyze_scenario_sensitivity(self):
        """Test sensitivity analysis within scenarios"""
        scenario = self.engine.create_economic_scenarios(self.base_params)[0]  # Use first scenario
        sensitivity_params = ['interest_rate', 'market_appreciation_rate']
        
        sensitivity_result = self.engine.analyze_scenario_sensitivity(
            self.base_params, scenario, sensitivity_params
        )
        
        self.assertIsInstance(sensitivity_result, dict)
        self.assertIn('scenario_name', sensitivity_result)
        self.assertIn('sensitivity_results', sensitivity_result)
        self.assertIn('scenario_parameters', sensitivity_result)
        
        self.assertEqual(sensitivity_result['scenario_name'], scenario.name)
        
        # Check sensitivity results for each parameter
        for param in sensitivity_params:
            if param in scenario.parameters:
                self.assertIn(param, sensitivity_result['sensitivity_results'])
                param_result = sensitivity_result['sensitivity_results'][param]
                
                self.assertIn('test_values', param_result)
                self.assertIn('results', param_result)
                self.assertIn('base_value', param_result)
                
                self.assertIsInstance(param_result['test_values'], list)
                self.assertIsInstance(param_result['results'], list)
    
    def test_parallel_processing(self):
        """Test parallel processing of scenarios"""
        # Create multiple scenarios to trigger parallel processing
        scenarios = self.engine.create_economic_scenarios(self.base_params)
        
        start_time = time.time()
        results = self.engine.run_scenario_analysis(self.base_params, scenarios)
        elapsed = time.time() - start_time
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), len(scenarios))  # Should include base case and summary
        
        # Should complete in reasonable time with parallel processing
        self.assertLess(elapsed, 10.0)
    
    def test_ensure_required_params(self):
        """Test parameter completion functionality"""
        minimal_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000
        }
        
        completed_params = self.engine._ensure_required_params(minimal_params)
        
        required_keys = [
            'loan_term', 'analysis_period', 'transaction_costs',
            'property_tax_rate', 'insurance_cost'
        ]
        
        for key in required_keys:
            self.assertIn(key, completed_params)
    
    @patch('src.analytics.scenario_modeling.calculate_npv_comparison')
    def test_calculation_error_handling(self, mock_calc):
        """Test handling of calculation errors"""
        mock_calc.side_effect = Exception("NPV calculation failed")
        
        scenarios = [self.engine.create_economic_scenarios(self.base_params)[0]]
        results = self.engine.run_scenario_analysis(self.base_params, scenarios)
        
        # Should handle errors gracefully
        self.assertIsInstance(results, list)
        
        # Check that error results are properly formatted
        error_results = [r for r in results if not r.get('calculation_successful', True)]
        if error_results:
            for result in error_results:
                self.assertIn('error_message', result)
                self.assertIn('scenario_name', result)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions"""
    
    def setUp(self):
        self.base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000,
            'interest_rate': 5.0,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0
        }
    
    def test_run_quick_scenario_analysis_default(self):
        """Test quick scenario analysis with defaults"""
        results = run_quick_scenario_analysis(self.base_params)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Should include base case and scenarios
        scenario_names = [r.get('scenario_name', '') for r in results]
        self.assertIn('Base Case', scenario_names)
    
    def test_run_quick_scenario_analysis_economic_only(self):
        """Test quick analysis with only economic scenarios"""
        results = run_quick_scenario_analysis(
            self.base_params, 
            include_economic_scenarios=True,
            custom_scenarios=None
        )
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 5)  # Base + 5 economic scenarios + summary
    
    def test_run_quick_scenario_analysis_custom_only(self):
        """Test quick analysis with custom scenarios"""
        custom_scenarios = [
            ScenarioDefinition(
                name="Custom High Rates",
                description="High interest rate scenario",
                parameters={'interest_rate': 9.0},
                probability=0.3
            ),
            ScenarioDefinition(
                name="Custom Low Rates",
                description="Low interest rate scenario", 
                parameters={'interest_rate': 2.0},
                probability=0.7
            )
        ]
        
        results = run_quick_scenario_analysis(
            self.base_params,
            include_economic_scenarios=False,
            custom_scenarios=custom_scenarios
        )
        
        self.assertIsInstance(results, list)
        custom_result_names = [r.get('scenario_name', '') for r in results]
        self.assertIn("Custom High Rates", custom_result_names)
        self.assertIn("Custom Low Rates", custom_result_names)
    
    def test_run_quick_scenario_analysis_mixed(self):
        """Test quick analysis with both economic and custom scenarios"""
        custom_scenario = ScenarioDefinition(
            name="Mixed Custom",
            description="Custom mixed scenario",
            parameters={'interest_rate': 7.5, 'market_appreciation_rate': 2.0}
        )
        
        results = run_quick_scenario_analysis(
            self.base_params,
            include_economic_scenarios=True,
            custom_scenarios=[custom_scenario]
        )
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 6)  # Should have both types
        
        result_names = [r.get('scenario_name', '') for r in results]
        self.assertIn("Mixed Custom", result_names)
        self.assertIn("Base Case", result_names)


class TestScenarioConfig(unittest.TestCase):
    """Test scenario configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = ScenarioConfig()
        
        self.assertEqual(config.max_workers, 4)
        self.assertEqual(config.timeout_seconds, 10.0)
        self.assertFalse(config.include_monte_carlo)
        self.assertEqual(config.monte_carlo_iterations, 5000)
        self.assertEqual(config.confidence_levels, [90, 95])
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = ScenarioConfig(
            max_workers=8,
            timeout_seconds=20.0,
            include_monte_carlo=True,
            monte_carlo_iterations=10000,
            confidence_levels=[95, 99]
        )
        
        self.assertEqual(config.max_workers, 8)
        self.assertEqual(config.timeout_seconds, 20.0)
        self.assertTrue(config.include_monte_carlo)
        self.assertEqual(config.monte_carlo_iterations, 10000)
        self.assertEqual(config.confidence_levels, [95, 99])


class TestEconomicScenarioTypes(unittest.TestCase):
    """Test economic scenario type enumeration"""
    
    def test_scenario_types_exist(self):
        """Test that all expected scenario types exist"""
        expected_types = [
            "recession", "stable", "growth", "boom", 
            "high_inflation", "deflation"
        ]
        
        for expected in expected_types:
            # Should be able to create enum value
            scenario_type = EconomicScenarioType(expected)
            self.assertEqual(scenario_type.value, expected)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        self.engine = ScenarioModelingEngine()
        self.base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000,
            'down_payment_pct': 30.0,
            'interest_rate': 5.0,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0
        }
    
    def test_extreme_scenario_parameters(self):
        """Test handling of extreme scenario parameters"""
        extreme_scenario = ScenarioDefinition(
            name="Extreme Scenario",
            description="Extreme parameter values",
            parameters={
                'interest_rate': 100.0,  # Extreme rate
                'market_appreciation_rate': -50.0,  # Extreme negative appreciation
                'cost_of_capital': 0.1  # Very low cost of capital
            }
        )
        
        # Should handle extreme values without crashing
        results = self.engine.run_scenario_analysis(self.base_params, [extreme_scenario])
        self.assertIsInstance(results, list)
    
    def test_zero_probability_scenarios(self):
        """Test handling of zero probability scenarios"""
        zero_prob_scenario = ScenarioDefinition(
            name="Zero Probability",
            description="Zero probability scenario",
            parameters={'interest_rate': 6.0},
            probability=0.0
        )
        
        results = self.engine.run_scenario_analysis(self.base_params, [zero_prob_scenario])
        scenario_results = [r for r in results if r.get('scenario_name') == 'Zero Probability']
        
        if scenario_results:
            expected_value = self.engine.calculate_expected_value(scenario_results)
            # Should handle zero probability gracefully
            self.assertIsInstance(expected_value, dict)
    
    def test_missing_scenario_parameters(self):
        """Test handling of scenarios with missing parameters"""
        minimal_scenario = ScenarioDefinition(
            name="Minimal Scenario",
            description="Scenario with minimal parameters",
            parameters={}  # No parameters
        )
        
        # Should use base parameters when scenario parameters are missing
        results = self.engine.run_scenario_analysis(self.base_params, [minimal_scenario])
        self.assertIsInstance(results, list)
        
        minimal_result = next((r for r in results if r.get('scenario_name') == 'Minimal Scenario'), None)
        if minimal_result:
            # Should have same result as base case (approximately)
            base_result = next((r for r in results if r.get('scenario_name') == 'Base Case'), None)
            if base_result:
                self.assertAlmostEqual(
                    minimal_result.get('npv_difference', 0),
                    base_result.get('npv_difference', 0),
                    delta=1000  # Small tolerance for calculation differences
                )
    
    def test_duplicate_scenario_names(self):
        """Test handling of duplicate scenario names"""
        scenario1 = ScenarioDefinition("Duplicate", "First", {'interest_rate': 4.0})
        scenario2 = ScenarioDefinition("Duplicate", "Second", {'interest_rate': 6.0})
        
        results = self.engine.run_scenario_analysis(self.base_params, [scenario1, scenario2])
        
        # Should handle duplicates without crashing
        self.assertIsInstance(results, list)
        
        duplicate_results = [r for r in results if r.get('scenario_name') == 'Duplicate']
        # Should have results for both scenarios (or handle appropriately)
        self.assertGreaterEqual(len(duplicate_results), 1)
    
    def test_very_long_scenario_descriptions(self):
        """Test handling of very long scenario descriptions"""
        long_description = "A" * 10000  # Very long description
        long_desc_scenario = ScenarioDefinition(
            name="Long Description",
            description=long_description,
            parameters={'interest_rate': 5.5}
        )
        
        results = self.engine.run_scenario_analysis(self.base_params, [long_desc_scenario])
        
        # Should handle long descriptions without issues
        self.assertIsInstance(results, list)
        long_result = next((r for r in results if r.get('scenario_name') == 'Long Description'), None)
        if long_result:
            self.assertEqual(long_result.get('description'), long_description)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        self.engine = ScenarioModelingEngine()
        self.base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000,
            'down_payment_pct': 30.0,
            'interest_rate': 5.0,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0,
            'analysis_period': 20,
            'loan_term': 15
        }
    
    def test_full_workflow(self):
        """Test complete scenario analysis workflow"""
        # Step 1: Create economic scenarios
        scenarios = self.engine.create_economic_scenarios(self.base_params)
        self.assertGreater(len(scenarios), 0)
        
        # Step 2: Add custom scenario
        custom_scenario = self.engine.create_custom_scenario(
            "Custom Test",
            "Custom test scenario",
            {'interest_rate': 7.0},
            0.25
        )
        scenarios.append(custom_scenario)
        
        # Step 3: Run analysis
        results = self.engine.run_scenario_analysis(self.base_params, scenarios)
        self.assertIsInstance(results, list)
        
        # Step 4: Rank scenarios
        scenario_results = [r for r in results if r.get('calculation_successful', False) and 'vs_base_case' in r]
        if len(scenario_results) > 1:
            ranked = self.engine.rank_scenarios(scenario_results)
            self.assertEqual(len(ranked), len(scenario_results))
        
        # Step 5: Calculate expected value
        prob_results = [r for r in results if r.get('probability') is not None and r.get('calculation_successful', False)]
        if prob_results:
            expected = self.engine.calculate_expected_value(prob_results)
            self.assertIsInstance(expected, dict)
        
        # Step 6: Sensitivity within scenario
        if scenarios:
            sens_result = self.engine.analyze_scenario_sensitivity(
                self.base_params, 
                scenarios[0], 
                ['interest_rate']
            )
            self.assertIsInstance(sens_result, dict)


if __name__ == '__main__':
    unittest.main(verbosity=2)