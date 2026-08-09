from datetime import datetime, timedelta
import time

from game_checker import (
    get_dragons_game_id,
    get_next_dragons_game,
)

from score_checker import get_score

from game_monitor import monitor_game

from notifier import (
    send_game_start_notification,
    send_before_game_notification,
)


def wait_until_game_start(next_game):

    # 次の試合が見つからない場合
    if next_game is None:

        print(
            "次の試合が見つかりません"
        )

        return False

    game_date = next_game.get("date")
    start_time = next_game.get("start_time")

    # 試合日・開始時刻が取得できない場合
    if not game_date or not start_time:

        print(
            "試合日または開始時刻を取得できないため待機できません"
        )

        return False

    try:

        start_datetime = datetime.strptime(
            game_date + start_time,
            "%Y%m%d%H:%M"
        )

    except ValueError:

        print(
            f"試合開始時刻の解析に失敗しました: "
            f"{game_date} {start_time}"
        )

        return False

    # 試合開始30分前
    notify_datetime = start_datetime - timedelta(
        minutes=30
    )

    notified = False

    print(
        f"次の試合：{game_date} {start_time}"
    )

    # 待機ログ用
    last_log_time = None

    while True:

        now = datetime.now()

        # --------------------------------
        # すでに試合開始時刻を過ぎている
        # --------------------------------

        if now >= start_datetime:

            print(
                "試合開始時刻になりました"
            )

            send_game_start_notification()

            return True

        # --------------------------------
        # 試合開始30分前通知
        # --------------------------------

        if (
            not notified
            and now >= notify_datetime
        ):

            send_before_game_notification(
                game_date,
                start_time
            )

            notified = True

        # --------------------------------
        # 5分ごとに待機ログ
        # --------------------------------

        if (
            last_log_time is None
            or (
                now - last_log_time
            ).total_seconds() >= 300
        ):

            remaining = (
                start_datetime - now
            )

            total_seconds = max(
                0,
                int(
                    remaining.total_seconds()
                )
            )

            hours = total_seconds // 3600

            minutes = (
                total_seconds % 3600
            ) // 60

            print(
                f"待機中... "
                f"現在 {now.strftime('%H:%M:%S')} "
                f"(試合開始まで "
                f"約{hours}時間{minutes}分)"
            )

            last_log_time = now

        time.sleep(30)


def run_scheduler():

    while True:

        print(
            "今日の中日戦を探しています..."
        )

        # --------------------------------
        # 今日の中日戦を探す
        # --------------------------------

        game_id = get_dragons_game_id()

        if game_id:

            print(
                f"GameID: {game_id}"
            )

            # --------------------------------
            # 試合情報を取得
            # --------------------------------

            score = get_score(game_id)

            # --------------------------------
            # 試合情報が取得できない
            # --------------------------------

            if score is None:

                print(
                    "試合情報を取得できませんでした"
                )

                next_game = get_next_dragons_game()

                if next_game:

                    started = wait_until_game_start(
                        next_game
                    )

                    if started:

                        monitor_game(
                            next_game["game_id"]
                        )

                else:

                    print(
                        "次の中日戦が見つかりません"
                    )

            # --------------------------------
            # 試合終了済み
            # --------------------------------

            elif score["game_state"] == "試合終了":

                print(
                    "現在の試合は終了しています"
                )

                # 終了した試合ではなく、
                # 未来の次の試合を探す
                next_game = get_next_dragons_game()

                if next_game:

                    started = wait_until_game_start(
                        next_game
                    )

                    if started:

                        monitor_game(
                            next_game["game_id"]
                        )

                else:

                    print(
                        "次の中日戦が見つかりません"
                    )

            # --------------------------------
            # 試合前・試合中
            # --------------------------------

            else:

                print(
                    "試合前・試合中のため監視を開始します"
                )

                monitor_game(game_id)

        # --------------------------------
        # 今日の中日戦がない
        # --------------------------------

        else:

            print(
                "今日の中日戦はありません"
            )

            # 次の中日戦を探す
            next_game = get_next_dragons_game()

            if next_game:

                started = wait_until_game_start(
                    next_game
                )

                if started:

                    monitor_game(
                        next_game["game_id"]
                    )

            else:

                print(
                    "次の中日戦が見つかりません"
                )

        # --------------------------------
        # ここまで来たら10分後に再確認
        # --------------------------------

        print(
            "次の日の試合を待機します"
        )

        time.sleep(600)