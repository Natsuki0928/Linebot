from flask import Flask,request,abort
from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent,TextMessage,TextSendMessage,LocationMessage

from linebot.exceptions import LineBotApiError
import scrape as sc
import urllib3.request

import os
import requests
import pprint
import random

app = Flask(__name__)

# 環境変数
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

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


@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    #入力された文字列を格納
    push_text = event.message.text

    #リプライする文字列
    #天気という文字列に対して天気情報を返す
    if push_text == "天気":
        url = 'http://weather.livedoor.com/forecast/webservice/json/v1?city=130010'
        api_data = requests.get(url).json()
        for weather in api_data['forecasts']:
            weather_date = weather['dateLabel']
            weather_forecasts = weather['telop']
            print(weather_date + ':' + weather_forecasts)
        reply_text = api_data["description"]["text"]
    else:
        reply_text = push_text

    judge = "好き" in push_text
    judge_2 = "かわいい" in push_text


    if judge == True:
        reply_text = "俺も"+push_text
    if judge_2 == True:
        reply_text = "照れる//"




    #おみくじリスト
    paper = ["大吉", "中吉", "小吉", "吉", "末吉", "凶"]
    paper_d = {"大吉": "世界は君の思い通りだ！٩( 'ω' )و",
               "中吉": "バッチリじゃん",
               "小吉": "まあまあじゃん(^^)",
               "吉": "ビミョーだね( ´Д`)y━･~~",
               "末吉": "頑張ろうか...",
               "凶": "今日は外でない方がいいよ(´･ω･`)"}

    result = random.choice(paper)
    if push_text == "おみくじ":
        reply_text = "今日の運勢は" + result + "だよ！" + paper_d[result]

    #リプライ部分の記述
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply_text))

    # 位置情報に基づいた天気情報の入力
    if '位置情報' in push_text:
        line_bot_api.reply_message(
            event.reply_token,
            [
            TextSendMessage(push_text='あなたの位置情報を教えてください。'),
            TextSendMessage(push_text='line://nv/location')
            ]
        )

    @handler.add(MessageEvent, message=LocationMessage)
    def handle_location(event):
        push_text = event.message.address

        result = sc.get_weather_from_location(push_text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(push_text=result)
        )


if __name__=="__main__":
    port=int(os.getenv("PORT",5000))
    app.run(host="0.0.0.0",port=port)
