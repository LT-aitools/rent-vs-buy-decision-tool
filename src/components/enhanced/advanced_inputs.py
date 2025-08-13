"""
Enhanced Advanced Input Components
Week 4 UX Enhancement - Smart input validation and user guidance

Features:
- Smart real-time validation with contextual feedback
- Progressive disclosure for complex options
- Adaptive input ranges based on context
- Accessibility-compliant ARIA labels and descriptions
- Mobile-responsive design patterns
"""

import streamlit as st
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, date
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.interfaces import UIComponent, ValidationResult, ValidationStatus, UIState, GuidanceContext
from utils.defaults import DEFAULT_VALUES, CURRENCY_OPTIONS, PROPERTY_TYPE_OPTIONS
from utils.formatting import format_currency, format_percentage, CURRENCY_SYMBOLS
from components.validation import InputValidator


@dataclass
class SmartInputConfig:
    """Configuration for smart input components"""
    field_name: str
    label: str
    input_type: str  # 'number', 'slider', 'selectbox', 'text', 'date'
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    format_string: Optional[str] = None
    help_text: str = ""
    validation_rules: List[str] = None
    adaptive_range: bool = False
    contextual_guidance: bool = True
    accessibility_label: str = ""


class AdvancedInputComponent(UIComponent):
    """Enhanced input component with smart validation and guidance"""
    
    def __init__(self):
        self.validator = InputValidator("USD")  # Default currency, updated dynamically
        self.guidance_cache = {}
        
    def render(self, data: Any, state: UIState) -> None:
        """Render advanced input components with error handling"""
        try:
            from .enhanced_security import ErrorHandler
            error_handler = ErrorHandler("advanced_inputs")
            
            # Safely update validator currency
            def update_currency():
                current_currency = state.input_values.get("currency", "USD")
                self.validator.currency = current_currency
                return True
            
            error_handler.safe_execute(update_currency, fallback=True)
            
            # Render based on mobile mode with error handling
            if state.mobile_mode:
                error_handler.safe_execute(
                    self._render_mobile_layout, 
                    data, state,
                    fallback=None
                )
            else:
                error_handler.safe_execute(
                    self._render_desktop_layout, 
                    data, state,
                    fallback=None
                )
                
        except Exception as e:
            st.error(f"Error rendering input components: {str(e)}")
            # Fallback to basic form rendering
            st.markdown("### Basic Input Form")
            st.text_input("Project Name", key="project_name_fallback")
            st.number_input("Purchase Price", key="purchase_price_fallback")
    
    def _render_desktop_layout(self, data: Any, state: UIState) -> None:
        """Render desktop-optimized layout"""
        # Enhanced project information section
        self._render_smart_project_section(state)
        
        # Advanced property parameters with adaptive ranges
        self._render_adaptive_property_section(state)
        
        # Financial parameters with smart validation
        self._render_smart_financial_section(state)
        
        # Operational parameters with progressive disclosure
        self._render_progressive_operational_section(state)
    
    def _render_mobile_layout(self, data: Any, state: UIState) -> None:
        """Render mobile-optimized layout"""
        st.markdown("### 📱 Mobile-Optimized Input")
        
        # Single column layout for mobile
        self._render_mobile_smart_inputs(state)
    
    def _render_smart_project_section(self, state: UIState) -> None:
        """Render project section with smart validation"""
        st.markdown("### 📋 Project Information")
        st.markdown("*Enhanced with real-time validation and guidance*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Smart project name input with validation
            project_name = self._render_smart_text_input(
                SmartInputConfig(
                    field_name="project_name",
                    label="Project Name",
                    input_type="text",
                    help_text="Enter a descriptive name for your analysis project",
                    validation_rules=["required", "max_length_100"],
                    accessibility_label="Project name for the real estate analysis"
                ),
                state
            )
            
            # Location input with enhanced validation
            location = self._render_smart_text_input(
                SmartInputConfig(
                    field_name="location",
                    label="Location/Address",
                    input_type="text",
                    help_text="Property location for market data integration",
                    validation_rules=["required", "max_length_200"],
                    accessibility_label="Property location or address"
                ),
                state
            )
        
        with col2:
            # Analyst name with smart suggestions
            analyst_name = self._render_smart_text_input(
                SmartInputConfig(
                    field_name="analyst_name",
                    label="Analyst Name",
                    input_type="text",
                    help_text="Name of the person conducting the analysis",
                    validation_rules=["required", "max_length_50"],
                    accessibility_label="Name of the analyst conducting the analysis"
                ),
                state
            )
            
            # Date input with smart defaults
            self._render_smart_date_input(
                SmartInputConfig(
                    field_name="analysis_date",
                    label="Analysis Date",
                    input_type="date",
                    help_text="Date of analysis for time-sensitive market data",
                    validation_rules=["required"],
                    accessibility_label="Date when the analysis is being conducted"
                ),
                state
            )
    
    def _render_adaptive_property_section(self, state: UIState) -> None:
        """Render property section with adaptive ranges"""
        st.markdown("### 🏢 Property Parameters")
        st.markdown("*Adaptive ranges based on property type and location*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Property type selector with enhanced options
            property_type = self._render_smart_selectbox(
                SmartInputConfig(
                    field_name="property_type",
                    label="Property Type",
                    input_type="selectbox",
                    help_text="Type of commercial property affects market rates",
                    validation_rules=["required"],
                    accessibility_label="Type of commercial property being analyzed"
                ),
                PROPERTY_TYPE_OPTIONS,
                state
            )
            
            # Adaptive property size based on type
            self._render_adaptive_property_size(property_type, state)
        
        with col2:
            # Market appreciation with contextual guidance
            self._render_smart_percentage_slider(
                SmartInputConfig(
                    field_name="market_appreciation_rate",
                    label="Market Appreciation Rate (%)",
                    input_type="slider",
                    min_value=0.0,
                    max_value=15.0,
                    step=0.1,
                    help_text="Expected annual property value appreciation",
                    validation_rules=["positive"],
                    contextual_guidance=True,
                    accessibility_label="Expected annual market appreciation rate"
                ),
                state
            )
            
            # Current space needed with validation
            self._render_smart_space_input(state)
    
    def _render_smart_financial_section(self, state: UIState) -> None:
        """Render financial parameters with smart validation"""
        st.markdown("### 💰 Financial Parameters")
        st.markdown("*Smart validation with market-based suggestions*")
        
        currency = state.input_values.get("currency", "USD")
        
        # Purchase price with market context
        self._render_smart_currency_input(
            SmartInputConfig(
                field_name="purchase_price",
                label=f"Purchase Price ({currency})",
                input_type="number",
                min_value=50000,
                max_value=100000000,
                step=10000,
                help_text="Property purchase price with market validation",
                validation_rules=["required", "positive", "reasonable_range"],
                adaptive_range=True,
                accessibility_label=f"Purchase price in {currency}"
            ),
            state
        )
        
        # Interest rate with current market data
        self._render_smart_rate_input(state)
        
        # Down payment with loan-to-value guidance
        self._render_smart_percentage_input(
            SmartInputConfig(
                field_name="down_payment_percent",
                label="Down Payment (%)",
                input_type="slider",
                min_value=0.0,
                max_value=100.0,
                step=1.0,
                help_text="Down payment affects loan terms and cash flow",
                validation_rules=["percentage"],
                contextual_guidance=True,
                accessibility_label="Down payment percentage of purchase price"
            ),
            state
        )
    
    def _render_progressive_operational_section(self, state: UIState) -> None:
        """Render operational parameters with progressive disclosure"""
        st.markdown("### ⚙️ Operational Parameters")
        st.markdown("*Progressive disclosure for advanced options*")
        
        # Basic operational parameters
        col1, col2 = st.columns(2)
        
        with col1:
            # Analysis period with adaptive suggestions
            self._render_smart_analysis_period(state)
            
            # Cost of capital with market guidance
            self._render_smart_rate_input(
                SmartInputConfig(
                    field_name="cost_of_capital",
                    label="Cost of Capital (%)",
                    input_type="number",
                    min_value=0.0,
                    max_value=20.0,
                    step=0.1,
                    format_string="%.1f",
                    help_text="Required rate of return for investment evaluation",
                    validation_rules=["positive", "reasonable_range"],
                    contextual_guidance=True,
                    accessibility_label="Cost of capital rate for investment evaluation"
                ),
                state
            )
        
        with col2:
            # Inflation rate with economic context
            self._render_smart_rate_input(
                SmartInputConfig(
                    field_name="inflation_rate",
                    label="Inflation Rate (%)",
                    input_type="number",
                    min_value=0.0,
                    max_value=20.0,
                    step=0.1,
                    format_string="%.1f",
                    help_text="Expected inflation rate affects future cash flows",
                    validation_rules=["positive"],
                    contextual_guidance=True,
                    accessibility_label="Expected annual inflation rate"
                ),
                state
            )
        
        # Progressive disclosure for advanced parameters
        with st.expander("🔧 Advanced Operational Parameters", expanded=False):
            self._render_advanced_operational_params(state)
    
    def _render_smart_text_input(self, config: SmartInputConfig, state: UIState) -> str:
        """Render smart text input with validation"""
        current_value = state.input_values.get(config.field_name, "")
        
        # Real-time validation
        validation_result = self.validate_input(config.field_name, current_value)
        
        # Render input with validation styling
        input_container = st.container()
        
        with input_container:
            value = st.text_input(
                config.label + ("*" if "required" in (config.validation_rules or []) else ""),
                value=current_value,
                key=config.field_name,
                help=config.help_text,
                max_chars=100 if "max_length_100" in (config.validation_rules or []) else 200,
                placeholder=self._get_smart_placeholder(config.field_name)
            )
            
            # Show validation feedback
            self._display_validation_feedback(validation_result)
            
            # Show contextual guidance
            if config.contextual_guidance:
                self._show_contextual_guidance(config.field_name, state)
        
        return value
    
    def _render_smart_date_input(self, config: SmartInputConfig, state: UIState) -> date:
        """Render smart date input with validation"""
        current_value = state.input_values.get(config.field_name, date.today())
        
        value = st.date_input(
            config.label + ("*" if "required" in (config.validation_rules or []) else ""),
            value=current_value,
            key=config.field_name,
            help=config.help_text
        )
        
        # Validation for date inputs
        validation_result = self.validate_input(config.field_name, value)
        self._display_validation_feedback(validation_result)
        
        return value
    
    def _render_smart_selectbox(self, config: SmartInputConfig, options: List[str], state: UIState) -> str:
        """Render smart selectbox with enhanced options"""
        current_value = state.input_values.get(config.field_name, options[0] if options else "")
        
        try:
            index = options.index(current_value) if current_value in options else 0
        except ValueError:
            index = 0
        
        value = st.selectbox(
            config.label + ("*" if "required" in (config.validation_rules or []) else ""),
            options=options,
            index=index,
            key=config.field_name,
            help=config.help_text
        )
        
        # Show contextual guidance for property type
        if config.field_name == "property_type":
            self._show_property_type_guidance(value)
        
        return value
    
    def _render_smart_currency_input(self, config: SmartInputConfig, state: UIState) -> float:
        """Render smart currency input with market validation"""
        current_value = state.input_values.get(config.field_name, 0)
        
        # Adaptive range based on property type and location
        if config.adaptive_range:
            min_val, max_val = self._get_adaptive_price_range(state)
            config.min_value = min_val
            config.max_value = max_val
        
        value = st.number_input(
            config.label + ("*" if "required" in (config.validation_rules or []) else ""),
            min_value=config.min_value,
            max_value=config.max_value,
            value=float(current_value) if current_value else config.min_value,
            step=config.step,
            key=config.field_name,
            help=config.help_text,
            format="%d"
        )
        
        # Market validation feedback
        self._show_market_price_feedback(value, state)
        
        return value
    
    def _render_smart_percentage_slider(self, config: SmartInputConfig, state: UIState) -> float:
        """Render smart percentage slider with contextual guidance"""
        current_value = state.input_values.get(config.field_name, 3.0)
        
        value = st.slider(
            config.label + ("*" if "required" in (config.validation_rules or []) else ""),
            min_value=config.min_value,
            max_value=config.max_value,
            value=float(current_value) if current_value else 3.0,
            step=config.step,
            key=config.field_name,
            help=config.help_text,
            format="%.1f%%"
        )
        
        # Show contextual guidance
        if config.contextual_guidance:
            self._show_rate_guidance(config.field_name, value)
        
        return value
    
    def _render_adaptive_property_size(self, property_type: str, state: UIState) -> None:
        """Render property size input with adaptive ranges"""
        # Adaptive ranges based on property type
        size_ranges = {
            "Office": (1000, 50000, 500),
            "Retail": (500, 20000, 100),
            "Industrial": (5000, 500000, 1000),
            "Warehouse": (10000, 1000000, 2000),
            "Mixed Use": (2000, 100000, 1000)
        }
        
        min_val, max_val, step_val = size_ranges.get(property_type, (1000, 100000, 500))
        
        current_value = state.input_values.get("ownership_property_size", min_val)
        
        value = st.number_input(
            "Property Size (m²)*",
            min_value=min_val,
            max_value=max_val,
            value=int(current_value) if current_value else min_val,
            step=step_val,
            key="ownership_property_size",
            help=f"Typical {property_type.lower()} property size range: {min_val:,} - {max_val:,} m²",
            format="%d"
        )
        
        # Show size context
        if value:
            self._show_property_size_context(value, property_type)
    
    def _render_smart_space_input(self, state: UIState) -> None:
        """Render current space needed with validation"""
        ownership_size = state.input_values.get("ownership_property_size", 0) or 0
        rental_size = state.input_values.get("rental_property_size", 0) or 0
        max_space = max(ownership_size, rental_size, 20000)
        
        current_value = state.input_values.get("current_space_needed", 0)
        
        value = st.number_input(
            "Current Space Needed (m²)*",
            min_value=100,
            max_value=int(max_space),
            value=int(current_value) if current_value else 100,
            step=100,
            key="current_space_needed",
            help="Space you currently need for operations",
            format="%d"
        )
        
        # Validation feedback
        if ownership_size > 0 and value > ownership_size:
            st.warning(f"⚠️ Space needed ({value:,} m²) exceeds property size ({ownership_size:,} m²)")
        elif ownership_size > 0 and value < ownership_size * 0.5:
            excess_space = ownership_size - value
            st.info(f"💡 Potential subletting opportunity: {excess_space:,} m² available")
    
    def _render_smart_analysis_period(self, state: UIState) -> None:
        """Render analysis period with smart suggestions"""
        property_type = state.input_values.get("property_type", "Office")
        
        # Suggested periods based on property type
        suggested_periods = {
            "Office": 25,
            "Retail": 20,
            "Industrial": 30,
            "Warehouse": 30,
            "Mixed Use": 25
        }
        
        suggested = suggested_periods.get(property_type, 25)
        current_value = state.input_values.get("analysis_period", suggested)
        
        value = st.number_input(
            "Analysis Period (years)*",
            min_value=1,
            max_value=50,
            value=int(current_value) if current_value else suggested,
            step=1,
            key="analysis_period",
            help=f"Recommended for {property_type.lower()}: {suggested} years"
        )
        
        # Show period guidance
        if value != suggested:
            if value < suggested - 5:
                st.info(f"💡 Consider longer period for {property_type.lower()} properties")
            elif value > suggested + 10:
                st.info(f"⚠️ Very long analysis period may reduce accuracy")
    
    def _render_smart_rate_input(self, state: UIState, config: SmartInputConfig = None) -> None:
        """Render interest rate input with market data"""
        if config is None:
            config = SmartInputConfig(
                field_name="interest_rate",
                label="Interest Rate (%)",
                input_type="number",
                min_value=0.0,
                max_value=20.0,
                step=0.1,
                format_string="%.2f",
                help_text="Current mortgage interest rate",
                validation_rules=["required", "positive"],
                contextual_guidance=True
            )
        
        current_value = state.input_values.get(config.field_name, 6.5)
        
        value = st.number_input(
            config.label + ("*" if "required" in (config.validation_rules or []) else ""),
            min_value=config.min_value,
            max_value=config.max_value,
            value=float(current_value) if current_value else 6.5,
            step=config.step,
            key=config.field_name,
            help=config.help_text,
            format=config.format_string or "%.2f"
        )
        
        # Show current market rate context
        self._show_current_rate_context(config.field_name, value)
    
    def _render_advanced_operational_params(self, state: UIState) -> None:
        """Render advanced operational parameters"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Future expansion with smart year selection
            self._render_smart_expansion_selector(state)
            
            # Subletting potential with space calculations
            self._render_smart_subletting_controls(state)
        
        with col2:
            # Long-term reserves with property type context
            self._render_smart_reserve_input(state)
            
            # Obsolescence risk with technology factors
            self._render_smart_obsolescence_input(state)
    
    def _render_mobile_smart_inputs(self, state: UIState) -> None:
        """Render mobile-optimized input layout"""
        # Mobile accordion sections
        sections = [
            ("📋 Project", self._render_mobile_project_section),
            ("🏢 Property", self._render_mobile_property_section),
            ("💰 Financial", self._render_mobile_financial_section),
            ("⚙️ Operations", self._render_mobile_operational_section)
        ]
        
        for title, render_func in sections:
            with st.expander(title, expanded=False):
                render_func(state)
    
    def validate_input(self, field_name: str, value: Any) -> ValidationResult:
        """Enhanced input validation with smart feedback"""
        # Use the existing validator with enhanced rules
        basic_validation = self.validator.validate_field(field_name, value)
        
        # Enhanced validation rules
        enhanced_result = self._apply_enhanced_validation(field_name, value, basic_validation)
        
        return enhanced_result
    
    def get_guidance(self, context: GuidanceContext) -> str:
        """Provide contextual guidance for inputs"""
        field_name = context.current_step
        
        # Cache guidance to avoid recomputation
        cache_key = f"{field_name}_{context.user_experience_level}"
        if cache_key in self.guidance_cache:
            return self.guidance_cache[cache_key]
        
        guidance = self._generate_contextual_guidance(field_name, context)
        self.guidance_cache[cache_key] = guidance
        
        return guidance
    
    # Helper methods for smart validation and guidance
    
    def _apply_enhanced_validation(self, field_name: str, value: Any, basic_result: ValidationResult) -> ValidationResult:
        """Apply enhanced validation rules"""
        if not basic_result.is_valid:
            return basic_result
        
        # Enhanced validation based on field type
        if field_name in ["purchase_price", "current_annual_rent"]:
            return self._validate_market_reasonable(field_name, value)
        elif field_name in ["interest_rate", "cost_of_capital"]:
            return self._validate_rate_reasonable(field_name, value)
        elif field_name in ["analysis_period"]:
            return self._validate_period_appropriate(field_name, value)
        
        return basic_result
    
    def _validate_market_reasonable(self, field_name: str, value: float) -> ValidationResult:
        """Validate if price/rent is market reasonable"""
        if field_name == "purchase_price":
            if value < 100000:
                return ValidationResult(
                    is_valid=True,
                    status=ValidationStatus.WARNING,
                    message="Purchase price seems low for commercial property",
                    suggestions=["Verify property details", "Check market comparables"]
                )
            elif value > 50000000:
                return ValidationResult(
                    is_valid=True,
                    status=ValidationStatus.WARNING,
                    message="Purchase price is very high",
                    suggestions=["Confirm financing availability", "Review investment strategy"]
                )
        
        return ValidationResult(is_valid=True, status=ValidationStatus.VALID, message="Value is reasonable")
    
    def _validate_rate_reasonable(self, field_name: str, value: float) -> ValidationResult:
        """Validate if interest rate is reasonable"""
        if field_name == "interest_rate":
            if value < 2.0:
                return ValidationResult(
                    is_valid=True,
                    status=ValidationStatus.WARNING,
                    message="Interest rate seems very low",
                    suggestions=["Verify current market rates", "Check loan terms"]
                )
            elif value > 12.0:
                return ValidationResult(
                    is_valid=True,
                    status=ValidationStatus.WARNING,
                    message="Interest rate seems very high",
                    suggestions=["Review credit terms", "Consider alternative financing"]
                )
        
        return ValidationResult(is_valid=True, status=ValidationStatus.VALID, message="Rate is reasonable")
    
    def _validate_period_appropriate(self, field_name: str, value: int) -> ValidationResult:
        """Validate if analysis period is appropriate"""
        if value < 10:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Short analysis period may not capture long-term benefits",
                suggestions=["Consider extending to 20-30 years", "Include terminal value"]
            )
        elif value > 40:
            return ValidationResult(
                is_valid=True,
                status=ValidationStatus.WARNING,
                message="Very long analysis period increases uncertainty",
                suggestions=["Consider 25-30 year period", "Use sensitivity analysis"]
            )
        
        return ValidationResult(is_valid=True, status=ValidationStatus.VALID, message="Period is appropriate")
    
    def _get_adaptive_price_range(self, state: UIState) -> Tuple[float, float]:
        """Get adaptive price range based on property type and size"""
        property_type = state.input_values.get("property_type", "Office")
        property_size = state.input_values.get("ownership_property_size", 5000)
        
        # Price per square meter by property type
        price_ranges = {
            "Office": (2000, 8000),
            "Retail": (1500, 6000),
            "Industrial": (800, 2500),
            "Warehouse": (600, 1500),
            "Mixed Use": (1800, 7000)
        }
        
        min_price_sqm, max_price_sqm = price_ranges.get(property_type, (1000, 5000))
        
        min_price = property_size * min_price_sqm
        max_price = property_size * max_price_sqm
        
        return (max(50000, min_price), min(100000000, max_price))
    
    def _get_smart_placeholder(self, field_name: str) -> str:
        """Get smart placeholder text for inputs"""
        placeholders = {
            "project_name": "e.g., Downtown Office Analysis 2024",
            "location": "e.g., 123 Business St, City Center",
            "analyst_name": "e.g., John Smith"
        }
        return placeholders.get(field_name, "")
    
    def _display_validation_feedback(self, result: ValidationResult) -> None:
        """Display validation feedback with appropriate styling"""
        if result.status == ValidationStatus.ERROR:
            st.error(f"❌ {result.message}")
        elif result.status == ValidationStatus.WARNING:
            st.warning(f"⚠️ {result.message}")
        elif result.status == ValidationStatus.VALID and result.message != "Valid":
            st.success(f"✅ {result.message}")
        
        if result.suggestions:
            with st.expander("💡 Suggestions", expanded=False):
                for suggestion in result.suggestions:
                    st.write(f"• {suggestion}")
    
    def _show_contextual_guidance(self, field_name: str, state: UIState) -> None:
        """Show contextual guidance for specific fields"""
        guidance_texts = {
            "project_name": "💡 Use descriptive names for easy identification",
            "location": "🌍 Specific locations help with market data integration",
            "analyst_name": "👤 Track who performed the analysis for audit trails"
        }
        
        if field_name in guidance_texts:
            st.caption(guidance_texts[field_name])
    
    def _show_property_type_guidance(self, property_type: str) -> None:
        """Show guidance based on selected property type"""
        guidance = {
            "Office": "📊 Office properties typically have stable tenants and predictable cash flows",
            "Retail": "🛍️ Retail properties may be more sensitive to economic cycles",
            "Industrial": "🏭 Industrial properties often have longer lease terms",
            "Warehouse": "📦 Warehouse demand driven by e-commerce and logistics",
            "Mixed Use": "🏢 Mixed use properties offer diversification but complexity"
        }
        
        if property_type in guidance:
            st.info(guidance[property_type])
    
    def _show_market_price_feedback(self, value: float, state: UIState) -> None:
        """Show market price feedback"""
        property_size = state.input_values.get("ownership_property_size", 0)
        if property_size > 0 and value > 0:
            price_per_sqm = value / property_size
            st.caption(f"📊 Price per m²: ${price_per_sqm:,.0f}")
            
            # Market context
            if price_per_sqm > 5000:
                st.caption("💰 Premium pricing - verify market justification")
            elif price_per_sqm < 1000:
                st.caption("💡 Below-market pricing - confirm property condition")
    
    def _show_rate_guidance(self, field_name: str, value: float) -> None:
        """Show guidance for rate inputs"""
        if field_name == "market_appreciation_rate":
            if value < 2.0:
                st.caption("📉 Conservative appreciation assumption")
            elif value > 6.0:
                st.caption("📈 Aggressive appreciation - consider sensitivity analysis")
            else:
                st.caption("📊 Moderate appreciation assumption")
    
    def _show_property_size_context(self, size: int, property_type: str) -> None:
        """Show context for property size"""
        if property_type == "Office":
            if size < 2000:
                st.caption("🏢 Small office space")
            elif size > 20000:
                st.caption("🏗️ Large office building")
        elif property_type == "Industrial":
            if size < 10000:
                st.caption("🏭 Small industrial facility")
            elif size > 100000:
                st.caption("🏭 Large industrial complex")
    
    def _show_current_rate_context(self, field_name: str, value: float) -> None:
        """Show current market rate context"""
        # This would integrate with real market data in production
        current_rates = {
            "interest_rate": 6.8,
            "cost_of_capital": 8.5,
            "inflation_rate": 3.2
        }
        
        if field_name in current_rates:
            market_rate = current_rates[field_name]
            if abs(value - market_rate) > 1.0:
                diff = value - market_rate
                direction = "above" if diff > 0 else "below"
                st.caption(f"📊 Current market: ~{market_rate}% (You: {direction} market)")
    
    def _generate_contextual_guidance(self, field_name: str, context: GuidanceContext) -> str:
        """Generate contextual guidance based on user experience level"""
        base_guidance = {
            "project_name": "Choose a descriptive name for your analysis",
            "location": "Enter the property location for market context",
            "purchase_price": "Consider total acquisition cost including fees",
            "interest_rate": "Use current market rates for accuracy"
        }
        
        if context.user_experience_level == "beginner":
            return f"🔰 {base_guidance.get(field_name, 'Enter the required information')}"
        elif context.user_experience_level == "expert":
            return f"🎯 {base_guidance.get(field_name, 'Configure parameter')}"
        else:
            return base_guidance.get(field_name, "")
    
    # Mobile-specific rendering methods
    def _render_mobile_project_section(self, state: UIState) -> None:
        """Mobile project section"""
        st.text_input("Project Name*", key="project_name")
        st.text_input("Location*", key="location")
        st.text_input("Analyst*", key="analyst_name")
        st.date_input("Date*", key="analysis_date")
    
    def _render_mobile_property_section(self, state: UIState) -> None:
        """Mobile property section"""
        st.selectbox("Property Type*", PROPERTY_TYPE_OPTIONS, key="property_type")
        st.number_input("Property Size (m²)*", min_value=1000, step=500, key="ownership_property_size")
        st.number_input("Current Space (m²)*", min_value=100, step=100, key="current_space_needed")
    
    def _render_mobile_financial_section(self, state: UIState) -> None:
        """Mobile financial section"""
        currency = state.input_values.get("currency", "USD")
        st.number_input(f"Purchase Price ({currency})*", min_value=50000, step=10000, key="purchase_price")
        st.slider("Down Payment (%)*", 0.0, 100.0, step=1.0, key="down_payment_percent")
        st.number_input("Interest Rate (%)*", min_value=0.0, max_value=20.0, step=0.1, key="interest_rate")
    
    def _render_mobile_operational_section(self, state: UIState) -> None:
        """Mobile operational section"""
        st.number_input("Analysis Period (years)*", min_value=1, max_value=50, key="analysis_period")
        st.number_input("Cost of Capital (%)*", min_value=0.0, max_value=20.0, step=0.1, key="cost_of_capital")
        st.number_input("Inflation Rate (%)*", min_value=0.0, max_value=20.0, step=0.1, key="inflation_rate")
    
    # Placeholder methods for future implementation
    def _render_smart_expansion_selector(self, state: UIState) -> None:
        """Smart expansion year selector"""
        st.selectbox("Future Expansion Year", ["Never", "Year 10", "Year 15", "Year 20"], key="future_expansion_year")
    
    def _render_smart_subletting_controls(self, state: UIState) -> None:
        """Smart subletting controls"""
        st.checkbox("Subletting Potential", key="subletting_potential")
    
    def _render_smart_reserve_input(self, state: UIState) -> None:
        """Smart reserve calculation"""
        st.number_input("Long-term CapEx Reserve (%)*", min_value=0.0, max_value=10.0, step=0.1, key="longterm_capex_reserve")
    
    def _render_smart_obsolescence_input(self, state: UIState) -> None:
        """Smart obsolescence risk input"""
        st.number_input("Obsolescence Risk (%)", min_value=0.0, max_value=5.0, step=0.1, key="obsolescence_risk_factor")
    
    def _render_smart_percentage_input(self, config: SmartInputConfig, state: UIState) -> float:
        """Render smart percentage input"""
        current_value = state.input_values.get(config.field_name, 20.0)
        
        value = st.slider(
            config.label,
            min_value=config.min_value,
            max_value=config.max_value,
            value=float(current_value) if current_value else 20.0,
            step=config.step,
            key=config.field_name,
            help=config.help_text,
            format="%.0f%%"
        )
        
        # Show loan-to-value context for down payment
        if config.field_name == "down_payment_percent":
            ltv = 100 - value
            st.caption(f"📊 Loan-to-Value: {ltv:.0f}%")
            if ltv > 80:
                st.caption("⚠️ High LTV may require PMI or higher rates")
        
        return value


def create_advanced_input_component() -> AdvancedInputComponent:
    """Factory function to create advanced input component"""
    return AdvancedInputComponent()


# Demo/testing function
def demo_advanced_inputs():
    """Demo function for testing advanced inputs"""
    st.title("🎨 Advanced Input Components Demo")
    
    # Create mock state
    mock_state = UIState(
        active_tab="inputs",
        input_values={
            "currency": "USD",
            "property_type": "Office",
            "ownership_property_size": 5000,
            "mobile_mode": st.sidebar.checkbox("Mobile Mode", False)
        },
        validation_results={},
        guidance_visible=True,
        mobile_mode=st.sidebar.checkbox("Mobile Mode", False)
    )
    
    # Create component
    component = create_advanced_input_component()
    
    # Render component
    component.render(None, mock_state)


if __name__ == "__main__":
    demo_advanced_inputs()