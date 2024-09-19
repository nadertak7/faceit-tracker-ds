from dataclasses import dataclass
import datetime
import os
import requests
from typing import Optional

from dotenv import load_dotenv
from glom import glom
import streamlit as st

# Allow access to utilities folder
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities.steamstatisticscalculations import unixtime_to_date, get_steam_games_stats

@dataclass
class SteamEndpoints:
    """API Endpoints that retreive relevant player steam information"""
    player_summary = """
        http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={steam_key}&steamids={steam_id}
    """
    player_games = """
        https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={steam_key}&steamid={steam_id}&include_appinfo=true&include_played_free_games=true
    """
    player_friends = """
    http://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={steam_key}&steamid={steam_id}&relationship=friend
    """

@dataclass
class PlayerSteamSummaryData:
    "A store for summary information about a player's steam profile"
    steam_id: int
    is_private: bool
    is_private_gamedata: bool
    created_at: Optional[datetime.datetime] = None

@dataclass
class PlayerSteamFriendsData:
    steam_id: int
    num_steam_friends: Optional[int] = None

@dataclass
class PlayerSteamGameData:
    steam_id: int
    num_games: Optional[int] = None
    playtime_cs2_mins: Optional[int] = None
    playtime_all_games_stdev: Optional[float] = None
    perc_cs2_playtime_all_games: Optional[float] = None
    perc_cs2_playtime_account_age: Optional[float] = None


class PlayerSteamDataRetrieval:
    """Handles the retrieval of a player's steam data."""
    def __init__(
        self,
        steam_id: int
    ) -> None:
        self.steam_id = steam_id
        self.steam_key = self._initialise_api_key()
        self.player_summary_data = (
            self
            ._request_data(SteamEndpoints.player_summary
                .format(
                    steam_key=self.steam_key,
                    steam_id=self.steam_id
                )
            )
        )
        self.player_games_data = (
            self
            ._request_data(SteamEndpoints.player_games
                .format(
                    steam_key=self.steam_key,
                    steam_id=self.steam_id
                )
            )
        )
        self.player_friends_data = (
            self
            ._request_data(SteamEndpoints.player_friends
                .format(
                    steam_key=self.steam_key,
                    steam_id=self.steam_id
                )
            )
        )
        self.player_summary_instance = self.player_steam_summary_data_store()

    @staticmethod
    def _initialise_api_key() -> str:
        """Loads the API Key that will be used for each request

        Raises:
            KeyError: If the STEAM_KEY environment variable does not exist

        Returns:
            str: The steam_key used in the API endpoint
        """
        load_dotenv()
        key = os.getenv("STEAM_KEY")
        if not key:
            raise KeyError("Environment Variable 'STEAM_KEY' does not exist")
        return key

    def _request_data(
        self,
        endpoint: str
    ) -> requests.Response:
        try:
            response_api = requests.get(
                # strip method is needed due to formatting of multi-line strings
                endpoint.strip(),
                timeout=20
            )
            response_api.raise_for_status()
        # Handle errors and present to user on front-end
        except requests.exceptions.HTTPError as http_error:
            st.error(f"Http Error: {http_error}")
        except requests.exceptions.ConnectionError as conn_error:
            st.error(f"Error Connecting: {conn_error}")
        except requests.exceptions.Timeout as timeout_error:
            st.error(f"Timeout Error: {timeout_error}")
        except requests.exceptions.RequestException as req_error:
            st.error(f"An Error Occurred: {req_error}")
        return response_api.json()

    def player_steam_summary_data_store(self) -> PlayerSteamSummaryData:
        """Inserts the player's steam summary information into the PlayerSteamData dataclass"""
        is_private_steam = any([
            glom(
                self.player_summary_data,
                "response.players.0.communityvisibilitystate",
                default=False
            ) == 1
        ])

        is_private_gamedata = any([
            self.player_games_data.get("response", False) == {}
        ])

        # If steam is private, use default values
        if any([is_private_steam, is_private_gamedata]):
            return PlayerSteamSummaryData(
                steam_id=self.steam_id,
                is_private=is_private_steam,
                is_private_gamedata=is_private_gamedata
            )

        steam_created_at_unix = glom(
            self.player_summary_data,
            "response.players.0.timecreated",
            default=None
        )
        steam_created_at = unixtime_to_date(steam_created_at_unix)

        return PlayerSteamSummaryData(
            steam_id=self.steam_id,
            is_private=is_private_steam,
            is_private_gamedata=is_private_gamedata,
            created_at=steam_created_at
        )

    def player_steam_friends_data_store(self) -> PlayerSteamFriendsData:
        if any([
            self.player_summary_instance.is_private,
            self.player_summary_instance.is_private_gamedata
        ]):
            return PlayerSteamFriendsData(steam_id=self.steam_id)

        num_steam_friends = len(glom(
            self.player_friends_data,
            "friendslist.friends",
            default=[]
        ))
        return PlayerSteamFriendsData(
            steam_id=self.steam_id,
            num_steam_friends=num_steam_friends
        )

    def player_steam_game_data_store(self) -> PlayerSteamGameData:
        if any([
            self.player_summary_instance.is_private,
            self.player_summary_instance.is_private_gamedata
        ]):
            return PlayerSteamGameData(steam_id=self.steam_id)

        return PlayerSteamGameData(
            steam_id=self.steam_id,
            **get_steam_games_stats(
                self.player_games_data,
                steam_created_at=self.player_summary_instance.created_at
            )
        )

# steam_data_instance = PlayerSteamDataRetrieval(76561198067301616)
# print(steam_data_instance.player_steam_summary_data_store())
# print(steam_data_instance.player_steam_friends_data_store())
# print(steam_data_instance.player_steam_game_data_store())
