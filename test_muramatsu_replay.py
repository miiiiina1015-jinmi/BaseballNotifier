import time

from notifier import (
    send_muramatsu_atbat_notification,
    send_muramatsu_result_notification,
)

# ==========================
# テストデータ
# ==========================

events = [

    {
        "id": 1,
        "inning": "1",
        "tb": "2",
        "home_name": "中日",
        "visitor_name": "阪神",
        "home_score": "0",
        "visitor_score": "0",
        "text": "＜2番：村松＞無死一塁"
    },

    {
        "id": 2,
        "inning": "1",
        "tb": "2",
        "home_name": "中日",
        "visitor_name": "阪神",
        "home_score": "0",
        "visitor_score": "0",
        "text": "1球目:ストライク"
    },

    {
        "id": 3,
        "inning": "1",
        "tb": "2",
        "home_name": "中日",
        "visitor_name": "阪神",
        "home_score": "0",
        "visitor_score": "0",
        "text": "2球目:ファウル"
    },

    {
        "id": 4,
        "inning": "1",
        "tb": "2",
        "home_name": "中日",
        "visitor_name": "阪神",
        "home_score": "0",
        "visitor_score": "0",
        "text": "4球目:センターフライ 1アウト"
    }

]

RESULT_KEYWORDS = (
    "アウト",
    "ヒット",
    "安打",
    "二塁打",
    "三塁打",
    "ホームラン",
    "本塁打",
    "四球",
    "死球",
    "送りバント",
    "犠打",
    "犠飛",
    "併殺",
    "失策",
    "エラー",
)

last_atbat_info = ""

print("===== リプレイ開始 =====")

for event in events:

    print(f"EVENT {event['id']} : {event['text']}")

    text = event["text"]

    if text.startswith("＜"):

        last_atbat_info = text.split("＞", 1)[1].strip()

        send_muramatsu_atbat_notification(event)

    elif any(keyword in text for keyword in RESULT_KEYWORDS):

        send_muramatsu_result_notification(
            event,
            last_atbat_info
        )

    time.sleep(2)

print("===== リプレイ終了 =====")