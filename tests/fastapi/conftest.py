import pytest
from fastapi.testclient import TestClient

from fastapi_app.main import app
from fastapi_app.dependencies.db import get_db
from fastapi_app.dependencies.auth import get_current_user
from domain import schemas
from utils.enums import UserRole


@pytest.fixture
def api_client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def authenticated_client(api_client):
    def _make_client(user_id=1, role=UserRole.staff):
        app.dependency_overrides[get_current_user] = (
            lambda: schemas.CurrentUserSchema(id=user_id, role=role)
        )
        return api_client

    yield _make_client

    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def client_by_role(authenticated_client, api_client):
    def _get(role):
        return authenticated_client(role=role) if role else api_client

    return _get
