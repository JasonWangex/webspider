from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from Domain import Cookies

engine = None
DBSession = None


def start_session():
    global engine
    global DBSession
    engine = create_engine(
        'mysql+mysqlconnector://cdb_outerroot:cdb_outerroot@57b17a81a1ef5.sh.cdb.myqcloud.com:6065/zhihu_users?charset=utf8mb4'
        , pool_size=200, max_overflow=0
    )
    DBSession = sessionmaker(bind=engine)


class cookies_dao(object):
    def __init__(self):
        pass

    @staticmethod
    def get_one_with_lock():
        global DBSession
        session = DBSession()
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
            if cookie_copy.id is not None:
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
