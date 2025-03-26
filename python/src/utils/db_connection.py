from utils.config import DB_TYPE, POSTGRES_USER, POSTGRES_PASS, POSTGRES_HOST, POSTGRES_DB, MSSQL_USER, MSSQL_PASS, MSSQL_HOST, MSSQL_DATABASE
from utils.database import DatabaseClient


def get_db_client():
    if DB_TYPE == 'postgresql':
        return DatabaseClient('postgresql', POSTGRES_DB, POSTGRES_USER, POSTGRES_PASS, POSTGRES_HOST)
    return DatabaseClient('mssql', MSSQL_DATABASE, MSSQL_USER, MSSQL_PASS, MSSQL_HOST)
