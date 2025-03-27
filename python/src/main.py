import os
from flask import Flask, send_from_directory, redirect, url_for, session, request
from flask_cors import CORS
from healthcheck import HealthCheck
from prometheus_client import generate_latest
from authlib.integrations.flask_client import OAuth

from utils.logging import set_logging_configuration
from utils.config import DEBUG, PORT, COOKIE_SECRET, KEYCLOAK_URL, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET
from api_endpoints import api_endpoints  # Uncomment to import enpoints

set_logging_configuration()


def create_app():    
    app = Flask(__name__, static_folder='dist', static_url_path='/')
    # app.secret_key = COOKIE_SECRET

    CORS(app)

    # oauth = OAuth(app)

    # oauth.register(name='keycloak', client_id=KEYCLOAK_CLIENT_ID, client_secret=KEYCLOAK_CLIENT_SECRET, server_metadata_url=f'{KEYCLOAK_URL.rstrip("/")}/.well-known/openid-configuration', client_kwargs={'scope': 'openid profile email'})

    health = HealthCheck()

    app.add_url_rule('/healthz', 'healthcheck', view_func=lambda: health.run())
    app.add_url_rule('/metrics', 'metrics', view_func=generate_latest)

    @app.before_request
    def check_authenticated():
        if 'user' not in session and request.path != '/login' and request.path != '/auth':
            return redirect(url_for("login"))

    @app.route("/login")
    def login():
        redirect_uri = url_for("auth", _external=True)
        return oauth.keycloak.authorize_redirect(redirect_uri)

    @app.route("/auth")
    def auth():
        token = oauth.keycloak.authorize_access_token()
        session["user"] = oauth.keycloak.parse_id_token(token, None)
        return redirect("/")

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    app.register_blueprint(api_endpoints)

    return app


app = create_app()


if __name__ == '__main__':  # pragma: no cover
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
