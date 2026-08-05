from discord_sender import send_discord


def notify_score(team_name, score):
    message = (
        f"⚾ {team_name}が得点！\n\n"
        f"{score['home_name']} {score['home']} - "
        f"{score['visitor']} {score['visitor_name']}"
    )

    print(message)

    send_discord(message)