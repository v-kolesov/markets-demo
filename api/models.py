from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy import ForeignKey

from redis_store import store
from utils import get_token_from_request_headers

db = SQLAlchemy()


def uuid4():
    return str(uuid.uuid4())


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String, primary_key=True, default=uuid4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String, unique=True)
    __password_hash = db.Column(db.String, nullable=False)
    auth_logs = db.relationship("UserAuthLogs", backref="user")

    @property
    def password(self):
        return self.__password_hash

    @password.setter
    def password(self, password):
        self.__password_hash = pbkdf2_sha256.hash(password)

    def password_verify(self, password):
        return pbkdf2_sha256.verify(password, self.__password_hash)

    @staticmethod
    def get_by_username(username):
        return User.query.filter(User.username == username).first()

    def login(self):
        token = uuid4()
        store.set_token(token, str(self.id))
        return token

    @staticmethod
    def get_from_token():
        _id = store.get_token_data(get_token_from_request_headers())
        return User.query.get(_id)


class UserAuthLogs(db.Model):
    __tablename__ = 'users_auth_logs'

    STATUSES = dict(
        SUCCESS=0,
        FAIL=1,
    )
    AUTH_TYPE = dict(
        BASIC=0,
        TOKEN=1
    )

    id = db.Column(db.String, primary_key=True, default=uuid4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String, ForeignKey('users.id'))
    auth_type = db.Column(db.String, nullable=False)
    ip = db.Column(db.String)
    status = db.Column(db.String, nullable=False)

