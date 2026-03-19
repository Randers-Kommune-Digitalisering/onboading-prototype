import logging
from flask import Blueprint, request
from utils.db_connection import get_db_client
from controllers.opgave_controller import (
    create_opgave_with_opgaveskabelon,
    get_opgave_by_forloebsskabelon_id,
    get_opgave,
    update_opgave,
    delete_opgave,
    get_opgave_by_forloeb_id,
    create_opgave,
    get_all_opgaver,
    get_opgave_by_forloebsskabelon_id_admin,
    get_opgave_by_forloeb_id_admin,
    get_opgave_by_ansvarlig,
)
from controllers.forloebsskabelon_controller import (
    create_forloebsskabelon,
    get_all_forloebsskabeloner,
    get_forloebsskabelon_by_id,
    update_forloebsskabelon,
    get_forloebsskabeloner_with_opgaver,
    delete_forloebsskabelon
)
from controllers.forloeb_controller import (
    create_forloeb,
    create_forloeb_preparation,
    start_preparation_forloeb,
    get_forloeb,
    get_all_forloeb,
    get_forloeb_with_opgaver,
    get_forloeb_by_email,
    get_forloeb_by_admin,
    complete_forloeb,
    update_forloeb,
    delete_forloeb
)
from controllers.user_controller import (
    get_admin_data,
    get_user_data,
    get_email,
    get_dq_numbers,
    get_fullname,
    # get_and_save_azure_ad_data
)
from controllers.ressource_controller import (
    create_ressource,
    create_ressource_file,
    get_ressources_by_opgaveid,
    delete_ressource,
    update_ressource,
    get_ressources_by_opgaveskabelonid,
    get_ressource,
    download_ressource_file,

)
from controllers.opgaveskabelon_controller import (
    create_opgaveskabelon,
    get_all_opgaveskabeloner,
    update_opgaveskabelon,
    delete_opgaveskabelon,
    get_opgaveskabelon
)
from controllers.external_access_controller import (
    request_external_access,
    get_external_userinfo,
    get_forloeb_external,
    get_opgaver_forloeb_external,
    download_ressource_file_external,
)
from controllers.mail_controller import (
    send_welcome_mail,
    send_planned_new_tasks_notifications,
    notify_expired_tasks_aggregated,
    purge_mails,
    get_planned_mails,
    delete_planned_mail,
)

logger = logging.getLogger(__name__)
db_client = get_db_client()

api_endpoints = Blueprint('api', __name__, url_prefix='/api')


@api_endpoints.route('/external/request-access', methods=['POST'])
def request_external_access_endpoint():
    return request_external_access()


@api_endpoints.route('/external/userinfo', methods=['GET'])
def external_userinfo_endpoint():
    return get_external_userinfo()


@api_endpoints.route('/external/forloeb/<int:forloeb_id>', methods=['GET'])
def external_forloeb_by_id_endpoint(forloeb_id):
    return get_forloeb_external(forloeb_id)


@api_endpoints.route('/external/opgave/forloeb/<int:forloeb_id>', methods=['GET'])
def external_opgaver_by_forloeb_id_endpoint(forloeb_id):
    return get_opgaver_forloeb_external(forloeb_id)


@api_endpoints.route('/external/ressource/<int:ressource_id>/download', methods=['GET'])
def external_ressource_download_endpoint(ressource_id):
    return download_ressource_file_external(ressource_id)


@api_endpoints.route('/mitforloeb', methods=['GET'])
def get_forloeb_by_email_endpoint():
    mail = request.headers.get('usermail')
    return get_forloeb_by_email(mail)


@api_endpoints.route('/opgave', methods=['POST'])
def create_opgave_endpoint():
    return create_opgave()


@api_endpoints.route('/opgave/opgaveskabelon', methods=['POST'])
def create_opgave_with_opgaveskabelon_endpoint():
    return create_opgave_with_opgaveskabelon()


@api_endpoints.route('/opgave/forloebsskabelon/<int:forlobsskabelon_id>', methods=['GET'])
def get_opgave_by_forloebsskabelon_id_endpoint(forlobsskabelon_id):
    return get_opgave_by_forloebsskabelon_id(forlobsskabelon_id)


@api_endpoints.route('/opgave/forloebsskabelon/admin/<int:forlobsskabelon_id>', methods=['GET'])
def get_opgave_by_forloebsskabelon_id_admin_endpoint(forlobsskabelon_id):
    return get_opgave_by_forloebsskabelon_id_admin(forlobsskabelon_id)


@api_endpoints.route('/opgave/admin', methods=['GET'])
def get_all_opgaver_admin_endpoint():
    mail = request.headers.get('usermail')
    return get_opgave_by_ansvarlig(mail)


@api_endpoints.route('/opgave/<int:opgave_id>', methods=['GET'])
def get_opgave_endpoint(opgave_id):
    return get_opgave(opgave_id)


@api_endpoints.route('/opgave/<int:opgave_id>', methods=['PUT'])
def update_opgave_endpoint(opgave_id):
    return update_opgave(opgave_id)


@api_endpoints.route('/opgave/<int:opgave_id>', methods=['DELETE'])
def delete_opgave_endpoint(opgave_id):
    return delete_opgave(opgave_id)


@api_endpoints.route('/opgave/forloeb/<int:forloeb_id>', methods=['GET'])
def get_opgave_by_forloeb_id_endpoint(forloeb_id):
    return get_opgave_by_forloeb_id(forloeb_id)


@api_endpoints.route('/opgave/forloeb/admin/<int:forloeb_id>', methods=['GET'])
def get_opgave_by_forloeb_id_admin_endpoint(forloeb_id):
    return get_opgave_by_forloeb_id_admin(forloeb_id)


@api_endpoints.route('/opgave', methods=['GET'])
def get_all_opgaver_endpoint():
    return get_all_opgaver()


@api_endpoints.route('/forloeb', methods=['POST'])
def create_forloeb_endpoint():
    return create_forloeb()


@api_endpoints.route('/forloeb-preparation', methods=['POST'])
def create_forloeb_preparation_endpoint():
    return create_forloeb_preparation()


@api_endpoints.route('/forloeb-start', methods=['POST'])
def start_forloeb_endpoint():
    return start_preparation_forloeb()


@api_endpoints.route('/forloeb', methods=['GET'])
def get_all_forloeb_endpoint():
    admin_name = request.headers.get('adminmail')
    if admin_name:
        return get_forloeb_by_admin(admin_name)
    return get_all_forloeb()


@api_endpoints.route('/forloeb/<int:forloeb_id>', methods=['DELETE'])
def delete_forloeb_endpoint(forloeb_id):
    return delete_forloeb(forloeb_id)


@api_endpoints.route('/forloeb/complete/<int:forloeb_id>', methods=['PUT'])
def complete_forloeb_endpoint(forloeb_id):
    return complete_forloeb(forloeb_id)


@api_endpoints.route('/forloeb/<int:forloeb_id>', methods=['PUT'])
def update_forloeb_endpoint(forloeb_id):
    return update_forloeb(forloeb_id)


@api_endpoints.route('/forloeb/<int:forloeb_id>', methods=['GET'])
def get_forloeb_endpoint(forloeb_id):
    return get_forloeb(forloeb_id)


@api_endpoints.route('/forloeb/<int:forloeb_id>/send-welcome', methods=['POST'])
def send_mail_forloeb_endpoint(forloeb_id):
    if not request.json or 'subject' not in request.json or 'content' not in request.json:
        return {'error': 'Subject and content are required in the request body'}, 400
    return send_welcome_mail(forloeb_id, request.json.get('subject', ''), request.json.get('content', ''))


@api_endpoints.route('/forloeb/opgaver', methods=['GET'])
def get_forloeb_with_opgaver_endpoint():
    return get_forloeb_with_opgaver()


@api_endpoints.route('/forlobsskabelon', methods=['POST'])
def create_forloebsskabelon_endpoint():
    return create_forloebsskabelon()


@api_endpoints.route('/forlobsskabelon', methods=['GET'])
def get_all_forloebsskabeloner_endpoint():
    return get_all_forloebsskabeloner()


@api_endpoints.route('/forlobsskabelon/<int:forloebsskabelon_id>', methods=['GET'])
def get_forloebsskabeloner_by_id_endpoint(forloebsskabelon_id):
    return get_forloebsskabelon_by_id(forloebsskabelon_id)


@api_endpoints.route('/forlobsskabelon/opgaver', methods=['GET'])
def get_forloebsskabeloner_with_opgaver_endpoint():
    return get_forloebsskabeloner_with_opgaver()


@api_endpoints.route('/forlobsskabelon/<int:forloebsskabelon_id>', methods=['PUT'])
def update_forloebsskabelon_endpoint(forloebsskabelon_id):
    return update_forloebsskabelon(forloebsskabelon_id)


@api_endpoints.route('/forlobsskabelon/<int:forloebsskabelon_id>', methods=['DELETE'])
def delete_forloebsskabelon_endpoint(forloebsskabelon_id):
    return delete_forloebsskabelon(forloebsskabelon_id)


@api_endpoints.route('/ressource/<int:ressource_id>', methods=['GET'])
def get_ressource_endpoint(ressource_id):
    return get_ressource(ressource_id)


@api_endpoints.route('/ressource', methods=['POST'])
def create_ressource_endpoint():
    return create_ressource()


@api_endpoints.route('/ressource/file', methods=['POST'])
def create_ressource_file_endpoint():
    return create_ressource_file()


@api_endpoints.route('/ressource/opgave/<int:opgave_id>', methods=['GET'])
def get_ressources_by_opgaveid_endpoint(opgave_id):
    return get_ressources_by_opgaveid(opgave_id)


@api_endpoints.route('/ressource/<int:ressource_id>', methods=['DELETE'])
def delete_ressource_endpoint(ressource_id):
    return delete_ressource(ressource_id)


@api_endpoints.route('/ressource/<int:ressource_id>', methods=['PUT'])
def update_ressource_endpoint(ressource_id):
    return update_ressource(ressource_id)


@api_endpoints.route('/ressource/<int:ressource_id>/download', methods=['GET'])
def download_ressource_file_endpoint(ressource_id):
    return download_ressource_file(ressource_id)


@api_endpoints.route('/ressource/opgaveskabelon/<int:opgaveskabelon_id>', methods=['GET'])
def get_ressources_by_opgaveskabelonid_endpoint(opgaveskabelon_id):
    return get_ressources_by_opgaveskabelonid(opgaveskabelon_id)


@api_endpoints.route('/opgaveskabelon', methods=['POST'])
def create_opgaveskabelon_endpoint():
    return create_opgaveskabelon()


@api_endpoints.route('/opgaveskabelon', methods=['GET'])
def get_all_opgaveskabeloner_endpoint():
    return get_all_opgaveskabeloner()


@api_endpoints.route('/opgaveskabelon/<int:opgaveskabelon_id>', methods=['GET'])
def get_opgaveskabelon_endpoint(opgaveskabelon_id):
    return get_opgaveskabelon(opgaveskabelon_id)


@api_endpoints.route('/opgaveskabelon/<int:opgaveskabelon_id>', methods=['PUT'])
def update_opgaveskabelon_endpoint(opgaveskabelon_id):
    return update_opgaveskabelon(opgaveskabelon_id)


@api_endpoints.route('/opgaveskabelon/<int:opgaveskabelon_id>', methods=['DELETE'])
def delete_opgaveskabelon_endpoint(opgaveskabelon_id):
    return delete_opgaveskabelon(opgaveskabelon_id)


@api_endpoints.route('/users', methods=['GET'])
def get_user_data_endpoint():
    return get_user_data()


@api_endpoints.route('/users/email', methods=['GET'])
def get_email_endpoint():
    return get_email()


@api_endpoints.route('/users/dq', methods=['GET'])
def get_dq_numbers_endpoint():
    return get_dq_numbers()


@api_endpoints.route('/users/fullname', methods=['GET'])
def get_fullname_endpoint():
    return get_fullname()


@api_endpoints.route('/users/admin', methods=['GET'])
def get_all_admin_data_endpoint():
    return get_admin_data()


@api_endpoints.route('/cron/notify-expired-tasks', methods=['POST'])
def notify_expired_tasks_endpoint():
    return notify_expired_tasks_aggregated()


@api_endpoints.route('/cron/send-planned-mails', methods=['POST'])
def send_planned_mails_endpoint():
    return send_planned_new_tasks_notifications()


@api_endpoints.route('/cron/get-planned-mails', methods=['GET'])
def get_planned_mails_endpoint():
    return get_planned_mails()


@api_endpoints.route('/cron/purge-mails', methods=['POST'])
def purge_mails_endpoint():
    days = request.args.get('days', default=30, type=int)
    return purge_mails(days)


@api_endpoints.route('/mail/delete/<int:mail_id>', methods=['DELETE'])
def delete_planned_mail_endpoint(mail_id):
    return delete_planned_mail(mail_id)


@api_endpoints.route('/healthz', methods=['GET'])
def healthcheck():
    return 'OK', 200
