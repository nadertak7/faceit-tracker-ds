import streamlit as st
from utilities import spacing

# Set config
st.set_page_config(page_title = "Email Sender", layout = "wide")

# Header
with st.container():
    left_column, middle_column, right_column = st.columns([0.2, 0.4, 0.4])
    with middle_column:
        st.header("Faceit Stats DS")
        spacing.large_vertical_space(5)
        st.text_input("Enter Faceit Nickname:")