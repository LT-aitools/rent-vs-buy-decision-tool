"""
Analytics Engine for Week 4 Real Estate Decision Tool

This module provides advanced analytics capabilities including:
- Sensitivity analysis with real-time visualization
- Monte Carlo simulation (10,000+ iterations)
- Scenario modeling and comparison
- Risk assessment algorithms
- Market trend integration

All components implement the AnalyticsEngine interface from src/shared/interfaces.py
and meet the performance targets specified in the Week 4 PRD.
"""

from .sensitivity_analysis import SensitivityAnalysisEngine
from .monte_carlo import MonteCarloEngine
from .scenario_modeling import ScenarioModelingEngine
from .risk_assessment import RiskAssessmentEngine

__all__ = [
    'SensitivityAnalysisEngine',
    'MonteCarloEngine', 
    'ScenarioModelingEngine',
    'RiskAssessmentEngine'
]