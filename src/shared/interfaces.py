"""
Week 4 Shared Interfaces
Standard interface definitions for sub-agent work tree coordination

This module defines the contracts between work trees to ensure seamless integration
while maintaining independence during development.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import abc


# ============================================================================
# Core Data Types
# ============================================================================

class AnalysisType(Enum):
    """Types of analysis supported by the system"""
    SENSITIVITY = "sensitivity"
    SCENARIO = "scenario" 
    MONTE_CARLO = "monte_carlo"
    RISK_ASSESSMENT = "risk_assessment"
    COMPARATIVE = "comparative"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationStatus(Enum):
    """Data validation status"""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"
    MISSING = "missing"


# ============================================================================
# Analytics Engine Interfaces (Work Tree 1)
# ============================================================================

@dataclass
class SensitivityVariable:
    """Definition of a variable for sensitivity analysis"""
    name: str
    base_value: float
    min_value: float
    max_value: float
    step_size: float
    unit: str
    description: str


@dataclass
class SensitivityResult:
    """Result of sensitivity analysis for a single variable"""
    variable_name: str
    variable_values: List[float]
    npv_impacts: List[float]
    percentage_changes: List[float]
    elasticity: float  # % change in NPV per % change in variable


@dataclass
class ScenarioDefinition:
    """Definition of a scenario for comparison"""
    name: str
    description: str
    parameters: Dict[str, float]
    probability: Optional[float] = None


@dataclass
class MonteCarloResult:
    """Results from Monte Carlo simulation"""
    iterations: int
    mean_npv: float
    std_dev: float
    percentiles: Dict[int, float]  # e.g., {5: -50000, 50: 125000, 95: 300000}
    probability_positive: float
    confidence_intervals: Dict[int, tuple]  # e.g., {90: (lower, upper)}


@dataclass
class RiskAssessment:
    """Risk assessment results"""
    overall_risk_level: RiskLevel
    risk_factors: Dict[str, float]  # factor_name -> risk_score (0-1)
    risk_description: str
    mitigation_suggestions: List[str]
    confidence_score: float


@dataclass
class AnalyticsResult:
    """Comprehensive analytics results from Analytics Engine"""
    analysis_timestamp: datetime
    ownership_npv: float  # Changed from base_npv_buy
    rental_npv: float     # Changed from base_npv_rent
    base_recommendation: str
    
    # Sensitivity Analysis
    sensitivity_results: List[SensitivityResult]
    sensitivity_summary: Dict[str, float]  # variable -> max_impact
    
    # Scenario Analysis
    scenario_comparisons: List[Dict[str, Any]]
    best_case_npv: float
    worst_case_npv: float
    
    # Monte Carlo
    monte_carlo: Optional[MonteCarloResult]
    
    # Risk Assessment
    risk_assessment: RiskAssessment
    
    # Metadata
    calculation_time_ms: float
    data_sources: List[str]


class AnalyticsEngine(abc.ABC):
    """Abstract base class for Analytics Engine"""
    
    @abc.abstractmethod
    def run_sensitivity_analysis(
        self, 
        base_params: Dict[str, float],
        variables: List[SensitivityVariable]
    ) -> List[SensitivityResult]:
        """Run sensitivity analysis on specified variables"""
        pass
    
    @abc.abstractmethod
    def run_scenario_analysis(
        self,
        base_params: Dict[str, float],
        scenarios: List[ScenarioDefinition]
    ) -> List[Dict[str, Any]]:
        """Compare multiple scenarios"""
        pass
    
    @abc.abstractmethod
    def run_monte_carlo(
        self,
        base_params: Dict[str, float],
        variable_distributions: Dict[str, Dict],
        iterations: int = 10000
    ) -> MonteCarloResult:
        """Run Monte Carlo simulation"""
        pass
    
    @abc.abstractmethod
    def assess_risk(
        self,
        analysis_params: Dict[str, float],
        market_data: 'MarketData'
    ) -> RiskAssessment:
        """Assess investment risk"""
        pass


# ============================================================================
# User Experience Interfaces (Work Tree 2)
# ============================================================================

@dataclass
class ValidationResult:
    """Result of input validation"""
    is_valid: bool
    status: ValidationStatus
    message: str
    suggestions: List[str] = None


@dataclass
class GuidanceContext:
    """Context for providing user guidance"""
    current_step: str
    user_inputs: Dict[str, Any]
    analysis_results: Optional[AnalyticsResult]
    user_experience_level: str  # "beginner", "intermediate", "expert"


@dataclass
class UIState:
    """Current state of the user interface"""
    active_tab: str
    input_values: Dict[str, Any]
    validation_results: Dict[str, ValidationResult]
    guidance_visible: bool
    mobile_mode: bool


class UIComponent(abc.ABC):
    """Abstract base class for UI components"""
    
    @abc.abstractmethod
    def render(self, data: Any, state: UIState) -> None:
        """Render the component"""
        pass
    
    @abc.abstractmethod
    def validate_input(self, field_name: str, value: Any) -> ValidationResult:
        """Validate user input"""
        pass
    
    @abc.abstractmethod
    def get_guidance(self, context: GuidanceContext) -> str:
        """Provide contextual guidance"""
        pass


class GuidanceSystem(abc.ABC):
    """Abstract base class for user guidance system"""
    
    @abc.abstractmethod
    def get_help_text(self, field_name: str, context: GuidanceContext) -> str:
        """Get help text for a specific field"""
        pass
    
    @abc.abstractmethod
    def get_decision_guidance(self, analysis_result: AnalyticsResult) -> str:
        """Provide guidance based on analysis results"""
        pass
    
    @abc.abstractmethod
    def get_next_step_suggestion(self, current_state: UIState) -> str:
        """Suggest next steps to user"""
        pass


# ============================================================================
# Data Integration Interfaces (Work Tree 3)
# ============================================================================

@dataclass
class MarketData:
    """Market data from external sources"""
    location: str
    zip_code: Optional[str]
    
    # Rental Market Data
    median_rent_per_sqm: float
    rental_vacancy_rate: float
    rental_growth_rate: float
    
    # Property Market Data
    median_property_price: float
    property_appreciation_rate: float
    months_on_market: float
    
    # Interest Rate Data
    current_mortgage_rates: Dict[str, float]  # loan_type -> rate
    rate_trend: str  # "rising", "falling", "stable"
    
    # Economic Indicators
    local_inflation_rate: float
    unemployment_rate: float
    population_growth_rate: float
    
    # Data Quality Metrics
    data_timestamp: datetime
    data_sources: List[str]
    confidence_score: float  # 0-1, higher is better
    freshness_hours: float


@dataclass
class DataRequest:
    """Request for market data"""
    location: str
    zip_code: Optional[str]
    data_types: List[str]  # ["rental", "property", "rates", "economic"]
    max_age_hours: float = 24.0
    fallback_to_cache: bool = True


@dataclass
class DataValidationResult:
    """Result of data validation"""
    is_valid: bool
    quality_score: float  # 0-1
    issues: List[str]
    recommendations: List[str]
    fallback_data_used: bool


class DataProvider(abc.ABC):
    """Abstract base class for data providers"""
    
    @abc.abstractmethod
    def get_market_data(self, request: DataRequest) -> MarketData:
        """Retrieve market data for location"""
        pass
    
    @abc.abstractmethod
    def validate_data(self, data: MarketData) -> DataValidationResult:
        """Validate data quality and freshness"""
        pass
    
    @abc.abstractmethod
    def get_cached_data(self, location: str) -> Optional[MarketData]:
        """Retrieve cached data if available"""
        pass
    
    @abc.abstractmethod
    def update_cache(self, location: str, data: MarketData) -> None:
        """Update cached data"""
        pass


# ============================================================================
# Testing & QA Interfaces (Work Tree 4)
# ============================================================================

@dataclass
class TestResult:
    """Result of a test execution"""
    test_name: str
    passed: bool
    execution_time_ms: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceMetric:
    """Performance measurement result"""
    metric_name: str
    value: float
    unit: str
    target_value: float
    meets_target: bool
    timestamp: datetime


@dataclass
class AccuracyTestCase:
    """Test case for financial accuracy verification"""
    test_name: str
    inputs: Dict[str, float]
    expected_outputs: Dict[str, float]
    tolerance: float = 0.01  # Maximum allowed difference
    description: str = ""


@dataclass
class TestSuiteResult:
    """Results from running a test suite"""
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    coverage_percentage: float
    execution_time_ms: float
    test_results: List[TestResult]


class TestFramework(abc.ABC):
    """Abstract base class for testing framework"""
    
    @abc.abstractmethod
    def run_unit_tests(self, component_name: str) -> TestSuiteResult:
        """Run unit tests for a component"""
        pass
    
    @abc.abstractmethod
    def run_integration_tests(self) -> TestSuiteResult:
        """Run integration tests"""
        pass
    
    @abc.abstractmethod
    def validate_accuracy(self, test_cases: List[AccuracyTestCase]) -> TestSuiteResult:
        """Validate financial calculation accuracy"""
        pass
    
    @abc.abstractmethod
    def benchmark_performance(self, component_name: str) -> List[PerformanceMetric]:
        """Benchmark component performance"""
        pass


# ============================================================================
# Cross-Tree Integration Interfaces
# ============================================================================

@dataclass
class IntegrationRequest:
    """Request for cross-tree functionality"""
    source_tree: str
    target_tree: str
    request_type: str
    parameters: Dict[str, Any]
    timeout_seconds: float = 30.0


@dataclass
class IntegrationResponse:
    """Response from cross-tree functionality"""
    success: bool
    data: Any
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0


class IntegrationBus(abc.ABC):
    """Message bus for cross-tree communication"""
    
    @abc.abstractmethod
    def send_request(self, request: IntegrationRequest) -> IntegrationResponse:
        """Send request to another work tree"""
        pass
    
    @abc.abstractmethod
    def register_handler(self, request_type: str, handler: callable) -> None:
        """Register handler for request type"""
        pass


# ============================================================================
# Utility Functions
# ============================================================================

def validate_interface_compliance(component: Any, interface_class: type) -> bool:
    """Check if component implements required interface"""
    if not hasattr(component, '__class__'):
        return False
    
    return issubclass(component.__class__, interface_class)


def create_mock_market_data(location: str = "Default") -> MarketData:
    """Create mock market data for testing"""
    return MarketData(
        location=location,
        zip_code="12345",
        median_rent_per_sqm=25.0,
        rental_vacancy_rate=5.0,
        rental_growth_rate=3.0,
        median_property_price=500000.0,
        property_appreciation_rate=4.0,
        months_on_market=2.5,
        current_mortgage_rates={"30_year_fixed": 6.5, "15_year_fixed": 6.0},
        rate_trend="stable",
        local_inflation_rate=3.0,
        unemployment_rate=4.5,
        population_growth_rate=1.2,
        data_timestamp=datetime.now(),
        data_sources=["mock_api"],
        confidence_score=0.8,
        freshness_hours=1.0
    )


def create_mock_analytics_result() -> AnalyticsResult:
    """Create mock analytics result for testing"""
    return AnalyticsResult(
        analysis_timestamp=datetime.now(),
        ownership_npv=125000.0,  # Changed from base_npv_buy
        rental_npv=-50000.0,     # Changed from base_npv_rent
        base_recommendation="Buy",
        sensitivity_results=[],
        sensitivity_summary={},
        scenario_comparisons=[],
        best_case_npv=200000.0,
        worst_case_npv=-25000.0,
        monte_carlo=None,
        risk_assessment=RiskAssessment(
            overall_risk_level=RiskLevel.MEDIUM,
            risk_factors={"market_risk": 0.6, "financial_risk": 0.4},
            risk_description="Moderate risk investment",
            mitigation_suggestions=["Consider market timing"],
            confidence_score=0.75
        ),
        calculation_time_ms=250.0,
        data_sources=["mock_data"]
    )