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
    
    # Clear API update flag if scheduled from previous run
    if st.session_state.get('_clear_api_flag_on_next_run', False):
        st.session_state['_api_update_in_progress'] = False
        st.session_state['_clear_api_flag_on_next_run'] = False
    
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
        
        # Country selection with supported countries first
        supported_countries = [
            ("🇺🇸 United States", "usa"),
            ("🇧🇷 Brazil", "brazil"), 
            ("🇬🇧 United Kingdom", "uk"),
            ("🇨🇦 Canada", "canada"),
            ("🇦🇺 Australia", "australia"), 
            ("🇩🇪 Germany", "germany"),
            ("🇫🇷 France", "france"),
            ("🇳🇱 Netherlands", "netherlands"),
            ("🇯🇵 Japan", "japan"),
            ("🇸🇬 Singapore", "singapore"),
            ("🇵🇱 Poland", "poland"),
            ("🇮🇱 Israel", "israel"),
            ("🇷🇴 Romania", "romania"),
            ("🌍 Other", "other")
        ]
        
        selected_country = st.selectbox(
            "Country*",
            options=[display for display, code in supported_countries],
            key="country_selection",
            help="Select your country for market-specific data. Supported countries have real market data."
        )
        
        # Get the country code
        country_code = None
        for display, code in supported_countries:
            if display == selected_country:
                country_code = code
                break
        
        # If "Other" is selected, show text input
        if country_code == "other":
            other_country = st.text_input(
                "Enter Country Name",
                key="other_country_name",
                placeholder="e.g., Argentina, China, etc.",
                help="Enter the name of your country. Default values will be used.",
                max_chars=50
            )
            final_country = other_country.strip() if other_country else "Other"
            location_input = final_country
        else:
            # Use the selected supported country
            location_input = country_code
            final_country = selected_country.split(" ", 1)[1] if " " in selected_country else selected_country
        
        # Handle country changes for API updates
        if location_input and location_input.strip():
            _handle_country_change(location_input.strip())
            
        # Show country status feedback
        if location_input:
            _show_country_status(country_code, final_country)
    
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
        
        # Track previous market appreciation rate to detect user changes
        prev_appreciation = st.session_state.get('_prev_market_appreciation_rate', 
                                               st.session_state.get('market_appreciation_rate', 
                                                                   DEFAULT_VALUES.get('market_appreciation_rate', 3.0)))
        
        current_appreciation = st.slider(
            "Market Appreciation Rate (%)*",
            key="market_appreciation_rate",
            min_value=0.0,
            max_value=15.0,
            step=0.1,
            format="%.1f%%",
            help=get_field_description("market_appreciation_rate") + " (Updates automatically based on location, or adjust manually)"
        )
        
        # Only mark as user override if this is a real user interaction
        if current_appreciation != prev_appreciation:
            # Skip user override detection if we're loading country data
            loading_country_data = st.session_state.get('_api_update_in_progress', False)
            
            if not loading_country_data:
                mark_field_as_user_modified('market_appreciation_rate', current_appreciation)
            
        st.session_state['_prev_market_appreciation_rate'] = current_appreciation
        
        # Show API update indicator
        _show_api_indicator('market_appreciation_rate', current_appreciation)

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
        
        # Track previous interest rate to detect user changes
        prev_rate = st.session_state.get('_prev_interest_rate', st.session_state.get('interest_rate', DEFAULT_VALUES.get('interest_rate', 7.0)))
        
        current_rate = st.number_input(
            "Interest Rate (%)*",
            key="interest_rate",
            min_value=0.0,
            max_value=20.0,
            step=0.1,
            format="%.2f",
            help=get_field_description("interest_rate") + " (Updates automatically based on location, or enter your own rate)"
        )
        
        # Only mark as user override if this is a real user interaction
        if current_rate != prev_rate:
            # Skip user override detection if we're loading country data
            loading_country_data = st.session_state.get('_api_update_in_progress', False)
            
            if not loading_country_data:
                mark_field_as_user_modified('interest_rate', current_rate)
            
        st.session_state['_prev_interest_rate'] = current_rate
        
        # Show API update indicator
        _show_api_indicator('interest_rate', current_rate)
    
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
            # Track previous property tax rate to detect user changes
            prev_property_tax = st.session_state.get('_prev_property_tax_rate',
                                                   st.session_state.get('property_tax_rate',
                                                                       DEFAULT_VALUES.get('property_tax_rate', 1.2)))
            
            current_property_tax = st.number_input(
                "Property Tax Rate (%)*",
                key="property_tax_rate",
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                format="%.2f",
                help=get_field_description("property_tax_rate") + " (Updates automatically based on location, or enter your own rate)"
            )
            
            # Only mark as user override if this is a real user interaction
            if current_property_tax != prev_property_tax:
                # Skip user override detection if we're loading country data
                loading_country_data = st.session_state.get('_api_update_in_progress', False)
                
                if not loading_country_data:
                    mark_field_as_user_modified('property_tax_rate', current_property_tax)
                
            st.session_state['_prev_property_tax_rate'] = current_property_tax
            
            # Show API update indicator
            _show_api_indicator('property_tax_rate', current_property_tax)
            
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
                f"Space Improvement Cost ({currency})",
                key="space_improvement_cost",
                min_value=0,
                max_value=1000000,
                step=1000,
                format="%d",
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
        
        # Track previous rent increase rate to detect user changes
        prev_rent_increase = st.session_state.get('_prev_rent_increase_rate',
                                                st.session_state.get('rent_increase_rate',
                                                                   DEFAULT_VALUES.get('rent_increase_rate', 3.0)))
        
        current_rent_increase = st.slider(
            "Rent Increase Rate (%)*",
            key="rent_increase_rate", 
            min_value=0.0,
            max_value=15.0,
            step=0.1,
            format="%.1f%%",
            help=get_field_description("rent_increase_rate") + " (Updates automatically based on location, or adjust manually)"
        )
        
        # Only mark as user override if this is a real user interaction
        if current_rent_increase != prev_rent_increase:
            # Skip user override detection if we're loading country data
            loading_country_data = st.session_state.get('_api_update_in_progress', False)
            
            if not loading_country_data:
                mark_field_as_user_modified('rent_increase_rate', current_rent_increase)
            
        st.session_state['_prev_rent_increase_rate'] = current_rent_increase
        
        # Show API update indicator
        _show_api_indicator('rent_increase_rate', current_rent_increase)
        
        st.number_input(
            f"Moving Costs ({currency})",
            key="moving_costs",
            min_value=0,
            max_value=1000000,
            step=1000,
            help=get_field_description("moving_costs")
        )
    
    with col2:
        # Moving costs are now implemented in NPV calculation
        pass
    
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
            # Clear any corrupted session state for future_expansion_year
            if "future_expansion_year" in st.session_state:
                current_val = st.session_state["future_expansion_year"]
                if not isinstance(current_val, str):
                    del st.session_state["future_expansion_year"]
            
            # Ensure analysis_period is a valid integer and reasonable size
            analysis_period = st.session_state.get("analysis_period", 25)
            try:
                if not isinstance(analysis_period, (int, float)) or analysis_period <= 0:
                    analysis_period = 25
                analysis_period = int(analysis_period)
                # Cap to prevent memory issues
                if analysis_period > 50:
                    analysis_period = 50
            except (TypeError, ValueError, OverflowError):
                analysis_period = 25
            
            # Generate expansion options safely
            try:
                expansion_options = get_expansion_year_options(analysis_period)
                # Ensure we have valid options
                if not expansion_options or not isinstance(expansion_options, list):
                    expansion_options = ["Never", "Year 10", "Year 15", "Year 20"]
            except Exception:
                expansion_options = ["Never", "Year 10", "Year 15", "Year 20"]
            
            # Ensure current selection is valid and reset if corrupted
            current_selection = st.session_state.get("future_expansion_year", "Never")
            if not isinstance(current_selection, str) or current_selection not in expansion_options:
                current_selection = "Never"
                # Reset the session state to a safe value
                st.session_state["future_expansion_year"] = "Never"
            
            # Get safe index
            try:
                default_index = expansion_options.index(current_selection) if current_selection in expansion_options else 0
            except (ValueError, TypeError):
                default_index = 0
            
            # Ensure index is valid
            if default_index >= len(expansion_options):
                default_index = 0
            
            # Extra safety checks before creating selectbox
            try:
                # Ensure all options are strings
                expansion_options = [str(option) for option in expansion_options]
                
                # Ensure index is an integer and within bounds
                default_index = int(default_index) if isinstance(default_index, (int, float)) else 0
                default_index = max(0, min(default_index, len(expansion_options) - 1))
                
                # Get help text safely
                try:
                    help_text = get_field_description("future_expansion_year")
                except Exception:
                    help_text = "Year when future expansion might be needed"
                
                st.selectbox(
                    "Future Expansion Year",
                    options=expansion_options,
                    key="future_expansion_year",
                    index=default_index,
                    help=help_text
                )
            except Exception as e:
                # If selectbox fails, show a simple text input as fallback
                st.text_input(
                    "Future Expansion Year",
                    value="Never",
                    key="future_expansion_year_fallback",
                    help="Selectbox failed, using text input as fallback"
                )
                # Store the fallback value in the main session state key
                st.session_state["future_expansion_year"] = st.session_state.get("future_expansion_year_fallback", "Never")
            
            st.number_input(
                "Additional Space Needed (m²)",
                key="additional_space_needed",
                min_value=0,
                max_value=100000,
                step=100,
                help=get_field_description("additional_space_needed")
            )
            
            # Track previous inflation rate to detect user changes
            prev_inflation = st.session_state.get('_prev_inflation_rate',
                                                st.session_state.get('inflation_rate',
                                                                    DEFAULT_VALUES.get('inflation_rate', 3.0)))
            
            current_inflation = st.number_input(
                "Inflation Rate (%)*",
                key="inflation_rate",
                min_value=0.0,
                max_value=20.0,
                step=0.1,
                format="%.1f",
                help=get_field_description("inflation_rate") + " (Updates automatically based on economic data, or enter your own rate)"
            )
            
            # Only mark as user override if this is a real user interaction
            if current_inflation != prev_inflation:
                # Skip user override detection if we're loading country data
                loading_country_data = st.session_state.get('_api_update_in_progress', False)
                
                if not loading_country_data:
                    mark_field_as_user_modified('inflation_rate', current_inflation)
                
            st.session_state['_prev_inflation_rate'] = current_inflation
            
            # Show API update indicator
            _show_api_indicator('inflation_rate', current_inflation)
        
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
                
                # Calculate max subletting space based on ownership property size
                ownership_size = st.session_state.get("ownership_property_size", 0) or 0
                current_space = st.session_state.get("current_space_needed", 0) or 0
                max_subletting_space = max(0, ownership_size - current_space) if ownership_size > current_space else 10000
                
                st.number_input(
                    "Space to Sublet (m²)",
                    key="subletting_space_sqm",
                    min_value=0,
                    max_value=int(max_subletting_space) if max_subletting_space > 0 else 10000,
                    step=100,
                    format="%d",
                    disabled=not subletting_enabled,
                    help="Enter the actual square meters of space you plan to sublet to other tenants"
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
        # Track previous corporate tax rate to detect user changes
        prev_corporate_tax = st.session_state.get('_prev_corporate_tax_rate',
                                               st.session_state.get('corporate_tax_rate',
                                                                   DEFAULT_VALUES.get('corporate_tax_rate', 25.0)))
        
        current_corporate_tax = st.number_input(
            "Corporate Tax Rate (%)",
            key="corporate_tax_rate",
            min_value=0.0,
            max_value=50.0,
            step=0.1,
            format="%.1f",
            help=get_field_description("corporate_tax_rate")
        )
        
        # Detect user changes and mark as user override
        if current_corporate_tax != prev_corporate_tax:
            loading_country_data = st.session_state.get('_api_update_in_progress', False)
            
            if not loading_country_data:
                mark_field_as_user_modified('corporate_tax_rate', current_corporate_tax)
            
        st.session_state['_prev_corporate_tax_rate'] = current_corporate_tax
        
        # Show API update indicator for corporate tax rate
        _show_api_indicator('corporate_tax_rate', current_corporate_tax)
        
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
        if purchase_price >= 1000000:
            # Use abbreviated format for values >= 1M
            price_display = f"{CURRENCY_SYMBOLS.get(currency, currency)}{purchase_price/1000000:.1f}M"
        elif purchase_price >= 10000:
            # Use K format for values >= 10K 
            price_display = f"{CURRENCY_SYMBOLS.get(currency, currency)}{purchase_price/1000:.0f}K"
        else:
            price_display = format_currency(purchase_price, currency, include_cents=False)
        
        st.metric("Purchase Price", price_display)
    
    with col2:
        if annual_rent >= 1000000:
            # Use abbreviated format for values >= 1M
            rent_display = f"{CURRENCY_SYMBOLS.get(currency, currency)}{annual_rent/1000000:.1f}M"
        elif annual_rent >= 10000:
            # Use K format for values >= 10K
            rent_display = f"{CURRENCY_SYMBOLS.get(currency, currency)}{annual_rent/1000:.0f}K"
        else:
            rent_display = format_currency(annual_rent, currency, include_cents=False)
        
        st.metric("Annual Rent", rent_display)
    
    with col3:
        # Use very compact format to avoid truncation
        if ownership_space >= 1000000:
            own_display = f"{ownership_space/1000000:.1f}M"
        elif ownership_space >= 1000:
            own_display = f"{ownership_space/1000:.0f}K" 
        else:
            own_display = f"{ownership_space:.0f}"
            
        if rental_space >= 1000000:
            rent_display = f"{rental_space/1000000:.1f}M"
        elif rental_space >= 1000:
            rent_display = f"{rental_space/1000:.0f}K"
        else:
            rent_display = f"{rental_space:.0f}"
        
        st.metric(
            "Property Sizes",
            f"{own_display} | {rent_display} m²"
        )
    
    with col4:
        st.metric(
            "Analysis Period",
            f"{analysis_period}y"
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
    
    # Run validation silently (no UI display)
    validator = InputValidator(st.session_state.get("currency", "USD"))
    
    # Collect all inputs for validation
    inputs = {field: st.session_state.get(field) for field in DEFAULT_VALUES.keys()}
    
    validation_result = validator.validate_all_inputs(inputs)
    
    # Force check completion status right before validation
    session_manager.check_section_completion()
    
    # Manual override for project completion if fields are valid
    if (st.session_state.get("project_name") and 
        st.session_state.get("country_selection") and 
        st.session_state.get("analyst_name")):
        st.session_state["project_info_complete"] = True
    
    # Show analysis readiness status
    is_ready = session_manager.is_ready_for_analysis()
    
    if is_ready and validation_result.is_valid:
        st.success("✅ **Ready for Analysis** - All required inputs are complete and valid!")
    elif is_ready:
        st.warning("⚠️ **Input Issues Found** - Please review and correct validation errors above")
    else:
        st.info("ℹ️ **Complete Required Sections** - Fill out all required fields to enable analysis")
    
    return validation_result.is_valid and is_ready


def _handle_country_change(country: str):
    """
    Handle country changes to trigger API updates for market data
    Simplified approach: Load API/static data, user can override with proper tooltips
    """
    try:
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        from data.data_priority_manager import get_data_priority_manager
        from data.international_data import get_international_provider
        
        # Check if country actually changed
        previous_country = st.session_state.get('_last_selected_country', '')
        if country == previous_country:
            return
            
        # Track the previous country for change detection
        st.session_state['_prev_selected_country'] = previous_country
            
        # Clear any existing data for fresh start
        priority_manager = get_data_priority_manager()
        priority_manager.clear_api_data()
        priority_manager.clear_user_overrides()  # Clear user overrides too
        
        # Mark that we're updating from API
        st.session_state['_api_update_in_progress'] = True
        
        # Load country data if supported
        international_provider = get_international_provider()
        
        updated_fields = []
        
        if country in ['usa', 'united states']:
            # Handle USA - can use FRED API
            try:
                from data.interest_rate_feeds import create_interest_rate_feeds
                import asyncio
                
                # Get US rates
                rate_feeds = create_interest_rate_feeds()
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    asyncio.set_event_loop(asyncio.new_event_loop())
                    loop = asyncio.get_event_loop()
                
                if not loop.is_running():
                    rates = loop.run_until_complete(rate_feeds.get_current_rates(['30_year_fixed']))
                    loop.run_until_complete(rate_feeds.close())
                    
                    if '30_year_fixed' in rates:
                        st.session_state['interest_rate'] = rates['30_year_fixed']
                        priority_manager.set_api_data('interest_rate', rates['30_year_fixed'], 'fred_api_usa')
                        updated_fields.append(f"Interest Rate: {rates['30_year_fixed']}%")
                
                # Add US market estimates (could be enhanced with real APIs later)
                us_estimates = {
                    'market_appreciation_rate': 3.5,  # US national average
                    'rent_increase_rate': 3.2,       # US national average  
                    'property_tax_rate': 1.1,        # US national average
                    'inflation_rate': 3.0            # Current US inflation target
                }
                
                for field_name, value in us_estimates.items():
                    st.session_state[field_name] = value
                    priority_manager.set_api_data(
                        field_name, 
                        value,
                        'us_market_estimates',
                        metadata={'country': 'USA', 'data_date': '2024-08-14', 'source': 'US_estimates'}
                    )
                    display_name = field_name.replace('_', ' ').title()
                    updated_fields.append(f"{display_name}: {value}%")
                        
            except Exception as e:
                # Fallback to US defaults
                st.session_state['interest_rate'] = 7.0
                updated_fields.append("Interest Rate: 7.0% (US default)")
                
        else:
            # Check if it's a supported international country
            country_data = international_provider.get_international_estimates(country)
            
            if country_data['estimates']:
                # Has API/static data
                estimates = country_data['estimates']
                metadata = country_data['metadata']
                
                # Update all fields with API data
                field_mapping = {
                    'interest_rate': 'interest_rate',
                    'market_appreciation_rate': 'market_appreciation_rate',
                    'rent_increase_rate': 'rent_increase_rate', 
                    'property_tax_rate': 'property_tax_rate',
                    'inflation_rate': 'inflation_rate',
                    'corporate_tax_rate': 'corporate_tax_rate'
                }
                
                for field_name, session_key in field_mapping.items():
                    if field_name in estimates:
                        value = estimates[field_name]
                        st.session_state[session_key] = value
                        priority_manager.set_api_data(
                            session_key, 
                            value,
                            f"international_data_{country}",
                            metadata=metadata
                        )
                        display_name = field_name.replace('_', ' ').title()
                        updated_fields.append(f"{display_name}: {value}{'%' if 'rate' in field_name else ''}")
            
            # If no data found (unsupported country), fields will use defaults
        
        # Show update notification
        if updated_fields:
            st.info(f"🌐 Updated {len(updated_fields)} field(s) for {country}: {', '.join(updated_fields)}")
        else:
            st.info(f"🌍 Using default values for {country}")
            
        # Set the country after updates
        st.session_state['_last_selected_country'] = country
        
        # Clear the API update flag after processing
        # Use a callback mechanism to clear it after this run
        def clear_api_flag():
            st.session_state['_api_update_in_progress'] = False
        
        # Schedule clearing for next interaction (streamlit will rerun)
        st.session_state['_clear_api_flag_on_next_run'] = True
            
    except Exception as e:
        # Don't break the UI if country handling fails
        st.session_state['_api_update_in_progress'] = False
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Country change handler error: {e}")
        pass


def _show_country_status(country_code: str, final_country: str):
    """Show status message for the selected country"""
    if country_code in ['usa']:
        st.info(f"🇺🇸 {final_country} - Live FRED API data available")
    elif country_code in ['brazil']:
        st.success(f"🇧🇷 {final_country} - Live BCB API + static data available")
    elif country_code in ['uk', 'canada', 'australia', 'germany', 'france', 'netherlands', 'japan', 'singapore', 'poland', 'israel']:
        st.success(f"✅ {final_country} - Static market data available")
    elif country_code == 'other':
        if final_country and final_country != "Other":
            st.warning(f"🌍 {final_country} - Using default values (no specific market data)")
        else:
            st.info("Select a country or enter 'Other' country name")
    else:
        st.warning(f"🌍 {final_country} - Using default values")


def mark_field_as_user_modified(field_name: str, value: Any):
    """
    Mark a field as user-modified to prevent API overwrites
    """
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        from data.address_api_handler import get_address_api_handler
        
        address_handler = get_address_api_handler()
        address_handler.mark_field_as_user_modified(field_name, value)
        
        # Mark in session state too
        st.session_state[f'_{field_name}_user_modified'] = True
        
    except Exception as e:
        # Don't break UI if this fails
        pass


def _show_api_indicator(field_name: str, current_value: Any):
    """
    Show visual indicator for field data source (API vs User Override vs None)
    """
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        
        from data.data_priority_manager import get_data_priority_manager
        
        priority_manager = get_data_priority_manager()
        
        # Check field status in priority manager
        try:
            field_data = priority_manager.get_value(field_name)
            is_user_modified = field_data.get('user_modified', False)
            priority_level = field_data.get('priority_level', '')
            source = field_data.get('source', '')
            
            # Simple logic: User Override > API Data > Default/None
            if is_user_modified:
                # Show ORANGE user override indicator
                st.markdown(
                    f'<div style="background-color: #FFF3E0; border-left: 4px solid #FF9800; padding: 8px; margin: 4px 0; border-radius: 4px;">'
                    f'<small><strong>✏️ User Override:</strong> Your custom value is protected from API updates</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            elif priority_level == 'api_data':
                # Show BLUE API indicator
                source_display = _format_api_source(source)
                
                # Check for metadata (data date)
                metadata = field_data.get('metadata', {})
                data_date = metadata.get('data_date', '')
                live_rate_used = metadata.get('live_rate_used', False)
                
                # Create additional info for static vs live data
                extra_info = ""
                if live_rate_used:
                    extra_info = f" • 🔴 LIVE API"
                elif data_date:
                    extra_info = f" • 📅 Data from {data_date}"
                elif 'international' in source.lower():
                    # For international data, try to extract date from source or use default
                    if '_data_' in source.lower():
                        extra_info = f" • 📅 Data from 2024-08-14"
                    else:
                        extra_info = f" • 📊 Static data"
                
                st.markdown(
                    f'<div style="background-color: #E3F2FD; border-left: 4px solid #2196F3; padding: 8px; margin: 4px 0; border-radius: 4px;">'
                    f'<small><strong>🌐 API Updated:</strong> {source_display} • Value: {current_value}{"%" if "rate" in field_name else ""}{extra_info}</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            # If priority_level is 'default_data' or 'fallback', show no indicator (clean interface)
                
        except ValueError:
            # Field not found in priority manager - no indicator
            pass
            
    except Exception as e:
        # Don't break UI if indicator fails
        pass


def _format_api_source(source: str) -> str:
    """Format API source for display"""
    source_mapping = {
        'fred_api': 'Federal Reserve (FRED)',
        'location_estimate': 'Location-Based Data',
        'market_api': 'Market Data API',
        'international_data': 'Central Bank Data',
        'system_default': 'Default Value'
    }
    
    for key, display in source_mapping.items():
        if key in source.lower():
            return display
    
    # Extract country info if present, but clean up dates
    if '_for_' in source:
        parts = source.split('_for_')
        if len(parts) > 1:
            location = parts[1].replace('_', ' ')
            # Remove date patterns like (2024-08-14) from location
            import re
            location = re.sub(r'\([^)]*\d{4}-\d{2}-\d{2}[^)]*\)', '', location).strip()
            location = location.title()
            api_type = parts[0].replace('_', ' ').title()
            return f"{api_type} ({location})"
    
    # Clean up any date patterns from the source name
    import re
    clean_source = re.sub(r'\([^)]*\d{4}-\d{2}-\d{2}[^)]*\)', '', source)
    return clean_source.replace('_', ' ').title()