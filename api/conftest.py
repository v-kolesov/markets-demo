import os
import pytest
import application
from models import db


@pytest.fixture
def app():
    os.environ['FLASK_ENV'] = 'testing'
    app = application.create()
    # with app.app_context():
    #     db.drop_all()
    #     db.create_all()
    yield app
