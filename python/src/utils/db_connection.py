from utils.config import MSSQL_USER, MSSQL_PASS, MSSQL_HOST, MSSQL_DATABASE
from utils.database import DatabaseClient


def get_db_client():
    return DatabaseClient('mssql', MSSQL_DATABASE, MSSQL_USER, MSSQL_PASS, MSSQL_HOST)