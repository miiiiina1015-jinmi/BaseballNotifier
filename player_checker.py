import requests


PLAYER_ID = "1750223"

PLAYER_NAME = "村松　開人"


BASE_URL = "https://spaia.jp/baseball/npb/api"



# bresult変換表
# 確認できたコードを元に随時追加

BRESULT_MAP = {

    "0": "打席継続",

    "40": "アウト",

    "41": "内野ゴロ",

    "42": "内野フライ",

    "43": "ライナー",

    "44": "ゴロアウト",

    "45": "三振",

    "46": "併殺",

    "50": "安打",

    "51": "単打",

    "52": "二塁打",

    "53": "三塁打",

    "54": "本塁打",

    "60": "犠打",

    "61": "犠飛",

    "70": "四球",

    "71": "死球",

}





def convert_bresult(code):

    if code is None:
        return "不明"


    return BRESULT_MAP.get(
        str(code),
        f"未登録({code})"
    )






def get_starting_member(game_id):

    url = (
        f"{BASE_URL}/starting_members_for_flash"
        f"?gameId={game_id}"
    )


    response = requests.get(url)


    if response.status_code != 200:
        return None


    data = response.json()


    if not data:
        return None



    for member in data:

        if str(member.get("playerId")) == PLAYER_ID:

            return {

                "name": member.get(
                    "playerName"
                ),

                "bat_no": member.get(
                    "startBatNo"
                ),

                "position": member.get(
                    "startPosition"
                ),

                "number": member.get(
                    "backNumber"
                )

            }



    return None





def get_atbat_history(game_id):

    url = (
        f"{BASE_URL}/flash_atbat_history"
        f"?gameId={game_id}"
    )


    response = requests.get(url)


    if response.status_code != 200:
        return None



    data = response.json()


    if not data:
        return None



    return data





def get_latest_atbat(game_id):

    data = get_atbat_history(game_id)


    if not data:
        return None



    return max(
        data,
        key=lambda x: x.get("ID", 0)
    )







def get_latest_muramatsu_atbat(game_id):

    data = get_atbat_history(game_id)


    if not data:
        return None



    muramatsu = []


    for item in data:


        if str(item.get("batId")) == PLAYER_ID:

            muramatsu.append(item)



    if not muramatsu:

        return None



    latest = max(
        muramatsu,
        key=lambda x: x.get("ID", 0)
    )



    return {

        "id": latest.get(
            "ID"
        ),

        "serial": latest.get(
            "fiveDigitSerialNumber"
        ),

        "ball_count": latest.get(
            "atBatBallCount"
        ),

        "bresult_code": latest.get(
            "bresult"
        ),

        "bresult": convert_bresult(
            latest.get("bresult")
        ),

        "updated": latest.get(
            "UpdatedAt"
        )

    }







def get_current_muramatsu_atbat(game_id):

    """
    現在村松選手が打席中か確認

    戻り値:
    None       → 村松ではない
    データ     → 村松打席中
    """


    latest = get_latest_atbat(game_id)


    if latest is None:

        return None



    if str(latest.get("batId")) != PLAYER_ID:

        return None



    return {

        "serial": latest.get(
            "fiveDigitSerialNumber"
        ),

        "ball_count": latest.get(
            "atBatBallCount"
        ),

        "bresult_code": latest.get(
            "bresult"
        ),

        "bresult": convert_bresult(
            latest.get("bresult")
        )

    }








if __name__ == "__main__":


    game_id = "2021039226"



    print("スタメン確認")

    print(
        get_starting_member(game_id)
    )



    print("\n最新1球")

    print(
        get_latest_atbat(game_id)
    )



    print("\n村松最新打席")

    print(
        get_latest_muramatsu_atbat(game_id)
    )



    print("\n現在村松打席中")

    print(
        get_current_muramatsu_atbat(game_id)
    )