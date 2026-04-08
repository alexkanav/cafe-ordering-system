import pytest

from tests.fastapi.constants import USERS_SERVICES
from domain.core.errors import NotFoundError, ConflictError, DomainValidationError, NOT_AUTHENTICATED, INSUFFICIENT_ROLE
from utils.enums import UserRole

coupon_id = 5
COUPON_URL = f"/api/users/coupon/{coupon_id}"


def test_check_coupon__valid_coupon__returns_200(
        authenticated_client,
        mocker,
):
    discount = 7

    mocker.patch(
        f"{USERS_SERVICES}.check_coupon",
        return_value=discount,
    )
    client = authenticated_client(role=UserRole.client)

    response = client.post(COUPON_URL)

    assert response.status_code == 200

    assert response.json() == {"discount": discount}


@pytest.mark.parametrize("response_error, expected_status, detail", [
    (DomainValidationError("Coupon expired"), 400, "Coupon expired"),
    (NotFoundError("Coupon not found"), 404, "Coupon not found"),
    (ConflictError("Coupon inactive"), 409, "Coupon inactive"),
])
def test_check_coupon__service_errors__returns_400_or_404_or_409(
        authenticated_client,
        mocker,
        response_error,
        expected_status,
        detail,
):
    mocker.patch(
        f"{USERS_SERVICES}.check_coupon",
        side_effect=response_error

    )
    client = authenticated_client(role=UserRole.client)

    response = client.post(COUPON_URL)

    assert response.status_code == expected_status

    assert response.json() == {"detail": detail}


def test_check_coupon__unauthenticated__returns_401(api_client):
    response = api_client.post(COUPON_URL)

    assert response.status_code == 401
