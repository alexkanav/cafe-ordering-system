import pytest

from tests.factories.dish import make_dish_payload
from tests.fastapi.constants import ADMIN_SERVICES, ADMIN_ROUTES
from utils.enums import UserRole
from domain.core.errors import NOT_AUTHENTICATED, INSUFFICIENT_ROLE

MENU_URL = "/api/admin/menu"
CATEGORIES_URL = "/api/admin/categories"
DISHES_URL = "/api/admin/dishes"


@pytest.mark.parametrize("role, expected_status, detail", [
    (UserRole.staff, 200, None),
    (UserRole.client, 403, INSUFFICIENT_ROLE),
    (None, 401, NOT_AUTHENTICATED),
])
def test_menu__access_by_role__returns_valid_menu_or_403_or_401(
        client_by_role,
        role,
        expected_status,
        detail,
):
    client = client_by_role(role)

    response = client.get(MENU_URL)

    assert response.status_code == expected_status
    data = response.json()

    if expected_status == 200:
        assert isinstance(data["dishes"], dict)
        assert isinstance(data["featured_dishes"], list)
        assert isinstance(data["categories"], list)
        assert isinstance(data["category_id_map"], dict)
    else:
        assert data == {"detail": detail}


def test_update_categories__staff_user__returns_200(
        authenticated_client,
        mocker,
):
    mock_update_categories = mocker.patch(
        f"{ADMIN_SERVICES}.update_categories"
    )
    mock_from_thread_run = mocker.patch(
        f"{ADMIN_ROUTES}.FastAPICache.clear"
    )

    payload = {"category_names": ["Drinks", "Desserts"]}

    client = authenticated_client(role=UserRole.staff)

    response = client.patch(
        CATEGORIES_URL,
        json=payload
    )

    mock_update_categories.assert_called_once()
    mock_from_thread_run.assert_called_once()

    assert response.status_code == 200
    assert response.json() == {"message": "Категорії оновлено"}


@pytest.mark.parametrize("role, expected_status, detail", [
    (UserRole.client, 403, INSUFFICIENT_ROLE),
    (None, 401, NOT_AUTHENTICATED),
])
def test_update_categories__unauthorized_access__returns_403_or_401(
        client_by_role,
        role,
        expected_status,
        detail,
):
    payload = {"category_names": ["Drinks"]}

    client = client_by_role(role)

    response = client.patch(CATEGORIES_URL, json=payload)

    assert response.status_code == expected_status
    assert response.json() == {"detail": detail}


def test_update_categories_status__invalid_payload__returns_422(authenticated_client):
    client = authenticated_client(role=UserRole.staff)

    response = client.patch(CATEGORIES_URL, json={"status": "incorrect data"})

    assert response.status_code == 422


def test_create_or_update_dish__staff_user__returns_200(
        authenticated_client,
        mocker,
):
    mock_create_or_update_dish = mocker.patch(
        f"{ADMIN_SERVICES}.create_or_update_dish"
    )

    mock_from_thread_run = mocker.patch(
        f"{ADMIN_ROUTES}.FastAPICache.clear"
    )

    dish = make_dish_payload()
    client = authenticated_client(role=UserRole.staff)

    response = client.post(DISHES_URL, json=dish)

    mock_create_or_update_dish.assert_called_once()
    mock_from_thread_run.assert_called_once()

    assert response.status_code == 200
    assert response.json() == {"message": f"Страву {dish['code']} оновлено"}


@pytest.mark.parametrize("role, expected_status, detail", [
    (UserRole.client, 403, INSUFFICIENT_ROLE),
    (None, 401, NOT_AUTHENTICATED),
])
def test_create_or_update_dish__unauthorized_access__returns_403_or_401(
        client_by_role,
        role,
        expected_status,
        detail,
):
    client = client_by_role(role)

    response = client.post(DISHES_URL, json=make_dish_payload())

    assert response.status_code == expected_status
    assert response.json() == {"detail": detail}


def test_create_or_update_dish__invalid_payload__returns_422(authenticated_client):
    client = authenticated_client(role=UserRole.staff)

    response = client.post(DISHES_URL, json={"status": "incorrect data"})

    assert response.status_code == 422
