from dataclasses import dataclass
import os
from typing import Dict

from dotenv import load_dotenv
from glom import glom
import requests
import streamlit as st
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities.faceitstatisticscalculations import calculate_stats

@dataclass
class FaceitEndpoints:
    player_info: str = "https://open.faceit.com/data/v4/players?nickname={nickname}"
    player_bans: str = "https://open.faceit.com/data/v4/players/{player_id}/bans"
    player_statistics: str = "https://open.faceit.com/data/v4/players/{player_id}/games/{game_id}/stats?offset={offset}&limit={limit}"

@dataclass
class ApiArguments:
    headers: Dict[str, str]
    endpoint: str

@dataclass
class PlayerInformationData:
    player_id: str
    nickname: str
    avatar: str
    num_friends: int
    is_verified: bool
    skill_level: int
    elo: int

@dataclass
class PlayerBanInformationData:
    player_id: str
    is_banned: bool
    is_smurf: bool
    num_bans: int
    ban_response: dict

@dataclass
class PlayerStatisticsAllTimeData:
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

@dataclass
class PlayerStatisticsLast20Data:
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

@dataclass
class PlayerStatisticsFirst10Data:
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
        self.player_cs2_game_stats = self.fetch_cs_game_stats("cs2")
        self.player_csgo_game_stats = self.fetch_cs_game_stats("csgo")
        self.all_cs_game_stats = self.player_cs2_game_stats + self.player_csgo_game_stats

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

    def player_data_store(self) -> PlayerInformationData:
        return PlayerInformationData(
            player_id=self.player_data.get("player_id"),
            nickname=self.player_data.get("nickname"),
            avatar=self.player_data.get("avatar"),
            num_friends=len(self.player_data.get("friends_ids", [])),
            is_verified=self.player_data.get("verified"),
            skill_level=glom(self.player_data, "games.cs2.skill_level", default=0),
            elo=glom(self.player_data, "games.cs2.faceit_elo", default=0)
        )

    def player_data_ban_store(self) -> PlayerBanInformationData:
        player_ban_items = self.player_ban_data.get("items", [])
        return PlayerBanInformationData(
            player_id = self.player_id,
            is_banned=False if len(player_ban_items) == 0 else True,
            is_smurf=any(item.get("reason") == "smurfing" for item in player_ban_items),
            num_bans=len(player_ban_items),
            ban_response=player_ban_items
        )
    

    def fetch_cs_game_stats(self, game_id):
        match_stats = []
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

    def player_data_stats_all_time_store(self):
        return PlayerStatisticsAllTimeData(self.player_id, **calculate_stats(self.all_cs_game_stats))
    
    def player_data_stats_last_20_store(self):
        last_20_cs_game_stats = self.all_cs_game_stats[:20]
        return PlayerStatisticsLast20Data(self.player_id, **calculate_stats(last_20_cs_game_stats))
    
    def player_data_stats_first_10_store(self):
        first_10_cs_game_stats = self.all_cs_game_stats[-len(self.all_cs_game_stats):-len(self.all_cs_game_stats) + 10]
        return PlayerStatisticsFirst10Data(self.player_id, **calculate_stats(first_10_cs_game_stats))

print(FaceitDataRetrieval("NadseN").player_data_stats_all_time_store())

