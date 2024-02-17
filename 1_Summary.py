import streamlit as st
from utilities import pageelements
from utilities.faceitstatisticsretrieval import RetrieveFaceitData

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
            # Instantiate class from utilities/faceitstatsretrieval.py
            player_data = RetrieveFaceitData(user_input)
            # Trigger request_data method and determine whether
            # response is successful
            response_status = player_data.request_data(
                endpoint_prefix="https://open.faceit.com/data/v4/players?nickname="
            )
            if response_status == 200:
                player_statistics = player_data.retrieve_statistics()
                # Display account information
                left_account_info_column, right_account_info_column = st.columns([0.5, 0.5])
                with left_account_info_column:
                    st.write(f"Faceit Username: {player_statistics.get("nickname")}")
                with right_account_info_column:
                    try:
                        st.image(player_statistics.get("avatar-image"), width=200)
                    except:
                        st.image('./resources/steamdefault.png', width=200)
                # Display Metrics
                left_metric_column, right_metric_column = st.columns(2)
                with left_metric_column:
                    st.metric("Elo", str(player_statistics.get("elo")))
                with right_metric_column:
                    st.metric("Faceit Level", str(player_statistics.get("skill-level")))
            # Error handling done in RetrieveFaceitData class
