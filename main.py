from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (FollowEvent, PostbackEvent, TemplateSendMessage, MessageAction,\
                                            ButtonsTemplate, DatetimePickerTemplateAction, ImageMessage, \
                                            ImageSendMessage, MessageEvent, TextMessage, TextSendMessage)
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import datetime
import os

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
        "友達登録ありがとう。写っている人が何歳ごろかを画像に書き込むよ。画像を送ってみてね。"))

#画像の受け取り
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    global message_id, user_id, name_list, user_dict, num, src_image_path
    
    #ユーザー情報を格納する為のリスト
    name_list = []
    day_list = []
    user_dict = {}
    #message_idを取得
    message_id = event.message.id
    #user_idを取得
    user_id = event.source.user_id
    
    #ファイル名をmessage_idに変換したパス
    src_image_path = Path(SRC_IMAGE_PATH.format(message_id)).absolute()

    # 画像をHerokuへ一時保存
    save_image(message_id, src_image_path)
    
    #ユーザー情報を確認し登録がない場合はパスする
    try:
        name_list, day_list = database.serch_data(user_id)
    except TypeError:
        pass
        
    #登録数
    num = len(name_list)
    
    #登録がない場合、名前を確認する
    if num == 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="写真に写っている人の名前は？"))
        #user_idを追加
        database.add_data(user_id)
    #登録がある場合、誰が写ってるか確認
    elif num != 0:
        #nameとdayで辞書を作成
        user_dict = dict(zip(name_list, day_list))
        
        #1人登録の場合
        if num == 1:
            name_1 = name_list[0]
            buttons_template = TemplateSendMessage(
                alt_text="誰が写ってる？",
                template=ButtonsTemplate(
                    text="誰が写ってる？", actions=[
                        MessageAction(label=name_1, text=name_1),
                        MessageAction(label="その他", text="その他")
                    ]
                )
            )
        
        #2人登録の場合
        elif num == 2:
            name_1 = name_list[0]
            name_2 = name_list[1]
            buttons_template = TemplateSendMessage(
                alt_text="誰が写ってる？",
                template=ButtonsTemplate(
                    text="誰が写ってる？", actions=[
                        MessageAction(label=name_1, text=name_1),
                        MessageAction(label=name_2, text=name_2),
                        MessageAction(label="その他", text="その他")
                    ]
                )
            )
        
        #３人登録の場合
        elif num == 3:
            name_1 = name_list[0]
            name_2 = name_list[1]
            name_3 = name_list[2]
            buttons_template = TemplateSendMessage(
                alt_text="誰が写ってる？",
                template=ButtonsTemplate(
                    text="誰が写ってる？", actions=[
                        MessageAction(label=name_1, text=name_1),
                        MessageAction(label=name_2, text=name_2),
                        MessageAction(label=name_3, text=name_3),
                        MessageAction(label="その他", text="その他")
                    ]
                )
            )
        
        line_bot_api.reply_message(event.reply_token, buttons_template)

#テキストの受け取り
@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    global text_name, birthday
    
    #登録が無い場合、生年月日の確認
    if num == 0:
        text_name = event.message.text
        select_day(event)
    #その他が選択された場合、名前を確認
    elif event.message.text == "その他":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="写真に写っている人の名前は？"))
    else:
        text_name = event.message.text
            
        #名前が登録済みの場合、生年月日を取得
        if text_name in name_list:
            birthday = user_dict[text_name]
        
        #ifの場合撮影日、それ以外の場合生年月日の選択            
        select_day(event)
    
#画像を処理して送信
@handler.add(PostbackEvent)
def handle_postback(event):
    global birthday
    
    #ファイル名をmessage_idに変換したパス
    main_image_path = MAIN_IMAGE_PATH.format(message_id)
    preview_image_path = PREVIEW_IMAGE_PATH.format(message_id)
    
    #birthdayが未定義の場合
    if not "birthday" in globals():
        #日付選択アクションの結果ををbirthdayに代入
        birthday = event.postback.params["date"]
        #nameとdayを更新
        database.update_data(user_id, num, text_name, birthday)
        
        #撮影日の選択    
        select_day(event)
    #birthdayが定義済みの場合
    elif "birthday" in globals():
        #画像処理
        date_the_image(src_image_path, Path(main_image_path).absolute(), event)
        date_the_image(src_image_path, Path(preview_image_path).absolute(), event)

        # 画像を指定
        image_message = ImageSendMessage(
                original_content_url=f"https://hidden-anchorage-52228.herokuapp.com/{main_image_path}",
                preview_image_url=f"https://hidden-anchorage-52228.herokuapp.com/{preview_image_path}"
        )
    
        #ログの取得
        app.logger.info(f"https://hidden-anchorage-52228.herokuapp.com/{main_image_path}")
        
        #画像の送信
        line_bot_api.reply_message(event.reply_token, image_message)
        
        #変数birthdayを削除
        del birthday
        
        #データベースの変更を保存し、接続を切る
        database.close_db()

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
    #birthdayが定義済みの場合
    if "birthday" in globals():
        message = "撮影日を選択してね"
    #birthdayが未定義の場合
    elif not "birthday" in globals():
        message = "生年月日を選択してね"
    
    #日付選択アクション    
    date_picker = TemplateSendMessage(
        alt_text=message,
        template=ButtonsTemplate(
            text=message,
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
def date_the_image(src: str, desc: str, event) -> None:
    im = Image.open(src)
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("./fonts/AquaKana.ttc", 50)
    
    #撮影日を取得
    date = event.postback.params["date"]
    #撮影日から生年月日を引いて、生後日数を計算
    how_old = datetime.datetime.strptime(date, "%Y-%m-%d") - datetime.datetime.strptime(str(birthday), "%Y-%m-%d")
    #生後日数と365(日)で商と余りを計算
    years, days = divmod(how_old.days, 365)
    #余りと30(日)で商を計算
    month = days // 30
    text = text_name + f"({years}才{month}ヶ月)"
    
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