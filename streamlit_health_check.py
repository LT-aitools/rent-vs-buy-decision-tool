"""
Streamlit Health Check Script
This script can be used to verify Streamlit deployment readiness
"""

import streamlit as st
import sys
import os

# Basic page config
st.set_page_config(
    page_title="Health Check",
    page_icon="✅",
    layout="centered"
)

st.title("✅ Streamlit Health Check")

# Environment info
st.subheader("Environment Information")
col1, col2 = st.columns(2)

with col1:
    st.metric("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}")
    st.metric("Working Directory", os.getcwd())

with col2:
    try:
        st.metric("File Location", __file__)
    except NameError:
        st.metric("File Location", "Unknown (exec context)")
    st.metric("Streamlit Version", st.__version__)

# Test imports
st.subheader("Dependency Check")

dependencies = [
    ("pandas", "pd"),
    ("numpy", "np"), 
    ("plotly.graph_objects", "go"),
    ("openpyxl", None),
    ("reportlab", None)
]

for dep, alias in dependencies:
    try:
        if alias:
            exec(f"import {dep} as {alias}")
        else:
            exec(f"import {dep}")
        st.success(f"✅ {dep} - OK")
    except ImportError as e:
        st.error(f"❌ {dep} - FAILED: {e}")

# Test basic functionality
st.subheader("Basic Functionality Test")

if st.button("Test Button"):
    st.balloons()
    st.success("Button test passed!")

# Test number input
test_value = st.number_input("Test Number Input", value=42)
st.info(f"You entered: {test_value}")

# Test file structure
st.subheader("File Structure Check")

expected_files = [
    "requirements.txt",
    "runtime.txt", 
    "main.py",
    "src/app.py"
]

for file_path in expected_files:
    full_path = os.path.join(os.getcwd(), file_path)
    if os.path.exists(full_path):
        st.success(f"✅ {file_path}")
    else:
        st.error(f"❌ {file_path} - Missing")

st.success("🎉 Health check completed!")