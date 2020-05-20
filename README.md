# 成長記録アシスタント君
画像を送信すると名前や生年月日をデータベースに保存し、撮影日から何歳ごろの写真かを計算して画像に書き込むラインボットです。

# デモ
![IMG_20200513_101654](https://user-images.githubusercontent.com/35654936/82497938-19159d00-9b2a-11ea-8ab2-f60dab443b4e.png)
![IMG_20200513_101617](https://user-images.githubusercontent.com/35654936/82498174-80cbe800-9b2a-11ea-9aa2-b0de8d6f4fee.png)


# ライブラリ
- Python3.7.1
- flask1.1.1
- line-bot-sdk1.14.0
- flask-sqlalchemy2.4.1

# 使い方
LineでID[@033cynwe]を検索、もしくは下記のQRコードをスキャンし友達登録。
画像を送信するとボットからメッセージが返ってくるので、質問に答えていくと自動でデータを登録し画像へ書き込みを行います。
2回目以降は保存してあるデータを参照し、新規の場合のみ登録を行います（最大3人登録可）。

# 製作者
名前：若松　里至(28)
アドレス：sawakamatsu3@gmail.com
