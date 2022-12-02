from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, declarative_base

DB_FILE = 'chat.sqlite'

engine = create_engine(f'sqlite:///{DB_FILE}', echo=True)
engine.connect()

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String)
    info = Column(String)

    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return "<User('%s','%s')>" % (self.login, self.info)


class UserHistory(Base):
    __tablename__ = 'users_history'
    id = Column(Integer, primary_key=True)
    login = Column(Integer, ForeignKey("users.id"), nullable=False)
    time = Column(DateTime)
    ip_address = Column(String)

    def __init__(self, login, time, ip_address):
        self.login = login
        self.time = time
        self.ip_address = ip_address

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.login, self.time, self.ip_address)


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey("users.id"), nullable=False)
    friend = Column(Integer, ForeignKey("users.id"), nullable=False)

    def __init__(self, owner, friend):
        self.owner = owner
        self.friend = friend

    def __repr__(self):
        return "<User('%s','%s')>" % (self.owner, self.friend)


Base.metadata.create_all(engine)
