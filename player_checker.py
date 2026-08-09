import requests

PLAYER_ID = "1750223"

BASE_URL = "https://spaia.jp/baseball/npb/api"


# ==========================
# スタメン取得
# ==========================

def get_starting_member(game_id):

    url = (
        f"{BASE_URL}/starting_members_for_flash"
        f"?gameId={game_id}"
    )

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        return None

    data = response.json()

    for member in data:

        if str(member.get("playerId")) == PLAYER_ID:

            return {
                "name": member.get("playerName"),
                "bat_no": member.get("startBatNo"),
                "position": member.get("startPosition"),
                "number": member.get("backNumber"),
            }

    return None


# ==========================
# game_text取得
# ==========================

def get_game_text(game_id):

    url = (
        f"{BASE_URL}/game_text_pbp"
        f"?GameID={game_id}"
    )

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        return []

    return response.json()


# ==========================
# 新しいイベント取得
# ==========================

def get_new_events(game_id, last_id):

    data = get_game_text(game_id)

    events = []

    for item in data:

        if str(item.get("PlayInfo_PlayerID")) != PLAYER_ID:
            continue

        event_id = item.get("ID")

        if last_id is not None and event_id <= last_id:
            continue

        text = item.get("TextInfo_Bat_Text") or ""

        if not text:
            continue

        events.append({
            "id": event_id,
            "text": text,

            # 通知用情報
            "inning": item.get("Inning"),
            "tb": item.get("TB"),

            "home_name": item.get("H_NameS"),
            "visitor_name": item.get("V_NameS"),

            "home_score": item.get("H_R"),
            "visitor_score": item.get("V_R"),
        })

    return events


# ==========================
# テスト
# ==========================

if __name__ == "__main__":

    game_id = input("GameID: ")

    events = get_new_events(game_id, None)

    print(f"{len(events)}件")

    for event in events:

        print("------------------")
        print("ID      :", event["id"])
        print("Text    :", event["text"])
        print("Inning  :", event["inning"])
        print("TB      :", event["tb"])
        print(
            "Score   :",
            f"{event['home_name']} {event['home_score']} - "
            f"{event['visitor_score']} {event['visitor_name']}"
        )