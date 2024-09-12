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
    player_id: str
    nickname: str
    avatar: str
    num_friends: int
    is_verified: bool
    skill_level: int
    elo: int = 0
    num_bans: int = 0

@dataclass
class PlayerBanInformation:
    is_banned: bool
    is_smurf: bool
    num_bans: int

class FaceitDataRetrieval:
    def __init__(
        self,
        faceit_nickname
    ) -> None:
        self.faceit_nickname = faceit_nickname
        self.headers = self._initialise_api()
        self.player_data = self._request_data(f"""
            https://open.faceit.com/data/v4/players?nickname={self.faceit_nickname}
        """)
        self.player_id = self.player_data.get("player_id")
        self.player_ban_data = self._request_data(f"""
            https://open.faceit.com/data/v4/players/{self.player_id}/bans
        """)

    @staticmethod
    def _initialise_api() -> Dict[str, str]:
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
        return headers

    def _request_data(
            self,
            endpoint
    ) -> requests.Response:
        try:
            response_api = requests.get(
                endpoint,
                headers=self.headers,
                timeout=20
            )
            response_api.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            st.error(f"Http Error: {http_error}")
        except requests.exceptions.ConnectionError as conn_error:
            st.error(f"Error Connecting: {conn_error}")
        except requests.exceptions.Timeout as timeout_error:
            st.error(f"Timeout Error: {timeout_error}")
        except requests.exceptions.RequestException as req_error:
            st.error(f"An Error Occurred: {req_error}")
        return response_api.json()

    def player_data_store(self) -> PlayerInformation:
        return PlayerInformation(
            player_id=self.player_data.get("player_id"),
            nickname=self.player_data.get("nickname"),
            avatar=self.player_data.get("avatar"),
            num_friends=len(self.player_data.get("friends_ids", [])),
            is_verified=self.player_data.get("verified"),
            skill_level=glom(self.player_data, "games.cs2.skill_level", default=0),
            elo=glom(self.player_data, "games.cs2.faceit_elo", default=0)
        )

    # TODO: Basic preliminary model. Needs investigation.
    # def player_data_ban_store(self) -> PlayerBanInformation:
    #     return PlayerBanInformation(
    #         is_banned=True if glom(self.player_ban_data, "items", default=None) else False,
    #         is_smurf=True if glom(self.player_ban_data, "items", default=None) else False,
    #         num_bans=len(self.player_ban_data.get("items", []))
    #     )

# print(FaceitDataRetrieval("nadumtax").player_data_ban_store())
