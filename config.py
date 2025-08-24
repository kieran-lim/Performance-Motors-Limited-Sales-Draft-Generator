import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # PostgreSQL configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Determine if we're connecting to a cloud database (Supabase) or local
    database_url = os.getenv("DATABASE_URL", "")
    is_cloud_database = "supabase.co" in database_url or "localhost" not in database_url
    
    if is_cloud_database:
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
        # Local database - no SSL required
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 1800,
            'connect_args': {
                'sslmode': 'disable'
            }
        }