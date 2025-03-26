import os
from dotenv import load_dotenv


# loads .env file, will not overide already set enviroment variables (will do nothing when testing, building and deploying)
load_dotenv()


DEBUG = os.getenv('DEBUG', 'True')
PORT = os.getenv('PORT', '8080')
POD_NAME = os.getenv('POD_NAME', 'pod_name_not_set')

DB_TYPE = os.getenv('DB_TYPE', None)  # environ["DB_TYPE"].strip()
POSTGRES_USER = os.getenv('POSTGRES_USER', '').strip()  # environ["POSTGRES_USER"].strip()
POSTGRES_PASS = os.getenv('POSTGRES_PASS', '').strip()  # environ["POSTGRES_PASS"].strip()
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '').strip()  # environ["POSTGRES_HOST"].strip()
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '').strip()  # environ["POSTGRES_PORT"].strip()
POSTGRES_DB = os.getenv('POSTGRES_DB', '').strip()  # environ["POSTGRES_DB"].strip()
MSSQL_USER = os.getenv('MSSQL_USER', '').strip()  # environ["MSSQL_USER"].strip()
MSSQL_PASS = os.getenv('MSSQL_PASS', '').strip()  # environ["MSSQL_PASS"].strip()
MSSQL_HOST = os.getenv('MSSQL_HOST', '').strip()  # environ["MSSQL_HOST"].strip()
MSSQL_PORT = None
MSSQL_DATABASE = os.getenv('MSSQL_DATABASE', '').strip()  # environ["MSSQL_DATABASE"].strip()
SFTP_HOST = os.environ['SFTP_HOST'].rstrip()
SFTP_USER = os.environ['SFTP_USER'].rstrip()
SFTP_PASS = os.environ['SFTP_PASS'].rstrip()
AZURE_CLIENTID = os.environ['AZURE_CLIENTID'].rstrip()
AZURE_TENANTID = os.environ['AZURE_TENANTID'].rstrip()
AZURE_CLIENTSECRET = os.environ['AZURE_CLIENTSECRET'].rstrip()
CSV_PATH = os.environ['CSV_PATH'].rstrip()
