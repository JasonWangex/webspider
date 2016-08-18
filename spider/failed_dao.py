from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = None
DBSession = None


def start_session():
    global engine
    global DBSession
    engine = create_engine(
        'mysql+mysqlconnector://cdb_outerroot:cdb_outerroot@57b17a81a1ef5.sh.cdb.myqcloud.com:6065/zhihu_users?charset=utf8mb4'
    )
    DBSession = sessionmaker(bind=engine)


def save(failed):
    global DBSession
    session = DBSession()
    try:
        failed.id = None
        session.add(failed)
        session.commit()
    finally:
        session.close()
