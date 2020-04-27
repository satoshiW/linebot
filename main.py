from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (FollowEvent, PostbackEvent, TemplateSendMessage, \
                                            ButtonsTemplate, DatetimePickerTemplateAction, ImageMessage, \
                                            ImageSendMessage, MessageEvent, TextMessage, TextSendMessage)
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import datetime
import os
import re

#import database

app = Flask(__name__)
app.debug = False

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

engine = create_engine("postgresql://vmmfszxyquhraz:dde9deee8b575db7a8f4214d70e99429a5bb1\
a73d018ce8665642754005ed4ed@ec2-52-86-73-86.compute-1.amazonaws.com:5432/d1l9tnctjr6utu")
Base = declarative_base()

class User(Base):
	__tablename__ = "user_list"
	user_id = Column("user_id", String(50), primary_key=True)
	name = Column("name", String(10))
	day = Column("day", Date)

Base.metadata.create_all(engine)
session = Session(bind=engine)

#画像の参照元パス
SRC_IMAGE_PATH = "static/images/{}.jpg"
MAIN_IMAGE_PATH = "static/images/{}_main.jpg"
PREVIEW_IMAGE_PATH = "static/images/{}_preview.jpg"

#message_idを格納する為のリスト
#message_list = []
name_list = []
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
        "友達登録ありがとう。画像を送信して撮影日を教えてくれたら、その日付を画像に書き込むよ。"))

#画像の受け取り
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    global message_id, user_id, num, src_image_path
    #message_idを取得
    message_id = event.message.id
    #user_idを取得
    user_id = event.source.user_id
    
    #ファイル名をmessage_idに変換したパス
    src_image_path = Path(SRC_IMAGE_PATH.format(message_id)).absolute()

    # 画像をHerokuへ一時保存
    save_image(message_id, src_image_path)
    
    #日時選択時に表示する為に画像として保存
    im = Image.open(src_image_path)
    im.save(src_image_path)
    
    #user_idが一致する行を検索
    names = session.query(User.name, User.day).filter(User.user_id==f"{user_id}").all()
    #一致した行のnameをリストへ挿入
    for row in names:
        name_list.append(row.name)
        user_dict[row.name] = row.day
    #nameの数
    num = len(name_list)
    
    #1人登録の場合
    if num == 1:
        name_1 = name_list[0]
        buttons_template = ButtonsTemplate(
        text="誰が写ってる？", actions=[
            MessageAction(label=name_1, text=name_1),
            MessageAction(label="その他", text="その他")
        ])
    #2人登録の場合
    elif num == 2:
        name_1 = name_list[0]
        name_2 = name_list[1]
        buttons_template = ButtonsTemplate(
        text="誰が写ってる？", actions=[
            MessageAction(label=name_1, text=name_1),
            MessageAction(label=name_2, text=name_2),
            MessageAction(label="その他", text="その他")
        ])
    #３人登録の場合
    elif num == 3:
        name_1 = name_list[0]
        name_2 = name_list[1]
        name_3 = name_list[2]
        buttons_template = ButtonsTemplate(
        text="誰が写ってる？", actions=[
            MessageAction(label=name_1, text=name_1),
            MessageAction(label=name_2, text=name_2),
            MessageAction(label=name_3, text=name_3),
            MessageAction(label="その他", text="その他")
        ])
    
    #登録がないか選択がその他の場合、名前を確認する
    if num == 0 or event.message.text == "その他":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="写真に写っている人の名前は？"))
        #登録数が3より少ない場合、user_idを追加
        if num < 3:
            #user_idを追加
            user1 = User(user_id=f"{user_id}")
            session.add(user1)
    #名前がある場合、生年月日を取得する
    else:
        text_name = event.message.text
        #res = session.query(User.day).filter(User.user_id==f"{user_id}", User.name==f"{text_name}").first()
        birthday = user_dict[text_name]
        #撮影日の選択            
        select_day(event)

@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    global text_name
    #名前をtext_nameに代入
    text_name = event.message.text
    
    #登録数が3より少ない場合、nameを追加
    if num < 3:
        user_name = session.query(User).filter(User.user_id==f"{user_id}", User.name==None).first()
        user_name.name = text_name
    
    #生年月日の選択
    select_day(event)
    
#画像を処理して送信
@handler.add(PostbackEvent)
def handle_postback(event):
    global birthday
    #ファイル名をmessage_idに変換したパス
    main_image_path = MAIN_IMAGE_PATH.format(message_id)
    preview_image_path = PREVIEW_IMAGE_PATH.format(message_id)
    
    if "birthday" in globals():
        #画像処理
        date_the_image(src_image_path, Path(main_image_path).absolute(), event, birthday)
        date_the_image(src_image_path, Path(preview_image_path).absolute(), event, birthday)

        # 画像の送信
        image_message = ImageSendMessage(
                original_content_url=f"https://hidden-anchorage-52228.herokuapp.com/{main_image_path}",
                preview_image_url=f"https://hidden-anchorage-52228.herokuapp.com/{preview_image_path}"
        )
    
        #ログの取得
        app.logger.info(f"https://hidden-anchorage-52228.herokuapp.com/{main_image_path}")
    
        line_bot_api.reply_message(event.reply_token, image_message)
    else:
        #生年月日をbirthdayに代入
        birthday = event.postback.params["date"]
    
        #登録数が3より少ない場合、dayを追加
        if num < 3:
            user_day = session.query(User).filter(User.user_id==f"{user_id}", User.day==None).first()
            user_day.day = birthday
        
        #撮影日の選択    
        select_day(event)

#画像保存関数
def save_image(message_id: str, save_path: str) -> None:
    # message_idから画像のバイナリデータを取得
    message_content = line_bot_api.get_message_content(message_id)
    with open(save_path, "wb") as f:
        # 取得したバイナリデータを書き込む
        for chunk in message_content.iter_content():
            f.write(chunk)

#日付選択関数
def select_day(event):
    if "birthday" in globals():
        message = "撮影日を選択してね"
    else:
        message = "生年月日を選択してね"
        
    date_picker = TemplateSendMessage(
        alt_text=message,
        template=ButtonsTemplate(
            text=message,
            thumbnail_image_url=f"https://hidden-anchorage-52228.herokuapp.com/{src_image_path}",
            actions=[
                DatetimePickerTemplateAction(
                    label="選択",
                    data="action=buy&itemid=1",
                    mode="date",
                    initial=str(datetime.date.today()),
                    max=str(datetime.date.today())
                )
            ]
        )
    )
    
    line_bot_api.reply_message(event.reply_token, date_picker)

#画像処理関数
def date_the_image(src: str, desc: str, event, birthday) -> None:
    im = Image.open(src)
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("./fonts/Helvetica.ttc", 50)
    
    #撮影日を取得
    date = event.postback.params["date"]
    text_day = datetime.datetime.strptime(date, "%Y-%m-%d") - datetime.datetime.strptime(birthday, "%Y-%m-%d")
    years, days = divmod(text_day.days, 365)
    month = days // 12
    text = text_name + f"({years}才{month}ヶ月"
    
    #テキストのサイズ
    text_width = draw.textsize(text, font=font)[0]
    text_height = draw.textsize(text, font=font)[1]
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
    draw.text((x - margin * 3, y - margin * 2), text, fill=(255, 255, 255), font=font)
    im.save(desc)

if __name__ == "__main__":
    #app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)