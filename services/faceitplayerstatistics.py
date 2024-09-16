from dataclasses import dataclass
import os
from typing import Dict

from dotenv import load_dotenv
from glom import glom
import requests
import streamlit as st

# Allow access to utilities folder
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities.faceitstatisticscalculations import calculate_stats

@dataclass
class FaceitEndpoints:
    """API endpoints that retrieve relevant player information"""
    player_info: str = "https://open.faceit.com/data/v4/players?nickname={nickname}"
    player_bans: str = "https://open.faceit.com/data/v4/players/{player_id}/bans"
    player_statistics: str = """
        https://open.faceit.com/data/v4/players/{player_id}/games/{game_id}/stats?offset={offset}&limit={limit}
    """

@dataclass
class PlayerInformationData:
    """A store for information about the player"""
    player_id: str
    nickname: str
    avatar: str
    num_friends: int
    is_verified: bool
    skill_level: int
    elo: int
    num_games: int

@dataclass
class PlayerBanInformationData:
    """A store for informaiton about the player's bans"""
    player_id: str
    is_banned: bool
    is_smurf: bool
    num_bans: int
    ban_response: dict

@dataclass
class PlayerStatisticsAllTimeData:
    """A store for the player's performance in Faceit across all their games"""
    player_id: str
    avg_kills: float
    avg_kr_ratio: float
    avg_kd_ratio: float
    avg_hsp: float
    avg_2_kills: float
    avg_3_kills: float
    avg_4_kills: float
    avg_5_kills: float
    perc_winrate: float
    avg_score_diff: float

@dataclass
class PlayerStatisticsLast20Data:
    """A store for the player's performance in Faceit in their last 20 games"""
    player_id: str
    avg_kills: float
    avg_kr_ratio: float
    avg_kd_ratio: float
    avg_hsp: float
    avg_2_kills: float
    avg_3_kills: float
    avg_4_kills: float
    avg_5_kills: float
    perc_winrate: float
    avg_score_diff: float

@dataclass
class PlayerStatisticsFirst10Data:
    """A store for the player's performance in Faceit in their first 10 games"""
    player_id: str
    avg_kills: float
    avg_kr_ratio: float
    avg_kd_ratio: float
    avg_hsp: float
    avg_2_kills: float
    avg_3_kills: float
    avg_4_kills: float
    avg_5_kills: float
    perc_winrate: float
    avg_score_diff: float

class PlayerFaceitDataRetrieval:
    """Handles the retrieval of a player's Faceit data"""
    def __init__(
        self,
        faceit_nickname: str
    ) -> None:
        """Initialises the class and its attributes

        Args:
            faceit_nickname (str): The nickname of the player on faceit
        """
        self.faceit_nickname = faceit_nickname
        self.headers = self._initialise_api_header()
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
        self.player_cs2_game_stats = self._request_faceit_match_data("cs2")
        self.player_csgo_game_stats = self._request_faceit_match_data("csgo")
        self.all_cs_game_stats = self.player_cs2_game_stats + self.player_csgo_game_stats

    @staticmethod
    def _initialise_api_header() -> Dict[str, str]:
        """Loads the header that will be used for each request

        Raises:
            KeyError: If the SERVER_KEY environment variable does not exist

        Returns:
            Dict[str, str]: Headers for the get request
        """
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
            endpoint: str
    ) -> requests.Response:
        """Sends a request to the provided API endpoint, handling errors in the process

        Args:
            endpoint (str): The endpoint URL

        Returns:
            requests.Response: The response of the get request
        """
        try:
            response_api = requests.get(
                # strip method is needed due to formatting of multi-line strings
                endpoint.strip(),
                headers=self.headers,
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

    def player_data_store(self) -> PlayerInformationData:
        """Inserts the player's information into the PlayerInformationData dataclass"""
        return PlayerInformationData(
            player_id=self.player_data.get("player_id"),
            nickname=self.player_data.get("nickname"),
            avatar=self.player_data.get("avatar"),
            num_friends=len(self.player_data.get("friends_ids", [])),
            is_verified=self.player_data.get("verified"),
            skill_level=glom(self.player_data, "games.cs2.skill_level", default=0),
            elo=glom(self.player_data, "games.cs2.faceit_elo", default=0),
            num_games=len(self.player_cs2_game_stats) + len(self.player_csgo_game_stats)
        )

    def player_data_ban_store(self) -> PlayerBanInformationData:
        """Inserts the player's ban information into the PlayerBanInformationData dataclass"""
        player_ban_items = self.player_ban_data.get("items", [])
        return PlayerBanInformationData(
            player_id = self.player_id,
            is_banned=False if len(player_ban_items) == 0 else True,
            is_smurf=any(item.get("reason") == "smurfing" for item in player_ban_items),
            num_bans=len(player_ban_items),
            ban_response=player_ban_items
        )

    def _request_faceit_match_data(self, game_id: str) -> Dict:
        """Handles paginated stats data"""
        match_stats = []
        # Endpoint fetches results {limit} at a time
        # And adds to offset until end is reached
        offset = 0
        limit = 100
        while True:
            endpoint = FaceitEndpoints.player_statistics.format(
                player_id=self.player_id,
                game_id=game_id,
                offset=offset,
                limit=limit
            )
            player_stats_batch = self._request_data(endpoint)
            items = player_stats_batch.get("items", [])
            if items == []:
                break
            match_stats.extend([item.get("stats") for item in items])
            offset += limit
        return match_stats

    def player_data_stats_all_time_store(self) -> PlayerStatisticsAllTimeData:
        """Inserts the player's all time stats into the relevant dataclass"""
        return PlayerStatisticsAllTimeData(self.player_id, **calculate_stats(self.all_cs_game_stats))

    def player_data_stats_last_20_store(self) -> PlayerStatisticsLast20Data:
        """Inserts the player's last 20 game stats into the relevant dataclass"""
        # Extract first 20 records in all_cs_game_stats
        last_20_cs_game_stats = self.all_cs_game_stats[:20]
        return PlayerStatisticsLast20Data(self.player_id, **calculate_stats(last_20_cs_game_stats))

    def player_data_stats_first_10_store(self):
        # Extract last 10 records in all_cs_game_stats
        """Inserts the player's first 10 game stats into the relevant dataclass"""
        first_10_cs_game_stats = self.all_cs_game_stats[-len(self.all_cs_game_stats):-len(self.all_cs_game_stats) + 10]
        return PlayerStatisticsFirst10Data(self.player_id, **calculate_stats(first_10_cs_game_stats))

print(PlayerFaceitDataRetrieval("nadysen").player_data_store())
