from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (FollowEvent, PostbackEvent, TemplateSendMessage, ButtonsTemplate, DatetimePickerTemplateAction, ImageMessage, ImageSendMessage, MessageEvent, TextMessage, TextSendMessage)

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import datetime
import os
import re

import database

app = Flask(__name__)
app.debug = False

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

#画像の参照元パス
SRC_IMAGE_PATH = "static/images/{}.jpg"
MAIN_IMAGE_PATH = "static/images/{}_main.jpg"
PREVIEW_IMAGE_PATH = "static/images/{}_preview.jpg"

#message_idを格納する為のリスト
message_list = []
user_dict = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#フォローイベント
@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=
        "友達登録ありがとう。画像を送信して撮影日を教えてくれたら、その日付を画像に書き込むよ"))

#画像の受け取り
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    #message_idを取得
    message_id = event.message.id
    #user_idを取得
    user_id = "'" + str(event.source.user_id) + "'"
    #message_idをリストに格納
    message_list.append(message_id)
    
    #ファイル名をmessage_idに変換したパス
    src_image_path = Path(SRC_IMAGE_PATH.format(message_id)).absolute()

    # 画像をHerokuへ一時保存
    save_image(message_id, src_image_path)
    
    #日時選択時に表示する為に画像として保存
    im = Image.open(src_image_path)
    im.save(src_image_path)
    
    database.get_data(event, user_id)

@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    #最新のmessage_idをリストから取得
    message_id = message_list[-1]
    #user_idを取得
    user_id = event.source.user_id
    #ファイル名をmessage_idに変換したパス
    src_image_path = Path(SRC_IMAGE_PATH.format(message_id)).absolute()
    
    user_dict[text_name] = birthday
    
    #撮影日の選択
    date_picker = TemplateSendMessage(
        alt_text='撮影日を選択してね',
        template=ButtonsTemplate(
            text='撮影日を選択してね',
            thumbnail_image_url=f"https://hidden-anchorage-52228.herokuapp.com/{src_image_path}",
            actions=[
                DatetimePickerTemplateAction(
                    label='選択',
                    data='action=buy&itemid=1',
                    mode='date',
                    initial=str(datetime.date.today()),
                    max=str(datetime.date.today())
                )
            ]
        )
    )
    
    line_bot_api.reply_message(
        event.reply_token,
        date_picker
    )

#画像を処理して送信
@handler.add(PostbackEvent)
def handle_postback(event):
    #最新のmessage_idをリストから取得
    message_id = message_list[-1]
    
    #ファイル名をmessage_idに変換したパス
    src_image_path = Path(SRC_IMAGE_PATH.format(message_id)).absolute()
    main_image_path = MAIN_IMAGE_PATH.format(message_id)
    preview_image_path = PREVIEW_IMAGE_PATH.format(message_id)
    
    #画像処理
    date_the_image(src_image_path, Path(main_image_path).absolute(), event)
    date_the_image(src_image_path, Path(preview_image_path).absolute(), event)

    # 画像の送信
    image_message = ImageSendMessage(
            original_content_url=f"https://hidden-anchorage-52228.herokuapp.com/{main_image_path}",
            preview_image_url=f"https://hidden-anchorage-52228.herokuapp.com/{preview_image_path}"
    )
    
    #ログの取得
    app.logger.info(f"https://hidden-anchorage-52228.herokuapp.com/{main_image_path}")
    
    line_bot_api.reply_message(event.reply_token, image_message)

#画像保存関数
def save_image(message_id: str, save_path: str) -> None:
    # message_idから画像のバイナリデータを取得
    message_content = line_bot_api.get_message_content(message_id)
    with open(save_path, "wb") as f:
        # 取得したバイナリデータを書き込む
        for chunk in message_content.iter_content():
            f.write(chunk)

#画像処理関数
def date_the_image(src: str, desc: str, event) -> None:
    im = Image.open(src)
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("./fonts/Helvetica.ttc", 50)
    #日時選択アクションの日付を取得
    text = event.postback.params['date'] + user_dict
    #正規表現での文字列置換
    text_mod = re.sub("-", "/", text)
    #テキストのサイズ
    text_width = draw.textsize(text_mod, font=font)[0]
    text_height = draw.textsize(text_mod, font=font)[1]
    
    margin = 10
    x = im.width - text_width
    y = im.height - text_height
    #描画する矩形のサイズ
    rect_size = ((text_width + margin * 6), (text_height + margin * 2))
    #矩形の描画
    rect = Image.new("RGB", rect_size, (0, 0, 0))
    #矩形を透明にする為のマスク
    mask = Image.new("L", rect_size, 128)
    
    #画像に矩形とマスクを貼り付け
    im.paste(rect, (x - margin * 6, y - margin * 3), mask)
    #テキストの書き込み
    draw.text((x - margin * 3, y - margin * 2), text_mod, fill=(255, 255, 255), font=font)
    im.save(desc)

if __name__ == "__main__":
    #app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)