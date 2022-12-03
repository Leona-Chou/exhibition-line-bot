# https://github.com/line/line-bot-sdk-python/blob/master/examples/flask-echo/app_with_handler.py

import os
# from dotenv import load_dotenv
import sys
import re
from argparse import ArgumentParser
from flask import Flask, request, abort
from flask_apscheduler import APScheduler
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage
)
from datetime import datetime
import ExhibitionInfo
import ExhibitionMongo

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
# load_dotenv()
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['GET', 'POST'])
def callback():

    # 處理POST
    if request.method == 'POST':

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

    # 處理GET
    elif request.method == 'GET':

        outstr = '''
            <h3>Line機器人</h3>
            '''
        return outstr


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    # 存取user_id
    user_id = event.source.user_id
    ExhibitionMongo.AddUserId(user_id)
    message = ''

    if event.message.text == 'test':  # 測試 text
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text + ' success!'))
        print('test success')

    elif event.message.text == '展喵有什麼功能？':
        # line emoji代碼對照表 https://developers.line.biz/en/docs/messaging-api/emoji-list/#line-emoji-definitions
        line_bot_api.reply_message(event.reply_token, TextSendMessage(
            text='\U0001F449輸入編號來查詢想要的資訊：\n\n1. 中正紀念堂展覽資訊\n2. 當代藝術館展覽資訊\n\n(其他展覽資訊還在開發中，暫無提供\U0001F62D)'
        ))
        print('功能 get')

    elif event.message.text == '1':  # 中正紀念堂
        lists = ExhibitionInfo.GetExihibitionInfo()
        for list in lists:
            m1 = re.match(r'^中正紀念堂.$', list['Location'])
            if m1:
                message = message\
                          + '展名：' + list['Title']\
                          + '\n開始日：' + datetime.strftime(list['StartDate'], '%Y/%m/%d')\
                          + '\n結束日：' + datetime.strftime(list['EndDate'], '%Y/%m/%d')\
                          + '\n時間：' + list['Time']\
                          + '\n地點：' + list['Location'] + '\n'\
                          + list['ExhibitionLink'] + '\n\n'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='中正紀念堂展覽：\n\n'+message))
        print('1 get')

    elif event.message.text == '2':  # 當代藝術館
        lists = ExhibitionInfo.GetExihibitionInfo()
        for list in lists:
            m1 = re.match(r'^當代藝術館.$', list['Location'])
            if m1:
                message = message \
                          + '展名：' + list['Title'] \
                          + '\n開始日：' + datetime.strftime(list['StartDate'], '%Y/%m/%d') \
                          + '\n結束日：' + datetime.strftime(list['EndDate'], '%Y/%m/%d') \
                          + '\n時間：' + list['Time'] \
                          + '\n地點：' + list['Location'] + '\n' \
                          + list['ExhibitionLink'] + '\n\n'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='當代藝術館展覽：\n\n' + message))
        print('2 get')
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入相關的關鍵詞或者點擊選單唷~"))
        print('else')


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
