import time
import threading

from datetime import datetime, timedelta

from config import CHECK_INTERVAL

from game_checker import (
    get_dragons_game_id,
    get_next_dragons_game
)

from score_checker import get_score

from discord_sender import send_discord


from player_checker import (
    get_starting_member,
    get_current_muramatsu_atbat,
    get_latest_muramatsu_atbat
)



# ==========================
# 設定
# ==========================

# 村松監視間隔
MURAMATSU_CHECK_INTERVAL = 10



# ==========================
# 村松通知管理
# ==========================

# スタメン通知済み
starting_notified_games = set()


# 村松打席通知済み
muramatsu_atbat_serial = None


# 村松結果通知済み
muramatsu_result_serial = None



# ==========================
# 村松監視停止用
# ==========================

muramatsu_stop_event = threading.Event()





# ==========================
# イニング表示
# ==========================

def inning_text(score):

    if score["tb"] == 1:
        return f"{score['inning']}回表"

    if score["tb"] == 2:
        return f"{score['inning']}回裏"

    return ""







# ==========================
# 得点通知
# ==========================

def notify_score(team_name, score):

    message = (
        f"⚾ {team_name}が得点！\n\n"
        f"📊 {score['home_name']} "
        f"{score['home']} - "
        f"{score['visitor']} "
        f"{score['visitor_name']}\n"
        f"🕒 {inning_text(score)}"
    )


    print(message)

    send_discord(message)







# ==========================
# 村松スタメン通知
# ==========================

def notify_muramatsu_starting(game_id):


    if game_id in starting_notified_games:

        return



    starter = get_starting_member(
        game_id
    )


    if starter is None:

        return



    starting_notified_games.add(
        game_id
    )



    message = (
        "⚾ スタメン発表\n\n"
        "村松開人選手\n\n"
        f"打順：{starter['bat_no']}番\n"
        f"守備：遊撃\n"
        f"背番号：{starter['number']}"
    )


    print(message)

    send_discord(message)







# ==========================
# 村松打席通知
# ==========================

def notify_muramatsu_atbat(atbat):

    global muramatsu_atbat_serial



    if atbat is None:

        return



    serial = atbat["serial"]



    if serial == muramatsu_atbat_serial:

        return



    muramatsu_atbat_serial = serial



    message = (
        "⚾ 村松開人選手 打席へ\n\n"
        f"打席ID：{serial}"
    )


    print(message)

    send_discord(message)








# ==========================
# 村松打席結果通知
# ==========================

def notify_muramatsu_result(result):

    global muramatsu_result_serial



    if result is None:

        return



    serial = result["serial"]



    if serial == muramatsu_result_serial:

        return



    # まだ打席継続中

    if result["bresult"] == "打席継続":

        return



    muramatsu_result_serial = serial



    message = (
        "⚾ 村松開人選手 打席結果\n\n"
        f"結果：{result['bresult']}"
    )


    print(message)

    send_discord(message)
    # ==========================
# 村松監視ループ
# ==========================

def monitor_muramatsu_loop(game_id):

    print(
        "村松監視開始"
    )


    while not muramatsu_stop_event.is_set():


        try:


            # 現在打席確認

            current_atbat = get_current_muramatsu_atbat(
                game_id
            )


            if current_atbat:

                notify_muramatsu_atbat(
                    current_atbat
                )



            # 結果確認

            result = get_latest_muramatsu_atbat(
                game_id
            )


            if result:

                notify_muramatsu_result(
                    result
                )



        except Exception as e:


            print(
                "村松監視エラー:",
                e
            )



        # 10秒待機

        muramatsu_stop_event.wait(
            MURAMATSU_CHECK_INTERVAL
        )



    print(
        "村松監視終了"
    )








# ==========================
# 試合監視
# ==========================

def monitor_game(game_id):


    print(
        "監視開始"
    )



    # 村松スタメン確認

    notify_muramatsu_starting(
        game_id
    )



    # 村松監視開始

    muramatsu_stop_event.clear()



    muramatsu_thread = threading.Thread(
        target=monitor_muramatsu_loop,
        args=(game_id,),
        daemon=True
    )


    muramatsu_thread.start()





    previous_score = get_score(
        game_id
    )



    if previous_score is None:


        print(
            "スコア取得失敗"
        )


        muramatsu_stop_event.set()


        return




    print(
        previous_score
    )





    while True:


        time.sleep(
            CHECK_INTERVAL
        )



        current_score = get_score(
            game_id
        )



        if current_score is None:


            print(
                "試合情報取得失敗"
            )


            continue





        print(
            f"監視中..."
            f"{current_score['home_name']} "
            f"{current_score['home']} - "
            f"{current_score['visitor']} "
            f"{current_score['visitor_name']}"
        )





        # ホーム得点

        if current_score["home"] > previous_score["home"]:


            notify_score(
                current_score["home_name"],
                current_score
            )





        # ビジター得点

        if current_score["visitor"] > previous_score["visitor"]:


            notify_score(
                current_score["visitor_name"],
                current_score
            )






        # 試合終了

        if current_score["game_state"] == "試合終了":


            print(
                "試合終了"
            )


            # 村松監視停止

            muramatsu_stop_event.set()



            send_discord(
                "🏁 試合終了\n\n"
                f"{current_score['home_name']} "
                f"{current_score['home']} - "
                f"{current_score['visitor']} "
                f"{current_score['visitor_name']}"
            )



            return





        previous_score = current_score
        # ==========================
# 試合開始待機
# ==========================

def wait_until_game_start(next_game):


    game_date = next_game["date"]

    start_time = next_game["start_time"]



    start_datetime = datetime.strptime(
        game_date + start_time,
        "%Y%m%d%H:%M"
    )



    notify_datetime = (
        start_datetime
        - timedelta(minutes=30)
    )



    print(
        f"次の試合:"
        f"{game_date} {start_time}"
    )



    notified = False



    while True:


        now = datetime.now()



        # 30分前通知

        if now >= notify_datetime and not notified:


            send_discord(
                "⚾ 今日の中日戦まもなく開始！\n\n"
                f"📅 {game_date}\n"
                f"🕕 {start_time}\n"
                f"🏟 バンテリンドーム"
            )


            print(
                "試合30分前通知送信"
            )


            notified = True






        # 試合開始

        if now >= start_datetime:


            print(
                "試合開始時間になりました"
            )


            send_discord(
                "⚾ 中日戦開始！\n\n"
                "監視を開始します"
            )


            return





        print(
            "次の試合まで待機中..."
        )



        time.sleep(
            300
        )








# ==========================
# Bot開始
# ==========================

print(
    "⚾ 中日ドラゴンズBot起動"
)





while True:



    print(
        "\n今日の中日戦を探しています..."
    )



    game_id = get_dragons_game_id()



    if game_id:


        print(
            f"GameID: {game_id}"
        )



        score = get_score(
            game_id
        )



        if score:



            print(
                "現在状態"
            )


            print(score)





            # 試合終了済み

            if score["game_state"] == "試合終了":



                print(
                    "本日の試合は終了済み"
                )



                next_game = get_next_dragons_game()



                if next_game:


                    print(
                        "次の試合を発見しました"
                    )


                    print(
                        next_game
                    )



                    wait_until_game_start(
                        next_game
                    )



                    monitor_game(
                        next_game["game_id"]
                    )






            else:


                monitor_game(
                    game_id
                )






    else:



        print(
            "今日は中日戦がありません"
        )



        next_game = get_next_dragons_game()



        if next_game:


            wait_until_game_start(
                next_game
            )


            monitor_game(
                next_game["game_id"]
            )






    print(
        "次の日の試合を待機します"
    )



    time.sleep(
        3600
    )