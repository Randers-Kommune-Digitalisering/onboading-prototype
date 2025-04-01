from flask import Flask, send_from_directory, redirect, url_for, session, request, abort
from flask_cors import CORS
from healthcheck import HealthCheck
from prometheus_client import generate_latest
from authlib.integrations.flask_client import OAuth

from utils.logging import set_logging_configuration
from utils.config import DEBUG, PORT, COOKIE_SECRET, KEYCLOAK_URL, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET, DISABLE_KEYCLOAK
from api_endpoints import api_endpoints

set_logging_configuration()


def create_app():
    app = Flask(__name__, static_folder='dist', static_url_path='/')

    CORS(app)

    if DISABLE_KEYCLOAK:
        @app.route('/api/userinfo')
        def user_info():
            user_info = {'name': 'Test Testsen', 'email': 'test@test.dk', 'roles': ['Admin', 'Ansvarlig', 'Ny medarbejder']}
            return user_info, 200
    else:
        app.secret_key = COOKIE_SECRET

        oauth = OAuth(app)

        oauth.register(name='keycloak', client_id=KEYCLOAK_CLIENT_ID, client_secret=KEYCLOAK_CLIENT_SECRET, server_metadata_url=f'{KEYCLOAK_URL.rstrip("/")}/.well-known/openid-configuration', client_kwargs={'scope': 'openid profile email'})

        @app.before_request
        def check_authenticated():
            if 'user' not in session and request.path not in ['/login', '/auth', '/healthz', '/metrics']:
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
                user_info['roles'] = user_info.get('resource_access', {}).get(KEYCLOAK_CLIENT_ID, {}).get('roles', [])
                return user_info, 200
            else:
                return redirect(url_for('login'))

    health = HealthCheck()

    app.add_url_rule('/healthz', 'healthcheck', view_func=lambda: health.run())
    app.add_url_rule('/metrics', 'metrics', view_func=generate_latest)

    @app.route('/', defaults={'path': ''})
    def serve_vue_app():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/<path:path>')
    def serve_static_files(path):
        try:
            return send_from_directory(app.static_folder, path)
        except FileNotFoundError:
            return send_from_directory(app.static_folder, 'index.html')
        except Exception as e:
            abort(500, description=str(e))

    app.register_blueprint(api_endpoints)

    return app


app = create_app()


if __name__ == '__main__':  # pragma: no cover
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
