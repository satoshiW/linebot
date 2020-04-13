from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

engine = create_engine("postgresql://vmmfszxyquhraz:dde9deee8b575db7a8f4214d70e99429a5bb1a73d018ce8665642754005ed4ed@ec2-52-86-73-86.compute-1.amazonaws.com:5432/d1l9tnctjr6utu")
Base = declarative_base()

class User(Base):
	__tablename__ = "user_list"
	user_id = Column("user_id", String(50), primary_key=True)
	name = Column("name", String(10))
	day = Column("day", Date)

Base.metadata.create_all(engine)
session = Session(bind=engine)

def get_data(event, user_id):
	#user_idの参照
	res = session.query(User).filter(User.user_id==f'{user_id}').count()
	#user_idが無かった場合
	if res == "0":
		#user_idを追加
		user1 = User(user_id=f"{user_id}")
		session.add(user1)
		update_data()
	#1人登録の場合
	elif res == "1":
		session.query(User).filter(User.user_id==f'{user_id}')
		name_1 = con.fetchone(con["name"])
		buttons_template = ButtonTemplate(
        text="誰が写ってる？", actions=[
			MessageAction(label=name_1, text=name_1),
			MessageAction(label="その他", text="その他")
		])
		get_day()
	#2人登録の場合
	elif con.fetchone() == 2:
		con.execute("""SELECT * FROM user_list WHERE user_id=user_id""")
		name_1 = con.fetchone(cursor["name"])
		name_2 = con.fetchone(cursor["name"])
		buttons_template = ButtonTemplate(
		text="誰が写ってる？", actions=[
			MessageAction(label=name_1, text=name_1),
			MessageAction(label=name_2, text=name_2),
			MessageAction(label="その他", text="その他")
		])
		get_day()
	#３人登録の場合
	else:
		con.execute("""SELECT * FROM user_list WHERE user_id=user_id""")
		name_1 = con.fetchone(cursor["name"])
		name_2 = con.fetchone(cursor["name"])
		name_3 = con.fetchone(cursor["name"])
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
			con.execute("""SELECT day FROM user_list WHERE user_id=user_id and name=text_name""")
			birthday = con["day"]

def update_data():
	#名前の確認
	line_bot_api.reply_message(
		event.reply_token,
		TextSendMessage(text="写真に写っている人の名前は？"))
	#名前をnameに代入
	text_name = event.message.text
	#nameを更新
	con.execute("""UPDATE user_list SET name=text_name WHERE user_id=user_id""")
	#生年月日の確認
	line_bot_api.reply_message(
		event.reply_token,
		TextSendMessage(text=text_name+"さんの生年月日を◯◯◯◯-◯◯-◯◯の形式で入力してね"))
	#生年月日をdayに代入
	birthday = event.message.text
	#dayを更新
	con.execute("""UPDATE user_list SET day=birthday WHERE user_id=user_id""")

def get_day():
	if event.message.text == "その他":
		update_data()
	else:
		text_name = event.message.text
		con.execute("""SELECT day FROM user_list WHERE user_id=user_id and name=text_name""")
		birthday = con["day"]

def engine_close():
	engine.commit()
	engine.close()