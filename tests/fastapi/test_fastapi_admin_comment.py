import pytest

from tests.fastapi.constants import ADMIN_SERVICES, ADMIN_ROUTES
from utils.enums import UserRole, CommentStatus
from domain.core.errors import NOT_AUTHENTICATED, INSUFFICIENT_ROLE, NotFoundError
from domain.core.constants import CacheNamespace

comments_id = 4
COMMENTS_URL = f"/api/admin/comments/{comments_id}"


@pytest.mark.parametrize("status", list(CommentStatus))
def test_update_comment_status__success__returns_200(authenticated_client, status, mocker):
    user_id = 100
    client = authenticated_client(user_id=user_id, role=UserRole.moderator)

    mock = mocker.patch(
        f"{ADMIN_SERVICES}.update_comment_status"
    )

    mock_clear = mocker.patch(
        f"{ADMIN_ROUTES}.FastAPICache.clear"
    )

    response = client.patch(COMMENTS_URL, json={"status": status.value})

    mock.assert_called_once_with(mocker.ANY, user_id, comments_id, status)
    mock_clear.assert_called_once_with(CacheNamespace.COMMENTS)

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Коментар {comments_id} змінив статус на {status.value}"
    }


@pytest.mark.parametrize("role, expected_status, detail", [
    (UserRole.client, 403, INSUFFICIENT_ROLE),
    (None, 401, NOT_AUTHENTICATED),
])
def test_update_comment_status__unauthorized_access__returns_403_or_401(
        client_by_role,
        role,
        expected_status,
        detail,
):
    client = client_by_role(role)

    response = client.patch(
        COMMENTS_URL,
        json={"status": CommentStatus.approved.value}
    )

    assert response.status_code == expected_status
    assert response.json() == {"detail": detail}


def test_update_comment_status__service_not_found__returns_404(authenticated_client, mocker):
    client = authenticated_client(role=UserRole.moderator)

    mocker.patch(
        f"{ADMIN_SERVICES}.update_comment_status",
        side_effect=NotFoundError("Not Found")
    )

    response = client.patch(
        COMMENTS_URL,
        json={"status": CommentStatus.approved.value}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


def test_update_comment_status__invalid_payload__returns_422(authenticated_client, mocker):
    client = authenticated_client(role=UserRole.moderator)

    response = client.patch(
        COMMENTS_URL,
        json={"status": "incorrect data"}
    )

    assert response.status_code == 422
