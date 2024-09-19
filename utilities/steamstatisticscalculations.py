from datetime import date, datetime
from typing import Dict, Union

from glom import glom
import numpy as np

def unixtime_to_date(unixtime: str) -> datetime:
    """Converts unix date returned by steam to datetime

    Args:
        unixtime (str): Steam account created timestamp

    Returns:
        datetime: Account created date
    """
    unixtime_created_at = datetime.fromtimestamp(unixtime)
    date_created_at = unixtime_created_at.date()
    return date_created_at

def get_steam_games_stats(
        game_dictionary: Dict,
        steam_created_at: datetime.date
    ) -> Dict[str, Union[int, float]]:
    """Wrangles endpoint response on steam player's game data

    Args:
        game_dictionary (_type_): _description_
        steam_created_at (_type_): _description_

    Returns:
        Dict[str, Union[int, float]]: _description_
    """
    game_data = glom(game_dictionary, "response.games", default=[])
    playtime_cs2_mins = next(
        (game.get('playtime_forever', None) for game in game_data if game['appid'] == 730),
        0
    )
    playtime_all_games_array = np.array([game["playtime_forever"] for game in game_data])

    try:
        perc_cs2_playtime_all_games = round(100 * (playtime_cs2_mins / int(np.sum(playtime_all_games_array))), 2)
    except ZeroDivisionError:
        perc_cs2_playtime_all_games = 0.0
    time_diff = date.today() - steam_created_at
    account_age_mins = time_diff.total_seconds() / 60

    steam_games_stats = {
        "num_games": len(game_data),
        "playtime_cs2_mins": next((game.get('playtime_forever', 0) for game in game_data if game['appid'] == 730), 0),
        "playtime_all_games_stdev": float(np.std(playtime_all_games_array) if playtime_all_games_array.size > 0 else 0.0),
        "perc_cs2_playtime_all_games": perc_cs2_playtime_all_games,
        "perc_cs2_playtime_account_age": round(100 * playtime_cs2_mins / account_age_mins, 2)
    }

    return steam_games_stats
