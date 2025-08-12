import streamlit as st

st.set_page_config(
    page_title="Test App",
    layout="wide"
)

st.title("🏢 Test Deployment")
st.write("If you can see this, basic Streamlit deployment is working!")

# Test basic imports
try:
    import pandas as pd
    st.success("✅ pandas imported successfully")
except ImportError as e:
    st.error(f"❌ pandas import failed: {e}")

try:
    import numpy as np
    st.success("✅ numpy imported successfully")
except ImportError as e:
    st.error(f"❌ numpy import failed: {e}")

try:
    import plotly
    st.success("✅ plotly imported successfully")
except ImportError as e:
    st.error(f"❌ plotly import failed: {e}")

# Test module imports
try:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    from calculations.npv_analysis import calculate_npv_comparison
    st.success("✅ NPV analysis module imported successfully")
except ImportError as e:
    st.error(f"❌ NPV analysis import failed: {e}")
except Exception as e:
    st.error(f"❌ Unexpected error: {e}")

st.write("**Environment Info:**")
st.write(f"Python version: {sys.version}")
st.write(f"Current working directory: {os.getcwd()}")
st.write(f"File location: {__file__}")