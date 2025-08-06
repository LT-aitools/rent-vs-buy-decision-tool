"""
UI Helper Functions
Common utility functions for the user interface

Provides:
- UI state management
- Common calculations for display
- Error handling utilities
- Navigation helpers
"""

import streamlit as st
from typing import Any, Dict, List, Optional, Tuple
import json
from datetime import datetime

def show_tooltip(text: str, help_text: str):
    """Display text with tooltip helper"""
    st.markdown(f"{text} ❓", help=help_text)

def create_info_card(title: str, value: str, delta: Optional[str] = None,
                    delta_color: str = "normal", help_text: Optional[str] = None):
    """Create an information card with optional delta and help"""
    container = st.container()
    with container:
        if help_text:
            st.help(help_text)
        st.metric(label=title, value=value, delta=delta, delta_color=delta_color)

def format_validation_message(field_name: str, message: str, message_type: str = "error") -> str:
    """Format validation messages with consistent styling"""
    icons = {
        "error": "❌",
        "warning": "⚠️", 
        "info": "ℹ️",
        "success": "✅"
    }
    
    icon = icons.get(message_type, "ℹ️")
    return f"{icon} **{field_name}**: {message}"

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    if denominator == 0 or denominator is None:
        return default
    return numerator / denominator

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0 or old_value is None:
        return 0.0
    return ((new_value - old_value) / old_value) * 100

def format_section_completion_status(is_complete: bool) -> Tuple[str, str]:
    """Return status icon and text for section completion"""
    if is_complete:
        return "✅", "Complete"
    else:
        return "⏳", "Pending"

def get_field_value_with_fallback(field_name: str, fallback_value: Any = None) -> Any:
    """Get field value from session state with fallback"""
    return st.session_state.get(field_name, fallback_value)

def update_session_field(field_name: str, value: Any, trigger_rerun: bool = False):
    """Update session state field and optionally trigger rerun"""
    st.session_state[field_name] = value
    if trigger_rerun:
        st.rerun()

def calculate_loan_payment(principal: float, rate: float, term: int) -> float:
    """Calculate monthly loan payment using PMT formula"""
    if rate == 0:
        return principal / (term * 12) if term > 0 else 0
    
    if term == 0:
        return 0
    
    monthly_rate = rate / 12 / 100
    num_payments = term * 12
    
    if monthly_rate == 0:
        return principal / num_payments
    
    payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
              ((1 + monthly_rate) ** num_payments - 1)
    
    return payment

def calculate_annual_loan_payment(principal: float, rate: float, term: int) -> float:
    """Calculate annual loan payment"""
    monthly_payment = calculate_loan_payment(principal, rate, term)
    return monthly_payment * 12

def get_currency_formatting_info(currency: str) -> Dict[str, Any]:
    """Get formatting information for a specific currency"""
    currency_info = {
        "USD": {"symbol": "$", "position": "before", "decimals": 2},
        "EUR": {"symbol": "€", "position": "after", "decimals": 2},
        "GBP": {"symbol": "£", "position": "before", "decimals": 2},
        "CAD": {"symbol": "C$", "position": "before", "decimals": 2},
        "AUD": {"symbol": "A$", "position": "before", "decimals": 2},
        "ILS": {"symbol": "₪", "position": "before", "decimals": 2},
        "LEI": {"symbol": "lei", "position": "after", "decimals": 2},
        "PLN": {"symbol": "zł", "position": "after", "decimals": 2}
    }
    
    return currency_info.get(currency, {"symbol": currency, "position": "before", "decimals": 2})

def create_download_link(data: Any, filename: str, link_text: str = "Download"):
    """Create a download link for data"""
    if isinstance(data, dict):
        json_string = json.dumps(data, indent=2, default=str)
        st.download_button(
            label=link_text,
            data=json_string,
            file_name=filename,
            mime="application/json"
        )
    else:
        st.download_button(
            label=link_text,
            data=str(data),
            file_name=filename,
            mime="text/plain"
        )

def display_comparison_metrics(title: str, value1: float, value2: float, 
                             labels: Tuple[str, str], currency: str = "USD",
                             format_as_currency: bool = True):
    """Display comparison metrics in columns"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**{title}**")
    
    with col2:
        if format_as_currency:
            from .formatting import format_currency
            formatted_value1 = format_currency(value1, currency)
        else:
            formatted_value1 = f"{value1:,.2f}"
        st.metric(labels[0], formatted_value1)
    
    with col3:
        if format_as_currency:
            from .formatting import format_currency
            formatted_value2 = format_currency(value2, currency)
        else:
            formatted_value2 = f"{value2:,.2f}"
        
        delta = value2 - value1
        delta_color = "normal"
        if delta > 0:
            delta_color = "inverse"  # Higher is typically worse for costs
        
        st.metric(labels[1], formatted_value2, delta=f"{delta:+,.0f}")

def create_expandable_help_section(title: str, content: str, expanded: bool = False):
    """Create an expandable help section"""
    with st.expander(f"❓ {title}", expanded=expanded):
        st.markdown(content)

def validate_positive_number(value: Any, field_name: str) -> Tuple[bool, str]:
    """Validate that a value is a positive number"""
    try:
        num_value = float(value)
        if num_value < 0:
            return False, f"{field_name} must be a positive number"
        return True, ""
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number"

def validate_percentage(value: Any, field_name: str, min_val: float = 0.0, 
                       max_val: float = 100.0) -> Tuple[bool, str]:
    """Validate percentage values"""
    try:
        num_value = float(value)
        if num_value < min_val:
            return False, f"{field_name} must be at least {min_val}%"
        if num_value > max_val:
            return False, f"{field_name} cannot exceed {max_val}%"
        return True, ""
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid percentage"

def create_styled_metric_card(title: str, value: str, subtitle: Optional[str] = None,
                            color: str = "blue"):
    """Create a styled metric card with custom color"""
    
    color_schemes = {
        "blue": {"bg": "#f0f9ff", "border": "#0ea5e9", "text": "#0c4a6e"},
        "green": {"bg": "#f0fdf4", "border": "#22c55e", "text": "#14532d"},
        "red": {"bg": "#fef2f2", "border": "#ef4444", "text": "#7f1d1d"},
        "yellow": {"bg": "#fffbeb", "border": "#f59e0b", "text": "#78350f"},
        "purple": {"bg": "#faf5ff", "border": "#a855f7", "text": "#581c87"}
    }
    
    scheme = color_schemes.get(color, color_schemes["blue"])
    
    st.markdown(f"""
    <div style='
        background-color: {scheme["bg"]};
        border-left: 4px solid {scheme["border"]};
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    '>
        <h3 style='margin: 0; color: {scheme["text"]}; font-size: 1.1rem;'>{title}</h3>
        <p style='margin: 0.25rem 0 0 0; font-size: 1.5rem; font-weight: bold; color: {scheme["text"]};'>{value}</p>
        {f'<p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; color: {scheme["text"]}; opacity: 0.7;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def display_progress_indicator(current_step: int, total_steps: int, step_names: List[str]):
    """Display a progress indicator for multi-step processes"""
    progress = current_step / total_steps
    st.progress(progress, text=f"Step {current_step} of {total_steps}: {step_names[current_step-1] if current_step <= len(step_names) else 'Complete'}")

def create_two_column_comparison(left_title: str, right_title: str, 
                               left_content: Any, right_content: Any):
    """Create a two-column comparison layout"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {left_title}")
        if callable(left_content):
            left_content()
        else:
            st.write(left_content)
    
    with col2:
        st.markdown(f"### {right_title}")
        if callable(right_content):
            right_content()
        else:
            st.write(right_content)

def format_business_number(value: float, format_type: str = "auto") -> str:
    """Format numbers for business display (K, M, B suffixes)"""
    if value is None:
        return "N/A"
    
    abs_value = abs(value)
    
    if format_type == "currency" or format_type == "auto":
        if abs_value >= 1_000_000_000:
            return f"${value/1_000_000_000:.1f}B"
        elif abs_value >= 1_000_000:
            return f"${value/1_000_000:.1f}M" 
        elif abs_value >= 1_000:
            return f"${value/1_000:.1f}K"
        else:
            return f"${value:,.0f}"
    else:
        if abs_value >= 1_000_000_000:
            return f"{value/1_000_000_000:.1f}B"
        elif abs_value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif abs_value >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return f"{value:,.0f}"

def create_status_badge(status: str, status_type: str = "info") -> str:
    """Create a status badge with appropriate styling"""
    
    badges = {
        "success": ("✅", "#22c55e", "#dcfce7", "#14532d"),
        "error": ("❌", "#ef4444", "#fef2f2", "#7f1d1d"), 
        "warning": ("⚠️", "#f59e0b", "#fffbeb", "#78350f"),
        "info": ("ℹ️", "#0ea5e9", "#f0f9ff", "#0c4a6e"),
        "pending": ("⏳", "#6b7280", "#f9fafb", "#374151")
    }
    
    icon, border_color, bg_color, text_color = badges.get(status_type, badges["info"])
    
    return f"""
    <span style='
        background-color: {bg_color};
        color: {text_color};
        border: 1px solid {border_color};
        padding: 0.25rem 0.5rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    '>
        {icon} {status}
    </span>
    """

def export_session_to_url() -> str:
    """Export current session state to a shareable URL (simplified version)"""
    # This would encode session state parameters into URL query parameters
    # For now, return a placeholder
    base_url = "https://your-app-url.com"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_url}?session={timestamp}"

def import_session_from_url(url_params: Dict[str, Any]) -> bool:
    """Import session state from URL parameters"""
    # This would decode URL parameters back into session state
    # Implementation would depend on specific URL encoding scheme
    return True