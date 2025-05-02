import pytest
from HOTEL.factory import Factory
from HOTEL.db import db as _db
from sqlalchemy.orm import scoped_session

@pytest.fixture(scope="session")
def app():
    """
    Create a Flask app configured for testing.
    """
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }
    factory = Factory()
    app = factory.create_app(test_config)

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    """
    Provide a test client for making requests to the app.
    """
    return app.test_client()

@pytest.fixture(scope="function")
def db(app):
    """
    Provide access to the test database.
    """
    return _db


@pytest.fixture(scope="function", autouse=True)
def session(db):
    """
    Connect to the database and remove the session once done.
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    db.session.remove()  
    db.session.begin()  

    yield db.session 

    transaction.rollback()
    connection.close()

    db.session.remove()  
