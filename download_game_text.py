import json
import requests

BASE_URL = "https://spaia.jp/baseball/npb/api"

game_id = input("GameID: ")

url = (
    f"{BASE_URL}/game_text_pbp"
    f"?GameID={game_id}"
)

response = requests.get(url, timeout=10)

print("Status:", response.status_code)

if response.status_code != 200:
    print(response.text)
    exit()

data = response.json()

filename = "game_text_pbp.json"

with open(
    filename,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        data,
        f,
        ensure_ascii=False,
        indent=2
    )

print(f"保存完了：{filename}")
print(f"件数：{len(data)}")