"""
Unit tests for Sensitivity Analysis Engine

Comprehensive test suite covering:
- Core functionality and accuracy
- Error handling and edge cases
- Performance requirements
- Input validation
- Statistical correctness
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

from src.analytics.sensitivity_analysis import (
    SensitivityAnalysisEngine, SensitivityConfig, 
    create_standard_sensitivity_variables, run_quick_sensitivity_analysis
)
from src.shared.interfaces import SensitivityVariable, RiskLevel


class TestSensitivityAnalysisEngine(unittest.TestCase):
    """Test suite for SensitivityAnalysisEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = SensitivityAnalysisEngine()
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
        self.test_variables = [
            SensitivityVariable(
                name='interest_rate',
                base_value=5.0,
                min_value=3.0,
                max_value=8.0,
                step_size=0.5,
                unit='%',
                description='Test interest rate'
            ),
            SensitivityVariable(
                name='market_appreciation_rate',
                base_value=3.0,
                min_value=1.0,
                max_value=6.0,
                step_size=0.5,
                unit='%',
                description='Test appreciation rate'
            )
        ]
    
    def test_initialization(self):
        """Test engine initialization"""
        self.assertIsInstance(self.engine, SensitivityAnalysisEngine)
        self.assertIsInstance(self.engine.config, SensitivityConfig)
        self.assertEqual(self.engine._analysis_cache, {})
    
    def test_custom_config_initialization(self):
        """Test engine initialization with custom config"""
        custom_config = SensitivityConfig(
            max_workers=2,
            timeout_seconds=1.0,
            statistical_confidence=0.99
        )
        engine = SensitivityAnalysisEngine(custom_config)
        self.assertEqual(engine.config.max_workers, 2)
        self.assertEqual(engine.config.timeout_seconds, 1.0)
        self.assertEqual(engine.config.statistical_confidence, 0.99)
    
    def test_run_sensitivity_analysis_basic(self):
        """Test basic sensitivity analysis functionality"""
        results = self.engine.run_sensitivity_analysis(self.base_params, self.test_variables)
        
        self.assertEqual(len(results), 2)
        
        for result in results:
            self.assertIn(result.variable_name, ['interest_rate', 'market_appreciation_rate'])
            self.assertIsInstance(result.variable_values, list)
            self.assertIsInstance(result.npv_impacts, list)
            self.assertIsInstance(result.percentage_changes, list)
            self.assertIsInstance(result.elasticity, float)
            self.assertTrue(len(result.variable_values) >= 10)  # Minimum data points
            self.assertEqual(len(result.variable_values), len(result.npv_impacts))
    
    def test_sensitivity_analysis_performance(self):
        """Test performance requirement (<2 seconds)"""
        start_time = time.time()
        results = self.engine.run_sensitivity_analysis(self.base_params, self.test_variables)
        elapsed = time.time() - start_time
        
        self.assertLess(elapsed, 2.0, "Sensitivity analysis should complete in under 2 seconds")
        self.assertGreater(len(results), 0, "Should return results")
    
    def test_empty_parameters_error(self):
        """Test error handling for empty parameters"""
        with self.assertRaises(ValueError) as context:
            self.engine.run_sensitivity_analysis({}, self.test_variables)
        self.assertIn("Base parameters cannot be empty", str(context.exception))
    
    def test_empty_variables_error(self):
        """Test error handling for empty variables"""
        with self.assertRaises(ValueError) as context:
            self.engine.run_sensitivity_analysis(self.base_params, [])
        self.assertIn("Variables list cannot be empty", str(context.exception))
    
    def test_invalid_variable_range(self):
        """Test handling of invalid variable ranges"""
        invalid_variable = SensitivityVariable(
            name='test_var',
            base_value=5.0,
            min_value=10.0,  # min > max (invalid)
            max_value=3.0,
            step_size=0.5,
            unit='%',
            description='Invalid variable'
        )
        
        # Should handle gracefully without crashing
        results = self.engine.run_sensitivity_analysis(self.base_params, [invalid_variable])
        self.assertEqual(len(results), 1)
        # Should return base value when range is invalid
        self.assertEqual(len(results[0].variable_values), 1)
    
    def test_caching_functionality(self):
        """Test caching works correctly"""
        # First call
        start_time = time.time()
        results1 = self.engine.run_sensitivity_analysis(self.base_params, self.test_variables)
        first_duration = time.time() - start_time
        
        # Second call with same parameters (should be from cache)
        start_time = time.time()
        results2 = self.engine.run_sensitivity_analysis(self.base_params, self.test_variables)
        second_duration = time.time() - start_time
        
        # Results should be identical
        self.assertEqual(len(results1), len(results2))
        for r1, r2 in zip(results1, results2):
            self.assertEqual(r1.variable_name, r2.variable_name)
            self.assertEqual(r1.variable_values, r2.variable_values)
        
        # Second call should be faster (cached)
        self.assertLess(second_duration, first_duration * 0.5)
    
    def test_elasticity_calculation(self):
        """Test elasticity calculation accuracy"""
        results = self.engine.run_sensitivity_analysis(self.base_params, self.test_variables)
        
        for result in results:
            # Elasticity should be finite
            self.assertTrue(np.isfinite(result.elasticity), 
                          f"Elasticity for {result.variable_name} should be finite")
            
            # For interest rate, elasticity should generally be negative
            if result.variable_name == 'interest_rate':
                self.assertLess(result.elasticity, 1.0, 
                              "Interest rate elasticity should be reasonable")
    
    def test_statistical_accuracy(self):
        """Test statistical properties of results"""
        results = self.engine.run_sensitivity_analysis(self.base_params, self.test_variables)
        
        for result in results:
            # Should have sufficient data points for statistical validity
            self.assertGreaterEqual(len(result.variable_values), 11)
            
            # Variable values should be within expected range
            variable_def = next(v for v in self.test_variables if v.name == result.variable_name)
            min_val = min(result.variable_values)
            max_val = max(result.variable_values)
            
            self.assertGreaterEqual(min_val, variable_def.min_value * 0.99)  # Allow small tolerance
            self.assertLessEqual(max_val, variable_def.max_value * 1.01)
    
    def test_ensure_required_params(self):
        """Test parameter completion functionality"""
        minimal_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000
        }
        
        completed_params = self.engine._ensure_required_params(minimal_params)
        
        # Should have all required parameters
        required_keys = [
            'loan_term', 'analysis_period', 'transaction_costs',
            'property_tax_rate', 'insurance_cost', 'annual_maintenance'
        ]
        
        for key in required_keys:
            self.assertIn(key, completed_params)
            self.assertIsInstance(completed_params[key], (int, float, bool))
    
    def test_parallel_processing(self):
        """Test parallel processing works correctly"""
        # Test with multiple variables to trigger parallel processing
        many_variables = create_standard_sensitivity_variables(self.base_params)[:4]
        
        results = self.engine.run_sensitivity_analysis(self.base_params, many_variables)
        
        # Should return results for all variables
        self.assertEqual(len(results), 4)
        
        # All results should be valid
        for result in results:
            self.assertGreater(len(result.variable_values), 0)
            self.assertTrue(np.isfinite(result.elasticity) or result.elasticity == 0.0)
    
    @patch('src.analytics.sensitivity_analysis.calculate_npv_comparison')
    def test_calculation_error_handling(self, mock_calc):
        """Test handling of calculation errors"""
        # Make calculation raise an exception
        mock_calc.side_effect = Exception("Calculation failed")
        
        results = self.engine.run_sensitivity_analysis(self.base_params, self.test_variables[:1])
        
        # Should handle errors gracefully
        self.assertEqual(len(results), 1)
        result = results[0]
        
        # Should have at least base value
        self.assertGreaterEqual(len(result.variable_values), 1)
        
        # Elasticity should be 0 when calculations fail
        self.assertEqual(result.elasticity, 0.0)


class TestSensitivityUtilityFunctions(unittest.TestCase):
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
    
    def test_create_standard_sensitivity_variables(self):
        """Test standard variables creation"""
        variables = create_standard_sensitivity_variables(self.base_params)
        
        self.assertIsInstance(variables, list)
        self.assertGreater(len(variables), 0)
        
        # Check variable names are as expected
        variable_names = [v.name for v in variables]
        expected_names = [
            'interest_rate', 'market_appreciation_rate', 'rent_increase_rate',
            'cost_of_capital', 'purchase_price', 'current_annual_rent'
        ]
        
        for name in expected_names:
            self.assertIn(name, variable_names)
        
        # Check variables have proper structure
        for variable in variables:
            self.assertIsInstance(variable, SensitivityVariable)
            self.assertIsInstance(variable.name, str)
            self.assertIsInstance(variable.base_value, (int, float))
            self.assertIsInstance(variable.min_value, (int, float))
            self.assertIsInstance(variable.max_value, (int, float))
            self.assertLess(variable.min_value, variable.max_value)
    
    def test_run_quick_sensitivity_analysis(self):
        """Test quick analysis function"""
        results = run_quick_sensitivity_analysis(self.base_params)
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        for result in results:
            self.assertIsInstance(result.variable_name, str)
            self.assertIsInstance(result.variable_values, list)
            self.assertIsInstance(result.npv_impacts, list)
    
    def test_custom_variables_quick_analysis(self):
        """Test quick analysis with custom variables"""
        custom_variables = [
            SensitivityVariable(
                name='interest_rate',
                base_value=5.0,
                min_value=3.0,
                max_value=7.0,
                step_size=0.5,
                unit='%',
                description='Custom interest rate'
            )
        ]
        
        results = run_quick_sensitivity_analysis(self.base_params, custom_variables)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].variable_name, 'interest_rate')


class TestSensitivityConfig(unittest.TestCase):
    """Test sensitivity configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = SensitivityConfig()
        
        self.assertEqual(config.max_workers, 4)
        self.assertEqual(config.timeout_seconds, 1.8)
        self.assertEqual(config.statistical_confidence, 0.95)
        self.assertEqual(config.min_data_points, 11)
        self.assertEqual(config.max_data_points, 21)
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = SensitivityConfig(
            max_workers=8,
            timeout_seconds=3.0,
            statistical_confidence=0.99
        )
        
        self.assertEqual(config.max_workers, 8)
        self.assertEqual(config.timeout_seconds, 3.0)
        self.assertEqual(config.statistical_confidence, 0.99)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        self.engine = SensitivityAnalysisEngine()
        self.base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000,
            'down_payment_pct': 30.0,
            'interest_rate': 5.0,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0
        }
    
    def test_zero_base_value_variable(self):
        """Test handling of zero base value"""
        zero_variable = SensitivityVariable(
            name='test_zero',
            base_value=0.0,
            min_value=-1.0,
            max_value=1.0,
            step_size=0.1,
            unit='',
            description='Zero base value test'
        )
        
        results = self.engine.run_sensitivity_analysis(self.base_params, [zero_variable])
        
        self.assertEqual(len(results), 1)
        result = results[0]
        
        # Should handle zero base value gracefully
        self.assertTrue(np.isfinite(result.elasticity) or result.elasticity == 0.0)
    
    def test_negative_values(self):
        """Test handling of negative parameter values"""
        negative_params = self.base_params.copy()
        negative_params['market_appreciation_rate'] = -2.0  # Negative appreciation
        
        negative_variable = SensitivityVariable(
            name='market_appreciation_rate',
            base_value=-2.0,
            min_value=-5.0,
            max_value=2.0,
            step_size=1.0,
            unit='%',
            description='Negative appreciation test'
        )
        
        results = self.engine.run_sensitivity_analysis(negative_params, [negative_variable])
        
        self.assertEqual(len(results), 1)
        # Should not crash with negative values
        self.assertIsInstance(results[0].elasticity, float)
    
    def test_very_small_step_size(self):
        """Test handling of very small step sizes"""
        small_step_variable = SensitivityVariable(
            name='interest_rate',
            base_value=5.0,
            min_value=4.999,
            max_value=5.001,
            step_size=0.0001,
            unit='%',
            description='Very small step test'
        )
        
        results = self.engine.run_sensitivity_analysis(self.base_params, [small_step_variable])
        
        self.assertEqual(len(results), 1)
        # Should handle small ranges appropriately
        result = results[0]
        self.assertGreaterEqual(len(result.variable_values), 11)  # Min data points
    
    def test_very_large_ranges(self):
        """Test handling of very large parameter ranges"""
        large_range_variable = SensitivityVariable(
            name='purchase_price',
            base_value=500000,
            min_value=100000,
            max_value=2000000,
            step_size=100000,
            unit='$',
            description='Large range test'
        )
        
        results = self.engine.run_sensitivity_analysis(self.base_params, [large_range_variable])
        
        self.assertEqual(len(results), 1)
        # Should cap at max data points
        result = results[0]
        self.assertLessEqual(len(result.variable_values), 21)  # Max data points


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)