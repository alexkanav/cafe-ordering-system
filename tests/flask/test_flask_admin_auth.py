import pytest
from flask_jwt_extended import decode_token
from sqlalchemy.exc import SQLAlchemyError
import uuid

from utils.enums import UserRole
from tests.factories.register import make_register_payload, make_login_payload
from tests.flask.constants import ADMIN_SERVICES

ME_URL = "/api/admin/me"
REGISTER_URL = "/api/admin/auth/register"
LOGIN_URL = "/api/admin/auth/login"
REGISTER_LIMIT = 10
LOGIN_LIMIT = 5


@pytest.mark.parametrize("role, expected_status", [
    (UserRole.staff, 200),
    (UserRole.client, 403),
])
def test_get_me__access_by_role__returns_current_user_or_403(
        create_staff_user,
        authenticated_client,
        role,
        expected_status
):
    user_id = create_staff_user(email=f"{uuid.uuid4().hex}@test.com").id
    client = authenticated_client(user_id=str(user_id), role=role)

    response = client.get(ME_URL)

    assert response.status_code == expected_status

    if response.status_code == 200:
        assert response.get_json() == {
            "id": user_id,
            "role": UserRole.staff.value
        }


def test_get_me__nonexistent_user__returns_403(authenticated_client):
    client = authenticated_client(user_id=str(88), role=UserRole.client)

    response = client.get(ME_URL)

    assert response.status_code == 403


def test_get_me__unauthenticated_user__returns_401(api_client):
    response = api_client.get(ME_URL)

    assert response.status_code == 401


def test_register__valid_data__returns_user_id_and_sets_cookie(clear_rate_limits, api_client, app):
    response = api_client.post(
        REGISTER_URL,
        json=make_register_payload(email=f"{uuid.uuid4().hex}@test.com"),
    )
    assert response.status_code == 201

    data = response.get_json()
    assert isinstance(data["user_id"], int)

    cookie = api_client.get_cookie("access_token_cookie")
    assert cookie is not None

    token = cookie.value

    with app.app_context():
        decoded = decode_token(token)

    assert decoded["role"] == "staff"


def test_register__rate_limit_exceeded__returns_429(clear_rate_limits, api_client):
    for i in range(REGISTER_LIMIT):
        response = api_client.post(
            REGISTER_URL,
            json=make_register_payload(email=f"staff_user{i}@test.com"),
        )
        assert response.status_code == 201

    response = api_client.post(
        REGISTER_URL,
        json=make_register_payload(email="staff_user@test.com"),
    )

    assert response.status_code == 429


def test_register__email_already_exists__returns_409(clear_rate_limits, api_client):
    payload = make_register_payload(email=f"{uuid.uuid4().hex}@test.com")
    api_client.post(REGISTER_URL, json=payload)

    response = api_client.post(REGISTER_URL, json=payload)

    assert response.status_code == 409
    assert response.get_json() == {"detail": f"Email {payload['email']} вже використана"}


def test_register__missing_required_field__returns_422(clear_rate_limits, api_client):
    payload = make_register_payload()
    del payload["email"]

    response = api_client.post(
        REGISTER_URL,
        json=payload
    )

    assert response.status_code == 422


def test_register__no_json_body__returns_400(clear_rate_limits, api_client):
    response = api_client.post(
        REGISTER_URL,
        data="not-json",
        content_type="text/plain"
    )

    assert response.status_code == 400
    assert response.get_json() == {"detail": "Invalid JSON"}


def test_register__server_error__returns_500(clear_rate_limits, api_client, mocker):
    mocker.patch(
        f"{ADMIN_SERVICES}.register_staff",
        side_effect=SQLAlchemyError("Server error")
    )

    response = api_client.post(REGISTER_URL, json=make_register_payload())
    assert response.status_code == 500
    assert response.get_json() == {"detail": "Не вдалося зареєструвати користувача"}


def test_login__valid_credentials__returns_user_id_and_sets_cookie(
        clear_rate_limits,
        create_staff_user,
        api_client,
        app
):
    email = f"{uuid.uuid4().hex}@test.com"
    user_id = create_staff_user(email=email).id

    response = api_client.post(
        LOGIN_URL,
        json=make_login_payload(email=email)
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["user_id"] == user_id

    cookie = api_client.get_cookie("access_token_cookie")
    assert cookie is not None

    token = cookie.value

    with app.app_context():
        decoded = decode_token(token)

    assert decoded["role"] == "staff"


def test_login__rate_limit_exceeded__returns_429(clear_rate_limits, create_staff_user, api_client):
    email = f"{uuid.uuid4().hex}@test.com"
    create_staff_user(email=email)

    for _ in range(LOGIN_LIMIT):
        response = api_client.post(
            LOGIN_URL,
            json=make_login_payload(email=email)
        )
        assert response.status_code == 200

    response = api_client.post(
        LOGIN_URL,
        json=make_login_payload(email=email),
    )

    assert response.status_code == 429


def test_login__invalid_password__returns_401(create_staff_user, api_client):
    email = f"{uuid.uuid4().hex}@test.com"
    create_staff_user(email=email, password="1234")

    response = api_client.post(
        LOGIN_URL,
        json=make_login_payload(email=email, password="1111")
    )
    assert response.status_code == 401


def test_login__missing_required_field__returns_422(api_client):
    response = api_client.post(LOGIN_URL, json={"password": "1234"})
    assert response.status_code == 422


def test_login__no_json_body__returns_400(api_client):
    response = api_client.post(
        LOGIN_URL,
    )
    assert response.status_code == 400
    assert response.get_json() == {"detail": "Invalid JSON"}


def test_logout__valid_request__clears_cookie(api_client):
    response = api_client.post("/api/admin/auth/logout")

    assert response.status_code == 200

    data = response.get_json()
    assert data["message"] == "Ви вийшли з системи"

    cookies = response.headers.getlist("Set-Cookie")

    assert any("access_token_cookie=;" in c for c in cookies)
