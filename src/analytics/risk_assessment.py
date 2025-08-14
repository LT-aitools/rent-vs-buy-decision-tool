"""
Risk Assessment Engine - Week 4 Analytics Component

Advanced risk assessment and analysis engine for investment decision support.
Implements the AnalyticsEngine interface for risk assessment requirements.

Features:
- Multi-dimensional risk factor analysis
- Market risk integration and assessment
- Financial risk metrics and calculations
- Risk scoring and classification
- Risk mitigation recommendations
- Confidence scoring and uncertainty quantification

Performance Target: Fast risk assessment and scoring
Accuracy Target: 95%+ accuracy in risk classification and scoring
"""

import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import threading
import math

from shared.interfaces import (
    AnalyticsEngine, RiskAssessment, RiskLevel, MarketData,
    MonteCarloResult, AnalyticsResult
)
from calculations.npv_analysis import calculate_npv_comparison
from analytics.input_validation import validate_and_sanitize_base_params, ValidationError, SecurityError

logger = logging.getLogger(__name__)


class RiskCategory(Enum):
    """Risk assessment categories"""
    MARKET_RISK = "market_risk"
    FINANCIAL_RISK = "financial_risk"
    LIQUIDITY_RISK = "liquidity_risk"
    INTEREST_RATE_RISK = "interest_rate_risk"
    OPERATIONAL_RISK = "operational_risk"
    REGULATORY_RISK = "regulatory_risk"
    CONCENTRATION_RISK = "concentration_risk"


@dataclass
class RiskFactor:
    """Individual risk factor definition"""
    name: str
    category: RiskCategory
    weight: float
    current_value: float
    risk_threshold_low: float
    risk_threshold_high: float
    description: str


@dataclass
class RiskConfig:
    """Configuration for risk assessment"""
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    confidence_threshold: float = 0.75
    max_acceptable_risk_score: float = 0.7
    market_data_freshness_hours: float = 24.0
    monte_carlo_integration: bool = True
    
    # Risk factor weights (sum should equal 1.0)
    market_risk_weight: float = 0.25
    financial_risk_weight: float = 0.30
    liquidity_risk_weight: float = 0.15
    interest_rate_risk_weight: float = 0.20
    operational_risk_weight: float = 0.10


class RiskAssessmentEngine(AnalyticsEngine):
    """
    Advanced risk assessment engine implementing AnalyticsEngine interface.
    
    Provides comprehensive risk analysis, scoring, and mitigation recommendations.
    """
    
    def __init__(self, config: Optional[RiskConfig] = None):
        self.config = config or RiskConfig()
        # LRU cache with size limit to prevent memory leaks
        self._risk_cache = {}
        self._cache_lock = threading.Lock()
        self._cache_max_size = 100  # Maximum cached risk assessments
        self._cache_access_order = []  # Track access order for LRU
        
    def assess_risk(
        self,
        analysis_params: Dict[str, float],
        market_data: MarketData
    ) -> RiskAssessment:
        """
        Perform comprehensive risk assessment for investment decision.
        
        Args:
            analysis_params: Analysis parameters including NPV inputs
            market_data: Current market data for risk context
            
        Returns:
            RiskAssessment with detailed risk analysis and recommendations
        """
        start_time = time.time()
        
        # Validate and sanitize inputs
        try:
            sanitized_params = validate_and_sanitize_base_params(analysis_params)
        except (ValidationError, SecurityError) as e:
            logger.error(f"Input validation failed: {e}")
            raise ValueError(f"Invalid input parameters: {e}")
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            raise ValueError(f"Parameter validation failed: {e}")
        
        if not market_data:
            raise ValueError("Market data cannot be empty")
        
        # Check cache first
        cache_key = self._get_cache_key(sanitized_params, market_data)
        with self._cache_lock:
            if cache_key in self._risk_cache:
                cached_result = self._risk_cache[cache_key]
                # Update access order for LRU
                self._cache_access_order.remove(cache_key)
                self._cache_access_order.append(cache_key)
                logger.info(f"Risk assessment from cache in {time.time() - start_time:.3f}s")
                return cached_result
            
        logger.info("Starting comprehensive risk assessment")
        
        # Use sanitized parameters
        analysis_params = sanitized_params
        
        # Calculate individual risk factors
        risk_factors = self._calculate_risk_factors(analysis_params, market_data)
        
        # Calculate overall risk score
        overall_risk_score = self._calculate_overall_risk_score(risk_factors)
        
        # Determine risk level
        overall_risk_level = self._determine_risk_level(overall_risk_score)
        
        # Generate risk description
        risk_description = self._generate_risk_description(
            overall_risk_level, risk_factors, overall_risk_score
        )
        
        # Generate mitigation suggestions
        mitigation_suggestions = self._generate_mitigation_suggestions(
            risk_factors, overall_risk_level, analysis_params
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            market_data, risk_factors, analysis_params
        )
        
        # Create risk assessment result
        risk_result = RiskAssessment(
            overall_risk_level=overall_risk_level,
            risk_factors=risk_factors,
            risk_description=risk_description,
            mitigation_suggestions=mitigation_suggestions,
            confidence_score=confidence_score
        )
        
        # Cache results with LRU management
        with self._cache_lock:
            # Implement LRU cache with size limit
            if len(self._risk_cache) >= self._cache_max_size:
                # Remove oldest entry (LRU)
                if self._cache_access_order:
                    oldest_key = self._cache_access_order.pop(0)
                    self._risk_cache.pop(oldest_key, None)
                    logger.debug(f"Evicted risk cache entry: {oldest_key}")
            
            self._risk_cache[cache_key] = risk_result
            self._cache_access_order.append(cache_key)
        
        elapsed = time.time() - start_time
        logger.info(f"Risk assessment completed in {elapsed:.3f}s")
        
        return risk_result
    
    def _calculate_risk_factors(
        self,
        analysis_params: Dict[str, float],
        market_data: MarketData
    ) -> Dict[str, float]:
        """Calculate individual risk factor scores (0-1 scale)."""
        risk_factors = {}
        
        # Market Risk Assessment
        market_risk = self._assess_market_risk(analysis_params, market_data)
        risk_factors.update(market_risk)
        
        # Financial Risk Assessment
        financial_risk = self._assess_financial_risk(analysis_params)
        risk_factors.update(financial_risk)
        
        # Liquidity Risk Assessment
        liquidity_risk = self._assess_liquidity_risk(analysis_params, market_data)
        risk_factors.update(liquidity_risk)
        
        # Interest Rate Risk Assessment
        interest_rate_risk = self._assess_interest_rate_risk(analysis_params, market_data)
        risk_factors.update(interest_rate_risk)
        
        # Operational Risk Assessment
        operational_risk = self._assess_operational_risk(analysis_params)
        risk_factors.update(operational_risk)
        
        return risk_factors
    
    def _assess_market_risk(
        self,
        analysis_params: Dict[str, float],
        market_data: MarketData
    ) -> Dict[str, float]:
        """Assess market-related risk factors."""
        market_risks = {}
        
        # Property Market Volatility Risk
        appreciation_rate = market_data.property_appreciation_rate
        if appreciation_rate < 0:
            volatility_risk = 0.9  # High risk for negative appreciation
        elif appreciation_rate < 2:
            volatility_risk = 0.6  # Medium risk for low appreciation
        elif appreciation_rate > 8:
            volatility_risk = 0.7  # High risk for unsustainable appreciation
        else:
            volatility_risk = 0.3  # Lower risk for moderate appreciation
        
        market_risks['property_market_volatility'] = volatility_risk
        
        # Rental Market Risk
        vacancy_rate = market_data.rental_vacancy_rate
        rental_growth = market_data.rental_growth_rate
        
        if vacancy_rate > 10:
            rental_market_risk = 0.8
        elif vacancy_rate > 5:
            rental_market_risk = 0.5
        else:
            rental_market_risk = 0.2
            
        # Adjust for rental growth
        if rental_growth < 1:
            rental_market_risk = min(1.0, rental_market_risk + 0.2)
        elif rental_growth > 6:
            rental_market_risk = min(1.0, rental_market_risk + 0.1)
            
        market_risks['rental_market_risk'] = rental_market_risk
        
        # Economic Environment Risk
        unemployment = market_data.unemployment_rate
        population_growth = market_data.population_growth_rate
        
        if unemployment > 8:
            economic_risk = 0.8
        elif unemployment > 5:
            economic_risk = 0.5
        else:
            economic_risk = 0.2
            
        # Adjust for population growth
        if population_growth < 0:
            economic_risk = min(1.0, economic_risk + 0.3)
        elif population_growth < 1:
            economic_risk = min(1.0, economic_risk + 0.1)
            
        market_risks['economic_environment_risk'] = economic_risk
        
        return market_risks
    
    def _assess_financial_risk(self, analysis_params: Dict[str, float]) -> Dict[str, float]:
        """Assess financial and leverage-related risk factors."""
        financial_risks = {}
        
        # Leverage Risk (Loan-to-Value)
        purchase_price = analysis_params.get('purchase_price', 500000)
        down_payment_pct = analysis_params.get('down_payment_pct', 30)
        loan_to_value = 100 - down_payment_pct
        
        if loan_to_value > 90:
            leverage_risk = 0.9
        elif loan_to_value > 80:
            leverage_risk = 0.7
        elif loan_to_value > 70:
            leverage_risk = 0.5
        else:
            leverage_risk = 0.3
            
        financial_risks['leverage_risk'] = leverage_risk
        
        # Cash Flow Risk
        annual_rent = analysis_params.get('current_annual_rent', 24000)
        cost_of_capital = analysis_params.get('cost_of_capital', 8.0)
        
        # Calculate affordability ratio
        affordability_ratio = annual_rent / (purchase_price * cost_of_capital / 100)
        
        if affordability_ratio < 0.8:
            cash_flow_risk = 0.8
        elif affordability_ratio < 1.0:
            cash_flow_risk = 0.6
        elif affordability_ratio < 1.2:
            cash_flow_risk = 0.4
        else:
            cash_flow_risk = 0.2
            
        financial_risks['cash_flow_risk'] = cash_flow_risk
        
        # Interest Rate Sensitivity
        interest_rate = analysis_params.get('interest_rate', 5.0)
        loan_term = analysis_params.get('loan_term', 20)
        
        # Higher rates and longer terms = higher sensitivity
        if interest_rate > 8 and loan_term > 25:
            rate_sensitivity = 0.8
        elif interest_rate > 6 or loan_term > 20:
            rate_sensitivity = 0.5
        else:
            rate_sensitivity = 0.3
            
        financial_risks['interest_rate_sensitivity'] = rate_sensitivity
        
        return financial_risks
    
    def _assess_liquidity_risk(
        self,
        analysis_params: Dict[str, float],
        market_data: MarketData
    ) -> Dict[str, float]:
        """Assess liquidity-related risk factors."""
        liquidity_risks = {}
        
        # Market Liquidity Risk
        months_on_market = market_data.months_on_market
        
        if months_on_market > 6:
            market_liquidity_risk = 0.8
        elif months_on_market > 3:
            market_liquidity_risk = 0.5
        else:
            market_liquidity_risk = 0.2
            
        liquidity_risks['market_liquidity_risk'] = market_liquidity_risk
        
        # Investment Size Risk (harder to sell expensive properties)
        purchase_price = analysis_params.get('purchase_price', 500000)
        median_price = market_data.median_property_price
        
        if purchase_price > median_price * 2:
            size_liquidity_risk = 0.7
        elif purchase_price > median_price * 1.5:
            size_liquidity_risk = 0.5
        else:
            size_liquidity_risk = 0.3
            
        liquidity_risks['investment_size_risk'] = size_liquidity_risk
        
        # Holding Period Risk
        analysis_period = analysis_params.get('analysis_period', 25)
        
        if analysis_period < 5:
            holding_period_risk = 0.8  # High risk for short holding periods
        elif analysis_period < 10:
            holding_period_risk = 0.5
        else:
            holding_period_risk = 0.2
            
        liquidity_risks['holding_period_risk'] = holding_period_risk
        
        return liquidity_risks
    
    def _assess_interest_rate_risk(
        self,
        analysis_params: Dict[str, float],
        market_data: MarketData
    ) -> Dict[str, float]:
        """Assess interest rate related risk factors."""
        rate_risks = {}
        
        # Rate Level Risk
        current_rates = market_data.current_mortgage_rates
        rate_30_year = current_rates.get('30_year_fixed', 6.5)
        
        if rate_30_year > 8:
            rate_level_risk = 0.8
        elif rate_30_year > 6:
            rate_level_risk = 0.5
        else:
            rate_level_risk = 0.3
            
        rate_risks['rate_level_risk'] = rate_level_risk
        
        # Rate Trend Risk
        rate_trend = market_data.rate_trend
        
        if rate_trend == "rising":
            trend_risk = 0.7
        elif rate_trend == "falling":
            trend_risk = 0.3
        else:  # stable
            trend_risk = 0.4
            
        rate_risks['rate_trend_risk'] = trend_risk
        
        # Refinancing Risk
        loan_term = analysis_params.get('loan_term', 20)
        analysis_period = analysis_params.get('analysis_period', 25)
        
        if analysis_period > loan_term:
            # Will need refinancing
            refinancing_risk = 0.6
        else:
            refinancing_risk = 0.2
            
        rate_risks['refinancing_risk'] = refinancing_risk
        
        return rate_risks
    
    def _assess_operational_risk(self, analysis_params: Dict[str, float]) -> Dict[str, float]:
        """Assess operational and management-related risk factors."""
        operational_risks = {}
        
        # Maintenance and Capital Expenditure Risk
        annual_maintenance = analysis_params.get('annual_maintenance', 10000)
        purchase_price = analysis_params.get('purchase_price', 500000)
        maintenance_ratio = annual_maintenance / purchase_price
        
        if maintenance_ratio > 0.03:  # >3% of property value
            maintenance_risk = 0.7
        elif maintenance_ratio > 0.02:  # >2% of property value
            maintenance_risk = 0.5
        else:
            maintenance_risk = 0.3
            
        operational_risks['maintenance_risk'] = maintenance_risk
        
        # Property Management Risk
        property_management = analysis_params.get('property_management', 0.0)
        
        if property_management == 0:
            # Self-management has higher operational risk
            management_risk = 0.6
        else:
            # Professional management reduces risk
            management_risk = 0.3
            
        operational_risks['property_management_risk'] = management_risk
        
        # Obsolescence Risk
        obsolescence_rate = analysis_params.get('obsolescence_risk_rate', 0.5)
        
        if obsolescence_rate > 1.0:
            obsolescence_risk = 0.7
        elif obsolescence_rate > 0.5:
            obsolescence_risk = 0.5
        else:
            obsolescence_risk = 0.3
            
        operational_risks['obsolescence_risk'] = obsolescence_risk
        
        return operational_risks
    
    def _calculate_overall_risk_score(self, risk_factors: Dict[str, float]) -> float:
        """Calculate weighted overall risk score."""
        
        # Group risk factors by category
        market_factors = [
            'property_market_volatility', 'rental_market_risk', 'economic_environment_risk'
        ]
        financial_factors = [
            'leverage_risk', 'cash_flow_risk', 'interest_rate_sensitivity'
        ]
        liquidity_factors = [
            'market_liquidity_risk', 'investment_size_risk', 'holding_period_risk'
        ]
        rate_factors = [
            'rate_level_risk', 'rate_trend_risk', 'refinancing_risk'
        ]
        operational_factors = [
            'maintenance_risk', 'property_management_risk', 'obsolescence_risk'
        ]
        
        # Calculate category scores
        market_score = np.mean([risk_factors.get(f, 0.5) for f in market_factors])
        financial_score = np.mean([risk_factors.get(f, 0.5) for f in financial_factors])
        liquidity_score = np.mean([risk_factors.get(f, 0.5) for f in liquidity_factors])
        rate_score = np.mean([risk_factors.get(f, 0.5) for f in rate_factors])
        operational_score = np.mean([risk_factors.get(f, 0.5) for f in operational_factors])
        
        # Calculate weighted overall score
        overall_score = (
            market_score * self.config.market_risk_weight +
            financial_score * self.config.financial_risk_weight +
            liquidity_score * self.config.liquidity_risk_weight +
            rate_score * self.config.interest_rate_risk_weight +
            operational_score * self.config.operational_risk_weight
        )
        
        return min(1.0, max(0.0, overall_score))
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on overall risk score."""
        if risk_score >= 0.75:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.60:
            return RiskLevel.HIGH
        elif risk_score >= 0.40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_risk_description(
        self,
        risk_level: RiskLevel,
        risk_factors: Dict[str, float],
        overall_score: float
    ) -> str:
        """Generate human-readable risk description."""
        
        # Find top risk factors
        top_risks = sorted(risk_factors.items(), key=lambda x: x[1], reverse=True)[:3]
        
        risk_names = {
            'property_market_volatility': 'property market volatility',
            'rental_market_risk': 'rental market conditions',
            'economic_environment_risk': 'economic environment',
            'leverage_risk': 'high leverage/debt levels',
            'cash_flow_risk': 'cash flow sustainability',
            'interest_rate_sensitivity': 'interest rate sensitivity',
            'market_liquidity_risk': 'market liquidity constraints',
            'investment_size_risk': 'investment size/marketability',
            'holding_period_risk': 'short holding period',
            'rate_level_risk': 'current interest rate levels',
            'rate_trend_risk': 'interest rate trends',
            'refinancing_risk': 'refinancing requirements',
            'maintenance_risk': 'maintenance and repair costs',
            'property_management_risk': 'property management complexity',
            'obsolescence_risk': 'property obsolescence'
        }
        
        base_descriptions = {
            RiskLevel.LOW: "This investment presents relatively low risk",
            RiskLevel.MEDIUM: "This investment carries moderate risk",
            RiskLevel.HIGH: "This investment involves significant risk",
            RiskLevel.CRITICAL: "This investment presents very high risk"
        }
        
        description = base_descriptions[risk_level]
        
        if top_risks:
            top_risk_names = [risk_names.get(risk[0], risk[0]) for risk in top_risks if risk[1] > 0.5]
            if top_risk_names:
                if len(top_risk_names) == 1:
                    description += f", primarily due to {top_risk_names[0]}."
                elif len(top_risk_names) == 2:
                    description += f", primarily due to {top_risk_names[0]} and {top_risk_names[1]}."
                else:
                    description += f", primarily due to {', '.join(top_risk_names[:-1])}, and {top_risk_names[-1]}."
            else:
                description += "."
        else:
            description += "."
            
        description += f" Overall risk score: {overall_score:.2f}/1.00."
        
        return description
    
    def _generate_mitigation_suggestions(
        self,
        risk_factors: Dict[str, float],
        risk_level: RiskLevel,
        analysis_params: Dict[str, float]
    ) -> List[str]:
        """Generate risk mitigation recommendations."""
        suggestions = []
        
        # High-risk factors requiring mitigation
        high_risk_threshold = 0.6
        
        for risk_factor, score in risk_factors.items():
            if score >= high_risk_threshold:
                if risk_factor == 'leverage_risk':
                    suggestions.append("Consider increasing down payment to reduce leverage risk")
                elif risk_factor == 'cash_flow_risk':
                    suggestions.append("Ensure adequate cash reserves for negative cash flow periods")
                elif risk_factor == 'market_liquidity_risk':
                    suggestions.append("Consider more liquid investment alternatives or longer holding periods")
                elif risk_factor == 'interest_rate_sensitivity':
                    suggestions.append("Consider fixed-rate financing or interest rate hedging strategies")
                elif risk_factor == 'property_market_volatility':
                    suggestions.append("Diversify across different property types or geographic markets")
                elif risk_factor == 'rental_market_risk':
                    suggestions.append("Research local rental demand trends and consider multi-unit properties")
                elif risk_factor == 'maintenance_risk':
                    suggestions.append("Budget additional reserves for maintenance and conduct thorough property inspection")
                elif risk_factor == 'property_management_risk':
                    suggestions.append("Consider professional property management services")
                elif risk_factor == 'refinancing_risk':
                    suggestions.append("Plan for potential refinancing costs and rate changes")
        
        # General suggestions based on overall risk level
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            suggestions.append("Consider postponing the investment until market conditions improve")
            suggestions.append("Seek professional real estate investment advice")
            suggestions.append("Analyze alternative investment options with better risk-return profiles")
        elif risk_level == RiskLevel.MEDIUM:
            suggestions.append("Monitor market conditions closely throughout the holding period")
            suggestions.append("Maintain adequate liquidity reserves for unexpected expenses")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:8]  # Limit to top 8 suggestions
    
    def _calculate_confidence_score(
        self,
        market_data: MarketData,
        risk_factors: Dict[str, float],
        analysis_params: Dict[str, float]
    ) -> float:
        """Calculate confidence score for the risk assessment."""
        
        # Data quality factors
        data_quality_score = market_data.confidence_score
        data_freshness = market_data.freshness_hours
        
        # Adjust for data freshness
        if data_freshness > 48:
            freshness_penalty = 0.2
        elif data_freshness > 24:
            freshness_penalty = 0.1
        else:
            freshness_penalty = 0.0
            
        data_score = max(0.0, data_quality_score - freshness_penalty)
        
        # Analysis completeness score
        required_params = [
            'purchase_price', 'current_annual_rent', 'down_payment_pct',
            'interest_rate', 'market_appreciation_rate', 'rent_increase_rate',
            'cost_of_capital', 'analysis_period'
        ]
        
        present_params = sum(1 for param in required_params if param in analysis_params)
        completeness_score = present_params / len(required_params)
        
        # Risk factor coverage score
        total_risk_factors = 15  # Expected number of risk factors
        calculated_factors = len([f for f in risk_factors.values() if f > 0])
        coverage_score = calculated_factors / total_risk_factors
        
        # Combined confidence score
        confidence = (data_score * 0.4 + completeness_score * 0.3 + coverage_score * 0.3)
        
        return min(1.0, max(0.1, confidence))  # Bound between 0.1 and 1.0
    
    def _get_cache_key(
        self,
        analysis_params: Dict[str, float],
        market_data: MarketData
    ) -> str:
        """Generate cache key for risk assessment parameters."""
        import hashlib
        
        # Sort parameters for consistent key
        param_str = ','.join(f"{k}:{v}" for k, v in sorted(analysis_params.items()))
        
        # Extract key market data fields for cache key
        market_fields = [
            f"location:{market_data.location}",
            f"rent_psqm:{market_data.median_rent_per_sqm}",
            f"prop_price:{market_data.median_property_price}",
            f"vacancy:{market_data.rental_vacancy_rate}",
            f"appreciation:{market_data.property_appreciation_rate}",
            f"unemployment:{market_data.unemployment_rate}",
            f"months_market:{market_data.months_on_market}",
            f"confidence:{market_data.confidence_score}",
            f"freshness:{market_data.freshness_hours}"
        ]
        market_str = '|'.join(market_fields)
        
        # Create hash of all parameters + market data (using SHA-256 for security)
        full_str = f"{param_str}#{market_str}"
        return hashlib.sha256(full_str.encode()).hexdigest()
    
    # Interface methods (implement required abstract methods)
    
    def run_sensitivity_analysis(
        self, 
        base_params: Dict[str, float],
        variables: List
    ) -> List:
        """Run sensitivity analysis (delegated to sensitivity analysis engine)."""
        logger.info("Sensitivity analysis delegated to SensitivityAnalysisEngine")
        return []
    
    def run_scenario_analysis(
        self,
        base_params: Dict[str, float],
        scenarios: List
    ) -> List[Dict[str, Any]]:
        """Run scenario analysis (delegated to scenario modeling engine)."""
        logger.info("Scenario analysis delegated to ScenarioModelingEngine")
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


# Utility functions

def create_mock_market_data_for_risk_assessment(location: str = "Test City") -> MarketData:
    """Create realistic mock market data for risk assessment testing."""
    from datetime import datetime
    from ..shared.interfaces import MarketData
    
    return MarketData(
        location=location,
        zip_code="12345",
        median_rent_per_sqm=25.0,
        rental_vacancy_rate=6.5,
        rental_growth_rate=2.8,
        median_property_price=485000.0,
        property_appreciation_rate=3.2,
        months_on_market=2.8,
        current_mortgage_rates={"30_year_fixed": 6.8, "15_year_fixed": 6.3},
        rate_trend="rising",
        local_inflation_rate=3.1,
        unemployment_rate=4.2,
        population_growth_rate=1.4,
        data_timestamp=datetime.now(),
        data_sources=["test_api", "market_research"],
        confidence_score=0.85,
        freshness_hours=2.5
    )


def run_quick_risk_assessment(
    analysis_params: Dict[str, float],
    market_data: Optional[MarketData] = None
) -> RiskAssessment:
    """
    Convenience function for quick risk assessment.
    
    Args:
        analysis_params: Analysis parameters for risk assessment
        market_data: Market data (creates mock data if None)
        
    Returns:
        RiskAssessment with comprehensive risk analysis
    """
    engine = RiskAssessmentEngine()
    
    if market_data is None:
        market_data = create_mock_market_data_for_risk_assessment()
    
    return engine.assess_risk(analysis_params, market_data)


if __name__ == "__main__":
    # Test risk assessment
    print("Testing Risk Assessment Engine...")
    
    # Test parameters
    test_params = {
        'purchase_price': 500000,
        'current_annual_rent': 24000,
        'down_payment_pct': 20.0,  # Higher leverage for testing
        'interest_rate': 7.0,
        'market_appreciation_rate': 2.5,
        'rent_increase_rate': 3.0,
        'cost_of_capital': 9.0,
        'analysis_period': 20,
        'annual_maintenance': 15000,  # Higher maintenance for testing
        'property_management': 0.0  # Self-management for testing
    }
    
    # Create test market data
    test_market_data = create_mock_market_data_for_risk_assessment()
    test_market_data.rental_vacancy_rate = 8.5  # Higher vacancy for testing
    test_market_data.months_on_market = 4.2  # Longer time on market
    
    # Run risk assessment
    start_time = time.time()
    engine = RiskAssessmentEngine()
    risk_result = engine.assess_risk(test_params, test_market_data)
    elapsed = time.time() - start_time
    
    print(f"✅ Risk assessment completed in {elapsed:.3f}s")
    print(f"✅ Overall risk level: {risk_result.overall_risk_level.value.upper()}")
    print(f"✅ Confidence score: {risk_result.confidence_score:.2f}")
    print(f"✅ Risk factors identified: {len(risk_result.risk_factors)}")
    print(f"✅ Mitigation suggestions: {len(risk_result.mitigation_suggestions)}")
    
    # Show top risk factors
    top_risks = sorted(risk_result.risk_factors.items(), key=lambda x: x[1], reverse=True)[:3]
    print("\nTop Risk Factors:")
    for risk_name, risk_score in top_risks:
        print(f"  {risk_name}: {risk_score:.2f}")
    
    print(f"\nRisk Description: {risk_result.risk_description}")