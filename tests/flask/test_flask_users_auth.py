from flask_jwt_extended import decode_token

from utils.enums import UserRole

URL_PREFIX = "/api/users/"
ME_URL = f"{URL_PREFIX}me"
RATE_LIMIT = 10


def test_get_me__client_user__returns_current_user(create_client_user, authenticated_client):
    user_id = create_client_user().id

    client = authenticated_client(user_id=str(user_id), role=UserRole.client)

    response = client.get(ME_URL)

    assert response.status_code == 200
    assert response.get_json() == {
        "id": user_id,
        "role": UserRole.client.value
    }

def test_get_me__nonexistent_user__returns_403(authenticated_client):
    client = authenticated_client(user_id=str(88), role=UserRole.client)

    response = client.get(ME_URL)

    assert response.status_code == 403


def test_get_me__not_authenticated_user__returns_401(api_client):
    response = api_client.get(ME_URL)

    assert response.status_code == 401


def test_create_user__returns_user_id_and_sets_cookie(clear_rate_limits, api_client, app):
    response = api_client.post(URL_PREFIX)

    assert response.status_code == 201

    data = response.get_json()
    assert isinstance(data["user_id"], int)

    cookie = api_client.get_cookie("access_token_cookie")
    assert cookie is not None
    assert cookie.value != ""

    token = cookie.value

    with app.app_context():
        decoded = decode_token(token)

    assert decoded["role"] == UserRole.client.value


def test_create_user__rate_limit_exceeded__returns_429(clear_rate_limits, api_client):
    for _ in range(RATE_LIMIT):
        response = api_client.post(URL_PREFIX)
        assert response.status_code == 201

    response = api_client.post(URL_PREFIX)

    assert response.status_code == 429
