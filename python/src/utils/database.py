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

    def ensure_database_exists(self):
        try:
            if self.db_type == 'mssql':
                driver = 'mssql+pymssql'
            elif self.db_type == 'mysql':
                driver = 'mysql+pymysql'
            elif self.db_type == 'postgresql':
                driver = 'postgresql+psycopg2'
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")

            connection_string = f'{driver}://{urllib.parse.quote_plus(self.username)}:{urllib.parse.quote_plus(self.password)}@{urllib.parse.quote_plus(self.host)}:{urllib.parse.quote_plus(self.port)}/{urllib.parse.quote_plus(self.database)}'
            engine = create_engine(connection_string, isolation_level="AUTOCOMMIT")
            with engine.connect() as conn:
                if self.db_type == 'mssql':
                    conn.execute(text(f"IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{self.database}') CREATE DATABASE {self.database}"))
                elif self.db_type == 'mysql':
                    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {self.database}"))
                elif self.db_type == 'postgresql':
                    result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{self.database}'"))
                    if not result.scalar():
                        conn.execute(text(f"CREATE DATABASE {self.database}"))
                self.logger.info(f"Database {self.database} ensured to exist")
        except Exception as e:
            self.logger.error(f"Error ensuring database exists: {e}")

    def ensure_column_exists(self, table_name, column_name, column_type):
        """
        Ensures that a column exists in the specified table. If not, adds it.
        Supports PostgreSQL, MySQL, and MSSQL.
        """
        try:
            with self.get_connection() as conn:
                if self.db_type == 'postgresql':
                    # Check if column exists
                    result = conn.execute(text(f"""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name='{table_name}' AND column_name='{column_name}'
                    """))
                    if not result.fetchone():
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
                        self.logger.info(f"Added column {column_name} to {table_name}")
                elif self.db_type == 'mysql' or self.db_type == 'mariadb':
                    result = conn.execute(text(f"""
                        SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME='{table_name}' AND COLUMN_NAME='{column_name}'
                    """))
                    if not result.fetchone():
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
                        self.logger.info(f"Added column {column_name} to {table_name}")
                elif self.db_type == 'mssql':
                    result = conn.execute(text(f"""
                        SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_NAME='{table_name}' AND COLUMN_NAME='{column_name}'
                    """))
                    if not result.fetchone():
                        conn.execute(text(f"ALTER TABLE {table_name} ADD {column_name} {column_type}"))
                        self.logger.info(f"Added column {column_name} to {table_name}")
                else:
                    self.logger.warning(f"ensure_column_exists not implemented for db_type {self.db_type}")
        except Exception as e:
            self.logger.error(f"Error ensuring column exists: {e}")

    # Ensure all tables and columns exist, create missing columns if needed
    def ensure_all_columns_exist(self):
        inspector = inspect(self.engine)
        with self.engine.connect() as conn:
            self.logger.info("Tables found: " + ", ".join([table.name for table in Base.metadata.sorted_tables]))
            for table in Base.metadata.sorted_tables:
                table_name = table.name
                self.logger.info(f"Checking table: {table_name}")
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
                self.logger.info(f"DB columns: {db_columns}")
                self.logger.info(f"Model columns: {model_columns}")
                self.logger.info(f"Missing columns: {missing_columns}")
                for col in table.columns:
                    if col.name in missing_columns:
                        try:
                            # Manually generate DDL for PostgreSQL, with proper quoting
                            preparer = self.engine.dialect.identifier_preparer
                            quoted_table = preparer.quote(table_name)
                            quoted_col = preparer.quote(col.name)
                            col_type = col.type.compile(self.engine.dialect)
                            ddl = f'ALTER TABLE {quoted_table} ADD COLUMN {quoted_col} {col_type}'
                            if col.default is not None and hasattr(col.default, 'arg'):
                                ddl += f' DEFAULT {col.default.arg}'
                            self.logger.info(f"Generated DDL for column {col.name}: {ddl}")
                            conn.execute(text(ddl))
                            self.logger.info(f"Added column {col.name} to {table_name}")
                        except SQLAlchemyError as e:
                            self.logger.error(f"Error adding column {col.name} to {table_name}: {e}")
                        except Exception as e:
                            self.logger.error(f"Unexpected error adding column {col.name} to {table_name}: {e}")
