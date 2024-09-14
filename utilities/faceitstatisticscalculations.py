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
        "Winrate": "perc_winrate"
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
    
    return averages