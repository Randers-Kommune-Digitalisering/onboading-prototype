from flask import Flask, redirect, url_for, session, request, jsonify
from flask_cors import CORS
from healthcheck import HealthCheck
from prometheus_client import generate_latest
from authlib.integrations.flask_client import OAuth

from utils.logging import set_logging_configuration
from utils.config import DEBUG, PORT, COOKIE_SECRET, KEYCLOAK_URL, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET, DISABLE_KEYCLOAK
from api_endpoints import api_endpoints
from controllers.user_controller import azure_data_exists, get_and_save_azure_ad_data
from utils.db_connection import create_db_client, add_missing_columns

set_logging_configuration()


def create_app():
    app = Flask(__name__, static_folder='dist')
    CORS(app)

    if DISABLE_KEYCLOAK:
        @app.route('/api/userinfo')
        def user_info():
            user_info = {'name': 'Test Testsen', 'email': 'Test.Robot@randers.dk', 'roles': ['Admin', 'Ansvarlig']}
            return user_info, 200
    else:
        app.secret_key = COOKIE_SECRET

        oauth = OAuth(app)

        oauth.register(name='keycloak', client_id=KEYCLOAK_CLIENT_ID, client_secret=KEYCLOAK_CLIENT_SECRET, server_metadata_url=f'{KEYCLOAK_URL.rstrip("/")}/.well-known/openid-configuration', client_kwargs={'scope': 'openid profile email'})

        @app.before_request
        def check_authenticated():
            if 'user' in session:
                return None

            # Always allow static assets for the SPA to load.
            if request.path.startswith('/assets/'):
                return None

            if request.path == '/favicon.ico':
                return None

            # Allow the external access flow only on the ForløbOverview route.
            if request.path == '/forloeb-overview' and request.args.get('external', '').lower() == 'true':
                return None

            # Allow external API endpoints (they validate via accessKey).
            if request.path.startswith('/api/external/'):
                return None

            # Allow userinfo lookup to return a JSON 401 (frontend falls back to Public).
            if request.path == '/api/userinfo':
                return None

            if request.path not in ['/login', '/auth', '/healthz', '/metrics', '/api/cron/notify-expired-tasks', '/api/cron/send-planned-mails']:
                return redirect(url_for("login"))

        @app.route("/login")
        def login():
            redirect_uri = url_for("auth", _external=True)
            return oauth.keycloak.authorize_redirect(redirect_uri)

        @app.route("/auth")
        def auth():
            token = oauth.keycloak.authorize_access_token()
            session["user"] = token['userinfo']
            return redirect("/")

        @app.route('/api/userinfo')
        def user_info():
            if 'user' in session:
                user_info = session['user']
                user_info['roles'] = user_info.get('resource_access', {}).get(KEYCLOAK_CLIENT_ID, {}).get('roles', ["Ny medarbejder", "Ansvarlig"])
                return user_info, 200
            else:
                return jsonify({"error": "Not authenticated"}), 401

    # Create database client
    create_db_client()
    add_missing_columns()

    # Import Azure data
    if not azure_data_exists():
        get_and_save_azure_ad_data()

    health = HealthCheck()

    app.add_url_rule('/healthz', 'healthcheck', view_func=lambda: health.run())
    app.add_url_rule('/metrics', 'metrics', view_func=generate_latest)

    app.register_blueprint(api_endpoints)

    @app.route('/assets/<path:path>')
    def static_file(path):
        return app.send_static_file('assets/' + path)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def index(path):
        return app.send_static_file('index.html')

    return app


app = create_app()


if __name__ == '__main__':  # pragma: no cover
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
