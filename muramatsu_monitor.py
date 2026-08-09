import threading
import time

from player_checker import get_new_events

from notifier import (
    send_muramatsu_atbat_notification,
    send_muramatsu_result_notification,
)

CHECK_INTERVAL = 5

muramatsu_stop_event = threading.Event()

# 通知済みテキスト
sent_texts = set()

# 打席開始時の状況（例：無死一塁）
last_atbat_info = None

# 打席終了とみなすキーワード
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


def monitor_muramatsu_loop(game_id):

    global sent_texts
    global last_atbat_info

    print("村松監視開始")

    # 起動前のイベントは通知しない
    events = get_new_events(game_id, None)

    for event in events:
        sent_texts.add(event["text"])

    print(f"{len(sent_texts)}件の過去イベントをスキップしました")

    while not muramatsu_stop_event.is_set():

        try:

            events = get_new_events(game_id, None)

            for event in events:

                text = event["text"]

                # 同じ本文は通知しない
                if text in sent_texts:
                    continue

                sent_texts.add(text)

                # 打席開始
                if text.startswith("＜"):

                    # 「＜2番：村松＞無死一塁」→「無死一塁」
                    if "＞" in text:
                        last_atbat_info = text.split("＞", 1)[1].strip()
                    else:
                        last_atbat_info = ""

                    send_muramatsu_atbat_notification(event)

                # 打席結果
                elif any(keyword in text for keyword in RESULT_KEYWORDS):

                    send_muramatsu_result_notification(
                        event,
                        last_atbat_info
                    )

        except Exception as e:

            print("村松監視エラー:", e)

        time.sleep(CHECK_INTERVAL)

    print("村松監視終了")


if __name__ == "__main__":

    game_id = input("GameID: ")

    print("=== 村松監視テスト ===")

    monitor = threading.Thread(
        target=monitor_muramatsu_loop,
        args=(game_id,),
        daemon=True
    )

    monitor.start()

    try:

        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        muramatsu_stop_event.set()

        monitor.join()

        print("終了")