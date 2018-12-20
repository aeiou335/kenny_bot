from bs4 import BeautifulSoup
import requests, re
from datetime import date
from linebot.models import *

#輸入一個關鍵字，回傳youtube搜尋的前兩個影片
class youtubeBot:
    def youtubeBot(name):
        queryname = "+".join(name.split(" ")).lower()
        print("queryname:",queryname)
        r = requests.get("https://www.youtube.com/results?search_query="+queryname+"&gl=TW&hl=zh-TW")
        soup = BeautifulSoup(r.text, "html.parser")
        res = [""]
        for data in soup.select('a'):
            #print("data:", data)
            hit = re.search("v=(.*)",data['href'])
            if hit:
                h = hit.group(1)
                if re.search("list",h):
                    continue
                if h == res[-1][32:]:
                    continue
                res.append("https://www.youtube.com/watch?v="+h)
            if len(res) == 3:
                break
        return res[1:]
        #print("h:", h)
        #return "https://www.youtube.com/watch?v="+h

#獲取今日在ptt上的nba 比分文章
class pttnbaBot:
    def parsePage(soup):
        s = soup.find_all("div", {"class":["r-ent","r-list-sep"]})
        #print(s)
        base_url = "https://www.ptt.cc"
        result = ""
        end = False
        today = str(date.today())
        _, _, curr_day = today.split("-")
        #print("today:", today)
        for data in s:
            #print(data["class"])
            if data["class"][0] == "r-list-sep":
                break
            title = data.find("div", {"class":"title"}).text
            publishDate = data.find("div", {"class":"date"}).text
            _, day = publishDate.split("/")
            #print("publishDate", publishDate)
            if curr_day != day:
                end = True
                break
            if title[1:5] == "[BOX":
                href = base_url + data.find("div", {"class":"title"}).a["href"]
                #print(title, href)
                result = result + title + href +"\n"
        return result, end
    def getBoxScore():
        url = "https://www.ptt.cc/bbs/NBA/index.html"
        base_url = "https://www.ptt.cc"
        result = ""
        while True:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            res, end = pttnbaBot.parsePage(soup)
            result += res
            if end == True:
                break
            prev = soup.findAll ( "a" , {"class":"btn wide"})[1]["href"]
            url = base_url+prev
        if result == "":
            result = "今日無比賽"
        return result

#經由開眼電影網查詢今天的電影時刻
class movieBot:
    def getMovieID(movieName, city):
        r = requests.get("http://www.atmovies.com.tw/movie")
        r.encoding="utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        s = soup.select("select[name=film_id] > option")
        #print(s[1]["value"])
        movieID = ""
        for data in s:
            if movieName in data.text:
                movieID = data["value"]
                break
        cityID = "a02"
        return movieID, cityID

    def getTimetable(movieName, city, theaterName):
        movieID, cityID = movieBot.getMovieID(movieName, city)
        print("movieID:", movieID)
        if movieID == "":
            return -1
        if cityID == "":
            return -2
        r = requests.get("http://www.atmovies.com.tw/showtime/"+movieID+"/"+cityID+"/")
        if r.status_code == 404:
            return -3
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "lxml")
        s = soup.find_all("div",{"id":"filmShowtimeBlock"})
        result = ""
        for data in s[0].find_all("ul"):
            if theaterName != "":
                theater = data.find("li",{"class":"theaterTitle"}).text
                if theaterName not in theater:
                    continue
            #filmVersion = data.find("li",{"class":"filmVersion"})
            #if filmVersion != None:
            #    filmVersion = filmVersion.text
            #timetable = data.find_all("li")
            for theater in data.find_all("li"):
                if theater.text.strip("\r\n") != "":
                    result += theater.text
                    result += "\n"
            result += "\n"
        if result == "":
            result = "您輸入的戲院目前未上映該電影"
        return result.strip("\n")

#所有template 的回應
class templateResponse:
    def homeTemplate():
        return TemplateSendMessage(
                alt_text='目錄 template',
                template=CarouselTemplate(
                    columns=[
                        CarouselColumn(
                        title='這不是肯尼的貓',
                        text='歡迎使用本聊天機器人，旅途中如有不愉快請見諒，在任何時刻發送貼圖可回到本頁面。',
                        thumbnail_image_url='https://i.imgur.com/qmCpvEj.jpg',
                        actions=[
                            MessageTemplateAction(
                                label='最近煩惱很多',
                                text='最近煩惱很多！'
                            ),
                            MessageTemplateAction(
                                label='想更了解肯尼嗎！',
                                text='想更了解肯尼嗎！'
                            ),
                            MessageTemplateAction(
                                label='肯尼特製實用的小功能',
                                text='肯尼特製實用的小功能！'
                            )
                        ]
                    ),
                    CarouselColumn(
                        title='這也不是肯尼的貓',
                        text='肯尼身高一米七，聰穎過人，善琴棋書畫。',
                        thumbnail_image_url='https://i.imgur.com/JoM8jvO.jpg',
                        actions=[
                            URITemplateAction(
                                label='kenny_bot 程式碼',
                                uri="https://github.com/aeiou335/kenny_bot"
                            ),
                            MessageTemplateAction(
                                label='關於kenny_bot',
                                text='關於kenny_bot！'
                            ),
                            MessageTemplateAction(
                                label='聯絡肯尼',
                                text='聯絡資訊！'
                            )
                        ]
                    )
                ]
            )
        )
    def sadRecently():
        return TemplateSendMessage(
                alt_text='煩惱 template',
                template=ButtonsTemplate(
                    title='這也不是肯尼的貓',
                    text='最近煩惱很多嗎？聽首歌吧!',
                    thumbnail_image_url='https://i.imgur.com/XqCMmOE.jpg',
                    actions=[
                        PostbackAction(
                            label='自行點歌',
                            text='自行點歌！',
                            data="youtube"
                        ),
                        URIAction(
                            label='想聽肯尼特製歌單！',
                            uri="https://www.youtube.com/playlist?list=PL1vicSg4kTn3PP-cWhwkfidQwHfByNiiF"
                        ),
                        URIAction(
                            label="才不想聽肯尼特製歌單！",
                            uri="https://open.spotify.com/playlist/37i9dQZF1DX6AozTSWwAdQ"
                        ),
                        MessageTemplateAction(
                                label='回主選單',
                                text='回主選單！'
                        )
                    ]
                )
            )         
    def wantToKnowMore():
        return TemplateSendMessage(
        alt_text='想更了解肯尼嗎 template',
        template=ConfirmTemplate(
            title='想更了解肯尼嗎？',
            text='點選“想”獲得更多肯尼的更多相關資訊',
            actions=[                              
                MessageTemplateAction(
                    label='想',
                    text='我想了解更多有關肯尼的資訊！',
                ),
                MessageTemplateAction(
                    label='不想',
                    text='抱歉不行不想認識肯尼！'
                )
            ]
        )
    )
    def kennyinfo():
        return TemplateSendMessage(
                alt_text='認識肯尼 template',
                template=ButtonsTemplate(
                    title='這也不是肯尼的貓',
                    text='認識肯尼',
                    thumbnail_image_url='https://i.imgur.com/mJ0NvPe.jpg',
                    actions=[
                        MessageTemplateAction(
                            label='肯尼的基本介紹',
                            text='肯尼的基本介紹！'
                        ),
                        MessageTemplateAction(
                            label='肯尼的五個冷知識',
                            text='肯尼的五個冷知識！'
                        ),
                        URIAction(
                            label='肯尼的履歷',
                            uri="http://bit.ly/2GxckX8"
                        ),
                        MessageTemplateAction(
                                label='回主選單',
                                text='回主選單！'
                        )
                    ]
                )
            )
    def kennyintro():
        msg1 = "1. 我叫林耘寬，畢業於台灣大學財金系以及數學系，現就讀於台灣大學財金所。"
        msg2 = "2. 從大學開始自學程式，後來發現自己對於這領域的熱愛，便修習了大部分的資工系必修以及許多選修課程。"
        msg3 = "3. 過去半年我在一間區塊鏈科技公司擔任實習軟體工程師，主要負責主鏈開發以及測試，共識演算法研究，跨鏈協議開發等工作。"
        msg4 = "4. 除了課業以外，我也擔任過財金之夜的副召以及管院足球隊的隊長兼創辦人，我們在去年拿下了台大聯賽的冠軍。"
        return [TextSendMessage(text=msg1), TextSendMessage(text=msg2), TextSendMessage(text=msg3), \
                TextSendMessage(text=msg4)]
    def fiveColdKnowledge():
        msg1 = "1. 肯尼曾經是個小說家，高中時代得過兩次馭墨三城文學獎，一個由雄中、雄女等校合辦的文學獎。"
        msg2 = "2. 肯尼在成為足球員之前是羽球員。"
        msg3 = "3. 肯尼喜歡的youtuber 是還沒加入上班不要看的蔡哥、超哥伯夷還沒離開的上班不要看和不拍業配的howfun如何爽。"
        msg4 = "4. 肯尼不喜歡柑橘類"+chr(0x100083) 
        msg5 = "5. 肯尼其實沒有養貓"+chr(0x100085)+chr(0x10000F)+chr(0x1000AD)
        return [TextSendMessage(text=msg1), TextSendMessage(text=msg2), TextSendMessage(text=msg3), \
                TextSendMessage(text=msg4), TextSendMessage(text=msg5)]

    def smallFunction():
        return TemplateSendMessage(
                alt_text='特殊功能 template',
                template=ButtonsTemplate(
                    title='這也不是肯尼的貓',
                    text='以下為肯尼製作的一些小功能。',
                    thumbnail_image_url='https://i.imgur.com/cYE2N4p.jpg',
                    actions=[
                        MessageTemplateAction(
                            label='台北電影時刻查詢',
                            text='台北電影時刻查詢！'
                        ),
                        MessageTemplateAction(
                            label='今日nba比分查詢',
                            text='今日nba比分查詢！'
                        ),
                        MessageTemplateAction(
                                label='回主選單',
                                text='回主選單'
                        )
                    ]
                )
            )
    def botIntro():
        msg = "本聊天機器人提供肯尼的個人簡單資訊以及一些實用的小功能，例如歌曲搜尋、電影時刻搜尋等等。 \
            \n在任何時刻發出貼圖均可回到主選單，或者隨意輸入文字也可回到主選單。 \
            \n本聊天機器人所有圖片為imgur網站取得，除了測試此機器人以外不做任何用途。 \
            \n本聊天機器人具有極高的人工智慧，請使用者謹慎斟酌使用。"+chr(0x100001)
        return TextSendMessage(text=msg)
#a = movieBot.getTimetable("水行", "台北")
#print(a)
#print(youtubeBot.youtubeBot("Lydia"))
#print(pttnbaBot.getBoxScore())
