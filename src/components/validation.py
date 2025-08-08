"""
Input Validation System
Comprehensive validation for all input fields with helpful error messages

Provides:
- Field-specific validation rules
- Business logic validation
- Cross-field validation
- Professional error messages
- Warning and info messages
"""

import streamlit as st
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.defaults import VALIDATION_RANGES, get_validation_range

class ValidationResult:
    """Container for validation results"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.is_valid: bool = True
    
    def add_error(self, message: str):
        """Add an error message"""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)
    
    def add_info(self, message: str):
        """Add an info message"""
        self.info.append(message)

class InputValidator:
    """Main validation class for all input fields"""
    
    def __init__(self, currency: str = "USD"):
        self.currency = currency
        self.currency_symbol = self._get_currency_symbol(currency)
    
    def _get_currency_symbol(self, currency: str) -> str:
        """Get currency symbol for error messages"""
        symbols = {
            "USD": "$", "EUR": "€", "GBP": "£", "CAD": "C$", 
            "AUD": "A$", "ILS": "₪", "LEI": "lei", "PLN": "zł"
        }
        return symbols.get(currency, currency)
    
    def validate_required_field(self, value: Any, field_name: str, 
                               display_name: str) -> ValidationResult:
        """Validate that a required field has a value"""
        result = ValidationResult()
        
        if value is None or value == "" or value == 0:
            result.add_error(f"{display_name} is required and cannot be empty")
        
        return result
    
    def validate_numeric_range(self, value: Union[int, float], field_name: str,
                              display_name: str) -> ValidationResult:
        """Validate numeric value against defined ranges"""
        result = ValidationResult()
        
        if value is None:
            return result
        
        ranges = get_validation_range(field_name)
        
        if "min" in ranges and value < ranges["min"]:
            if field_name in ["purchase_price", "current_annual_rent", "insurance_cost"]:
                result.add_error(
                    f"{display_name} must be at least {self.currency_symbol}{ranges['min']:,}"
                )
            elif field_name.endswith("_percent") or field_name.endswith("_rate"):
                result.add_error(
                    f"{display_name} must be at least {ranges['min']}%"
                )
            else:
                result.add_error(
                    f"{display_name} must be at least {ranges['min']:,}"
                )
        
        if "max" in ranges and value > ranges["max"]:
            if field_name in ["purchase_price", "current_annual_rent", "insurance_cost"]:
                result.add_error(
                    f"{display_name} cannot exceed {self.currency_symbol}{ranges['max']:,}"
                )
            elif field_name.endswith("_percent") or field_name.endswith("_rate"):
                result.add_error(
                    f"{display_name} cannot exceed {ranges['max']}%"
                )
            else:
                result.add_error(
                    f"{display_name} cannot exceed {ranges['max']:,}"
                )
        
        return result
    
    def validate_text_length(self, value: str, field_name: str,
                           display_name: str) -> ValidationResult:
        """Validate text field length"""
        result = ValidationResult()
        
        if value is None:
            return result
        
        ranges = get_validation_range(field_name)
        max_length = ranges.get("max_length", 1000)
        
        if len(value) > max_length:
            result.add_error(
                f"{display_name} cannot exceed {max_length} characters "
                f"(currently {len(value)} characters)"
            )
        
        return result
    
    def validate_percentage(self, value: Union[int, float], field_name: str,
                           display_name: str) -> ValidationResult:
        """Validate percentage values"""
        result = ValidationResult()
        
        if value is None:
            return result
        
        # Add business logic warnings for percentages
        if field_name == "down_payment_percent":
            if value < 10:
                result.add_warning(
                    "Down payments below 10% may require additional insurance or fees"
                )
            elif value > 50:
                result.add_info(
                    "High down payment reduces financing risk and interest costs"
                )
        
        elif field_name == "interest_rate":
            if value > 10:
                result.add_warning(
                    "Interest rates above 10% are unusually high - please verify"
                )
            elif value < 1:
                result.add_info(
                    "Very low interest rates provide strong financing advantage"
                )
        
        elif field_name == "market_appreciation_rate":
            if value > 8:
                result.add_warning(
                    "Market appreciation above 8% annually is optimistic"
                )
            elif value < 1:
                result.add_warning(
                    "Very low appreciation rates may not keep pace with inflation"
                )
        
        return result
    
    def validate_space_relationship(self, total_size: Optional[float],
                                  current_needed: Optional[float]) -> ValidationResult:
        """Validate space size relationships"""
        result = ValidationResult()
        
        if total_size is None or current_needed is None:
            return result
        
        if current_needed > total_size:
            result.add_error(
                "Current space needed cannot exceed total property size"
            )
        
        utilization = (current_needed / total_size) * 100
        
        if utilization < 50:
            result.add_warning(
                f"Low space utilization ({utilization:.0f}%) - consider subletting potential"
            )
        elif utilization > 90:
            result.add_info(
                f"High space utilization ({utilization:.0f}%) - limited expansion room"
            )
        
        return result
    
    def validate_loan_terms(self, purchase_price: Optional[float],
                           down_payment_percent: Optional[float],
                           interest_rate: Optional[float],
                           loan_term: Optional[int]) -> ValidationResult:
        """Validate loan parameter relationships"""
        result = ValidationResult()
        
        if None in [purchase_price, down_payment_percent, interest_rate, loan_term]:
            return result
        
        loan_amount = purchase_price * (1 - down_payment_percent / 100)
        
        if down_payment_percent == 100:
            result.add_info("Full cash purchase - no financing costs")
        elif loan_amount < 10000:
            result.add_info("Very small loan amount - financing may not be necessary")
        
        if loan_term > 25:
            result.add_warning(
                "Loan terms over 25 years increase total interest costs significantly"
            )
        elif loan_term < 10:
            result.add_info(
                "Short loan terms reduce total interest but increase monthly payments"
            )
        
        return result
    
    def validate_rental_parameters(self, current_rent: Optional[float],
                                 current_space: Optional[float]) -> ValidationResult:
        """Validate rental parameter relationships"""
        result = ValidationResult()
        
        if current_rent is None or current_space is None:
            return result
        
        rent_per_sqm = current_rent / current_space
        
        if rent_per_sqm < 5:
            result.add_warning(
                f"Rent per m² ({self.currency_symbol}{rent_per_sqm:.2f}) seems unusually low"
            )
        elif rent_per_sqm > 100:
            result.add_warning(
                f"Rent per m² ({self.currency_symbol}{rent_per_sqm:.2f}) seems unusually high"
            )
        else:
            result.add_info(
                f"Current rent: {self.currency_symbol}{rent_per_sqm:.2f} per m²"
            )
        
        return result
    
    def validate_expansion_parameters(self, total_size: Optional[float],
                                    current_needed: Optional[float],
                                    additional_needed: Optional[float],
                                    expansion_year: Optional[str]) -> ValidationResult:
        """Validate expansion parameter relationships"""
        result = ValidationResult()
        
        if None in [total_size, current_needed, additional_needed] or expansion_year == "Never":
            return result
        
        total_future_need = current_needed + additional_needed
        
        if total_future_need > total_size:
            excess = total_future_need - total_size
            result.add_error(
                f"Future space needs ({total_future_need:,.0f} m²) exceed property size. "
                f"Shortfall: {excess:,.0f} m²"
            )
        elif additional_needed > 0:
            available_space = total_size - total_future_need
            result.add_info(
                f"After expansion: {available_space:,.0f} m² of space remaining"
            )
        
        return result
    
    def validate_all_inputs(self, inputs: Dict[str, Any]) -> ValidationResult:
        """Comprehensive validation of all inputs"""
        result = ValidationResult()
        
        # Required field validations
        required_fields = [
            ("project_name", "Project Name"),
            ("location", "Location"),
            ("analyst_name", "Analyst Name"),
            ("total_property_size", "Total Property Size"),
            ("current_space_needed", "Current Space Needed"),
            ("purchase_price", "Purchase Price"),
            ("current_annual_rent", "Current Annual Rent")
        ]
        
        for field_name, display_name in required_fields:
            field_result = self.validate_required_field(
                inputs.get(field_name), field_name, display_name
            )
            result.errors.extend(field_result.errors)
            result.warnings.extend(field_result.warnings)
            result.info.extend(field_result.info)
            if not field_result.is_valid:
                result.is_valid = False
        
        # Numeric range validations
        numeric_fields = [
            ("total_property_size", "Total Property Size"),
            ("current_space_needed", "Current Space Needed"),
            ("market_appreciation_rate", "Market Appreciation Rate"),
            ("purchase_price", "Purchase Price"),
            ("down_payment_percent", "Down Payment %"),
            ("interest_rate", "Interest Rate"),
            ("loan_term", "Loan Term"),
            ("property_tax_rate", "Property Tax Rate"),
            ("current_annual_rent", "Current Annual Rent"),
            ("rent_increase_rate", "Rent Increase Rate")
        ]
        
        for field_name, display_name in numeric_fields:
            value = inputs.get(field_name)
            if value is not None:
                field_result = self.validate_numeric_range(value, field_name, display_name)
                result.errors.extend(field_result.errors)
                result.warnings.extend(field_result.warnings)
                result.info.extend(field_result.info)
                if not field_result.is_valid:
                    result.is_valid = False
        
        # Text length validations
        text_fields = [
            ("project_name", "Project Name"),
            ("location", "Location"),
            ("analyst_name", "Analyst Name")
        ]
        
        for field_name, display_name in text_fields:
            value = inputs.get(field_name)
            if value is not None:
                field_result = self.validate_text_length(value, field_name, display_name)
                result.errors.extend(field_result.errors)
                if not field_result.is_valid:
                    result.is_valid = False
        
        # Cross-field validations
        space_result = self.validate_space_relationship(
            inputs.get("total_property_size"),
            inputs.get("current_space_needed")
        )
        result.errors.extend(space_result.errors)
        result.warnings.extend(space_result.warnings)
        result.info.extend(space_result.info)
        if not space_result.is_valid:
            result.is_valid = False
        
        loan_result = self.validate_loan_terms(
            inputs.get("purchase_price"),
            inputs.get("down_payment_percent"),
            inputs.get("interest_rate"),
            inputs.get("loan_term")
        )
        result.warnings.extend(loan_result.warnings)
        result.info.extend(loan_result.info)
        
        rental_result = self.validate_rental_parameters(
            inputs.get("current_annual_rent"),
            inputs.get("current_space_needed")
        )
        result.warnings.extend(rental_result.warnings)
        result.info.extend(rental_result.info)
        
        expansion_result = self.validate_expansion_parameters(
            inputs.get("total_property_size"),
            inputs.get("current_space_needed"),
            inputs.get("additional_space_needed"),
            inputs.get("future_expansion_year")
        )
        result.errors.extend(expansion_result.errors)
        result.warnings.extend(expansion_result.warnings)
        result.info.extend(expansion_result.info)
        if not expansion_result.is_valid:
            result.is_valid = False
        
        return result

def display_validation_messages(validation_result: ValidationResult):
    """Display validation messages in the UI"""
    # Display errors
    for error in validation_result.errors:
        st.error(f"❌ {error}")
    
    # Display warnings
    for warning in validation_result.warnings:
        st.warning(f"⚠️ {warning}")
    
    # Display info messages
    for info in validation_result.info:
        st.info(f"ℹ️ {info}")

def validate_and_display(inputs: Dict[str, Any], currency: str = "USD") -> bool:
    """Validate inputs and display messages, return True if valid"""
    validator = InputValidator(currency)
    result = validator.validate_all_inputs(inputs)
    display_validation_messages(result)
    return result.is_valid