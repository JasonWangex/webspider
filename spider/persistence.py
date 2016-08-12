from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from Domain import User

engine = None
DBSession = None


def start_session():
    global engine
    global DBSession
    engine = create_engine('mysql+mysqlconnector://cdb_outerroot:4m6tAbHB7@57ad3a781f1e8.sh.cdb.myqcloud.com:7936/zhihu_users?charset=utf8mb4')
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
