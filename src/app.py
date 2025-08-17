"""
Real Estate Rent vs. Buy Decision Tool
Main Entry Point - Full Featured Application

This version includes the complete rent vs buy analysis functionality.
"""

import streamlit as st
import sys
import os

# Page configuration - must be first
st.set_page_config(
    page_title="Real Estate Decision Tool",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Try to load the full app
try:
    # Import the full app components
    exec(open(os.path.join(current_dir, 'app_full.py')).read())
    # If we get here, the full app loaded successfully
    st.sidebar.success("✅ App Updated! (v2.1.10 - Precision Fixes)")
except Exception as e:
    # Fallback to simple version if full app fails
    st.title("🏢 Real Estate Rent vs. Buy Decision Tool")
    st.error(f"⚠️ Full application temporarily unavailable: {e}")
    
    # Show more detailed error for debugging
    import traceback
    with st.expander("🔧 Technical Details (for debugging)"):
        st.code(traceback.format_exc())
    
    st.info("🔧 **Fallback Mode** - Basic functionality available")
    
    # Simple calculator as fallback
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
    
    st.markdown("---")
    st.markdown("**Repository:** https://github.com/LT-aitools/rent-vs-buy-decision-tool")