import logging
from flask import Blueprint
from utils.database import DatabaseClient
from utils.config import MSSQL_USER, MSSQL_PASS, MSSQL_HOST, MSSQL_DATABASE
from models.base import Base
from controllers.opgaver_controller import create_opgave, get_all_opgaver, get_opgaver_by_forloebsskabelon_id
from controllers.forloebsskabelon_controller import create_forloebsskabelon

db_client = DatabaseClient('mssql', MSSQL_DATABASE, MSSQL_USER, MSSQL_PASS, MSSQL_HOST)
Base.metadata.create_all(db_client.engine)


logger = logging.getLogger(__name__)
api_endpoints = Blueprint('api', __name__, url_prefix='/api')


@api_endpoints.route('/opgaver', methods=['GET'])
def get_all_opgaver_endpoint():
    return get_all_opgaver()


@api_endpoints.route('/opgaver', methods=['POST'])
def create_opgave_endpoint():
    return create_opgave()


@api_endpoints.route('/opgaver/forloebsskabelon/<int:forlobsskabelon_id>', methods=['GET'])
def get_opgaver_by_forloebsskabelon_id_endpoint(forlobsskabelon_id):
    return get_opgaver_by_forloebsskabelon_id(forlobsskabelon_id)


@api_endpoints.route('/forlobsskabelon', methods=['POST'])
def create_forloebsskabelon_endpoint():
    return create_forloebsskabelon()
