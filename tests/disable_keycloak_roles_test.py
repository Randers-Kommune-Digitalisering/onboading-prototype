import main


def test_disable_keycloak_identity_and_roles_are_applied_and_refreshed():
    # Ensure the DISABLE_KEYCLOAK branch is used when create_app() is called.
    main.DISABLE_KEYCLOAK = True

    # Seed with an initial role and identity.
    main.DISABLE_KEYCLOAK_ROLES = 'OldRole'
    main.DISABLE_KEYCLOAK_USER_EMAIL = 'old.user@example.com'
    main.DISABLE_KEYCLOAK_USER_NAME = 'Old User'
    app = main.create_app()
    app.config.update({"TESTING": True})

    client = app.test_client()
    first = client.get('/api/userinfo')
    assert first.status_code == 200
    assert first.get_json().get('roles') == ['OldRole']
    assert first.get_json().get('email') == 'old.user@example.com'
    assert first.get_json().get('name') == 'Old User'

    # Change identity + roles and verify the session is updated even though the
    # user is already present in the session cookie.
    main.DISABLE_KEYCLOAK_ROLES = 'Admin, Ansvarlig'
    main.DISABLE_KEYCLOAK_USER_EMAIL = 'new.user@example.com'
    main.DISABLE_KEYCLOAK_USER_NAME = 'New User'
    second = client.get('/api/userinfo')
    assert second.status_code == 200
    assert second.get_json().get('roles') == ['Admin', 'Ansvarlig']
    assert second.get_json().get('email') == 'new.user@example.com'
    assert second.get_json().get('name') == 'New User'
