"""
Real Estate Rent vs. Buy Decision Tool
Minimal Cloud Version for Streamlit Cloud Deployment
"""

import streamlit as st

st.set_page_config(
    page_title="Real Estate Decision Tool",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Real Estate Decision Tool")
st.write("**Status:** Successfully deployed to Streamlit Cloud! ✅")

st.markdown("---")

# Basic working calculator
st.subheader("📊 Quick Analysis")

col1, col2 = st.columns(2)
with col1:
    purchase_price = st.number_input("Purchase Price ($)", value=500000, min_value=0, step=10000)
with col2:
    annual_rent = st.number_input("Annual Rent ($)", value=24000, min_value=0, step=1000)

if purchase_price > 0 and annual_rent > 0:
    ratio = (annual_rent / purchase_price) * 100
    
    st.markdown("### Results")
    st.metric("Rent-to-Price Ratio", f"{ratio:.2f}%")
    
    if ratio < 5:
        st.success("💰 **Buying may be more favorable** - Low rent-to-price ratio")
        st.info("Generally, when rent-to-price ratios are below 5%, purchasing may offer better long-term value.")
    elif ratio > 8:
        st.warning("🏠 **Renting may be more favorable** - High rent-to-price ratio")
        st.info("When ratios exceed 8%, renting often provides more financial flexibility.")
    else:
        st.info("⚖️ **Detailed analysis recommended** - Ratio in neutral range")
        st.info("Ratios between 5-8% require deeper analysis of your specific situation.")

st.markdown("---")
st.markdown("**Full Version:** This is a simplified cloud version. The complete analysis tool with NPV calculations, charts, and exports is available for local development.")
st.markdown("**Repository:** https://github.com/LT-aitools/rent-vs-buy-decision-tool")