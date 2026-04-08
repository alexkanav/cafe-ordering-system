import pytest

from tests.fastapi.constants import ADMIN_SERVICES
from domain.core.errors import NotFoundError, ConflictError, NOT_AUTHENTICATED, INSUFFICIENT_ROLE
from utils.enums import UserRole

order_id = 8
ORDERS_URL = "/api/admin/orders"
COMPLETE_URL = f"{ORDERS_URL}/{order_id}/complete"


@pytest.mark.parametrize("role, expected_status, detail", [
    (UserRole.staff, 200, None),
    (UserRole.client, 403, INSUFFICIENT_ROLE),
    (None, 401, NOT_AUTHENTICATED),
])
def test_get_orders__access_by_role__returns_200_or_403_or_401(
        client_by_role,
        role,
        expected_status,
        detail,
):
    client = client_by_role(role)

    response = client.get(ORDERS_URL)

    assert response.status_code == expected_status

    data = response.json()

    if expected_status == 200:
        assert isinstance(data["orders"], list)
        assert isinstance(data["orders_count"], int)

    else:
        assert data == {"detail": detail}


def test_get_orders_count__returns_count(authenticated_client, mocker):
    count = 11
    mocker.patch(
        f"{ADMIN_SERVICES}.get_orders_count",
        return_value=count
    )

    client = authenticated_client(role=UserRole.staff)

    response = client.get(f"{ORDERS_URL}/count")

    assert response.status_code == 200
    assert response.json() == {"count": count}


def test_complete_order__staff_user__returns_200(
        authenticated_client,
        mocker,
):
    mock_complete_order = mocker.patch(
        f"{ADMIN_SERVICES}.complete_order"
    )
    client = authenticated_client(role=UserRole.staff)

    response = client.patch(COMPLETE_URL)

    assert response.status_code == 200
    mock_complete_order.assert_called_once_with(mocker.ANY, order_id, mocker.ANY)

    assert response.json() == {
        "message": f"Замовлення:{order_id} виконано."
    }


@pytest.mark.parametrize("role, expected_status, detail", [
    (UserRole.client, 403, INSUFFICIENT_ROLE),
    (None, 401, NOT_AUTHENTICATED),
])
def test_complete_order__unauthorized_access__returns_403_or_401(
        client_by_role,
        role,
        expected_status,
        detail,
):
    client = client_by_role(role)

    response = client.patch(COMPLETE_URL)

    assert response.status_code == expected_status
    assert response.json() == {"detail": detail}


@pytest.mark.parametrize("response_error, expected_status, detail", [
    (NotFoundError("Order not found"), 404, "Order not found"),
    (ConflictError("Order already completed"), 409, "Order already completed"),
])
def test_complete_order__service_errors__returns_404_or_409(
        authenticated_client,
        mocker,
        response_error,
        expected_status,
        detail,
):
    mocker.patch(
        f"{ADMIN_SERVICES}.complete_order",
        side_effect=response_error
    )
    client = authenticated_client(role=UserRole.staff)

    response = client.patch(COMPLETE_URL)

    assert response.status_code == expected_status
    assert response.json() == {"detail": detail}
