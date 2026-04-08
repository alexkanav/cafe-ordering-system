import pytest
from sqlalchemy.exc import IntegrityError

from tests.fastapi.constants import USERS_SERVICES
from domain.core.errors import NotFoundError
from utils.enums import UserRole

MENU_URL = "/api/users/menu"
LIKE_DISH_URL = "/api/users/dishes/100/like"


def test_get_menu__success__returns_200(api_client):
    response = api_client.get(MENU_URL)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data["dishes"], dict)
    assert isinstance(data["categories"], list)


def test_get_menu__cached__returns_cached_result(api_client, mocker, clear_cache):
    mock = mocker.patch(
        f"{USERS_SERVICES}.build_user_menu",
        return_value={"dishes": {}, "categories": []}
    )

    api_client.get(MENU_URL)
    response = api_client.get(MENU_URL)

    assert mock.call_count == 1
    assert response.json() == {"dishes": {}, "categories": []}


def test_like_dish__dish_exists__returns_200(
        authenticated_client,
        mocker,
):
    mocker.patch(f"{USERS_SERVICES}.add_dish_like")

    client = authenticated_client(role=UserRole.client)

    response = client.post(LIKE_DISH_URL)
    assert response.status_code == 200
    assert response.json() == {"message": "Вподобання додано"}


@pytest.mark.parametrize("response_error, expected_status, detail", [
    (NotFoundError("Not Found"), 404, "Not Found"),
    (IntegrityError("", "", ""), 409, "Ви вже оцінювали цей продукт"),
])
def test_like_dish__service_errors__returns_404_or_409(
        authenticated_client,
        mocker,
        response_error,
        expected_status,
        detail,
):
    mocker.patch(
        f"{USERS_SERVICES}.add_dish_like",
        side_effect=response_error,
    )
    client = authenticated_client(role=UserRole.client)

    response = client.post(LIKE_DISH_URL)

    assert response.status_code == expected_status
    assert response.json() == {"detail": detail}


def test_like_dish__unauthenticated__returns_401(api_client):
    response = api_client.post(LIKE_DISH_URL)
    assert response.status_code == 401
