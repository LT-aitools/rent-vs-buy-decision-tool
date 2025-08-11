import streamlit as st

st.set_page_config(page_title="Connection Test")
st.write("# 🎉 Streamlit Connection Test")
st.write("If you can see this, the connection is working!")
st.write("Now we can proceed with debugging the rental cost issue.")

if st.button("Test Button"):
    st.success("Button clicked successfully!")