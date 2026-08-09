import json
import requests

BASE_URL = "https://spaia.jp/baseball/npb/api"

game_id = input("GameID: ")

url = f"{BASE_URL}/game_text_pbp?GameID={game_id}"

response = requests.get(url)

data = response.json()

for item in data:

    if str(item.get("PlayInfo_PlayerID")) == "1750223":

        print(json.dumps(item, ensure_ascii=False, indent=2))

        break