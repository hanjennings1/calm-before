import os
from dotenv import load_dotenv

# Read the variables in server/.env into the environment
load_dotenv()

class Config:
    # Dev database (Neon: calm_before_dev)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Not needed, and it adds overhead
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Neon's free tier sleeps when idle and drops connections;
    # pre-ping checks a connection is alive before using it
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Required by the National Weather Service API
    NWS_USER_AGENT = os.environ.get("NWS_USER_AGENT")

class TestConfig(Config):
    TESTING = True

    # Tests use the separate test database (Neon: calm_before_test)