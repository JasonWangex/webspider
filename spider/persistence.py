from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from Domain import User
from Domain import Cookies

engine = None
DBSession = None


def start_session():
    global engine
    global DBSession
    engine = create_engine(
        'mysql+mysqlconnector://cdb_outerroot:cdb_outerroot@57b17a81a1ef5.sh.cdb.myqcloud.com:6065/zhihu_users?charset=utf8mb4')
    DBSession = sessionmaker(bind=engine)


class user_dao(object):
    def __init__(self):
        pass

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
        except IntegrityError:
            for user in user_list:
                user_dao.save_or_update(user)
        finally:
            session.close()

    @staticmethod
    def get_user_for_followers():
        global DBSession
        session = DBSession()
        try:
            user = session.query(User).filter(User.needGetFollowers == True).first()
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
            user = session.query(User).filter(User.needGetFollowees == True).first()
            return user
        except NoResultFound:
            pass
        finally:
            session.close()


class failed_dao(object):
    def __init__(self):
        pass

    @staticmethod
    def save(failed):
        global DBSession
        session = DBSession()
        try:
            failed.id = None
            session.add(failed)
            session.commit()
        finally:
            session.close()


class cookies_dao(object):
    def __init__(self):
        pass

    @staticmethod
    def get_one_with_lock():
        global DBSession
        session = DBSession()
        cookie = Cookies()
        cookie_copy = Cookies()
        try:
            cookie = session.query(Cookies).filter(Cookies.available == True).first()
            cookie_copy = Cookies()
            cookie_copy.id = cookie.id
            cookie_copy.cookie = cookie.cookie
            cookie_copy.xsrf = cookie.xsrf
            cookie_copy.relation = cookie.relation
            cookie_copy.available = False
            cookie_copy.disabled = cookie.disabled
            return cookie_copy
        except NoResultFound:
            pass
        finally:
            session.close()
            if cookie.id is not None:
                session = DBSession()
                session.merge(cookie_copy)
                session.commit()
                session.close()

    @staticmethod
    def release_lock(cookie):
        global DBSession
        if cookie is not None:
            session = DBSession()
            cookie.available = True
            session.merge(cookie)
            session.commit()
            session.close()

    @staticmethod
    def insert_cookie(cookie):
        global DBSession
        if cookie is not None:
            session = DBSession()
            session.add(cookie)
            session.commit()
            session.close()

