import sqlalchemy
import logging
import urllib.parse
from models import Base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError


class DatabaseClient:
    def __init__(self, db_type, database, username, password, host, port=None):
        self.db_type = db_type.lower()
        self.database = database
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"Initializing DatabaseClient with db_type={db_type}, database={database}, username={username}, host={host}, port={port}")

        if self.db_type == 'mssql':
            driver = 'mssql+pymssql'
        elif self.db_type == 'mariadb':
            driver = 'mariadb+mariadbconnector'
        elif self.db_type == 'postgresql':
            driver = 'postgresql+psycopg2'
        else:
            raise ValueError(f"Invalid database type {self.db_type}")

        connection_string = f'{driver}://{urllib.parse.quote_plus(username)}:{urllib.parse.quote_plus(password)}@{urllib.parse.quote_plus(host)}:{urllib.parse.quote_plus(port)}/{urllib.parse.quote_plus(database)}'
        self.logger.info(f"Connection string: {connection_string}")

        self.engine = create_engine(connection_string)

    def get_engine(self):
        return self.engine

    def get_connection(self):
        try:
            if self.engine:
                return self.engine.connect()
            self.logger.error("DatabaseClient not initialized properly. Engine is None. Check error from init.")
        except Exception as e:
            self.logger.error(f"Error connecting to database: {e}")

    def get_session(self):
        try:
            if self.engine:
                return Session(self.get_engine())
            self.logger.error("DatabaseClient not initialized properly. Engine is None. Check error from init.")
        except Exception as e:
            self.logger.error(f"Error connecting to database: {e}")

    def execute_sql(self, sql):
        try:
            with self.get_connection() as conn:
                res = conn.execute(sqlalchemy.text(sql))
                conn.commit()
                return res
        except Exception as e:
            self.logger.error(f"Error executing SQL: {e}")

    def ensure_all_columns_exist(self):  # Check if tables and columns exists, create any missing
        inspector = inspect(self.engine)

        for table in Base.metadata.sorted_tables:
            table_name = table.name
            # Create table if it doesn't exist
            if not inspector.has_table(table_name):
                self.logger.warning(f"Table {table_name} does not exist, creating...")
                table.create(self.engine)
                inspector = inspect(self.engine)  # refresh inspector
                continue

            # Check for missing columns
            db_columns = {col['name'] for col in inspector.get_columns(table_name)}
            model_columns = {col.name for col in table.columns}
            missing_columns = model_columns - db_columns
            if missing_columns:
                self.logger.info(f"Detected missing columns: {missing_columns}")

            for col in table.columns:
                if col.name in missing_columns:
                    try:  # Manually generate DDL for missing columns
                        preparer = self.engine.dialect.identifier_preparer
                        quoted_table = preparer.quote(table_name)
                        quoted_col = preparer.quote(col.name)
                        col_type = col.type.compile(self.engine.dialect)
                        ddl = f'ALTER TABLE {quoted_table} ADD COLUMN {quoted_col} {col_type}'
                        if col.default is not None and hasattr(col.default, 'arg'):
                            ddl += f' DEFAULT {col.default.arg}'
                        self.logger.info(f"Generated DDL for column {col.name}: {ddl}")

                        with self.engine.connect() as conn:
                            result = conn.execute(text(ddl))
                            self.logger.info(f"Added column {col.name} to {table_name} with result: {result}")
                    except SQLAlchemyError as e:
                        self.logger.error(f"Error adding column {col.name} to {table_name}: {e}")
                    except Exception as e:
                        self.logger.error(f"Unexpected error adding column {col.name} to {table_name}: {e}")
