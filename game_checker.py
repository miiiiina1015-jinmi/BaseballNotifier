import re

from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright


BASE_URL = "https://spaia.jp/baseball/npb/schedule"


# =========================================================
# ページ取得
# =========================================================

def get_page_html(date=None):

    url = BASE_URL

    if date:
        url += f"?date={date}"

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        try:

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            try:

                page.wait_for_selector(
                    "li.daily-game",
                    timeout=15000
                )

            except Exception:

                # 試合がない日は daily-game が存在しない
                print(
                    f"{date or '今日'}：試合情報が見つかりません"
                )

                return ""

            return page.content()

        except Exception as e:

            print(
                f"ページ取得エラー: {e}"
            )

            return ""

        finally:

            browser.close()


# =========================================================
# 試合一覧取得
# =========================================================

def get_games(date=None):

    html = get_page_html(date)

    if not html:
        return []

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    return soup.select(
        "li.daily-game"
    )


# =========================================================
# 中日戦情報を抽出
# =========================================================

def extract_game(game):

    text = game.get_text(
        " ",
        strip=True
    )

    # 中日戦ではない
    if "中日" not in text:
        return None

    # 試合ページへのリンクを探す
    link = game.find(
        "a",
        href=re.compile(
            r"/baseball/npb/game/\d+"
        )
    )

    if link is None:
        return None

    # GameIDを取得
    match = re.search(
        r"/game/(\d+)",
        link["href"]
    )

    if match is None:
        return None

    game_id = match.group(1)

    # 開始時刻を取得
    time_match = re.search(
        r"\d{1,2}:\d{2}",
        text
    )

    start_time = None

    if time_match:
        start_time = time_match.group()

    return {

        "game_id": game_id,

        "start_time": start_time

    }


# =========================================================
# 今日の中日戦GameID取得
# =========================================================

def get_dragons_game_id():

    games = get_games()

    for game in games:

        result = extract_game(game)

        if result:

            return result["game_id"]

    return None


# =========================================================
# 次の中日戦取得
# =========================================================

def get_next_dragons_game():

    now = datetime.now()

    # 今日から31日先まで検索
    for i in range(0, 31):

        target = now + timedelta(days=i)

        date_str = target.strftime(
            "%Y%m%d"
        )

        games = get_games(date_str)

        for game in games:

            result = extract_game(game)

            if result is None:
                continue

            start_time = result["start_time"]

            # 開始時刻が取得できない場合
            if start_time is None:

                print(
                    f"開始時刻不明のためスキップ: "
                    f"{date_str} "
                    f"GameID={result['game_id']}"
                )

                continue

            # 日付＋開始時刻をdatetimeに変換
            try:

                start_datetime = datetime.strptime(
                    date_str + start_time,
                    "%Y%m%d%H:%M"
                )

            except ValueError:

                print(
                    f"開始時刻の解析に失敗したためスキップ: "
                    f"{date_str} "
                    f"{start_time}"
                )

                continue

            # すでに開始済みの試合は「次の試合」にしない
            if start_datetime <= now:

                print(
                    f"開始済みのためスキップ: "
                    f"{date_str} "
                    f"{start_time} "
                    f"GameID={result['game_id']}"
                )

                continue

            return {

                "date": date_str,

                "game_id": result["game_id"],

                "start_time": start_time

            }

    return None


# =========================================================
# 試合テキスト取得
# =========================================================

def get_game_text(game_id):

    url = (
        f"{BASE_URL}/game_text_pbp"
        f"?GameID={game_id}"
    )

    # 現在のコードではこの関数を直接使用していないため
    # 必要になった場合に備えて空の結果を返す
    try:

        import requests

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code != 200:
            return []

        return response.json()

    except Exception as e:

        print(
            f"試合テキスト取得エラー: {e}"
        )

        return []


# =========================================================
# 村松選手の現在の打席情報
# =========================================================

def get_current_muramatsu_atbat(game_id):

    data = get_game_text(game_id)

    for item in reversed(data):

        player = item.get(
            "PlayInfo_PlayerName"
        )

        text = item.get(
            "TextInfo_Bat_Text",
            ""
        )

        if (
            player
            and "村松" in player
            and text.startswith("＜")
        ):

            return {

                "serial": item.get("ID"),

                "text": text

            }

    return None


# =========================================================
# 村松選手の最新打席結果
# =========================================================

def get_latest_muramatsu_atbat(game_id):

    data = get_game_text(game_id)

    started = False

    for item in reversed(data):

        player = item.get(
            "PlayInfo_PlayerName"
        )

        text = item.get(
            "TextInfo_Bat_Text",
            ""
        )

        if player and "村松" in player:

            started = True

            continue

        if started:

            if (
                text.startswith("＜")
                or text == ""
            ):

                continue

            return {

                "serial": item.get("ID"),

                "text": text

            }

    return None


# =========================================================
# テスト
# =========================================================

if __name__ == "__main__":

    print(
        "================================"
    )

    print(
        "game_checker.py テスト"
    )

    print(
        "================================"
    )

    # ---------------------------------
    # 今日の中日戦
    # ---------------------------------

    game_id = get_dragons_game_id()

    if game_id:

        print(
            "今日の中日戦GameID:",
            game_id
        )

    else:

        print(
            "今日は中日戦がありません"
        )

    print()

    # ---------------------------------
    # 次の中日戦
    # ---------------------------------

    next_game = get_next_dragons_game()

    print(
        "次の中日戦:",
        next_game
    )