import pytest

from app import create_app
from config import TestConfig


@pytest.fixture
def app():
    """A Flask app wired to the test database."""
    app = create_app(TestConfig)
    yield app


@pytest.fixture
def client(app):
    """A test client for making requests without running the server."""
    return app.test_client()