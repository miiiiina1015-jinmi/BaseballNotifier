from player_checker import get_starting_member

from notifier import send_starting_notification


# スタメン通知済み管理
starting_notified_games = set()


def notify_muramatsu_starting(game_id):

    # 同じ試合で二重通知しない
    if game_id in starting_notified_games:
        return

    starter = get_starting_member(game_id)

    if starter is None:
        return

    starting_notified_games.add(game_id)

    send_starting_notification(starter)
    