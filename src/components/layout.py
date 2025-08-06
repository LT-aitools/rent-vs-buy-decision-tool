"""
Layout and Styling Components
Professional UI layout system for the Real Estate Decision Tool

Provides:
- App structure and navigation
- Professional theming
- Responsive design
- Executive presentation styling
"""

import streamlit as st
from typing import Optional

def setup_page_config():
    """Configure the Streamlit page with professional settings"""
    st.set_page_config(
        page_title="Real Estate Decision Tool",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': "Real Estate Rent vs. Buy Decision Tool - Professional Financial Analysis"
        }
    )

def apply_custom_css():
    """Apply custom CSS for professional styling"""
    st.markdown("""
    <style>
    /* Main app styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Professional header styling */
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 3rem;
    }
    
    /* Input form styling */
    .stNumberInput > div > div > input {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 0.375rem;
    }
    
    .stSelectbox > div > div {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 0.375rem;
    }
    
    .stTextInput > div > div > input {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 0.375rem;
    }
    
    /* Metric card styling */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Section headers */
    .section-header {
        color: #1e40af;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }
    
    /* Error styling */
    .stAlert > div {
        border-radius: 0.375rem;
    }
    
    /* Success styling */
    .stSuccess > div {
        border-radius: 0.375rem;
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
    }
    
    /* Warning styling */
    .stWarning > div {
        border-radius: 0.375rem;
        background-color: #fffbeb;
        border: 1px solid #fde68a;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f1f5f9;
        border-radius: 0.375rem;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 0.375rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main > div {
            padding: 1rem;
        }
        
        .main-header {
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render the professional application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🏢 Real Estate Decision Tool</h1>
        <p><em>Professional Hold-Forever Investment Strategy Analysis</em></p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_navigation():
    """Render the professional sidebar navigation"""
    st.sidebar.markdown("### 📋 Input Parameters")
    st.sidebar.markdown("Complete all sections below for analysis:")
    
    # Navigation status indicators
    sections = {
        "Project Information": "project_info_complete",
        "Property & Market": "property_market_complete", 
        "Purchase Parameters": "purchase_params_complete",
        "Rental Parameters": "rental_params_complete",
        "Operational Parameters": "operational_params_complete",
        "Tax & Accounting": "tax_accounting_complete"
    }
    
    for section_name, status_key in sections.items():
        status = "✅" if st.session_state.get(status_key, False) else "⏳"
        st.sidebar.markdown(f"{status} {section_name}")

def create_metric_card(title: str, value: str, delta: Optional[str] = None, 
                      delta_color: str = "normal"):
    """Create a professional metric card"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(
            label=title,
            value=value,
            delta=delta,
            delta_color=delta_color
        )

def create_section_header(title: str, icon: str = ""):
    """Create a professional section header"""
    st.markdown(f"""
    <div class="section-header">
        {icon} {title}
    </div>
    """, unsafe_allow_html=True)

def create_info_box(message: str, type_: str = "info"):
    """Create styled info boxes"""
    if type_ == "info":
        st.info(f"ℹ️ {message}")
    elif type_ == "warning":
        st.warning(f"⚠️ {message}")
    elif type_ == "success":
        st.success(f"✅ {message}")
    elif type_ == "error":
        st.error(f"❌ {message}")

def create_professional_columns(num_cols: int, gap: str = "small"):
    """Create responsive columns with professional spacing"""
    return st.columns(num_cols, gap=gap)

def render_footer():
    """Render professional footer"""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #64748b; font-size: 0.875rem; margin-top: 2rem;'>
        <p>Real Estate Decision Tool | Professional Financial Analysis Platform</p>
        <p>Hold-Forever Investment Strategy | Executive-Ready Reporting</p>
    </div>
    """, unsafe_allow_html=True)

def initialize_professional_layout():
    """Initialize the complete professional layout"""
    setup_page_config()
    apply_custom_css()
    render_header()
    render_sidebar_navigation()

# CSS for mobile responsiveness
RESPONSIVE_CSS = """
<style>
/* Mobile-first responsive design */
@media (max-width: 640px) {
    .stColumns > div {
        width: 100% !important;
        margin-bottom: 1rem;
    }
    
    .main-header h1 {
        font-size: 1.5rem;
    }
    
    .metric-card {
        padding: 0.75rem;
    }
}

@media (min-width: 641px) and (max-width: 1024px) {
    .stColumns > div {
        padding: 0 0.5rem;
    }
}

@media (min-width: 1025px) {
    .stColumns > div {
        padding: 0 1rem;
    }
}
</style>
"""

def apply_responsive_design():
    """Apply responsive design CSS"""
    st.markdown(RESPONSIVE_CSS, unsafe_allow_html=True)