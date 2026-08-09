from discord_sender import send_discord


def send_before_game_notification(game_date, start_time):

    message = (
        "⚾ 今日の中日戦まもなく開始！\n\n"
        f"📅 {game_date}\n"
        f"🕕 {start_time}\n"
        "🏟 バンテリンドーム"
    )

    print(message)
    send_discord(message)


def send_game_start_notification():

    message = (
        "⚾ 中日戦開始！\n\n"
        "監視を開始します"
    )

    print(message)
    send_discord(message)


def send_game_end_notification(score):

    message = (
        "🏁 試合終了\n\n"
        f"{score['home_name']} "
        f"{score['home']} - "
        f"{score['visitor']} "
        f"{score['visitor_name']}"
    )

    print(message)
    send_discord(message)


def send_score_notification(team_name, score):

    if score["tb"] == 1:
        inning = f"{score['inning']}回表"
    elif score["tb"] == 2:
        inning = f"{score['inning']}回裏"
    else:
        inning = ""

    message = (
        f"⚾ {team_name}が得点！\n\n"
        f"📊 {score['home_name']} "
        f"{score['home']} - "
        f"{score['visitor']} "
        f"{score['visitor_name']}\n"
        f"🕒 {inning}"
    )

    print(message)
    send_discord(message)


def send_starting_notification(starter):

    message = (
        "⚾ スタメン発表\n\n"
        "村松開人選手\n\n"
        f"打順：{starter['bat_no']}番\n"
        "守備：遊撃\n"
        f"背番号：{starter['number']}"
    )

    print(message)
    send_discord(message)


# ==================================
# 村松 打席開始
# ==================================

def send_muramatsu_atbat_notification(event):

    tb = "表" if str(event["tb"]) == "1" else "裏"

    inning = f"{event['inning']}回{tb}"

    score = (
        f"{event['home_name']} "
        f"{event['home_score']} - "
        f"{event['visitor_score']} "
        f"{event['visitor_name']}"
    )

    message = (
        "⚾ 村松開人選手 打席へ\n\n"
        f"🏟 {score}\n"
        f"🕒 {inning}\n\n"
        f"👥 {event['text']}\n"
    )

    print(message)
    send_discord(message)


# ==================================
# 村松 打席結果
# ==================================

def send_muramatsu_result_notification(event, atbat_info):

    tb = "表" if str(event["tb"]) == "1" else "裏"

    inning = f"{event['inning']}回{tb}"

    score = (
        f"{event['home_name']} "
        f"{event['home_score']} - "
        f"{event['visitor_score']} "
        f"{event['visitor_name']}"
    )

    message = (
        "⚾ 村松開人選手 打席結果\n\n"
        f"🏟 {score}\n"
        f"🕒 {inning}\n"
        f"👥 {atbat_info}\n\n"
        f"📝 {event['text']}"
    )

    print(message)
    send_discord(message)