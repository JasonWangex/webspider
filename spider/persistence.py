from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from Domain import User
import config





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
