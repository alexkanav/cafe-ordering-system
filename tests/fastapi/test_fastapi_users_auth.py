from fastapi_app.auth.jwt import create_access_token, decode_access_token
from utils.enums import UserRole
from domain.core.errors import NOT_AUTHENTICATED

URL_PREFIX = "/api/users"
ME_URL = f"{URL_PREFIX}/me"
RATE_LIMIT = 10


def test_get_me__authorized_user__returns_current_user(create_client_user, api_client):
    user_id = create_client_user().id
    token = create_access_token(
        subject=str(user_id),
        role=UserRole.client
    )
    response = api_client.get(
        ME_URL,
        cookies={"access_token": token}
    )
    assert response.status_code == 200

    assert response.json() == {
        "id": user_id,
        "role": UserRole.client.value
    }


def test_get_me__not_authenticated_user__returns_401(api_client):
    response = api_client.get(ME_URL)

    assert response.status_code == 401
    assert response.json() == {"detail": NOT_AUTHENTICATED}


def test_create_user__returns_user_id_and_sets_cookie(db_session, api_client):
    response = api_client.post(URL_PREFIX)
    assert response.status_code == 201

    body = response.json()
    user_id = body.get("user_id")
    assert user_id is not None, "Response did not include user_id"

    token = response.cookies.get("access_token")
    assert token is not None
    assert token != ""

    decoded = decode_access_token(token)
    assert decoded.role == UserRole.client


def test_create_user__rate_limit_exceeded__returns_429(clear_rate_limits, api_client):
    for _ in range(RATE_LIMIT):
        response = api_client.post(URL_PREFIX)
        assert response.status_code == 201

    response = api_client.post(URL_PREFIX)

    assert response.status_code == 429
    assert response.json()["detail"] == "Too many requests"
