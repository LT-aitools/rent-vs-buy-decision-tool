"""
Real Estate Rent vs. Buy Decision Tool
Main Streamlit Application Entry Point

Redirects to the enhanced application with comprehensive visualizations.

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

# Import and run the enhanced application
import sys
import os

# Add current directory and parent directory to path for robust imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Import the enhanced application
try:
    import streamlit as st
    
    # Set page config first
    st.set_page_config(
        page_title="Real Estate Decision Tool",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Try to import and run the enhanced app
    try:
        from app_with_visualizations import main
        main()
    except ImportError as import_error:
        st.error(f"Import Error: {import_error}")
        st.info("Falling back to basic error display")
        st.code(f"Current directory: {current_dir}")
        st.code(f"Python path: {sys.path[:5]}")  # Show first 5 entries
        
except Exception as e:
    import streamlit as st
    st.error(f"Critical Error loading application: {e}")
    st.info("Please check the application logs for more details.")
    import traceback
    st.code(traceback.format_exc())