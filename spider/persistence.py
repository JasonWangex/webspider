from _locale import Error

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from User import User

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
        try:
            if user.id is not None:
                session.merge(user)
            else:
                session.add(user)
            session.commit()
        except Error:
            pass
        finally:
            session.close()

    @staticmethod
    def save_or_update_all(user_list):
        global DBSession
        session = DBSession()
        users = list()
        for user in user_list:
            users.append(user.__dict__)

        try:
            session.execute(
                User.__table__.insert(),
                users
            )
            session.commit()
        except Error:
            for user in user_list:
                user_dao.save_or_update(user)
        finally:
            session.close()

    @staticmethod
    def get_user_for_followers():
        global DBSession
        session = DBSession()
        try:
            user = session.query(User).filter(User.needGetFollowers is True).one()
            return user
        except NoResultFound:
            pass
        finally:
            session.close()

    @staticmethod
    def get_user_for_followees():
        global DBSession
        session = DBSession()
        try:
            user = session.query(User).filter(User.needGetFollowees is True).one()
            return user
        except NoResultFound:
            pass
        finally:
            session.close()
