import mysql.connector

connection = mysql.connector.connect(
		host="us-cdbr-iron-east-04.cleardb.net",
		user="ba35bf40e5c8e5",
		passwd="05a70afa",
		db="heroku_aa2b206541cbf4a",
		charset="utf8"
)
cursor = connection.cursor()

def get_data(event, user_id):
	#user_idの参照
	cursor.execute(f"""SELECT COUNT(user_id) FROM user WHERE user_id='{user_id}'""")
	#user_idが無かった場合
	if cursor == 0:
		#user_idを追加
		cursor.execute("""INSERT INTO user VALUES user_id""")
		update_data()
	#1人登録の場合
	elif cursor == 1:
		cursor.execute("""SELECT * FROM user WHERE user_id=user_id""")
		name_1 = cursor.fetchone(cursor["name"])
		buttons_template = ButtonTemplate(
        text="誰が写ってる？", actions=[
			MessageAction(label=name_1, text=name_1),
			MessageAction(label="その他", text="その他")
		])
		get_day()
	#2人登録の場合
	elif cursor == 2:
		cursor.execute("""SELECT * FROM user WHERE user_id=user_id""")
		name_1 = cursor.fetchone(cursor["name"])
		name_2 = cursor.fetchone(cursor["name"])
		buttons_template = ButtonTemplate(
		text="誰が写ってる？", actions=[
			MessageAction(label=name_1, text=name_1),
			MessageAction(label=name_2, text=name_2),
			MessageAction(label="その他", text="その他")
		])
		get_day()
	#３人登録の場合
	else:
		cursor.execute("""SELECT * FROM user WHERE user_id=user_id""")
		name_1 = cursor.fetchone(cursor["name"])
		name_2 = cursor.fetchone(cursor["name"])
		name_3 = cursor.fetchone(cursor["name"])
		buttons_template = ButtonTemplate(
		text="誰が写ってる？", actions=[
			MessageAction(label=name_1, text=name_1),
			MessageAction(label=name_2, text=name_2),
			MessageAction(label=name_3, text=name_3),
			MessageAction(label="その他", text="その他")
		])
		if event.message.text == "その他":
			#名前の確認
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage(text="写真に写っている人の名前は？"))
			#名前をnameに代入
			text_name = event.message.text
			#生年月日の確認
			line_bot_api.reply_message(
				event.reply_token,
				TextSendMessage(text=text_name+"さんの生年月日を◯◯◯◯-◯◯-◯◯の形式で入力してね"))
			#生年月日をdayに代入
			birthday = event.message.text
		else:
			text_name = event.message.text
			corsor.execute("""SELECT day FROM user WHERE user_id=user_id and name=text_name""")
			birthday = cursor["day"]

def update_data():
	#名前の確認
	line_bot_api.reply_message(
		event.reply_token,
		TextSendMessage(text="写真に写っている人の名前は？"))
	#名前をnameに代入
	text_name = event.message.text
	#nameを更新
	cursor.execute("""UPDATE user SET name=text_name WHERE user_id=user_id""")
	#生年月日の確認
	line_bot_api.reply_message(
		event.reply_token,
		TextSendMessage(text=text_name+"さんの生年月日を◯◯◯◯-◯◯-◯◯の形式で入力してね"))
	#生年月日をdayに代入
	birthday = event.message.text
	#dayを更新
	cursor.execute("""UPDATE user SET day=birthday WHERE user_id=user_id""")

def get_day():
	if event.message.text == "その他":
		update_data()
	else:
		text_name = event.message.text
		corsor.execute("""SELECT day FROM user WHERE user_id=user_id and name=text_name""")
		birthday = corsor["day"]

def close_db():
	connection.commit()
	connection.close()