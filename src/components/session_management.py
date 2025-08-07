"""
Session State Management
Handles persistent state across user interactions

Provides:
- Session state initialization with defaults
- Input state persistence
- Section completion tracking
- State reset and export functionality
"""

import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.defaults import DEFAULT_VALUES, get_default_value

class SessionManager:
    """Manages session state for the Real Estate Decision Tool"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state with default values"""
        # Initialize input values with defaults
        for field_name, default_value in DEFAULT_VALUES.items():
            if field_name not in st.session_state:
                st.session_state[field_name] = default_value
        
        # Initialize section completion tracking
        section_completion_keys = [
            "project_info_complete",
            "property_market_complete",
            "purchase_params_complete",
            "rental_params_complete", 
            "operational_params_complete",
            "tax_accounting_complete"
        ]
        
        for key in section_completion_keys:
            if key not in st.session_state:
                st.session_state[key] = False
        
        # Initialize calculated fields
        calculated_fields = [
            "transaction_costs_amount",
            "security_deposit_amount",
            "rental_commission_amount",
            "lease_break_penalty_amount",
            "rent_per_sqm",
            "annual_maintenance_amount"
        ]
        
        for field in calculated_fields:
            if field not in st.session_state:
                st.session_state[field] = 0
        
        # Initialize UI state
        ui_state_keys = [
            "validation_errors",
            "show_advanced_options",
            "current_tab",
            "inputs_changed"
        ]
        
        for key in ui_state_keys:
            if key not in st.session_state:
                if key == "validation_errors":
                    st.session_state[key] = []
                elif key == "show_advanced_options":
                    st.session_state[key] = False
                elif key == "current_tab":
                    st.session_state[key] = "dashboard"
                elif key == "inputs_changed":
                    st.session_state[key] = False
    
    def update_calculated_fields(self):
        """Update calculated fields based on current inputs"""
        # Transaction costs amount
        purchase_price = st.session_state.get("purchase_price", 0) or 0
        transaction_costs_percent = st.session_state.get("transaction_costs_percent", 5.0)
        st.session_state["transaction_costs_amount"] = purchase_price * (transaction_costs_percent / 100)
        
        # Annual maintenance amount
        annual_maintenance_percent = st.session_state.get("annual_maintenance_percent", 2.0)
        st.session_state["annual_maintenance_amount"] = purchase_price * (annual_maintenance_percent / 100)
        
        # Rental-related amounts
        current_annual_rent = st.session_state.get("current_annual_rent", 0) or 0
        
        # Security deposit
        security_deposit_months = st.session_state.get("security_deposit_months", 2)
        st.session_state["security_deposit_amount"] = (current_annual_rent / 12) * security_deposit_months
        
        # Rental commission
        rental_commission_months = st.session_state.get("rental_commission_months", 1)
        st.session_state["rental_commission_amount"] = (current_annual_rent / 12) * rental_commission_months
        
        # Lease break penalty
        lease_break_penalty_months = st.session_state.get("lease_break_penalty_months", 6)
        st.session_state["lease_break_penalty_amount"] = (current_annual_rent / 12) * lease_break_penalty_months
        
        # Rent per square meter
        current_space_needed = st.session_state.get("current_space_needed", 1) or 1
        st.session_state["rent_per_sqm"] = current_annual_rent / current_space_needed
    
    def check_section_completion(self):
        """Check and update section completion status"""
        # Project Information section
        project_fields = ["project_name", "location", "analyst_name"]
        st.session_state["project_info_complete"] = all(
            st.session_state.get(field) not in [None, "", 0] 
            for field in project_fields
        )
        
        # Property & Market section
        property_fields = ["total_property_size", "current_space_needed"]
        st.session_state["property_market_complete"] = all(
            st.session_state.get(field) not in [None, "", 0]
            for field in property_fields
        )
        
        # Purchase Parameters section
        purchase_fields = ["purchase_price"]
        st.session_state["purchase_params_complete"] = all(
            st.session_state.get(field) not in [None, "", 0]
            for field in purchase_fields
        )
        
        # Rental Parameters section
        rental_fields = ["current_annual_rent"]
        st.session_state["rental_params_complete"] = all(
            st.session_state.get(field) not in [None, "", 0]
            for field in rental_fields
        )
        
        # Operational Parameters section (all have defaults, so always complete)
        st.session_state["operational_params_complete"] = True
        
        # Tax & Accounting section (all have defaults, so always complete)
        st.session_state["tax_accounting_complete"] = True
    
    def get_completion_percentage(self) -> float:
        """Calculate overall completion percentage"""
        completion_keys = [
            "project_info_complete",
            "property_market_complete", 
            "purchase_params_complete",
            "rental_params_complete",
            "operational_params_complete",
            "tax_accounting_complete"
        ]
        
        completed_sections = sum(
            1 for key in completion_keys 
            if st.session_state.get(key, False)
        )
        
        return (completed_sections / len(completion_keys)) * 100
    
    def is_ready_for_analysis(self) -> bool:
        """Check if all required inputs are complete for analysis"""
        required_sections = [
            "project_info_complete",
            "property_market_complete",
            "purchase_params_complete", 
            "rental_params_complete"
        ]
        
        return all(st.session_state.get(key, False) for key in required_sections)
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export current session data for saving/sharing"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "inputs": {},
            "completion_status": {}
        }
        
        # Export all input fields
        for field_name in DEFAULT_VALUES.keys():
            value = st.session_state.get(field_name)
            # Convert datetime/date objects to strings for JSON serialization
            if isinstance(value, (datetime, st._typing.Date)):
                value = value.isoformat()
            export_data["inputs"][field_name] = value
        
        # Export completion status
        completion_keys = [
            "project_info_complete", "property_market_complete",
            "purchase_params_complete", "rental_params_complete",
            "operational_params_complete", "tax_accounting_complete"
        ]
        
        for key in completion_keys:
            export_data["completion_status"][key] = st.session_state.get(key, False)
        
        return export_data
    
    def import_session_data(self, data: Dict[str, Any]) -> bool:
        """Import session data from saved state"""
        try:
            # Import input fields
            if "inputs" in data:
                for field_name, value in data["inputs"].items():
                    if field_name in DEFAULT_VALUES:
                        # Handle date string conversion
                        if field_name == "analysis_date" and isinstance(value, str):
                            try:
                                st.session_state[field_name] = datetime.fromisoformat(value).date()
                            except:
                                st.session_state[field_name] = get_default_value(field_name)
                        else:
                            st.session_state[field_name] = value
            
            # Import completion status
            if "completion_status" in data:
                for key, value in data["completion_status"].items():
                    st.session_state[key] = value
            
            # Update calculated fields
            self.update_calculated_fields()
            return True
            
        except Exception as e:
            st.error(f"Error importing session data: {str(e)}")
            return False
    
    def reset_session(self):
        """Reset session to default state"""
        # Clear all input fields
        for field_name in DEFAULT_VALUES.keys():
            st.session_state[field_name] = get_default_value(field_name)
        
        # Reset completion tracking
        completion_keys = [
            "project_info_complete", "property_market_complete",
            "purchase_params_complete", "rental_params_complete", 
            "operational_params_complete", "tax_accounting_complete"
        ]
        
        for key in completion_keys:
            st.session_state[key] = False
        
        # Reset UI state
        st.session_state["validation_errors"] = []
        st.session_state["show_advanced_options"] = False
        st.session_state["current_tab"] = "dashboard"
        st.session_state["inputs_changed"] = False
        
        # Update calculated fields
        self.update_calculated_fields()
    
    def get_input_summary(self) -> Dict[str, Any]:
        """Get a summary of all current inputs for display"""
        summary = {
            "Project Information": {
                "Project Name": st.session_state.get("project_name"),
                "Location": st.session_state.get("location"),
                "Analyst": st.session_state.get("analyst_name"),
                "Analysis Date": st.session_state.get("analysis_date"),
                "Currency": st.session_state.get("currency")
            },
            "Property Details": {
                "Property Type": st.session_state.get("property_type"),
                "Total Size": f"{st.session_state.get('total_property_size', 0):,.0f} m²",
                "Current Need": f"{st.session_state.get('current_space_needed', 0):,.0f} m²",
                "Market Appreciation": f"{st.session_state.get('market_appreciation_rate', 0):.1f}%"
            },
            "Financial Parameters": {
                "Purchase Price": st.session_state.get("purchase_price"),
                "Down Payment": f"{st.session_state.get('down_payment_percent', 0):.1f}%",
                "Interest Rate": f"{st.session_state.get('interest_rate', 0):.1f}%",
                "Annual Rent": st.session_state.get("current_annual_rent"),
                "Rent per m²": f"{st.session_state.get('rent_per_sqm', 0):.2f}"
            },
            "Analysis Settings": {
                "Analysis Period": f"{st.session_state.get('analysis_period', 25)} years",
                "Cost of Capital": f"{st.session_state.get('cost_of_capital', 8):.1f}%",
                "Growth Rate": f"{st.session_state.get('growth_rate', 5):.1f}%"
            }
        }
        
        return summary

# Global session manager instance
@st.cache_resource
def get_session_manager():
    """Get singleton session manager instance"""
    return SessionManager()

def initialize_session():
    """Initialize session state - call this at app startup"""
    session_manager = get_session_manager()
    session_manager.initialize_session_state()
    return session_manager