"""
Input Forms System
Comprehensive input form system for all 30+ fields organized by section

Provides:
- Professional input forms with validation
- Organized sections with expandable groups  
- Smart defaults and helpful tooltips
- Real-time calculation updates
- Professional styling and UX
"""

import streamlit as st
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.defaults import (
    DEFAULT_VALUES, CURRENCY_OPTIONS, PROPERTY_TYPE_OPTIONS,
    get_field_description, get_expansion_year_options
)
from utils.formatting import (
    format_currency, format_number, format_percentage,
    format_input_placeholder, CURRENCY_SYMBOLS
)
from .validation import InputValidator, display_validation_messages
from .session_management import get_session_manager

def render_project_information_section():
    """Render Project Information input section"""
    st.markdown("### 📋 Project Information")
    st.markdown("*Basic project details and analysis parameters*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input(
            "Project Name*",
            key="project_name",
            placeholder=format_input_placeholder("project_name"),
            help=get_field_description("project_name"),
            max_chars=100
        )
        
        st.text_input(
            "Location/Address*", 
            key="location",
            placeholder=format_input_placeholder("location"),
            help=get_field_description("location"),
            max_chars=200
        )
    
    with col2:
        st.text_input(
            "Analyst Name*",
            key="analyst_name", 
            placeholder=format_input_placeholder("analyst_name"),
            help=get_field_description("analyst_name"),
            max_chars=50
        )
        
        st.date_input(
            "Analysis Date*",
            key="analysis_date",
            help=get_field_description("analysis_date")
        )
    
    # Currency selection (full width)
    def format_currency_option(currency_code):
        symbol = CURRENCY_SYMBOLS.get(currency_code, currency_code)
        return f"{currency_code} ({symbol})"
    
    st.selectbox(
        "Currency*",
        options=CURRENCY_OPTIONS,
        key="currency",
        help=get_field_description("currency"),
        format_func=format_currency_option
    )

def render_property_market_section():
    """Render Property & Market Information section"""  
    st.markdown("### 🏢 Property & Market Information")
    st.markdown("*Property specifications and market assumptions*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox(
            "Property Type*",
            options=PROPERTY_TYPE_OPTIONS,
            key="property_type",
            help=get_field_description("property_type")
        )
        
    with col2:
        # Calculate maximum space needed based on available property sizes
        ownership_size = st.session_state.get("ownership_property_size", 0) or 0
        rental_size = st.session_state.get("rental_property_size", 0) or 0
        max_available_space = max(ownership_size, rental_size, 20000000)  # 20,000 sq meters default
        
        st.number_input(
            "Current Space Needed (m²)*", 
            key="current_space_needed",
            min_value=500,
            max_value=max_available_space,
            step=100,
            format="%d",
            help=get_field_description("current_space_needed")
        )
        
        st.slider(
            "Market Appreciation Rate (%)*",
            key="market_appreciation_rate",
            min_value=0.0,
            max_value=15.0,
            step=0.1,
            format="%.1f%%",
            help=get_field_description("market_appreciation_rate")
        )

def render_purchase_parameters_section():
    """Render Purchase Parameters section"""
    st.markdown("### 💰 Purchase Parameters")
    st.markdown("*Financial parameters for property ownership scenario*")
    
    currency = st.session_state.get("currency", "USD")
    currency_symbol = CURRENCY_SYMBOLS.get(currency, currency)
    
    # Primary purchase parameters
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            f"Purchase Price ({currency})*",
            key="purchase_price",
            min_value=50000,
            max_value=100000000,
            step=10000,
            format="%d",
            help=get_field_description("purchase_price")
        )
        
        st.number_input(
            "Property Size (m²)*",
            key="ownership_property_size",
            min_value=1000,
            max_value=1000000,
            step=100,
            format="%d",
            help=get_field_description("ownership_property_size")
        )
        
        st.slider(
            "Down Payment (%)*",
            key="down_payment_percent", 
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            format="%.0f%%",
            help=get_field_description("down_payment_percent")
        )
        
        st.number_input(
            "Interest Rate (%)*",
            key="interest_rate",
            min_value=0.0,
            max_value=20.0,
            step=0.1,
            format="%.2f",
            help=get_field_description("interest_rate")
        )
    
    with col2:
        st.number_input(
            "Transaction Costs (%)",
            key="transaction_costs_percent",
            min_value=0.0,
            max_value=15.0,
            step=0.1,
            format="%.1f",
            help=get_field_description("transaction_costs_percent")
        )
        
        st.number_input(
            "Loan Term (years)*",
            key="loan_term",
            min_value=0,
            max_value=30,
            step=1,
            help=get_field_description("loan_term")
        )
        
        st.number_input(
            "Annual Maintenance (%)*",
            key="annual_maintenance_percent",
            min_value=0.0,
            max_value=10.0,
            step=0.1,
            format="%.1f",
            help=get_field_description("annual_maintenance_percent")
        )
    
    # Additional purchase parameters
    with st.expander("🔧 Additional Purchase Parameters", expanded=False):
        col3, col4 = st.columns(2)
        
        with col3:
            st.number_input(
                "Property Tax Rate (%)*",
                key="property_tax_rate",
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                format="%.2f",
                help=get_field_description("property_tax_rate")
            )
            
            st.number_input(
                f"Insurance Cost ({currency})*",
                key="insurance_cost",
                min_value=0,
                max_value=100000,
                step=500,
                help=get_field_description("insurance_cost")
            )
            
            st.slider(
                "Land Value (%)",
                key="land_value_percent",
                min_value=10.0,
                max_value=50.0,
                step=1.0,
                format="%.0f%%",
                help=get_field_description("land_value_percent")
            )
        
        with col4:
            st.number_input(
                f"Property Management ({currency})",
                key="property_management",
                min_value=0,
                max_value=100000,
                step=100,
                help=get_field_description("property_management")
            )
            
            st.number_input(
                f"Space Improvement Cost ({currency}/m²)",
                key="space_improvement_cost",
                min_value=0,
                max_value=1000,
                step=10,
                help=get_field_description("space_improvement_cost")
            )
            
            st.number_input(
                "Property Tax Escalation (%)*",
                key="property_tax_escalation_rate",
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                format="%.1f",
                help=get_field_description("property_tax_escalation_rate")
            )

def render_rental_parameters_section():
    """Render Rental Parameters section"""
    st.markdown("### 🏠 Rental Parameters")
    st.markdown("*Financial parameters for rental scenario*")
    
    currency = st.session_state.get("currency", "USD")
    currency_symbol = CURRENCY_SYMBOLS.get(currency, currency)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            f"Current Annual Rent ({currency})*",
            key="current_annual_rent",
            min_value=1000,
            max_value=10000000,
            step=1000,
            help=get_field_description("current_annual_rent")
        )
        
        st.number_input(
            "Property Size (m²)*",
            key="rental_property_size",
            min_value=1000,
            max_value=1000000,
            step=100,
            format="%d",
            help=get_field_description("rental_property_size")
        )
        
        st.slider(
            "Rent Increase Rate (%)*",
            key="rent_increase_rate", 
            min_value=0.0,
            max_value=15.0,
            step=0.1,
            format="%.1f%%",
            help=get_field_description("rent_increase_rate")
        )
        
        st.number_input(
            f"Moving Costs ({currency})",
            key="moving_costs",
            min_value=0,
            max_value=1000000,
            step=1000,
            help=get_field_description("moving_costs")
        )
    
    with col2:
        st.number_input(
            "Security Deposit (months)",
            key="security_deposit_months",
            min_value=0,
            max_value=12,
            step=1,
            help=get_field_description("security_deposit_months")
        )
        
        st.number_input(
            "Rental Commission (months)",
            key="rental_commission_months",
            min_value=0,
            max_value=6,
            step=1,
            help=get_field_description("rental_commission_months")
        )
        
        st.number_input(
            "Lease Break Penalty (months)",
            key="lease_break_penalty_months",
            min_value=0,
            max_value=24,
            step=1,
            help=get_field_description("lease_break_penalty_months")
        )
    
    # Display calculated rent per square meter
    current_rent = st.session_state.get("current_annual_rent", 0) or 0
    current_space = st.session_state.get("current_space_needed", 1) or 1
    rent_per_sqm = current_rent / current_space if current_space > 0 else 0
    
    if current_rent > 0 and current_space > 0:
        st.info(f"📊 **Calculated Rent per m²**: {currency_symbol}{rent_per_sqm:,.2f}")

def render_operational_parameters_section():
    """Render Operational Parameters section"""
    try:
        st.markdown("### ⚙️ Operational Parameters") 
        st.markdown("*Business growth and operational assumptions*")
        
        currency = st.session_state.get("currency", "USD")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input(
                "Analysis Period (years)*",
                key="analysis_period",
                min_value=1,
                max_value=100,
                step=1,
                help=get_field_description("analysis_period")
            )
            
            st.slider(
                "Growth Rate (%)*",
                key="growth_rate",
                min_value=-5.0,
                max_value=25.0,
                step=0.1,
                format="%.1f%%",
                help=get_field_description("growth_rate")
            )
            
            st.number_input(
                "Cost of Capital (%)*", 
                key="cost_of_capital",
                min_value=0.0,
                max_value=20.0,
                step=0.1,
                format="%.1f",
                help=get_field_description("cost_of_capital")
            )
        
        with col2:
            # Ensure analysis_period is a valid integer
            analysis_period = st.session_state.get("analysis_period", 25)
            if not isinstance(analysis_period, int) or analysis_period <= 0:
                analysis_period = 25
            
            # Generate expansion options safely
            try:
                expansion_options = get_expansion_year_options(analysis_period)
            except (TypeError, ValueError):
                expansion_options = ["Never", "Year 10", "Year 15", "Year 20"]
            
            current_selection = st.session_state.get("future_expansion_year", "Never")
            if current_selection not in expansion_options:
                current_selection = "Never"
            
            # Get safe index
            try:
                default_index = expansion_options.index(current_selection)
            except (ValueError, TypeError):
                default_index = 0
            
            st.selectbox(
                "Future Expansion Year",
                options=expansion_options,
                key="future_expansion_year",
                index=default_index,
                help=get_field_description("future_expansion_year")
            )
            
            st.number_input(
                "Additional Space Needed (m²)",
                key="additional_space_needed",
                min_value=0,
                max_value=100000,
                step=100,
                help=get_field_description("additional_space_needed")
            )
            
            st.number_input(
                "Inflation Rate (%)*",
                key="inflation_rate",
                min_value=0.0,
                max_value=20.0,
                step=0.1,
                format="%.1f",
                help=get_field_description("inflation_rate")
            )
        
        # Subletting parameters
        with st.expander("🏗️ Subletting & Advanced Parameters", expanded=False):
            col3, col4 = st.columns(2)
            
            with col3:
                st.checkbox(
                    "Subletting Potential*",
                    key="subletting_potential",
                    help=get_field_description("subletting_potential")
                )
                
                subletting_enabled = st.session_state.get("subletting_potential", False)
                
                st.number_input(
                    f"Subletting Rate ({currency}/m²)",
                    key="subletting_rate",
                    min_value=0,
                    max_value=1000,
                    step=1,
                    disabled=not subletting_enabled,
                    help=get_field_description("subletting_rate")
                )
                
                st.slider(
                    "Subletting Occupancy (%)",
                    key="subletting_occupancy",
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    format="%.0f%%",
                    disabled=not subletting_enabled,
                    help=get_field_description("subletting_occupancy")
                )
            
            with col4:
                st.number_input(
                    "Long-term CapEx Reserve (%)*",
                    key="longterm_capex_reserve",
                    min_value=0.0,
                    max_value=10.0,
                    step=0.1,
                    format="%.1f",
                    help=get_field_description("longterm_capex_reserve")
                )
                
                st.number_input(
                    "Property Upgrade Cycle (years)",
                    key="property_upgrade_cycle",
                    min_value=5,
                    max_value=50,
                    step=1,
                    help=get_field_description("property_upgrade_cycle")
                )
                
                st.number_input(
                    "Obsolescence Risk Factor (%)",
                    key="obsolescence_risk_factor",
                    min_value=0.0,
                    max_value=5.0,
                    step=0.1,
                    format="%.1f",
                    help=get_field_description("obsolescence_risk_factor")
                )
    except Exception as e:
        st.error(f"Error in operational parameters: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

def render_tax_accounting_section():
    """Render Tax & Accounting Parameters section"""
    st.markdown("### 📊 Tax & Accounting Parameters")
    st.markdown("*Tax implications and accounting assumptions*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Corporate Tax Rate (%)",
            key="corporate_tax_rate",
            min_value=0.0,
            max_value=50.0,
            step=0.1,
            format="%.1f",
            help=get_field_description("corporate_tax_rate")
        )
        
        st.number_input(
            "Depreciation Period (years)",
            key="depreciation_period",
            min_value=1,
            max_value=50,
            step=1,
            help=get_field_description("depreciation_period")
        )
    
    with col2:
        st.checkbox(
            "Interest Deductible",
            key="interest_deductible",
            help=get_field_description("interest_deductible")
        )
        
        st.checkbox(
            "Property Tax Deductible", 
            key="property_tax_deductible",
            help=get_field_description("property_tax_deductible")
        )
        
        st.checkbox(
            "Rent Deductible",
            key="rent_deductible", 
            help=get_field_description("rent_deductible")
        )

def render_input_summary():
    """Render a summary of key inputs"""
    st.markdown("### 📋 Input Summary")
    
    session_manager = get_session_manager()
    completion_percentage = session_manager.get_completion_percentage()
    
    # Progress indicator
    st.progress(completion_percentage / 100, text=f"Input Completion: {completion_percentage:.0f}%")
    
    # Key metrics summary
    col1, col2, col3, col4 = st.columns(4)
    
    currency = st.session_state.get("currency", "USD")
    purchase_price = st.session_state.get("purchase_price", 0) or 0
    annual_rent = st.session_state.get("current_annual_rent", 0) or 0
    ownership_space = st.session_state.get("ownership_property_size", 0) or 0
    rental_space = st.session_state.get("rental_property_size", 0) or 0
    analysis_period = st.session_state.get("analysis_period", 25)
    
    with col1:
        st.metric(
            "Purchase Price",
            format_currency(purchase_price, currency, include_cents=False)
        )
    
    with col2:
        st.metric(
            "Annual Rent", 
            format_currency(annual_rent, currency, include_cents=False)
        )
    
    with col3:
        st.metric(
            "Property Sizes",
            f"Own: {ownership_space:,.0f} m² | Rent: {rental_space:,.0f} m²"
        )
    
    with col4:
        st.metric(
            "Analysis Period",
            f"{analysis_period} years"
        )

def render_all_input_forms():
    """Render all input form sections with error handling"""
    
    try:
        # Initialize session state
        session_manager = get_session_manager()
        session_manager.update_calculated_fields()
        session_manager.check_section_completion()
        
        # Render input summary at the top
        render_input_summary()
        
        st.markdown("---")
        
        # Render all input sections with individual error handling
        try:
            with st.expander("📋 Project Information", expanded=True):
                render_project_information_section()
        except Exception as e:
            st.error(f"Error in Project Information: {str(e)}")
        
        try:
            with st.expander("🏢 Property & Market Information", expanded=True):
                render_property_market_section()
        except Exception as e:
            st.error(f"Error in Property & Market: {str(e)}")
        
        try:
            with st.expander("💰 Purchase Parameters", expanded=False):
                render_purchase_parameters_section()
        except Exception as e:
            st.error(f"Error in Purchase Parameters: {str(e)}")
        
        try:
            with st.expander("🏠 Rental Parameters", expanded=False):
                render_rental_parameters_section()
        except Exception as e:
            st.error(f"Error in Rental Parameters: {str(e)}")
        
        try:
            with st.expander("⚙️ Operational Parameters", expanded=False):
                render_operational_parameters_section()
        except Exception as e:
            import traceback
            st.error(f"Error in Operational Parameters: {str(e)}")
            st.code(traceback.format_exc())
        
        try:
            with st.expander("📊 Tax & Accounting Parameters", expanded=False):
                render_tax_accounting_section()
        except Exception as e:
            st.error(f"Error in Tax & Accounting: {str(e)}")
            
    except Exception as e:
        st.error(f"⚠️ **Initialization Error**: {str(e)}")
        st.info("🔄 **Please refresh the page to continue**")
        st.markdown("---")
        st.markdown("### 🚀 Getting Started")
        st.markdown("""
        This tool helps you analyze whether to rent or buy commercial real estate.
        
        **To get started:**
        1. Fill out the required input fields in the sidebar
        2. Review validation messages and fix any issues  
        3. Run the financial analysis once all inputs are complete
        
        **Note**: The interface is loading. Please refresh if you continue to see errors.
        """)
        return False
    
    # Validation section
    st.markdown("---")
    st.markdown("### ✅ Input Validation")
    
    # Run validation
    validator = InputValidator(st.session_state.get("currency", "USD"))
    
    # Collect all inputs for validation
    inputs = {field: st.session_state.get(field) for field in DEFAULT_VALUES.keys()}
    
    validation_result = validator.validate_all_inputs(inputs)
    display_validation_messages(validation_result)
    
    # Show analysis readiness status
    is_ready = session_manager.is_ready_for_analysis()
    
    if is_ready and validation_result.is_valid:
        st.success("✅ **Ready for Analysis** - All required inputs are complete and valid!")
    elif is_ready:
        st.warning("⚠️ **Input Issues Found** - Please review and correct validation errors above")
    else:
        st.info("ℹ️ **Complete Required Sections** - Fill out all required fields to enable analysis")
    
    return validation_result.is_valid and is_ready