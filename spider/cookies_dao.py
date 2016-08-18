from sqlalchemy.orm.exc import NoResultFound

from Domain import Cookies
import config


def get_one():
    session = config.DBSession()
    try:
        cookie = session.query(Cookies).filter(Cookies.available == True).first()
        cookie_copy = Cookies()
        cookie_copy.id = cookie.id
        cookie_copy.cookie = cookie.cookie
        cookie_copy.xsrf = cookie.xsrf
        cookie_copy.relation = cookie.relation
        cookie_copy.available = cookie.available
        cookie_copy.disabled = cookie.disabled
        return cookie_copy
    except NoResultFound:
        pass
    finally:
        session.close()


def release_lock(cookie):
    if cookie is not None:
        session = config.DBSession()
        cookie.available = True
        session.merge(cookie)
        session.commit()
        session.close()


def insert_cookie(cookie):
    if cookie is not None:
        session = config.DBSession()
        session.add(cookie)
        session.commit()
        session.close()


def lock_cookie(cookie):
    if cookie.id is not None:
        session = config.DBSession()
        cookie.available = False
        session.merge(cookie)
        session.commit()
        session.close()
