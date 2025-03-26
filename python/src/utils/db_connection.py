from utils.config import POSTGRES_USER, POSTGRES_PASS, POSTGRES_HOST, POSTGRES_DB, POSTGRES_PORT
from utils.database import DatabaseClient


def get_db_client():
    return DatabaseClient(
        db_type='postgresql',
        database=POSTGRES_DB,
        username=POSTGRES_USER,
        password=POSTGRES_PASS,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )
