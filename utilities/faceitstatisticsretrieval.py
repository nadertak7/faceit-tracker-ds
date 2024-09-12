from dataclasses import dataclass
import os
import requests
from typing import Dict, Optional


from dotenv import load_dotenv
from glom import glom
import streamlit as st


@dataclass
class ApiArguments:
    headers: Dict[str, str]
    endpoint: str

@dataclass
class PlayerInformation:
    nickname: str
    avatar: str
    skill_level: Optional[int] = None
    elo: Optional[int] = None
    num_friends = int
    is_verified = bool

class FaceitDataRetrieval:
    def __init__(
        self,
        faceit_nickname
    ) -> None:
        self.faceit_nickname = faceit_nickname
        self.api_arguments = self._initialise_api()
        self.response = self._request_data()

    def _initialise_api(self) -> ApiArguments:
        # Handle server key        
        load_dotenv()
        # The SERVER_KEY environment variable was generated at:
        # https://developers.faceit.com/apps > select app > api keys > create server side api key
        bearer = os.getenv("SERVER_KEY")
        if not bearer:
            raise KeyError("Environment variable 'SERVER_KEY' does not exist")

        headers = {
            "Authorization": f"Bearer {bearer}",
            "accept": "application/json"
        }
        ENDPOINT = f"https://open.faceit.com/data/v4/players?nickname={self.faceit_nickname}"

        api_arguments = ApiArguments(
            headers=headers,
            endpoint=ENDPOINT
        )
        return api_arguments
    
    def _request_data(
            self
    ) -> requests.Response:
        try:
            response_api = requests.get(
                self.api_arguments.endpoint,
                self.api_arguments.headers,
                timeout=20
            )
        except requests.exceptions.HTTPError as http_error:
            st.error(f"Http Error: {http_error}")
        except requests.exceptions.ConnectionError as conn_error:
            st.error(f"Error Connecting: {conn_error}")
        except requests.exceptions.Timeout as timeout_error:
            print (f"Timeout Error: {timeout_error}")
        except requests.exceptions.RequestException as req_error:
            print (f"An Error Occurred: {req_error}")
        return response_api

    def wrangle_player_data(
            self
    ):
        player_summary = self.response.json()

        player_information = PlayerInformation(
            nickname=player_summary.get("nickname"),
            avatar=player_summary.get("avatar"),
            skill_level=glom(player_summary, "games.cs2.skill_level"),
            elo=glom(player_summary, "games.cs2.faceit_elo")
            num_friends=len(player_summary.get("friends_ids")),
            is_verified=player_summary.get("verified")
        )
        return player_information



FaceitDataRetrieval("hellotest")