import requests


def get_score(game_id):
    url = f"https://spaia.jp/baseball/npb/api/live_games?GameID={game_id}"

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        return None

    data = response.json()

    if not data:
        return None

    game = data[0]

    return {
        "home_name": game["H_Score_NameS"],
        "visitor_name": game["V_Score_NameS"],
        "home": game["H_Score_R"],
        "visitor": game["V_Score_R"],
        "inning": game["Inning"],
        "tb": game["TB"],
        "game_state": game["GameStateName"],
    }