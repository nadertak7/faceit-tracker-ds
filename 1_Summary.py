import streamlit as st
from utilities import pageelements
from utilities.faceitstatisticsretrieval import RetrieveFaceitData

# Set config
st.set_page_config(page_title = "Email Sender", layout = "wide")

# Page contents
with st.container():
    left_column, middle_column, right_column = st.columns([0.2, 0.4, 0.4])
    with middle_column:
        # Header
        st.header("Faceit Stats DS")
        pageelements.large_vertical_space(1)

        # User Input
        user_input = st.text_input("Enter Faceit Nickname:")
        pageelements.small_vertical_space(1)

        if user_input:
            # Instantiate class from utilities/faceitstatsretrieval.py
            faceit_data = RetrieveFaceitData(user_input)
            # Trigger request_data method and determine whether
            # response is successful
            response_status = faceit_data.request_data()
            if response_status == 200:
                player_statistics = faceit_data.retrieve_statistics()

                left_metric_column, right_metric_column = st.columns(2)
                left_metric_column.metric("Elo", player_statistics.get("elo"))
                right_metric_column.metric("Faceit Level", player_statistics.get("skill-level"))
