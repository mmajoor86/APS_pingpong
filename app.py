import streamlit as st

import page_1
import page_2

# Sidebar with options to navigate between pages
st.title("🏓 The APS Ping-Pong League🏓")
st.sidebar.title("🚀 Navigation")
selection = st.sidebar.radio(
    label="Select Page",
    label_visibility="hidden",
    options=["Match Registration", "📊 Rankings"],
)


# Depending on the selection, call the relevant page
if selection == "Match Registration":
    page_1.app()
elif selection == "📊 Rankings":
    page_2.app()
