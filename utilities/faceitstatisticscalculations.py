import numpy as np

def _calculate_winrate(match_dictionary: dict) -> float:
    if not match_dictionary:
        return 0.00
    results = [int(match.get("Result", 0)) for match in match_dictionary]
    results_array = np.array(results)
    win_percentage = (
        (np.sum(results_array == 1) / len(results_array)) * 100
    )
    return round(float(win_percentage), 2)

def _calculate_point_difference(match_dictionary: dict) -> int:
    if not match_dictionary:
        return 0.00
    results = [int(match.get("Result", 0)) for match in match_dictionary]
    game_scores = [match.get("Score", 0) for match in match_dictionary]
    
    split_score_array = np.array([x.split(' / ') for x in game_scores], dtype=int)
    results_array = np.array(results, dtype=int)
    
    scores_diff_absolute = np.abs(split_score_array[:, 0] - split_score_array[:, 1])
    scores_diff_adjusted = np.where(results_array == 1, scores_diff_absolute, -scores_diff_absolute)
    scores_diff_adjusted_average = np.mean(scores_diff_adjusted)
    print(round(float(scores_diff_adjusted_average), 2))
    return round(float(scores_diff_adjusted_average), 2)

def calculate_stats(match_dictionary: dict) -> dict:
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

    averages = {}
    for key, new_key in key_mapping.items():
        results = [float(match.get(key, 0)) for match in match_dictionary]
        results_array = np.array(results)
        results_array_average = np.mean(results_array)
        averages[new_key] = round(float(results_array_average), 2)

    averages["perc_winrate"] = _calculate_winrate(match_dictionary)
    averages["avg_score_diff"] = _calculate_point_difference(match_dictionary)

    return averages