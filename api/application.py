import os
from flask import Flask
from flask.helpers import get_env

from default_users import default_users
from models import db
from endpoints.users import api



# This for parsing .env variables
from redis_store import store

CASE_BOOLEAN = {
    'true': True,
    'false': False
}




def get_db_path():
    return f'/data/{get_env()}.db'


def init_config(app):
    """ Load config from environment variables"""
    for (k, v) in os.environ.items():
        value = CASE_BOOLEAN.get(v.lower(), v)
        try:
            value = int(value)
        except ValueError:
            pass
        app.config[k] = value

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'sqlite:///{get_db_path()}'
    )


def create(fncs=[
        init_config,
        store.init_app,
        db.init_app,
        api.init_app,

        ]):

    app = Flask(__name__)
    from models import User

    """ Initialize the external flask modules  """
    for fnc in fncs:
        fnc(app)

    """ Create database if it does't exist """
    if not os.path.exists(get_db_path()):
        with app.app_context():
            db.create_all()
            # add the default users to just-created database
            for _user in default_users:
                db.session.add(User(
                    username=_user['username'],
                    password=_user['password'],
                ))
            db.session.commit()
    return app
