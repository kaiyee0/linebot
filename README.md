## linebot
Line X Tech X Fresh
![Image of QRCode](https://github.com/kaiyee0/linebot/blob/master/LineBot.png)
### In this bot, there are 4 main functions.
 1. Get the weather today
 2. Get the latest news in Taiwan
 
 (======== below not available in Heroku though ========)
 3. Randomly chose the restaurant nearby and return the outcome to user.
 4. Daily sent the news and the weather forecast in the morning.
 
And most of the features are done in the function handle_message.

#### 1. Get the weather

Below is about the function codto call the weather info.

```python
def get_weather():
    API_ADDRESS = "Your Location"
    API_TOKEN = "Your API TOKEN"
    weather_data = req.get(API_ADDRESS+API_TOKEN).json()
    ...
```
Just replace the API Address and your own token, then you might be able to get the return json file.
In this bot, I used the API from [openweathermap](https://openweathermap.org/).

#### 2. Get the latest news

I used to get news by scrawling, yet, I would like to try on new stuff: [Google News API](https://newsapi.org/s/google-news-api) to do so.


```python
def get_news():
    API_ADDRESS = "==="
    API_TOKEN = "==="
    ...
    NUM = number of news you would like to get
    columns = []
    for i in range(NUM):
        ...
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
```

This is really simple: you only need to get API & set it to the Carousel Template.

IS IT?
###### Warning:
You must notice that line would only accept "https" url, so if the url returned with "http://" heading (if the linebot needs to connect to it to acquire data, like thumbnail image), the error would occurs. It almost took me 1 day to figure out whats wrong. However, I didn't come out with a better idea.

#### 3. Randomly chose the restaurant nearby and return the outcome to user.
It's really simple, get the location info sent by user, send the data to GOOGLE MAP API, and write a random function to choose where to have something to eat.
```python
def get_food(x, y):
    ...
    food_data = req.get(API_ADDRESS).json()
    ...
    ...
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
    ...
    return([food_detail])
```
You may see that there is a postback function there, so I need to write another hading methond to deal with it.

```python
@handler.add(PostbackEvent)
def postback(event):
    if event.postback.data != None:
            tmp_data = event.postback.data
            server_msg = get_food(tmp_data.split(",")[0], tmp_data.split(",")[1])
            line_bot_api.reply_message(event.reply_token,TemplateSendMessage(alt_text = '餐廳推薦', template=CarouselTemplate(server_msg)))
```

HOWEVER, In this function, it was weird that it was working well in local but not in heroku. After some research, some said that cuz google map api is not available on net, so I could only do it with my MAC and iPHONE LOL. I'd spend some time to figure out if there's any other way; or if you do know how, just DM me.

#### 4. Daily sent the news and the weather forecast in the morning.
I would write a thread and call the function every morning.
```python
#in kayapp.py
schedule.every().day.at("====").do(news_weather_alert)
t = Thread(target=test.run_schedule)
t.start()

#in test.py
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)
```
Yet, it didn't work in Heroku either. In my opinion, it's because Heroku has its own thread programmimg method and I just don't know yet. Maybe when I have more time, I could do some study then.
