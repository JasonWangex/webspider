import config


def save(failed):

    session = config.DBSession()
    try:
        failed.id = None
        session.add(failed)
        session.commit()
    finally:
        session.close()
