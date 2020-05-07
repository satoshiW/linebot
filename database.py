from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
import datetime
import os

#環境変数からデータベースのURLを取得
DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
Base = declarative_base()

#テーブル定義
class User(Base):
	__tablename__ = "user_list"
	user_id = Column("user_id", String(50), primary_key=True)
	name1 = Column("name1", String(10))
	day1 = Column("day1", Date)
	name2 = Column("name2", String(10))
	day2 = Column("day2", Date)
	name3 = Column("name3", String(10))
	day3 = Column("day3", Date)

Base.metadata.create_all(engine)
session = Session(bind=engine)

#user_idの検索
def serch_data(user_id):
	try:
		#user_idで検索
		res = session.query(User.name1, User.day1, User.name2, User.day2, User.name3, User.day3).filter(User.user_id==f"{user_id}").one()
		
		#nameとdayをそれぞれリストへ挿入
		name_list = [n for n in res if type(n) is str]
		day_list = [str(d) for d in res if type(d) is datetime.date]
		return name_list, day_list
	#user_idの登録が無い場合パスする
	except NoResultFound:
		pass

#user_idの登録
def add_data(user_id):
	session.add(User(user_id=f"{user_id}"))

#ユーザー情報の更新
def update_data(user_id, num, text_name, birthday):
	user_data = session.query(User).filter(User.user_id==f"{user_id}").one()
	
	#登録数に応じてnameとdayを保存
	if num == 0:
		user_data.name1 = text_name
		user_data.day1 = birthday
	elif num == 1:
		user_data.name2 = text_name
		user_data.day2 = birthday
	elif num == 2:
		user_data.name3 = text_name
		user_data.day3 = birthday
    
#データベースの変更を保存し、接続を切る
def close_db():
	session.commit()
	session.close()