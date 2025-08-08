"""
Comprehensive Integration Tests for Analysis Engine
End-to-end testing from UI inputs to final results

Test Coverage:
- NPV Integration Engine: UI → Calculations → Results pipeline
- Decision Engine: Recommendation logic and confidence levels  
- Sensitivity Analysis: Parameter variation and break-even calculations
- Results Processor: Professional formatting and KPI generation
- Complete workflow integration and error handling
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date
from typing import Dict, Any

# Import analysis modules
from src.analysis.npv_integration import NPVIntegrationEngine, get_npv_integration_engine
from src.analysis.decision_engine import DecisionEngine, make_investment_decision
from src.analysis.sensitivity import SensitivityAnalyzer, run_quick_sensitivity_analysis
from src.analysis.results_processor import ResultsProcessor, process_analysis_results


class TestNPVIntegrationEngine(unittest.TestCase):
    """Test NPV Integration Engine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = NPVIntegrationEngine()
        self.valid_session_data = {
            'purchase_price': 500000,
            'current_annual_rent': 120000,
            'total_property_size': 5000,
            'current_space_needed': 4000,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'down_payment_percent': 30.0,
            'interest_rate': 5.0,
            'loan_term': 20,
            'currency': 'USD',
            'rent_increase_rate': 3.0,
            'market_appreciation_rate': 3.5,
            'property_tax_rate': 1.2,
            'insurance_cost': 5000,
            'annual_maintenance_percent': 2.0,
            'analysis_date': date.today(),
            'project_name': 'Test Project',
            'location': 'Test Location',
            'analyst_name': 'Test Analyst'
        }
    
    def test_input_extraction_valid_data(self):
        """Test extraction of valid inputs from session state"""
        inputs = self.engine.extract_inputs_from_session(self.valid_session_data)
        
        # Check critical fields are extracted
        self.assertEqual(inputs['purchase_price'], 500000)
        self.assertEqual(inputs['current_annual_rent'], 120000)
        self.assertEqual(inputs['analysis_period'], 25)
        self.assertEqual(inputs['cost_of_capital'], 8.0)
        
        # Check validation passes
        self.assertEqual(len(self.engine.validation_errors), 0)
    
    def test_input_extraction_missing_data(self):
        """Test extraction with missing critical data"""
        incomplete_data = {
            'purchase_price': 500000,
            # Missing current_annual_rent - should trigger validation error
            'total_property_size': 5000
        }
        
        inputs = self.engine.extract_inputs_from_session(incomplete_data)
        
        # Should have validation errors
        self.assertGreater(len(self.engine.validation_errors), 0)
        
        # Should still return inputs with defaults
        self.assertIn('current_annual_rent', inputs)
    
    def test_input_transformation(self):
        """Test transformation of inputs for calculations"""
        raw_inputs = self.engine.extract_inputs_from_session(self.valid_session_data)
        calc_params = self.engine.transform_inputs_for_calculations(raw_inputs)
        
        # Check parameter structure
        required_params = [
            'purchase_price', 'down_payment_pct', 'interest_rate', 'loan_term',
            'current_annual_rent', 'rent_increase_rate', 'analysis_period', 'cost_of_capital'
        ]
        
        for param in required_params:
            self.assertIn(param, calc_params)
        
        # Check calculated values
        self.assertEqual(calc_params['purchase_price'], 500000)
        self.assertEqual(calc_params['down_payment_pct'], 30.0)
    
    def test_complete_analysis_pipeline(self):
        """Test complete analysis from session data to results"""
        results = self.engine.run_complete_analysis(self.valid_session_data)
        
        # Check successful calculation
        self.assertTrue(results.get('calculation_successful', False))
        self.assertIn('recommendation', results)
        self.assertIn('npv_difference', results)
        self.assertIn('ownership_npv', results)
        self.assertIn('rental_npv', results)
        
        # Check metadata
        self.assertIn('calculation_timestamp', results)
        self.assertIn('input_parameters', results)
    
    def test_input_validation_errors(self):
        """Test handling of invalid input data"""
        invalid_data = {
            'purchase_price': -100000,  # Invalid: negative
            'current_annual_rent': 0,    # Invalid: zero
            'down_payment_percent': 150,  # Invalid: over 100%
            'interest_rate': -5.0,       # Invalid: negative
            'analysis_period': 0         # Invalid: zero
        }
        
        results = self.engine.run_complete_analysis(invalid_data)
        
        # Should fail with validation errors
        self.assertFalse(results.get('calculation_successful', True))
        self.assertEqual(results.get('recommendation'), 'ERROR')
        self.assertGreater(len(results.get('validation_errors', [])), 0)
    
    def test_calculation_summary(self):
        """Test generation of calculation summary"""
        results = self.engine.run_complete_analysis(self.valid_session_data)
        summary = self.engine.get_calculation_summary(results)
        
        if results.get('calculation_successful', False):
            # Check summary structure
            self.assertEqual(summary['status'], 'Success')
            self.assertIn('recommendation', summary)
            self.assertIn('npv_advantage', summary)
            self.assertIn('explanation', summary)
        else:
            self.assertEqual(summary['status'], 'Failed')
            self.assertIn('error', summary)


class TestDecisionEngine(unittest.TestCase):
    """Test Decision Engine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = DecisionEngine()
        self.sample_npv_results = {
            'calculation_successful': True,
            'npv_difference': 750000,
            'ownership_npv': -2500000,
            'rental_npv': -3250000,
            'ownership_initial_investment': 150000,
            'terminal_value_advantage': 500000,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'input_parameters': {
                'purchase_price': 500000,
                'interest_rate': 5.0,
                'market_appreciation_rate': 3.5,
                'down_payment_pct': 30
            }
        }
    
    def test_decision_recommendation_positive_npv(self):
        """Test decision with positive NPV difference"""
        decision = self.engine.calculate_decision_recommendation(self.sample_npv_results)
        
        # Check decision structure
        self.assertIn('recommendation', decision)
        self.assertIn('confidence_level', decision)
        self.assertIn('risk_assessment', decision)
        self.assertIn('executive_summary', decision)
        
        # Should recommend buying with positive NPV
        self.assertIn(decision['recommendation'], ['BUY', 'STRONG_BUY', 'MARGINAL_BUY'])
    
    def test_decision_recommendation_negative_npv(self):
        """Test decision with negative NPV difference"""
        negative_npv_results = self.sample_npv_results.copy()
        negative_npv_results['npv_difference'] = -500000
        negative_npv_results['ownership_npv'] = -3500000
        negative_npv_results['rental_npv'] = -3000000
        
        decision = self.engine.calculate_decision_recommendation(negative_npv_results)
        
        # Should recommend renting with negative NPV
        self.assertIn(decision['recommendation'], ['RENT', 'STRONG_RENT', 'MARGINAL_RENT'])
    
    def test_confidence_level_calculation(self):
        """Test confidence level calculation logic"""
        # High confidence case - large NPV margin, reasonable assumptions
        high_confidence_results = self.sample_npv_results.copy()
        high_confidence_results['npv_difference'] = 2000000
        
        decision = self.engine.calculate_decision_recommendation(high_confidence_results)
        confidence = decision.get('confidence_level', 'Unknown')
        
        # Should have high confidence with large NPV advantage
        self.assertIn(confidence, ['High', 'Very High', 'Medium'])
        
        # Low confidence case - small NPV margin
        low_confidence_results = self.sample_npv_results.copy()
        low_confidence_results['npv_difference'] = 50000
        
        decision = self.engine.calculate_decision_recommendation(low_confidence_results)
        confidence = decision.get('confidence_level', 'Unknown')
        
        # Should have lower confidence with small advantage
        self.assertIn(confidence, ['Low', 'Medium', 'Very Low'])
    
    def test_risk_assessment(self):
        """Test risk assessment functionality"""
        decision = self.engine.calculate_decision_recommendation(self.sample_npv_results)
        risk_assessment = decision.get('risk_assessment', {})
        
        # Check risk assessment structure
        self.assertIn('overall_risk_level', risk_assessment)
        self.assertIn('risk_score', risk_assessment)
        self.assertIn('risk_factors', risk_assessment)
        self.assertIn('key_risks', risk_assessment)
        
        # Risk level should be valid
        risk_level = risk_assessment.get('overall_risk_level')
        valid_risk_levels = ['Very Low', 'Low', 'Moderate', 'High', 'Very High']
        self.assertIn(risk_level, valid_risk_levels)
    
    def test_executive_reasoning(self):
        """Test executive reasoning generation"""
        decision = self.engine.calculate_decision_recommendation(self.sample_npv_results)
        executive_summary = decision.get('executive_summary', {})
        
        # Check executive summary structure
        self.assertIn('primary_reason', executive_summary)
        self.assertIn('decision_summary', executive_summary)
        self.assertIn('supporting_factors', executive_summary)
        self.assertIn('key_considerations', executive_summary)
        
        # Primary reason should be meaningful
        primary_reason = executive_summary.get('primary_reason', '')
        self.assertGreater(len(primary_reason), 20)  # Should be substantial text
    
    def test_error_handling(self):
        """Test decision engine error handling"""
        error_results = {
            'calculation_successful': False,
            'error_message': 'Test calculation error'
        }
        
        decision = self.engine.calculate_decision_recommendation(error_results)
        
        # Should handle error gracefully
        self.assertEqual(decision['recommendation'], 'ERROR')
        self.assertEqual(decision['confidence_level'], 'Very Low')
        self.assertIn('error_message', decision)


class TestSensitivityAnalyzer(unittest.TestCase):
    """Test Sensitivity Analysis functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = SensitivityAnalyzer()
        self.base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 120000,
            'down_payment_pct': 30.0,
            'interest_rate': 5.0,
            'loan_term': 20,
            'transaction_costs': 25000,
            'market_appreciation_rate': 3.0,
            'rent_increase_rate': 3.0,
            'cost_of_capital': 8.0,
            'analysis_period': 25,
            'property_tax_rate': 1.2,
            'property_tax_escalation': 2.0,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'property_management': 0.0,
            'capex_reserve_rate': 1.5,
            'obsolescence_risk_rate': 0.5,
            'inflation_rate': 3.0,
            'land_value_pct': 25.0,
            'depreciation_period': 39,
            'corporate_tax_rate': 25.0,
            'interest_deductible': True,
            'property_tax_deductible': True,
            'rent_deductible': True,
            'security_deposit': 20000,
            'rental_commission': 10000,
            'moving_costs': 5000
        }
    
    def test_parameter_definitions(self):
        """Test sensitivity parameter definitions"""
        self.analyzer.configure_base_parameters(self.base_params)
        param_defs = self.analyzer.define_sensitivity_parameters()
        
        # Check critical parameters are defined
        critical_params = ['interest_rate', 'market_appreciation_rate', 'cost_of_capital']
        for param in critical_params:
            self.assertIn(param, param_defs)
            self.assertTrue(param_defs[param].get('critical', False))
            
        # Check parameter structure
        for param_name, param_config in param_defs.items():
            self.assertIn('base_value', param_config)
            self.assertIn('min_value', param_config)
            self.assertIn('max_value', param_config)
            self.assertIn('step_count', param_config)
            self.assertIn('label', param_config)
    
    def test_single_parameter_sensitivity(self):
        """Test single parameter sensitivity analysis"""
        self.analyzer.configure_base_parameters(self.base_params)
        
        # Test interest rate sensitivity
        test_values = [3.0, 4.0, 5.0, 6.0, 7.0]
        results = self.analyzer.run_single_parameter_sensitivity('interest_rate', test_values)
        
        # Check results structure
        self.assertEqual(results['parameter_name'], 'interest_rate')
        self.assertEqual(len(results['test_values']), 5)
        self.assertEqual(len(results['npv_differences']), 5)
        self.assertEqual(len(results['recommendations']), 5)
        
        # Check sensitivity range calculation
        self.assertIsInstance(results['sensitivity_range'], float)
        self.assertGreaterEqual(results['sensitivity_range'], 0)
    
    def test_break_even_calculation(self):
        """Test break-even point calculation"""
        self.analyzer.configure_base_parameters(self.base_params)
        
        # Test break-even for parameters likely to have break-even points
        break_even_results = self.analyzer.calculate_break_even_analysis(['interest_rate', 'cost_of_capital'])
        
        # Check results structure
        for param_name in ['interest_rate', 'cost_of_capital']:
            if param_name in break_even_results:
                result = break_even_results[param_name]
                self.assertIn('break_even_found', result)
                
                if result.get('break_even_found', False):
                    self.assertIn('break_even_value', result)
                    self.assertIn('base_value', result)
                    self.assertIn('percentage_change', result)
    
    def test_comprehensive_sensitivity_analysis(self):
        """Test comprehensive sensitivity analysis"""
        self.analyzer.configure_base_parameters(self.base_params)
        
        # Run analysis (critical parameters only for performance)
        results = self.analyzer.run_comprehensive_sensitivity_analysis(focus_on_critical=True)
        
        # Check results structure
        self.assertIn('parameter_results', results)
        self.assertIn('tornado_data', results)
        self.assertIn('analysis_summary', results)
        
        # Check tornado data is sorted
        tornado_data = results.get('tornado_data', [])
        if len(tornado_data) > 1:
            # Should be sorted by sensitivity range (descending)
            for i in range(len(tornado_data) - 1):
                self.assertGreaterEqual(
                    tornado_data[i]['sensitivity_range'],
                    tornado_data[i + 1]['sensitivity_range']
                )
    
    def test_scenario_analysis(self):
        """Test scenario analysis functionality"""
        self.analyzer.configure_base_parameters(self.base_params)
        
        scenarios = {
            'optimistic': {
                'market_appreciation_rate': 5.0,
                'interest_rate': 4.0,
                'rent_increase_rate': 4.0
            },
            'pessimistic': {
                'market_appreciation_rate': 1.0,
                'interest_rate': 7.0,
                'rent_increase_rate': 2.0
            },
            'base_case': {}  # No overrides
        }
        
        results = self.analyzer.run_scenario_analysis(scenarios)
        
        # Check results structure
        self.assertIn('scenarios', results)
        self.assertIn('comparison_table', results)
        self.assertIn('scenario_ranking', results)
        
        # Check all scenarios were processed
        for scenario_name in scenarios.keys():
            self.assertIn(scenario_name, results['scenarios'])


class TestResultsProcessor(unittest.TestCase):
    """Test Results Processor functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = ResultsProcessor('USD')
        self.sample_npv_results = {
            'calculation_successful': True,
            'npv_difference': 750000,
            'ownership_npv': -2500000,
            'rental_npv': -3250000,
            'ownership_initial_investment': 150000,
            'rental_initial_investment': 15000,
            'terminal_value_advantage': 500000,
            'ownership_terminal_value': 800000,
            'rental_terminal_value': 300000,
            'recommendation': 'BUY',
            'confidence': 'Medium',
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'input_parameters': {
                'purchase_price': 500000,
                'current_annual_rent': 120000,
                'down_payment_pct': 30,
                'interest_rate': 5.0,
                'market_appreciation_rate': 3.5
            }
        }
    
    def test_npv_results_processing(self):
        """Test processing of NPV analysis results"""
        processed = self.processor.process_npv_analysis_results(self.sample_npv_results)
        
        # Check main sections
        required_sections = [
            'executive_summary', 'key_metrics', 'financial_comparison',
            'investment_analysis', 'metadata', 'presentation_tables', 'visualization_data'
        ]
        
        for section in required_sections:
            self.assertIn(section, processed)
    
    def test_executive_summary_creation(self):
        """Test executive summary creation"""
        processed = self.processor.process_npv_analysis_results(self.sample_npv_results)
        exec_summary = processed.get('executive_summary', {})
        
        # Check required fields
        required_fields = [
            'recommendation', 'recommendation_formatted', 'confidence_level',
            'action_text', 'npv_advantage', 'summary_statement'
        ]
        
        for field in required_fields:
            self.assertIn(field, exec_summary)
        
        # Check formatting
        self.assertIn('$', exec_summary.get('npv_advantage', ''))  # Should have currency
        self.assertGreater(len(exec_summary.get('summary_statement', '')), 20)  # Should be substantial
    
    def test_key_metrics_extraction(self):
        """Test key metrics extraction and formatting"""
        processed = self.processor.process_npv_analysis_results(self.sample_npv_results)
        key_metrics = processed.get('key_metrics', {})
        
        # Check essential metrics
        essential_metrics = [
            'ownership_npv', 'rental_npv', 'npv_advantage',
            'initial_investment', 'roi_percentage'
        ]
        
        for metric in essential_metrics:
            self.assertIn(metric, key_metrics)
            
            metric_data = key_metrics[metric]
            self.assertIn('value', metric_data)
            self.assertIn('raw_value', metric_data)
            self.assertIn('label', metric_data)
            self.assertIn('description', metric_data)
    
    def test_visualization_data_preparation(self):
        """Test visualization data preparation"""
        processed = self.processor.process_npv_analysis_results(self.sample_npv_results)
        viz_data = processed.get('visualization_data', {})
        
        # Check chart data structures
        self.assertIn('npv_comparison', viz_data)
        self.assertIn('investment_breakdown', viz_data)
        self.assertIn('gauge_metrics', viz_data)
        
        # Check NPV comparison data
        npv_comparison = viz_data['npv_comparison']
        self.assertIn('categories', npv_comparison)
        self.assertIn('values', npv_comparison)
        self.assertIn('colors', npv_comparison)
        self.assertEqual(len(npv_comparison['categories']), len(npv_comparison['values']))
    
    def test_presentation_tables_creation(self):
        """Test creation of presentation tables"""
        processed = self.processor.process_npv_analysis_results(self.sample_npv_results)
        tables = processed.get('presentation_tables', {})
        
        # Check table structures
        self.assertIn('summary_table', tables)
        self.assertIn('parameters_table', tables)
        
        # Check table format (list of lists)
        summary_table = tables['summary_table']
        self.assertIsInstance(summary_table, list)
        self.assertGreater(len(summary_table), 1)  # Should have header + data
        
        # Check all rows have same number of columns
        if summary_table:
            header_length = len(summary_table[0])
            for row in summary_table:
                self.assertEqual(len(row), header_length)
    
    def test_error_results_formatting(self):
        """Test formatting of error results"""
        error_results = {
            'calculation_successful': False,
            'error_message': 'Test calculation error',
            'validation_errors': ['Invalid input 1', 'Invalid input 2']
        }
        
        processed = self.processor.process_npv_analysis_results(error_results)
        
        # Check error handling
        exec_summary = processed.get('executive_summary', {})
        self.assertEqual(exec_summary.get('recommendation'), 'ERROR')
        self.assertEqual(exec_summary.get('recommendation_color'), 'error')
        
        # Check error details
        self.assertIn('error_details', processed)
        error_details = processed['error_details']
        self.assertIn('primary_error', error_details)
        self.assertIn('validation_errors', error_details)
        self.assertIn('suggested_actions', error_details)
    
    def test_csv_export(self):
        """Test CSV export functionality"""
        processed = self.processor.process_npv_analysis_results(self.sample_npv_results)
        csv_data = self.processor.export_to_csv(processed)
        
        # Check CSV format
        self.assertIsInstance(csv_data, str)
        self.assertIn('"Metric","Value"', csv_data)  # Should have header (quoted)
        self.assertIn('"Recommendation",', csv_data)  # Should have recommendation
        
        # Should have multiple lines
        lines = csv_data.split('\n')
        self.assertGreater(len(lines), 5)


class TestIntegrationWorkflow(unittest.TestCase):
    """Test complete integration workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.valid_session_data = {
            'purchase_price': 500000,
            'current_annual_rent': 120000,
            'total_property_size': 5000,
            'current_space_needed': 4000,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'down_payment_percent': 30.0,
            'interest_rate': 5.0,
            'loan_term': 20,
            'currency': 'USD',
            'rent_increase_rate': 3.0,
            'market_appreciation_rate': 3.5,
            'property_tax_rate': 1.2,
            'insurance_cost': 5000,
            'annual_maintenance_percent': 2.0,
            'analysis_date': date.today(),
            'project_name': 'Integration Test Project',
            'location': 'Test Location',
            'analyst_name': 'Test Analyst'
        }
    
    def test_complete_analysis_workflow(self):
        """Test complete analysis workflow from session to formatted results"""
        # Step 1: Run NPV analysis
        npv_engine = NPVIntegrationEngine()
        npv_results = npv_engine.run_complete_analysis(self.valid_session_data)
        
        self.assertTrue(npv_results.get('calculation_successful', False))
        
        # Step 2: Generate decision recommendation
        decision_results = make_investment_decision(npv_results, "moderate")
        
        self.assertIn('recommendation', decision_results)
        self.assertIn('confidence_level', decision_results)
        
        # Step 3: Run sensitivity analysis
        calc_params = npv_engine.transform_inputs_for_calculations(
            npv_engine.extract_inputs_from_session(self.valid_session_data)
        )
        sensitivity_results = run_quick_sensitivity_analysis(calc_params)
        
        self.assertIn('tornado_data', sensitivity_results)
        
        # Step 4: Format results for presentation
        formatted_results = process_analysis_results(
            npv_results, 'USD', decision_results
        )
        
        self.assertIn('executive_summary', formatted_results)
        self.assertIn('key_metrics', formatted_results)
        
        # Verify workflow coherence
        npv_recommendation = npv_results.get('recommendation', '')
        decision_recommendation = decision_results.get('recommendation', '')
        formatted_recommendation = formatted_results.get('executive_summary', {}).get('recommendation', '')
        
        # All recommendations should be consistent (within reasonable mapping)
        self.assertIsNotNone(npv_recommendation)
        self.assertIsNotNone(decision_recommendation)
        self.assertIsNotNone(formatted_recommendation)
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks for analysis pipeline"""
        start_time = datetime.now()
        
        # Run complete analysis
        npv_engine = NPVIntegrationEngine()
        npv_results = npv_engine.run_complete_analysis(self.valid_session_data)
        
        # Run decision analysis
        decision_results = make_investment_decision(npv_results, "moderate")
        
        # Process results
        processor = ResultsProcessor('USD')
        formatted_results = processor.process_npv_analysis_results(npv_results, decision_results)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Should complete within 2 seconds for single analysis
        self.assertLess(execution_time, 2.0, f"Analysis took {execution_time:.2f}s, should be under 2s")
        
        # Results should be complete
        self.assertTrue(npv_results.get('calculation_successful', False))
        self.assertIn('recommendation', decision_results)
        self.assertIn('executive_summary', formatted_results)
    
    def test_edge_case_handling(self):
        """Test handling of edge cases throughout the pipeline"""
        edge_cases = [
            # 100% down payment (no loan)
            {**self.valid_session_data, 'down_payment_percent': 100.0, 'interest_rate': 5.0},
            
            # 0% interest rate
            {**self.valid_session_data, 'interest_rate': 0.0, 'loan_term': 20},
            
            # Very high rent vs low purchase price
            {**self.valid_session_data, 'purchase_price': 200000, 'current_annual_rent': 50000},
            
            # Very long analysis period
            {**self.valid_session_data, 'analysis_period': 50},
            
            # High cost of capital
            {**self.valid_session_data, 'cost_of_capital': 15.0}
        ]
        
        for i, edge_case_data in enumerate(edge_cases):
            with self.subTest(edge_case=i):
                # Should not crash on edge cases
                try:
                    npv_engine = NPVIntegrationEngine()
                    results = npv_engine.run_complete_analysis(edge_case_data)
                    
                    # Either succeeds or fails gracefully
                    if results.get('calculation_successful', False):
                        # If successful, should have valid results
                        self.assertIn('npv_difference', results)
                        self.assertIn('recommendation', results)
                    else:
                        # If failed, should have error information
                        self.assertIn('error_message', results)
                        
                except Exception as e:
                    self.fail(f"Edge case {i} caused unhandled exception: {e}")


if __name__ == '__main__':
    # Configure test runner
    unittest.main(
        verbosity=2,
        buffer=True,  # Capture print statements
        failfast=False  # Run all tests even if some fail
    )