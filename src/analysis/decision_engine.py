"""
Decision Engine
Advanced buy vs rent recommendation logic with confidence levels and risk assessment

This module provides:
- Executive decision recommendations based on NPV analysis
- Multi-factor confidence level calculations
- Risk assessment and scenario analysis
- Clear decision reasoning and justification
- Business-focused executive summaries

All decision logic follows the Business PRD specifications exactly.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class DecisionRecommendation(Enum):
    """Decision recommendation types"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    MARGINAL_BUY = "MARGINAL_BUY"
    NEUTRAL = "NEUTRAL"
    MARGINAL_RENT = "MARGINAL_RENT"
    RENT = "RENT"
    STRONG_RENT = "STRONG_RENT"
    ERROR = "ERROR"


class ConfidenceLevel(Enum):
    """Confidence level classifications"""
    VERY_HIGH = "Very High"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    VERY_LOW = "Very Low"


class DecisionEngine:
    """
    Advanced Decision Engine for Real Estate Investment Analysis
    
    Provides sophisticated decision-making logic that goes beyond simple NPV
    comparison to include risk factors, market conditions, and business context.
    """
    
    def __init__(self):
        """Initialize the Decision Engine"""
        self.decision_history = []
        self.risk_factors = []
        
    def calculate_decision_recommendation(
        self, 
        npv_results: Dict[str, Any],
        risk_tolerance: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive buy vs rent recommendation
        
        Args:
            npv_results: Results from NPV analysis
            risk_tolerance: Risk tolerance level ("conservative", "moderate", "aggressive")
            
        Returns:
            Dictionary with detailed decision recommendation
        """
        if not npv_results.get('calculation_successful', False):
            return self._create_error_decision(npv_results.get('error_message', 'Unknown error'))
        
        # Extract key metrics
        npv_difference = npv_results.get('npv_difference', 0)
        ownership_npv = npv_results.get('ownership_npv', 0)  
        rental_npv = npv_results.get('rental_npv', 0)
        initial_investment = npv_results.get('ownership_initial_investment', 0)
        terminal_value_advantage = npv_results.get('terminal_value_advantage', 0)
        
        # Calculate decision metrics
        decision_metrics = self._calculate_decision_metrics(
            npv_difference, ownership_npv, rental_npv, initial_investment, terminal_value_advantage
        )
        
        # Determine base recommendation
        base_recommendation = self._determine_base_recommendation(npv_difference, risk_tolerance)
        
        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(npv_results, decision_metrics)
        
        # Perform risk assessment
        risk_assessment = self._perform_risk_assessment(npv_results, decision_metrics)
        
        # Generate executive reasoning
        executive_reasoning = self._generate_executive_reasoning(
            base_recommendation, npv_difference, decision_metrics, risk_assessment
        )
        
        # Create decision recommendation
        decision = {
            'recommendation': base_recommendation.value,
            'confidence_level': confidence_level.value,
            'npv_advantage': npv_difference,
            'decision_metrics': decision_metrics,
            'risk_assessment': risk_assessment,
            'executive_summary': executive_reasoning,
            'timestamp': datetime.now().isoformat(),
            'risk_tolerance_used': risk_tolerance
        }
        
        # Store in decision history
        self.decision_history.append(decision.copy())
        
        return decision
    
    def _calculate_decision_metrics(
        self,
        npv_difference: float,
        ownership_npv: float,
        rental_npv: float,
        initial_investment: float,
        terminal_value_advantage: float
    ) -> Dict[str, float]:
        """Calculate additional metrics for decision-making"""
        
        # Return on initial investment (proper NPV-based ROI formula)
        if initial_investment > 0:
            # ROI = (Total Return / Initial Investment) * 100
            # For NPV analysis: ROI = (Ownership NPV + Initial Investment) / Initial Investment * 100
            roi_percentage = (ownership_npv + initial_investment) / initial_investment * 100
        elif initial_investment == 0:
            roi_percentage = float('inf') if npv_difference > 0 else 0.0
        else:
            # Negative initial investment (shouldn't happen, but handle gracefully)
            roi_percentage = 0.0
        
        # NPV margin (relative advantage)
        total_rental_cost = abs(rental_npv) if rental_npv != 0 else 1
        npv_margin_percentage = (npv_difference / total_rental_cost * 100)
        
        # Terminal value contribution
        terminal_contribution = (terminal_value_advantage / npv_difference * 100) if npv_difference != 0 else 0
        
        # Risk-adjusted metrics
        ownership_concentration_risk = 1.0  # All capital in one asset
        rental_flexibility_value = abs(rental_npv) * 0.05  # 5% value for flexibility
        
        return {
            'roi_percentage': float(roi_percentage),
            'npv_margin_percentage': float(npv_margin_percentage),
            'terminal_contribution_percentage': float(terminal_contribution),
            'ownership_concentration_risk': float(ownership_concentration_risk),
            'rental_flexibility_value': float(rental_flexibility_value),
            'absolute_advantage': float(abs(npv_difference)),
            'relative_advantage': float(npv_margin_percentage)
        }
    
    def _determine_base_recommendation(
        self, 
        npv_difference: float, 
        risk_tolerance: str
    ) -> DecisionRecommendation:
        """Determine base recommendation based on NPV difference and risk tolerance"""
        
        # Define thresholds based on risk tolerance
        if risk_tolerance == "conservative":
            thresholds = {
                'strong_buy': 2000000,
                'buy': 1000000, 
                'marginal_buy': 500000,
                'neutral': 250000,
                'marginal_rent': -250000,
                'rent': -1000000
            }
        elif risk_tolerance == "aggressive":
            thresholds = {
                'strong_buy': 500000,
                'buy': 250000,
                'marginal_buy': 100000,
                'neutral': 50000,
                'marginal_rent': -50000,
                'rent': -250000
            }
        else:  # moderate
            thresholds = {
                'strong_buy': 1500000,
                'buy': 750000,
                'marginal_buy': 300000,
                'neutral': 100000,
                'marginal_rent': -100000,
                'rent': -500000
            }
        
        # Determine recommendation
        if npv_difference >= thresholds['strong_buy']:
            return DecisionRecommendation.STRONG_BUY
        elif npv_difference >= thresholds['buy']:
            return DecisionRecommendation.BUY
        elif npv_difference >= thresholds['marginal_buy']:
            return DecisionRecommendation.MARGINAL_BUY
        elif npv_difference >= thresholds['neutral']:
            return DecisionRecommendation.NEUTRAL
        elif npv_difference >= thresholds['marginal_rent']:
            return DecisionRecommendation.MARGINAL_RENT
        elif npv_difference >= thresholds['rent']:
            return DecisionRecommendation.RENT
        else:
            return DecisionRecommendation.STRONG_RENT
    
    def _calculate_confidence_level(
        self, 
        npv_results: Dict[str, Any], 
        decision_metrics: Dict[str, float]
    ) -> ConfidenceLevel:
        """Calculate confidence level based on multiple factors"""
        
        confidence_score = 0
        
        # Factor 1: NPV margin size (0-30 points)
        npv_margin = abs(decision_metrics.get('npv_margin_percentage', 0))
        if npv_margin >= 50:
            confidence_score += 30
        elif npv_margin >= 25:
            confidence_score += 20
        elif npv_margin >= 10:
            confidence_score += 10
        elif npv_margin >= 5:
            confidence_score += 5
        
        # Factor 2: Terminal value contribution stability (0-25 points)
        terminal_contrib = abs(decision_metrics.get('terminal_contribution_percentage', 0))
        if terminal_contrib <= 30:  # Less dependent on terminal value = more stable
            confidence_score += 25
        elif terminal_contrib <= 50:
            confidence_score += 15
        elif terminal_contrib <= 70:
            confidence_score += 10
        else:
            confidence_score += 5
        
        # Factor 3: Initial investment reasonableness (0-20 points)
        initial_investment = npv_results.get('ownership_initial_investment', 0)
        purchase_price = npv_results.get('input_parameters', {}).get('purchase_price', 1)
        investment_ratio = initial_investment / purchase_price if purchase_price > 0 else 1
        
        if 0.2 <= investment_ratio <= 0.4:  # 20-40% down payment is optimal
            confidence_score += 20
        elif 0.15 <= investment_ratio <= 0.5:
            confidence_score += 15
        elif 0.1 <= investment_ratio <= 0.6:
            confidence_score += 10
        else:
            confidence_score += 5
        
        # Factor 4: Market assumptions reasonableness (0-15 points)
        params = npv_results.get('input_parameters', {})
        interest_rate = params.get('interest_rate', 0)
        market_appreciation = params.get('market_appreciation_rate', 0)
        
        if 2 <= interest_rate <= 8 and 1 <= market_appreciation <= 6:
            confidence_score += 15
        elif 1 <= interest_rate <= 12 and 0 <= market_appreciation <= 8:
            confidence_score += 10
        else:
            confidence_score += 5
        
        # Factor 5: Analysis period appropriateness (0-10 points)
        analysis_period = npv_results.get('analysis_period', 25)
        if 20 <= analysis_period <= 30:
            confidence_score += 10
        elif 15 <= analysis_period <= 35:
            confidence_score += 7
        else:
            confidence_score += 3
        
        # Convert score to confidence level
        if confidence_score >= 85:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 70:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 55:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 40:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    def _perform_risk_assessment(
        self, 
        npv_results: Dict[str, Any], 
        decision_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        
        params = npv_results.get('input_parameters', {})
        risk_factors = []
        risk_score = 0  # 0-100 scale
        
        # Market risk factors
        market_appreciation = params.get('market_appreciation_rate', 3)
        if market_appreciation >= 6:
            risk_factors.append("High market appreciation assumption may be optimistic")
            risk_score += 15
        elif market_appreciation <= 1:
            risk_factors.append("Low market appreciation may indicate declining market")
            risk_score += 10
        
        # Interest rate risk
        interest_rate = params.get('interest_rate', 5)
        if interest_rate >= 8:
            risk_factors.append("High interest rates increase financing costs")
            risk_score += 10
        elif interest_rate <= 2:
            risk_factors.append("Very low interest rates may not be sustainable")
            risk_score += 5
        
        # Leverage risk
        down_payment_pct = params.get('down_payment_pct', 30)
        if down_payment_pct <= 15:
            risk_factors.append("Low down payment increases financial leverage risk")
            risk_score += 20
        elif down_payment_pct >= 80:
            risk_factors.append("High down payment reduces liquidity")
            risk_score += 10
        
        # Terminal value dependency risk
        terminal_contrib = decision_metrics.get('terminal_contribution_percentage', 0)
        if abs(terminal_contrib) >= 70:
            risk_factors.append("Decision heavily dependent on terminal value assumptions")
            risk_score += 25
        elif abs(terminal_contrib) >= 50:
            risk_factors.append("Moderate dependency on terminal value assumptions")
            risk_score += 15
        
        # Concentration risk
        ownership_npv = abs(npv_results.get('ownership_npv', 0))
        initial_investment = npv_results.get('ownership_initial_investment', 0)
        if initial_investment > 0 and ownership_npv / initial_investment >= 5:  # High exposure relative to investment
            risk_factors.append("High concentration risk in single real estate asset")
            risk_score += 15
        elif initial_investment <= 0 and ownership_npv > 0:
            risk_factors.append("Extreme concentration risk - no initial investment with positive exposure")
            risk_score += 20
        
        # Market timing risk
        analysis_period = npv_results.get('analysis_period', 25)
        if analysis_period >= 35:
            risk_factors.append("Long analysis period increases market uncertainty")
            risk_score += 10
        
        # Liquidity risk
        if down_payment_pct >= 50:
            risk_factors.append("Significant capital tied up in illiquid real estate")
            risk_score += 10
        
        # Determine overall risk level
        if risk_score >= 70:
            risk_level = "Very High"
        elif risk_score >= 50:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Moderate"
        elif risk_score >= 15:
            risk_level = "Low"
        else:
            risk_level = "Very Low"
        
        return {
            'overall_risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'key_risks': {
                'market_risk': market_appreciation >= 6 or market_appreciation <= 1,
                'interest_rate_risk': interest_rate >= 8 or interest_rate <= 2,
                'leverage_risk': down_payment_pct <= 15,
                'terminal_value_risk': abs(terminal_contrib) >= 70,
                'concentration_risk': initial_investment > 0 and ownership_npv / initial_investment >= 5,
                'liquidity_risk': down_payment_pct >= 50
            }
        }
    
    def _generate_executive_reasoning(
        self,
        recommendation: DecisionRecommendation,
        npv_difference: float,
        decision_metrics: Dict[str, float],
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive-level reasoning and summary"""
        
        # Format NPV difference
        npv_formatted = f"${abs(npv_difference):,.0f}"
        
        # Primary reasoning based on recommendation
        if recommendation in [DecisionRecommendation.STRONG_BUY, DecisionRecommendation.BUY]:
            primary_reason = f"Ownership provides {npv_formatted} NPV advantage over rental"
            decision_summary = "Recommend proceeding with property purchase"
            
        elif recommendation == DecisionRecommendation.MARGINAL_BUY:
            primary_reason = f"Ownership shows {npv_formatted} NPV advantage, but margin is moderate"
            decision_summary = "Lean toward purchase with careful consideration of risks"
            
        elif recommendation == DecisionRecommendation.NEUTRAL:
            primary_reason = f"NPV difference is minimal ({npv_formatted})"
            decision_summary = "Either option viable - consider non-financial factors"
            
        elif recommendation == DecisionRecommendation.MARGINAL_RENT:
            primary_reason = f"Rental shows {npv_formatted} NPV advantage, but margin is small"
            decision_summary = "Lean toward rental while monitoring market conditions"
            
        elif recommendation in [DecisionRecommendation.RENT, DecisionRecommendation.STRONG_RENT]:
            primary_reason = f"Rental provides {npv_formatted} NPV advantage over ownership"
            decision_summary = "Recommend continuing with rental arrangement"
            
        else:
            primary_reason = "Analysis incomplete or invalid"
            decision_summary = "Cannot provide recommendation due to data issues"
        
        # Key supporting factors
        supporting_factors = []
        
        roi = decision_metrics.get('roi_percentage', 0)
        if roi >= 15:
            supporting_factors.append(f"Strong ROI of {roi:.1f}% on initial investment")
        elif roi >= 8:
            supporting_factors.append(f"Moderate ROI of {roi:.1f}% on initial investment")
        elif roi <= -10:
            supporting_factors.append(f"Negative ROI of {roi:.1f}% indicates poor investment")
        
        # Risk considerations
        risk_level = risk_assessment.get('overall_risk_level', 'Unknown')
        if risk_level in ['Very High', 'High']:
            supporting_factors.append(f"⚠️ {risk_level} risk level requires careful consideration")
        elif risk_level == 'Very Low':
            supporting_factors.append(f"✅ {risk_level} risk profile supports decision confidence")
        
        # Terminal value dependency
        terminal_contrib = decision_metrics.get('terminal_contribution_percentage', 0)
        if abs(terminal_contrib) >= 70:
            supporting_factors.append("⚠️ Decision heavily dependent on long-term property value assumptions")
        elif abs(terminal_contrib) <= 30:
            supporting_factors.append("✅ Decision based primarily on operational cash flows")
        
        return {
            'primary_reason': primary_reason,
            'decision_summary': decision_summary,
            'supporting_factors': supporting_factors,
            'key_considerations': risk_assessment.get('risk_factors', [])[:3],  # Top 3 risks
            'confidence_note': self._get_confidence_note(decision_metrics, risk_assessment)
        }
    
    def _get_confidence_note(
        self, 
        decision_metrics: Dict[str, float], 
        risk_assessment: Dict[str, Any]
    ) -> str:
        """Generate confidence note for executive summary"""
        
        risk_level = risk_assessment.get('overall_risk_level', 'Unknown')
        npv_margin = decision_metrics.get('npv_margin_percentage', 0)
        
        if risk_level == 'Very Low' and abs(npv_margin) >= 25:
            return "High confidence in recommendation due to large NPV margin and low risk factors"
        elif risk_level in ['Low', 'Moderate'] and abs(npv_margin) >= 15:
            return "Good confidence in recommendation with manageable risk factors"
        elif risk_level == 'High' or abs(npv_margin) <= 10:
            return "Moderate confidence - recommendation sensitive to assumptions"
        else:
            return "Lower confidence due to high risks or small NPV margins"
    
    def _create_error_decision(self, error_message: str) -> Dict[str, Any]:
        """Create error decision response"""
        return {
            'recommendation': DecisionRecommendation.ERROR.value,
            'confidence_level': ConfidenceLevel.VERY_LOW.value,
            'error_message': error_message,
            'executive_summary': {
                'primary_reason': 'Analysis failed due to data or calculation errors',
                'decision_summary': 'Cannot provide recommendation',
                'supporting_factors': [],
                'key_considerations': [error_message]
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_decision_comparison(
        self, 
        scenario_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare multiple scenarios and provide meta-analysis
        
        Args:
            scenario_results: List of NPV analysis results for different scenarios
            
        Returns:
            Comparative decision analysis
        """
        if not scenario_results:
            return {'error': 'No scenarios provided for comparison'}
        
        # Calculate decisions for all scenarios
        decisions = []
        for scenario in scenario_results:
            decision = self.calculate_decision_recommendation(scenario)
            decisions.append(decision)
        
        # Find best scenario
        best_scenario_idx = 0
        best_npv = float('-inf')
        
        for i, decision in enumerate(decisions):
            npv = decision.get('npv_advantage', float('-inf'))
            if npv > best_npv:
                best_npv = npv
                best_scenario_idx = i
        
        # Analyze consistency
        recommendations = [d.get('recommendation') for d in decisions]
        consistent_recommendation = all(r == recommendations[0] for r in recommendations)
        
        # Calculate recommendation distribution
        recommendation_counts = {}
        for rec in recommendations:
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
        
        return {
            'best_scenario_index': best_scenario_idx,
            'best_scenario_npv': best_npv,
            'consistent_recommendation': consistent_recommendation,
            'recommendation_distribution': recommendation_counts,
            'all_decisions': decisions,
            'meta_confidence': 'High' if consistent_recommendation else 'Low'
        }
    
    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Get history of all decisions made by this engine"""
        return self.decision_history.copy()
    
    def clear_decision_history(self):
        """Clear decision history"""
        self.decision_history = []


# Convenience functions for external use
def make_investment_decision(npv_results: Dict[str, Any], risk_tolerance: str = "moderate") -> Dict[str, Any]:
    """
    Make investment decision from NPV results
    
    Args:
        npv_results: Results from NPV analysis
        risk_tolerance: Risk tolerance level
        
    Returns:
        Investment decision recommendation
    """
    engine = DecisionEngine()
    return engine.calculate_decision_recommendation(npv_results, risk_tolerance)


def get_executive_summary(decision: Dict[str, Any], currency: str = "USD") -> str:
    """
    Generate executive summary text from decision
    
    Args:
        decision: Decision results from DecisionEngine
        currency: Currency for formatting
        
    Returns:
        Executive summary as formatted text
    """
    if decision.get('recommendation') == 'ERROR':
        return "❌ **Analysis Error**: Cannot provide investment recommendation due to data issues."
    
    summary = decision.get('executive_summary', {})
    recommendation = decision.get('recommendation', 'UNKNOWN')
    confidence = decision.get('confidence_level', 'Unknown')
    
    # Create formatted summary
    text = f"## 📊 **Investment Recommendation: {recommendation}**\n\n"
    text += f"**Confidence Level:** {confidence}\n\n"
    text += f"**Primary Analysis:** {summary.get('primary_reason', 'No analysis available')}\n\n"
    text += f"**Decision:** {summary.get('decision_summary', 'No summary available')}\n\n"
    
    # Add supporting factors
    factors = summary.get('supporting_factors', [])
    if factors:
        text += "**Key Supporting Factors:**\n"
        for factor in factors:
            text += f"• {factor}\n"
        text += "\n"
    
    # Add key considerations
    considerations = summary.get('key_considerations', [])
    if considerations:
        text += "**Key Considerations:**\n"
        for consideration in considerations[:3]:  # Top 3
            text += f"• {consideration}\n"
        text += "\n"
    
    # Add confidence note
    confidence_note = summary.get('confidence_note', '')
    if confidence_note:
        text += f"**Confidence Assessment:** {confidence_note}\n"
    
    return text


if __name__ == "__main__":
    # Test the decision engine
    print("Testing Decision Engine...")
    
    # Create test NPV results
    test_npv_results = {
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
    
    # Test decision making
    engine = DecisionEngine()
    decision = engine.calculate_decision_recommendation(test_npv_results, "moderate")
    
    print(f"✅ Decision Engine test completed")
    print(f"Recommendation: {decision.get('recommendation')}")
    print(f"Confidence: {decision.get('confidence_level')}")
    print(f"Risk Level: {decision.get('risk_assessment', {}).get('overall_risk_level')}")
    
    # Test executive summary
    executive_text = get_executive_summary(decision)
    print(f"\nExecutive Summary Preview:")
    print(executive_text[:200] + "..." if len(executive_text) > 200 else executive_text)