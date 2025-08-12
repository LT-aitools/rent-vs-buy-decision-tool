"""
Real Estate Rent vs. Buy Decision Tool
Simple Main Entry Point for Streamlit Cloud Deployment

This is a simplified version that should work reliably on Streamlit Cloud.
"""

import streamlit as st

# Page configuration - must be first
st.set_page_config(
    page_title="Real Estate Decision Tool",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏢 Real Estate Rent vs. Buy Decision Tool")
st.markdown("---")

st.info("🚧 **Deployment in progress** - This is a simplified version while we resolve cloud deployment issues.")

st.markdown("""
### 📋 What This Tool Does
- **Comprehensive Financial Analysis** - Compare rent vs purchase scenarios
- **NPV Calculations** - Net present value analysis over time
- **Interactive Dashboards** - Professional visualizations and charts  
- **Excel/PDF Exports** - Executive-ready reports
- **Hold-Forever Strategy** - Optimized for long-term property ownership

### 🛠 Current Status
We're working on resolving deployment issues to bring you the full application with all features.

### 💻 Local Development
The full application works perfectly when run locally. The issue is specific to cloud deployment.
""")

# Test basic functionality
if st.button("🧪 Test Basic Functionality"):
    try:
        import pandas as pd
        import numpy as np
        import plotly.graph_objects as go
        
        st.success("✅ All core dependencies loaded successfully")
        
        # Simple demo calculation
        purchase_price = st.number_input("Purchase Price ($)", value=500000, min_value=0)
        annual_rent = st.number_input("Annual Rent ($)", value=24000, min_value=0)
        
        if purchase_price > 0 and annual_rent > 0:
            rent_to_price_ratio = (annual_rent / purchase_price) * 100
            st.metric("Rent-to-Price Ratio", f"{rent_to_price_ratio:.2f}%")
            
            if rent_to_price_ratio < 5:
                st.success("💰 **Buying may be favorable** - Low rent-to-price ratio")
            elif rent_to_price_ratio > 8:
                st.warning("🏠 **Renting may be favorable** - High rent-to-price ratio") 
            else:
                st.info("⚖️ **Detailed analysis needed** - Ratio in neutral range")
    
    except Exception as e:
        st.error(f"❌ Error: {e}")

st.markdown("---")
st.markdown("**Repository:** https://github.com/LT-aitools/rent-vs-buy-decision-tool")