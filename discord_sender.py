import os
import requests


WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")


def send_discord(message):
    if not WEBHOOK_URL:
        print("エラー: DISCORD_WEBHOOK_URL が設定されていません")
        return

    response = requests.post(
        WEBHOOK_URL,
        json={
            "content": message
        }
    )

    print(response.status_code)
    