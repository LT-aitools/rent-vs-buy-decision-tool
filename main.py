"""
Fallback entry point for Streamlit Cloud deployment
This file ensures Streamlit Cloud can find a valid entry point
"""

import streamlit as st
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main app
try:
    from src.app import *
except ImportError:
    st.error("Could not import main app. Please check src/app.py")
    st.info("Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool")