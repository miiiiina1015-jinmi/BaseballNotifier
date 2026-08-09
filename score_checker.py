import requests


BASE_URL = "https://spaia.jp/baseball/npb/api"


def _get_json(url):

    try:

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:

        print("スコアAPI取得失敗:", e)

        return None


def get_score(game_id):

    url = (
        f"{BASE_URL}/live_games"
        f"?GameID={game_id}"
    )

    data = _get_json(url)

    if data is None:
        return None

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