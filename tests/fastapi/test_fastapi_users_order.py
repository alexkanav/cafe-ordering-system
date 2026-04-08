from sqlalchemy.exc import SQLAlchemyError

from tests.fastapi.constants import USERS_SERVICES
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

    assert response.json() == {
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


def test_place_order__invalid_payload__returns_422(authenticated_client):
    client = authenticated_client(role=UserRole.client)

    response = client.post(
        ORDER_URL,
        json={"order": "invalid_order"},
    )

    assert response.status_code == 422


def test_place_order__invalid_order__returns_500(
        authenticated_client,
        mocker,
):
    mocker.patch(
        f"{USERS_SERVICES}.create_order",
        side_effect=SQLAlchemyError()
    )
    client = authenticated_client(role=UserRole.client)

    response = client.post(
        ORDER_URL,
        json=make_order_payload(),
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Не вдалося створити замовлення"}


def test_get_discount__authenticated_user__returns_200(authenticated_client):
    client = authenticated_client(role=UserRole.client)

    response = client.get(DISCOUNT_URL)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data["discount"], int)


def test_get_discount__unauthenticated__returns_401(api_client):
    response = api_client.get(DISCOUNT_URL)

    assert response.status_code == 401
