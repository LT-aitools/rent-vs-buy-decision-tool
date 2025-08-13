"""
Unit tests for Monte Carlo Simulation Engine

Comprehensive test suite covering:
- Core Monte Carlo functionality
- Distribution generation and validation
- Statistical accuracy and convergence
- Performance requirements
- Error handling and edge cases
"""

import unittest
import pytest
import numpy as np
import time
from typing import Dict, List
from unittest.mock import patch, MagicMock
from scipy import stats

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analytics.monte_carlo import (
    MonteCarloEngine, MonteCarloConfig, DistributionGenerator,
    create_standard_distributions, run_quick_monte_carlo
)
from src.shared.interfaces import MonteCarloResult


class TestDistributionGenerator(unittest.TestCase):
    """Test distribution generation functionality"""
    
    def setUp(self):
        self.generator = DistributionGenerator()
        self.sample_size = 1000
    
    def test_normal_distribution(self):
        """Test normal distribution generation"""
        mean, std = 5.0, 1.0
        samples = self.generator.normal(mean, std, self.sample_size)
        
        self.assertEqual(len(samples), self.sample_size)
        self.assertAlmostEqual(np.mean(samples), mean, delta=0.2)
        self.assertAlmostEqual(np.std(samples), std, delta=0.2)
        self.assertTrue(np.all(np.isfinite(samples)))
    
    def test_uniform_distribution(self):
        """Test uniform distribution generation"""
        low, high = 2.0, 8.0
        samples = self.generator.uniform(low, high, self.sample_size)
        
        self.assertEqual(len(samples), self.sample_size)
        self.assertGreaterEqual(np.min(samples), low)
        self.assertLessEqual(np.max(samples), high)
        self.assertAlmostEqual(np.mean(samples), (low + high) / 2, delta=0.5)
    
    def test_triangular_distribution(self):
        """Test triangular distribution generation"""
        low, mode, high = 1.0, 3.0, 6.0
        samples = self.generator.triangular(low, mode, high, self.sample_size)
        
        self.assertEqual(len(samples), self.sample_size)
        self.assertGreaterEqual(np.min(samples), low)
        self.assertLessEqual(np.max(samples), high)
        # Mode should be most frequent value (approximately)
        hist, bins = np.histogram(samples, bins=50)
        mode_bin = bins[np.argmax(hist)]
        self.assertAlmostEqual(mode_bin, mode, delta=0.5)
    
    def test_lognormal_distribution(self):
        """Test lognormal distribution generation"""
        mean, sigma = 0.0, 0.5
        samples = self.generator.lognormal(mean, sigma, self.sample_size)
        
        self.assertEqual(len(samples), self.sample_size)
        self.assertTrue(np.all(samples > 0))  # Lognormal is always positive
        self.assertTrue(np.all(np.isfinite(samples)))
    
    def test_beta_distribution(self):
        """Test beta distribution generation"""
        alpha, beta_param, low, high = 2.0, 3.0, 1.0, 10.0
        samples = self.generator.beta(alpha, beta_param, low, high, self.sample_size)
        
        self.assertEqual(len(samples), self.sample_size)
        self.assertGreaterEqual(np.min(samples), low)
        self.assertLessEqual(np.max(samples), high)


class TestMonteCarloConfig(unittest.TestCase):
    """Test Monte Carlo configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = MonteCarloConfig()
        
        self.assertEqual(config.default_iterations, 15000)
        self.assertEqual(config.min_iterations, 10000)
        self.assertEqual(config.max_iterations, 50000)
        self.assertEqual(config.timeout_seconds, 4.5)
        self.assertEqual(config.confidence_levels, [90, 95, 99])
        self.assertEqual(config.percentiles, [5, 10, 25, 50, 75, 90, 95])
        self.assertIsNotNone(config.max_workers)
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = MonteCarloConfig(
            default_iterations=20000,
            timeout_seconds=10.0,
            confidence_levels=[95, 99],
            max_workers=2
        )
        
        self.assertEqual(config.default_iterations, 20000)
        self.assertEqual(config.timeout_seconds, 10.0)
        self.assertEqual(config.confidence_levels, [95, 99])
        self.assertEqual(config.max_workers, 2)


class TestMonteCarloEngine(unittest.TestCase):
    """Test Monte Carlo simulation engine"""
    
    def setUp(self):
        self.engine = MonteCarloEngine()
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
        self.test_distributions = {
            'interest_rate': {
                'distribution': 'normal',
                'params': [5.0, 0.5]
            },
            'market_appreciation_rate': {
                'distribution': 'uniform',
                'params': [2.0, 5.0]
            }
        }
    
    def test_initialization(self):
        """Test engine initialization"""
        self.assertIsInstance(self.engine, MonteCarloEngine)
        self.assertIsInstance(self.engine.config, MonteCarloConfig)
        self.assertIsInstance(self.engine.generator, DistributionGenerator)
    
    def test_basic_monte_carlo_simulation(self):
        """Test basic Monte Carlo simulation"""
        iterations = 5000  # Smaller for unit test
        result = self.engine.run_monte_carlo(
            self.base_params, 
            self.test_distributions, 
            iterations
        )
        
        self.assertIsInstance(result, MonteCarloResult)
        self.assertGreaterEqual(result.iterations, iterations * 0.8)  # Allow some failures
        self.assertTrue(np.isfinite(result.mean_npv))
        self.assertTrue(np.isfinite(result.std_dev))
        self.assertGreaterEqual(result.std_dev, 0)
        self.assertGreaterEqual(result.probability_positive, 0)
        self.assertLessEqual(result.probability_positive, 1)
    
    def test_performance_requirement(self):
        """Test performance requirement (<5 seconds)"""
        iterations = 12000
        start_time = time.time()
        result = self.engine.run_monte_carlo(
            self.base_params, 
            self.test_distributions, 
            iterations
        )
        elapsed = time.time() - start_time
        
        self.assertLess(elapsed, 5.0, "Monte Carlo should complete in under 5 seconds")
        self.assertGreater(result.iterations, 0, "Should complete some iterations")
    
    def test_empty_parameters_error(self):
        """Test error handling for empty parameters"""
        with self.assertRaises(ValueError) as context:
            self.engine.run_monte_carlo({}, self.test_distributions, 1000)
        self.assertIn("Base parameters cannot be empty", str(context.exception))
    
    def test_empty_distributions_error(self):
        """Test error handling for empty distributions"""
        with self.assertRaises(ValueError) as context:
            self.engine.run_monte_carlo(self.base_params, {}, 1000)
        self.assertIn("Variable distributions cannot be empty", str(context.exception))
    
    def test_iterations_bounds(self):
        """Test iteration bounds enforcement"""
        # Test minimum bound
        result_min = self.engine.run_monte_carlo(
            self.base_params, self.test_distributions, 100  # Below minimum
        )
        self.assertGreaterEqual(result_min.iterations, 8000)  # Should use minimum
        
        # Test maximum bound
        config = MonteCarloConfig(max_iterations=15000)
        engine_max = MonteCarloEngine(config)
        result_max = engine_max.run_monte_carlo(
            self.base_params, self.test_distributions, 100000  # Above maximum
        )
        self.assertLessEqual(result_max.iterations, 15000)  # Should cap at maximum
    
    def test_percentiles_ordering(self):
        """Test that percentiles are properly ordered"""
        result = self.engine.run_monte_carlo(
            self.base_params, self.test_distributions, 5000
        )
        
        percentile_values = []
        for p in [5, 25, 50, 75, 95]:
            if p in result.percentiles:
                percentile_values.append(result.percentiles[p])
        
        # Check that percentiles are in ascending order
        self.assertEqual(percentile_values, sorted(percentile_values))
    
    def test_confidence_intervals(self):
        """Test confidence interval calculation"""
        result = self.engine.run_monte_carlo(
            self.base_params, self.test_distributions, 5000
        )
        
        for level, (lower, upper) in result.confidence_intervals.items():
            self.assertLessEqual(lower, upper, f"Confidence interval {level}% should have lower <= upper")
            self.assertTrue(np.isfinite(lower) and np.isfinite(upper))
    
    def test_distribution_validation(self):
        """Test distribution validation"""
        # Test invalid distribution type
        invalid_distributions = {
            'interest_rate': {
                'distribution': 'invalid_type',
                'params': [5.0, 1.0]
            }
        }
        
        # Should handle invalid distribution gracefully
        result = self.engine.run_monte_carlo(
            self.base_params, invalid_distributions, 1000
        )
        self.assertIsInstance(result, MonteCarloResult)
    
    def test_all_distribution_types(self):
        """Test all supported distribution types"""
        distributions = {
            'var1': {'distribution': 'normal', 'params': [5.0, 1.0]},
            'var2': {'distribution': 'uniform', 'params': [2.0, 8.0]},
            'var3': {'distribution': 'triangular', 'params': [1.0, 3.0, 6.0]},
            'var4': {'distribution': 'lognormal', 'params': [0.0, 0.5]},
            'var5': {'distribution': 'beta', 'params': [2.0, 3.0, 1.0, 10.0]}
        }
        
        # Add these variables to base params
        extended_params = self.base_params.copy()
        extended_params.update({k: 5.0 for k in distributions.keys()})
        
        result = self.engine.run_monte_carlo(
            extended_params, distributions, 2000
        )
        
        self.assertIsInstance(result, MonteCarloResult)
        self.assertGreater(result.iterations, 1000)  # Should complete most iterations
    
    def test_statistical_properties(self):
        """Test statistical properties of results"""
        # Use known distribution to test statistical accuracy
        known_distributions = {
            'interest_rate': {
                'distribution': 'normal',
                'params': [5.0, 1.0]  # Mean=5, Std=1
            }
        }
        
        result = self.engine.run_monte_carlo(
            self.base_params, known_distributions, 10000
        )
        
        # Basic statistical checks
        self.assertTrue(np.isfinite(result.mean_npv))
        self.assertGreater(result.std_dev, 0)
        self.assertIsInstance(result.probability_positive, float)
        
        # Check percentiles make sense
        if 50 in result.percentiles and 25 in result.percentiles and 75 in result.percentiles:
            median = result.percentiles[50]
            q25 = result.percentiles[25]
            q75 = result.percentiles[75]
            self.assertLessEqual(q25, median)
            self.assertLessEqual(median, q75)
    
    def test_parallel_processing(self):
        """Test parallel processing functionality"""
        # Test with sufficient iterations to trigger parallel processing
        result = self.engine.run_monte_carlo(
            self.base_params, self.test_distributions, 8000
        )
        
        self.assertIsInstance(result, MonteCarloResult)
        self.assertGreater(result.iterations, 6000)  # Should complete most iterations
    
    def test_ensure_required_params(self):
        """Test parameter completion"""
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
    
    def test_performance_metrics(self):
        """Test performance tracking"""
        self.engine.run_monte_carlo(
            self.base_params, self.test_distributions, 5000
        )
        
        metrics = self.engine.get_simulation_performance()
        
        self.assertIn('last_simulation_time', metrics)
        self.assertIn('target_time', metrics)
        self.assertIn('performance_ratio', metrics)
        self.assertIn('meets_target', metrics)
        
        self.assertEqual(metrics['target_time'], 5.0)
        self.assertIsInstance(metrics['meets_target'], bool)


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
    
    def test_create_standard_distributions(self):
        """Test standard distributions creation"""
        distributions = create_standard_distributions(self.base_params)
        
        self.assertIsInstance(distributions, dict)
        self.assertGreater(len(distributions), 0)
        
        expected_variables = [
            'interest_rate', 'market_appreciation_rate', 
            'rent_increase_rate', 'cost_of_capital', 'purchase_price'
        ]
        
        for var in expected_variables:
            self.assertIn(var, distributions)
            self.assertIn('distribution', distributions[var])
            self.assertIn('params', distributions[var])
    
    def test_run_quick_monte_carlo(self):
        """Test quick Monte Carlo analysis"""
        result = run_quick_monte_carlo(self.base_params, iterations=5000)
        
        self.assertIsInstance(result, MonteCarloResult)
        self.assertGreater(result.iterations, 3000)
        self.assertTrue(np.isfinite(result.mean_npv))
    
    def test_custom_distributions_quick_analysis(self):
        """Test quick analysis with custom distributions"""
        custom_distributions = {
            'interest_rate': {
                'distribution': 'normal',
                'params': [6.0, 0.8]
            }
        }
        
        result = run_quick_monte_carlo(
            self.base_params, 
            custom_distributions, 
            iterations=3000
        )
        
        self.assertIsInstance(result, MonteCarloResult)
        self.assertGreater(result.iterations, 2000)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        self.engine = MonteCarloEngine()
        self.base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000,
            'down_payment_pct': 30.0,
            'interest_rate': 5.0,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0
        }
    
    def test_extreme_parameter_values(self):
        """Test handling of extreme parameter values"""
        extreme_params = self.base_params.copy()
        extreme_params['interest_rate'] = 50.0  # Extreme interest rate
        extreme_params['purchase_price'] = 1000000000  # Extreme price
        
        distributions = {
            'interest_rate': {
                'distribution': 'uniform',
                'params': [45.0, 55.0]
            }
        }
        
        # Should handle extreme values without crashing
        result = self.engine.run_monte_carlo(extreme_params, distributions, 1000)
        self.assertIsInstance(result, MonteCarloResult)
    
    def test_zero_standard_deviation(self):
        """Test handling of zero standard deviation"""
        distributions = {
            'interest_rate': {
                'distribution': 'normal',
                'params': [5.0, 0.0]  # Zero std dev
            }
        }
        
        # Should handle zero variance gracefully
        result = self.engine.run_monte_carlo(self.base_params, distributions, 1000)
        self.assertIsInstance(result, MonteCarloResult)
    
    def test_invalid_distribution_parameters(self):
        """Test handling of invalid distribution parameters"""
        invalid_distributions = {
            'var1': {'distribution': 'normal', 'params': []},  # No parameters
            'var2': {'distribution': 'uniform', 'params': [10.0, 5.0]},  # min > max
            'var3': {'distribution': 'triangular', 'params': [1.0, 5.0, 3.0]},  # mode > max
        }
        
        # Should validate and fix parameters
        validated = self.engine._validate_distributions(invalid_distributions)
        
        # Should have fixed the issues or removed invalid entries
        for var, config in validated.items():
            self.assertIn('distribution', config)
            self.assertIn('params', config)
            params = config['params']
            if config['distribution'] == 'uniform' and len(params) >= 2:
                self.assertLessEqual(params[0], params[1])
    
    def test_very_small_iterations(self):
        """Test handling of very small iteration counts"""
        result = self.engine.run_monte_carlo(
            self.base_params,
            {'interest_rate': {'distribution': 'normal', 'params': [5.0, 1.0]}},
            iterations=1  # Minimum possible
        )
        
        # Should enforce minimum iterations
        self.assertGreaterEqual(result.iterations, self.engine.config.min_iterations * 0.8)
    
    @patch('src.analytics.monte_carlo.calculate_npv_comparison')
    def test_calculation_failures(self, mock_calc):
        """Test handling of calculation failures"""
        # Make half the calculations fail
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:
                raise Exception("Calculation failed")
            return {'npv_difference': 100000}
        
        mock_calc.side_effect = side_effect
        
        result = self.engine.run_monte_carlo(
            self.base_params,
            {'interest_rate': {'distribution': 'normal', 'params': [5.0, 1.0]}},
            iterations=100
        )
        
        # Should handle failures gracefully
        self.assertIsInstance(result, MonteCarloResult)
        self.assertGreater(result.iterations, 0)  # Should have some successful iterations


if __name__ == '__main__':
    unittest.main(verbosity=2)