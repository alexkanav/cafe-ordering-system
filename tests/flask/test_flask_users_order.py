import pytest

from tests.flask.constants import USERS_SERVICES
from tests.factories.order import make_order_payload, make_order_operation_result_schema
from utils.enums import UserRole

ORDER_URL = "/api/users/order"
DISCOUNT_URL = "/api/users/discount"


def test_place_order__valid_order__returns_201(authenticated_client, mocker):
    order_id = 11
    lead_time = 25

    client = authenticated_client(role=UserRole.client)

    mocker.patch(
        f"{USERS_SERVICES}.create_order",
        return_value=make_order_operation_result_schema(id=order_id, leadTime=lead_time),
    )

    response = client.post(
        ORDER_URL,
        json=make_order_payload(),
    )

    assert response.status_code == 201

    assert response.get_json() == {
        "message": "Замовлення прийнято",
        "id": order_id,
        "leadTime": lead_time,
    }


def test_place_order__unauthenticated__returns_401(api_client):
    response = api_client.post(
        ORDER_URL,
        json=make_order_payload(),
    )

    assert response.status_code == 401


@pytest.mark.parametrize("payload, expected_status", [
    ({"order": "invalid_order"}, 422),
    ({}, 400),
])
def test_place_order__invalid_payload__returns_400_or_422(
        authenticated_client,
        payload,
        expected_status,
):
    client = authenticated_client(role=UserRole.client)

    response = client.post(ORDER_URL, json=payload)

    assert response.status_code == expected_status


def test_get_discount__authenticated_user__returns_200(authenticated_client):
    client = authenticated_client(role=UserRole.client)

    response = client.get(DISCOUNT_URL)

    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data["discount"], int)


def test_get_discount__unauthenticated__returns_401(api_client):
    response = api_client.get(DISCOUNT_URL)

    assert response.status_code == 401
