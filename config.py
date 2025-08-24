import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Only force SSL for remote Postgres, not localhost
    SQLALCHEMY_ENGINE_OPTIONS = {}
    if SQLALCHEMY_DATABASE_URI.startswith(("postgres://","postgresql://","postgresql+psycopg2://")):
        if "localhost" not in SQLALCHEMY_DATABASE_URI and "127.0.0.1" not in SQLALCHEMY_DATABASE_URI:
            SQLALCHEMY_ENGINE_OPTIONS = {
                "pool_size": 5,
                "max_overflow": 10,
                "pool_timeout": 30,
                "pool_recycle": 1800,
                "connect_args": {"sslmode": "require"},
            }
