from tests.factories.comment import make_comment_schema, make_comment_payload
from tests.fastapi.constants import USERS_SERVICES
from utils.enums import UserRole
from domain.core.errors import NOT_AUTHENTICATED

COMMENTS_URL = "/api/users/comments"
RATE_LIMIT = 2


def test_get_comments__comments_exist__returns_comments(api_client, mocker, clear_cache):
    comment = make_comment_schema()

    mock_get_comment = mocker.patch(
        f"{USERS_SERVICES}.get_comments",
        return_value=[comment]
    )

    response = api_client.get(COMMENTS_URL)

    mock_get_comment.assert_called_once_with(mocker.ANY, limit=10)
    assert response.status_code == 200
    assert response.json() == {
        "comments": [comment.model_dump(mode="json")]
    }


def test_get_comments__cached__returns_cached_result(api_client, mocker, clear_cache):
    mock = mocker.patch(f"{USERS_SERVICES}.get_comments", return_value=[])

    api_client.get(COMMENTS_URL)
    response = api_client.get(COMMENTS_URL)

    assert mock.call_count == 1
    assert response.status_code == 200
    assert response.json() == {"comments": []}


def test_get_comments__no_comments__returns_empty_list(api_client, mocker, clear_cache):
    mocker.patch(
        f"{USERS_SERVICES}.get_comments",
        return_value=[]
    )

    response = api_client.get(COMMENTS_URL)

    assert response.status_code == 200
    assert response.json() == {"comments": []}


def test_create_comment__valid_data__returns_201(client_by_role, clear_rate_limits, mocker):
    comment_id = 5
    client = client_by_role(UserRole.client)

    mock_create_comment = mocker.patch(
        f"{USERS_SERVICES}.create_comment",
        return_value=comment_id
    )

    response = client.post(
        COMMENTS_URL,
        json=make_comment_payload()
    )
    mock_create_comment.assert_called_once()
    assert response.status_code == 201
    assert str(comment_id) in response.json()["message"]


def test_create_comment__rate_limit_exceeded__returns_429(
        clear_rate_limits,
        authenticated_client,
):
    client = authenticated_client(role=UserRole.client)

    for _ in range(RATE_LIMIT):
        response = client.post(
            COMMENTS_URL,
            json=make_comment_payload()
        )

        assert response.status_code == 201

    response = client.post(
        COMMENTS_URL,
        json=make_comment_payload()
    )

    assert response.status_code == 429
    assert response.json() == {"detail": "Too many requests"}


def test_create_comment__unauthenticated__returns_401(api_client):
    response = api_client.post(
        COMMENTS_URL,
        json=make_comment_payload()
    )

    assert response.status_code == 401
    assert response.json() == {"detail": NOT_AUTHENTICATED}


def test_create_comment__invalid_data__returns_422(authenticated_client):
    client = authenticated_client(role=UserRole.client)

    response = client.post(
        COMMENTS_URL,
        json={"invalid": "data"}
    )

    assert response.status_code == 422
