from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from Domain import User
import config


def save_or_update(user):
    session = config.DBSession()
    try:
        if user.id is not None:
            session.merge(user)
        else:
            session.add(user)
        session.commit()
    finally:
        session.close()


def save_or_update_all(user_list):
    session = config.DBSession()
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
            save_or_update(user)
    finally:
        session.close()


def get_user_for_followers():
    session = config.DBSession()
    try:
        user = session.query(User).filter(User.needGetFollowers == True).first()
        return user
    except NoResultFound:
        pass
    finally:
        session.close()


def get_user_for_followees(user_id=0):
    session = config.DBSession()
    try:
        if user_id == 0:
            user = session.query(User).filter(User.needGetFollowees == True).first()
        else:
            user = session.query(User).filter(User.id == user_id).first()
        return user
    except NoResultFound:
        pass
    finally:
        session.close()


def get_next_user(user=User()):
    session = config.DBSession()
    try:
        if user.id is None:
            user = session.query(User).filter(User.needGetFollowees == True).first()
        else:
            user = session.query(User).filter(User.id > user.id).filter(User.needGetFollowees == True).first()
        return user
    except NoResultFound:
        pass
    finally:
        session.close()
