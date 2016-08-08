from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from User import User
import json

engine = None
DBSession = None



class user_dao(object):
    def __init__(self):
        pass

    @staticmethod
    def start_session():
        global engine
        global DBSession
        engine = create_engine('mysql+mysqlconnector://root:wjz@17948@localhost:3306/zhihu_users')
        DBSession = sessionmaker(bind=engine)

    @staticmethod
    def save_or_update(user):
        global DBSession
        session = DBSession()
        if user.id is not None:
            session.merge(user)
        else:
            session.add(user)
        session.flush()
        session.commit()

    @staticmethod
    def save_or_update_all(userlist):
        global DBSession
        session = DBSession()
        users = list()
        for user in userlist:
            users.append(user.__dict__)

        session.execute(
            User.__table__.insert(),
            users
        )
        session.commit()

new_user = User(name="dddd", uid="123")
