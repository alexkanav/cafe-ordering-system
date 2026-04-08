import pytest

from utils.enums import UserRole

start_date = "2025-04-01"
end_date = "2025-04-30"
STATISTIC_URL = "/api/admin/statistics?startDate={start}&endDate={end}"


@pytest.mark.parametrize("role, expected_status", [
    (UserRole.staff, 200),
    (UserRole.client, 403),
    (None, 401),
])
def test_statistics__access_by_role__returns_200_or_403_or_401(
        client_by_role,
        role,
        expected_status,
):
    client = client_by_role(role)

    response = client.get(STATISTIC_URL.format(start=start_date, end=end_date))

    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.get_json()

        assert data["sales_summary"]["total_sales"] == []
        assert data["dish_order_stats"]["dishes"] == []


def test_statistics__incorrect_date_order__returns_400(authenticated_client):
    client = authenticated_client(role=UserRole.staff)

    response = client.get(STATISTIC_URL.format(start=end_date, end=start_date))

    assert response.status_code == 400
    assert response.get_json() == {"detail": "startDate must be before endDate"}


def test_statistics__missing_dates__returns_400(authenticated_client):
    client = authenticated_client(role=UserRole.staff)

    response = client.get(STATISTIC_URL.format(start="", end=""))

    assert response.status_code == 400
    assert response.get_json() == {"detail": "startDate and endDate are required"}


def test_statistics__invalid_date_format__returns_400(authenticated_client):
    client = authenticated_client(role=UserRole.staff)

    response = client.get(STATISTIC_URL.format(start="invalid", end="invalid"))

    assert response.status_code == 400
    assert response.get_json() == {"detail": "Invalid date format. Use YYYY-MM-DD"}
