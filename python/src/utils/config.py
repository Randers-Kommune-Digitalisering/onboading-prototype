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
SFTP_HOST = os.environ['SFTP_HOST'].rstrip()
SFTP_USER = os.environ['SFTP_USER'].rstrip()
SFTP_PASS = os.environ['SFTP_PASS'].rstrip()
AZURE_CLIENTID = os.environ['AZURE_CLIENTID'].rstrip()
AZURE_TENANTID = os.environ['AZURE_TENANTID'].rstrip()
AZURE_CLIENTSECRET = os.environ['AZURE_CLIENTSECRET'].rstrip()
CSV_PATH = os.environ['CSV_PATH'].rstrip()
