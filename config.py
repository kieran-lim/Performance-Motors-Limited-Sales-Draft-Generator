import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    # Use PostgreSQL for local development if no DATABASE_URL is provided
    default_database_url = "postgresql://localhost/sales_draft_db"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", default_database_url)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Determine database type and configure accordingly
    database_url = os.getenv("DATABASE_URL", default_database_url)
    
    if "sqlite" in database_url:
        # SQLite database - no special configuration needed
        SQLALCHEMY_ENGINE_OPTIONS = {}
    elif "supabase.co" in database_url:
        # Cloud database (Supabase) - requires SSL
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 1800,
            'connect_args': {
                'sslmode': 'require'
            }
        }
    else:
        # Local PostgreSQL database - no SSL required
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 1800,
            'connect_args': {
                'sslmode': 'disable'
            }
        }