from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

engine = create_engine("postgres://qaxaikcjpxaqpy:9eaf8a7a006a3c7924f6fb625c53f94d7c4f3e50d\
466e3a1f57ac26bbe097ccd@ec2-52-201-55-4.compute-1.amazonaws.com:5432/d55nc1eudvai0c")
Base = declarative_base()

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

def serch_data(user_id):
	try:
		session.query(User.name1, User.day1, User.name2, User.day2, User.name3, User.day3).filter(User.user_id==f"{user_id}").one()
	except NoResultFound:
		pass
	
def add_data(user_id):
	user1 = User(user_id=f"{user_id}")
	session.add(user1)
    
def close_db():
	session.commit()
	session.close()