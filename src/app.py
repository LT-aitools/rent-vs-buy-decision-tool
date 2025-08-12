"""
Real Estate Rent vs. Buy Decision Tool
Main Streamlit Application Entry Point

Redirects to the enhanced application with comprehensive visualizations.

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

# Import and run the enhanced application
import sys
import os

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced application
try:
    from app_with_visualizations import main
    main()
except Exception as e:
    import streamlit as st
    st.error(f"Error loading application: {e}")
    st.info("Please check the application logs for more details.")
    import traceback
    st.code(traceback.format_exc())