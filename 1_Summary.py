import streamlit as st
from utilities import pageelements

# Set config
st.set_page_config(page_title = "Email Sender", layout = "wide")

# Page contents
with st.container():
    left_column, middle_column, right_column = st.columns([0.2, 0.6, 0.2])
    with middle_column:
        # Header
        st.header("Faceit Stats DS")
        pageelements.large_vertical_space(1)

        # User Input
        user_input = st.text_input("Enter Faceit Nickname:", max_chars=12)
        pageelements.small_vertical_space(1)

        if user_input:
            pass
