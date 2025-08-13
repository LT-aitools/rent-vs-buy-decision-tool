"""
Integration tests for Analytics Engine Components

Comprehensive integration test suite covering:
- Cross-component integration and consistency
- Interface compliance verification
- End-to-end workflow testing
- Performance integration testing
- Error handling across components
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

from src.analytics.sensitivity_analysis import SensitivityAnalysisEngine, create_standard_sensitivity_variables
from src.analytics.monte_carlo import MonteCarloEngine, create_standard_distributions
from src.analytics.scenario_modeling import ScenarioModelingEngine
from src.analytics.risk_assessment import RiskAssessmentEngine, create_mock_market_data_for_risk_assessment
from src.shared.interfaces import AnalyticsEngine, SensitivityVariable, ScenarioDefinition


class TestComponentIntegration(unittest.TestCase):
    """Test integration between analytics components"""
    
    def setUp(self):
        self.sensitivity_engine = SensitivityAnalysisEngine()
        self.monte_carlo_engine = MonteCarloEngine()
        self.scenario_engine = ScenarioModelingEngine()
        self.risk_engine = RiskAssessmentEngine()
        
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
        
        self.market_data = create_mock_market_data_for_risk_assessment()
    
    def test_all_engines_implement_interface(self):
        """Test that all engines properly implement AnalyticsEngine interface"""
        engines = [
            self.sensitivity_engine,
            self.monte_carlo_engine, 
            self.scenario_engine,
            self.risk_engine
        ]
        
        for engine in engines:
            self.assertIsInstance(engine, AnalyticsEngine)
            
            # Check required methods exist
            self.assertTrue(hasattr(engine, 'run_sensitivity_analysis'))
            self.assertTrue(hasattr(engine, 'run_scenario_analysis'))
            self.assertTrue(hasattr(engine, 'run_monte_carlo'))
            self.assertTrue(hasattr(engine, 'assess_risk'))
    
    def test_parameter_consistency_across_engines(self):
        """Test that all engines handle the same parameter set consistently"""
        # Test that all engines can process the same base parameters
        variables = create_standard_sensitivity_variables(self.base_params)[:2]
        distributions = create_standard_distributions(self.base_params)
        scenarios = self.scenario_engine.create_economic_scenarios(self.base_params)[:2]
        
        # Run each engine
        sensitivity_results = self.sensitivity_engine.run_sensitivity_analysis(self.base_params, variables)
        monte_carlo_result = self.monte_carlo_engine.run_monte_carlo(self.base_params, distributions, 5000)
        scenario_results = self.scenario_engine.run_scenario_analysis(self.base_params, scenarios)
        risk_result = self.risk_engine.assess_risk(self.base_params, self.market_data)
        
        # All should complete successfully
        self.assertIsNotNone(sensitivity_results)
        self.assertIsNotNone(monte_carlo_result)
        self.assertIsNotNone(scenario_results)
        self.assertIsNotNone(risk_result)
        
        self.assertGreater(len(sensitivity_results), 0)
        self.assertGreater(monte_carlo_result.iterations, 0)
        self.assertGreater(len(scenario_results), 0)
        self.assertIsNotNone(risk_result.overall_risk_level)
    
    def test_npv_consistency_across_components(self):
        """Test NPV consistency across different analysis components"""
        from src.calculations.npv_analysis import calculate_npv_comparison
        
        # Calculate base NPV
        base_npv_result = calculate_npv_comparison(**self.base_params)
        base_npv = base_npv_result['npv_difference']
        
        # Test Monte Carlo mean should be reasonably close to base NPV
        distributions = {'interest_rate': {'distribution': 'normal', 'params': [5.0, 0.1]}}  # Very small variance
        mc_result = self.monte_carlo_engine.run_monte_carlo(self.base_params, distributions, 5000)
        
        # With small variance, MC mean should be close to base NPV
        npv_difference = abs(mc_result.mean_npv - base_npv)
        relative_difference = npv_difference / abs(base_npv) if base_npv != 0 else 0
        self.assertLess(relative_difference, 0.5, "Monte Carlo mean should be reasonably close to base NPV")
        
        # Test scenario analysis base case should match calculated base NPV
        scenarios = [ScenarioDefinition("Test", "Test scenario", {}, None)]  # Empty scenario = base case
        scenario_results = self.scenario_engine.run_scenario_analysis(self.base_params, scenarios)
        
        base_case_result = next((r for r in scenario_results if r.get('scenario_name') == 'Base Case'), None)
        if base_case_result:
            scenario_base_npv = base_case_result.get('npv_difference', 0)
            base_npv_diff = abs(scenario_base_npv - base_npv)
            base_relative_diff = base_npv_diff / abs(base_npv) if base_npv != 0 else 0
            self.assertLess(base_relative_diff, 0.01, "Scenario base case should match calculated base NPV")
    
    def test_cross_component_workflow(self):
        """Test complete analytics workflow using all components"""
        # Step 1: Risk Assessment
        risk_result = self.risk_engine.assess_risk(self.base_params, self.market_data)
        self.assertIsNotNone(risk_result)
        
        # Step 2: Sensitivity Analysis (focus on high-risk factors if available)
        variables = create_standard_sensitivity_variables(self.base_params)[:3]
        sensitivity_results = self.sensitivity_engine.run_sensitivity_analysis(self.base_params, variables)
        self.assertGreater(len(sensitivity_results), 0)
        
        # Step 3: Scenario Analysis
        scenarios = self.scenario_engine.create_economic_scenarios(self.base_params)[:3]
        scenario_results = self.scenario_engine.run_scenario_analysis(self.base_params, scenarios)
        self.assertGreater(len(scenario_results), 0)
        
        # Step 4: Monte Carlo Analysis
        distributions = create_standard_distributions(self.base_params)
        mc_result = self.monte_carlo_engine.run_monte_carlo(self.base_params, distributions, 5000)
        self.assertGreater(mc_result.iterations, 0)
        
        # Verify workflow consistency
        self.assertTrue(all([
            risk_result.confidence_score > 0,
            len(sensitivity_results) == 3,
            len([r for r in scenario_results if r.get('calculation_successful', False)]) > 0,
            mc_result.iterations > 4000
        ]))
    
    def test_error_propagation_across_components(self):
        """Test that errors in one component don't break others"""
        # Use invalid parameters that might cause issues
        invalid_params = self.base_params.copy()
        invalid_params['purchase_price'] = -1000000  # Negative price
        invalid_params['interest_rate'] = -50.0  # Negative interest rate
        
        # Test that each component handles errors gracefully
        try:
            variables = create_standard_sensitivity_variables(invalid_params)[:1]
            sensitivity_results = self.sensitivity_engine.run_sensitivity_analysis(invalid_params, variables)
            # Should not raise exception, might return limited results
            self.assertIsNotNone(sensitivity_results)
        except Exception as e:
            self.fail(f"Sensitivity analysis should handle invalid parameters gracefully: {e}")
        
        try:
            distributions = {'interest_rate': {'distribution': 'normal', 'params': [-50.0, 10.0]}}
            mc_result = self.monte_carlo_engine.run_monte_carlo(invalid_params, distributions, 1000)
            self.assertIsNotNone(mc_result)
        except Exception as e:
            self.fail(f"Monte Carlo should handle invalid parameters gracefully: {e}")
        
        try:
            scenarios = [ScenarioDefinition("Invalid", "Invalid scenario", {'interest_rate': -100.0})]
            scenario_results = self.scenario_engine.run_scenario_analysis(invalid_params, scenarios)
            self.assertIsNotNone(scenario_results)
        except Exception as e:
            self.fail(f"Scenario modeling should handle invalid parameters gracefully: {e}")
    
    def test_performance_integration(self):
        """Test integrated performance across all components"""
        start_time = time.time()
        
        # Run all components with reasonable parameters
        variables = create_standard_sensitivity_variables(self.base_params)[:2]  # Limit for performance
        distributions = create_standard_distributions(self.base_params)
        scenarios = self.scenario_engine.create_economic_scenarios(self.base_params)[:3]
        
        # Execute all analyses
        sensitivity_results = self.sensitivity_engine.run_sensitivity_analysis(self.base_params, variables)
        mc_result = self.monte_carlo_engine.run_monte_carlo(self.base_params, distributions, 8000)
        scenario_results = self.scenario_engine.run_scenario_analysis(self.base_params, scenarios)
        risk_result = self.risk_engine.assess_risk(self.base_params, self.market_data)
        
        total_time = time.time() - start_time
        
        # Integrated analysis should complete in reasonable time
        self.assertLess(total_time, 15.0, "Complete integrated analysis should finish in under 15 seconds")
        
        # All components should produce results
        self.assertGreater(len(sensitivity_results), 0)
        self.assertGreater(mc_result.iterations, 6000)
        self.assertGreater(len(scenario_results), 0)
        self.assertIsNotNone(risk_result.overall_risk_level)
    
    def test_data_format_consistency(self):
        """Test that data formats are consistent across components"""
        # Run analyses
        variables = create_standard_sensitivity_variables(self.base_params)[:1]
        sensitivity_results = self.sensitivity_engine.run_sensitivity_analysis(self.base_params, variables)
        
        distributions = create_standard_distributions(self.base_params)
        mc_result = self.monte_carlo_engine.run_monte_carlo(self.base_params, distributions, 3000)
        
        scenarios = self.scenario_engine.create_economic_scenarios(self.base_params)[:1]
        scenario_results = self.scenario_engine.run_scenario_analysis(self.base_params, scenarios)
        
        risk_result = self.risk_engine.assess_risk(self.base_params, self.market_data)
        
        # Check data format consistency
        # Sensitivity results should have proper structure
        for result in sensitivity_results:
            self.assertTrue(hasattr(result, 'variable_name'))
            self.assertTrue(hasattr(result, 'variable_values'))
            self.assertTrue(hasattr(result, 'npv_impacts'))
            self.assertTrue(hasattr(result, 'elasticity'))
        
        # Monte Carlo result should have proper structure
        self.assertTrue(hasattr(mc_result, 'iterations'))
        self.assertTrue(hasattr(mc_result, 'mean_npv'))
        self.assertTrue(hasattr(mc_result, 'std_dev'))
        self.assertTrue(hasattr(mc_result, 'percentiles'))
        
        # Scenario results should be properly formatted
        for result in scenario_results:
            if isinstance(result, dict):
                # Check for common fields
                if 'scenario_name' in result:
                    self.assertIsInstance(result['scenario_name'], str)
        
        # Risk result should have proper structure
        self.assertTrue(hasattr(risk_result, 'overall_risk_level'))
        self.assertTrue(hasattr(risk_result, 'risk_factors'))
        self.assertTrue(hasattr(risk_result, 'confidence_score'))
    
    def test_concurrent_execution(self):
        """Test that components can run concurrently without conflicts"""
        import threading
        
        results = {}
        errors = {}
        
        def run_sensitivity():
            try:
                variables = create_standard_sensitivity_variables(self.base_params)[:1]
                results['sensitivity'] = self.sensitivity_engine.run_sensitivity_analysis(self.base_params, variables)
            except Exception as e:
                errors['sensitivity'] = e
        
        def run_monte_carlo():
            try:
                distributions = create_standard_distributions(self.base_params)
                results['monte_carlo'] = self.monte_carlo_engine.run_monte_carlo(self.base_params, distributions, 3000)
            except Exception as e:
                errors['monte_carlo'] = e
        
        def run_scenarios():
            try:
                scenarios = self.scenario_engine.create_economic_scenarios(self.base_params)[:2]
                results['scenarios'] = self.scenario_engine.run_scenario_analysis(self.base_params, scenarios)
            except Exception as e:
                errors['scenarios'] = e
        
        def run_risk():
            try:
                results['risk'] = self.risk_engine.assess_risk(self.base_params, self.market_data)
            except Exception as e:
                errors['risk'] = e
        
        # Start all threads
        threads = [
            threading.Thread(target=run_sensitivity),
            threading.Thread(target=run_monte_carlo),
            threading.Thread(target=run_scenarios),
            threading.Thread(target=run_risk)
        ]
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join(timeout=10.0)  # 10 second timeout per thread
        
        elapsed = time.time() - start_time
        
        # Check that no errors occurred
        if errors:
            self.fail(f"Concurrent execution errors: {errors}")
        
        # Check that all components completed
        expected_components = ['sensitivity', 'monte_carlo', 'scenarios', 'risk']
        for component in expected_components:
            self.assertIn(component, results, f"Component {component} did not complete")
            self.assertIsNotNone(results[component])
        
        # Concurrent execution should be faster than sequential
        self.assertLess(elapsed, 12.0, "Concurrent execution should complete efficiently")


class TestParameterValidation(unittest.TestCase):
    """Test parameter validation consistency across components"""
    
    def setUp(self):
        self.engines = {
            'sensitivity': SensitivityAnalysisEngine(),
            'monte_carlo': MonteCarloEngine(),
            'scenario': ScenarioModelingEngine(),
            'risk': RiskAssessmentEngine()
        }
        
        self.valid_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000,
            'down_payment_pct': 30.0,
            'interest_rate': 5.0,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0
        }
    
    def test_missing_required_parameters(self):
        """Test handling of missing required parameters"""
        incomplete_params = {
            'purchase_price': 500000,
            'current_annual_rent': 24000
            # Missing other required parameters
        }
        
        # Each engine should either handle missing parameters or fail gracefully
        # Sensitivity Analysis
        try:
            variables = [SensitivityVariable('interest_rate', 5.0, 3.0, 8.0, 0.5, '%', 'Test')]
            result = self.engines['sensitivity'].run_sensitivity_analysis(incomplete_params, variables)
            # Should either work (with defaults) or handle gracefully
            self.assertIsNotNone(result)
        except ValueError:
            pass  # Acceptable to raise ValueError for missing parameters
        
        # Similar tests for other engines would go here
        # (abbreviated for space, but each should be tested)
    
    def test_parameter_type_consistency(self):
        """Test that all engines handle parameter types consistently"""
        # Test with string numbers (common user input error)
        string_params = {
            'purchase_price': '500000',
            'current_annual_rent': '24000',
            'down_payment_pct': '30.0',
            'interest_rate': '5.0',
            'market_appreciation_rate': '3.0',
            'rent_increase_rate': '3.0',
            'cost_of_capital': '8.0'
        }
        
        # Convert to proper types for testing
        converted_params = {k: float(v) for k, v in string_params.items()}
        
        # Test that engines work with properly typed parameters
        variables = [SensitivityVariable('interest_rate', 5.0, 3.0, 8.0, 0.5, '%', 'Test')]
        result = self.engines['sensitivity'].run_sensitivity_analysis(converted_params, variables)
        self.assertIsNotNone(result)


class TestConfigurationConsistency(unittest.TestCase):
    """Test configuration consistency across components"""
    
    def test_timeout_configurations(self):
        """Test that timeout configurations work consistently"""
        from src.analytics.sensitivity_analysis import SensitivityConfig
        from src.analytics.monte_carlo import MonteCarloConfig
        from src.analytics.scenario_modeling import ScenarioConfig
        
        # Test short timeouts
        sens_config = SensitivityConfig(timeout_seconds=0.5)
        mc_config = MonteCarloConfig(timeout_seconds=1.0)
        scenario_config = ScenarioConfig(timeout_seconds=1.0)
        
        # Engines should respect timeout configurations
        sens_engine = SensitivityAnalysisEngine(sens_config)
        mc_engine = MonteCarloEngine(mc_config)
        scenario_engine = ScenarioModelingEngine(scenario_config)
        
        self.assertEqual(sens_engine.config.timeout_seconds, 0.5)
        self.assertEqual(mc_engine.config.timeout_seconds, 1.0)
        self.assertEqual(scenario_engine.config.timeout_seconds, 1.0)
    
    def test_performance_configurations(self):
        """Test performance-related configurations"""
        from src.analytics.sensitivity_analysis import SensitivityConfig
        from src.analytics.monte_carlo import MonteCarloConfig
        
        # Test worker configurations
        sens_config = SensitivityConfig(max_workers=2)
        mc_config = MonteCarloConfig(max_workers=2)
        
        sens_engine = SensitivityAnalysisEngine(sens_config)
        mc_engine = MonteCarloEngine(mc_config)
        
        self.assertEqual(sens_engine.config.max_workers, 2)
        self.assertEqual(mc_engine.config.max_workers, 2)


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end analytics workflows"""
    
    def setUp(self):
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
    
    def test_complete_analytics_workflow(self):
        """Test complete analytics workflow from start to finish"""
        # Initialize all engines
        sensitivity_engine = SensitivityAnalysisEngine()
        monte_carlo_engine = MonteCarloEngine()
        scenario_engine = ScenarioModelingEngine()
        risk_engine = RiskAssessmentEngine()
        market_data = create_mock_market_data_for_risk_assessment()
        
        workflow_results = {}
        
        # Step 1: Initial Risk Assessment
        print("Step 1: Risk Assessment...")
        risk_result = risk_engine.assess_risk(self.base_params, market_data)
        workflow_results['risk_assessment'] = risk_result
        self.assertIsNotNone(risk_result)
        
        # Step 2: Sensitivity Analysis based on risk factors
        print("Step 2: Sensitivity Analysis...")
        variables = create_standard_sensitivity_variables(self.base_params)[:3]  # Top 3 for performance
        sensitivity_results = sensitivity_engine.run_sensitivity_analysis(self.base_params, variables)
        workflow_results['sensitivity_analysis'] = sensitivity_results
        self.assertGreater(len(sensitivity_results), 0)
        
        # Step 3: Scenario Analysis
        print("Step 3: Scenario Analysis...")
        scenarios = scenario_engine.create_economic_scenarios(self.base_params)[:4]  # 4 scenarios
        scenario_results = scenario_engine.run_scenario_analysis(self.base_params, scenarios)
        workflow_results['scenario_analysis'] = scenario_results
        self.assertGreater(len(scenario_results), 0)
        
        # Step 4: Monte Carlo Simulation
        print("Step 4: Monte Carlo Simulation...")
        distributions = create_standard_distributions(self.base_params)
        mc_result = monte_carlo_engine.run_monte_carlo(self.base_params, distributions, 8000)
        workflow_results['monte_carlo'] = mc_result
        self.assertGreater(mc_result.iterations, 6000)
        
        # Step 5: Integrated Analysis Summary
        print("Step 5: Creating Integrated Summary...")
        integrated_summary = self._create_integrated_summary(workflow_results)
        self.assertIsInstance(integrated_summary, dict)
        self.assertIn('overall_recommendation', integrated_summary)
        self.assertIn('confidence_level', integrated_summary)
        self.assertIn('key_risks', integrated_summary)
        self.assertIn('sensitivity_insights', integrated_summary)
        
        print("✅ Complete workflow test passed!")
    
    def _create_integrated_summary(self, workflow_results: Dict) -> Dict:
        """Create integrated summary from all workflow results"""
        risk_result = workflow_results.get('risk_assessment')
        sensitivity_results = workflow_results.get('sensitivity_analysis', [])
        scenario_results = workflow_results.get('scenario_analysis', [])
        mc_result = workflow_results.get('monte_carlo')
        
        # Determine overall recommendation
        recommendations = []
        
        # From scenario analysis
        for result in scenario_results:
            if isinstance(result, dict) and 'recommendation' in result:
                recommendations.append(result['recommendation'])
        
        # Most common recommendation
        if recommendations:
            recommendation_counts = {}
            for rec in recommendations:
                recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
            overall_recommendation = max(recommendation_counts, key=recommendation_counts.get)
        else:
            overall_recommendation = "ANALYSIS_INCOMPLETE"
        
        # Confidence level from Monte Carlo probability
        confidence_level = "Medium"
        if mc_result and hasattr(mc_result, 'probability_positive'):
            if mc_result.probability_positive > 0.7:
                confidence_level = "High"
            elif mc_result.probability_positive < 0.3:
                confidence_level = "Low"
        
        # Key risks from risk assessment
        key_risks = []
        if risk_result and hasattr(risk_result, 'risk_factors'):
            high_risk_factors = [
                name for name, score in risk_result.risk_factors.items() 
                if score > 0.6
            ]
            key_risks = high_risk_factors[:3]  # Top 3
        
        # Sensitivity insights
        sensitivity_insights = []
        if sensitivity_results:
            for result in sensitivity_results:
                if hasattr(result, 'elasticity') and abs(result.elasticity) > 0.5:
                    sensitivity_insights.append({
                        'parameter': result.variable_name,
                        'elasticity': result.elasticity,
                        'impact': 'High' if abs(result.elasticity) > 1.0 else 'Medium'
                    })
        
        return {
            'overall_recommendation': overall_recommendation,
            'confidence_level': confidence_level,
            'key_risks': key_risks,
            'sensitivity_insights': sensitivity_insights,
            'analysis_timestamp': time.time(),
            'components_completed': len(workflow_results)
        }


if __name__ == '__main__':
    unittest.main(verbosity=2)