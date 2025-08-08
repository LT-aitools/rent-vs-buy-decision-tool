"""
Sensitivity Analysis Engine
Parameter variation engine with impact analysis and break-even calculations

This module provides:
- Multi-parameter sensitivity analysis with configurable ranges
- Break-even point calculations for key variables
- Impact analysis showing parameter influence on NPV decisions
- Scenario comparison functionality with tornado diagrams
- Risk assessment through parameter variation

All sensitivity analysis follows the Business PRD specifications exactly.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import traceback
import time

from .npv_integration import NPVIntegrationEngine

logger = logging.getLogger(__name__)


class SensitivityAnalyzer:
    """
    Advanced Sensitivity Analysis Engine
    
    Performs comprehensive parameter sensitivity analysis to understand
    how changes in key assumptions affect the NPV recommendation.
    """
    
    def __init__(self):
        """Initialize the Sensitivity Analyzer"""
        self.npv_engine = NPVIntegrationEngine()
        self.base_parameters = {}
        self.sensitivity_results = {}
        
    def configure_base_parameters(self, base_params: Dict[str, Any]):
        """
        Configure base case parameters for sensitivity analysis
        
        Args:
            base_params: Base case calculation parameters
        """
        self.base_parameters = base_params.copy()
        
    def define_sensitivity_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Define parameters for sensitivity analysis with ranges
        
        Returns:
            Dictionary of parameters with their variation ranges
        """
        return {
            'interest_rate': {
                'base_value': self.base_parameters.get('interest_rate', 5.0),
                'min_value': 1.0,
                'max_value': 12.0,
                'step_count': 11,
                'label': 'Interest Rate (%)',
                'critical': True
            },
            'market_appreciation_rate': {
                'base_value': self.base_parameters.get('market_appreciation_rate', 3.0),
                'min_value': 0.0,
                'max_value': 8.0,
                'step_count': 9,
                'label': 'Market Appreciation Rate (%)',
                'critical': True
            },
            'rent_increase_rate': {
                'base_value': self.base_parameters.get('rent_increase_rate', 3.0),
                'min_value': 0.0,
                'max_value': 8.0,
                'step_count': 9,
                'label': 'Rent Increase Rate (%)',
                'critical': True
            },
            'cost_of_capital': {
                'base_value': self.base_parameters.get('cost_of_capital', 8.0),
                'min_value': 4.0,
                'max_value': 15.0,
                'step_count': 12,
                'label': 'Cost of Capital (%)',
                'critical': True
            },
            'down_payment_pct': {
                'base_value': self.base_parameters.get('down_payment_pct', 30.0),
                'min_value': 10.0,
                'max_value': 100.0,
                'step_count': 10,
                'label': 'Down Payment (%)',
                'critical': False
            },
            'property_tax_rate': {
                'base_value': self.base_parameters.get('property_tax_rate', 1.2),
                'min_value': 0.5,
                'max_value': 3.0,
                'step_count': 6,
                'label': 'Property Tax Rate (%)',
                'critical': False
            },
            'purchase_price': {
                'base_value': self.base_parameters.get('purchase_price', 500000),
                'min_value': self.base_parameters.get('purchase_price', 500000) * 0.8,
                'max_value': self.base_parameters.get('purchase_price', 500000) * 1.2,
                'step_count': 9,
                'label': 'Purchase Price',
                'critical': True
            },
            'current_annual_rent': {
                'base_value': self.base_parameters.get('current_annual_rent', 120000),
                'min_value': self.base_parameters.get('current_annual_rent', 120000) * 0.8,
                'max_value': self.base_parameters.get('current_annual_rent', 120000) * 1.2,
                'step_count': 9,
                'label': 'Annual Rent',
                'critical': True
            }
        }
    
    def run_single_parameter_sensitivity(
        self, 
        parameter_name: str, 
        test_values: List[float]
    ) -> Dict[str, Any]:
        """
        Run sensitivity analysis for a single parameter
        
        Args:
            parameter_name: Name of parameter to vary
            test_values: List of values to test
            
        Returns:
            Sensitivity analysis results for the parameter
        """
        if not self.base_parameters:
            raise ValueError("Base parameters not configured. Call configure_base_parameters() first.")
        
        results = {
            'parameter_name': parameter_name,
            'test_values': test_values,
            'npv_differences': [],
            'recommendations': [],
            'calculation_errors': [],
            'break_even_value': None,
            'sensitivity_range': 0.0
        }
        
        for test_value in test_values:
            try:
                # Create modified parameters
                test_params = self.base_parameters.copy()
                test_params[parameter_name] = test_value
                
                # Ensure all required parameters are present
                if 'loan_term' not in test_params:
                    test_params['loan_term'] = 20
                if 'transaction_costs' not in test_params:
                    test_params['transaction_costs'] = test_params.get('purchase_price', 500000) * 0.05
                
                # Calculate NPV with modified parameter
                npv_results = self.npv_engine.execute_npv_analysis(test_params)
                
                if npv_results.get('calculation_successful', False):
                    npv_diff = npv_results.get('npv_difference', 0)
                    recommendation = npv_results.get('recommendation', 'ERROR')
                    
                    results['npv_differences'].append(npv_diff)
                    results['recommendations'].append(recommendation)
                else:
                    results['npv_differences'].append(0.0)
                    results['recommendations'].append('ERROR')
                    results['calculation_errors'].append(f"Value {test_value}: {npv_results.get('error_message', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Sensitivity analysis error for {parameter_name}={test_value}: {e}")
                results['npv_differences'].append(0.0)
                results['recommendations'].append('ERROR')
                results['calculation_errors'].append(f"Value {test_value}: {str(e)}")
        
        # Calculate break-even point and sensitivity range
        results['break_even_value'] = self._find_break_even_point(test_values, results['npv_differences'])
        results['sensitivity_range'] = max(results['npv_differences']) - min(results['npv_differences']) if results['npv_differences'] else 0.0
        
        return results
    
    def run_comprehensive_sensitivity_analysis(
        self, 
        focus_on_critical: bool = True
    ) -> Dict[str, Any]:
        """
        Run comprehensive sensitivity analysis on all key parameters
        
        Args:
            focus_on_critical: If True, only analyze critical parameters
            
        Returns:
            Complete sensitivity analysis results
        """
        if not self.base_parameters:
            raise ValueError("Base parameters not configured. Call configure_base_parameters() first.")
        
        # Get parameter definitions
        param_definitions = self.define_sensitivity_parameters()
        
        # Filter to critical parameters if requested
        if focus_on_critical:
            param_definitions = {k: v for k, v in param_definitions.items() if v.get('critical', False)}
        
        analysis_results = {
            'base_case_npv': None,
            'parameter_results': {},
            'tornado_data': [],
            'most_sensitive_parameter': None,
            'break_even_summary': {},
            'analysis_summary': {}
        }
        
        # Calculate base case
        try:
            # Ensure base parameters include all required fields
            complete_base_params = self.base_parameters.copy()
            if 'loan_term' not in complete_base_params:
                complete_base_params['loan_term'] = 20
            if 'transaction_costs' not in complete_base_params:
                complete_base_params['transaction_costs'] = complete_base_params.get('purchase_price', 500000) * 0.05
                
            base_npv_results = self.npv_engine.execute_npv_analysis(complete_base_params)
            if base_npv_results.get('calculation_successful', False):
                analysis_results['base_case_npv'] = base_npv_results.get('npv_difference', 0)
            else:
                analysis_results['base_case_npv'] = 0
        except Exception as e:
            logger.error(f"Base case calculation failed: {e}")
            analysis_results['base_case_npv'] = 0
        
        # Run sensitivity analysis for each parameter
        max_sensitivity = 0
        most_sensitive_param = None
        
        for param_name, param_config in param_definitions.items():
            try:
                # Generate test values
                test_values = np.linspace(
                    param_config['min_value'],
                    param_config['max_value'],
                    param_config['step_count']
                ).tolist()
                
                # Run single parameter analysis
                param_results = self.run_single_parameter_sensitivity(param_name, test_values)
                analysis_results['parameter_results'][param_name] = param_results
                
                # Update tornado data
                sensitivity_range = param_results['sensitivity_range']
                analysis_results['tornado_data'].append({
                    'parameter': param_config['label'],
                    'sensitivity_range': sensitivity_range,
                    'parameter_name': param_name
                })
                
                # Track most sensitive parameter
                if sensitivity_range > max_sensitivity:
                    max_sensitivity = sensitivity_range
                    most_sensitive_param = param_name
                
                # Update break-even summary
                break_even = param_results['break_even_value']
                if break_even is not None:
                    analysis_results['break_even_summary'][param_name] = {
                        'break_even_value': break_even,
                        'base_value': param_config['base_value'],
                        'label': param_config['label']
                    }
                    
            except Exception as e:
                logger.error(f"Sensitivity analysis failed for {param_name}: {e}")
                analysis_results['parameter_results'][param_name] = {
                    'error': str(e),
                    'parameter_name': param_name
                }
        
        # Sort tornado data by sensitivity range
        analysis_results['tornado_data'].sort(key=lambda x: x['sensitivity_range'], reverse=True)
        analysis_results['most_sensitive_parameter'] = most_sensitive_param
        
        # Generate analysis summary
        analysis_results['analysis_summary'] = self._generate_sensitivity_summary(analysis_results)
        
        self.sensitivity_results = analysis_results
        return analysis_results
    
    def run_scenario_analysis(
        self, 
        scenarios: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Run analysis for multiple pre-defined scenarios
        
        Args:
            scenarios: Dictionary of scenario names to parameter overrides
            
        Returns:
            Scenario comparison results
        """
        if not self.base_parameters:
            raise ValueError("Base parameters not configured. Call configure_base_parameters() first.")
        
        scenario_results = {
            'base_case': None,
            'scenarios': {},
            'comparison_table': [],
            'best_case_scenario': None,
            'worst_case_scenario': None,
            'scenario_ranking': []
        }
        
        # Calculate base case
        try:
            base_npv_results = self.npv_engine.execute_npv_analysis(self.base_parameters)
            scenario_results['base_case'] = {
                'npv_difference': base_npv_results.get('npv_difference', 0),
                'recommendation': base_npv_results.get('recommendation', 'ERROR'),
                'ownership_npv': base_npv_results.get('ownership_npv', 0),
                'rental_npv': base_npv_results.get('rental_npv', 0)
            }
        except Exception as e:
            logger.error(f"Base case scenario calculation failed: {e}")
        
        # Calculate each scenario
        best_npv = float('-inf')
        worst_npv = float('inf')
        best_scenario = None
        worst_scenario = None
        
        for scenario_name, parameter_overrides in scenarios.items():
            try:
                # Create scenario parameters
                scenario_params = self.base_parameters.copy()
                scenario_params.update(parameter_overrides)
                
                # Ensure all required parameters are present
                if 'loan_term' not in scenario_params:
                    scenario_params['loan_term'] = 20
                if 'transaction_costs' not in scenario_params:
                    scenario_params['transaction_costs'] = scenario_params.get('purchase_price', 500000) * 0.05
                
                # Calculate NPV for scenario
                npv_results = self.npv_engine.execute_npv_analysis(scenario_params)
                
                if npv_results.get('calculation_successful', False):
                    npv_diff = npv_results.get('npv_difference', 0)
                    
                    scenario_result = {
                        'npv_difference': npv_diff,
                        'recommendation': npv_results.get('recommendation', 'ERROR'),
                        'ownership_npv': npv_results.get('ownership_npv', 0),
                        'rental_npv': npv_results.get('rental_npv', 0),
                        'parameter_overrides': parameter_overrides,
                        'calculation_successful': True
                    }
                    
                    # Track best and worst scenarios
                    if npv_diff > best_npv:
                        best_npv = npv_diff
                        best_scenario = scenario_name
                    
                    if npv_diff < worst_npv:
                        worst_npv = npv_diff
                        worst_scenario = scenario_name
                        
                else:
                    scenario_result = {
                        'error_message': npv_results.get('error_message', 'Unknown error'),
                        'calculation_successful': False,
                        'parameter_overrides': parameter_overrides
                    }
                
                scenario_results['scenarios'][scenario_name] = scenario_result
                
            except Exception as e:
                logger.error(f"Scenario analysis failed for {scenario_name}: {e}")
                scenario_results['scenarios'][scenario_name] = {
                    'error_message': str(e),
                    'calculation_successful': False,
                    'parameter_overrides': parameter_overrides
                }
        
        # Create comparison table and ranking
        successful_scenarios = {name: result for name, result in scenario_results['scenarios'].items() 
                              if result.get('calculation_successful', False)}
        
        scenario_results['scenario_ranking'] = sorted(
            successful_scenarios.items(),
            key=lambda x: x[1]['npv_difference'],
            reverse=True
        )
        
        scenario_results['best_case_scenario'] = best_scenario
        scenario_results['worst_case_scenario'] = worst_scenario
        
        # Create comparison table
        for scenario_name, result in scenario_results['scenarios'].items():
            if result.get('calculation_successful', False):
                scenario_results['comparison_table'].append({
                    'scenario': scenario_name,
                    'npv_difference': result['npv_difference'],
                    'recommendation': result['recommendation'],
                    'vs_base_case': result['npv_difference'] - (scenario_results['base_case']['npv_difference'] if scenario_results['base_case'] else 0)
                })
        
        return scenario_results
    
    def calculate_break_even_analysis(
        self, 
        target_parameters: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate break-even points for specific parameters
        
        Args:
            target_parameters: List of parameter names to find break-even points for
            
        Returns:
            Break-even analysis results
        """
        if not self.base_parameters:
            raise ValueError("Base parameters not configured. Call configure_base_parameters() first.")
        
        param_definitions = self.define_sensitivity_parameters()
        break_even_results = {}
        
        for param_name in target_parameters:
            if param_name not in param_definitions:
                logger.warning(f"Parameter {param_name} not found in definitions")
                continue
                
            param_config = param_definitions[param_name]
            
            try:
                # Use binary search to find break-even point
                break_even_value = self._binary_search_break_even(
                    param_name,
                    param_config['min_value'],
                    param_config['max_value']
                )
                
                break_even_results[param_name] = {
                    'break_even_value': break_even_value,
                    'base_value': param_config['base_value'],
                    'label': param_config['label'],
                    'percentage_change': ((break_even_value - param_config['base_value']) / param_config['base_value'] * 100) if param_config['base_value'] != 0 else None,
                    'break_even_found': break_even_value is not None
                }
                
            except Exception as e:
                logger.error(f"Break-even calculation failed for {param_name}: {e}")
                break_even_results[param_name] = {
                    'error_message': str(e),
                    'break_even_found': False
                }
        
        return break_even_results
    
    def _find_break_even_point(
        self, 
        test_values: List[float], 
        npv_differences: List[float]
    ) -> Optional[float]:
        """Find break-even point where NPV difference crosses zero"""
        if len(test_values) != len(npv_differences):
            return None
        
        for i in range(len(npv_differences) - 1):
            current_npv = npv_differences[i]
            next_npv = npv_differences[i + 1]
            
            # Check if NPV crosses zero between these points
            if (current_npv <= 0 <= next_npv) or (next_npv <= 0 <= current_npv):
                # Linear interpolation to find exact break-even point
                current_value = test_values[i]
                next_value = test_values[i + 1]
                
                if next_npv == current_npv:
                    return current_value
                
                # Linear interpolation: y = mx + b, solve for x when y = 0
                slope = (next_npv - current_npv) / (next_value - current_value)
                intercept = current_npv - slope * current_value
                break_even = -intercept / slope if slope != 0 else None
                
                # Verify break-even is within range
                if (break_even is not None and 
                    min(current_value, next_value) <= break_even <= max(current_value, next_value)):
                    return break_even
        
        return None
    
    def _binary_search_break_even(
        self, 
        parameter_name: str, 
        min_val: float, 
        max_val: float, 
        tolerance: float = 1000.0,
        timeout_seconds: float = 30.0
    ) -> Optional[float]:
        """
        Use binary search to find precise break-even point with timeout protection
        
        Args:
            parameter_name: Name of parameter to vary
            min_val: Minimum parameter value
            max_val: Maximum parameter value
            tolerance: NPV difference tolerance for break-even
            timeout_seconds: Maximum time to spend searching
        """
        max_iterations = 20
        start_time = time.time()
        
        for iteration in range(max_iterations):
            # Check timeout
            if time.time() - start_time > timeout_seconds:
                logger.warning(f"Binary search timeout after {timeout_seconds}s for {parameter_name}")
                break
            mid_val = (min_val + max_val) / 2
            
            try:
                # Test NPV at midpoint
                test_params = self.base_parameters.copy()
                test_params[parameter_name] = mid_val
                
                npv_results = self.npv_engine.execute_npv_analysis(test_params)
                
                if not npv_results.get('calculation_successful', False):
                    break
                
                npv_diff = npv_results.get('npv_difference', 0)
                
                # Check if we're close enough to zero
                if abs(npv_diff) <= tolerance:
                    return mid_val
                
                # Adjust search range
                if npv_diff > 0:
                    max_val = mid_val
                else:
                    min_val = mid_val
                    
                # Check convergence
                if abs(max_val - min_val) < (max_val - min_val) * 0.01:  # 1% convergence
                    break
                    
            except Exception as e:
                logger.error(f"Binary search error at {parameter_name}={mid_val}: {e}")
                break
        
        return (min_val + max_val) / 2 if abs(max_val - min_val) < tolerance else None
    
    def _generate_sensitivity_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of sensitivity analysis"""
        
        summary = {
            'total_parameters_analyzed': len(analysis_results['parameter_results']),
            'most_sensitive_parameter': None,
            'least_sensitive_parameter': None,
            'parameters_with_break_even': 0,
            'recommendation_stability': 'High',  # High/Medium/Low
            'key_insights': [],
            'risk_factors': []
        }
        
        # Find most and least sensitive parameters
        tornado_data = analysis_results.get('tornado_data', [])
        if tornado_data:
            summary['most_sensitive_parameter'] = tornado_data[0]['parameter_name']
            summary['least_sensitive_parameter'] = tornado_data[-1]['parameter_name']
        
        # Count parameters with break-even points
        break_even_summary = analysis_results.get('break_even_summary', {})
        summary['parameters_with_break_even'] = len(break_even_summary)
        
        # Analyze recommendation stability
        base_case_npv = analysis_results.get('base_case_npv', 0)
        if base_case_npv is None:
            base_case_npv = 0
            
        recommendation_changes = 0
        total_scenarios = 0
        
        for param_results in analysis_results['parameter_results'].values():
            if 'recommendations' in param_results:
                recommendations = param_results['recommendations']
                base_recommendation = 'BUY' if base_case_npv > 0 else 'RENT'
                
                for rec in recommendations:
                    total_scenarios += 1
                    if rec != 'ERROR' and ((base_recommendation == 'BUY' and rec in ['RENT', 'STRONG_RENT', 'MARGINAL_RENT']) or
                                         (base_recommendation == 'RENT' and rec in ['BUY', 'STRONG_BUY', 'MARGINAL_BUY'])):
                        recommendation_changes += 1
        
        if total_scenarios > 0:
            change_rate = recommendation_changes / total_scenarios
            if change_rate <= 0.1:
                summary['recommendation_stability'] = 'High'
            elif change_rate <= 0.3:
                summary['recommendation_stability'] = 'Medium'
            else:
                summary['recommendation_stability'] = 'Low'
        
        # Generate key insights
        if summary['most_sensitive_parameter']:
            most_sensitive = summary['most_sensitive_parameter']
            summary['key_insights'].append(f"Decision is most sensitive to changes in {most_sensitive}")
        
        if summary['recommendation_stability'] == 'Low':
            summary['risk_factors'].append("Recommendation changes frequently with parameter variations")
        
        if summary['parameters_with_break_even'] >= 3:
            summary['key_insights'].append(f"Break-even points identified for {summary['parameters_with_break_even']} parameters")
        
        return summary
    
    def get_tornado_chart_data(self) -> List[Dict[str, Any]]:
        """
        Get data formatted for tornado chart visualization
        
        Returns:
            List of data points for tornado chart
        """
        if not self.sensitivity_results:
            return []
        
        tornado_data = self.sensitivity_results.get('tornado_data', [])
        return sorted(tornado_data, key=lambda x: x['sensitivity_range'], reverse=True)
    
    def export_sensitivity_results(self) -> Dict[str, Any]:
        """
        Export all sensitivity analysis results
        
        Returns:
            Complete sensitivity analysis data
        """
        return {
            'sensitivity_results': self.sensitivity_results.copy(),
            'base_parameters': self.base_parameters.copy(),
            'parameter_definitions': self.define_sensitivity_parameters(),
            'export_timestamp': np.datetime64('now').isoformat()
        }


# Convenience functions for external use
def run_quick_sensitivity_analysis(base_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run quick sensitivity analysis on critical parameters
    
    Args:
        base_params: Base case parameters
        
    Returns:
        Sensitivity analysis results
    """
    analyzer = SensitivityAnalyzer()
    analyzer.configure_base_parameters(base_params)
    return analyzer.run_comprehensive_sensitivity_analysis(focus_on_critical=True)


def calculate_parameter_break_even(base_params: Dict[str, Any], parameter_name: str) -> Optional[float]:
    """
    Calculate break-even point for a specific parameter
    
    Args:
        base_params: Base case parameters
        parameter_name: Parameter to analyze
        
    Returns:
        Break-even value or None if not found
    """
    analyzer = SensitivityAnalyzer()
    analyzer.configure_base_parameters(base_params)
    
    results = analyzer.calculate_break_even_analysis([parameter_name])
    return results.get(parameter_name, {}).get('break_even_value')


if __name__ == "__main__":
    # Test the sensitivity analyzer
    print("Testing Sensitivity Analyzer...")
    
    # Create test base parameters
    test_params = {
        'purchase_price': 500000,
        'current_annual_rent': 120000,
        'down_payment_pct': 30.0,
        'interest_rate': 5.0,
        'market_appreciation_rate': 3.0,
        'rent_increase_rate': 3.0,
        'cost_of_capital': 8.0,
        'analysis_period': 25,
        'property_tax_rate': 1.2,
        'insurance_cost': 5000,
        'annual_maintenance': 10000
    }
    
    # Test sensitivity analysis
    analyzer = SensitivityAnalyzer()
    analyzer.configure_base_parameters(test_params)
    
    # Run single parameter test
    test_values = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    single_result = analyzer.run_single_parameter_sensitivity('interest_rate', test_values)
    
    print(f"✅ Single parameter test completed")
    print(f"Interest Rate Break-Even: {single_result.get('break_even_value')}")
    print(f"Sensitivity Range: ${single_result.get('sensitivity_range', 0):,.0f}")
    
    # Test comprehensive analysis (limited for demo)
    print("\n🔍 Running comprehensive analysis (critical parameters only)...")
    comprehensive_results = analyzer.run_comprehensive_sensitivity_analysis(focus_on_critical=True)
    
    most_sensitive = comprehensive_results.get('most_sensitive_parameter')
    tornado_data = comprehensive_results.get('tornado_data', [])
    
    print(f"✅ Comprehensive analysis completed")
    print(f"Most Sensitive Parameter: {most_sensitive}")
    print(f"Parameters Analyzed: {len(tornado_data)}")
    
    if tornado_data:
        print("\nTop 3 Most Sensitive Parameters:")
        for i, item in enumerate(tornado_data[:3]):
            print(f"  {i+1}. {item['parameter']}: ${item['sensitivity_range']:,.0f} range")