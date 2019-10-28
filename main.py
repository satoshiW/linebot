from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (ImageMessage, ImageSendMessage, MessageEvent, TextMessage, TextSendMessage)
from pathlib import Path
import os

app = Flask(__name__)
app.debug = False

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)
"""
SRC_IMAGE_PATH = "https://api.line.me/v2/bot/message/{}.jpg/content"
MAIN_IMAGE_PATH = "https://api.line.me/v2/bot/message/{}_main.jpg/content"
PREVIEW_IMAGE_PATH = "https://api.line.me/v2/bot/message/{}_preview.jpg/content"
"""
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
def handle_image(event):
    message_id = event.message.id

    message_content = line_bot_api.get_message_content(message_id)
    with open(Path(f"https://hidden-anchorage-52228.herokuapp.com/{message_id}.jpg").absolute(), 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
"""
    src_image_path = Path(SRC_IMAGE_PATH.format(message_id)).absolute()
    main_image_path = MAIN_IMAGE_PATH.format(message_id)
    preview_image_path = PREVIEW_IMAGE_PATH.format(message_id)

    # 画像を保存
    save_image(message_id, src_image_path)
    
    # 画像の送信
    image_message = ImageSendMessage(
        original_content_url=f"https://hidden-anchorage-52228.herokuapp.com/{main_image_path}",
        preview_image_url=f"https://hidden-anchorage-52228.herokuapp.com/{preview_image_path}"
    )

    app.logger.info(f"https://hidden-anchorage-52228.herokuapp.com/{main_image_path}")
    line_bot_api.reply_message(event.reply_token, image_message)

    # 画像を削除する
    src_image_path.unlink()

def save_image(message_id: str, save_path: str) -> None:
    # message_idから画像のバイナリデータを取得
    message_content = line_bot_api.get_message_content(message_id)
    with open(save_path, "wb") as f:
        # バイナリを1024バイトずつ書き込む
        for chunk in message_content.iter_content():
            f.write(chunk)
"""

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)