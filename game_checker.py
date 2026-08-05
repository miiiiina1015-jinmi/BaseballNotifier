import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


BASE_URL = "https://spaia.jp/baseball/npb/schedule"



def get_page_html(date=None):

    url = BASE_URL

    if date:
        url += f"?date={date}"


    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        page.goto(url)

        page.wait_for_selector(
            "li.daily-game",
            timeout=10000
        )

        html = page.content()

        browser.close()

        return html





def extract_game(game):

    text = game.get_text(
        " ",
        strip=True
    )


    # 中日が含まれない試合は除外

    if "中日" not in text:

        return None



    link = game.find(
        "a",
        href=re.compile(
            r"/baseball/npb/game/\d+"
        )
    )


    if link is None:

        return None



    match = re.search(
        r"/game/(\d+)",
        link["href"]
    )


    if match is None:

        return None



    # 開始時間取得

    time_match = re.search(
        r"\d{1,2}:\d{2}",
        text
    )


    start_time = None


    if time_match:

        start_time = time_match.group()



    return {

        "game_id": match.group(1),

        "start_time": start_time

    }





def get_dragons_game_id():

    html = get_page_html()


    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    games = soup.select(
        "li.daily-game"
    )


    for game in games:

        result = extract_game(game)


        if result:

            return result["game_id"]



    return None





def get_next_dragons_game():

    today = datetime.now()



    # 30日先まで検索

    for i in range(1, 31):

        target = today + timedelta(days=i)


        date_str = target.strftime(
            "%Y%m%d"
        )


        html = get_page_html(
            date_str
        )


        soup = BeautifulSoup(
            html,
            "html.parser"
        )


        games = soup.select(
            "li.daily-game"
        )


        for game in games:

            result = extract_game(game)


            if result:

                return {

                    "date": date_str,

                    "game_id": result["game_id"],

                    "start_time": result["start_time"]

                }



    return None





if __name__ == "__main__":

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



    next_game = get_next_dragons_game()


    print(
        "次の中日戦:",
        next_game
    )