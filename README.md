# kenny_bot
A line chatbot implemented with line-bot-sdk-python and flask.

## 加入好友
可透過line id 或者 QR code 加此 bot 好友
line id: @vif1768e
![](https://i.imgur.com/GZgCRrU.png)

## 功能說明

### 主選單
在任何時刻輸入貼圖均會回到主選單，或者非系統要求輸入時，輸入任何非指令的文字都會回到主選單。
#### 主選單的功能如下：
1. 最近煩惱很多： 內建點歌功能、我以及spotify 提供的正向類型歌單。
2. 台北電影時刻查詢
3. 今日nba比分查詢
4. kenny_bot 程式碼：此 bot 的 github 連結。
5. 關於kenny_bot：關於此 bot 的介紹。
6. 聯絡肯尼：我的聯絡方式。

以下詳細介紹前三項之功能。

### 最近煩惱很多
我煩惱很多的時候都會聽歌解憂，所以提供這個功能。
1. 自行點歌：bot會回覆"請問聽什麼歌？"，輸入名稱即可得到youtube 該關鍵字前兩名的影片。注意由於是搜尋該關鍵字前兩名的影片，所以不一定是歌曲。
2. 想聽肯尼特製歌單：連結至我提供的youtube 歌單。
3. 才不想聽肯尼特製歌單：連結至spotify 官方提供歌單。
4. 回主選單

### 台北電影時刻查詢
會要求輸入電影名稱以及影城名稱，不必輸入全名，但該字串須為原字串的連續部分字串，如：比悲傷更悲傷的故事，可輸入悲傷，悲傷的故事，但不可輸入悲傷悲傷。輸入格式為：電影名稱 影城名稱。範例：1)悲傷 國賓長春 2)水行俠 威秀。

### 今日nba比分查詢
是從ptt網頁版爬蟲獲得本日box文章，回傳本日比數以及網頁連結，可經由連結進入該文章，目前已知由jptt可能無法開啟，建議使用網頁瀏覽器開啟或者其他ptt app。

## 程式使用說明
需要在config.py當中填入個人的 Channel Access Token 以及 Channel Secret 即可正常使用，獲得方式可參考官方文件。
