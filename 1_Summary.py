from pydantic import BaseModel, field_validator, ValidationError
import streamlit as st
from utilities import pageelements
from services.faceitstatisticsretrieval import FaceitDataRetrieval

class PlayerInput(BaseModel):
    player_name: str

    @field_validator('player_name')
    def validate_player_name(cls, faceit_name: str):
        if len(faceit_name) < 3:
            st.error('Player name must be at least 3 characters long.')
        if len(faceit_name) > 12:
            st.error('Player name must be no more than 12 characters long.')
        if not all(char.isalnum() or char in {'_', '-'} for char in faceit_name):
            st.error("Player name can only contain letters, numbers, '_' and '-'.")
        return faceit_name

# Set config
st.set_page_config(page_title = "Faceit Tracker DS", layout = "wide")

# Page contents
with st.container():
    left_column, middle_column, right_column = st.columns([0.2, 0.6, 0.2])
    with middle_column:
        # Header
        st.header("Faceit Stats DS")
        pageelements.large_vertical_space(1)

        # User Input
        user_input = player_name = st.text_input(
            "Enter Faceit Nickname:",
            max_chars=12
        )
        pageelements.small_vertical_space(1)

        if user_input:
            try:
                validated_input = PlayerInput(player_name=user_input)
            except ValidationError as validation_error:
                # TODO: Add log validation_error.errors()[0]['msg']
                pass