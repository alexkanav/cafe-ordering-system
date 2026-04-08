import pytest

from tests.factories.coupon import make_coupon_payload
from domain.core.errors import NotFoundError, ConflictError
from tests.fastapi.constants import ADMIN_SERVICES
from utils.enums import UserRole

COUPONS_URL = "/api/admin/coupons"
coupon_id = 15
DEACTIVATE_URL = f"{COUPONS_URL}/{coupon_id}/deactivate"


@pytest.mark.parametrize("role, expected_status", [
    (UserRole.staff, 200),
    (UserRole.client, 403),
    (None, 401),
])
def test_get_coupons__access_by_role__returns_200_or_403_or_401(
        client_by_role,
        role,
        expected_status,
):
    client = client_by_role(role)

    response = client.get(COUPONS_URL)

    assert response.status_code == expected_status

    if expected_status == 200:
        assert isinstance(response.get_json(), list)


def test_create_coupon__staff_user__returns_201(
        authenticated_client,
        mocker,
):
    client = authenticated_client(role=UserRole.staff)
    mock_create_coupon = mocker.patch(
        f"{ADMIN_SERVICES}.create_coupon",
        return_value=coupon_id
    )

    response = client.post(COUPONS_URL, json=make_coupon_payload())

    assert response.status_code == 201

    mock_create_coupon.assert_called_once()

    assert response.get_json() == {
        "message": f"Додано купон id={coupon_id}"
    }


@pytest.mark.parametrize("role, expected_status", [
    (UserRole.client, 403),
    (None, 401),
])
def test_create_coupon__unauthorized_access__returns_403_or_401(
        client_by_role,
        role,
        expected_status,
):
    client = client_by_role(role)

    response = client.post(COUPONS_URL, json=make_coupon_payload())

    assert response.status_code == expected_status


def test_create_coupon__code_already_exists__returns_409(
        authenticated_client,
        mocker,
):
    mocker.patch(
        f"{ADMIN_SERVICES}.create_coupon",
        side_effect=ConflictError("Coupon already exists")
    )
    client = authenticated_client(role=UserRole.staff)

    response = client.post(COUPONS_URL, json=make_coupon_payload())

    assert response.status_code == 409
    assert response.get_json() == {
        "detail": "Coupon already exists"
    }


def test_create_coupon__invalid_payload__returns_422(authenticated_client):
    client = authenticated_client(role=UserRole.staff)

    response = client.post(COUPONS_URL, json={"invalid": "data"})
    assert response.status_code == 422


def test_deactivate_coupon__staff_user__returns_200(
        authenticated_client,
        mocker,
):
    mock_deactivate_coupon = mocker.patch(
        f"{ADMIN_SERVICES}.deactivate_coupon"
    )

    client = authenticated_client(role=UserRole.staff)

    response = client.patch(DEACTIVATE_URL)

    assert response.status_code == 200

    data = response.get_json()
    mock_deactivate_coupon.assert_called_once_with(mocker.ANY, coupon_id)

    assert "message" in data
    assert str(coupon_id) in data["message"]


@pytest.mark.parametrize("role, expected_status", [
    (UserRole.client, 403),
    (None, 401),
])
def test_deactivate_coupon__unauthorized_access__returns_403_or_401(
        client_by_role,
        role,
        expected_status,
):
    client = client_by_role(role)

    response = client.patch(DEACTIVATE_URL)

    assert response.status_code == expected_status


@pytest.mark.parametrize("response_error, expected_status, detail", [
    (NotFoundError("Coupon not found"), 404, "Coupon not found"),
    (ConflictError("Coupon already inactive"), 409, "Coupon already inactive"),
])
def test_deactivate_coupon__service_errors__returns_404_or_409(
        authenticated_client,
        mocker,
        response_error,
        expected_status,
        detail,
):
    mocker.patch(
        f"{ADMIN_SERVICES}.deactivate_coupon",
        side_effect=response_error
    )
    client = authenticated_client(role=UserRole.staff)

    response = client.patch(DEACTIVATE_URL)
    assert response.status_code == expected_status
    assert response.get_json() == {
        "detail": detail
    }
