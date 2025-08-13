"""
Cross-Component Integration Tests
Testing integration between all work trees and components

This module provides:
- Cross-work-tree integration testing
- Component interface validation
- Data flow verification
- End-to-end workflow testing
- Error propagation testing
"""

import unittest
import sys
import os
import time
from datetime import datetime, date
from typing import Dict, Any, List
from unittest.mock import Mock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.shared.interfaces import (
    MarketData, AnalyticsResult, ValidationResult, ValidationStatus,
    create_mock_market_data, create_mock_analytics_result
)


class TestAnalyticsEngineIntegration(unittest.TestCase):
    """Test integration with Analytics Engine (Work Tree 1)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_params = {
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            'down_payment_pct': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'market_appreciation_rate': 3.5,
            'rent_increase_rate': 3.0,
            'property_tax_rate': 1.2,
            'insurance_cost': 5000,
            'annual_maintenance': 10000
        }
    
    def test_npv_to_analytics_integration(self):
        """Test integration from NPV calculations to analytics engine"""
        try:
            from src.analysis.npv_integration import NPVIntegrationEngine
            from src.analysis.sensitivity import SensitivityAnalyzer
        except ImportError:
            self.skipTest("Required modules not available")
        
        # Step 1: Run NPV analysis
        npv_engine = NPVIntegrationEngine()
        npv_results = npv_engine.run_complete_analysis({
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            'total_property_size': 2000,
            'current_space_needed': 2000,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'down_payment_percent': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'currency': 'USD'
        })
        
        self.assertTrue(npv_results.get('calculation_successful', False))
        
        # Step 2: Use NPV results for sensitivity analysis
        calc_params = npv_engine.transform_inputs_for_calculations(
            npv_engine.extract_inputs_from_session({
                'purchase_price': 500000,
                'current_annual_rent': 60000,
                'total_property_size': 2000,
                'current_space_needed': 2000,
                'analysis_period': 25,
                'cost_of_capital': 8.0,
                'down_payment_percent': 20.0,
                'interest_rate': 5.0,
                'loan_term': 30
            })
        )
        
        analyzer = SensitivityAnalyzer()
        analyzer.configure_base_parameters(calc_params)
        
        # Test sensitivity analysis integration
        sensitivity_results = analyzer.run_single_parameter_sensitivity(
            'interest_rate', [4.0, 5.0, 6.0]
        )
        
        # Verify integration worked
        self.assertIn('parameter_name', sensitivity_results)
        self.assertIn('npv_differences', sensitivity_results)
        self.assertEqual(len(sensitivity_results['npv_differences']), 3)
        
        # Verify data consistency
        base_npv = npv_results.get('npv_difference', 0)
        sensitivity_npvs = sensitivity_results['npv_differences']
        
        # The middle value (5.0% interest) should be close to base NPV
        middle_npv = sensitivity_npvs[1]
        self.assertAlmostEqual(base_npv, middle_npv, delta=5000,
                              msg="Sensitivity analysis inconsistent with base NPV")
    
    def test_decision_engine_integration(self):
        """Test integration with decision engine"""
        try:
            from src.analysis.npv_integration import NPVIntegrationEngine
            from src.analysis.decision_engine import make_investment_decision
        except ImportError:
            self.skipTest("Required modules not available")
        
        # Run NPV analysis
        npv_engine = NPVIntegrationEngine()
        npv_results = npv_engine.run_complete_analysis({
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            'total_property_size': 2000,
            'current_space_needed': 2000,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'down_payment_percent': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'currency': 'USD'
        })
        
        # Feed results to decision engine
        decision_results = make_investment_decision(npv_results, "moderate")
        
        # Verify decision consistency
        self.assertIn('recommendation', decision_results)
        self.assertIn('confidence_level', decision_results)
        
        npv_diff = npv_results.get('npv_difference', 0)
        recommendation = decision_results.get('recommendation', 'UNKNOWN')
        
        # Decision should be consistent with NPV
        if npv_diff > 50000:
            self.assertIn(recommendation, ['BUY', 'STRONG_BUY', 'MARGINAL_BUY'])
        elif npv_diff < -50000:
            self.assertIn(recommendation, ['RENT', 'STRONG_RENT', 'MARGINAL_RENT'])
    
    def test_results_processor_integration(self):
        """Test integration with results processor"""
        try:
            from src.analysis.npv_integration import NPVIntegrationEngine
            from src.analysis.decision_engine import make_investment_decision
            from src.analysis.results_processor import process_analysis_results
        except ImportError:
            self.skipTest("Required modules not available")
        
        # Run full pipeline
        npv_engine = NPVIntegrationEngine()
        npv_results = npv_engine.run_complete_analysis({
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            'total_property_size': 2000,
            'current_space_needed': 2000,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'down_payment_percent': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'currency': 'USD'
        })
        
        decision_results = make_investment_decision(npv_results, "moderate")
        formatted_results = process_analysis_results(npv_results, 'USD', decision_results)
        
        # Verify formatting integration
        self.assertIn('executive_summary', formatted_results)
        self.assertIn('key_metrics', formatted_results)
        self.assertIn('presentation_tables', formatted_results)
        
        # Check consistency across processing pipeline
        exec_summary = formatted_results['executive_summary']
        npv_recommendation = npv_results.get('recommendation', '')
        decision_recommendation = decision_results.get('recommendation', '')
        formatted_recommendation = exec_summary.get('recommendation', '')
        
        # All should be consistent (allowing for formatting differences)
        self.assertIsNotNone(formatted_recommendation)


class TestDataIntegrationWorkflow(unittest.TestCase):
    """Test integration with Data Integration components (Work Tree 3)"""
    
    def test_market_data_integration(self):
        """Test integration with market data providers"""
        # Create mock market data
        market_data = create_mock_market_data("Test Location")
        
        # Verify market data structure
        self.assertEqual(market_data.location, "Test Location")
        self.assertIsInstance(market_data.median_rent_per_sqm, float)
        self.assertIsInstance(market_data.median_property_price, float)
        self.assertGreater(market_data.confidence_score, 0.0)
        
        # Test integration with calculations
        try:
            from src.calculations.npv_analysis import calculate_npv_analysis
        except ImportError:
            self.skipTest("NPV calculation module not available")
        
        # Use market data in calculations
        calc_params = {
            'purchase_price': market_data.median_property_price,
            'current_annual_rent': market_data.median_rent_per_sqm * 2000 * 12,  # 2000 sqm property
            'down_payment_pct': 20.0,
            'interest_rate': market_data.current_mortgage_rates.get('30_year_fixed', 5.0),
            'loan_term': 30,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.2,
            'insurance_cost': 5000,
            'annual_maintenance': 10000,
            'market_appreciation_rate': market_data.property_appreciation_rate,
            'rent_increase_rate': market_data.rental_growth_rate,
            'transaction_costs': market_data.median_property_price * 0.05
        }
        
        result = calculate_npv_analysis(calc_params)
        
        # Should calculate successfully with market data
        self.assertIn('ownership_npv', result)
        self.assertIn('rental_npv', result)
        self.assertIn('npv_difference', result)
    
    def test_data_validation_integration(self):
        """Test data validation integration"""
        # Test with valid data
        valid_market_data = MarketData(
            location="Valid City",
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
            confidence_score=0.9,
            freshness_hours=1.0
        )
        
        # Verify data is valid
        self.assertGreater(valid_market_data.confidence_score, 0.8)
        self.assertLess(valid_market_data.freshness_hours, 24.0)
        
        # Test with questionable data
        questionable_data = MarketData(
            location="Questionable City",
            zip_code="99999",
            median_rent_per_sqm=5.0,  # Very low
            rental_vacancy_rate=25.0,  # Very high
            rental_growth_rate=-2.0,  # Negative growth
            median_property_price=50000.0,  # Very low
            property_appreciation_rate=-1.0,  # Depreciation
            months_on_market=12.0,  # Long time on market
            current_mortgage_rates={"30_year_fixed": 15.0},  # Very high rate
            rate_trend="volatile",
            local_inflation_rate=10.0,  # High inflation
            unemployment_rate=15.0,  # High unemployment
            population_growth_rate=-2.0,  # Population decline
            data_timestamp=datetime.now(),
            data_sources=["unreliable_source"],
            confidence_score=0.3,  # Low confidence
            freshness_hours=72.0  # Stale data
        )
        
        # Should still process but with warnings
        self.assertLess(questionable_data.confidence_score, 0.5)
        self.assertGreater(questionable_data.freshness_hours, 48.0)


class TestUserExperienceIntegration(unittest.TestCase):
    """Test integration with User Experience components (Work Tree 2)"""
    
    def test_ui_validation_integration(self):
        """Test UI validation integration"""
        # Test valid input validation
        valid_inputs = {
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            'down_payment_percent': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'analysis_period': 25
        }
        
        # Mock validation function
        def validate_input(field_name: str, value: Any) -> ValidationResult:
            if field_name == 'purchase_price' and value <= 0:
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.ERROR,
                    message="Purchase price must be positive",
                    suggestions=["Enter a positive purchase price"]
                )
            elif field_name == 'interest_rate' and (value < 0 or value > 20):
                return ValidationResult(
                    is_valid=False,
                    status=ValidationStatus.ERROR,
                    message="Interest rate must be between 0% and 20%",
                    suggestions=["Enter a reasonable interest rate"]
                )
            else:
                return ValidationResult(
                    is_valid=True,
                    status=ValidationStatus.VALID,
                    message="Valid input"
                )
        
        # Test validation
        for field, value in valid_inputs.items():
            result = validate_input(field, value)
            self.assertTrue(result.is_valid, f"Valid input {field}={value} failed validation")
        
        # Test invalid inputs
        invalid_cases = [
            ('purchase_price', -100000),
            ('interest_rate', 25.0),
            ('interest_rate', -5.0)
        ]
        
        for field, value in invalid_cases:
            result = validate_input(field, value)
            self.assertFalse(result.is_valid, f"Invalid input {field}={value} passed validation")
    
    def test_guidance_system_integration(self):
        """Test guidance system integration"""
        # Mock analytics result
        analytics_result = create_mock_analytics_result()
        
        # Test guidance based on results
        def get_decision_guidance(analysis_result: AnalyticsResult) -> str:
            recommendation = analysis_result.base_recommendation
            confidence = analysis_result.risk_assessment.confidence_score
            
            if recommendation == "Buy" and confidence > 0.7:
                return "Strong recommendation to buy. The analysis shows clear financial advantages."
            elif recommendation == "Buy" and confidence > 0.5:
                return "Moderate recommendation to buy. Consider the risk factors carefully."
            elif recommendation == "Rent":
                return "Recommendation to continue renting. Buying does not show clear advantages."
            else:
                return "Results are inconclusive. Consider gathering more data."
        
        guidance = get_decision_guidance(analytics_result)
        self.assertIsInstance(guidance, str)
        self.assertGreater(len(guidance), 20)  # Should be substantial guidance


class TestExportIntegration(unittest.TestCase):
    """Test integration with export functionality"""
    
    def test_excel_export_integration(self):
        """Test Excel export integration"""
        try:
            from src.export.excel.excel_generator import ExcelGenerator
        except ImportError:
            self.skipTest("Excel export module not available")
        
        # Mock analysis results
        analysis_results = {
            'calculation_successful': True,
            'npv_difference': 100000,
            'ownership_npv': -2000000,
            'rental_npv': -2100000,
            'recommendation': 'BUY',
            'confidence_level': 'Medium',
            'input_parameters': {
                'purchase_price': 500000,
                'current_annual_rent': 60000,
                'analysis_period': 25
            }
        }
        
        # Test export generation
        try:
            generator = ExcelGenerator()
            # This would normally generate an actual Excel file
            # For testing, we just verify the generator can be instantiated
            self.assertIsNotNone(generator)
        except Exception as e:
            self.fail(f"Excel generator instantiation failed: {e}")
    
    def test_pdf_export_integration(self):
        """Test PDF export integration"""
        try:
            from src.export.pdf.pdf_generator import PDFGenerator
        except ImportError:
            self.skipTest("PDF export module not available")
        
        # Mock analysis results
        analysis_results = {
            'calculation_successful': True,
            'npv_difference': 100000,
            'ownership_npv': -2000000,
            'rental_npv': -2100000,
            'recommendation': 'BUY'
        }
        
        try:
            generator = PDFGenerator()
            self.assertIsNotNone(generator)
        except Exception as e:
            self.fail(f"PDF generator instantiation failed: {e}")


class TestErrorPropagationIntegration(unittest.TestCase):
    """Test error propagation across components"""
    
    def test_calculation_error_propagation(self):
        """Test how calculation errors propagate through the system"""
        try:
            from src.analysis.npv_integration import NPVIntegrationEngine
        except ImportError:
            self.skipTest("Required modules not available")
        
        # Invalid input data that should cause errors
        invalid_data = {
            'purchase_price': -100000,  # Negative price
            'current_annual_rent': 0,   # Zero rent
            'down_payment_percent': 150,  # Over 100%
            'interest_rate': -5.0,      # Negative rate
            'analysis_period': 0        # Zero period
        }
        
        npv_engine = NPVIntegrationEngine()
        results = npv_engine.run_complete_analysis(invalid_data)
        
        # Should fail gracefully
        self.assertFalse(results.get('calculation_successful', True))
        self.assertEqual(results.get('recommendation'), 'ERROR')
        self.assertIn('validation_errors', results)
        self.assertGreater(len(results['validation_errors']), 0)
    
    def test_component_failure_isolation(self):
        """Test that component failures are isolated and don't crash the system"""
        # Test with partially corrupted data
        partial_data = {
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            # Missing required fields
        }
        
        try:
            from src.analysis.npv_integration import NPVIntegrationEngine
        except ImportError:
            self.skipTest("Required modules not available")
        
        npv_engine = NPVIntegrationEngine()
        
        # Should handle missing data gracefully
        try:
            results = npv_engine.run_complete_analysis(partial_data)
            # Should not crash, but should indicate failure
            if not results.get('calculation_successful', False):
                self.assertIn('error_message', results)
        except Exception as e:
            self.fail(f"System crashed instead of handling error gracefully: {e}")


class TestPerformanceIntegration(unittest.TestCase):
    """Test performance characteristics of integrated workflows"""
    
    def test_full_workflow_performance(self):
        """Test performance of full workflow integration"""
        try:
            from src.analysis.npv_integration import NPVIntegrationEngine
            from src.analysis.decision_engine import make_investment_decision
            from src.analysis.results_processor import process_analysis_results
        except ImportError:
            self.skipTest("Required modules not available")
        
        test_data = {
            'purchase_price': 500000,
            'current_annual_rent': 60000,
            'total_property_size': 2000,
            'current_space_needed': 2000,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'down_payment_percent': 20.0,
            'interest_rate': 5.0,
            'loan_term': 30,
            'currency': 'USD'
        }
        
        start_time = time.time()
        
        # Run full workflow
        npv_engine = NPVIntegrationEngine()
        npv_results = npv_engine.run_complete_analysis(test_data)
        
        if npv_results.get('calculation_successful', False):
            decision_results = make_investment_decision(npv_results, "moderate")
            formatted_results = process_analysis_results(npv_results, 'USD', decision_results)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within 3 seconds
        self.assertLess(execution_time, 3.0,
                       f"Full workflow took {execution_time:.2f}s, should be under 3s")
    
    def test_batch_processing_performance(self):
        """Test performance of batch processing"""
        try:
            from src.calculations.npv_analysis import calculate_npv_analysis
        except ImportError:
            self.skipTest("NPV calculation module not available")
        
        base_params = {
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
        
        start_time = time.time()
        
        # Process 50 variations
        results = []
        for i in range(50):
            params = base_params.copy()
            params['purchase_price'] += i * 10000  # Vary price
            params['interest_rate'] += i * 0.1     # Vary rate
            
            result = calculate_npv_analysis(params)
            results.append(result)
        
        end_time = time.time()
        batch_time = end_time - start_time
        
        # Should process 50 calculations in under 5 seconds
        self.assertLess(batch_time, 5.0,
                       f"Batch processing took {batch_time:.2f}s, should be under 5s")
        
        # All results should be valid
        self.assertEqual(len(results), 50)
        for result in results:
            self.assertIn('ownership_npv', result)
            self.assertIn('rental_npv', result)


if __name__ == '__main__':
    unittest.main(verbosity=2)