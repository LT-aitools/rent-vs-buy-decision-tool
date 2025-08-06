"""
Default Values from Business PRD
Smart defaults for all input fields based on business requirements

All defaults are taken directly from the Business PRD specifications
to ensure consistency and reduce user input burden.
"""

from datetime import datetime
from typing import Dict, Any

# Currency options from PRD
CURRENCY_OPTIONS = [
    "USD", "EUR", "GBP", "CAD", "AUD", "ILS", "LEI", "PLN"
]

# Property type options from PRD
PROPERTY_TYPE_OPTIONS = [
    "Warehouse", 
    "Distribution Center", 
    "Manufacturing", 
    "Office", 
    "Mixed Use"
]

# Default values for all input fields
DEFAULT_VALUES: Dict[str, Any] = {
    # 1.1 PROJECT INFORMATION
    "project_name": f"Property Analysis {datetime.now().strftime('%Y-%m-%d')}",
    "location": "",
    "analysis_date": datetime.now().date(),
    "analyst_name": "",
    "currency": "USD",
    
    # 1.2 PROPERTY & MARKET INFORMATION  
    "property_type": "Warehouse",
    "total_property_size": None,  # Required, no default
    "current_space_needed": None,  # Required, no default
    "market_appreciation_rate": 3.0,  # 3%
    
    # 1.3 FINANCIAL PARAMETERS - PURCHASE SCENARIO
    "purchase_price": None,  # Required, no default
    "transaction_costs_percent": 5.0,  # 5% of purchase price
    "down_payment_percent": 30.0,  # 30%
    "interest_rate": 5.0,  # 5.0%
    "loan_term": 20,  # 20 years
    "property_tax_rate": 1.2,  # 1.2%
    "insurance_cost": 5000,  # $5,000
    "annual_maintenance_percent": 2.0,  # 2% of purchase price
    "property_management": 0,  # $0
    "land_value_percent": 25.0,  # 25%
    "space_improvement_cost": 50,  # $50 per sq meter
    "property_tax_escalation_rate": 2.0,  # 2.0%
    "inflation_rate": 3.0,  # 3.0%
    
    # 1.4 FINANCIAL PARAMETERS - RENTAL SCENARIO
    "current_annual_rent": None,  # Required, no default
    "rent_increase_rate": 3.0,  # 3%
    "security_deposit_months": 2,  # 2 months rent
    "rental_commission_months": 1,  # 1 month rent
    "lease_break_penalty_months": 6,  # 6 months rent
    "moving_costs": 0,  # $0
    
    # 1.5 OPERATIONAL PARAMETERS
    "analysis_period": 25,  # 25 years
    "growth_rate": 5.0,  # 5%
    "future_expansion_year": 10,  # Year 10
    "additional_space_needed": 0,  # 0 sq meter
    "subletting_potential": False,  # No
    "subletting_rate": 0,  # $0 per sq meter
    "subletting_occupancy": 85.0,  # 85%
    "cost_of_capital": 8.0,  # 8%
    "longterm_capex_reserve": 1.5,  # 1.5%
    "property_upgrade_cycle": 15,  # 15 years
    "obsolescence_risk_factor": 0.5,  # 0.5%
    
    # 1.6 TAX & ACCOUNTING PARAMETERS
    "corporate_tax_rate": 25.0,  # 25%
    "depreciation_period": 39,  # 39 years
    "interest_deductible": True,  # Yes
    "property_tax_deductible": True,  # Yes
    "rent_deductible": True,  # Yes
}

# Validation ranges for each field
VALIDATION_RANGES: Dict[str, Dict[str, Any]] = {
    # Text fields
    "project_name": {"max_length": 100},
    "location": {"max_length": 200},
    "analyst_name": {"max_length": 50},
    
    # Numeric ranges
    "total_property_size": {"min": 1000, "max": 1000000},
    "current_space_needed": {"min": 500, "max": 1000000},
    "market_appreciation_rate": {"min": 0.0, "max": 15.0},
    
    "purchase_price": {"min": 50000, "max": 100000000},
    "transaction_costs_percent": {"min": 0.0, "max": 15.0},
    "down_payment_percent": {"min": 0.0, "max": 100.0},
    "interest_rate": {"min": 0.0, "max": 20.0},
    "loan_term": {"min": 0, "max": 30},
    "property_tax_rate": {"min": 0.0, "max": 10.0},
    "insurance_cost": {"min": 0, "max": 100000},
    "annual_maintenance_percent": {"min": 0.0, "max": 10.0},
    "property_management": {"min": 0, "max": 100000},
    "land_value_percent": {"min": 10.0, "max": 50.0},
    "space_improvement_cost": {"min": 0, "max": 1000},
    "property_tax_escalation_rate": {"min": 0.0, "max": 10.0},
    "inflation_rate": {"min": 0.0, "max": 20.0},
    
    "current_annual_rent": {"min": 1000, "max": 10000000},
    "rent_increase_rate": {"min": 0.0, "max": 15.0},
    "security_deposit_months": {"min": 0, "max": 12},
    "rental_commission_months": {"min": 0, "max": 6},
    "lease_break_penalty_months": {"min": 0, "max": 24},
    "moving_costs": {"min": 0, "max": 1000000},
    
    "analysis_period": {"min": 0, "max": 100},
    "growth_rate": {"min": -5.0, "max": 25.0},
    "future_expansion_year": {"min": 1, "max": 100},
    "additional_space_needed": {"min": 0, "max": 100000},
    "subletting_rate": {"min": 0, "max": 1000},
    "subletting_occupancy": {"min": 0.0, "max": 100.0},
    "cost_of_capital": {"min": 0.0, "max": 20.0},
    "longterm_capex_reserve": {"min": 0.0, "max": 10.0},
    "property_upgrade_cycle": {"min": 5, "max": 50},
    "obsolescence_risk_factor": {"min": 0.0, "max": 5.0},
    
    "corporate_tax_rate": {"min": 0.0, "max": 50.0},
    "depreciation_period": {"min": 0, "max": 50},
}

# Field descriptions and tooltips
FIELD_DESCRIPTIONS: Dict[str, str] = {
    # Project Information
    "project_name": "Identifier for scenario tracking and reporting",
    "location": "Property address or general location for reference",
    "analysis_date": "Date when this analysis was performed",
    "analyst_name": "Person performing the analysis for accountability",
    "currency": "Currency for all monetary values in the analysis",
    
    # Property & Market
    "property_type": "Type of facility being analyzed for rent vs buy decision",
    "total_property_size": "Total square meters of the entire property",
    "current_space_needed": "Current operational space requirement in square meters",
    "market_appreciation_rate": "Expected annual property value appreciation percentage",
    
    # Purchase Parameters
    "purchase_price": "Total acquisition cost of the property",
    "transaction_costs_percent": "Legal, inspection, and broker fees as % of purchase price",
    "down_payment_percent": "Percentage of purchase price paid as equity upfront",
    "interest_rate": "Annual interest rate for financing the property purchase",
    "loan_term": "Number of years for loan amortization",
    "property_tax_rate": "Annual property tax as percentage of property value",
    "insurance_cost": "Annual property insurance premium amount",
    "annual_maintenance_percent": "Annual maintenance and repairs as % of purchase price",
    "property_management": "Annual property management fees",
    "land_value_percent": "Land value as percentage of total purchase price",
    "space_improvement_cost": "Cost per square meter to improve unutilized space",
    "property_tax_escalation_rate": "Annual property tax assessment increase rate",
    "inflation_rate": "General annual inflation rate for cost escalations",
    
    # Rental Parameters
    "current_annual_rent": "Current total annual rental cost",
    "rent_increase_rate": "Expected annual rent escalation percentage",
    "security_deposit_months": "Upfront rental security deposit in months of rent",
    "rental_commission_months": "Broker commission for new lease in months of rent",
    "lease_break_penalty_months": "Penalty for early lease termination in months of rent",
    "moving_costs": "One-time cost to relocate operations",
    
    # Operational Parameters
    "analysis_period": "Time horizon in years for the rent vs buy analysis",
    "growth_rate": "Expected business growth rate affecting space needs",
    "future_expansion_year": "Year when additional space will be needed",
    "additional_space_needed": "Extra square meters required for future growth",
    "subletting_potential": "Whether excess space can be sublet to generate income",
    "subletting_rate": "Annual income per square meter from subletting",
    "subletting_occupancy": "Expected occupancy rate for subletting activities",
    "cost_of_capital": "Company's cost of capital/discount rate for NPV calculations",
    "longterm_capex_reserve": "Annual reserve for major property improvements",
    "property_upgrade_cycle": "Years between major renovations or upgrades",
    "obsolescence_risk_factor": "Annual risk of property becoming less suitable",
    
    # Tax & Accounting
    "corporate_tax_rate": "Applicable corporate tax rate for tax benefit calculations",
    "depreciation_period": "Property depreciation schedule for tax purposes",
    "interest_deductible": "Whether mortgage interest is tax deductible",
    "property_tax_deductible": "Whether property taxes are tax deductible",
    "rent_deductible": "Whether rent expense is tax deductible",
}

def get_default_value(field_name: str) -> Any:
    """Get the default value for a specific field"""
    return DEFAULT_VALUES.get(field_name)

def get_validation_range(field_name: str) -> Dict[str, Any]:
    """Get validation parameters for a specific field"""
    return VALIDATION_RANGES.get(field_name, {})

def get_field_description(field_name: str) -> str:
    """Get the description/tooltip for a specific field"""
    return FIELD_DESCRIPTIONS.get(field_name, "")

def get_expansion_year_options(analysis_period: int) -> list:
    """Get dropdown options for future expansion year"""
    options = ["Never"] + [f"Year {i}" for i in range(1, analysis_period + 1)]
    return options