import os
from dotenv import load_dotenv


# loads .env file, will not overide already set enviroment variables (will do nothing when testing, building and deploying)
load_dotenv()


DEBUG = os.getenv('DEBUG', 'False') in ['True', 'true']
PORT = os.getenv('PORT', '8080')
POD_NAME = os.getenv('POD_NAME', 'pod_name_not_set')

MSSQL_USER = os.environ["MSSQL_USER"].strip()
MSSQL_PASS = os.environ["MSSQL_PASS"].strip()
MSSQL_HOST = os.environ["MSSQL_HOST"].strip()
MSSQL_PORT = None
MSSQL_DATABASE = os.environ["MSSQL_DATABASE"].strip()
