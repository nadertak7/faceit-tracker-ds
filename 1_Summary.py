import streamlit as st
from utilities import pageelements
from utilities.faceitstatisticsretrieval import RetrieveFaceitData

# Set config
st.set_page_config(page_title = "Email Sender", layout = "wide")

# Header
with st.container():
    left_column, middle_column, right_column = st.columns([0.2, 0.4, 0.4])
    with middle_column:
        st.header("Faceit Stats DS")
        pageelements.large_vertical_space(1)
        user_input = st.text_input("Enter Faceit Nickname:")
        pageelements.small_vertical_space(1)

        if user_input:
            faceit_data = RetrieveFaceitData(user_input)
            faceit_data.request_data()
            player_statistics = faceit_data.retrieve_statistics()

            left_metric_column, right_metric_column = st.columns(2)
            left_metric_column.metric("Elo", player_statistics.get("elo"))
            right_metric_column.metric("Faceit Level", player_statistics.get("skill-level"))

