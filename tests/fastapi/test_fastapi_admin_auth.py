import pytest
from sqlalchemy.exc import SQLAlchemyError

from fastapi_app.auth.jwt import create_access_token, decode_access_token
from utils.enums import UserRole
from tests.factories.register import make_register_payload, make_login_payload
from tests.fastapi.constants import ADMIN_SERVICES
from domain.core.errors import NOT_AUTHENTICATED, INSUFFICIENT_ROLE, USER_NOT_FOUND

ME_URL = "/api/admin/me"
REGISTER_URL = "/api/admin/auth/register"
LOGIN_URL = "/api/admin/auth/login"
REGISTER_LIMIT = 10
LOGIN_LIMIT = 5
email = "user@test.com"


@pytest.mark.parametrize("role, expected_status", [
    (UserRole.staff, 200),
    (UserRole.client, 403),
])
def test_get_me__access_by_role__returns_current_user_or_403(create_staff_user, api_client, role, expected_status):
    user_id = create_staff_user().id
    token = create_access_token(
        subject=str(user_id),
        role=role
    )
    response = api_client.get(
        ME_URL,
        cookies={"access_token": token}
    )
    assert response.status_code == expected_status

    if expected_status == 200:
        assert response.json() == {"id": user_id, "role": UserRole.staff}
    else:
        assert response.json() == {"detail": INSUFFICIENT_ROLE}


def test_get_me__nonexistent_user__returns_403(api_client):
    token = create_access_token(
        subject="150",
        role=UserRole.staff
    )
    response = api_client.get(
        ME_URL,
        cookies={"access_token": token}
    )
    assert response.status_code == 403
    assert response.json() == {"detail": USER_NOT_FOUND}


def test_get_me__unauthenticated_user__returns_401(api_client):
    response = api_client.get(ME_URL)

    assert response.status_code == 401
    assert response.json() == {"detail": NOT_AUTHENTICATED}


def test_register__valid_data__returns_user_id_and_sets_cookie(clear_rate_limits, api_client):
    response = api_client.post(
        REGISTER_URL,
        json=make_register_payload(),
    )
    assert response.status_code == 201

    body = response.json()
    user_id = body.get("user_id")
    assert user_id is not None, "Response did not include user_id"

    token = response.cookies.get("access_token")
    assert token is not None
    assert token != ""

    decoded = decode_access_token(token)
    assert decoded.role == UserRole.staff


def test_register__rate_limit_exceeded__returns_429(clear_rate_limits, api_client):
    for i in range(REGISTER_LIMIT):
        response = api_client.post(
            REGISTER_URL,
            json=make_register_payload(email=f"user{i}@test.com"),
        )
        assert response.status_code == 201

    response = api_client.post(
        REGISTER_URL,
        json=make_register_payload(email=f"user_@test.com"),
    )

    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests"}


def test_register__email_already_exists__returns_409(clear_rate_limits, api_client):
    test_email = "t1@test.com"
    api_client.post(REGISTER_URL, json=make_register_payload(email=test_email))
    response = api_client.post(REGISTER_URL, json=make_register_payload(email=test_email))

    assert response.status_code == 409
    assert response.json() == {"detail": f"Email {test_email} вже використана"}


def test_register__server_error__returns_500(api_client, mocker):
    mocker.patch(
        f"{ADMIN_SERVICES}.register_staff",
        side_effect=SQLAlchemyError("Coupon not found")
    )

    response = api_client.post(REGISTER_URL, json=make_register_payload())
    assert response.status_code == 500


def test_login__valid_credentials__returns_user_id_and_sets_cookie(clear_rate_limits, create_staff_user, api_client):
    user_id = create_staff_user(email=email).id

    response = api_client.post(
        LOGIN_URL,
        json=make_login_payload(email=email),
    )
    assert response.status_code == 200

    assert response.json()["user_id"] == user_id

    token = response.cookies.get("access_token")
    assert token

    decoded = decode_access_token(token)
    assert decoded.sub == str(user_id)
    assert decoded.role == UserRole.staff


def test_login__rate_limit_exceeded__returns_429(clear_rate_limits, create_staff_user, api_client):
    create_staff_user(email=email)

    for _ in range(LOGIN_LIMIT):
        response = api_client.post(
            LOGIN_URL,
            json=make_login_payload(email=email),
        )
        assert response.status_code == 200

    response = api_client.post(
        LOGIN_URL,
        json=make_login_payload(email=email),
    )

    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests"}


def test_login__invalid_password__returns_401(clear_rate_limits, create_staff_user, api_client):
    create_staff_user(email=email)
    response = api_client.post(
        LOGIN_URL,
        json=make_login_payload(password="1111"),
    )
    assert response.status_code == 401
    assert response.json() == {"detail": 'Відмова: Email та пароль не збігаються'}


def test_logout__returns_200_and_clears_cookie(api_client):
    response = api_client.post("/api/admin/auth/logout")

    assert response.status_code == 200

    set_cookie = response.headers.get("set-cookie", "").lower()

    assert "access_token=" in set_cookie
    assert "max-age=0" in set_cookie
