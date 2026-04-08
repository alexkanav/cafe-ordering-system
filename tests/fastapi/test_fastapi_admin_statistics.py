import pytest

from utils.enums import UserRole
from domain.core.errors import NOT_AUTHENTICATED, INSUFFICIENT_ROLE

start_date = "2025-04-01"
end_date = "2025-04-30"
STATISTIC_URL = "/api/admin/statistics?startDate={start}&endDate={end}"


@pytest.mark.parametrize("role, expected_status, detail", [
    (UserRole.staff, 200, None),
    (UserRole.client, 403, INSUFFICIENT_ROLE),
    (None, 401, NOT_AUTHENTICATED),
])
def test_statistics__access_by_role__returns_200_or_403_or_401(
        client_by_role,
        role,
        expected_status,
        detail,
):
    client = client_by_role(role)

    response = client.get(STATISTIC_URL.format(start=start_date, end=end_date))

    assert response.status_code == expected_status

    data = response.json()

    if expected_status == 200:

        assert data["sales_summary"]["total_sales"] == []
        assert data["dish_order_stats"]["dishes"] == []

    else:
        assert data == {"detail": detail}


def test_statistics__invalid_payload__returns_422(authenticated_client):
    client = authenticated_client(role=UserRole.staff)

    response = client.get(STATISTIC_URL.format(start="invalid", end="invalid"))

    assert response.status_code == 422


def test_statistics__incorrect_date_order__returns_400(authenticated_client):
    client = authenticated_client(role=UserRole.staff)

    response = client.get(STATISTIC_URL.format(start=end_date, end=start_date))

    assert response.status_code == 400
    assert response.json() == {"detail": "start_date must be before or equal to end_date"}
