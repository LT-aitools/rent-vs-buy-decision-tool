"""
Scenario Modeling Engine - Week 4 Analytics Component

Advanced scenario modeling and comparison engine for strategic decision analysis.
Implements the AnalyticsEngine interface for scenario analysis requirements.

Features:
- Multi-scenario comparison with parameter variations
- Probabilistic scenario analysis
- Best/worst case scenario identification
- Scenario ranking and optimization
- Economic scenario modeling (recession, boom, stable)
- Custom scenario definition and analysis

Performance Target: Fast scenario comparison and ranking
Accuracy Target: 95%+ statistical accuracy in scenario comparisons
"""

import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from shared.interfaces import (
    AnalyticsEngine, ScenarioDefinition, AnalyticsResult,
    MonteCarloResult, RiskAssessment, RiskLevel, SensitivityResult
)
from calculations.npv_analysis import calculate_npv_comparison
from analytics.input_validation import validate_and_sanitize_base_params, ValidationError, SecurityError

logger = logging.getLogger(__name__)


class EconomicScenarioType(Enum):
    """Standard economic scenario types"""
    RECESSION = "recession"
    STABLE = "stable"
    GROWTH = "growth"
    BOOM = "boom"
    INFLATION = "high_inflation"
    DEFLATION = "deflation"


@dataclass
class ScenarioConfig:
    """Configuration for scenario modeling"""
    max_workers: int = 4
    timeout_seconds: float = 10.0
    include_monte_carlo: bool = False
    monte_carlo_iterations: int = 5000
    confidence_levels: List[int] = None
    
    def __post_init__(self):
        if self.confidence_levels is None:
            self.confidence_levels = [90, 95]


class ScenarioModelingEngine(AnalyticsEngine):
    """
    Advanced scenario modeling engine implementing AnalyticsEngine interface.
    
    Provides comprehensive scenario analysis, comparison, and optimization.
    """
    
    def __init__(self, config: Optional[ScenarioConfig] = None):
        self.config = config or ScenarioConfig()
        # LRU cache with size limit to prevent memory leaks
        self._scenario_cache = {}
        self._cache_lock = threading.Lock()
        self._cache_max_size = 75  # Maximum cached scenario analyses
        self._cache_access_order = []  # Track access order for LRU
        
    def run_scenario_analysis(
        self,
        base_params: Dict[str, float],
        scenarios: List[ScenarioDefinition]
    ) -> List[Dict[str, Any]]:
        """
        Run comprehensive scenario analysis and comparison.
        
        Args:
            base_params: Base case parameters for NPV calculation
            scenarios: List of scenario definitions to analyze
            
        Returns:
            List of scenario comparison results with rankings and analysis
        """
        start_time = time.time()
        
        # Validate and sanitize inputs
        try:
            sanitized_base_params = validate_and_sanitize_base_params(base_params)
        except (ValidationError, SecurityError) as e:
            logger.error(f"Input validation failed: {e}")
            raise ValueError(f"Invalid input parameters: {e}")
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            raise ValueError(f"Parameter validation failed: {e}")
        
        if not scenarios:
            raise ValueError("Scenarios list cannot be empty")
        
        # Validate scenario count
        if len(scenarios) > 50:  # Security limit
            raise ValueError(f"Too many scenarios: {len(scenarios)} > 50")
            
        logger.info(f"Starting scenario analysis for {len(scenarios)} scenarios")
        
        # Use sanitized parameters
        base_params = sanitized_base_params
        
        # Check cache first
        cache_key = self._get_cache_key(base_params, scenarios)
        with self._cache_lock:
            if cache_key in self._scenario_cache:
                cached_result = self._scenario_cache[cache_key]
                # Update access order for LRU
                self._cache_access_order.remove(cache_key)
                self._cache_access_order.append(cache_key)
                logger.info(f"Scenario analysis from cache in {time.time() - start_time:.3f}s")
                return cached_result
        
        # Ensure required parameters
        base_params = self._ensure_required_params(base_params)
        
        # Calculate base case first
        base_case_result = self._calculate_base_case(base_params)
        
        # Analyze all scenarios
        scenario_results = self._analyze_scenarios_parallel(base_params, scenarios)
        
        # Create comprehensive comparison
        comparison_results = self._create_scenario_comparison(
            base_case_result, scenario_results, scenarios
        )
        
        # Cache results with LRU management
        with self._cache_lock:
            # Implement LRU cache with size limit
            if len(self._scenario_cache) >= self._cache_max_size:
                # Remove oldest entry (LRU)
                if self._cache_access_order:
                    oldest_key = self._cache_access_order.pop(0)
                    self._scenario_cache.pop(oldest_key, None)
                    logger.debug(f"Evicted scenario cache entry: {oldest_key}")
            
            self._scenario_cache[cache_key] = comparison_results
            self._cache_access_order.append(cache_key)
        
        elapsed = time.time() - start_time
        logger.info(f"Scenario analysis completed in {elapsed:.3f}s for {len(scenarios)} scenarios")
        
        return comparison_results
    
    def create_economic_scenarios(
        self, 
        base_params: Dict[str, float]
    ) -> List[ScenarioDefinition]:
        """
        Create standard economic scenarios for analysis.
        
        Args:
            base_params: Base case parameters to create variations around
            
        Returns:
            List of standard economic scenario definitions
        """
        scenarios = []
        
        # Recession Scenario
        recession_params = {
            'interest_rate': base_params.get('interest_rate', 5.0) + 2.0,  # Higher rates
            'market_appreciation_rate': -1.0,  # Property values decline
            'rent_increase_rate': 1.0,  # Lower rent increases
            'cost_of_capital': base_params.get('cost_of_capital', 8.0) + 1.5,  # Higher discount rate
            'property_tax_escalation': 1.0,  # Lower tax increases
            'inflation_rate': 1.5  # Lower inflation
        }
        scenarios.append(ScenarioDefinition(
            name="Economic Recession",
            description="Economic downturn with higher interest rates, declining property values, and reduced growth",
            parameters=recession_params,
            probability=0.15
        ))
        
        # Growth Scenario
        growth_params = {
            'interest_rate': max(1.0, base_params.get('interest_rate', 5.0) - 1.0),  # Lower rates
            'market_appreciation_rate': base_params.get('market_appreciation_rate', 3.0) + 2.0,  # Higher appreciation
            'rent_increase_rate': base_params.get('rent_increase_rate', 3.0) + 1.5,  # Higher rent increases
            'cost_of_capital': max(4.0, base_params.get('cost_of_capital', 8.0) - 1.0),  # Lower discount rate
            'property_tax_escalation': 3.0,  # Higher tax increases
            'inflation_rate': 4.0  # Higher inflation
        }
        scenarios.append(ScenarioDefinition(
            name="Economic Growth",
            description="Strong economic growth with lower interest rates, rising property values, and inflation",
            parameters=growth_params,
            probability=0.35
        ))
        
        # High Interest Rate Scenario
        high_rate_params = {
            'interest_rate': base_params.get('interest_rate', 5.0) + 4.0,  # Much higher rates
            'market_appreciation_rate': base_params.get('market_appreciation_rate', 3.0) - 1.0,  # Slower appreciation
            'cost_of_capital': base_params.get('cost_of_capital', 8.0) + 2.0,  # Higher discount rate
        }
        scenarios.append(ScenarioDefinition(
            name="High Interest Rates",
            description="Period of elevated interest rates impacting financing costs",
            parameters=high_rate_params,
            probability=0.20
        ))
        
        # Property Boom Scenario
        boom_params = {
            'market_appreciation_rate': base_params.get('market_appreciation_rate', 3.0) + 4.0,  # Rapid appreciation
            'rent_increase_rate': base_params.get('rent_increase_rate', 3.0) + 2.0,  # Rapid rent increases
            'property_tax_escalation': 4.0,  # Higher tax increases
            'inflation_rate': 5.0  # High inflation
        }
        scenarios.append(ScenarioDefinition(
            name="Property Market Boom",
            description="Rapid property value and rent appreciation with high inflation",
            parameters=boom_params,
            probability=0.10
        ))
        
        # Stable Scenario (minimal changes from base)
        stable_params = {
            'interest_rate': base_params.get('interest_rate', 5.0),
            'market_appreciation_rate': base_params.get('market_appreciation_rate', 3.0),
            'rent_increase_rate': base_params.get('rent_increase_rate', 3.0),
            'inflation_rate': 2.5  # Stable, low inflation
        }
        scenarios.append(ScenarioDefinition(
            name="Economic Stability",
            description="Stable economic conditions with steady, predictable growth",
            parameters=stable_params,
            probability=0.20
        ))
        
        return scenarios
    
    def create_custom_scenario(
        self,
        name: str,
        description: str,
        parameter_variations: Dict[str, float],
        probability: Optional[float] = None
    ) -> ScenarioDefinition:
        """
        Create a custom scenario definition.
        
        Args:
            name: Scenario name
            description: Scenario description
            parameter_variations: Dictionary of parameter changes from base case
            probability: Optional probability weight for scenario
            
        Returns:
            ScenarioDefinition object
        """
        return ScenarioDefinition(
            name=name,
            description=description,
            parameters=parameter_variations,
            probability=probability
        )
    
    def analyze_scenario_sensitivity(
        self,
        base_params: Dict[str, float],
        scenario: ScenarioDefinition,
        sensitivity_parameters: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze sensitivity within a specific scenario.
        
        Args:
            base_params: Base case parameters
            scenario: Scenario to analyze
            sensitivity_parameters: Parameters to vary within the scenario
            
        Returns:
            Sensitivity analysis results within the scenario context
        """
        # Create scenario base parameters
        scenario_params = base_params.copy()
        scenario_params.update(scenario.parameters)
        
        # Run sensitivity analysis on specified parameters
        sensitivity_results = {}
        
        for param_name in sensitivity_parameters:
            if param_name in scenario_params:
                base_value = scenario_params[param_name]
                
                # Create test values around scenario parameter value
                test_values = [
                    base_value * 0.9,
                    base_value * 0.95,
                    base_value,
                    base_value * 1.05,
                    base_value * 1.1
                ]
                
                param_results = []
                for test_value in test_values:
                    test_params = scenario_params.copy()
                    test_params[param_name] = test_value
                    
                    try:
                        npv_result = calculate_npv_comparison(**test_params)
                        param_results.append({
                            'parameter_value': test_value,
                            'npv_difference': npv_result['npv_difference'],
                            'recommendation': npv_result['recommendation']
                        })
                    except Exception as e:
                        logger.error(f"Scenario sensitivity calculation failed for {param_name}={test_value}: {e}")
                
                sensitivity_results[param_name] = {
                    'test_values': test_values,
                    'results': param_results,
                    'base_value': base_value
                }
        
        return {
            'scenario_name': scenario.name,
            'sensitivity_results': sensitivity_results,
            'scenario_parameters': scenario.parameters
        }
    
    def rank_scenarios(
        self,
        scenario_results: List[Dict[str, Any]],
        ranking_criteria: str = 'npv_difference'
    ) -> List[Dict[str, Any]]:
        """
        Rank scenarios based on specified criteria.
        
        Args:
            scenario_results: List of scenario analysis results
            ranking_criteria: Criteria for ranking ('npv_difference', 'risk_adjusted', 'probability_weighted')
            
        Returns:
            Sorted list of scenarios with rankings
        """
        if ranking_criteria == 'npv_difference':
            # Rank by NPV difference (higher is better)
            ranked = sorted(scenario_results, 
                          key=lambda x: x.get('npv_difference', float('-inf')), 
                          reverse=True)
            
        elif ranking_criteria == 'risk_adjusted':
            # Rank by risk-adjusted returns (NPV / volatility proxy)
            ranked = []
            for result in scenario_results:
                npv = result.get('npv_difference', 0)
                # Use absolute NPV as volatility proxy (higher absolute values = higher risk)
                risk_adjustment = abs(npv) if npv != 0 else 1
                risk_adjusted_score = npv / risk_adjustment
                result['risk_adjusted_score'] = risk_adjusted_score
                ranked.append(result)
            
            ranked.sort(key=lambda x: x.get('risk_adjusted_score', float('-inf')), reverse=True)
            
        elif ranking_criteria == 'probability_weighted':
            # Rank by probability-weighted NPV
            ranked = []
            for result in scenario_results:
                npv = result.get('npv_difference', 0)
                probability = result.get('probability', 1.0)
                weighted_score = npv * probability
                result['probability_weighted_score'] = weighted_score
                ranked.append(result)
            
            ranked.sort(key=lambda x: x.get('probability_weighted_score', float('-inf')), reverse=True)
            
        else:
            ranked = scenario_results.copy()
        
        # Add ranking numbers
        for i, result in enumerate(ranked):
            result['rank'] = i + 1
            
        return ranked
    
    def calculate_expected_value(
        self,
        scenario_results: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate probability-weighted expected values across scenarios.
        
        Args:
            scenario_results: List of scenario analysis results with probabilities
            
        Returns:
            Dictionary with expected value calculations
        """
        total_probability = 0.0
        weighted_npv = 0.0
        weighted_ownership_npv = 0.0
        weighted_rental_npv = 0.0
        
        valid_scenarios = []
        
        for result in scenario_results:
            probability = result.get('probability', 0.0)
            if probability > 0:
                total_probability += probability
                weighted_npv += result.get('npv_difference', 0.0) * probability
                weighted_ownership_npv += result.get('ownership_npv', 0.0) * probability
                weighted_rental_npv += result.get('rental_npv', 0.0) * probability
                valid_scenarios.append(result)
        
        # Normalize probabilities if they don't sum to 1
        if total_probability > 0 and abs(total_probability - 1.0) > 0.01:
            normalization_factor = 1.0 / total_probability
            weighted_npv *= normalization_factor
            weighted_ownership_npv *= normalization_factor
            weighted_rental_npv *= normalization_factor
        
        # Calculate variance for risk metrics
        variance_npv = 0.0
        if len(valid_scenarios) > 1:
            for result in valid_scenarios:
                probability = result.get('probability', 0.0) / total_probability if total_probability > 0 else 0.0
                npv_diff = result.get('npv_difference', 0.0) - weighted_npv
                variance_npv += (npv_diff ** 2) * probability
        
        std_dev_npv = np.sqrt(variance_npv) if variance_npv > 0 else 0.0
        
        return {
            'expected_npv_difference': weighted_npv,
            'expected_ownership_npv': weighted_ownership_npv,
            'expected_rental_npv': weighted_rental_npv,
            'npv_standard_deviation': std_dev_npv,
            'total_probability': total_probability,
            'valid_scenarios': len(valid_scenarios),
            'sharpe_ratio': weighted_npv / std_dev_npv if std_dev_npv > 0 else 0.0
        }
    
    def _calculate_base_case(self, base_params: Dict[str, float]) -> Dict[str, Any]:
        """Calculate base case NPV analysis."""
        try:
            base_result = calculate_npv_comparison(**base_params)
            return {
                'scenario_name': 'Base Case',
                'npv_difference': base_result['npv_difference'],
                'ownership_npv': base_result['ownership_npv'],
                'rental_npv': base_result['rental_npv'],
                'recommendation': base_result['recommendation'],
                'confidence': base_result['confidence'],
                'calculation_successful': True,
                'parameters': {}
            }
        except Exception as e:
            logger.error(f"Base case calculation failed: {e}")
            return {
                'scenario_name': 'Base Case',
                'npv_difference': 0.0,
                'calculation_successful': False,
                'error_message': str(e),
                'parameters': {}
            }
    
    def _analyze_scenarios_parallel(
        self,
        base_params: Dict[str, float],
        scenarios: List[ScenarioDefinition]
    ) -> List[Dict[str, Any]]:
        """Analyze scenarios using parallel processing."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all scenario analyses
            future_to_scenario = {
                executor.submit(self._analyze_single_scenario, base_params, scenario): scenario
                for scenario in scenarios
            }
            
            # Collect results
            for future in as_completed(future_to_scenario, timeout=self.config.timeout_seconds):
                try:
                    result = future.result(timeout=1.0)  # Quick timeout per scenario
                    results.append(result)
                except Exception as e:
                    scenario = future_to_scenario[future]
                    logger.error(f"Scenario analysis failed for {scenario.name}: {e}")
                    
                    # Create error result
                    error_result = {
                        'scenario_name': scenario.name,
                        'npv_difference': 0.0,
                        'calculation_successful': False,
                        'error_message': str(e),
                        'parameters': scenario.parameters,
                        'probability': scenario.probability
                    }
                    results.append(error_result)
        
        return results
    
    def _analyze_single_scenario(
        self,
        base_params: Dict[str, float],
        scenario: ScenarioDefinition
    ) -> Dict[str, Any]:
        """Analyze a single scenario."""
        # Create scenario parameters
        scenario_params = base_params.copy()
        scenario_params.update(scenario.parameters)
        
        try:
            # Calculate NPV for scenario
            npv_result = calculate_npv_comparison(**scenario_params)
            
            return {
                'scenario_name': scenario.name,
                'description': scenario.description,
                'npv_difference': npv_result['npv_difference'],
                'ownership_npv': npv_result['ownership_npv'],
                'rental_npv': npv_result['rental_npv'],
                'recommendation': npv_result['recommendation'],
                'confidence': npv_result['confidence'],
                'calculation_successful': True,
                'parameters': scenario.parameters,
                'probability': scenario.probability
            }
            
        except Exception as e:
            logger.error(f"Scenario calculation failed for {scenario.name}: {e}")
            return {
                'scenario_name': scenario.name,
                'description': scenario.description,
                'npv_difference': 0.0,
                'calculation_successful': False,
                'error_message': str(e),
                'parameters': scenario.parameters,
                'probability': scenario.probability
            }
    
    def _create_scenario_comparison(
        self,
        base_case: Dict[str, Any],
        scenario_results: List[Dict[str, Any]],
        scenarios: List[ScenarioDefinition]
    ) -> List[Dict[str, Any]]:
        """Create comprehensive scenario comparison."""
        all_results = [base_case] + scenario_results
        
        # Add comparison metrics
        base_npv = base_case.get('npv_difference', 0.0)
        
        for result in all_results:
            if result['scenario_name'] != 'Base Case':
                scenario_npv = result.get('npv_difference', 0.0)
                result['vs_base_case'] = scenario_npv - base_npv
                result['vs_base_case_pct'] = ((scenario_npv - base_npv) / abs(base_npv) * 100) if base_npv != 0 else 0.0
            else:
                result['vs_base_case'] = 0.0
                result['vs_base_case_pct'] = 0.0
        
        # Calculate summary statistics
        successful_scenarios = [r for r in scenario_results if r.get('calculation_successful', False)]
        
        if successful_scenarios:
            npv_values = [r['npv_difference'] for r in successful_scenarios]
            
            summary_stats = {
                'scenario_name': 'Summary Statistics',
                'min_npv': min(npv_values),
                'max_npv': max(npv_values),
                'mean_npv': np.mean(npv_values),
                'std_npv': np.std(npv_values),
                'scenarios_analyzed': len(successful_scenarios),
                'scenarios_favor_buy': sum(1 for r in successful_scenarios if r.get('npv_difference', 0) > 0),
                'scenarios_favor_rent': sum(1 for r in successful_scenarios if r.get('npv_difference', 0) < 0)
            }
            
            all_results.append(summary_stats)
        
        return all_results
    
    def _get_cache_key(
        self,
        base_params: Dict[str, float],
        scenarios: List[ScenarioDefinition]
    ) -> str:
        """Generate cache key for scenario analysis parameters."""
        import hashlib
        
        # Sort parameters for consistent key
        param_str = ','.join(f"{k}:{v}" for k, v in sorted(base_params.items()))
        
        # Sort scenarios for consistent key
        scenario_items = []
        for scenario in sorted(scenarios, key=lambda s: s.name):
            scenario_params = sorted(scenario.parameters.items()) if scenario.parameters else []
            param_part = ','.join(f"{k}:{v}" for k, v in scenario_params)
            prob_part = f":{scenario.probability}" if scenario.probability is not None else ""
            scenario_str = f"{scenario.name}|{param_part}{prob_part}"
            scenario_items.append(scenario_str)
        scenarios_str = '#'.join(scenario_items)
        
        # Create hash of all parameters + scenarios (using SHA-256 for security)
        full_str = f"{param_str}#{scenarios_str}"
        return hashlib.sha256(full_str.encode()).hexdigest()
    
    def _ensure_required_params(self, base_params: Dict[str, float]) -> Dict[str, float]:
        """Ensure all required parameters are present with defaults."""
        required_defaults = {
            'loan_term': 20,
            'analysis_period': 25,
            'transaction_costs': base_params.get('purchase_price', 500000) * 0.05,
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
            'moving_costs': 0.0,
            'space_improvement_cost': 0.0
        }
        
        complete_params = base_params.copy()
        for key, default_value in required_defaults.items():
            if key not in complete_params:
                complete_params[key] = default_value
                
        return complete_params
    
    # Interface methods (implement required abstract methods)
    
    def run_sensitivity_analysis(
        self, 
        base_params: Dict[str, float],
        variables: List
    ) -> List:
        """Run sensitivity analysis (delegated to sensitivity analysis engine)."""
        logger.info("Sensitivity analysis delegated to SensitivityAnalysisEngine")
        return []
    
    def run_monte_carlo(
        self,
        base_params: Dict[str, float],
        variable_distributions: Dict[str, Dict],
        iterations: int = 10000
    ):
        """Run Monte Carlo simulation (delegated to Monte Carlo engine)."""
        logger.info("Monte Carlo analysis delegated to MonteCarloEngine")
        return None
    
    def assess_risk(
        self,
        analysis_params: Dict[str, float],
        market_data
    ) -> RiskAssessment:
        """Assess investment risk (delegated to risk assessment engine)."""
        logger.info("Risk assessment delegated to RiskAssessmentEngine")
        return RiskAssessment(
            overall_risk_level=RiskLevel.MEDIUM,
            risk_factors={},
            risk_description="Risk assessment not available in scenario modeling",
            mitigation_suggestions=[],
            confidence_score=0.0
        )


# Utility functions

def run_quick_scenario_analysis(
    base_params: Dict[str, float],
    include_economic_scenarios: bool = True,
    custom_scenarios: Optional[List[ScenarioDefinition]] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function for quick scenario analysis.
    
    Args:
        base_params: Base case parameters
        include_economic_scenarios: Whether to include standard economic scenarios
        custom_scenarios: Optional custom scenarios to include
        
    Returns:
        List of scenario analysis results
    """
    engine = ScenarioModelingEngine()
    
    scenarios = []
    
    if include_economic_scenarios:
        scenarios.extend(engine.create_economic_scenarios(base_params))
    
    if custom_scenarios:
        scenarios.extend(custom_scenarios)
    
    if not scenarios:
        # Create at least basic scenarios
        scenarios = engine.create_economic_scenarios(base_params)[:3]  # Top 3 scenarios
    
    return engine.run_scenario_analysis(base_params, scenarios)


if __name__ == "__main__":
    # Test scenario modeling
    print("Testing Scenario Modeling Engine...")
    
    # Test parameters
    test_params = {
        'purchase_price': 500000,
        'current_annual_rent': 24000,
        'down_payment_pct': 30.0,
        'interest_rate': 5.0,
        'market_appreciation_rate': 3.0,
        'rent_increase_rate': 3.0,
        'cost_of_capital': 8.0
    }
    
    # Run scenario analysis
    start_time = time.time()
    engine = ScenarioModelingEngine()
    
    # Create economic scenarios
    scenarios = engine.create_economic_scenarios(test_params)
    print(f"✅ Created {len(scenarios)} economic scenarios")
    
    # Run analysis
    results = engine.run_scenario_analysis(test_params, scenarios)
    elapsed = time.time() - start_time
    
    print(f"✅ Analysis completed in {elapsed:.3f}s")
    print(f"✅ Scenarios analyzed: {len([r for r in results if r.get('calculation_successful', False)])}")
    
    # Show results summary
    successful_results = [r for r in results if r.get('calculation_successful', False) and 'vs_base_case' in r]
    if successful_results:
        ranked = engine.rank_scenarios(successful_results)
        print(f"✅ Best scenario: {ranked[0].get('scenario_name', 'Unknown')}")
        print(f"✅ NPV difference: ${ranked[0].get('npv_difference', 0):,.0f}")
    
    # Calculate expected value
    prob_results = [r for r in results if r.get('probability') is not None and r.get('calculation_successful', False)]
    if prob_results:
        expected_value = engine.calculate_expected_value(prob_results)
        print(f"✅ Expected NPV: ${expected_value.get('expected_npv_difference', 0):,.0f}")
        print(f"✅ NPV Std Dev: ${expected_value.get('npv_standard_deviation', 0):,.0f}")