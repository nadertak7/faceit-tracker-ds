from typing import List, Dict

import numpy as np

def _calculate_winrate(match_dictionary: List[Dict]) -> float:
    """Caluclates a player's winrate from a list of boolean match results

    Args:
        match_dictionary (List[Dict]): The match data to calculate from

    Returns:
        float: The player's winrate
    """
    if not match_dictionary:
        return 0.00
    results = [int(match.get("Result", 0)) for match in match_dictionary]
    results_array = np.array(results)
    # Calculates percentage of 1 values in the array of player results
    win_percentage = (
        (np.sum(results_array == 1) / len(results_array)) * 100
    )
    return round(float(win_percentage), 2)

def _calculate_point_difference(match_dictionary: List[Dict]) -> int:
    """Calculates the average point difference from a list of boolean match
    results and scores

    Args:
        match_dictionary (List[Dict]): The match data to calculate from

    Returns:
        int: The player's average point difference
    """
    if not match_dictionary:
        return 0.00
    results = [int(match.get("Result", 0)) for match in match_dictionary]
    game_scores = [match.get("Score", 0) for match in match_dictionary]

    # Splits strings in formats "n1 / n2"
    split_score_array = np.array([x.split(' / ') for x in game_scores], dtype=int)
    results_array = np.array(results, dtype=int)

    # Calculates absolute score difference
    scores_diff_absolute = np.abs(split_score_array[:, 0] - split_score_array[:, 1])
    # Returns a negative score difference for a loss and positive for a win
    scores_diff_adjusted = np.where(results_array == 1, scores_diff_absolute, -scores_diff_absolute)
    scores_diff_adjusted_average = np.mean(scores_diff_adjusted)
    print(round(float(scores_diff_adjusted_average), 2))
    return round(float(scores_diff_adjusted_average), 2)

def calculate_stats(match_dictionary: List[Dict]) -> Dict[str, float]:
    """Calculates a number of metrics that already exist in the endpoint.
    Then adds the hidden methods above to the same data structure

    Args:
        match_dictionary (List[Dict]): The match data to calculate from

    Returns:
        Dict[str, float]: A dictionary of the player's various calculated statistics
    """
    key_mapping = {
        "Kills": "avg_kills",
        "K/R Ratio": "avg_kr_ratio",
        "K/D Ratio": "avg_kd_ratio",
        "Headshots %": "avg_hsp",
        "Double Kills": "avg_2_kills",
        "Triple Kills": "avg_3_kills",
        "Quadro Kills": "avg_4_kills",
        "Penta Kills": "avg_5_kills",
        # Custom metrics which do not need a key
        "perc_winrate": "perc_winrate",
        "avg_score_diff": "avg_score_diff"
    }

    if not match_dictionary:
        return {value: 0.00 for value in key_mapping.values()}

    # Looks at the endpoint response for most items in the key_mapping dict
    averages = {}
    for key, new_key in key_mapping.items():
        results = [float(match.get(key, 0)) for match in match_dictionary]
        results_array = np.array(results)
        results_array_average = np.mean(results_array)
        averages[new_key] = round(float(results_array_average), 2)

    # Adds the custom calculations from the above.
    averages["perc_winrate"] = _calculate_winrate(match_dictionary)
    averages["avg_score_diff"] = _calculate_point_difference(match_dictionary)

    return averages
