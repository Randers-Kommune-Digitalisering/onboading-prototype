import pytest
from main import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_healthz(client):
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'success'


def test_metrics(client):
    # POD_NAME env var set in pytest.ini (test-pod)
    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'is_ready gauge\nis_ready{error_type="None",job_name="test-pod"} 1.0' in response.text


def test_max_content_length_configured(app):
    assert app.config.get('MAX_CONTENT_LENGTH') == 20 * 1024 * 1024


def test_oversize_upload_returns_413_not_500():
    import main

    # Ensure we don't get redirected to /login during this request.
    main.DISABLE_KEYCLOAK = True

    app = main.create_app()
    app.config.update({
        "TESTING": True,
        "MAX_CONTENT_LENGTH": 1,  # force RequestEntityTooLarge on any non-empty upload
    })

    client = app.test_client()
    payload = {
        "name": "x",
        "OpgaveID": "1",
        "file": (b"ab", "a.txt"),
    }

    response = client.post('/api/ressource/file', data=payload, content_type='multipart/form-data')
    assert response.status_code == 413
