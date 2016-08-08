from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, default="")
    uid = Column(String, default="")
    hashId = Column(String, default="")
    gender = Column(Integer, default=0)
    avatar = Column(String, default="")
    introduction = Column(String, default="")
    description = Column(String, default="")
    career = Column(String, default="")
    location = Column(String, default="")
    education = Column(String, default="")
    approval = Column(Integer, default=0)
    thanks = Column(Integer, default=0)
    collected = Column(Integer, default=0)
    share = Column(Integer, default=0)


