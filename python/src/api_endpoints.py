import logging
from flask import Blueprint
from utils.database import DatabaseClient
from utils.config import MSSQL_USER, MSSQL_PASS, MSSQL_HOST, MSSQL_DATABASE
from models import Base
from controllers.opgave_controller import (
    create_opgave_with_opgaveskabelon,
    get_opgave_by_forloebsskabelon_id,
    update_opgave,
    delete_opgave,
    get_opgave_by_forloeb_id,
    create_opgave
)
from controllers.forloebsskabelon_controller import (
    create_forloebsskabelon,
    get_all_forloebsskabeloner,
    update_forloebsskabelon_name

)

from controllers.forloeb_controller import (
    create_forloeb
)

from controllers.ressource_controller import (
    create_ressource,
    get_ressources_by_opgaveid,
    delete_ressource,
    update_ressource,
    get_ressources_by_opgaveskabelonid

)

from controllers.opgaveskabeloner_controller import (
    create_opgaveskabelon,
    get_all_opgaveskabeloner,
    update_opgaveskabelon,
    delete_opgaveskabelon
)

db_client = DatabaseClient('mssql', MSSQL_DATABASE, MSSQL_USER, MSSQL_PASS, MSSQL_HOST)
Base.metadata.create_all(db_client.engine)


logger = logging.getLogger(__name__)
api_endpoints = Blueprint('api', __name__, url_prefix='/api')


@api_endpoints.route('/opgave', methods=['POST'])
def create_opgave_endpoint():
    return create_opgave()


@api_endpoints.route('/opgave/opgaveskabelon', methods=['POST'])
def create_opgave_with_opgaveskabelon_endpoint():
    return create_opgave_with_opgaveskabelon()


@api_endpoints.route('/opgave/forloebsskabelon/<int:forlobsskabelon_id>', methods=['GET'])
def get_opgave_by_forloebsskabelon_id_endpoint(forlobsskabelon_id):
    return get_opgave_by_forloebsskabelon_id(forlobsskabelon_id)


@api_endpoints.route('/opgave/<int:opgave_id>', methods=['PUT'])
def update_opgave_endpoint(opgave_id):
    return update_opgave(opgave_id)


@api_endpoints.route('/opgave/<int:opgave_id>', methods=['DELETE'])
def delete_opgave_endpoint(opgave_id):
    return delete_opgave(opgave_id)


@api_endpoints.route('/opgave/forloeb/<int:forloeb_id>', methods=['GET'])
def get_opgave_by_forloeb_id_endpoint(forloeb_id):
    return get_opgave_by_forloeb_id(forloeb_id)


@api_endpoints.route('/forloeb', methods=['POST'])
def create_forloeb_endpoint():
    return create_forloeb()


@api_endpoints.route('/forlobsskabelon', methods=['POST'])
def create_forloebsskabelon_endpoint():
    return create_forloebsskabelon()


@api_endpoints.route('/forlobsskabelon', methods=['GET'])
def get_all_forloebsskabeloner_endpoint():
    return get_all_forloebsskabeloner()


@api_endpoints.route('/forlobsskabelon/<int:forloebsskabelon_id>', methods=['PUT'])
def update_forloebsskabelon_name_endpoint(forloebsskabelon_id):
    return update_forloebsskabelon_name(forloebsskabelon_id)


@api_endpoints.route('/ressource', methods=['POST'])
def create_ressource_endpoint():
    return create_ressource()


@api_endpoints.route('/ressource/opgave/<int:opgave_id>', methods=['GET'])
def get_ressources_by_opgaveid_endpoint(opgave_id):
    return get_ressources_by_opgaveid(opgave_id)


@api_endpoints.route('/ressource/<int:ressource_id>', methods=['DELETE'])
def delete_ressource_endpoint(ressource_id):
    return delete_ressource(ressource_id)


@api_endpoints.route('/ressource/<int:ressource_id>', methods=['PUT'])
def update_ressource_endpoint(ressource_id):
    return update_ressource(ressource_id)


@api_endpoints.route('/ressource/opgaveskabelon/<int:opgaveskabelon_id>', methods=['GET'])
def get_ressources_by_opgaveskabelonid_endpoint(opgaveskabelon_id):
    return get_ressources_by_opgaveskabelonid(opgaveskabelon_id)


@api_endpoints.route('/opgaveskabelon', methods=['POST'])
def create_opgaveskabelon_endpoint():
    return create_opgaveskabelon()


@api_endpoints.route('/opgaveskabelon', methods=['GET'])
def get_all_opgaveskabeloner_endpoint():
    return get_all_opgaveskabeloner()


@api_endpoints.route('/opgaveskabelon/<int:id>', methods=['PUT'])
def update_opgaveskabelon_endpoint(id):
    return update_opgaveskabelon(id)


@api_endpoints.route('/opgaveskabelon/<int:id>', methods=['DELETE'])
def delete_opgaveskabelon_endpoint(id):
    return delete_opgaveskabelon(id)