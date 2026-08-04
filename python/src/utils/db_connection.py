from utils.config import POSTGRES_USER, POSTGRES_PASS, POSTGRES_HOST, POSTGRES_DB
from utils.database import DatabaseClient
from models import Base
from utils.logging import logging


logger = logging.getLogger(__name__)


def create_db_client():
    """
    Factory function to create a DatabaseClient instance.
    """
    db_client = get_db_client()
    engine = db_client.engine
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.error(f"Error creating tables or columns: {e}")
    return db_client


def add_missing_columns():
    """
    Ensure all necessary columns exist in the database.
    """
    db_client = get_db_client()
    try:
        db_client.ensure_all_columns_exist()
    except Exception as e:
        logger.error(f"Error ensuring all columns exist: {e}")


def get_db_client():
    return DatabaseClient(
        db_type='postgresql',
        database=POSTGRES_DB,
        username=POSTGRES_USER,
        password=POSTGRES_PASS,
        host=POSTGRES_HOST,
        port='5432'
    )
