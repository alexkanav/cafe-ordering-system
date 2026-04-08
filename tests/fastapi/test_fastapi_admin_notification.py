import pytest

from tests.fastapi.constants import ADMIN_SERVICES
from utils.enums import UserRole
from domain.core.errors import NOT_AUTHENTICATED, INSUFFICIENT_ROLE, NotFoundError

notification_id = 5
NOTIFICATIONS_URL = "/api/admin/notifications"
MARK_NOTIFICATIONS_URL = f"{NOTIFICATIONS_URL}/{notification_id}"


@pytest.mark.parametrize("role, expected_status, detail", [
    (UserRole.staff, 200, None),
    (UserRole.client, 403, INSUFFICIENT_ROLE),
    (None, 401, NOT_AUTHENTICATED),
])
def test_get_notifications__access_by_role__returns_200_or_403_or_401(
        client_by_role,
        role,
        expected_status,
        detail,
):
    client = client_by_role(role)

    response = client.get(NOTIFICATIONS_URL)

    assert response.status_code == expected_status

    if expected_status == 200:
        assert isinstance(response.json(), list)
    else:
        assert response.json() == {"detail": detail}


def test_mark_notification_as_read__staff_user__returns_200(
        authenticated_client,
        mocker,
):
    mark_notification_as_read = mocker.patch(
        f"{ADMIN_SERVICES}.mark_notification_as_read"
    )

    client = authenticated_client(role=UserRole.staff)

    response = client.patch(MARK_NOTIFICATIONS_URL)

    mark_notification_as_read.assert_called_once_with(mocker.ANY, notification_id, mocker.ANY)

    assert response.status_code == 200
    assert response.json() == {"message": f"Сповіщення:{notification_id} помічене як прочитане"}


@pytest.mark.parametrize("role, expected_status, detail", [
    (UserRole.client, 403, INSUFFICIENT_ROLE),
    (None, 401, NOT_AUTHENTICATED),
])
def test_mark_notification_as_read__unauthorized_access__returns_403_or_401(
        client_by_role,
        role,
        expected_status,
        detail,
):
    client = client_by_role(role)

    response = client.patch(MARK_NOTIFICATIONS_URL)

    assert response.status_code == expected_status
    assert response.json() == {"detail": detail}


def test_mark_notification_as_read__service_not_found__returns_404(
        authenticated_client,
        mocker,
):
    mocker.patch(
        f"{ADMIN_SERVICES}.mark_notification_as_read",
        side_effect=NotFoundError("Not Found")
    )

    client = authenticated_client(role=UserRole.staff)

    response = client.patch(MARK_NOTIFICATIONS_URL)

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_unread_notification_count__staff_user__returns_correct_count(
        authenticated_client,
        mocker,
):
    mocker.patch(
        f"{ADMIN_SERVICES}.count_unread_notifications",
        return_value=notification_id
    )

    client = authenticated_client(role=UserRole.staff)

    response = client.get(f"{NOTIFICATIONS_URL}/unread/count")

    assert response.status_code == 200
    assert response.json()["unread_notif_count"] == notification_id


@pytest.mark.parametrize("role, expected_status, detail", [
    (UserRole.client, 403, INSUFFICIENT_ROLE),
    (None, 401, NOT_AUTHENTICATED),
])
def test_unread_notification_count__unauthorized_access__returns_403_or_401(
        client_by_role,
        role,
        expected_status,
        detail,
):
    client = client_by_role(role)

    response = client.get(f"{NOTIFICATIONS_URL}/unread/count")

    assert response.status_code == expected_status
    assert response.json() == {"detail": detail}
