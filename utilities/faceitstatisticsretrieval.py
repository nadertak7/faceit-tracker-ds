# Import modules
import os
from dotenv import load_dotenv
import requests
import streamlit as st

class RetrieveFaceitData:
    """
    A class to retrieve Faceit data for a given player.

    Attributes:
        faceit_name (str): The Faceit username for which data will be retrieved.
        response_api (requests.Response): The response object obtained from the Faceit API.
    """
    # Load secrets
    load_dotenv()
 
    # Initialise instance variables
    def __init__(self, faceit_name):
        """
        Initialise the RetrieveFaceitData object.

        Parameters:
            faceit_name (str): The Faceit username for which data will be retrieved.
        """
        self.faceit_name = faceit_name

    def request_data(self, endpoint_prefix):
        """
        Send a GET request to the Faceit API to retrieve player data.

        Parameters:
            endpoint_prefix (str): The Faceit endpoint selected to retrieve data from.

        Raises:
            Exception: If the player is not found or an error occurs during the request.
        
        Returns: 
            status_code (int): The status code of the response. 
        """
        # Set GET request args
        headers = {
            # The SERVER_KEY environment variable was generated at:
            # https://developers.faceit.com/apps > select app > api keys > create server side api key
            "Authorization": f"Bearer {os.getenv("SERVER_KEY")}",
            "accept": "application/json"
        }

        endpoint = endpoint_prefix + self.faceit_name

        # GET request
        try:
            response_api = requests.get(
                endpoint, 
                headers=headers, 
                timeout=100
            )
            # Error handling
            if response_api.status_code == 200:
                st.toast("Success")
                self.response_api = response_api
            elif response_api.status_code == 404:
                raise Exception("Player was not found. Please ensure the nickname entered is correct.")
            else:
                raise Exception("Something went wrong.")
        except Exception as exception:
            st.error(f"An error occurred: {exception}")
        return response_api.status_code
    
    def retrieve_statistics(self):
        """
        Retrieve statistics from the response obtained from the Faceit API.

        Returns:
            dict: A dictionary containing player statistics.
        """
        player_summary = self.response_api.json()

        cs2_player_data = (player_summary
                   .get('games', {})
                   .get('cs2', {})
        )

        player_statistics = {
            "nickname": player_summary.get('nickname'),
            "skill-level": cs2_player_data.get('skill_level', 0),
            "elo": cs2_player_data.get('faceit_elo', 0),
            "avatar-image": player_summary.get('avatar')
        }
        return player_statistics
