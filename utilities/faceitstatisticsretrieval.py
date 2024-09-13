from dataclasses import dataclass
import os
from typing import Dict

from dotenv import load_dotenv
from glom import glom
import requests
import streamlit as st

@dataclass
class FaceitEndpoints:
    player_info: str = "https://open.faceit.com/data/v4/players?nickname={nickname}"
    player_bans: str = "https://open.faceit.com/data/v4/players/{player_id}/bans"

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
    elo: int

@dataclass
class PlayerBanInformation:
    is_banned: bool
    is_smurf: bool
    num_bans: int
    ban_response: dict

class FaceitDataRetrieval:
    def __init__(
        self,
        faceit_nickname
    ) -> None:
        self.faceit_nickname = faceit_nickname
        self.headers = self._initialise_api()
        self.player_data = (self
            ._request_data(FaceitEndpoints.player_info
                .format(nickname=self.faceit_nickname)
            )
        )
        self.player_id = self.player_data.get("player_id")
        self.player_ban_data = (self
            ._request_data(FaceitEndpoints.player_bans
                .format(player_id=self.player_id)
            )
        )

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
            "Authorization": f"bearer {bearer}",
            "accept": "application/json"
        }
        return headers

    def _request_data(
            self,
            endpoint
    ) -> requests.Response:
        try:
            response_api = requests.get(
                endpoint.strip(),
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

    def player_data_ban_store(self) -> PlayerBanInformation:
        player_ban_items = self.player_ban_data.get("items", [])
        return PlayerBanInformation(
            is_banned=False if len(player_ban_items) == 0 else True,
            is_smurf=any(item.get("reason") == "smurfing" for item in player_ban_items),
            num_bans=len(player_ban_items),
            ban_response=player_ban_items
        )
