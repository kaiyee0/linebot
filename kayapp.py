from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
import requests as req
import schedule
import time
import json as json
from threading import Thread
import test

app = Flask(__name__)

line_bot_api = LineBotApi('0F/zzhWKg4a7BZF95nceo29APozuOKTP0OzTk5vZ4e45U1OHMEoebA/qryii8cuUnTcF2XMj7pVTjekE/BuRs++/rTZh84tQq9Kq1JC9dFI6vGkPjggHs6JisMTwcP+H1xRNZyls+7AGjMLZ3xL2uwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('8ea2488f611063eacf646d8f3fd5dae7')

userList = []

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def get_weather():
    API_ADDRESS = "http://api.openweathermap.org/data/2.5/weather?q=Taipei,Taiwan%20tw&appid="
    API_TOKEN = "62cf74b0b81efaec9cef03804a15f255"
    weather_data = req.get(API_ADDRESS+API_TOKEN).json()
    server_msg = []
    server_msg.append(weather_data['weather'][0]['main'])
    server_msg.append(weather_data['main']['temp']- 273.15)
    print(server_msg[1])
    return server_msg

def get_news():
    API_ADDRESS = "https://newsapi.org/v2/top-headlines?country=tw&apiKey="
    API_TOKEN = "6bf598451b5040d184082307fb2f8c12"
    news_data = req.get(API_ADDRESS+API_TOKEN).json().get('articles')
    print(news_data[0]['description'])
    NUM = 3
    columns = []
    for i in range(NUM):
        news = news_data[i]['description']
        news = news.replace("\n", "")
        news = news[:50]
        news += "..."   
        image_url = news_data[i]['urlToImage']
        if "http:" in image_url:
            image_url = image_url[:4] + "s" + image_url[4:]
        print(image_url)
        news_template = CarouselColumn(
                        thumbnail_image_url=image_url,
                        title=news_data[i]['title'],
                        text=news,
                        actions=[
                            URITemplateAction(
                                label='View More...',
                                uri=news_data[i]['url']
                            )
                        ]
                    )
        columns.append(news_template)
    return columns
    
def get_food(x, y):
    GOOGLE_NEAR_API = "AIzaSyB1icghM3V6uFkPzbYpB5t5bASuW4rRBYA"
    API_ADDRESS = "https://maps.googleapis.com/maps/api/place/radarsearch/json?location=" + str(x) + "," + str(y) + "&radius=1000&type=restaurant&key=" + GOOGLE_NEAR_API
    #AIzaSyCDm0-lul1c4x1ZhyNDf1K2WcXSpFk1PfM
    food_data = req.get(API_ADDRESS).json()
    print(random.choice(food_data['results'])['place_id'])
    #Get Detail
    chosen_food = random.choice(food_data['results'])['place_id']
    GOOGLE_PLACE_API = "AIzaSyCDm0-lul1c4x1ZhyNDf1K2WcXSpFk1PfM"
    API_ADDRESS = "https://maps.googleapis.com/maps/api/place/details/json?placeid=" + chosen_food + "&key=" + GOOGLE_PLACE_API
    food_data = req.get(API_ADDRESS).json()
    image_url = food_data['result']['icon']
    if "http:" in image_url:
            image_url = image_url[:4] + "s" + image_url[4:]
    food_detail = CarouselColumn(
                        thumbnail_image_url=image_url,
                        title=food_data['result']['name'],
                        text="網友評價" + str(food_data['result']['rating']),
                        actions=[
                            URITemplateAction(
                                label='Location',
                                uri=food_data['result']['url']
                            )
                            ,PostbackTemplateAction(
                                label='找別家',
                                data=str(x) + ',' + str(y)
                            )
                        ]
                    )
    print(image_url)
    return([food_detail])

@handler.add(MessageEvent, message=TextMessage)
@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):
    if not userList.count(event.source.user_id):
        userList.append(event.source.user_id)

    if event.message.type == "location":
        print("FOOD")
        server_msg = get_food(event.message.latitude, event.message.longitude)
        line_bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text = '餐廳推薦', template=CarouselTemplate(server_msg)))

    elif event.message.type == "text":
        client_msg = event.message.text
        if "天氣" in client_msg:
            print("WEATHER")
            to_user_msg = "今天氣象為："
            server_msg = get_weather()
            to_user_msg += str(server_msg[0]) + "，氣溫為：" + str(server_msg[1]) + "度"
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=to_user_msg))
        elif "新聞" in client_msg:
            print("NEWS")
            server_msg = get_news()
            line_bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text = 'Kay News', template=CarouselTemplate(server_msg)))
        elif "吃什麼" in client_msg:
            print("GET_LOCATION")
            server_msg = "分享位置以取得附近餐廳"
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=server_msg))
        elif "自我介紹" in client_msg:
            print("WHO")
            server_msg = "來這裡看看吧！\nhttps://www.facebook.com/profile.php?id=100002253904214&ref=bookmarks"
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=server_msg))
        else:
            server_msg = "抱歉，我聽不懂你在說什麼～"
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=server_msg))

def news_weather_alert():
    for user in userList:
        to_user_msg = "早安，今天氣象為："
        server_msg = get_weather()
        to_user_msg += str(server_msg[0]) + "，氣溫為：" + str(server_msg[1]) + "度"
        line_bot_api.push_message(user, TextSendMessage(text=to_user_msg))
        server_msg = get_news()
        line_bot_api.push_message(user,TemplateSendMessage(alt_text = 'Kay News', template=CarouselTemplate(server_msg)))

@handler.add(PostbackEvent)
def postback(event):
    if event.postback.data != None:
            tmp_data = event.postback.data
            server_msg = get_food(tmp_data.split(",")[0], tmp_data.split(",")[1])
            line_bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text = '餐廳推薦', template=CarouselTemplate(server_msg)))

schedule.every().day.at("03:23").do(news_weather_alert)
t = Thread(target=test.run_schedule)
t.start()

if __name__ == "__main__":
    app.run(debug=True)
    

