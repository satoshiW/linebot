from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (PostbackEvent, TemplateSendMessage, ButtonsTemplate, DatetimePickerTemplateAction, ImageMessage, ImageSendMessage, MessageEvent, TextMessage, TextSendMessage)

from pathlib import Path
#from PIL.ExifTags import TAGS
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
#import boto3

app = Flask(__name__)
app.debug = False

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
#aws_s3_bucket = os.environ["AWS_STORAGE_BUCKET_NAME"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

SRC_IMAGE_PATH = "static/images/{}.jpg"
MAIN_IMAGE_PATH = "static/images/{}_main.jpg"
PREVIEW_IMAGE_PATH = "static/images/{}_preview.jpg"

#message_idを格納する空のリスト
image_list = []

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

@handler.add(MessageEvent, message=ImageMessage)
def get_image(event):
    message_id = event.message.id
    image_list.append(message_id)
    image_id = image_list[-1]

    src_image_path = Path(SRC_IMAGE_PATH.format(image_id)).absolute()
    
    """
    try:
    	exif = Image.open(src_image_path)._getexif()
    except AttributeError:
    	return {}
    	
    exif_table = {}
    for tag_id, value in exif.items():
    	tag = TAGS.get(tag_id, tag_id)
    	exif_table[tag] = value

    return exif_table.get("DateTimeOriginal")
    """
    # 画像をHerokuへ一時保存
    save_image(message_id, src_image_path)
    
    date_picker = TemplateSendMessage(
        alt_text='撮影日を選択してね',
        template=ButtonsTemplate(
            text='撮影日を選択してね',
            title='YYYY-MM-dd',
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

@handler.add(PostbackEvent)
def handle_postback(event):
    image_id = image_list[-1]
    
    src_image_path = Path(SRC_IMAGE_PATH.format(image_id)).absolute()
    main_image_path = MAIN_IMAGE_PATH.format(image_id)
    preview_image_path = PREVIEW_IMAGE_PATH.format(image_id)
    
    date_the_image(src_image_path, Path(main_image_path).absolute(), event)
    date_the_image(src_image_path, Path(preview_image_path).absolute(), event)
    
    """
    image_message = ImageSendMessage(
        original_content_url = f"s3_image_url",
        preview_image_url = f"s3_image_url"
    )"""

    # 画像の送信
    image_message = ImageSendMessage(
            original_content_url=f"https://hidden-anchorage-52228.herokuapp.com/{main_image_path}",
            preview_image_url=f"https://hidden-anchorage-52228.herokuapp.com/{preview_image_path}"
    )

    app.logger.info(f"https://hidden-anchorage-52228.herokuapp.com/{main_image_path}")
    
    #app.logger.info(f"s3_image_url")
    line_bot_api.reply_message(event.reply_token, image_message)

    # 画像を削除
    #src_image_path.unlink()

def save_image(message_id: str, save_path: str) -> None:
    # message_idから画像のバイナリデータを取得
    message_content = line_bot_api.get_message_content(message_id)
    with open(save_path, "wb") as f:
        # 取得したバイナリデータを書き込む
        for chunk in message_content.iter_content():
            f.write(chunk)

    """
    file_name = message_id + ".jpg"
    
    s3_resource = boto3.resource("s3")
    s3_resource.Bucket(aws_s3_bucket).upload_file("static/images/" + file_name, file_name)
    
    s3_client = boto3.client("s3")
    s3_image_url = s3_client.generate_presigned_url(
           ClientMethod = "get_object",
           Params = {"Bucket": aws_s3_bucket, "Key": file_name},
           ExpiresIn = 100,
           HttpMethod = "GET"
    )"""

def date_the_image(src: str, desc: str, event) -> None:
    im = Image.open(src)
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("./fonts/Helvetica.ttc", 50)
    text = event.postback.params['date']

    margin = 10
    text_width = draw.textsize(text, font=font)[0]
    text_height = draw.textsize(text, font=font)[1]
    x = im.width - text_width
    y = im.height - text_height
    draw.rectangle(
            (x - margin * 6, y - margin * 3, im.width, im.height - margin), fill=(0, 0, 0)
        ).putalpha(128)
    draw.text((x - margin * 3, y - margin * 2), text, fill=(255, 255, 255), font=font)
        
    im.save(desc)

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)