import pytest

from app import create_app
from config import TestConfig
from models import db


@pytest.fixture
def app():
    """A Flask app wired to the test database, with fresh tables for each test."""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for making requests without running the server."""
    return app.test_client()