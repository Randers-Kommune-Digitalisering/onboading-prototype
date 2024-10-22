import sqlalchemy
import logging
from sqlalchemy.orm import sessionmaker, scoped_session

class DatabaseClient:
    def __init__(self, db_type, database, username, password, host, port=None):
        if db_type.lower() == 'mssql':
            driver = 'mssql+pymssql'
        elif db_type.lower() == 'mariadb':
            driver = 'mariadb+mariadbconnector'
        elif db_type.lower() == 'postgresql':
            driver = 'postgresql+psycopg2'
        else:
            raise ValueError(f"Invalid database type {db_type}")

        self.logger = logging.getLogger(__name__)

        if port:
            host = host + f':{port}'

        self.engine = sqlalchemy.create_engine(f'{driver}://{username}:{password}@{host}/{database}')
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        self.logger.debug(f"Database engine created with driver {driver}")

    def get_session(self):
        try:
            self.logger.debug("Creating a new database session...")
            return self.Session()
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")

    def close_session(self, session):
        try:
            self.logger.debug("Closing the database session...")
            session.close()
        except Exception as e:
            self.logger.error(f"Error closing session: {e}")

    def execute_sql(self, sql, params=None):
        session = self.get_session()
        try:
            if params:
                self.logger.debug(f"Executing SQL with params: {sql} {params}")
                result = session.execute(sqlalchemy.text(sql), params)
            else:
                self.logger.debug(f"Executing SQL: {sql}")
                result = session.execute(sqlalchemy.text(sql))
            session.commit()
            return result
        except Exception as e:
            self.logger.error(f"Error executing SQL: {e}")
            session.rollback()
        finally:
            self.close_session(session)
