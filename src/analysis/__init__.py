"""
Data Analysis Integration Engine
Comprehensive analysis capabilities connecting UI inputs to calculations engine

This package provides:
- NPV Integration Engine: UI → Calculations → Results pipeline
- Decision Engine: Buy vs Rent recommendations with confidence levels
- Sensitivity Analysis: Parameter impact analysis and break-even calculations
- Results Processor: Professional formatting and KPI generation
- Integration Testing: End-to-end validation

All analysis functions follow the Business PRD specifications exactly.
"""

from .npv_integration import NPVIntegrationEngine
from .decision_engine import DecisionEngine  
from .sensitivity import SensitivityAnalyzer
from .results_processor import ResultsProcessor

__all__ = [
    'NPVIntegrationEngine',
    'DecisionEngine',
    'SensitivityAnalyzer', 
    'ResultsProcessor'
]