import time
import threading

from config import CHECK_INTERVAL

from score_checker import get_score

from notifier import (
    send_score_notification,
    send_game_end_notification,
)

from starting_monitor import (
    notify_muramatsu_starting,
)

from muramatsu_monitor import (
    monitor_muramatsu_loop,
    muramatsu_stop_event,
)


def monitor_game(game_id):

    from muramatsu_monitor import sent_texts

    sent_texts.clear()

    print("監視開始")

    # スタメン通知
    notify_muramatsu_starting(game_id)

    # 村松監視開始
    muramatsu_stop_event.clear()

    muramatsu_thread = threading.Thread(
        target=monitor_muramatsu_loop,
        args=(game_id,),
        daemon=True
    )

    muramatsu_thread.start()

    # 試合開始待ち
    previous_score = None

    while previous_score is None:

        previous_score = get_score(game_id)

        if previous_score is None:

            print("試合開始待ち...")

            time.sleep(10)

    print("初期スコア:", previous_score)

    # 試合監視
    while True:

        time.sleep(CHECK_INTERVAL)

        current_score = get_score(game_id)

        if current_score is None:

            print("試合情報取得失敗")

            continue

        print("前回スコア:", previous_score)
        print("現在スコア:", current_score)

        # ★ 得点判定ログ
        print(
            f"得点判定 Home: {previous_score['home']} → {current_score['home']}, "
            f"Visitor: {previous_score['visitor']} → {current_score['visitor']}"
        )

        print("------------------------")

        print(
            f"監視中..."
            f"{current_score['home_name']} "
            f"{current_score['home']} - "
            f"{current_score['visitor']} "
            f"{current_score['visitor_name']}"
        )

        # ホーム得点
        if current_score["home"] > previous_score["home"]:

            print("ホーム得点検知")

            send_score_notification(
                current_score["home_name"],
                current_score
            )

        # ビジター得点
        if current_score["visitor"] > previous_score["visitor"]:

            print("ビジター得点検知")

            send_score_notification(
                current_score["visitor_name"],
                current_score
            )

        # 試合終了
        if current_score["game_state"] == "試合終了":

            print("試合終了")

            muramatsu_stop_event.set()

            send_game_end_notification(current_score)

            return

        previous_score = current_score