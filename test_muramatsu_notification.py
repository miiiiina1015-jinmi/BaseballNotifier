from notifier import (
    send_muramatsu_atbat_notification,
    send_muramatsu_result_notification,
)

event = {
    "text": "＜2番：村松＞無死一塁",
    "inning": "1",
    "tb": "2",
    "home_name": "中日",
    "visitor_name": "ヤクルト",
    "home_score": "0",
    "visitor_score": "0",
}

send_muramatsu_atbat_notification(event)

event["text"] = "2球目:送りバント成功！打者走者村松も増田(一)のエラーにより出塁する 二三塁"

send_muramatsu_result_notification(event)