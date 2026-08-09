import requests
from bs4 import BeautifulSoup

URL = "https://baseball.yahoo.co.jp/npb/game/2021039226/score"


def get_html():
    response = requests.get(URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    return soup