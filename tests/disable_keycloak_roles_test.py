import main


def test_disable_keycloak_roles_are_applied_and_refreshed():
    # Ensure the DISABLE_KEYCLOAK branch is used when create_app() is called.
    main.DISABLE_KEYCLOAK = True

    # Seed with an initial role.
    main.DISABLE_KEYCLOAK_ROLES = 'OldRole'
    app = main.create_app()
    app.config.update({"TESTING": True})

    client = app.test_client()
    first = client.get('/api/userinfo')
    assert first.status_code == 200
    assert first.get_json().get('roles') == ['OldRole']

    # Change roles and verify the session is updated even though the user is
    # already present in the session cookie.
    main.DISABLE_KEYCLOAK_ROLES = 'Admin, Ansvarlig'
    second = client.get('/api/userinfo')
    assert second.status_code == 200
    assert second.get_json().get('roles') == ['Admin', 'Ansvarlig']
