"""
Real Estate Rent vs. Buy Decision Tool
Main Streamlit Application with Professional UI Components

Complete implementation with professional input forms, validation,
and responsive design based on Business and Technical PRDs.

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

import streamlit as st
from datetime import datetime
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom UI components
try:
    from components import (
        initialize_professional_layout,
        render_all_input_forms,
        initialize_session,
        get_session_manager,
        create_info_box,
        render_footer
    )
except ImportError as e:
    st.error(f"Error importing components: {e}")
    st.stop()

def render_dashboard_tab():
    """Render the main dashboard with input forms"""
    st.markdown("## 📊 Input Dashboard")
    st.markdown("*Complete all input sections below to enable financial analysis*")
    
    # Instructions for sidebar access
    st.info("👈 **Use the sidebar on the left** to input your property and financial data.")
    
    # Render input forms in sidebar
    with st.sidebar:
        try:
            inputs_valid = render_all_input_forms()
        except Exception as e:
            st.error("⚠️ **Loading Error** - Please refresh the page")
            inputs_valid = False
    
    # Main dashboard area
    try:
        session_manager = get_session_manager()
    except Exception as e:
        st.error(f"⚠️ **Session Error**: {str(e)}")
        st.info("🔄 Please refresh the page to continue")
        return
    
    if inputs_valid:
        st.success("✅ **All inputs are valid and ready for analysis!**")
        
        # Display input summary in main area
        st.markdown("### 📋 Analysis Summary")
        summary = session_manager.get_input_summary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            for section, data in list(summary.items())[:2]:
                st.markdown(f"**{section}**")
                for key, value in data.items():
                    st.write(f"• {key}: {value}")
                st.markdown("")
        
        with col2:
            for section, data in list(summary.items())[2:]:
                st.markdown(f"**{section}**")
                for key, value in data.items():
                    st.write(f"• {key}: {value}")
                st.markdown("")
        
        # Placeholder for analysis results
        st.markdown("---")
        st.markdown("### 📈 Financial Analysis")
        st.info("🚧 **Analysis Engine Coming Soon** - Calculations and visualizations will be implemented next")
        
        # Show completion status
        try:
            completion = session_manager.get_completion_percentage()
            st.progress(completion / 100, text=f"Setup Complete: {completion:.0f}%")
        except Exception:
            st.progress(0.0, text="Setup Complete: 0%")
        
    else:
        # Show what's needed
        st.markdown("### 📝 Getting Started")
        
        create_info_box(
            "Complete the input sections in the sidebar to begin your rent vs buy analysis. "
            "All required fields must be filled with valid data.",
            "info"
        )
        
        # Show completion progress
        try:
            completion = session_manager.get_completion_percentage()
            st.progress(completion / 100, text=f"Input Progress: {completion:.0f}%")
        except Exception:
            st.progress(0.0, text="Input Progress: 0%")
        
        # Development status
        st.markdown("### 🛠 Development Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Week 1", "UI Components", "✅ Complete")
        
        with col2:
            st.metric("Week 2", "Calculations", "🚧 In Progress")
        
        with col3:
            st.metric("Week 3", "Visualizations", "⏳ Pending")

def render_export_tab():
    """Render export and sharing functionality"""
    st.markdown("## 📤 Export & Sharing")
    
    session_manager = get_session_manager()
    
    if not session_manager.is_ready_for_analysis():
        create_info_box(
            "Complete all required input sections to enable export functionality.",
            "warning"
        )
        return
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Export Current Analysis")
        
        # Export session data as JSON
        export_data = session_manager.export_session_data()
        
        st.download_button(
            label="📄 Download Input Data (JSON)",
            data=str(export_data),
            file_name=f"real_estate_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="Download all input parameters for backup or sharing"
        )
        
        st.download_button(
            label="📈 Export Analysis Report (Coming Soon)",
            data="Analysis report functionality coming soon",
            file_name="analysis_report.txt",
            disabled=True,
            help="Full Excel/PDF export will be available after calculations are implemented"
        )
    
    with col2:
        st.markdown("### 🔄 Session Management")
        
        if st.button("🔄 Reset All Inputs", type="secondary"):
            session_manager.reset_session()
            st.success("✅ All inputs have been reset to default values")
            st.rerun()
        
        st.markdown("**Import Analysis:**")
        uploaded_file = st.file_uploader(
            "Upload JSON file",
            type=['json'],
            help="Upload a previously exported analysis JSON file"
        )
        
        if uploaded_file is not None:
            try:
                import json
                data = json.load(uploaded_file)
                if session_manager.import_session_data(data):
                    st.success("✅ Analysis imported successfully!")
                    st.rerun()
                else:
                    st.error("❌ Error importing analysis data")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")

def render_help_tab():
    """Render help and documentation"""
    st.markdown("## ❓ Help & Documentation")
    
    # Quick start guide
    st.markdown("### 🚀 Quick Start Guide")
    
    with st.expander("📋 How to Use This Tool", expanded=True):
        st.markdown("""
        1. **Complete Input Sections**: Fill out all required fields in the sidebar sections
        2. **Review Validation**: Address any validation warnings or errors
        3. **Run Analysis**: Once inputs are complete, the analysis will be calculated automatically
        4. **Review Results**: Examine the rent vs buy recommendation and supporting data
        5. **Export Report**: Download Excel/PDF reports for presentation and record-keeping
        """)
    
    with st.expander("💡 Input Field Explanations"):
        st.markdown("""
        **Project Information**: Basic details about your analysis project
        
        **Property & Market**: Property specifications and market assumptions
        
        **Purchase Parameters**: All costs and financing terms for buying the property
        
        **Rental Parameters**: Current rent and rental cost assumptions
        
        **Operational Parameters**: Business growth, expansion, and operational assumptions
        
        **Tax & Accounting**: Tax rates and deductibility assumptions
        """)
    
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Common Issues:**
        - *Validation errors*: Check that all required fields are filled with valid values
        - *Missing calculations*: Ensure all required sections are marked as complete
        - *Performance issues*: Clear browser cache or refresh the page
        
        **Getting Help:**
        - Review field tooltips (❓ icons) for detailed explanations
        - Check validation messages for specific guidance
        - Refer to the Business PRD for methodology details
        """)
    
    # Technical information
    st.markdown("### 📚 Technical Documentation")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("[📋 Business PRD](docs/business-prd.txt)")
        st.markdown("[🛠 Technical PRD](docs/technical-prd.md)")
    
    with col2:
        st.markdown("[📊 Methodology Details](docs/business-prd.txt#calculations)")
        st.markdown("[🔍 Field Definitions](docs/business-prd.txt#inputs)")

def main():
    """Main application entry point with professional UI"""
    
    # Initialize page config FIRST (must be first Streamlit command)
    st.set_page_config(
        page_title="Real Estate Decision Tool",
        page_icon="🏢", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Then initialize other components
    initialize_session()
    
    # Apply basic styling
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); 
                padding: 1.5rem 2rem; border-radius: 0.5rem; margin-bottom: 2rem; 
                color: white; text-align: center;">
        <h1 style="color: white; margin: 0;">🏢 Real Estate Decision Tool</h1>
        <p style="color: white; margin: 0; font-style: italic;">Professional Hold-Forever Investment Strategy Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab navigation
    tab1, tab2, tab3 = st.tabs(["📊 Analysis Dashboard", "📤 Export & Share", "❓ Help & Documentation"])
    
    with tab1:
        render_dashboard_tab()
    
    with tab2:
        render_export_tab()
    
    with tab3:
        render_help_tab()
    
    # Professional footer
    render_footer()

if __name__ == "__main__":
    main()