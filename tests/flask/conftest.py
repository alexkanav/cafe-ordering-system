import pytest
from flask import g
from flask_jwt_extended import create_access_token

from flask_app import create_app
from utils.enums import UserRole


@pytest.fixture
def app(db_session):
    app = create_app()

    app.config["TESTING"] = True

    @app.before_request
    def inject_test_db():
        g.db = db_session
        g.db.rollback_needed = False

    return app


@pytest.fixture
def make_token(app):
    def _token(user_id="1", role=UserRole.staff):
        with app.app_context():
            return create_access_token(identity=str(user_id), additional_claims={"role": role.value})

    return _token


@pytest.fixture
def api_client(app):
    return app.test_client()


@pytest.fixture
def authenticated_client(app, make_token):
    def _client(**overrides):
        token = make_token(**overrides)

        client = app.test_client()
        client.set_cookie(
            key="access_token_cookie",
            value=token,
        )
        return client

    return _client


@pytest.fixture
def client_by_role(authenticated_client, api_client):
    def _get(role=None):
        return authenticated_client(role=role) if role else api_client

    return _get
