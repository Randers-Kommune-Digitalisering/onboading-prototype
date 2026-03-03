import os
import sys
from dotenv import load_dotenv


# loads .env file, will not overide already set enviroment variables (will do nothing when testing, building and deploying)
load_dotenv()

# Test defaults: keep pytest runs deterministic regardless of local .env.
if 'pytest' in sys.modules:
    os.environ['DEBUG'] = 'False'
    os.environ.setdefault('POD_NAME', 'test-pod')


DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't', 'yes', 'y')
PORT = os.getenv('PORT', '8080')
POD_NAME = os.getenv('POD_NAME', 'pod_name_not_set')
DISABLE_KEYCLOAK = os.getenv('DISABLE_KEYCLOAK', 'False').lower() in ('true', '1', 't')

DB_TYPE = os.getenv('DB_TYPE', None)  # environ["DB_TYPE"].strip()
POSTGRES_USER = os.getenv('POSTGRES_USER', '').strip()  # environ["POSTGRES_USER"].strip()
POSTGRES_PASS = os.getenv('POSTGRES_PASS', '').strip()  # environ["POSTGRES_PASS"].strip()
POSTGRES_HOST = os.getenv('POSTGRES_HOST', '').strip()  # environ["POSTGRES_HOST"].strip()
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '').strip()  # environ["POSTGRES_PORT"].strip()
POSTGRES_DB = os.getenv('POSTGRES_DB', '').strip()  # environ["POSTGRES_DB"].strip()
SFTP_HOST = os.getenv('SFTP_HOST', '').strip()  # environ["SFTP_HOST"].strip()
SFTP_USER = os.getenv('SFTP_USER', '').strip()  # environ["SFTP_USER"].strip()
SFTP_PASS = os.getenv('SFTP_PASS', '').strip()  # environ["SFTP_PASS"].strip()
AZURE_CLIENTID = os.getenv('AZURE_CLIENTID', '').strip()  # environ["AZURE_CLIENTID"].strip()
AZURE_TENANTID = os.getenv('AZURE_TENANTID', '').strip()  # environ["AZURE_TENANTID"].strip()
AZURE_CLIENTSECRET = os.getenv('AZURE_CLIENTSECRET', '').strip()  # environ["AZURE_CLIENTSECRET"].strip()

AZURE_CSV_PATH = os.getenv('AZURE_CSV_PATH', '/data/azure.csv').strip()  # environ["CSV_PATH"].strip()
SD_CSV_PATH = os.getenv('SD_CSV_PATH', '/data/sd.csv').strip()  # environ["CSV_PATH"].strip()

KEYCLOAK_URL = os.environ["KEYCLOAK_URL"].strip()
KEYCLOAK_CLIENT_ID = os.environ["KEYCLOAK_CLIENT_ID"].strip()
KEYCLOAK_CLIENT_SECRET = os.environ["KEYCLOAK_CLIENT_SECRET"].strip()
COOKIE_SECRET = os.environ["COOKIE_SECRET"].strip()

MAIL_SERVICE_URL = os.environ["MAIL_SERVICE_URL"].strip()
MAIL_SERVICE_SENDER = os.environ["MAIL_SERVICE_SENDER"].strip()

# SFTP_HOST = os.environ['SFTP_HOST'].rstrip()
# SFTP_USER = os.environ['SFTP_USER'].rstrip()
# SFTP_PASS = os.environ['SFTP_PASS'].rstrip()
# AZURE_CLIENTID = os.environ['AZURE_CLIENTID'].rstrip()
# AZURE_TENANTID = os.environ['AZURE_TENANTID'].rstrip()
# AZURE_CLIENTSECRET = os.environ['AZURE_CLIENTSECRET'].rstrip()
# CSV_PATH = os.environ['CSV_PATH'].rstrip()
