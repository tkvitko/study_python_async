import datetime

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, declarative_base, sessionmaker

DB_FILE = 'chat.sqlite'

# engine.connect()

Base = declarative_base()


class ServerDatabase:

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        login = Column(String)
        ip = Column(String)

        def __init__(self, login, ip):
            self.login = login
            self.ip = ip

        def __repr__(self):
            return "<User('%s','%s')>" % (self.login, self.ip)

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

    def __init__(self):
        self.engine = create_engine(f'sqlite:///{DB_FILE}', echo=True)
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_user(self, login, ip, port):
        user = self.User(login, ip)
        self.session.add(user)

        now = datetime.datetime.now()
        user_history = self.UserHistory(login, now, ip)
        self.session.add(user_history)
        self.session.commit()


if __name__ == '__main__':
    db = ServerDatabase()
    db.add_user('client_1', '192.168.1.4', 8888)

