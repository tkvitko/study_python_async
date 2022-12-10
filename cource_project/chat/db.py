import datetime
import hashlib

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
        online = Column(Integer)
        password_hash = Column(Integer)

        def __init__(self, login, ip, password_hash):
            self.login = login
            self.ip = ip
            self.online = False
            self.password_hash = password_hash

        def __repr__(self):
            return "<User('%s','%s')>" % (self.login, self.ip)

    class Message(Base):
        __tablename__ = 'messages'
        id = Column(Integer, primary_key=True)
        from_user = Column(Integer, ForeignKey("users.id"), nullable=False)
        to_user = Column(Integer, ForeignKey("users.id"), nullable=False)
        text = Column(String)

        def __init__(self, from_user, to_user, text):
            self.from_user = from_user
            self.to_user = to_user
            self.text = text

        def __repr__(self):
            return "<Message('%s','%s','%s')>" % (self.from_user, self.to_user, self.text)

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
            return "<UserHistory('%s','%s', '%s')>" % (self.login, self.time, self.ip_address)

    class Contact(Base):
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        owner = Column(Integer, ForeignKey("users.id"), nullable=False)
        friend = Column(Integer, ForeignKey("users.id"), nullable=False)

        def __init__(self, owner, friend):
            self.owner = owner
            self.friend = friend

        def __repr__(self):
            return "<Contact('%s','%s')>" % (self.owner, self.friend)

    def __init__(self):
        self.engine = create_engine(f'sqlite:///{DB_FILE}', echo=True)
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_user(self, login, ip, password_hash):
        user = self.User(login, ip, password_hash)
        self.session.add(user)

        now = datetime.datetime.now()
        user_history = self.UserHistory(login, now, ip)
        self.session.add(user_history)
        self.session.commit()

    def get_contact_object_for_users_pair(self, owner_login, friend_login):
        owner = self.session.query(self.User).filter_by(login=owner_login).first()
        print(owner)
        friend = self.session.query(self.User).filter_by(login=friend_login).first()
        print(friend)
        if owner and friend:
            return self.Contact(owner.id, friend.id)

    def add_contact_for_user(self, owner_login, friend_login):
        contact = self.get_contact_object_for_users_pair(owner_login, friend_login)
        print(contact)
        self.session.add(contact)
        self.session.commit()

    def remove_contact_from_user(self, owner_login, friend_login):
        contact = self.get_contact_object_for_users_pair(owner_login, friend_login)
        self.session.delete(contact)
        self.session.commit()

    def get_user_contacts(self, user_login):
        user = self.session.query(self.User).filter_by(login=user_login).first()
        user_id = user.id
        contacts = self.session.query(self.Contact).filter_by(owner=user_id).all()

        return [self.session.query(self.User).filter_by(id=contact.friend).first().login for contact in contacts]

    def check_user_exists(self, user_login):
        if self.session.query(self.User).filter_by(login=user_login).first():
            return True
        return False

    def get_users(self):
        return [[user.login, user.online] for user in self.session.query(self.User).all()]

    def save_message(self, from_user, to_user, text):
        message = self.Message(from_user, to_user, text)
        self.session.add(message)
        self.session.commit()

    def get_messages_from_db(self, from_user, to_user):
        messages = self.session.query(self.Message).filter_by(from_user=from_user, to_user=to_user).all()
        messages.extend(self.session.query(self.Message).filter_by(from_user=to_user, to_user=from_user).all())
        return [message.text for message in messages]

    def set_user_status(self, user_login, is_online):
        user = self.session.query(self.User).filter_by(login=user_login).first()
        user.online = 1 if is_online else 0
        self.session.commit()

    def get_db_engine(self):
        return self.engine

    def check_users_password_hash(self, user_login, password_hash):
        user = self.session.query(self.User).filter_by(login=user_login).first()
        return user.password_hash == password_hash


if __name__ == '__main__':
    db = ServerDatabase()
    # db.add_user('client_10', '192.168.1.4', 8888)
    # db.save_message('yyy', 'xxx', 'hell')
    # db.add_user('client_2', '192.168.1.5', 8888)
    # db.add_contact_for_user('client_1', 'client_4')
    # db.add_contact_for_user('client_2', 'client_3')
    # print(db.get_user_contacts('client_1'))
    # print(db.get_users())
    # db.set_user_status('client_10', is_online=False)
    # print(db.engine)
    # print(db.get_messages_from_db('Taras', 'Marina'))
    h = hashlib.sha256()
    h.update(b'123456')
    # db.add_user('Alex', '0.0.0.0', h.hexdigest())
    print(h.hexdigest())
    # print(db.check_users_password_hash('Alex', test))
    k = hashlib.sha256()
    k.update('123456'.encode('ascii'))
    print(k.hexdigest())

