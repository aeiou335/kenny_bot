from flask import Flask, request, abort
from flask.logging import create_logger

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from util import youtubeBot, pttnbaBot, movieBot, templateResponse
from config import Config
import os, random, plyvel
db = plyvel.DB("userBuffer", create_if_missing=True)
info = Config.secret()
app = Flask(__name__)
logger = create_logger(app)
# Channel Access Token
line_bot_api = LineBotApi(info["token"])
# Channel Secret
handler = WebhookHandler(info["secret"])

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    #app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(PostbackEvent)
def handle_postback(event):
    print("event.data:", event.postback.data)
    print("event.reply_token", event.reply_token)
    #message = TextSendMessage(text=event.postback.data)
    #line_bot_api.reply_message(event.reply_token, message)
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    user_id = event.source.user_id
    db.put(user_id.encode(), "".encode())
    sticker_message = StickerSendMessage(
        package_id = "2",
        sticker_id = str(random.randint(151,160))
    )
    buttons_template = templateResponse.homeTemplate()
    line_bot_api.reply_message(
        event.reply_token,
        [sticker_message, buttons_template])

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
    print("event.source.user_id:", event.source.user_id)
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)

    print(profile.display_name)
    print(profile.user_id)
    print(profile.picture_url)
    print(profile.status_message)
    #app.logger.debug('info log')
    msg = event.message.text.lower()
    #msg = msg.split(" ",1)
    print("msg:", msg)
    user_data = db.get(user_id.encode())
    if user_data != None:
        if user_data.decode() == "youtube":
            db.put(user_id.encode(), "".encode())
            if msg[-1] != "！":
                res = youtubeBot.youtubeBot(msg)
                message = TextSendMessage(text=res[0])
                message2 = TextSendMessage(text=res[1])
                #message3 = TextSendMessage(text=res[2])
                line_bot_api.reply_message(event.reply_token, [message, message2])
                return 0
        elif user_data.decode() == "movie":
            db.put(user_id.encode(), "".encode())
            if msg[-1] != "！":
                msg = msg.split(" ")
                if len(msg) != 2:
                    result = "您的輸入有問題，請參考範例：水行俠 國賓"
                else:
                    res = movieBot.getTimetable(msg[0], "taipei", msg[1])
                    if res == -1:
                        result = "您輸入的電影目前未在台北上映"+chr(0x100014)
                    #elif res == -3:
                    #    result = "您輸入的戲院目前未上映該電影"+chr(0x100086)
                    else:
                        result = res
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
                return 0
    
    if msg == "聯絡資訊！":
        contact_info = "請透過我的以下資訊來聯繫我 \
            \nemail: kennylin0304@gmail.com \
            \n手機: 0911083034 \
            \ngithub: https://github.com/aeiou335 "+chr(0x10000B)
        result = TextSendMessage(text=contact_info)
        """
    elif msg == "電影時刻":
        n = len(msg[1].split(" "))
        if n == 2:
            movieName, city = msg[1].split(" ")
            theaterName = ""
        elif n == 3:
            movieName, city, theaterName = msg[1].split(" ")
        else:
            res = "您的輸入有問題，請參考以下規則：電影時刻 電影名稱 城市 （電影院名稱）\n括號中電影院名稱可填可不填"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=res))
            return 0
        timetable = movieBot.getTimetable(movieName, city, theaterName)
        if timetable == -1:
            res = "抱歉未搜尋到此電影。"+chr(0x10007C)
        elif timetable == -2:
            res = "抱歉地點輸入有誤。"+chr(0x100083)
        elif timetable == -3:
            res = "抱歉此電影目前未在此地點上映。"+chr(0x100086)
        else:
            if len(timetable) > 2000:
            #    for i in range(len(timetable)/2000)+1):
                res = timetable[:2000]
            else:
                res = timetable
    """
    elif msg == "台北電影時刻查詢！":
        result = TextSendMessage(text="請輸入你想看的電影名稱及戲院名稱，中間以一個空白隔開，例如：水行俠 國賓")
        db.put(user_id.encode(), "movie".encode())
    elif msg == "今日nba比分查詢！":
        result = TextSendMessage(text=pttnbaBot.getBoxScore())
    elif msg == "最近煩惱很多！":
        result = templateResponse.sadRecently()
    elif msg == "自行點歌！":
        result = TextSendMessage(text="請問聽什麼歌？")
        db.put(user_id.encode(), "youtube".encode())
    elif msg == "關於kenny_bot！":
        result = templateResponse.botIntro()
    elif msg == "回主選單！":
        result = templateResponse.homeTemplate()
    else:
        message = "Hi {} 你好，這是肯尼的聊天機器人，很高興認識你。\U00100084".format(profile.display_name)
        buttons_template = templateResponse.homeTemplate()
        result = [TextSendMessage(text=message), buttons_template]
        
    line_bot_api.reply_message(event.reply_token, result)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9000))
    app.run(host='0.0.0.0', port=port)
